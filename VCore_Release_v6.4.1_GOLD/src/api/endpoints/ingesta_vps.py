import os
import tempfile
import xml.etree.ElementTree as ET
import hashlib
import re
import io
import PyPDF2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, String, text, update
from typing import Optional

from src.database.session import get_db
from src.database.models import Tenant, Comprobante
from src.services.parser.cfdi_parser import process_inbound_file

router = APIRouter(tags=["Ingesta VPS"])

async def handle_multi_pdf(record: Comprobante, original_filename: str, pdf_content: bytes, db: AsyncSession, rfc: str):
    """Manejo de múltiples PDFs concatenando la ruta con pipe |"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    storage_dir = os.path.join(project_root, "Operacion_CFDI", rfc, "PDFs")
    os.makedirs(storage_dir, exist_ok=True)
    
    base_name = str(record.uuid).lower()
    suffix = 1
    new_filename = f"{base_name}_{suffix}.pdf"
    new_path = os.path.join(storage_dir, new_filename)
    
    while os.path.exists(new_path) or (record.pdf_path and new_path in record.pdf_path):
        suffix += 1
        new_filename = f"{base_name}_{suffix}.pdf"
        new_path = os.path.join(storage_dir, new_filename)
        
    with open(new_path, "wb") as f:
        f.write(pdf_content)
        
    updated_pdf_path = f"{record.pdf_path}|{new_path}" if record.pdf_path else new_path
    
    await db.execute(
        update(Comprobante).where(Comprobante.uuid == record.uuid).values(pdf_path=updated_pdf_path)
    )
    await db.commit()
    
    return {"status": "success", "message": f"Archivo ya existe, nuevo PDF concatenado ({new_filename}).", "uuid": str(record.uuid)}

@router.post("/upload_cfdi")
async def upload_cfdi(
    x_api_key: str = Header(..., alias="X-API-KEY"),
    xml_file: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    if not xml_file and not pdf_file:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un archivo (XML o PDF).")

    # 1. Validar API KEY contra Tenants
    result = await db.execute(select(Tenant).where(Tenant.api_key == x_api_key))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=401, detail="API Key inválida o no registrada.")
    
    if not tenant.is_active:
        raise HTTPException(status_code=403, detail="El Tenant está inactivo.")

    # [VCORE L6] Inyectar tenant_id en la sesión para Row Level Security (RLS)
    await db.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant.tenant_id)}
    )

    # Leer archivos en memoria para el Hashing Temprano y posterior procesamiento
    xml_content = await xml_file.read() if xml_file else None
    pdf_content = await pdf_file.read() if pdf_file else None

    # Intentar extraer el UUID y validar el XML de forma temprana
    uuid_xml = None
    rfc_emisor = None
    if xml_file and xml_content:
        try:
            try:
                root = ET.fromstring(xml_content.decode('utf-8-sig').strip())
            except UnicodeDecodeError:
                root = ET.fromstring(xml_content.decode('latin-1').strip())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Archivo XML corrupto o no parseable: {str(e)}")

        emisor = root.find('.//{*}Emisor')
        rfc_emisor = (emisor.get('Rfc') or emisor.get('rfc')) if emisor is not None else None
        
        namespaces = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
        uuid_xml = tfd.get('UUID') if tfd is not None else None

        if not rfc_emisor:
             raise HTTPException(status_code=400, detail="El XML no contiene el atributo Rfc en el nodo Emisor.")
        if not uuid_xml:
             raise HTTPException(status_code=400, detail="El XML no contiene un UUID fiscal.")

        # Filtro Zero Trust (RFC Validation)
        receptor = root.find('.//{*}Receptor')
        rfc_receptor = (receptor.get('Rfc') or receptor.get('rfc')) if receptor is not None else None
        
        rfc_valido = False
        if rfc_emisor.upper() == tenant.rfc.upper():
             rfc_valido = True
        elif rfc_receptor and rfc_receptor.upper() == tenant.rfc.upper():
             rfc_valido = True

        if not rfc_valido:
             raise HTTPException(status_code=403, detail="Zero Trust: El RFC del XML no coincide con el RFC asociado al API Key.")

    # 2. Idempotencia Binaria (MD5) - Early Check
    primary_content = xml_content if xml_content else pdf_content
    md5_hash = hashlib.md5(primary_content).hexdigest()

    # Buscar comprobante existente por MD5 o por UUID
    record = None
    record_md5 = None
    
    existing_md5 = await db.execute(select(Comprobante).where(Comprobante.md5_hash == md5_hash))
    record_md5 = existing_md5.scalar_one_or_none()
    record = record_md5

    if not record and uuid_xml:
        existing_uuid = await db.execute(select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid_xml.lower()))
        record = existing_uuid.scalar_one_or_none()

    if record:
        from src.services.cfdi_storage import normalize_vcore_path
        
        # Traducir rutas a rutas de Linux reales
        norm_xml_path = normalize_vcore_path(record.xml_path) if record.xml_path else None
        
        # En caso de múltiples PDFs separados por '|'
        norm_pdf_paths = []
        if record.pdf_path:
            norm_pdf_paths = [normalize_vcore_path(p.strip()) for p in record.pdf_path.split('|') if p.strip()]
            
        # Si no hay rutas PDF pero el XML sí tiene ruta, predecir la ruta del PDF
        if not norm_pdf_paths and norm_xml_path:
            dest_pdf = os.path.splitext(norm_xml_path)[0] + ".pdf"
            norm_pdf_paths = [dest_pdf]
            
        xml_exists = os.path.exists(norm_xml_path) if norm_xml_path else False
        pdf_exists = any(os.path.exists(p) for p in norm_pdf_paths) if norm_pdf_paths else False
        
        restored = False
        db_updates = {}
        
        # Si falta el XML y el cliente lo está enviando en este request, auto-recuperar
        if xml_file and norm_xml_path and not xml_exists:
            os.makedirs(os.path.dirname(norm_xml_path), exist_ok=True)
            with open(norm_xml_path, "wb") as f:
                f.write(xml_content)
            restored = True
            
        # Si falta el PDF y el cliente lo está enviando en este request, auto-recuperar
        if pdf_file and norm_pdf_paths and not pdf_exists:
            dest_pdf = norm_pdf_paths[0]
            os.makedirs(os.path.dirname(dest_pdf), exist_ok=True)
            with open(dest_pdf, "wb") as f:
                f.write(pdf_content)
            restored = True
            
        # Si se detectaron rutas viejas/Windows en base de datos, actualizarlas a las rutas Linux normalizadas
        if norm_xml_path and record.xml_path != norm_xml_path:
            record.xml_path = norm_xml_path
            db_updates["xml_path"] = norm_xml_path
            
        if norm_pdf_paths:
            new_pdf_path_str = "|".join(norm_pdf_paths)
            if record.pdf_path != new_pdf_path_str:
                record.pdf_path = new_pdf_path_str
                db_updates["pdf_path"] = new_pdf_path_str

        # Registrar el md5_hash si no estaba registrado
        if not record.md5_hash and md5_hash:
            record.md5_hash = md5_hash
            db_updates["md5_hash"] = md5_hash
                
        if db_updates:
            db.add(record)
            await db.commit()
            
        if restored:
            return JSONResponse(
                status_code=200, 
                content={
                    "status": "success", 
                    "message": "Archivos físicos restaurados (MD5/UUID Match + Self-Healing)", 
                    "uuid": str(record.uuid),
                    "db_updated": len(db_updates) > 0
                }
            )
            
        # Si no se restauró nada pero se envió un PDF y el MD5 no coincidió (se encontró por UUID)
        # Significa que quieren asociar un PDF diferente/Multi-PDF a este comprobante
        if pdf_file and not record_md5:
            return await handle_multi_pdf(record, pdf_file.filename, pdf_content, db, tenant.rfc)
            
        return JSONResponse(
            status_code=200, 
            content={"status": "skipped", "message": "Archivo ya procesado (MD5/UUID Match)"}
        )

    # Variables temporales para limpieza
    tmp_xml_path = None
    tmp_pdf_path = None
    
    try:
        # 3. Ghost Healer (Solo PDF)
        if not xml_file and pdf_file:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text_pdf = ""
            for page in pdf_reader.pages:
                text_pdf += page.extract_text() or ""
            
            uuid_match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', text_pdf)
            uuid_encontrado = None
            
            if uuid_match:
                uuid_encontrado = uuid_match.group(0).lower()
                existing = await db.execute(select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid_encontrado))
                record = existing.scalar_one_or_none()
                if record:
                    # Aplicar Multi-PDF si ya existe el XML base
                    return await handle_multi_pdf(record, pdf_file.filename, pdf_content, db, tenant.rfc)
            
            # Sin XML y no existe en DB, guardar en Orphans
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            orphans_dir = os.path.join(project_root, "Operacion_CFDI", "Orphans", tenant.rfc)
            os.makedirs(orphans_dir, exist_ok=True)
            
            dest_pdf = os.path.join(orphans_dir, pdf_file.filename)
            with open(dest_pdf, "wb") as f:
                f.write(pdf_content)
            return {"status": "success", "message": "PDF recibido en cuarentena (Ghost Healer).", "tenant_rfc": tenant.rfc, "uuid_detected": uuid_encontrado}

        # 7. Inserción mediante process_inbound_file
        tmp_dir = tempfile.mkdtemp()
        tmp_xml_path = os.path.join(tmp_dir, xml_file.filename)
        with open(tmp_xml_path, "wb") as f:
             f.write(xml_content)
             
        if pdf_file:
             tmp_pdf_path = os.path.join(tmp_dir, pdf_file.filename)
             with open(tmp_pdf_path, "wb") as f:
                  f.write(pdf_content)

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        failed_dir = os.path.join(project_root, "Operacion_CFDI", "Invalid_ADN")
        log_dir = os.path.join(project_root, "Operacion_CFDI", "logs")
        
        exito = await process_inbound_file(
            xml_path=tmp_xml_path,
            failed_dir=failed_dir,
            log_dir=log_dir,
            db=db,
            entidad_id=tenant.tenant_id,
            pdf_path=tmp_pdf_path,
            index_only=False
        )
        
        if not exito:
             raise HTTPException(status_code=500, detail="El motor L6 falló al procesar e insertar el comprobante.")
        
        # Registrar el MD5 Hash
        await db.execute(
            update(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid_xml.lower()).values(md5_hash=md5_hash)
        )
        await db.commit()
             
        return {"status": "success", "message": "Comprobante procesado exitosamente.", "uuid": uuid_xml}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        # Limpieza de temporales
        if tmp_xml_path and os.path.exists(tmp_xml_path):
             try: os.remove(tmp_xml_path)
             except: pass
        if tmp_pdf_path and os.path.exists(tmp_pdf_path):
             try: os.remove(tmp_pdf_path)
             except: pass
