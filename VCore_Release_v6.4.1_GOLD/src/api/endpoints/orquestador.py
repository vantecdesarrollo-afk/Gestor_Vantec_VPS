import os
import subprocess
import uuid
import logging
import jwt
import glob
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from src.core.config import settings
from pathlib import Path
import tempfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from src.database.session import get_db
from src.database.models import EntidadSMTPConfig, Comprobante, Tenant
from sqlalchemy import cast, String, func

router = APIRouter(prefix="/api/orquestador", tags=["Orquestador"])

logger = logging.getLogger(__name__)

class ReenvioRequest(BaseModel):
    uuid_documento: uuid.UUID
    destinatario: str
    asunto: str
    cuerpo: str

@router.post("/reenvio")
async def reenvio_comprobante(
    payload: ReenvioRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        uuid_str = str(payload.uuid_documento).lower()
        # Definir app_root al inicio para uso en barrido de bóveda y mailer (Directiva v82.0)
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid_str)
        result = await db.execute(query)
        comp = result.scalar_one_or_none()

        if not comp:
            raise HTTPException(status_code=404, detail="Documento no encontrado.")

        # --- VALIDACIÓN IDOR (Condición CTO v84.0) ---
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token ausente o inválido")
            
        token = auth_header.split(" ")[1]
        try:
            token_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            is_super = token_payload.get("is_superadmin") is True
            user_entidad = str(token_payload.get("tenant_id") or token_payload.get("entidad_id") or "")
        except Exception:
            raise HTTPException(status_code=401, detail="Fallo de autenticación en Orquestador")

        if not is_super:
            # Si no es SuperAdmin, el ID de entidad del token debe coincidir con el del documento
            if str(comp.entidad_id) != user_entidad:
                logger.warning(f"Intento de IDOR: Usuario {user_entidad} intentó reenviar CFDI de entidad {comp.entidad_id}")
                raise HTTPException(status_code=403, detail="No tiene permisos para reenviar este documento")

        entidad_id_doc = comp.entidad_id
        smtp_query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == entidad_id_doc)
        smtp_result = await db.execute(smtp_query)
        smtp_config = smtp_result.scalar_one_or_none()

        if not smtp_config:
            raise HTTPException(status_code=400, detail="Configuración SMTP no encontrada para este comprobante.")

        # 3. Pre-flight Check: Resolver adjuntos
        from src.services.cfdi_storage import find_cfdi_attachments
        att = find_cfdi_attachments(uuid_str, comp.serie or "", comp.folio or "", comp.tipo_comprobante or "I")
        
        # 1. Resolver adjuntos originales
        final_xml = comp.xml_path or att["xml_path"]
        
        # --- CIRUGÍA MULTI-PDF L6 ---
        pdf_raw = comp.pdf_path or att.get("pdf_path", "")
        pdfs_from_db = [p.strip() for p in pdf_raw.split('|') if p.strip()]

        # Limpieza reactiva de rutas en disco
        if final_xml and not os.path.exists(final_xml): final_xml = None
        
        # Validar y separar los PDFs
        valid_pdfs = [p for p in pdfs_from_db if os.path.exists(p)]

        if comp and comp.xml_path and not final_xml:
            if comp.xml_path.endswith('.xml') and os.path.exists(comp.xml_path):
                final_xml = comp.xml_path

        # 2. Inferencia de PDF desde XML (Solo si no hay PDFs en BD)
        if final_xml and not valid_pdfs:
            p_path = final_xml.replace('.xml', '.pdf')
            if os.path.exists(p_path):
                valid_pdfs.append(p_path)

        import glob
        # 3. Fallbacks de disco para XML (Directiva v82.0)
        if not final_xml:
            for p in [f"storage/**/{uuid_str}.xml", f"Operacion_CFDI/**/{uuid_str}.xml", f"**/{uuid_str}.xml"]:
                m = glob.glob(p, recursive=True)
                if m:
                    final_xml = os.path.abspath(m[0])
                    break

        all_pdfs = list(set(valid_pdfs))
        
        # BARRIDO SEGURO EN LA CARPETA DEL XML (Directiva Frente 3)
        if final_xml and os.path.exists(final_xml):
            dir_xml = os.path.dirname(os.path.abspath(final_xml))
            patron = os.path.join(dir_xml, f"*{uuid_str}*.pdf")
            for pdf_found in glob.glob(patron):
                if pdf_found not in all_pdfs:
                    all_pdfs.append(pdf_found)

        # MANTENEMOS EL FALLBACK ORIGINAL POR SEGURIDAD
        if not all_pdfs:
            for p in [f"storage/**/{uuid_str}.pdf", f"Operacion_CFDI/**/{uuid_str}.pdf", f"**/{uuid_str}.pdf"]:
                m = glob.glob(p, recursive=True)
                for found in m:
                    path_abs = os.path.abspath(found)
                    if path_abs not in all_pdfs:
                        all_pdfs.append(path_abs)

        if not final_xml or not os.path.exists(final_xml):
            raise HTTPException(status_code=422, detail="Archivo XML no encontrado para el envío.")

        # Reasignación para el mailer
        xml_path = final_xml

        # 5. Envío Real vía Microservicio MailVantec
        try:
            import tempfile
            import sys
            
            # Crear archivo temporal para el cuerpo HTML
            body_path = os.path.join(tempfile.gettempdir(), f"body_{uuid_str}.html")
            with open(body_path, "w", encoding="utf-8") as fb:
                fb.write(payload.cuerpo)
            
            mailer_script = os.path.join(app_root, "microservices", "mailer", "mailVantec.py")
            
            cmd = [
                sys.executable,
                mailer_script,
                "-s", payload.asunto,
                "-f", smtp_config.from_address,
                "-t", payload.destinatario,
                "-u", smtp_config.username,
                "-y", smtp_config.password_encrypted,
                "-z", smtp_config.host,
                "-p", str(smtp_config.port)
            ]
            
            if smtp_config.security_type == 'STARTTLS':
                cmd.append("-l")
                
            cmd.append(body_path)
            
            # Restauración de lógica posicional original
            if xml_path: cmd.append(xml_path)
            
            # AGREGAR TODOS LOS PDFS ENCONTRADOS DIRECTAMENTE AL COMANDO
            for p_file in all_pdfs: 
                cmd.append(p_file)
                
            # Disparar Microservicio (Estado Mañana 10:00 AM)
            proceso = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {"status": "success", "message": f"Comprobante enviado exitosamente a {payload.destinatario}"}
            
        except subprocess.CalledProcessError as e_process:
            logger.error(f"Fallo en microservicio mailVantec: {e_process.stderr} | {e_process.stdout}")
            raise HTTPException(status_code=500, detail=f"Error en procesador de correo Vantec: STDOUT: {e_process.stdout}")
        except Exception as e_gen:
            logger.error(f"Fallo inesperado al invocar mailVantec: {str(e_gen)}")
            raise HTTPException(status_code=500, detail=f"Error de sistema de correo: {str(e_gen)}")

    except Exception as e:
        logger.error(f"Error en reenvio: {e}")
        raise HTTPException(status_code=500, detail=str(e))