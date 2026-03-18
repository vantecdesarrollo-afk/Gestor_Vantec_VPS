import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def do_insert():
    async with AsyncSessionLocal() as session:
        # Prender RLS
        await session.execute(text("SELECT set_config('app.current_tenant_id', 'e6f64bb0-3971-4cc8-b883-cd183eca77d7', true)"))

        # Buscar cfdi_id del PAGO (Folio 303)
        res_id = await session.execute(text("SELECT id FROM cfdis WHERE uuid = 'd2a9308b-f4d9-4357-8adf-de186a7ef5d1'"))
        comp_id = res_id.scalar()
        print(f"Found cfdi_id: {comp_id}")

        if not comp_id:
             print("Missing cfdi_id, attempting fallback or search other way...")
             # Fallback: buscar cfdi_id del Invoice o similar? No, relation needs Pago link usually.
    
        # Borrar anterior si existiera
        await session.execute(
            text("DELETE FROM cfdi_relacionados WHERE uuid_padre ILIKE 'd2a9308b%' AND uuid_relacionado ILIKE 'd1d1f7d4%'")
        )

        if comp_id:
             # INSERT RAW con UPPERCASE
             await session.execute(
                 text("""
                     INSERT INTO cfdi_relacionados (cfdi_id, uuid_padre, uuid_relacionado, tipo_relacion, monto_pagado, saldo_insoluto, num_parcialidad)
                     VALUES (:cfdi_id, 'D2A9308B-F4D9-4357-8ADF-DE186A7EF5D1', 'D1D1F7D4-7683-4F46-A545-5E08C907CB11', 'PAGO', 28820.03, 0.00, 1)
                 """),
                 {"cfdi_id": comp_id}
             )
             await session.commit()
             print("RAW Uppercase Relation inserted and committed.")
        else:
             print("No insert made due to missing cfdi_id.")

if __name__ == "__main__":
    asyncio.run(do_insert())
