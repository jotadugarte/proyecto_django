# Project Specification (SPEC.md)

> **REQ-ID format:** Use `REQ-[DOMAIN]-[NNN]` for traceability (e.g. `REQ-AUTH-001`, `REQ-DASH-002`).

## 🎯 Purpose & Vision
Juego de navegador estratégico de ciencia ficción. Los jugadores administran planetas, construyen infraestructuras y producen recursos en tiempo real.

## 📖 Domain Glossary
| Term | Definition | Semantic Meaning |
|------|------------|------------------|
| Planet | Un cuerpo celeste controlado por un jugador. | Modelo principal de dominio. Contiene edificios y recursos. |
| Production Tick | El cálculo discreto de los recursos generados por un planeta en el tiempo transcurrido desde la última revisión. | Se dispara bajo demanda (Lazy Evaluation) al visitar la vista del planeta. |
| Building | Infraestructura que se construye en un planeta. | Las categorías incluyen "extraction", "defense" y "hangar". |

## 🏗️ Core Entities & Relationships
- **User / DictatorProfile**: Cada jugador se representa mediante la tabla estándar de `User` y un perfil de dictador asociado.
  - tiene un `main_planet` (FK a Planet)
- **Planet**: El centro económico y militar del juego.
  - belongs_to `owner` (DictatorProfile)
  - has_many `PlanetResource` (inventario)
  - has_many `PlanetBuilding` (infraestructuras construidas)
- **BuildingType**: Catálogo estático (o maestro) de edificios disponibles, con sus costos (`cost` JSON) y tasas de producción (`production` JSON).
- **ResourceType**: Catálogo estático de recursos (Plastilina, Energía Eólica, Café con Leche).

## 🛠️ Key Workflows & Business Logic

1. **User Registration [REQ-AUTH-001]**
   - Un usuario se registra proporcionando `username`, `first_name` y validación de `password`.
   - Automáticamente se le asigna un `DictatorProfile` y un Planeta Inicial (vía signal).

2. **Planet Production Loop (Lazy Evaluation) [REQ-PROD-001]**
   - No hay un proceso "cron" global. La producción se calcula **just-in-time** cuando se cargan los datos del planeta.
   - El `tick_planet_production` calcula los minutos transcurridos desde `last_production_tick`.
   - Para cada edificio de extracción, se suma al balance de `PlanetResource` la tasa base * nivel * minutos. Las fracciones se acumulan en `production_remainder`.

3. **Building Construction [REQ-BLD-001]**
   - Los edificios requieren recursos pagados por adelantado. La fórmula base de crecimiento es exponencial (factor 1.5 por nivel contiguo posterior al nivel 0).
   - "Planta Eolica" es el único que cuesta 0 para subir de nivel 0 a 1.
   - La transacción descuenta recursos de forma atómica y aumenta el nivel del `PlanetBuilding`.
