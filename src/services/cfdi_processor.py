
import os
import shutil
import uuid
import time
import defusedxml.ElementTree as ET
from datetime import datetime
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Cfdi, CfdiRelacionado
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CfdiProcessor:
    """
    Core de Procesamiento Unificado (Categoría Enterprise - Vantec).
    Centraliza el Deep Parsing de XML e inserción a DB.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def procesar_cfdi(
        self, 
        ruta_archivo: str, 
        entidad_id: uuid.UUID, 
        mover_a_boveda: bool = False,
        source_type: str = 'UPLOAD_MANUAL',
        ruta_pdf: Optional[str] = None
    ) -> Cfdi:
        """
        [ES] Función central de ingesta. Procesa XML y opcionalmente PDF.
        [EN] Central ingestion function. Processes XML and optionally PDF.
        """
        
        # 1. Espera activa por bloqueo de archivo / File lock wait (Windows)
        content = await self._read_file_with_retry(ruta_archivo)
        
        # 2. Motor de Deep Parsing
        filename = os.path.basename(ruta_archivo)
        parsed_data = self._parse_cfdi_deep(content, filename)
        cfdi_uuid = parsed_data["uuid"]
        
        # 3. Lógica de Bóveda (Secure Multi-tenant Storage)
        final_xml_path = ruta_archivo
        final_pdf_path = ruta_pdf

        if mover_a_boveda:
            # Deterministic storage with UUID rename
            # Almacenamiento determinista con renombrado por UUID
            final_xml_path, final_pdf_path = self._asegurar_en_boveda_dual(
                ruta_xml=ruta_archivo,
                ruta_pdf=ruta_pdf,
                entidad_id=entidad_id,
                cfdi_uuid=cfdi_uuid,
                fecha=parsed_data["issue_date"]
            )

        # 4. Lógica Upsert (Evitar colapso por duplicados) / Upsert Logic
        try:
            result = await self.db.execute(select(Cfdi).where(Cfdi.uuid == cfdi_uuid))
            existing_cfdi = result.scalars().first()

            if existing_cfdi:
                logger.info(f"♻️ CFDI Duplicado detectado ({cfdi_uuid}). Actualizando rutas.")
                existing_cfdi.xml_file_path = final_xml_path
                existing_cfdi.pdf_file_path = final_pdf_path
                existing_cfdi.metadata_xml = parsed_data["metadata_xml"]
                existing_cfdi.total = parsed_data["total"]
                existing_cfdi.parent_uuid = parsed_data.get("parent_uuid")
                
                # REPROCESAR RELACIONES
                await self.db.execute(
                    text("DELETE FROM cfdi_relacionados WHERE cfdi_id = :id"),
                    {"id": existing_cfdi.cfdi_id}
                )
                for rel in parsed_data.get("relaciones", []):
                    self.db.add(CfdiRelacionado(
                        cfdi_id=existing_cfdi.cfdi_id,
                        uuid_padre=cfdi_uuid,
                        uuid_relacionado=rel["uuid_relacionado"],
                        tipo_relacion=rel["tipo_relacion"],
                        monto_pagado=rel["monto_pagado"],
                        saldo_insoluto=rel["saldo_insoluto"],
                        num_parcialidad=rel["num_parcialidad"]
                    ))
                
                await self.db.commit()
                await self.db.refresh(existing_cfdi)
                return existing_cfdi
            else:
                # 5. Inserción Directa / New Entry
                new_cfdi = Cfdi(
                    entidad_id=entidad_id,
                    uuid=cfdi_uuid,
                    rfc_emisor=parsed_data["rfc_emisor"],
                    rfc_receptor=parsed_data["rfc_receptor"],
                    issue_date=parsed_data["issue_date"],
                    total=parsed_data["total"],
                    version=parsed_data["version"],
                    tipo_comprobante=parsed_data["tipo_comprobante"],
                    metodo_pago=parsed_data["metodo_pago"],
                    forma_pago=parsed_data["forma_pago"],
                    serie=parsed_data["serie"],
                    folio=parsed_data["folio"],
                    xml_file_path=final_xml_path,
                    pdf_file_path=final_pdf_path,
                    metadata_xml=parsed_data["metadata_xml"],
                    parent_uuid=parsed_data.get("parent_uuid"),
                    source_type=source_type,
                    status="VALID"
                )
                self.db.add(new_cfdi)
                await self.db.flush()

                for rel in parsed_data.get("relaciones", []):
                    self.db.add(CfdiRelacionado(
                        cfdi_id=new_cfdi.cfdi_id,
                        uuid_padre=cfdi_uuid,
                        uuid_relacionado=rel["uuid_relacionado"],
                        tipo_relacion=rel["tipo_relacion"],
                        monto_pagado=rel["monto_pagado"],
                        saldo_insoluto=rel["saldo_insoluto"],
                        num_parcialidad=rel["num_parcialidad"]
                    ))

                await self.db.commit()
                await self.db.refresh(new_cfdi)
                return new_cfdi

        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error de persistencia para {cfdi_uuid}: {str(e)}")
            raise

    async def attach_orphan_pdf(self, ruta_pdf: str, entidad_id: uuid.UUID) -> Optional[Cfdi]:
        """
        [ES] Intenta vincular un PDF huérfano a un CFDI existente basándose en el nombre (Serie-Folio).
        """
        filename = os.path.basename(ruta_pdf)
        base_name = os.path.splitext(filename)[0]
        
        import re
        serie = ""
        folio = base_name
        m = re.match(r'^([A-Za-z]*)-?(\d+)$', base_name)
        if m:
            serie = m.group(1).upper()
            folio = m.group(2)
            
        folio_clean = str(folio).lstrip('0') if folio else ""
        if not folio_clean: folio_clean = "0"
        
        query = select(Cfdi).where(
            Cfdi.entidad_id == entidad_id,
            Cfdi.folio == folio_clean
        )
        if serie:
            query = query.where(Cfdi.serie == serie)
            
        result = await self.db.execute(query.order_by(Cfdi.issue_date.desc()))
        cfdi = result.scalars().first()
        
        if cfdi:
            fecha = cfdi.issue_date
            base_dir = os.path.join(os.getcwd(), "storage", "tenants", str(entidad_id), str(fecha.year), f"{fecha.month:02d}")
            os.makedirs(base_dir, exist_ok=True)
            destino_pdf = os.path.join(base_dir, f"{cfdi.uuid}.pdf")
            
            try:
                import shutil
                shutil.move(ruta_pdf, destino_pdf)
                cfdi.pdf_file_path = destino_pdf
                await self.db.commit()
                return cfdi
            except Exception as e:
                logger.error(f"Error moviendo PDF huérfano: {str(e)}")
                return None
        return None

    async def _read_file_with_retry(self, path: str, retries: int = 5, delay: float = 1.0) -> bytes:
        """
        [ES] Re-intento de lectura para evitar colisiones en Windows.
        [EN] Read retry to avoid Windows file collisions.
        """
        for i in range(retries):
            try:
                with open(path, 'rb') as f:
                    return f.read()
            except IOError:
                if i == retries - 1:
                    raise
                time.sleep(delay * (2 ** i))
        return b""

    def _parse_cfdi_deep(self, content: bytes, filename: str = None) -> Dict[str, Any]:
        """
        [ES] Deep Parsing de Vantec para extraer metadatos y relaciones.
        [EN] Vantec Deep Parsing to extract metadata and relationships.
        """
        root = ET.fromstring(content)
        namespaces = {
            'cfdi': root.tag.split('}')[0].strip('{'),
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        
        version = root.get('Version') or root.get('version')
        tipo = root.get('TipoDeComprobante') or root.get('tipoDeComprobante')
        metodo = root.get('MetodoPago') or root.get('metodoPago')
        forma = root.get('FormaPago') or root.get('formaPago')
        serie = root.get('Serie') or root.get('serie')
        folio = root.get('Folio') or root.get('folio')

        # Vantec Normalization: Priorizar Nombre Físico & Quitar Ceros
        if filename:
            import re
            base_name = os.path.splitext(filename)[0].upper()
            m = re.match(r'^([A-Z]*)-?(\d+)$', base_name)
            if m:
                ext_serie = m.group(1)
                ext_folio = m.group(2)
                if ext_folio:
                    folio = ext_folio
                if ext_serie:
                    serie = ext_serie

        if folio:
            folio = str(folio).lstrip('0')
            if not folio:
                folio = "0"
        fecha_str = root.get('Fecha') or root.get('fecha')
        total_str = root.get('Total') or root.get('total')
        
        tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
        cfdi_uuid = tfd.get('UUID') if tfd is not None else None
        
        if not cfdi_uuid:
            raise ValueError("UUID no encontrado / UUID not found in XML.")

        emisor = root.find('.//{*}Emisor')
        rfc_emisor = emisor.get('Rfc') if emisor is not None else "ERROR"
        receptor = root.find('.//{*}Receptor')
        rfc_receptor = receptor.get('Rfc') if receptor is not None else "ERROR"

        conceptos = []
        conceptos_node = root.find('.//{*}Conceptos')
        if conceptos_node is not None:
            for c in conceptos_node.findall('{*}Concepto'):
                conceptos.append({
                    "clave": c.get('ClaveProdServ'),
                    "descripcion": c.get('Descripcion'),
                    "cantidad": c.get('Cantidad'),
                    "importe": c.get('Importe'),
                    "valor_unitario": c.get('ValorUnitario'),
                    "descuento": c.get('Descuento')
                })

        # Relaciones
        relaciones = []
        cfdi_rel_node = root.find('.//{*}CfdiRelacionados')
        if cfdi_rel_node is not None:
            tipo_rel = cfdi_rel_node.get('TipoRelacion')
            for rel in cfdi_rel_node.findall('{*}CfdiRelacionado'):
                relaciones.append({
                    "uuid_relacionado": rel.get('UUID'),
                    "tipo_relacion": tipo_rel,
                    "monto_pagado": None,
                    "saldo_insoluto": None,
                    "num_parcialidad": None
                })

        # Vantec Multiversion: Complemento de Pagos 1.0 & 2.0 con XPath Wildcard
        pagos_node = root.find('.//{*}Pagos')
        monto_total_pagos = None
        
        if pagos_node is not None:
            # 1. Totales (Solo en Pago 2.0)
            totales_node = pagos_node.find('{*}Totales')
            if totales_node is not None:
                monto_total_pagos = totales_node.get('MontoTotalPagos')
                logger.info(f"💰 Vantec Intelligence: MontoTotalPagos extraído: {monto_total_pagos}")

            # 2. Iterar Pagos (V1.0 & V2.0)
            for pago in pagos_node.findall('{*}Pago'):
                for doc_rel in pago.findall('{*}DoctoRelacionado'):
                    relaciones.append({
                        "uuid_relacionado": doc_rel.get('IdDocumento'),
                        "tipo_relacion": "PAGO",
                        "monto_pagado": float(doc_rel.get('ImpPagado') or doc_rel.get('ImpPagado') or 0),
                        "saldo_insoluto": float(doc_rel.get('ImpSaldoInsoluto') or 0),
                        "num_parcialidad": int(doc_rel.get('NumParcialidad') or 1)
                    })
        
        # Normalizar Total para el modelo Cfdi
        final_total = float(total_str)
        if tipo == 'P' and monto_total_pagos:
            final_total = float(monto_total_pagos)
        elif tipo == 'P' and not monto_total_pagos:
            # Fallback a suma de ImpPagado si no hay nodo Totales (Pago 1.0)
            final_total = sum(r["monto_pagado"] for r in relaciones if r["tipo_relacion"] == "PAGO")

        metadata = {
            "version": version,
            "conceptos": conceptos,
            "relaciones_extraidas": len(relaciones),
            "emisor": {"rfc": rfc_emisor, "nombre": emisor.get('Nombre') if emisor is not None else ""},
            "receptor": {"rfc": rfc_receptor, "nombre": receptor.get('Nombre') if receptor is not None else ""},
            "subtotal": root.get('SubTotal') or root.get('subTotal'),
            "timbrado": {
                "uuid": cfdi_uuid,
                "fecha": tfd.get('FechaTimbrado'),
                "rfc_prov": tfd.get('RfcProvCertif')
            },
            "ingesta": {
                "fecha_servidor": datetime.now().isoformat(),
                "entorno": "ON-PREMISE"
            }
        }

        # Extraer Impuestos para el Drawer
        impuestos_node = root.find('.//{*}Impuestos')
        if impuestos_node is not None:
            metadata["impuestos"] = {
                "total_trasladados": impuestos_node.get('TotalImpuestosTrasladados')
            }

        return {
            "uuid": cfdi_uuid,
            "rfc_emisor": rfc_emisor,
            "rfc_receptor": rfc_receptor,
            "issue_date": datetime.fromisoformat(fecha_str),
            "total": final_total,
            "version": version,
            "tipo_comprobante": tipo,
            "metodo_pago": metodo,
            "forma_pago": forma,
            "serie": serie,
            "folio": folio,
            "metadata_xml": metadata,
            "relaciones": relaciones,
            "parent_uuid": self._extraer_parent_uuid_de_pago(root) if tipo == 'P' else None
        }

    def _extraer_parent_uuid_de_pago(self, root: Any) -> Optional[str]:
        """
        [ES] Extrae el UUID padre de un complemento de pago.
        [EN] Extracts the parent UUID from a payment complement.
        """
        docto_relacionado = root.find('.//{*}DoctoRelacionado')
        return docto_relacionado.get('IdDocumento') if docto_relacionado is not None else None

    def _asegurar_en_boveda_dual(
        self, 
        ruta_xml: str, 
        ruta_pdf: Optional[str], 
        entidad_id: uuid.UUID, 
        cfdi_uuid: str, 
        fecha: datetime
    ) -> tuple:
        """
        [ES] Mueve XML y PDF a la bóveda con renombrado determinista (UUID).
        [EN] Moves XML and PDF to the vault with deterministic renaming (UUID).
        """
        base_dir = os.path.join(os.getcwd(), "storage", "tenants", str(entidad_id), str(fecha.year), f"{fecha.month:02d}")
        os.makedirs(base_dir, exist_ok=True)
        
        destino_xml = os.path.join(base_dir, f"{cfdi_uuid}.xml")
        shutil.move(ruta_xml, destino_xml)
        
        destino_pdf = None
        if ruta_pdf and os.path.exists(ruta_pdf):
            destino_pdf = os.path.join(base_dir, f"{cfdi_uuid}.pdf")
            shutil.move(ruta_pdf, destino_pdf)
            
        return destino_xml, destino_pdf

