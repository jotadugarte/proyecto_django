# Data Flow & Side-Effect Map

**Purpose:** Maps how entities mutate and propagate throughout the system. AI agents must consult this document to ensure they do not orphan data or bypass necessary side-effects.

## 1. Primary Data Flow
*(Building / Upgrade Request)*
1. **Client** hace POST a la vista de detalle de planeta con el ID del edificio a mejorar.
2. **Service (`core.services.building`)** valida precondiciones: calcula el costo y verifica los saldos (saldo `>=` costo).
3. **Service** ejecuta actualización transaccional (`transaction.atomic`) descontando los saldos en masa (`bulk_update`) e incrementando el nivel del edificio.
4. **Client** recibe redirect para recargar la vista.

## 2. Cascading Side Effects
*When an entity is modified, these asynchronous or secondary actions MUST occur:*

| Trigger Action | Required Side Effect | Mechanism |
|---|---|---|
| **User created** (`User` model post_save) | Se crea el `DictatorProfile` asociado. Se busca un `Planet` sin dueño y se le asocia como `main_planet`. | Django Signal (`core/signals.py`) |
| **User visits Planet** (GET a `planet_detail`) | El tiempo transcurrido desde la última visita muta los recursos (ingreso pasivo). | Call a `tick_planet_production()` en la View |
| **User visits Planet** | Se asegura la existencia de todo tipo de recurso base (`PlanetResource`) para el planeta, uniendo arrays faltantes. | Call a `bulk_create(ignore_conflicts=True)` en la View |

## 3. Caching Invalidation Strategy
* **Strategy:** [Pendiente de definir, actualmente operaciones directas sobre BD SQLite]
* **Critical Nodes:** Ninguno por el momento.
