import asyncio
import os
import sys
import defusedxml.ElementTree as ET
from sqlalchemy import select
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Usuario
from src.services.cfdi_processor import CfdiProcessor

async def create_mock_files_and_process(entidad_id):
    print("🚀 Iniciando Seed de Datos Reales (Vantec 804 / 305)")
    os.makedirs("/tmp/watcher_test_real", exist_ok=True)
    
    # Fuentes originales
    fuente_ingreso = r"C:\Vantec\Test\factura_ingreso.xml"
    fuente_pago = r"C:\Vantec\Test\pago_rep.xml"
    
    # Destinos con los nombres requeridos
    xml_ing_path = "/tmp/watcher_test_real/804.xml"
    pdf_ing_path = "/tmp/watcher_test_real/804.pdf"
    
    xml_pag_path = "/tmp/watcher_test_real/305.xml"
    pdf_pag_path = "/tmp/watcher_test_real/305.pdf"
    
    # Copiar archivos
    import shutil
    shutil.copy2(fuente_ingreso, xml_ing_path)
    shutil.copy2(fuente_pago, xml_pag_path)
    
    # Crear PDFs falsos
    with open(pdf_ing_path, "wb") as f:
        f.write(b"%PDF-1.4 Fake PDF Data Ingreso 804")
    with open(pdf_pag_path, "wb") as f:
        f.write(b"%PDF-1.4 Fake PDF Data Pago 305")
        
    print(f"Archivos preparados en /tmp/watcher_test_real")
    
    # Extraer UUID del ingreso para test de UI
    tree = ET.parse(xml_ing_path)
    root = tree.getroot()
    namespaces = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
    tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
    uuid_ingreso = tfd.get('UUID')
    
    async with AsyncSessionLocal() as db:
        processor = CfdiProcessor(db)
        
        # 1. Procesar Ingreso
        print("Procesando Ingreso 804 (Strict filename)...")
        await processor.procesar_cfdi(
            ruta_archivo=xml_ing_path,
            entidad_id=entidad_id,
            mover_a_boveda=True,
            ruta_pdf=pdf_ing_path
        )
        
        # 2. Procesar Pago
        print("Procesando REP 305 (Strict filename)...")
        await processor.procesar_cfdi(
            ruta_archivo=xml_pag_path,
            entidad_id=entidad_id,
            mover_a_boveda=True,
            ruta_pdf=pdf_pag_path
        )
        
    print(f"✅ Ingesta legacy 804/305 exitosa. UUID del Ingreso: {uuid_ingreso}")
    return uuid_ingreso

async def run_playwright_test(uuid_ingreso: str):
    print("🎭 Iniciando Validaciones de UI en Browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        artifact_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'artifacts')
        os.makedirs(artifact_dir, exist_ok=True)
        
        try:
            # 1. Login
            await page.goto("http://localhost:8002/login")
            await page.fill("#username", "admin@vantec.mx")
            await page.fill("#password", "admin123")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/dashboard")
            
            # 2. Seleccionar Entidad
            print("Seleccionando Entidad en Dashboard...")
            await page.wait_for_selector("#entity-selector")
            await page.select_option("#entity-selector", index=1)
            await page.wait_for_timeout(2000)
            
            # 3. Explorador CFDI
            print("Navegando al Explorador CFDI...")
            await page.goto("http://localhost:8002/cfdis")
            await page.wait_for_selector("#cfdiTableBody tr")
            await page.wait_for_timeout(3000)
            
            print(f"Abriendo Drawer (Trazabilidad) para {uuid_ingreso}...")
            await page.evaluate(f"openDetailDrawer('{uuid_ingreso}')")
            await page.wait_for_selector("#detailDrawer")
            await page.wait_for_timeout(1000)
            
            print("Capturando Drawer con Pagos Relacionados para factura 804...")
            screenshot_path = os.path.join(artifact_dir, "vantec_804_305_drawer.png")
            await page.screenshot(path=screenshot_path)
            print("✅ Capturas generadas con éxito.")
            print(f"Artifacts Path: {artifact_dir}")
        except Exception as e:
            print(f"❌ Error en UI Test: {str(e)}")
            await page.screenshot(path=os.path.join(artifact_dir, "error_804_state.png"))
        finally:
            await browser.close()
            
async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EntidadFiscal))
        entidad = result.scalars().first()
        if not entidad:
            print("No entidades encontradas. Abortando.")
            return

    uuid_ing = await create_mock_files_and_process(entidad.id)
    await run_playwright_test(uuid_ing)

if __name__ == "__main__":
    asyncio.run(main())
