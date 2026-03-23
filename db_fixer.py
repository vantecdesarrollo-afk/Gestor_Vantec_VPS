import asyncio
from sqlalchemy import text
from src.database.session import engine

async def run_fix():
    print("🚀 Iniciando reparación de la base de datos...")
    async with engine.begin() as conn:
        try:
            # 1. Agregar columna 'id' si no existe
            await conn.execute(text("ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;"))
            print("✅ Columna 'id' verificada/creada.")

            # 2. Agregar el resto de columnas necesarias
            columns = [
                "moneda VARCHAR(3)",
                "estatus_sat VARCHAR(20)",
                "ruta_resguardo VARCHAR(500)"
            ]
            
            for col in columns:
                await conn.execute(text(f"ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS {col};"))
            
            print("✅ Columnas moneda, estatus_sat y ruta_resguardo verificadas/creadas.")
            print("\n🔥 Base de datos sincronizada. Ya puedes borrar este archivo y correr el server.")
            
        except Exception as e:
            print(f"\n❌ Error al reparar: {e}")

if __name__ == "__main__":
    asyncio.run(run_fix())