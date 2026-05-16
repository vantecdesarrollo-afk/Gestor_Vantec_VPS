import sys, os
BASE_PATH = r"C:\Test_Antigravity\Gestor_CFDI_Vantec"
sys.path.insert(0, BASE_PATH)

from watcher import write_audit_log, get_daily_log_path

RFC = "VCO1307234VA"
log_file = get_daily_log_path("EMPRESA", RFC)

# Forzamos una entrada manual para demostrar el formato L6 V2
write_audit_log(log_file, "DUPLICADO | RFC: VCO1307234VA | ORIGEN: FORCE_TEST.xml | ACCIÓN: Bloqueado (Manual Verification)")
print(f"✅ Log manual escrito en: {log_file}")
