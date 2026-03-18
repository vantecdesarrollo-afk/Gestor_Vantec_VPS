import asyncio
import os
import uuid
from datetime import datetime
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi, Tenant
from sqlalchemy import select
from playwright.async_api import async_playwright

async def run():
    # 1. Seed 5 documents
    async with AsyncSessionLocal() as db:
        tenant = (await db.execute(select(Tenant).where(Tenant.rfc == 'VCO1307234VA'))).scalar_one_or_none()
        if tenant:
            tenant_id = tenant.tenant_id
            
            # Wipe existing to ensure exactly 5
            await db.execute(text("TRUNCATE TABLE cfdis CASCADE;"))
            
            docs = [
                {"uuid": str(uuid.uuid4()), "rfc_e": "VCO1307234VA", "rfc_r": "XAXX010101000", "date": "2024-01-15T12:00:00", "total": 15000.50, "tipo": "I", "metodo": "PUE"},
                {"uuid": str(uuid.uuid4()), "rfc_e": "VCO1307234VA", "rfc_r": "XEXX010101000", "date": "2024-02-20T10:30:00", "total": 28500.00, "tipo": "I", "metodo": "PPD"},
                {"uuid": str(uuid.uuid4()), "rfc_e": "VCO1307234VA", "rfc_r": "XAXX010101000", "date": "2024-03-05T09:15:00", "total": 4200.75, "tipo": "I", "metodo": "PUE"},
                {"uuid": str(uuid.uuid4()), "rfc_e": "VCO1307234VA", "rfc_r": "XEXX010101000", "date": "2024-03-25T16:45:00", "total": 12000.00, "tipo": "E", "metodo": "PUE"},
                {"uuid": str(uuid.uuid4()), "rfc_e": "VCO1307234VA", "rfc_r": "ABC010101ABC", "date": "2024-04-10T11:20:00", "total": 55000.00, "tipo": "I", "metodo": "PPD"}
            ]
            
            for d in docs:
                # We need to simulate the XML for Analytics parsing
                xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Fecha="{d['date']}" Total="{d['total']}" TipoDeComprobante="{d['tipo']}" MetodoPago="{d['metodo']}" Moneda="MXN">
    <cfdi:Emisor Rfc="{d['rfc_e']}"/>
    <cfdi:Receptor Rfc="{d['rfc_r']}"/>
    <cfdi:Conceptos>
        <cfdi:Concepto Descripcion="Servicios Profesionales de Consultoria"/>
    </cfdi:Conceptos>
</cfdi:Comprobante>
"""
                os.makedirs('storage', exist_ok=True)
                path = f"storage/{d['uuid']}.xml"
                with open(path, 'w') as f:
                    f.write(xml_content)
                    
                cfdi = Cfdi(
                    tenant_id=tenant_id,
                    uuid=d["uuid"],
                    rfc_emisor=d["rfc_e"],
                    rfc_receptor=d["rfc_r"],
                    issue_date=datetime.fromisoformat(d["date"]),
                    total=d["total"],
                    version="4.0",
                    xml_file_path=os.path.abspath(path),
                    status="VALID"
                )
                db.add(cfdi)
            await db.commit()
            print("Inserted 5 CFDIS")

    # 2. Capture Screenshot with Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto("http://127.0.0.1:8000/login")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin123")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/dashboard")
        
        # Select RFC in dropdown
        await page.select_option("#entity-selector", label="VCO1307234VA")
        
        # Wait for data fetch
        await asyncio.sleep(4)
        
        # Take screenshot of the top containing KPIs and charts
        await page.screenshot(path="dashboard_recovered_v100.png", full_page=True)
        await browser.close()
        print("Captured screenshot to dashboard_recovered_v100.png")

if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(run())
