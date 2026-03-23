import sys
import asyncio
from sqlalchemy import select, func, cast, String
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, CfdiRelacionado
from collections import defaultdict

async def test_dashboard():
    # Redirect stdout to a file for review
    with open("debug_analytics_output.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        
        async with AsyncSessionLocal() as db:
            try:
                # Find a valid entidad_id first
                e_q = select(Comprobante.entidad_id).limit(1)
                e_res = await db.execute(e_q)
                entidad_id = e_res.scalar()
                
                if not entidad_id:
                    print("No entidad_id found in Comprobantes table")
                    return

                print(f"Testing with Entidad: {entidad_id}")

                query = select(Comprobante).where(Comprobante.entidad_id == entidad_id)
                result = await db.execute(query)
                data = result.scalars().all()
                
                print(f"Found {len(data)} comprobantes")
                
                ingresos = 0.0
                puntos_grafica = defaultdict(float)

                for c in data:
                    monto = float(c.total or 0)
                    if c.tipo_comprobante == 'P':
                        sq = select(func.sum(CfdiRelacionado.monto_pagado)).where(
                            cast(CfdiRelacionado.cfdi_id, String) == str(c.uuid)
                        )
                        res_sq = await db.execute(sq)
                        val = res_sq.scalar()
                        monto = float(val) if val is not None else 0.0
                        print(f"REP Payment {c.uuid} parsed monto: {monto}")
                    
                    if c.tipo_comprobante in ['I', 'P']:
                        ingresos += monto
                        if c.fecha_emision:
                            label = c.fecha_emision.strftime("%d/%m")
                            puntos_grafica[label] += monto

                print("\n=== RESULTS ===")
                print(f"Total Ingresos: {ingresos}")
                print(f"Charts labels: {list(puntos_grafica.keys())}")
                print(f"Charts values: {list(puntos_grafica.values())}")

            except Exception as e:
                import traceback
                print(f"\n!!! EXCEPTION !!!\n{e}")
                traceback.print_exc(file=f)

if __name__ == "__main__":
    asyncio.run(test_dashboard())
