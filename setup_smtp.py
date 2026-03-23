import asyncio
import uuid
import smtplib
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadSMTPConfig, Tenant

async def main():
    tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    
    async with AsyncSessionLocal() as db:
        # 1. Verify tenant
        res = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = res.scalar_one_or_none()
        if not tenant:
             print("Tenant not found")
             return

        # 2. Upsert SMTP
        smtp_res = await db.execute(select(EntidadSMTPConfig).where(EntidadSMTPConfig.entidad_id == tenant_id))
        config = smtp_res.scalar_one_or_none()
        
        real_host = "smtp.office365.com"
        real_port = 587
        real_username = "ugxs63@psoplaneta.com"
        real_from = "facturacion@planeta.com.mx"
        real_pass = "ViYrPPeq"
        real_sec = "STARTTLS"
        real_auth = "LOGIN"

        if config:
             config.host = real_host
             config.port = real_port
             config.username = real_username
             config.from_address = real_from
             config.password_encrypted = real_pass
             config.security_type = real_sec
             config.authentication_type = real_auth
        else:
             config = EntidadSMTPConfig(
                 entidad_id=tenant_id,
                 host=real_host,
                 port=real_port,
                 username=real_username,
                 from_address=real_from,
                 password_encrypted=real_pass,
                 security_type=real_sec,
                 authentication_type=real_auth
             )
             db.add(config)
             
        await db.commit()
        print("SMTP config saved in database")

        # 3. Test connection (Office 365)
        print(f"Testing SMTP connection to {real_host}:{real_port}...")
        try:
             server = smtplib.SMTP(real_host, real_port, timeout=10)
             server.starttls()
             server.login(real_username, real_pass)
             server.quit()
             print("SUCCESS: SMTP connection and authentication successful (250 OK)")
        except Exception as e:
             print(f"FAILURE: SMTP Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
