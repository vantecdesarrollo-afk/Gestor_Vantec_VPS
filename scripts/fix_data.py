import asyncio
import logging
import defusedxml.ElementTree as ET
from pathlib import Path
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataFix")

async def fix_cfdi_data():
    async with AsyncSessionLocal() as db:
        # Buscar CFDIs con campos críticos vacíos
        result = await db.execute(
            select(Cfdi).where(
                (Cfdi.serie == None) | (Cfdi.folio == None) | (Cfdi.tipo_comprobante == None) |
                (Cfdi.serie == "") | (Cfdi.folio == "")
            )
        )
        cfdis = result.scalars().all()
        
        logger.info(f"Encontrados {len(cfdis)} registros para reparar.")
        
        reparados = 0
        for cfdi in cfdis:
            xml_path = Path(cfdi.xml_file_path)
            if not xml_path.exists():
                logger.warning(f"Archivo XML no encontrado: {xml_path}")
                continue
                
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Extracción estricta PascalCase (SAT Standard)
                serie = root.get('Serie')
                folio = root.get('Folio')
                tipo = root.get('TipoDeComprobante')
                
                logger.info(f"Procesando {cfdi.uuid}: Serie={serie}, Folio={folio}, Tipo={tipo}")
                
                cfdi.serie = serie
                cfdi.folio = folio
                cfdi.tipo_comprobante = tipo
                
                reparados += 1
            except Exception as e:
                logger.error(f"Error procesando {cfdi.uuid}: {e}")
                
        if reparados > 0:
            await db.commit()
            logger.info(f"Éxito: {reparados} registros actualizados en la base de datos.")
        else:
            logger.info("No se requirieron actualizaciones.")

if __name__ == "__main__":
    asyncio.run(fix_cfdi_data())
