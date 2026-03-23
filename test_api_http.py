import traceback
from fastapi.testclient import TestClient
from src.main import app

def test_api():
    client = TestClient(app)
    try:
        with client:
            # 1. Login
            login_res = client.post("/api/v1/auth/login", data={"username": "admin", "password": "prueba01"})
            print("Login status:", login_res.status_code)
            if login_res.status_code != 200:
                 print("Login failed:", login_res.text)
                 return
                 
            token = login_res.json().get("access_token")
            
            # 2. Get active entidad
            ent_res = client.get("/api/v1/admin/entidades", headers={"Authorization": f"Bearer {token}"})
            print("Entitats list status:", ent_res.status_code)
            if ent_res.status_code != 200:
                 print("Entidades failed:", ent_res.text)
                 return
                 
            ents = ent_res.json()
            if not ents:
                 print("No entities found")
                 return
            active_entidad = ents[0]["id"]
            print("Using active entidad:", active_entidad)

            headers = {
                "Authorization": f"Bearer {token}"
            }
            # We don't have cookies, let's look at auth.py to see where it gets it.
            res = client.get(f"/api/v1/comprobantes?t=1", headers=headers)
            print("Comprobantes Status:", res.status_code)
            with open("response_res.txt", "w", encoding="utf-8") as f:
                f.write(res.text)
            if res.status_code != 200:
                print("Error written to response_res.txt")
            else:
                print("Success:", len(res.json()), "items")

    except Exception as e:
        import traceback
        with open("traceback_export_http.txt", "w", encoding="utf-8") as f:
             f.write(traceback.format_exc())
        print("Error written to traceback_export_http.txt")

if __name__ == "__main__":
    test_api()
