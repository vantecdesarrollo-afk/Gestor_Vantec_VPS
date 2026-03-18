import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal
from src.database.models import CfdiRelacionado

async def insert():
    async with AsyncSessionLocal() as session:
        # Prender RLS
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', 'e6f64bb0-3971-4cc8-b883-cd183eca77d7', true)")
        )

        res_id = await session.execute(text("SELECT id FROM cfdis WHERE uuid = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1'"))
        comp_id = res_id.scalar()
        print(f"Found cfdi_id: {comp_id}")

        # Borrar anterior si existiera
        await session.execute(
            text("DELETE FROM cfdi_relacionados WHERE uuid_padre = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1' AND uuid_relacionado = 'd1d1f7d4-7683-4f46-a545-5e08c907cb11'")
        )
        
        if comp_id:
             # Usar ORM
             nueva_relacion = CfdiRelacionado(
                 cfdi_id=comp_id,
                 uuid_padre='d2a9308b-f4d9-4357-8adf-de186a7ef5d1',
                 uuid_relacionado='d1d1f7d4-7683-4f46-a545-5e08c907cb11',
                 tipo_relacion='PAGO',
                 monto_pagado=28820.03,
                 saldo_insoluto=0.00,
                 num_parcialidad=1
             )
             session.add(nueva_relacion)
             await session.commit()
             print("ORM Relation inserted and committed.")
        else:
             print("Skipping insert due to missing cfdi_id anchor.")

if __name__ == "__main__":
    try:
         asyncio.run(insert())
    except Exception as e:
         import json
         with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\insert_error_log.json", "w") as f:
              json.dump({"error": str(e)}, f)
         print(f"Error saved: {e}")
