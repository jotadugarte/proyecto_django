# Documentación de la aplicación — Imperio Galáctico

Documento de referencia de las funcionalidades de la aplicación para desarrolladores y mantenimiento.

---

## 1. Resumen

Aplicación web tipo juego de estrategia (Django): galaxias, sistemas solares, planetas, dictadores y recursos. Los usuarios se autentican, tienen un perfil de dictador y gestionan uno o más planetas (recursos, edificios, unidades).

---

## 2. Arranque e instalación

- **Base de datos vacía:** ver [SETUP.md](SETUP.md).
- En resumen: `python manage.py migrate` y luego `python manage.py setup_game` (producción) o `python manage.py setup_game --test` (incluye usuarios de prueba).

---

## 3. Autenticación y usuarios

### 3.1 Inicio de sesión

- **URL:** `/accounts/login/` (nombre de URL: `login`).
- **Plantilla:** `core/templates/registration/login.html` (hereda de `core/base.html`).
- Campos: usuario y contraseña. Tras iniciar sesión se redirige a la portada (planeta principal del dictador).

### 3.2 Cerrar sesión

- **Ubicación:** barra lateral (nav) de la vista general del usuario, cuando está autenticado.
- **Comportamiento:** formulario POST a la URL de logout de Django (`/accounts/logout/`). Tras cerrar sesión se redirige a la pantalla de inicio de sesión.
- **Nota:** En Django 5+ el cierre de sesión debe hacerse por POST por seguridad.

### 3.3 Registro de nuevos usuarios (crear cuenta)

- **URL:** `/accounts/register/` (nombre de URL: `register`).
- **Vista:** `core.views.register`.
- **Formulario:** Usuario (obligatorio), Nombre (opcional), Contraseña y Repetir contraseña.
- **Validaciones:** usuario no duplicado, contraseñas coinciden.
- **Tras registro:** se crea el usuario; el signal `create_dictator_profile` crea el perfil Dictator y asigna automáticamente un planeta no ocupado. Redirección a la pantalla de inicio de sesión para que el usuario entre con su nueva cuenta.
- **Enlace:** en la pantalla de inicio de sesión aparece el enlace “Crear cuenta nueva” que lleva a `/accounts/register/`.

### 3.4 Asignación automática de planeta

- Al crearse un **nuevo usuario** (registro o creación por admin), el signal `core.signals.create_dictator_profile`:
  1. Crea el perfil `Dictator` asociado al usuario.
  2. Busca un planeta sin dueño (`owner__isnull=True`) de forma aleatoria.
  3. Asigna ese planeta como `owner` y como `main_planet` del dictador.
- Si no hay planetas libres, el usuario se crea pero queda sin planeta; se registra un warning en el log.

---

## 4. Setup del juego (`setup_game`)

- **Comando:** `python manage.py setup_game`.
- **Descripción:** Crea galaxia, sistemas solares, planetas, tipos de recurso/edificio/unidad y el superusuario admin. Opcionalmente crea usuarios de prueba.

### 4.1 Parámetro `--test`

- **Sin `--test` (producción):** solo se crea el superusuario `admin` (contraseña `admin`). No se crean orion ni perseo.
- **Con `--test` (pruebas):** además se crean los usuarios dictadores `orion` y `perseo` (contraseña `password123`), cada uno con un planeta asignado por el signal.

Uso:

```bash
python manage.py setup_game        # Producción: solo admin
python manage.py setup_game --test # Pruebas: admin + orion + perseo
```

### 4.2 Datos creados siempre

- Una galaxia (p. ej. Andrómeda).
- 256 sistemas solares (grid 16×16), 9 planetas por sistema.
- Tipos de recurso, edificios y unidades definidos en el comando.
- Superusuario `admin` (acceso a `/admin/`).

---

## 5. Producción de recursos en el tiempo

Los recursos del planeta se acumulan con el tiempo según los **edificios extractores** (categoría `extraction`) y su **nivel**:

- Cada vez que el usuario entra al detalle de un planeta se ejecuta un "tick" de producción: se calcula el tiempo transcurrido desde el último tick (`Planet.last_production_tick`) y se suma a cada recurso la producción correspondiente.
- Fórmula: por cada extractor con nivel ≥ 1, `producción = tasa_base_por_hora × nivel × horas_transcurridas`. La tasa base viene del campo `production` del `BuildingType` (p. ej. Planta Eólica → 20 Energía Eólica/hora a nivel 1).
- Implementación: servicio `core.services.production.tick_planet_production(planet)`, invocado al cargar la vista de detalle del planeta.
- En la ficha de cada extractor (sección Infraestructura) se muestra la **producción por minuto y por hora** de cada recurso según el nivel actual, para comprobar que la acumulación en el tiempo es correcta.

---

## 6. Interfaz de usuario (vista general)

- **Base:** `core/templates/core/base.html`.
- **Barra lateral (nav):**
  - Si no está autenticado: enlace “Iniciar sesión” (login).
  - Si está autenticado: nombre del dictador, lista “Mis Planetas” (enlaces al detalle de cada planeta) y botón **Cerrar sesión** al final del menú.
- **Contenido principal:** bloque `content` (detalle de planeta, pantalla de login, registro, etc.).

---

## 7. Admin de Django

- **URL:** `/admin/`.
- **Usuario por defecto (creado por `setup_game`):** `admin` / contraseña `admin`. Debe cambiarse en producción.

---

## 8. Archivos relevantes por funcionalidad

| Funcionalidad        | Archivos principales |
|----------------------|----------------------|
| Login                | `django.contrib.auth.urls`, `core/templates/registration/login.html` |
| Logout               | `core/templates/core/base.html` (form POST), `LOGOUT_REDIRECT_URL` en settings |
| Registro             | `core/forms.py` (`UserRegistrationForm`), `core/views.py` (`register`), `core/templates/registration/register.html`, `mi_juego/urls.py` (ruta `register`) |
| Asignación de planeta| `core/signals.py` (`create_dictator_profile`) |
| Setup juego          | `core/management/commands/setup_game.py` |
| Vista base / nav     | `core/templates/core/base.html` |
| Producción en el tiempo | `core/models.Planet.last_production_tick`, `core/services/production.py` (`tick_planet_production`), llamada en `core/views.py` (`planet_detail`) |

---

## 9. Referencias

- [SETUP.md](SETUP.md) — Arranque con base de datos vacía.
- [ROADMAP.md](ROADMAP.md) — Roadmap del proyecto.
- [docs/core/SPEC.md](core/SPEC.md) — Especificación y requisitos.
- [docs/core/SYSTEM_ARCHITECTURE.md](core/SYSTEM_ARCHITECTURE.md) — Arquitectura del sistema.
