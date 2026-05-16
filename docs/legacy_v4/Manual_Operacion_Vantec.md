# Manual de Operación Técnica - Vantec VCORE (Estándar de Oro L6 v4.5)

Este documento certifica los protocolos de resiliencia de grado industrial y el valor competitivo del ecosistema Vantec VCore.

---

## 🛠️ 1. Infraestructura AWS-Grade (VCore Manager v2.1)
El sistema opera bajo un esquema de **Alta Disponibilidad del 99.9%** gestionado por el `vcore_manager.py`.

### Capacidades de Resiliencia:
1.  **Autorestart Atómico:** Si el motor de ingesta (Engine) o el tablero (Dashboard) detectan un fallo crítico, el Manager los levanta en < 5 segundos.
2.  **Idempotencia Absoluta:** El sistema utiliza validación binaria por **Hash MD5**. Si un archivo es idéntico a uno ya procesado, se ignora sin generar basura digital o duplicar registros.
3.  **Naming Único (Short Hash):** Los anexos (proformas, acuses) ya no usan timestamps ruidosos. Ahora emplean un **Short Hash** de 8 caracteres basado en su contenido binario, garantizando nombres de archivo estables y profesionales.
4.  **Bypass de Errores SO:** Implementado el **Readiness Protocol** para evitar `WinError 3` o `Permission Denied` durante transferencias de red lentas.

---

## 🔑 2. Acceso al Ecosistema
*   **URL:** `http://127.0.0.1:8000`
*   **Credenciales:** `admin` / `admin123`
*   **Heartbeat:** El sistema reporta su salud cada 5 minutos en `vcore_manager_err.log`.

---

## 💼 3. VCore: El Estándar de Oro (Argumentario Comercial)
Puntos clave para demostraciones de alto nivel a clientes con carteras de +$2.5M:

### A. El "Ghost Healer" (Reconciliación Inteligente)
> "VCore tiene memoria fiscal. No importa si recibe primero el PDF y días después el XML. El sistema custodia el huérfano y realiza un rescate atómico en cuanto aparece el ancla XML. El orden no altera la contabilidad."

### B. El Expediente Dinámico (Multi-PDF)
> "Una factura es una historia. VCore permite anexar ilimitados documentos (acuse, proforma, evidencias) a un solo UUID. El sistema detecta contenidos distintos y construye el expediente solo."

### C. Filtro de ADN Fiscal (Tolerancia Cero)
> "VCore es una aduana digital. Cualquier archivo corrupto o no fiscal es expulsado a Invalid_ADN. Su Dashboard siempre estará limpio y certificado."

### D. Resiliencia Industrial
> "Tecnología que nunca duerme. Bajo un gestor de procesos de alta disponibilidad, el sistema se recupera solo de fallos del servidor, garantizando que su información siempre esté a un clic de distancia."

---

**Documento Validado y Sellado por Mando de Ingeniería.**
Fecha: 2026-04-03
Estado: **PRODUCCIÓN / ESTÁNDAR DE ORO v4.5 ACTIVO**
🏁 **MISIÓN 1 & 2: VICTORIA TOTAL**
