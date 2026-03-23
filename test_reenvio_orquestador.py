import asyncio
import httpx
import uuid

async def main():
    async with httpx.AsyncClient() as client:
         token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ1c2VybmFtZSI6ImVyb2JsZXNqIiwiZW50aWRhZF9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0Nj655440000IsInRlbmFudF9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsImlzX3N1cGVyYWRtaW4iOnRydWUsImVudGlkYWRlcyI6W3siaWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyZmMiOiJWQ08xMzA3MjM0VkEiLCJyb2wiOiJBRE1JTiJ9XSwiZXhwIjoxNzc0MDI5MzMxfQ.ormg0sca5uOGcAXXFyd4AvOImdMqIyJAboRVuBWw664"
         headers = {
             "Authorization": f"Bearer {token}",
             "Content-Type": "application/json"
         }
         
         # Folio 804 UUID (extracted previously or lookup in Db)
         # In Step 421 row 1-3 found 24A75E3B-261F-455A-9D04-B30BE95865BD
         payload = {
              "uuid_documento": "24A75E3B-261F-455A-9D04-B30BE95865BD",
              "destinatario": "test@planeta.com.mx",
              "asunto": "Validacion mailer",
              "cuerpo": "Prueba"
         }
         
         try:
             res = await client.post("http://127.0.0.1:8000/api/orquestador/reenvio", headers=headers, json=payload, timeout=20)
             print(f"STATUS CODE: {res.status_code}")
             print(f"RESPONSE: {res.text}")
         except Exception as e:
             print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
