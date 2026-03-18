import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def find_xml_path():
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(Comprobante).where(Comprobante.folio == '0000000303'))
            c = res.scalar_one_or_none()
            if c:
                log(f"Folio 303: UUID={c.uuid}, Ruta={c.ruta_resguardo}")
            else:
                log("Folio 303 not found.")
                
            res = await session.execute(select(Comprobante).where(Comprobante.folio == '0000000305'))
            c2 = res.scalar_one_or_none()
            if c2:
                log(f"Folio 305: UUID={c2.uuid}, Ruta={c2.ruta_resguardo}")
        except Exception as e:
            log(f"Error: {e}")
            
    with open("find_xml_path_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(find_xml_path())
