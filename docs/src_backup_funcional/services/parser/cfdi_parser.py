import xml.etree.ElementTree as ET
import logging
from pathlib import Path
import shutil
import uuid as uuid_lib
import os as os_lib
import time
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# Configuración de Logs según el estándar Vantec
logger = logging.getLogger("VANTEC_PARSER")
class CFDIParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        # 🛡️ Blindaje L6 v5.1: Lectura Robusta (BOM + Stripping)
        try:
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                 content = f.read().strip()
                 if not content:
                      raise ValueError("Archivo XML vacío o ilegible.")
                 self.root = ET.fromstring(content)
                 self.tree = ET.ElementTree(self.root)
        except (ET.ParseError, UnicodeDecodeError):
            # Fallback Legacy (latin-1) con sanitización mandatoria
            with open(self.file_path, 'r', encoding='latin-1') as f:
                 content = f.read().strip()
                 if not content:
                      raise ValueError("Archivo XML legacy vacío.")
                 self.root = ET.fromstring(content)
                 self.tree = ET.ElementTree(self.root)
        
        self.version = self._get_version()

    def _get_version(self):
        return self.root.get('Version') or self.root.get('version')

    def get_metadata(self):
        namespaces = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        tfd = self.root.find('.//tfd:TimbreFiscalDigital', namespaces)
        cfdi_uuid = tfd.get('UUID') if tfd is not None else None

        tipo_comp = self.root.get('TipoDeComprobante') or self.root.get('tipoDeComprobante')
        if tipo_comp:
            tipo_comp = tipo_comp[0].upper() # Ingreso -> I
        total_val = self.root.get('Total') or self.root.get('total')
        subtotal_val = self.root.get('SubTotal') or self.root.get('subTotal')
        tipo_cambio_val = self.root.get('TipoCambio') or self.root.get('tipoCambio') or 1.0

        metadata = {"forma_pago": None, "total": total_val}
        if tipo_comp == 'P':
            # 🌐 Mapeo Universal de Namespaces (Pagos 1.0 y 2.0)
            pago_ns = {
                'p20': 'http://www.sat.gob.mx/Pagos20', 
                'p10': 'http://www.sat.gob.mx/Pagos'
            }
            # Búsqueda agnóstica de versión (v3.3 vs v4.0)
            pagos_node = (self.root.find('.//p20:Pagos', pago_ns) or 
                          self.root.find('.//p10:Pagos', pago_ns) or
                          self.root.find('.//{*}Pagos'))
            
            if pagos_node is not None:
                # Detectar prefijo dinámicamente para sub-nodos
                p_pref = 'p20' if 'Pagos20' in (pagos_node.tag or '') else 'p10'
                
                # Buscar primer nodo de Pago para metadatos generales
                pago_item = pagos_node.find(f'.//{p_pref}:Pago', pago_ns) or pagos_node.find('.//{*}Pago')
                if pago_item is not None:
                    metadata["forma_pago"] = (pago_item.get('FormaDePagoP') or 
                                             pago_item.get('FormaPagoP') or 
                                             pago_item.get('formaPagoP'))
                    
                # Totales específicos de la versión
                totales_node = pagos_node.find(f'.//{p_pref}:Totales', pago_ns) or pagos_node.find('.//{*}Totales')
                if totales_node is not None:
                    monto_total = totales_node.get('MontoTotalPagos') or totales_node.get('montoTotalPagos')
                    if monto_total:
                        metadata["total"] = total_val = float(monto_total)
                elif pago_item is not None:
                    # Fallback Pagos 1.0 (v3.3)
                    metadata["total"] = total_val = float(pago_item.get('Monto') or 0.0)

        emisor = self.root.find('.//{*}Emisor')
        receptor = self.root.find('.//{*}Receptor')
        
        def _s(val): return str(val).strip() if val else None

        metadata.update({
            "version": self.version,
            "uuid": cfdi_uuid,
            "serie": _s(self.root.get('Serie') or self.root.get('serie')),
            "folio": _s(self.root.get('Folio') or self.root.get('folio')),
            "fecha": self.root.get('Fecha') or self.root.get('fecha'),
            "rfc_emisor": _s((emisor.get('Rfc') or emisor.get('rfc')) if emisor is not None else None),
            "nombre_emisor": _s((emisor.get('Nombre') or emisor.get('nombre')) if emisor is not None else None),
            "rfc_receptor": _s((receptor.get('Rfc') or receptor.get('rfc')) if receptor is not None else None),
            "nombre_receptor": _s((receptor.get('Nombre') or receptor.get('nombre')) if receptor is not None else None),
            "regimen_fiscal_receptor": _s((receptor.get('RegimenFiscalReceptor') or receptor.get('regimenFiscalReceptor')) if receptor is not None else None),
            "domicilio_fiscal_receptor": _s((receptor.get('DomicilioFiscalReceptor') or receptor.get('domicilioFiscalReceptor')) if receptor is not None else None),
            "total": total_val,
            "subtotal": subtotal_val,
            "tipo_cambio": tipo_cambio_val,
            "tipo_comprobante": tipo_comp,
            "moneda": self.root.get('Moneda') or self.root.get('moneda') or "MXN",
            "metodo_pago": self.root.get('MetodoPago') or self.root.get('metodoPago'),
            "relaciones": [],
            "conceptos": []
        })
        
        # Sobreescribir con el valor de la raíz si no se encontró en Pagos (fallback)
        if not metadata["forma_pago"]:
             metadata["forma_pago"] = self.root.get('FormaPago') or self.root.get('formaPago')
        
        # Extraer Conceptos Robustos
        concepts_xpath = './/{*}Conceptos/{*}Concepto'
        for node in self.root.findall(concepts_xpath):
             metadata["conceptos"].append({
                 "clave_prod_serv": node.get('ClaveProdServ') or node.get('clave_prod_serv'),
                 "descripcion": node.get('Descripcion') or node.get('descripcion') or "",
                 "cantidad": float(node.get('Cantidad') or 0),
                 "valor_unitario": float(node.get('ValorUnitario') or 0),
                 "importe": float(node.get('Importe') or 0)
             })

        # Vantec Core: Extraer relaciones de Raíz (Notas de Crédito, Sustitución, etc.)
        if tipo_comp != 'P':
             # Soporte Multiversión (4.0 / 3.3)
             rel_ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'cfdi33': 'http://www.sat.gob.mx/cfd/3'}
             rel_node = self.root.find('.//cfdi:CfdiRelacionados', rel_ns) or self.root.find('.//cfdi33:CfdiRelacionados', rel_ns)
             
             if rel_node is not None:
                  t_rel = rel_node.get('TipoRelacion')
                  for r_id in rel_node.findall('.//{*}CfdiRelacionado'):
                       u_rel = (r_id.get('UUID') or "").lower().strip()
                       if u_rel:
                            metadata["relaciones"].append({
                                "uuid_relacionado": u_rel,
                                "tipo_relacion": t_rel,
                                "monto_pagado": float(total_val or 0.0), # Para NC, el monto pagado es el total de la NC
                                "num_parcialidad": 1,
                                "saldo_anterior": 0.0,
                                "saldo_insoluto": 0.0,
                                "descripcion_virtual": f"Nota de Crédito/Relación Tipo {t_rel}"
                            })

        # 🛡️ Blindaje L6 v5.1: Extracción Hardened de Pagos 2.0 / 1.0
        if tipo_comp == 'P':
             namespaces = {'p20': 'http://www.sat.gob.mx/Pagos20', 'p10': 'http://www.sat.gob.mx/Pagos'}
             p_node = (self.root.find('.//p20:Pagos', namespaces) or 
                       self.root.find('.//p10:Pagos', namespaces) or
                       self.root.find('.//{*}Pagos'))
             
             if p_node is not None:
                  p_pref = 'p20' if 'Pagos20' in (p_node.tag or '') else 'p10'
                  # ITERACIÓN N:1 - Recorrer TODOS los nodos de Pago (Multidivisa/Multifecha)
                  for pago in p_node.findall(f'.//{p_pref}:Pago', namespaces) or p_node.findall('.//{*}Pago'):
                       # Si tiene FormaPagoP dentro del pago
                       if not metadata.get("forma_pago"):
                           metadata["forma_pago"] = (pago.get('FormaDePagoP') or 
                                                    pago.get('FormaPagoP') or 
                                                    pago.get('formaPagoP'))
                       
                       # ITERACIÓN N:1 - DoctoRelacionado (Soporte Universal)
                       for doc_rel in pago.findall(f'.//{p_pref}:DoctoRelacionado', namespaces) or pago.findall('.//{*}DoctoRelacionado'):
                             u_rel = (doc_rel.get('IdDocumento') or doc_rel.get('idDocumento') or "").lower().strip()
                             if not u_rel: continue

                             desc_pago = f"Pago de Factura (L6): {doc_rel.get('Folio') or 'S/N'} (Parcialidad: {doc_rel.get('NumParcialidad') or '1'})"
                             monto_val = float(doc_rel.get('ImpPagado') or doc_rel.get('impPagado') or 0.0)
                             
                             metadata["relaciones"].append({
                                 "uuid_relacionado": u_rel,
                                 "tipo_relacion": "PAGO",
                                 "monto_pagado": monto_val,
                                 "num_parcialidad": doc_rel.get('NumParcialidad') or doc_rel.get('numParcialidad'),
                                 "saldo_anterior": float(doc_rel.get('ImpSaldoAnt') or doc_rel.get('impSaldoAnt') or 0.0),
                                 "saldo_insoluto": float(doc_rel.get('ImpSaldoInsoluto') or doc_rel.get('impSaldoInsoluto') or doc_rel.get('ImpSaldoIns') or 0.0),
                                 "descripcion_virtual": desc_pago
                             })
                             
                             # Inyectar como concepto para que la UI lo tome naturalmente
                             metadata["conceptos"].append({
                                 "descripcion": desc_pago,
                                 "importe": monto_val,
                                 "cantidad": 1,
                                 "valor_unitario": monto_val
                             })

        emisor = self.root.find('.//{*}Emisor')
        receptor = self.root.find('.//{*}Receptor')
        
        if emisor is not None:
            metadata["rfc_emisor"] = emisor.get('Rfc') or emisor.get('rfc')
        if receptor is not None:
            metadata["rfc_receptor"] = receptor.get('Rfc') or receptor.get('rfc')
            metadata["nombre_receptor"] = receptor.get('Nombre') or receptor.get('nombre')

        return metadata

    def _calcular_ruta_resguardo(self, rfc: str, fecha_val) -> str:
        try:
            year = str(fecha_val.year)
            month = f"{fecha_val.month:02d}"
        except:
             year = "OTROS"
             month = "OTROS"
            
        # Relative to project root
        project_root = os_lib.path.abspath(os_lib.path.join(os_lib.path.dirname(__file__), "..", "..", ".."))
        base_ops = os_lib.path.join(project_root, "Operacion_CFDI")
        return os_lib.path.join(base_ops, "Files", rfc, year, month)
