import asyncio
import os
import glob
import xml.etree.ElementTree as ET
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.core.config import settings

# ⚠️ RUTAS Y CONFIGURACIÓN
DIRECTORIO_CFDIS = r"C:\ITC\Fappeal\Planeta\Outfile\SAT\Factura\0-2K" 
ENTIDAD_ID = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def sync_folder():
    async with async_session() as db:
        print("🧹 1. Purgando datos viejos...")
        
        try:
            await db.execute(text("ALTER TABLE cfdi_relacionados DROP CONSTRAINT IF EXISTS cfdi_relacionados_cfdi_id_fkey"))
            await db.commit()
        except Exception:
            await db.rollback()

        await db.execute(text(f"DELETE FROM cfdi_relacionados WHERE cfdi_id IN (SELECT uuid FROM comprobantes WHERE entidad_id = '{ENTIDAD_ID}')"))
        await db.execute(text(f"DELETE FROM comprobantes WHERE entidad_id = '{ENTIDAD_ID}'"))
        await db.commit()
        print("✅ Base de datos limpia.")

        print(f"📂 2. Leyendo archivos en {DIRECTORIO_CFDIS}...")
        archivos_xml = glob.glob(os.path.join(DIRECTORIO_CFDIS, "*.xml"))
        
        for ruta_xml in archivos_xml:
            nombre_archivo = os.path.basename(ruta_xml)
            try:
                tree = ET.parse(ruta_xml)
                root = tree.getroot()
                
                version = root.get('Version') or root.get('version') or "4.0"
                serie = root.get('Serie') or root.get('serie') or ""
                folio = root.get('Folio') or root.get('folio') or ""
                fecha_str = root.get('Fecha') or root.get('fecha')
                total = float(root.get('Total') or root.get('total') or 0)
                tipo_comp = root.get('TipoDeComprobante') or root.get('tipoDeComprobante') or "I"
                
                # 🛠️ CORRECCIÓN DE MÉTODO Y FORMA DE PAGO PARA COMPLEMENTOS 'P'
                metodo_pago = root.get('MetodoPago') or root.get('metodoPago') or ""
                forma_pago = root.get('FormaPago') or root.get('formaPago') or ""
                
                if tipo_comp.upper() == 'P':
                    metodo_pago = "---" # Los Pagos no llevan MetodoPago en la raíz
                    # Extraer la FormaDePagoP del complemento si existe
                    pago_nodo = root.find('.//{*}Pago')
                    if pago_nodo is not None:
                        forma_pago = pago_nodo.get('FormaDePagoP') or forma_pago
                else:
                    if not metodo_pago:
                        metodo_pago = "PUE" # Fallback de seguridad para Ingresos/Egresos

                fecha_dt = None
                if fecha_str:
                    try:
                        clean_date_str = fecha_str.split('.')[0].replace('Z', '')
                        fecha_dt = datetime.fromisoformat(clean_date_str)
                    except Exception:
                        fecha_dt = datetime.now()
                else:
                     fecha_dt = datetime.now()

                emisor = root.find('.//{*}Emisor')
                rfc_emisor = emisor.get('Rfc') if emisor is not None else "DESCONOCIDO"
                
                receptor = root.find('.//{*}Receptor')
                rfc_receptor = receptor.get('Rfc') if receptor is not None else "DESCONOCIDO"
                
                tfd = root.find('.//{*}TimbreFiscalDigital')
                cfdi_uuid = tfd.get('UUID') if tfd is not None else None
                
                if not cfdi_uuid:
                    continue

                query_insert_comp = text("""
                    INSERT INTO comprobantes 
                    (uuid, serie, folio, rfc_emisor, rfc_receptor, version, total, ruta_resguardo, fecha_emision, entidad_id, tipo_comprobante, metodo_pago, forma_pago, status)
                    VALUES (:uuid, :serie, :folio, :rfc_emisor, :rfc_receptor, :version, :total, :ruta_resguardo, :fecha_emision, :entidad_id, :tipo_comprobante, :metodo_pago, :forma_pago, :status)
                """)
                await db.execute(query_insert_comp, {
                    "uuid": cfdi_uuid.lower(), "serie": serie, "folio": folio,
                    "rfc_emisor": rfc_emisor, "rfc_receptor": rfc_receptor,
                    "version": version, "total": total, "ruta_resguardo": ruta_xml,
                    "fecha_emision": fecha_dt, "entidad_id": ENTIDAD_ID,
                    "tipo_comprobante": tipo_comp, "metodo_pago": metodo_pago,
                    "forma_pago": forma_pago, "status": "VALID"
                })

                if tipo_comp.upper() == 'P':
                    relacionados = root.findall('.//{*}DoctoRelacionado')
                    for rel in relacionados:
                        id_doc_pagado = rel.get('IdDocumento')
                        monto_pagado = float(rel.get('ImpPagado') or 0)
                        
                        if id_doc_pagado:
                            query_insert_rel = text("""
                                INSERT INTO cfdi_relacionados (cfdi_id, uuid_padre, uuid_relacionado, tipo_relacion, monto_pagado)
                                VALUES (:cfdi_id, :uuid_padre, :uuid_relacionado, :tipo_relacion, :monto_pagado)
                            """)
                            await db.execute(query_insert_rel, {
                                "cfdi_id": cfdi_uuid.lower(),
                                "uuid_padre": id_doc_pagado.lower(), 
                                "uuid_relacionado": cfdi_uuid.lower(), 
                                "tipo_relacion": "PAGO",
                                "monto_pagado": monto_pagado
                            })
                            print(f"   🔗 Relación creada: Pago {folio} cubre factura {id_doc_pagado} por ${monto_pagado}")

                await db.commit()
                print(f"📥 Ingestado OK: {folio} ({cfdi_uuid}) - Tipo: {tipo_comp}")

            except Exception as e:
                await db.rollback()
                print(f"❌ Error al procesar el archivo {nombre_archivo}. Motivo real: {e}")

        print("🚀 Sincronización completada. Base de datos sellada.")

if __name__ == "__main__":
    asyncio.run(sync_folder())