import asyncio
import os
import tempfile
from sqlalchemy import select, cast, String
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi
from src.api.endpoints.orquestador import reenvio_comprobante, ReenvioRequest

async def m():
    db = AsyncSessionLocal()
    r = ReenvioRequest(
        uuid_documento='D1D1F7D4-7683-4F46-A545-5E08C907CB11', 
        destinatario='test@test.com', 
        asunto='test', 
        cuerpo='test'
    )
    try:
        res = await reenvio_comprobante(r, db)
        print("RES:", res)
        tmp_dir = tempfile.gettempdir()
        log_paths = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if f.startswith("cmd_args_")]
        for l in log_paths:
            print("FILE:", l)
            with open(l, 'r') as f:
                print(f.read())
    except Exception as e:
        print("Err:", e)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(m())
