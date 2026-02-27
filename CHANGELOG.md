# Changelog

All notable user-facing and config changes are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Producción en el tiempo:** Los recursos del planeta se acumulan según el nivel de los edificios extractores; cada visita al detalle del planeta aplica un tick de producción (REQ-PROD-001).
- **Producción por minuto/hora en UI:** En la ficha de cada extractor se muestra la producción actual por minuto y por hora (REQ-PROD-002).
- **Registro de usuarios:** Pantalla de creación de cuenta (`/accounts/register/`) con usuario, nombre y contraseña; enlace "Crear cuenta nueva" en la pantalla de login.
- **Cerrar sesión:** Botón "Cerrar sesión" en la barra lateral (POST a logout).
- **Setup del juego:** Comando `setup_game` crea admin y universo; opción `--test` crea además usuarios orion y perseo.
- **Documentación:** `docs/APPLICATION.md`, `docs/SETUP.md`; ROADMAP con REQ-IDs (REQ-PROD-*, REQ-CONFIG-001, REQ-COMBAT-*).

### Fixed
- **Bug:** Recursos no acumulaban porque la producción fraccionaria se truncaba a entero. Solución: campo `production_remainder` en Planet para acumular decimales entre ticks (REQ-PROD-003).

### Changed
- Asignación automática de planeta al crear usuario (signal) mejorada con logging en lugar de `print`.
- Index (portada) captura `ObjectDoesNotExist` en lugar de `except: pass`.
- Lógica de lista de edificios del planeta extraída al selector `get_buildings_info_for_planet`.
- Servicio de producción dividido en `_compute_produced` y `_apply_production_to_planet` con precondición de planeta persistido.
