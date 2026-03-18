import asyncio
import os
import sys
import uuid
import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import select
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Usuario
from src.services.cfdi_processor import CfdiProcessor

# Templates de XML Vantec
xml_ingreso_template = """<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="{serie}" Folio="{folio}" Fecha="{fecha}T10:00:00" Total="1160.00" TipoDeComprobante="I" MetodoPago="PPD" FormaPago="99">
  <cfdi:Emisor Rfc="VANT010101XYZ" Nombre="Vantec Core SA de CV"/>
  <cfdi:Receptor Rfc="CLIE010101ABC" Nombre="Cliente SA de CV"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="80111600" Cantidad="1" Descripcion="Servicios de Desarrollo Vantec" ValorUnitario="1000.00" Importe="1000.00" Descuento="0.00"/>
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="160.00"/>
  <cfdi:Complemento>
    <tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" UUID="{uuid_ingreso}" FechaTimbrado="{fecha}T10:00:00" RfcProvCertif="SAT970701NN3"/>
  </cfdi:Complemento>
</cfdi:Comprobante>
"""

xml_pago_template = """<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="{serie}" Folio="{folio}" Fecha="{fecha}T11:00:00" Total="0" TipoDeComprobante="P">
  <cfdi:Emisor Rfc="VANT010101XYZ" Nombre="Vantec Core SA de CV"/>
  <cfdi:Receptor Rfc="CLIE010101ABC" Nombre="Cliente SA de CV"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="84111506" Cantidad="1" Descripcion="Pago" ValorUnitario="0.00" Importe="0.00"/>
  </cfdi:Conceptos>
  <cfdi:Complemento>
    <tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" UUID="{uuid_pago}" FechaTimbrado="{fecha}T11:00:00" RfcProvCertif="SAT970701NN3"/>
    <pago20:Pagos xmlns:pago20="http://www.sat.gob.mx/Pagos20" Version="2.0">
      <pago20:Pago FechaPago="{fecha}T11:00:00" FormaDePagoP="03" MonedaP="MXN" Monto="1160.00">
        <pago20:DoctoRelacionado IdDocumento="{uuid_ingreso}" MonedaDR="MXN" NumParcialidad="1" ImpSaldoAnt="1160.00" ImpPagado="1160.00" ImpSaldoInsoluto="0.00"/>
      </pago20:Pago>
    </pago20:Pagos>
  </cfdi:Complemento>
</cfdi:Comprobante>
"""

async def create_mock_files_and_process(entidad_id: uuid.UUID):
    print("🚀 Iniciando Seed de Datos Reales (Ingreso + REP)")
    os.makedirs("/tmp/watcher_test", exist_ok=True)
    
    uuid_ingreso = str(uuid_lib.uuid4()).upper()
    uuid_pago = str(uuid_lib.uuid4()).upper()
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    
    # Archivos Ingreso
    xml_ing_path = "/tmp/watcher_test/F-1020.xml"
    pdf_ing_path = "/tmp/watcher_test/F-1020.pdf"
    with open(xml_ing_path, "w", encoding="utf-8") as f:
        f.write(xml_ingreso_template.format(serie="F", folio="1020", fecha=fecha_str, uuid_ingreso=uuid_ingreso))
    with open(pdf_ing_path, "wb") as f:
        f.write(b"%PDF-1.4 Fake PDF Data Ingreso")
        
    # Archivos Pago
    xml_pag_path = "/tmp/watcher_test/P-4050.xml"
    pdf_pag_path = "/tmp/watcher_test/P-4050.pdf"
    with open(xml_pag_path, "w", encoding="utf-8") as f:
        f.write(xml_pago_template.format(serie="P", folio="4050", fecha=fecha_str, uuid_pago=uuid_pago, uuid_ingreso=uuid_ingreso))
    with open(pdf_pag_path, "wb") as f:
        f.write(b"%PDF-1.4 Fake PDF Data Pago")
        
    print(f"Archivos creados en /tmp/watcher_test: F-1020.xml y P-4050.xml")
    
    async with AsyncSessionLocal() as db:
        processor = CfdiProcessor(db)
        
        # 1. Procesar Ingreso (Simulando lógica Watcher de emparejamiento PDF)
        print("Procesando Ingreso (Watcher logic)...")
        await processor.procesar_cfdi(
            ruta_archivo=xml_ing_path,
            entidad_id=entidad_id,
            mover_a_boveda=True,
            ruta_pdf=pdf_ing_path
        )
        
        # 2. Procesar Pago
        print("Procesando REP (Watcher logic)...")
        await processor.procesar_cfdi(
            ruta_archivo=xml_pag_path,
            entidad_id=entidad_id,
            mover_a_boveda=True,
            ruta_pdf=pdf_pag_path
        )
        
    print("✅ Ingesta Legacy exitosa y enviada a Bóveda.")
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
            
            # 2. Dashboard y Select Entidad
            print("Seleccionando Entidad en Dashboard...")
            await page.wait_for_selector("#entity-selector")
            await page.select_option("#entity-selector", index=1)
            await page.wait_for_timeout(2000)
            
            print("Capturando Dashboard con Datepicker...")
            await page.screenshot(path=os.path.join(artifact_dir, "dashboard_datepicker.png"))
            
            # 3. Explorador CFDI
            print("Navegando al Explorador CFDI...")
            await page.goto("http://localhost:8002/cfdis")
            await page.wait_for_selector("#cfdiTableBody tr")
            await page.wait_for_timeout(2000)
            
            # Buscar el registro del ingreso y abrir drawer
            # Asumiendo que `openDetailDrawer('uuid_ingreso')` funciona
            print(f"Abriendo Drawer (Trazabilidad) para {uuid_ingreso}...")
            await page.evaluate(f"openDetailDrawer('{uuid_ingreso}')")
            await page.wait_for_selector("#detailDrawer")
            await page.wait_for_timeout(1000)
            
            print("Capturando Drawer con Pagos Relacionados...")
            await page.screenshot(path=os.path.join(artifact_dir, "cfdi_trazabilidad_drawer.png"))
            print("✅ Capturas generadas con éxito.")
            print(f"Artifacts Path: {artifact_dir}")
        except Exception as e:
            print(f"❌ Error en UI Test: {str(e)}")
            await page.screenshot(path=os.path.join(artifact_dir, "error_state.png"))
        finally:
            await browser.close()
            
async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario))
        user = result.scalars().first()
        
        # Buscar la primera entidad
        result = await db.execute(select(EntidadFiscal))
        entidad = result.scalars().first()
        if not entidad:
            print("No entidades encontradas. Abortando.")
            return

    uuid_ing = await create_mock_files_and_process(entidad.id)
    await run_playwright_test(uuid_ing)

if __name__ == "__main__":
    asyncio.run(main())
