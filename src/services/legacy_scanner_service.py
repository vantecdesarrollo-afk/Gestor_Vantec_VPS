import os
import logging
from pathlib import Path
from uuid import UUID
from datetime import datetime
import defusedxml.ElementTree as ET
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database.models import Cfdi, EntidadFiscal, CfdiRelacionado
from src.database.session import AsyncSessionLocal

# Configuración básica de logging para el servicio
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegacyScanner")

class LegacyScannerService:
    """
    Servicio Senior para el escaneo e indexación de comprobanteslegacy (Zero-Copy).
    Soporta relaciones complejas, CRP y bucles de iteración sobre nodos XML.
    """

    async def scan_directory(self, tenant_id: UUID, base_path: str):
        """
        Escanea recursivamente el directorio base buscando archivos XML de CFDI.
        Implementa validación de Tenant y Resiliencia en el indexado masivo.
        """
        base_path_obj = Path(base_path)
        if not base_path_obj.exists() or not base_path_obj.is_dir():
            print(f"[!] Error: La ruta no existe o no es un directorio: {base_path}")
            return 0

        indexados = 0
        errores = 0
        duplicados = 0
        total_encontrados = 0

        print(f"\n[+] Vantec Scanner -> Iniciando escaneo en: {base_path}")
        print(f"[+] Tenant ID: {tenant_id}")

        async with AsyncSessionLocal() as db:
            # Validación de Entidad (Diagnóstico Vantec)
            entidad_check = await db.execute(select(EntidadFiscal).where(EntidadFiscal.id == tenant_id))
            if not entidad_check.scalar_one_or_none():
                print(f"\n[!] Error crítico: La Entidad ID {tenant_id} no existe en la base de datos.")
                return 0

            # rglob('*.xml') navega automáticamente por subcarpetas de rangos
            for xml_file in base_path_obj.rglob('*.xml'):
                total_encontrados += 1
                try:
                    resultado = await self._process_xml_file(tenant_id, xml_file, db)
                    
                    if resultado == "INDEXED":
                        indexados += 1
                    elif resultado == "DUPLICATE":
                        duplicados += 1
                    
                    if total_encontrados % 10 == 0:
                        print(f" [+] Progreso: {indexados} indexados, {duplicados} duplicados, {errores} errores...")
                        
                except Exception as e:
                    errores += 1
                    print(f"[!] ERROR DE BD en {xml_file.absolute()}: {str(e)}")
                    continue

        print(f"\n[=] Escaneo finalizado:")
        print(f" -> Total encontrados: {total_encontrados}")
        print(f" -> Total indexados: {indexados}")
        print(f" -> Duplicados omitidos: {duplicados}")
        print(f" -> Errores omitidos: {errores}")
        return indexados

    async def _process_xml_file(self, tenant_id: UUID, xml_path: Path, db: AsyncSession):
        """
        Parsea un archivo XML, extrae metadatos y relaciones múltiples.
        Implementa soporte para CFDI 3.3, 4.0 y Complementos de Pago.
        """
        try:
            with open(xml_path, 'rb') as f:
                content = f.read()
                root = ET.fromstring(content)

            # Namespaces dinámicos por versión
            namespaces = {
                'cfdi': root.tag.split('}')[0].strip('{'),
                'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
                'pago10': 'http://www.sat.gob.mx/Pagos',
                'pago20': 'http://www.sat.gob.mx/Pagos20'
            }

            # 1. Metadatos Base (SAT PascalCase Priority)
            version = root.get('Version') or root.get('version')
            tipo_comprobante = root.get('TipoDeComprobante') or root.get('tipoDeComprobante')
            serie = root.get('Serie') or root.get('serie')
            folio = root.get('Folio') or root.get('folio')
            fecha_str = root.get('Fecha') or root.get('fecha')
            total_str = root.get('Total') or root.get('total') or "0"
            
            emisor = root.find('.//cfdi:Emisor', namespaces)
            rfc_emisor = emisor.get('Rfc') if emisor is not None else "UNKNOWN"
            receptor = root.find('.//cfdi:Receptor', namespaces)
            rfc_receptor = receptor.get('Rfc') if receptor is not None else "UNKNOWN"
            
            tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
            if tfd is None: raise ValueError("Nodo TFD faltante.")
            cfdi_uuid = tfd.get('UUID')

            # 2. Inserción o Actualización del Documento Maestro (Upsert Logic Vantec)
            try:
                # Verificar si ya existe para esta entidad
                existing_q = await db.execute(select(Cfdi).where(Cfdi.uuid == cfdi_uuid, Cfdi.entidad_id == tenant_id))
                existing_cfdi = existing_q.scalar_one_or_none()

                if existing_cfdi:
                    print(f" [+] Actualizando CFDI existente: {cfdi_uuid} ({serie}-{folio})")
                    existing_cfdi.tipo_comprobante = tipo_comprobante
                    existing_cfdi.serie = serie
                    existing_cfdi.folio = folio
                    existing_cfdi.issue_date = datetime.fromisoformat(fecha_str) # Asegurar sincronía
                    existing_cfdi.total = float(total_str)
                    
                    # Guardar cambios
                    await db.commit()
                    await db.refresh(existing_cfdi)
                    new_cfdi = existing_cfdi
                    status_res = "UPDATED"
                else:
                    new_cfdi = Cfdi(
                        entidad_id=tenant_id,
                        uuid=cfdi_uuid,
                        rfc_emisor=rfc_emisor,
                        rfc_receptor=rfc_receptor,
                        issue_date=datetime.fromisoformat(fecha_str),
                        total=float(total_str),
                        version=version or "N/A",
                        tipo_comprobante=tipo_comprobante,
                        serie=serie,
                        folio=folio,
                        xml_file_path=str(xml_path.absolute()),
                        pdf_file_path=str(xml_path.with_suffix('.pdf').absolute()) if xml_path.with_suffix('.pdf').exists() else None,
                        source_type='LEGACY_EMISION',
                        status='VALID'
                    )
                    db.add(new_cfdi)
                    await db.commit()
                    await db.refresh(new_cfdi)
                    status_res = "INDEXED"

            except Exception as e:
                await db.rollback()
                print(f" [!] Error al procesar registro: {str(e)}")
                return "ERROR"

            # 3. EXTRACCIÓN DE RELACIONES (Loop sobre nodos)
            relaciones_list = []

            # A) Nodos <cfdi:CfdiRelacionados>
            rel_root = root.find('.//cfdi:CfdiRelacionados', namespaces)
            if rel_root is not None:
                tipo_rel = rel_root.get('TipoRelacion')
                for node in rel_root.findall('.//cfdi:CfdiRelacionado', namespaces):
                    rel_uuid = node.get('UUID')
                    if rel_uuid:
                        relaciones_list.append(CfdiRelacionado(
                            cfdi_id=new_cfdi.cfdi_id,
                            uuid_padre=cfdi_uuid,
                            uuid_relacionado=rel_uuid,
                            tipo_relacion=tipo_rel
                        ))

            # B) Complemento de Pago (CRP 1.0 y 2.0)
            if tipo_comprobante == 'P':
                # Buscamos en ambos namespaces de pagos
                for ns in ['pago10', 'pago20']:
                    doctos = root.findall(f'.//{ns}:DoctoRelacionado', namespaces)
                    for dr in doctos:
                        rel_uuid = dr.get('IdDocumento')
                        imp_pagado = dr.get('ImpPagado') or dr.get('impPagado')
                        imp_saldo = dr.get('ImpSaldoInsoluto') or dr.get('impSaldoInsoluto')
                        parcialidad = dr.get('NumParcialidad') or dr.get('numParcialidad')

                        if rel_uuid:
                            relaciones_list.append(CfdiRelacionado(
                                cfdi_id=new_cfdi.cfdi_id,
                                uuid_padre=cfdi_uuid,
                                uuid_relacionado=rel_uuid,
                                tipo_relacion='PAGO',
                                monto_pagado=float(imp_pagado) if imp_pagado else 0,
                                saldo_insoluto=float(imp_saldo) if imp_saldo else 0,
                                num_parcialidad=int(parcialidad) if parcialidad else None
                            ))

            # 4. Persistencia masiva de relaciones para este archivo
            if relaciones_list:
                db.add_all(relaciones_list)
                await db.commit()

            return "INDEXED"

        except Exception as e:
            raise e
