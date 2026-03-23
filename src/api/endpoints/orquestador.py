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
):
    try:
        uuid_str = str(payload.uuid_documento).upper()
        query = select(Cfdi).where(Cfdi.uuid == uuid_str)
        result = await db.execute(query)
        cfdi = result.scalar_one_or_none()

        if not cfdi:
            raise HTTPException(status_code=404, detail="Documento no encontrado.")

        entidad_id_doc = cfdi.tenant_id
        smtp_query = select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == entidad_id_doc)
        smtp_result = await db.execute(smtp_query)
        smtp_config = smtp_result.scalar_one_or_none()

        if not smtp_config:
            raise HTTPException(status_code=400, detail="Configuración SMTP no encontrada.")

        from src.database.models import Comprobante
        from sqlalchemy import cast, String, func
        comp_query = select(Comprobante).where(func.lower(cast(Comprobante.uuid, String)) == uuid_str.lower())
        comp_result = await db.execute(comp_query)
        comp = comp_result.scalar_one_or_none()

        # 3. Pre-flight Check: Verificar con Helper Enterprise
        from src.services.cfdi_storage import find_cfdi_attachments
        my_serie = getattr(comp, 'serie', "") if comp else getattr(cfdi, 'serie', "")
        my_folio = getattr(comp, 'folio', "") if comp else getattr(cfdi, 'folio', "")
        my_tipo = getattr(comp, 'tipo_comprobante', "I") if comp else getattr(cfdi, 'tipo_comprobante', "I")
        
        att = find_cfdi_attachments(uuid_str, my_serie, my_folio, my_tipo)
        # 1. Resolver adjuntos originales
        final_xml = att["xml_path"] or cfdi.xml_file_path
        final_pdf = att["pdf_path"] or cfdi.pdf_file_path

        # Limpieza reactiva de rutas en disco
        if final_xml and not os.path.exists(final_xml): final_xml = None
        if final_pdf and not os.path.exists(final_pdf): final_pdf = None

        if comp and comp.ruta_resguardo and not final_xml:
             if comp.ruta_resguardo.endswith('.xml') and os.path.exists(comp.ruta_resguardo):
                  final_xml = comp.ruta_resguardo

        # 2. Inferencia de PDF desde XML
        if final_xml and not final_pdf:
             p_path = final_xml.replace('.xml', '.pdf')
             if os.path.exists(p_path):
                  final_pdf = p_path

        import glob
        # 3. Fallbacks de disco
        if not final_xml:
             for p in [f"storage/**/{uuid_str}.xml", f"Operacion_CFDI/**/{uuid_str}.xml", f"**/{uuid_str}.xml"]:
                m = glob.glob(p, recursive=True)
                if m: final_xml = os.path.abspath(m[0]); break

        if not final_pdf:
             for p in [f"storage/**/{uuid_str}.pdf", f"Operacion_CFDI/**/{uuid_str}.pdf", f"**/{uuid_str}.pdf"]:
                m = glob.glob(p, recursive=True)
                if m: final_pdf = os.path.abspath(m[0]); break

        # 4. Fallback Único Generación (Mutuamente excluyente)
        if not final_pdf and final_xml and os.path.exists(final_xml):
             from src.services.pdf_generator import generate_pdf_from_xml
             dest_tmp = os.path.join(tempfile.gettempdir(), f"{uuid_str}_preview.pdf")
             
             from src.database.models import Tenant
             t_q = await db.execute(select(Tenant).where(Tenant.tenant_id == entidad_id_doc))
             t = t_q.scalar_one_or_none()
             
             if generate_pdf_from_xml(final_xml, dest_tmp, uuid_str, t.logo_path if t else ""):
                  final_pdf = dest_tmp

        if not final_xml or not os.path.exists(final_xml):
            raise HTTPException(status_code=422, detail="Archivo XML no encontrado para el envío.")

        # Reasignación para el mailer
        xml_path = final_xml
        pdf_path = final_pdf

        script_dir = Path(__file__).parent.parent.parent.parent / "microservices" / "mailer"
        temp_html_path = script_dir / "temp_body_reenvio.html"
        cuerpo_formateado = payload.cuerpo.replace('\n', '<br>')
        html_content = f"<html><body>{cuerpo_formateado}</body></html>"
        
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        script_path_rpa = script_dir / "mailVantec.py"
        cmd = ["python", str(script_path_rpa), "-s", payload.asunto, "-f", smtp_config.from_address or smtp_config.username, "-t", payload.destinatario, "-u", smtp_config.username, "-y", smtp_config.password_encrypted, "-z", smtp_config.host, "-p", str(smtp_config.port), "-v"]
        if smtp_config.security_type in ["STARTTLS", "TLS"]: cmd.append("-l")

        cmd.append(str(temp_html_path))
        cmd.append(xml_path) 
        if pdf_path and os.path.exists(pdf_path): cmd.append(pdf_path)

        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(temp_html_path): os.remove(temp_html_path)

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Falla en RPA mailer: {process.stderr}")

        return {"status": "success", "message": "Comprobante reenviado exitosamente."}

    except HTTPException: raise
    except Exception as e:
        if 'temp_html_path' in locals() and os.path.exists(temp_html_path): os.remove(temp_html_path)
        raise HTTPException(status_code=500, detail=f"Error crítico en orquestador.reenvio: {str(e)}")
