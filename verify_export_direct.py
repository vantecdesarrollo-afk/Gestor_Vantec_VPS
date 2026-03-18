import asyncio
import openpyxl
from io import BytesIO
from src.api.endpoints.analytics import export_analytics
from src.database.session import AsyncSessionLocal
import uuid

# Mock Request class for state
class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def verify():
    async with AsyncSessionLocal() as session:
        # 1. Fetch any tenant to use its ID
        from src.database.models import Tenant, Cfdi
        from sqlalchemy import select
        
        tenant = (await session.execute(select(Tenant).limit(1))).scalar_one_or_none()
        if not tenant:
             print("No tenant in DB")
             return
             
        req = MockRequest()
        req.state.tenant_id = tenant.tenant_id
        
        print(f"Testing export for Tenant: {tenant.tenant_id}")
        
        # Call direct
        # export_analytics expects (request, fecha_inicio, fecha_fin, db)
        response = await export_analytics(request=req, fecha_inicio=None, fecha_fin=None, db=session)
        
        # Consume StreamingResponse
        # body_iterator is async in streaming responses
        content = b""
        async for chunk in response.body_iterator:
            content += chunk
            
        # 3. Read Excel from memory
        wb = openpyxl.load_workbook(BytesIO(content))
        ws = wb.active
        
        rows = list(ws.rows)
        print(f"Total rows: {len(rows)}")
        if len(rows) > 0:
             header_row = [cell.value for cell in rows[0]]
             print("Headers Found (Count: {}):".format(len(header_row)))
             print(header_row)
             if len(header_row) == 21:
                  print("SUCCESS: 21 Columns matched!")
             else:
                  print("ERROR: Expected 21, got", len(header_row))
                  
             # Print first data row
             if len(rows) > 1:
                  first_data = [cell.value for cell in rows[1]]
                  print("First Data Row:", first_data)

if __name__ == '__main__':
    asyncio.run(verify())
