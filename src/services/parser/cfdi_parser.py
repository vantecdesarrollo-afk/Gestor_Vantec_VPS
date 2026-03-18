import xml.etree.ElementTree as ET
import logging
from pathlib import Path
import shutil
import uuid as uuid_lib
import os as os_lib
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Cfdi
from datetime import datetime

# Configuración de Logs según el estándar Vantec
logger = logging.getLogger("VANTEC_PARSER")

class CFDIParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        self.version = self._get_version()

    def _get_version(self):
        return self.root.get('Version') or self.root.get('version')

    def get_metadata(self):
        namespaces = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        tfd = self.root.find('.//tfd:TimbreFiscalDigital', namespaces)
        cfdi_uuid = tfd.get('UUID') if tfd is not None else None

        tipo_comp = self.root.get('TipoDeComprobante') or self.root.get('tipoDeComprobante')
        total_val = self.root.get('Total') or self.root.get('total')

        if tipo_comp == 'P':
            pago20_ns = {'pago20': 'http://www.sat.gob.mx/Pagos20'}
            pagos_node = self.root.find('.//pago20:Pagos', pago20_ns)
            if pagos_node is not None:
                totales_node = pagos_node.find('pago20:Totales', pago20_ns)
                if totales_node is not None:
                    monto_total_pagos = totales_node.get('MontoTotalPagos')
                    if monto_total_pagos:
                        total_val = monto_total_pagos

        metadata = {
            "version": self.version,
            "uuid": cfdi_uuid,
            "serie": self.root.get('Serie') or self.root.get('serie'),
            "folio": self.root.get('Folio') or self.root.get('folio'),
            "fecha": self.root.get('Fecha') or self.root.get('fecha'),
            "total": total_val,
            "tipo_comprobante": tipo_comp,
            "metodo_pago": self.root.get('MetodoPago') or self.root.get('metodoPago'),
            "forma_pago": self.root.get('FormaPago') or self.root.get('formaPago'),
            "relaciones": []
        }
        
        # Vantec Core: Extraer relaciones de Pago 2.0
        if tipo_comp == 'P':
             pago20_ns = {'pago20': 'http://www.sat.gob.mx/Pagos20'}
             pagos_node = self.root.find('.//pago20:Pagos', pago20_ns)
             if pagos_node is not None:
                  for pago in pagos_node.findall('pago20:Pago', pago20_ns):
                       for doc_rel in pago.findall('pago20:DoctoRelacionado', pago20_ns):
                            metadata["relaciones"].append({
                                "uuid_relacionado": doc_rel.get('IdDocumento'),
                                "tipo_relacion": "PAGO",
                                "monto_pagado": float(doc_rel.get('ImpPagado') or 0),
                                "saldo_insoluto": float(doc_rel.get('ImpSaldoInsoluto') or 0),
                                "num_parcialidad": int(doc_rel.get('NumParcialidad') or 1)
                            })

        emisor = self.root.find('.//{*}Emisor')
        receptor = self.root.find('.//{*}Receptor')
        
        if emisor is not None:
            metadata["rfc_emisor"] = emisor.get('Rfc') or emisor.get('rfc')
        if receptor is not None:
            metadata["rfc_receptor"] = receptor.get('Rfc') or receptor.get('rfc')

        return metadata

    def _calcular_ruta_resguardo(self, rfc: str, fecha_val) -> str:
        try:
            year = str(fecha_val.year)
            month = f"{fecha_val.month:02d}"
        except:
             year = "OTROS"
             month = "OTROS"
            
        base_ops = r"C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI"
        return os_lib.path.join(base_ops, "Files", rfc, year, month)


