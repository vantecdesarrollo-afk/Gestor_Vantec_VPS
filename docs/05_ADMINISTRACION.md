# ??? PILAR 5: MANUAL DE ADMINISTRACION Y GOBERNANZA (VCore v5.0.0)
**Estatus:** Uso Exclusivo para Oficiales de Administracion Vantec.
**Objetivo:** Gestion de identidades, entidades y seguridad perimetral.

---

## 1. Panel de Control Super Admin
El centro neuralgico de VCore permite la gestion centralizada del ecosistema. Desde esta interfaz, el Administrador tiene visibilidad total sobre la infraestructura de datos y la capacidad de orquestar Entidades (Tenants) y Usuarios.

## 2. Gestion de Entidades (Tenants)
VCore opera bajo una arquitectura multi-inquilino donde cada empresa es un bunker aislado.
* **Registro Institucional:** Es mandatorio registrar el RFC y la Razon Social exacta.
* **Identidad Visual:** Se debe cargar el logotipo corporativo para que el Dashboard y los reportes hereden la identidad visual del cliente.

## 3. Gestion de Usuarios y Roles de Combate
El ecosistema protege el acceso mediante una jerarquia de responsabilidades clara. Por seguridad, el sistema asigna el rango de **VISOR** de forma predeterminada.

### Jerarquia de Roles:
* **SUPER ADMINISTRADOR (Global):** Dueno de la infraestructura. Unico perfil autorizado para registrar nuevas empresas.
* **ADMINISTRADOR (Entidad):** Autoridad total sobre una empresa especifica. Gestiona sus propios usuarios y configuraciones.
* **VISOR (Consulta):** Acceso limitado a la visualizacion y descarga de activos, sin permisos de alteracion.

## 4. Matriz de Acceso y Aislamiento L6
VCore garantiza que un usuario de la "Empresa A" jamas pueda visualizar datos de la "Empresa B". El aislamiento es atomico a nivel de consulta SQL. El Administrador debe validar que cada usuario tenga asignada la autoridad administrativa correcta.

## 5. Protocolos de Seguridad Activa y Sesiones
VCore implementa medidas de proteccion perimetral para garantizar que el acceso sea siempre legitimo.

### Control de Sesiones (Motor Sentinel)
* **Caducidad Automatica:** Si no se detecta interaccion en un periodo prolongado, el motor Sentinel cerrara la sesion de forma automatica.
* **Proposito:** Evitar accesos no autorizados en estaciones de trabajo desatendidas.

### Politica de Identidades y Credenciales
* **Complejidad Industrial:** Las contrasenas exigen un estandar de 8+ caracteres, incluyendo Mayuscula, Numero y Caracter Especial.
* **Blindaje de Boveda:** Todas las credenciales se almacenan mediante cifrado AES-256 a nivel de base de datos.
* **Motor SMTP:** Es mandatorio configurar el servidor de salida para habilitar los tokens de recuperacion de acceso y notificaciones.

---
## ??? CHECKLIST DE ADMINISTRACION (CTO)
| Requisito | Accion Requerida | Estado |
| :--- | :--- | :---: |
| **Aislamiento** | ?Se valido que el usuario no vea datos de otro RFC? | ? |
| **Identidad** | ?El logotipo del cliente carga correctamente en reportes? | ? |
| **Sentinel** | ?La sesion expira correctamente tras inactividad? | ? |