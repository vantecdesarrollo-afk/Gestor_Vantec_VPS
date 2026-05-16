/**
 * sentinel.js - Monitor de Actividad y Gobernanza de Sesión (L6 v3.5)
 * Implementa la "Ventana Deslizable" para el control de inactividad.
 */

class SentinelMonitor {
    constructor() {
        this.inactivityTimeoutMins = 15; // Default 15
        this.maxLifetimeMins = 30;       // Default 30 (Hard logout)
        this.lastActivity = Date.now();
        this.loginTime = Date.now();
        this.checkInterval = null;
        
        // Cargar tiempos desde localStorage si existen (por si hubo recarga)
        this.loadSessionTimers();
        
        this.init();
    }

    loadSessionTimers() {
        const storedLoginTime = localStorage.getItem('sentinel_login_time');
        if (storedLoginTime) {
            this.loginTime = parseInt(storedLoginTime, 10);
        } else {
            localStorage.setItem('sentinel_login_time', this.loginTime.toString());
        }

        const storedLastActivity = localStorage.getItem('sentinel_last_activity');
        if (storedLastActivity) {
            this.lastActivity = parseInt(storedLastActivity, 10);
        }
    }

    updateActivity() {
        this.lastActivity = Date.now();
        localStorage.setItem('sentinel_last_activity', this.lastActivity.toString());
        // console.log("[SENTINEL] Actividad detectada - Timer Reiniciado");
    }

    init() {
        // Event Listeners para activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(name => {
            window.addEventListener(name, () => this.updateActivity(), { passive: true });
        });

        // Loop de verificación cada minuto
        this.checkInterval = setInterval(() => this.check(), 30000); // Revisar cada 30 segundos
        
        console.log("[SENTINEL] Monitor de actividad activado.");
    }

    check() {
        const now = Date.now();
        const inactivityDelay = (now - this.lastActivity) / 1000 / 60;
        const totalLifetime = (now - this.loginTime) / 1000 / 60;

        // 1. Verificar Inactividad (Sentinel Timeout)
        if (inactivityDelay >= this.inactivityTimeoutMins) {
            console.warn("[SENTINEL] Timeout por inactividad alcanzado.");
            this.forceLogout("Sesión expirada por inactividad.");
            return;
        }

        // 2. Verificar Max Lifetime (Hard Logout)
        if (totalLifetime >= this.maxLifetimeMins) {
            console.warn("[SENTINEL] Máximo tiempo de sesión alcanzado.");
            this.forceLogout("Máximo tiempo de seguridad alcanzado.");
            return;
        }

        // 3. Notificación próxima a expirar (Opcional, 1 min antes)
        if (inactivityDelay >= (this.inactivityTimeoutMins - 1)) {
            console.info("[SENTINEL] La sesión expirará pronto por inactividad.");
        }
    }

    forceLogout(reason) {
        if (this.checkInterval) clearInterval(this.checkInterval);
        
        // Limpiar tokens y estado sentinel
        localStorage.removeItem('token');
        localStorage.removeItem('active_entidad');
        localStorage.removeItem('sentinel_login_time');
        localStorage.removeItem('sentinel_last_activity');

        console.log("[SENTINEL] Logout forzado:", reason);
        
        // Redirigir con mensaje
        const params = new URLSearchParams({
            reason: reason,
            expired: 'true'
        });
        window.location.href = `/login?${params.toString()}`;
    }
}

// Inicializar si el path no es login
if (window.location.pathname !== '/login') {
    window.sentinel = new SentinelMonitor();
}