async def process_inbound_file(xml_path: str, failed_dir: str, log_dir: str, db: AsyncSession, entidad_id, pdf_path=None, index_only: bool = False):
    # Soporte para múltiples PDFs (Lista o String único)
    pdf_paths = [pdf_path] if isinstance(pdf_path, str) else (pdf_path or [])
    # Obtener nombre de archivo de forma segura desde el inicio
    file_name = os_lib.path.basename(xml_path)
    
    try:
        parser = CFDIParser(xml_path)
        data = parser.get_metadata()
        rfc_emisor = data.get("rfc_emisor")

        from src.database.models import Tenant, Comprobante, CfdiRelacionado, CfdiConcepto, FinancialAnomalyLog
        from sqlalchemy import select, update
        
        # =====================================================================
        # 1. VALIDACIÓN DE TENANT (SSoT): Soporte Dual (Emisión/Recepción)
        # =====================================================================
        rfc_receptor = str(data.get("rfc_receptor") or "").strip().upper()
        # Try matching Emisor first (Outbound)
        tenant_query = await db.execute(select(Tenant).where(Tenant.rfc == rfc_emisor))
        tenant = tenant_query.scalars().first()
        
        # If not, try matching Receptor (Inbound)
        if not tenant:
            tenant_query = await db.execute(select(Tenant).where(Tenant.rfc == rfc_receptor))
            tenant = tenant_query.scalars().first()

        if not tenant:
            if index_only:
                 raise ValueError(f"RFCs {rfc_emisor}/{rfc_receptor} no registrados como Tenant. Omitiendo.")
            
            # Movimiento físico a Orphans (Según Manual)
            project_root = os_lib.path.abspath(os_lib.path.join(os_lib.path.dirname(__file__), "..", "..", ".."))
            orphans_dir = os_lib.path.join(project_root, "Operacion_CFDI", "Orphans")
            os_lib.makedirs(orphans_dir, exist_ok=True)
            
            shutil.move(xml_path, os_lib.path.join(orphans_dir, file_name))
            if pdf_path and os_lib.path.exists(pdf_path):
                 shutil.move(pdf_path, os_lib.path.join(orphans_dir, os_lib.path.basename(pdf_path)))
            
            logger.warning(f"Archivo movido a Orphans: RFCs {rfc_emisor}/{rfc_receptor} no registrados.")
            return True 

        entidad_id = tenant.tenant_id
        
        if not data.get("uuid"):
            raise ValueError("UUID no encontrado en el timbre fiscal del XML.")

        fecha_val = data.get("fecha")
        if fecha_val:
            try:
                fecha_val = datetime.fromisoformat(str(fecha_val).replace('Z', ''))
            except:
                fecha_val = datetime.now()
        else:
            fecha_val = datetime.now()

        # Calcular ruta de resguardo
        if tenant.base_repository_path:
            if tenant.rfc == 'CMES8901177E8' or "VANTEC" in str(tenant.business_name).upper():
                ruta_resguardo = tenant.base_repository_path
            else:
                tc = str(data.get("tipo_comprobante")).upper()
                if tc == 'P': folder_tipo = "PAGOS"
                elif tc == 'E': folder_tipo = "NOTACREDITO"
                else: folder_tipo = "FACTURA"
                
                serie = str(data.get("serie") or "OTROS").strip()
                ruta_resguardo = os_lib.path.join(tenant.base_repository_path, folder_tipo, serie)
        else:
            ruta_resguardo = parser._calcular_ruta_resguardo(rfc_emisor, fecha_val)
            
        dest_xml = os_lib.path.join(ruta_resguardo, f"{data['uuid']}.xml") if not index_only else xml_path
        
        # Generar rutas de destino para todos los PDFs
        final_pdf_paths = []
        if not index_only:
            for i, p in enumerate(pdf_paths):
                suffix = f"_{i}" if i > 0 else ""
                final_pdf_paths.append(os_lib.path.join(ruta_resguardo, f"{data['uuid']}{suffix}.pdf"))
        else:
            final_pdf_paths = pdf_paths

        # Guardar en DB como cadena separada por pipes
        db_pdf_path = "|".join(final_pdf_paths) if final_pdf_paths else None

        try:
            total_num = float(data["total"]) if data["total"] else 0.0
            subtotal_num = float(data.get("subtotal") or total_num)
        except:
            total_num = 0.0
            subtotal_num = 0.0

        # Validar duplicados (Idempotencia en SSoT, según Protocolo L6)
        existing = await db.execute(select(Comprobante).where(Comprobante.uuid == data["uuid"]))
        if existing.scalar_one_or_none():
             logger.warning(f"Omitiendo duplicado: {data['uuid']} (Delegando movimiento al Watcher)")
             raise ValueError(f"CFDI Duplicado Detectado: {data['uuid']}")

        # =====================================================================
        # 2. DETECCIÓN DE PAGOS HUÉRFANOS (Vantec L6 Protocol)
        # =====================================================================
        is_orphan = False
        if data.get("tipo_comprobante") == 'P':
             # Verificar si el UUID relacionado existe en el SSoT
             for rel in data.get("relaciones", []):
                  uuid_rel = rel.get("uuid_relacionado")
                  if uuid_rel:
                       try:
                            res_rel = await db.execute(select(Comprobante).where(Comprobante.uuid == uuid_lib.UUID(uuid_rel)))
                            if not res_rel.scalar_one_or_none():
                                 is_orphan = True
                                 # Auditoría Física (L6 Protocol)
                                 anomaly = FinancialAnomalyLog(
                                     entidad_id=entidad_id,
                                     uuid_documento=uuid_lib.UUID(data["uuid"]),
                                     tipo_anomalia='PAGO_HUERFANO',
                                     detalle=f"Referencia de pago a UUID {uuid_rel} inexistente en SSoT.",
                                     estatus_anomalia='ACTIVA'
                                 )
                                 db.add(anomaly)
                                 logger.warning(f"⚠️ PAGO HUÉRFANO DETECTADO: Pago {data['uuid']} referencia a factura {uuid_rel} no encontrada.")
                       except: pass

        # =====================================================================
        # 3. INSERCIÓN ÚNICA (SSoT)
        # =====================================================================
        vcore_comp = Comprobante(
            uuid=uuid_lib.UUID(data["uuid"]),
            entidad_id=entidad_id,
            serie=data.get("serie"),
            folio=data.get("folio"),
            fecha_emision=fecha_val,
            rfc_emisor=data.get("rfc_emisor"),
            nombre_emisor=data.get("nombre_emisor") or "Emisor Sin Identificar",
            rfc_receptor=data.get("rfc_receptor"),
            nombre_receptor=data.get("nombre_receptor") or "Cliente Sin Identificar",
            regimen_fiscal_receptor=data.get("regimen_fiscal_receptor"), # 🛡️ L6 v5.1
            domicilio_fiscal_receptor=data.get("domicilio_fiscal_receptor"), # 🛡️ L6 v5.1
            tipo_comprobante=data.get("tipo_comprobante") or "I",
            moneda=data.get("moneda") or "MXN",
            subtotal=subtotal_num,
            total=total_num,
            estatus_sat="Vigente",
            orphan_payment=is_orphan,
            version=data.get("version"),
            xml_path=dest_xml,
            pdf_path=db_pdf_path,
            metodo_pago=data.get("metodo_pago"),
            forma_pago=data.get("forma_pago")
        )
        db.add(vcore_comp)

        # =====================================================================
        # 4. GHOST RECOVERY (Vantec Core L6)
        # =====================================================================
        if data.get("tipo_comprobante") == 'I':
             # Buscar REPs que tengan este UUID como relacionado y sean huérfanos
             target_uuid_str = str(data["uuid"]).lower()
             q_rec = select(Comprobante).join(CfdiRelacionado, CfdiRelacionado.cfdi_id == Comprobante.uuid).where(
                 Comprobante.tipo_comprobante == 'P',
                 Comprobante.orphan_payment == True,
                 CfdiRelacionado.uuid_relacionado == target_uuid_str
             )
             res_rec = await db.execute(q_rec)
             healed_reps = res_rec.scalars().all()
             
             for rep in healed_reps:
                  rep.orphan_payment = False
                  logger.info(f"👻 GHOST RECOVERY: Pago {rep.uuid} vinculado con Factura {data['uuid']}")
                  rec_log = FinancialAnomalyLog(
                      entidad_id=entidad_id,
                      uuid_documento=rep.uuid,
                      tipo_anomalia='GHOST_RECOVERY',
                      detalle=f"Sanado por la aparición tardía de la factura {data['uuid']}",
                      estatus_anomalia='RESUELTA'
                  )
                  db.add(rec_log)

        # Inserción de Relaciones
        for r in data.get("relaciones", []):
             nueva_rel = CfdiRelacionado(
                 cfdi_id=uuid_lib.UUID(data["uuid"]),
                 uuid_padre=data["uuid"],
                 uuid_relacionado=r.get("uuid_relacionado"),
                 tipo_relacion=r.get("tipo_relacion"),
                 monto_pagado=r.get("monto_pagado")
             )
             db.add(nueva_rel)

        # Inserción de Conceptos
        for c in data.get("conceptos", []):
             nuevo_concepto = CfdiConcepto(
                 cfdi_id=vcore_comp.uuid,
                 clave_prod_serv=c.get("clave_prod_serv"),
                 cantidad=c.get("cantidad"),
                 descripcion=c.get("descripcion"),
                 valor_unitario=c.get("valor_unitario"),
                 importe=c.get("importe")
             )
             db.add(nuevo_concepto)
        
        await db.commit()
        # El éxito es silencioso (Vantec Standards)
        # logger.info(f"✅ SSoT Éxito: Indexado {data.get('serie') or ''}{data.get('folio') or ''}")
        # --- RESGUARDO FÍSICO ---
        if not index_only:
             os_lib.makedirs(ruta_resguardo, exist_ok=True)
             if os_lib.path.exists(xml_path):
                  shutil.move(xml_path, dest_xml)
             
             for src, dst in zip(pdf_paths, final_pdf_paths):
                  if src and os_lib.path.exists(src):
                       shutil.move(src, dst)
             
        return True
    
    except Exception as e:
        await db.rollback()
        if "CFDI Duplicado" in str(e):
             # Desacoplado: El Watcher captura el raise y ejecuta el movimiento tras el log
             raise e

        if index_only: raise e

        os_lib.makedirs(failed_dir, exist_ok=True)
        try:
            if os_lib.path.exists(xml_path):
                shutil.move(xml_path, os_lib.path.join(failed_dir, file_name))
            for p in pdf_paths:
                if p and os_lib.path.exists(p):
                     shutil.move(p, os_lib.path.join(failed_dir, os_lib.path.basename(p)))
        except: pass
            
        os_lib.makedirs(log_dir, exist_ok=True)
        log_path = os_lib.path.join(log_dir, f"{os_lib.path.splitext(file_name)[0]}_error.log")
        try:
            with open(log_path, "w", encoding='utf-8') as f_log:
                f_log.write(f"Error procesando {file_name}\nFecha: {datetime.now().isoformat()}\nDetalle: {str(e)}\n")
        except: pass
        return False # Added return for failed processing

