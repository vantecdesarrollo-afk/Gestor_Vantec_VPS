import asyncio
from sqlalchemy import text
from src.database.session import engine

async def script():
    async with engine.begin() as conn:
        print("🛠️ Nivelando columnas de 'comprobantes'...")
        columnas = [
            ("nombre_emisor", "VARCHAR(255)"),
            ("nombre_receptor", "VARCHAR(255)"),
            ("estatus_sat", "VARCHAR(20)"),
            ("ruta_resguardo", "VARCHAR(500)"),
            ("metodo_pago", "VARCHAR(10)"),
            ("forma_pago", "VARCHAR(2)"),
            ("moneda", "VARCHAR(3)"),
            ("tipo_comprobante", "VARCHAR(1)")
        ]
        for col, tipo in columnas:
            await conn.execute(text(f"ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS {col} {tipo};"))
        
        # IMPORTANTE: Asegurar que 'uuid' sea la llave primaria y no 'id'
        print("✅ Columnas sincronizadas.")

if __name__ == "__main__":
    asyncio.run(script())