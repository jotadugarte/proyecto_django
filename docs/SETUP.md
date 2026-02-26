# Arranque del proyecto (base de datos vacía)

Si borras la base de datos (`db.sqlite3`) o arrancas desde cero:

1. **Migrar**
   ```bash
   python manage.py migrate
   ```

2. **Cargar universo y usuarios**
   - **Producción** (solo admin):
     ```bash
     python manage.py setup_game
     ```
   - **Pruebas** (admin + usuarios orion y perseo):
     ```bash
     python manage.py setup_game --test
     ```

Esto crea siempre:

- Galaxia, 256 sistemas solares, 9 planetas por sistema
- Tipos de recurso, edificios y unidades
- **Superusuario admin:** usuario `admin`, contraseña `admin` (acceso a `/admin/`)

Con `--test` además se crean los usuarios dictadores `orion` y `perseo` (contraseña `password123`), cada uno con un planeta asignado.

Cambia las contraseñas en producción.