async def process_inbound_file(xml_path: str, failed_dir: str, log_dir: str, db: AsyncSession, entidad_id, pdf_path: str = None):
    # Obtener nombre de archivo de forma segura desde el inicio
    file_name = os_lib.path.basename(xml_path)
    
    try:
        parser = CFDIParser(xml_path)
        data = parser.get_metadata()
        
        if not data.get("uuid"):
            raise ValueError("UUID no encontrado en el timbre fiscal del XML.")

        fecha_val = data.get("fecha")
        if fecha_val:
            try:
                # remove Z if present
                fecha_val = datetime.fromisoformat(fecha_val.replace('Z', ''))
            except:
                fecha_val = datetime.now()
        else:
            fecha_val = datetime.now()

        # Calcular ruta resguardo con rfc_emisor y fecha
        rfc_para_ruta = data.get("rfc_emisor") or "OTROS"
        ruta_resguardo = parser._calcular_ruta_resguardo(rfc_para_ruta, fecha_val)
        dest_xml = os_lib.path.join(ruta_resguardo, f"{data['uuid']}.xml")



        try:
            total_num = float(data["total"]) if data["total"] else 0.0
        except:
            total_num = 0.0

        # Validar duplicados (Idempotencia)
        from sqlalchemy import select
        from src.database.models import Cfdi
        existing = await db.execute(select(Cfdi).where(Cfdi.uuid == data["uuid"]))
        if existing.scalar_one_or_none():
            logger.warning(f"Omitiendo duplicado: {data['uuid']}")
            raise ValueError(f"CFDI Duplicado: {data['uuid']}")

        nuevo_comprobante = Cfdi(
            uuid=data["uuid"],
            tenant_id=entidad_id,
            rfc_emisor=data.get("rfc_emisor"),
            rfc_receptor=data.get("rfc_receptor"),
            version=data.get("version"),
            status="VALID",
            total=total_num,
            issue_date=fecha_val,
            xml_file_path=dest_xml
        )

        
        db.add(nuevo_comprobante)


        # Vantec Core: Insertar relaciones para CFDIs
        # Relaciones deshabilitadas para v1.0.0
        
        await db.commit()
        logger.info(f"✅ Éxito: Indexado {data.get('serie') or ''}{data.get('folio') or ''} v{data.get('version')}")
        
        # --- RESGUARDO EN BÓVEDA (VANTEC AUTO-VAULT) ---
        os_lib.makedirs(ruta_resguardo, exist_ok=True)
        dest_xml = os_lib.path.join(ruta_resguardo, f"{data['uuid']}.xml")
        
        # Mover XML
        if os_lib.path.exists(xml_path):
             shutil.move(xml_path, dest_xml)
        
        # Mover PDF opcional
        if pdf_path and os_lib.path.exists(pdf_path):
             dest_pdf = os_lib.path.join(ruta_resguardo, f"{data['uuid']}.pdf")
             shutil.move(pdf_path, dest_pdf)
             
    except Exception as e:
        await db.rollback()
        xml_file = file_name
        import logging
        logging.error(f"Fallo en {xml_file}: {e}")
        
        # Si es un duplicado, no mover a failed, ya está en Bóveda (evitar romper resguardo)
        if "CFDI Duplicado" in str(e):
             # Solo eliminar de procesamiento para liberar lock
             try:
                 if os_lib.path.exists(xml_path): os_lib.remove(xml_path)
                 if pdf_path and os_lib.path.exists(pdf_path): os_lib.remove(pdf_path)
             except: pass
             return True # Finalizar sin error de ingesta catastrófico

        os_lib.makedirs(failed_dir, exist_ok=True)
        dest_failed = os_lib.path.join(failed_dir, file_name)
        
        try:
            if os_lib.path.exists(xml_path):
                shutil.move(xml_path, dest_failed)
            # También mover PDF a failed si falló
            if pdf_path and os_lib.path.exists(pdf_path):
                 shutil.move(pdf_path, os_lib.path.join(failed_dir, os_lib.path.basename(pdf_path)))
        except Exception as move_error:
            logger.error(f"🚨 Error moviendo a failed: {str(move_error)}")
            
        os_lib.makedirs(log_dir, exist_ok=True)
        log_name = f"{os_lib.path.splitext(file_name)[0]}_error.log"
        log_path = os_lib.path.join(log_dir, log_name)
        try:
            with open(log_path, "w", encoding='utf-8') as f_log:
                f_log.write(f"Error procesando {file_name}\nFecha: {datetime.now().isoformat()}\nDetalle: {str(e)}\n")
        except:
            pass