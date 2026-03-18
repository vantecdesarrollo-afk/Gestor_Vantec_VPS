import asyncio
import uuid
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def fix_data():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    
    # UUIDs de los documentos involucrados
    # Folio 303 (Pago): d2a9308b-f4d9-4357-8adf-de186a7ef5d1
    # Folio 800 (Invoice): d1d1f7d4-7683-4f46-a545-5e08c907cb11
    # Folio 305 (Pago): af41872d-1e12-44ec-9d58-614b23e9655c
    
    print("Running final database fixes...")
    
    async with AsyncSessionLocal() as session:
        # Prender RLS
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        
        # 1. Update Totales para Pagos (para que no salgan en 0)
        # Folio 305: $106,575.00
        await session.execute(
            text("UPDATE comprobantes SET total = 106575.00 WHERE uuid = 'af41872d-1e12-44ec-9d58-614b23e9655c'")
        )
        print("Updated Folio 305 Total to 106575.00")
        
        # Folio 303: $28,820.03
        await session.execute(
            text("UPDATE comprobantes SET total = 28820.03 WHERE uuid = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1'")
        )
        print("Updated Folio 303 Total to 28820.03")
        
        # 2. Insertar relación faltante para Folio 800 (UUID: d1d1f7d4...) vinculando a 303 (UUID: d2a9308b...)
        # Primero borrar si ya existe para evitar duplicado
        await session.execute(
            text("DELETE FROM cfdi_relacionados WHERE uuid_padre = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1' AND uuid_relacionado = 'd1d1f7d4-7683-4f46-a545-5e08c907cb11'")
        )
        
        # Buscar el ID del cfdi 303 (Cfdi model) o solo insertar con uuid_padre
        # En el modelo CfdiRelacionado, cfdi_id suele ser el ID interno de la tabla comprobantes del PAGO.
        res_comp = await session.execute(text("SELECT id FROM cfdis WHERE uuid = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1'"))
        comp_id = res_comp.scalar()
        
        if comp_id:
             await session.execute(
                 text("""
                     INSERT INTO cfdi_relacionados (cfdi_id, uuid_padre, uuid_relacionado, tipo_relacion, monto_pagado, saldo_insoluto, num_parcialidad)
                     VALUES (:cfdi_id, 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1', 'd1d1f7d4-7683-4f46-a545-5e08c907cb11', 'PAGO', 28820.03, 0.00, 1)
                 """),
                 {"cfdi_id": comp_id}
             )
             print("Inserted missing relation from 303 to 800 for count recalculation.")

        await session.commit()
        print("All live database updates committed.")

if __name__ == "__main__":
    try:
         asyncio.run(fix_data())
    except Exception as e:
         with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\error_log.txt", "w") as f:
              f.write(str(e))
         print(f"Error saved: {e}")
