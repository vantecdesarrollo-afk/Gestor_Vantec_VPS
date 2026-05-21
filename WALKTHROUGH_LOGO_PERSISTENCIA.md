# Walkthrough: Restoring and Hardening Logo Persistency & GUI explorers (VPS & Local)

During container redeployments, updates, and rebuilds on the VPS via Coolify, custom-uploaded tenant logos were disappearing, resulting in broken image icons and 404 errors. Additionally, the "Emisión" document explorer screen was freezing and stuck loading. This walkthrough explains the root causes of these issues, documents the complete changes implemented to prevent them, and outlines the results.

---

## 🔍 Root Cause Analysis

1. **Ephemeral Writes for Logos**: Previously, logo files uploaded when creating or updating a tenant were written directly to `static/logos` inside the container/project root.
2. **Container Ephemerality**: In modern environments like Docker/Coolify, the container filesystem is ephemeral. Rebuilding or updating a service completely wipes the old image filesystem and creates a new one from scratch.
3. **Missing Persistence**: While Coolify mounts the persistent volume `/app/Operacion_CFDI` (mapped to `settings.STORAGE_PATH`), the `static/logos` folder was *not* placed inside this volume. Consequently, any uploaded logos were immediately lost upon redeployment.
4. **Mixed Content blocking of `cfdis.js`**: When accessing the portal via secure HTTPS (`https://apivcore.vantec-consultores.com.mx`), the explorer page was completely freezing and stuck on "Cargando documentos..." because the browser's console blocked `cfdis.js` as Mixed Content. The FastAPI app runs behind an SSL-terminating reverse proxy. Using the Jinja template helper `{{ url_for('static', path='/js/cfdis.js') }}` resolved the scheme using the forwarded HTTP protocol, generating a plain `http://` URL. The browser blocked this script as unsafe Mixed Content under HTTPS, preventing the rendering code from starting.

---

## 🛠️ Implemented Architectural Solutions

To resolve the regression completely, we applied a **zero-migration, auto-recovering** persistence model and secure script loading:

### 1. Unified Endpoint Alignment
We updated both endpoints (`create_entidad` and `update_entidad`) in **both** paths (`src/` and `VCore_Release_v6.4.1_GOLD/src/`) to write directly to the persistent volume path `settings.STORAGE_PATH / "logos"`:
* **Files Modified**:
  - `src/api/endpoints/admin.py`
  - `VCore_Release_v6.4.1_GOLD/src/api/endpoints/admin.py`

```python
if logo_file and logo_file.filename:
     from src.core.config import settings
     logos_dir = os.path.join(settings.STORAGE_PATH, "logos")
     os.makedirs(logos_dir, exist_ok=True)
     filename = f"{uuid.uuid4()}_{logo_file.filename}"
     tenant.logo_path = f"/static/logos/{filename}"
     with open(os.path.join(logos_dir, filename), "wb") as buffer:
          shutil.copyfileobj(logo_file.file, buffer)
```

> [!NOTE]
> By keeping `tenant.logo_path = f"/static/logos/{filename}"` in the database, we achieve **100% backward compatibility** with existing rows in the database and frontend routers without requiring a schema migration.

---

### 2. Auto-Migration Engine (Self-Healing Lifespan)
We added a startup migration helper to the FastAPI `lifespan` in both development and GOLD files. If the container or server boots up and finds files in the legacy/ephemeral `static/logos/` directory, it automatically copies them to the persistent `storage/logos/` folder:
* **Files Modified**:
  - `src/main.py`
  - `VCore_Release_v6.4.1_GOLD/src/main.py`

```python
# --- AUTO-MIGRACIÓN DE LOGOS EXISTENTES A ALMACENAMIENTO PERSISTENTE ---
try:
    from src.core.config import settings
    logos_dir = os.path.join(settings.STORAGE_PATH, "logos")
    os.makedirs(logos_dir, exist_ok=True)
    
    old_logos_dir = os.path.join(STATIC_DIR, "logos")
    if os.path.exists(old_logos_dir):
        print(f"[LIFESPAN] Verificando logotipos antiguos en: {old_logos_dir}...")
        for filename in os.listdir(old_logos_dir):
            old_file = os.path.join(old_logos_dir, filename)
            new_file = os.path.join(logos_dir, filename)
            if os.path.isfile(old_file) and not os.path.exists(new_file):
                shutil.copy2(old_file, new_file)
                print(f"[LIFESPAN] Logo migrado correctamente a persistente: {filename}")
except Exception as e:
    print(f"[LIFESPAN] Advertencia en migración de logotipos: {e}")
```

---

### 3. Tenant-Neutral Auth Middleware Fix
We identified that the `multi_tenant_middleware` was intercepting all `/api/` paths and enforcing the presence of `X-Entidad-ID`. For endpoints like `/api/v1/auth/refresh` and `/api/v1/auth/me`, a tenant ID context is not applicable.
- **Solution**: We explicitly defined `TENANT_NEUTRAL_ROUTES` in the middleware to bypass `X-Entidad-ID` validation for `/api/v1/auth/refresh` and `/api/v1/auth/me`.
* **Files Modified**:
  - `src/api/middleware.py`
  - `VCore_Release_v6.4.1_GOLD/src/api/middleware.py`

---

### 4. Robust Folio Type Casting in frontend (`cfdis.js`)
We identified that if the database or the backend returns `folio` as an integer (e.g. `804`) instead of a string, calling `cfdi.folio.replace(/^0+/, '')` throws a `TypeError: cfdi.folio.replace is not a function`, freezing the rendering loop.
- **Solution**: We wrapped all occurrences of `folio` replaces in `static/js/cfdis.js` and `VCore_Release_v6.4.1_GOLD/static/js/cfdis.js` to cast `folio` to a String safely before executing the regex replace.
* **Files Modified**:
  - `static/js/cfdis.js`
  - `VCore_Release_v6.4.1_GOLD/static/js/cfdis.js`

---

### 5. Prevent browser HTTPS Mixed Content blocking of script assets
We modified all references to `/js/cfdis.js` in `cfdis.html` and `cfdisBK.html` (under both dev and GOLD release structures) to use domain-relative root-level paths (`src="/static/js/cfdis.js?v=..."`). This guarantees that scripts automatically inherit the active browser protocol (`https://`) and domain, completely bypassing the security blocks.

* **Files Modified**:
  - `templates/cfdis.html`
  - `templates/cfdisBK.html`
  - `VCore_Release_v6.4.1_GOLD/templates/cfdis.html`
  - `VCore_Release_v6.4.1_GOLD/templates/cfdisBK.html`

```html
<script src="/static/js/cfdis.js?v=2.200_L6_UX"></script>
```

---

## 🔬 Verification & Operational Steps

1. **Auto-Migration during deployment**: Confirmed by startup logs. Legacy logos committed to the repository were safely copied to the persistent volume `/app/Operacion_CFDI/logos`.
2. **Uploading Logo one last time**: Since the old dynamic logo was in the old container's ephemeral cache, please go to **Configuración > Editar Empresa** and upload the company logo one last time. It will write directly to the persistent volume mount and will **never** be lost again.
3. **No more Mixed Content errors**: The relative root script source guarantees the script loads safely via secure HTTPS.
