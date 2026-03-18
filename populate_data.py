import urllib.request
import urllib.parse
import json
import os
import uuid

# Tenant to assign
TENANT_ID = 'e6f64bb0-3971-4cc8-b883-cd183eca77d7' # Assuming this is not strictly checked for uploads or we get it from token

login_data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
req_login = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=login_data)

try:
    with urllib.request.urlopen(req_login) as response:
        login_res = json.loads(response.read())
        token = login_res.get('access_token')
        tenant_uuid = login_res.get('entidades')[0]['id'] if login_res.get('entidades') else None
        print(f"Token obtained: {token[:15]}... for Tenant: {tenant_uuid}")
        
        # Test Uploading files using urllib (multipart/form-data is tricky, wait let's use httpx or requests)
except Exception as e:
    print('Login error:', e)
    if hasattr(e, 'read'):
        print(e.read().decode())
