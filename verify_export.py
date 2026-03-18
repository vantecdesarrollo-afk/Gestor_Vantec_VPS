import asyncio
import base64
import json
import openpyxl
from io import BytesIO
from fastapi.testclient import TestClient
from src.main import app

def verify():
    client = TestClient(app)
    # 1. Login
    r = client.post('/api/v1/auth/login', data={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
         print("Login failed:", r.text)
         return
    token = r.json()['access_token']
    parts = token.split('.')
    payload = json.loads(base64.b64decode(parts[1] + '==').decode('utf-8'))
    tenant = payload['entidades'][0]['id']
    headers = {'Authorization': f'Bearer {token}', 'X-Entidad-ID': tenant}

    # 2. Call Export
    r_exp = client.get('/api/v1/analytics/export', headers=headers)
    print("Export Status:", r_exp.status_code)
    
    if r_exp.status_code != 200:
         print("Export failed:", r_exp.text)
         return

    # 3. Read Excel from memory
    wb = openpyxl.load_workbook(BytesIO(r_exp.content))
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
    verify()
