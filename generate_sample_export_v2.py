import asyncio, csv, os, sys, uuid
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, cast, String
from src.database.models import Comprobante
from src.database.models_dashboard_opt import DashCfdiDocument

DB_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"
engine = create_async_engine(DB_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    async with AsyncSessionLocal() as db:
        print("[+] Cargando Comprobantes para reporte aplanado...")
        query = (
            select(Comprobante, DashCfdiDocument.subtotal)
            .options(selectinload(Comprobante.relacionados))
            .outerjoin(DashCfdiDocument, cast(Comprobante.uuid, String) == DashCfdiDocument.uuid_fiscal)
        )
        res = await db.execute(query)
        rows = res.all()
        print(f"[+] Encontrados {len(rows)} registros.")

        output_path = r"C:\Users\erobl\.gemini\antigravity\brain\0635ee82-117f-46ee-8915-cc4a1be11ad0\sample_export_aplanado.csv"
        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "UUID", "Serie", "Folio", "Fecha", "RFC Emisor", "Nombre Emisor", 
                "RFC Receptor", "Nombre Receptor", "Tipo", "Moneda", "Subtotal", "Impuestos", "Total", 
                "Método Pago", "Forma Pago", "Estatus Inteligente", 
                "Monto Pagado", "UUID Relacionado", "Num Parcialidad", "Saldo Anterior", "Saldo Insoluto"
            ])
            for item in rows:
                r = item[0]
                subtotal = float(item[1] or r.total or 0)
                impuestos = float(r.total or 0) - subtotal
                
                est_int = "Vigente"
                if r.metodo_pago == 'PUE': est_int = "Pagado"
                elif r.metodo_pago == 'PPD':
                    if not r.relacionados: est_int = "Pendiente"
                    else:
                        tot_pag = sum(float(rel.monto_pagado or 0) for rel in r.relacionados)
                        est_int = "Pagado" if tot_pag >= float(r.total or 0) else "Parcial"
                        
                if r.relacionados:
                    for rel in r.relacionados:
                        writer.writerow([
                            str(r.uuid), r.serie or "", r.folio or "", r.fecha_emision,
                            r.rfc_emisor, r.nombre_emisor, r.rfc_receptor, r.nombre_receptor,
                            r.tipo_comprobante, r.moneda, subtotal, impuestos, float(r.total or 0),
                            r.metodo_pago, r.forma_pago, est_int,
                            float(rel.monto_pagado or 0), str(rel.uuid_relacionado), rel.num_parcialidad or "-",
                            float(rel.saldo_insoluto or 0) + float(rel.monto_pagado or 0), float(rel.saldo_insoluto or 0)
                        ])
                else:
                    writer.writerow([
                        str(r.uuid), r.serie or "", r.folio or "", r.fecha_emision,
                        r.rfc_emisor, r.nombre_emisor, r.rfc_receptor, r.nombre_receptor,
                        r.tipo_comprobante, r.moneda, subtotal, impuestos, float(r.total or 0),
                        r.metodo_pago, r.forma_pago, est_int,
                        "-", "-", "-", "-", "-"
                    ])
        print(f"[+] Reporte exportado en {output_path}")

try:
    asyncio.run(main())
except Exception as e:
    print(f"Error: {e}")
