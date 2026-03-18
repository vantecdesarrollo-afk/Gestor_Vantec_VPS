import os
import json
import asyncio
from watcher import main
from src.database.session import AsyncSessionLocal
from src.database.models import Tenant
from sqlalchemy import select

async def run():
    t_id = 'e6f64bb0-3971-4cc8-b883-cd183eca77d7'
    os.environ['WATCHER_ZONES'] = json.dumps({r'C:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload': t_id})
    print('Starting authentic Watcher loop for:', t_id)
    await main()



if __name__ == '__main__':
    asyncio.run(run())
