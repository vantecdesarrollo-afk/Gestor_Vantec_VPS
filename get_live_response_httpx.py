import httpx
import json

url = "http://127.0.0.1:8000/api/v1/comprobantes/af41872d-1e12-44ec-9d58-614b23e9655c"

with open("live_endpoint_response.json", "w", encoding="utf-8") as f:
    try:
        res = httpx.get(url, timeout=10.0)
        if res.status_code == 200:
             f.write(json.dumps(res.json(), indent=4))
             print(f"✅ Success! Written to live_endpoint_response.json")
        else:
             f.write(f"❌ Error Status {res.status_code}: {res.text}\n")
             print(f"❌ Error Status {res.status_code}")
    except Exception as e:
        f.write(f"❌ EXCEPTION: {str(e)}\n")
        print(f"❌ EXCEPTION: {str(e)}")
