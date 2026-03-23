with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\analytics.py", "r", encoding="utf-8") as f:
    c = f.read()

old_ppd = """        # 4. PPD Pendientes Lógica (VCORE-BRIDGE)
        subquery = select(CfdiRelacionado.uuid_relacionado)
        q_ppd = select(func.count()).select_from(DashCfdiDocument).where(
            DashCfdiDocument.tenant_id == entidad_id,
            DashCfdiDocument.metodo_pago == 'PPD',
            DashCfdiDocument.uuid_fiscal.notin_(subquery)
        )"""

new_ppd = """        # 4. PPD Pendientes Lógica (VCORE-BRIDGE)
        from sqlalchemy import cast, String
        subquery = select(cast(CfdiRelacionado.uuid_relacionado, String))
        q_ppd = select(func.count()).select_from(DashCfdiDocument).where(
            DashCfdiDocument.tenant_id == entidad_id,
            DashCfdiDocument.metodo_pago == 'PPD',
            cast(DashCfdiDocument.uuid_fiscal, String).notin_(subquery)
        )"""

c = c.replace(old_ppd, new_ppd)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\analytics.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Analytics SQL Cast Applied")
