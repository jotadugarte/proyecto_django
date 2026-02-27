# System Architecture & Boundaries

**Purpose:** This document defines the unchangeable technical laws of the project. AI agents are strictly forbidden from proposing or implementing solutions that violate these boundaries unless an explicit Architectural Decision Record (ADR) is approved.

## 1. The Technology Stack
* **Language/Runtime:** [e.g., TypeScript 5.x / Ruby 3.x]
* **Core Framework:** [e.g., Expo React Native / Ruby on Rails 8]
* **Primary Database:** [e.g., SQLite via Drizzle ORM / PostgreSQL]
* **Styling/UI Engine:** [e.g., Tamagui / CSS Variables & BEM]

## 2. Architectural Paradigm
* **Design Pattern:** Architecture Layered con Service Objects para la lógica de negocio y Selectores para queries complejas.
* **State Management:** *Lazy Evaluation* para simulación de tiempo real (calcular producción on-demand basada en `last_tick` al cargar datos, sin cron jobs globales).
* **API Paradigm:** Web tradicional (Templates Django) con SSR (Server-Side Rendering).

## 3. The "Kill List" (Forbidden Patterns)
*AI Agents MUST NOT use or suggest the following under any circumstances:*
* 🚫 **Fat Controllers / Fat Views:** Toda la lógica de negocio debe residir en `services/` (mutaciones) o `selectors/` (lecturas). Las views solo manejan HTTP.
* 🚫 **N+1 Queries / individuales `.save()` en loops:** Queda prohibido iterar sobre listas para hacer `.save()` (usar `bulk_update()`) o crear registros individuales en loops (usar `bulk_create(ignore_conflicts=True)`).
* 🚫 **Mutaciones parciales de estado:** Cualquier actualización que afecte a múltiples modelos (ej. deducir recursos y subir de nivel un edificio) debe estar encapsulada en `transaction.atomic`.

## 4. Environment & Infrastructure
* **Deployment Target:** [e.g., iOS/Android App Stores / Kamal to Bare Metal]
* **Secrets Management:** [e.g., Expo SecureStore / Rails Credentials]
