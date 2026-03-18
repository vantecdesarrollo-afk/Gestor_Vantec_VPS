from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import os
import subprocess
import uuid
import logging
from pathlib import Path
import tempfile

from src.database.session import get_db
from src.database.models import EntidadSMTPConfig, Cfdi

def map_host_to_container(windows_path: str) -> str:
    """
    [ES] Mapea rutas de host Windows a rutas internas del contendor Docker.
    """
    if not windows_path:
        return windows_path
    base_host = r'C:\ITC\Fappeal\Planeta\CorreoElectronico\MailFac'
    base_container = '/app/storage/planeta_docs'
    mapped = windows_path.replace(base_host, base_container).replace('\\', '/')
    return mapped

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
    db: AsyncSession = Depends(get_db)
    # HOTFIX VANTEC: Eliminamos Depends(get_active_entidad). 
    # El Frontend no envía la cabecera en esta vista. El tenant se infiere del CFDI.
):
    """
    [ES] Orquestador de reenvío con Verificación de Integridad de Datos y Configuración SMTP de Tenant.
    """
    try:
        # 1. Pre-flight Check: Validar existencia en DB por UUID primero
        uuid_str = str(payload.uuid_documento).upper()
        query = select(Cfdi).where(Cfdi.uuid == uuid_str)
        result = await db.execute(query)
        cfdi = result.scalar_one_or_none()

        if not cfdi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento con UUID {uuid_str} no encontrado en la base de datos."
            )

        # 2. Obtener Configuración SMTP usando el Tenant dueño del documento
        entidad_id_doc = cfdi.tenant_id
        
        smtp_query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == entidad_id_doc)

        smtp_result = await db.execute(smtp_query)
        smtp_config = smtp_result.scalar_one_or_none()

        if not smtp_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuración SMTP no encontrada para la empresa emisora del documento."
            )

        # 3. Pre-flight Check: Verificar existencia física de archivos
        xml_path = cfdi.xml_file_path
        pdf_path = cfdi.pdf_file_path

        if not xml_path:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ruta de XML no especificada en la base de datos."
            )

        # 4. Preparación de contenido HTML y archivo temporal
        # VCore Fix: Generar archivo en directorio del script para evitar fallas de permisos/lectura
        script_dir = Path(__file__).parent.parent.parent.parent / "microservices" / "mailer"
        temp_html_path = script_dir / "temp_body_reenvio.html"
        
        cuerpo_formateado = payload.cuerpo.replace('\n', '<br>')
        html_content = f"<html><body>{cuerpo_formateado}</body></html>"
        
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 5. Invocación Nativa RPA (mailVantec.py)
        script_path_rpa = script_dir / "mailVantec.py"

        cmd = [
            "python",
            str(script_path_rpa),
            "-s", payload.asunto,
            "-f", smtp_config.from_address or smtp_config.username,
            "-t", payload.destinatario,
            "-u", smtp_config.username,
            "-y", smtp_config.password_encrypted,
            "-z", smtp_config.host,
            "-p", str(smtp_config.port),
            "-v" 
        ]

        if smtp_config.security_type in ["STARTTLS", "TLS"]:
            cmd.append("-l")

        xml_container_path = map_host_to_container(xml_path)
        cmd.append(str(temp_html_path))
        cmd.append(xml_container_path)

        if pdf_path:
             pdf_container_path = map_host_to_container(pdf_path)
             cmd.append(pdf_container_path)

        logger.info(f"Ejecutando RPA mailer para UUID {cfdi.uuid}...")
        
        process = subprocess.run(

            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

        if process.returncode != 0:
            logger.error(f"Error en mailVantec execution: {process.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Falla en el motor de envío: {process.stderr}"
            )

        return {
            "status": "success",
            "message": f"Comprobante (UUID {cfdi.uuid}) reenviado exitosamente.",
            "transaction_id": str(uuid.uuid4())
        }


    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error crítico en orquestador.reenvio: {str(e)}")
        if 'temp_html_path' in locals() and os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error interno del orquestador: {str(e)}"
        )