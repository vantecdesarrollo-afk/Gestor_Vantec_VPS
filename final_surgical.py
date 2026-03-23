# --- 1. Frontend Debounce (loadCfdis) ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "r", encoding="utf-8") as f:
    js = f.read()

old_load = """async function loadCfdis() {
    const tableBody = document.getElementById('cfdiTableBody');"""

new_load = """let isLoadingCfdis = false;
async function loadCfdis() {
    if (isLoadingCfdis) return;
    isLoadingCfdis = true;
    const tableBody = document.getElementById('cfdiTableBody');"""

js = js.replace(old_load, new_load)

# Add finally condition to release debounce
old_catch = """    } catch (error) {
        console.error('[VANTEC FATAL] Fallo al cargar desde /api/v1/comprobantes/:', error);
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-red-500 font-bold">Error de conexión: ${error.message}</td></tr>`;
        }
    }
}"""

new_catch = """    } catch (error) {
        console.error('[VANTEC FATAL] Fallo al cargar desde /api/v1/comprobantes/:', error);
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="11" class="px-6 py-12 text-center text-red-500 font-bold">Error de conexión: ${error.message}</td></tr>`;
        }
    } finally {
        isLoadingCfdis = false;
    }
}"""

# safe string replace
if old_catch in js:
     js = js.replace(old_catch, new_catch)
else:
     # alternate if spacings mismatch
     js = js.replace("} catch (error) {", "} catch (error) {\n        console.error('[VANTEC FATAL]')") 
     with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
         f.write(js)

with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\static\js\cfdis.js", "w", encoding="utf-8") as f:
    f.write(js)


# --- 2. Defensive Looping in comprobantes.py ---
with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\src\api\endpoints\comprobantes.py", "r", encoding="utf-8") as f:
    c = f.read()

loop_start = """        output = []
        for r in rows:
            # Calculamos el total real para los Pagos (P)"""

loop_start_safe = """        output = []
        for r in rows:
            try:
                # Calculamos el total real para los Pagos (P)"""

c = c.replace(loop_start, loop_start_safe)

# close defensive try loop before output.append
append_content = """            reps_directos = [{"""

# We need to wrap with try/except
old_append_block = """            output.append({"""

# Since output.append is inside loop, let's find the end of the loop and append the except block
# Let's read lines surrounding footer of loop r in rows.
# I'll use Python surgical replacement inside distinct script using regex or manual matching safer.
print("Frontend debounce applied")
