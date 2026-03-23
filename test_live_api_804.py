import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_api():
    output = []
    # 1. Find 804 UUID
    from src.database.session import SessionLocal
    from src.database.models import Comprobante
    
    db = SessionLocal()
    comp = db.query(Comprobante).filter(Comprobante.folio.like('%804%')).first()
    db.close()
    
    if not comp:
        print("No se encontró factura 804")
        return
        
    uuid = str(comp.uuid)
    output.append(f"UUID: {uuid}")
    
    # 2. Test XML download
    response_xml = client.get(f"/api/v1/comprobantes/{uuid}/xml", params={"entidad_id": str(comp.entidad_id)})
    output.append(f"XML Response Status: {response_xml.status_code}")
    output.append(f"XML Content Preview: {response_xml.content[:50]}")
    if response_xml.headers.get("Content-Disposition"):
        output.append(f"XML Disposition: {response_xml.headers['Content-Disposition']}")

    # 3. Test PDF download
    response_pdf = client.get(f"/api/v1/comprobantes/{uuid}/pdf", params={"entidad_id": str(comp.entidad_id)})
    output.append(f"PDF Response Status: {response_pdf.status_code}")
    output.append(f"PDF Content Preview: {response_pdf.content[:50]}")
    if response_pdf.headers.get("Content-Disposition"):
         output.append(f"PDF Disposition: {response_pdf.headers['Content-Disposition']}")
         
    with open("live_api_804.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Results saved to live_api_804.txt")

if __name__ == "__main__":
    test_api()