async def analyze_pdf_fiscal_data(pdf_path):
    from pypdf import PdfReader
    import re
    
    # [L6 v4.0] Regex Ultra-Flexible (Soporta espacios y saltos de línea del PDF)
    uuid_pattern = re.compile(r'[0-9a-fA-F]{8}\s*-\s*[0-9a-fA-F]{4}\s*-\s*[0-9a-fA-F]{4}\s*-\s*[0-9a-fA-F]{4}\s*-\s*[0-9a-fA-F]{12}')
    rfc_pattern  = re.compile(r'[A-Z&Ñ\xd1]{3,4}[0-9]{6}[A-Z0-9]{3}', re.IGNORECASE)
    
    data = {"uuid": None, "nature": "NO_FISCAL", "rfc": "N/A"}
    try:
        reader = PdfReader(pdf_path)
        
        # 1. Extracción de Texto Estructurado
        full_text = " ".join([p.extract_text() or "" for p in reader.pages])
        
        # 2. Extracción de Metadata XMP (Vital para Ghostscript/Bullzip)
        metadata = str(reader.metadata) if reader.metadata else ""

        # 3. Escaneo Binario (Fallback para archivos corruptos o sin texto plano)
        with open(pdf_path, 'rb') as f:
            raw = f.read()
            binary_dump = raw.decode('utf-8', 'ignore') + " " + raw.decode('latin-1', 'ignore')

        # UNIFICACIÓN DE DATOS PARA ANÁLISIS
        content = (full_text + " " + metadata + " " + binary_dump).replace('\n', ' ')

        # BÚSQUEDA DE IDENTIDAD
        match_uuid = uuid_pattern.search(content)
        match_rfc = rfc_pattern.findall(content)

        if match_uuid:
            data["uuid"] = re.sub(r'\s+', '', match_uuid.group(0)).upper() # Normalización L6
            data["nature"] = "FISCAL"
            if match_rfc:
                # Filtramos el RFC más probable (el de 12-13 caracteres)
                data["rfc"] = max(set(match_rfc), key=len).upper()
        
        # [DEBUG LOG] Solo se activa si el sistema sigue sin ver el RFC
        if data["rfc"] == "N/A" and data["uuid"]:
            print(f"⚠️  ALERTA CTO: UUID detectado ({data['uuid']}) pero RFC invisible en el stream.")

    except Exception as e:
        print(f"💀 FALLO MOTOR L6: {e}")
    
    return data