import os
import shutil
import time
import uuid

# Configuration / Configuración
DROP_ZONE = "drop_zone_test"
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
STORAGE_DIR = "storage/tenants"

def test_twin_file_strategy():
    """
    [ES] Prueba la estrategia de archivos gemelos (XML+PDF).
    [EN] Tests the twin file strategy (XML+PDF).
    """
    print("🚀 Testing Twin File Strategy...")
    
    # 1. Prepare Drop Zone
    if not os.path.exists(DROP_ZONE):
        os.makedirs(DROP_ZONE)
    
    # 2. Create dummy XML and PDF
    test_uuid = str(uuid.uuid4())
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" Version="4.0" Fecha="2026-03-10T09:00:00" Total="116.00">
    <cfdi:Emisor Rfc="VANT010101ABC" Nombre="VANTEC TEST"/>
    <cfdi:Receptor Rfc="RECP010101XYZ" Nombre="RECEPTOR TEST"/>
    <cfdi:Conceptos>
        <cfdi:Concepto Cantidad="1" Descripcion="Test Twin" Importe="100.00" ValorUnitario="100.00"/>
    </cfdi:Conceptos>
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital UUID="{test_uuid}" FechaTimbrado="2026-03-10T09:05:00"/>
    </cfdi:Complemento>
</cfdi:Comprobante>"""

    xml_path = os.path.join(DROP_ZONE, "invoice_test.xml")
    pdf_path = os.path.join(DROP_ZONE, "invoice_test.pdf")
    
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    with open(pdf_path, "w") as f:
        f.write("DUMMY PDF CONTENT")
    
    print(f"📄 Files created in Drop Zone: {xml_path}, {pdf_path}")
    print(f"🎯 Target UUID: {test_uuid}")
    print("⏳ Waiting for watcher to process (Manually verify logs in uvicorn)...")
    print("ℹ️ Note: This script only prepares the files. Watcher must be running.")

if __name__ == "__main__":
    test_twin_file_strategy()
