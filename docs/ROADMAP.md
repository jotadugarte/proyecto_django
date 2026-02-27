# Project Roadmap

Things done and things left to do. Update this when finishing branches; use `roadmap-manage` to add, prioritize, or catalog items.

**Format:** Use `[x]` for done, `[ ]` for pending. Add `(REQ-ID)` to link to SPEC. Add `— YYYY-MM-DD` for done date. Add `— Branch: name` for in-progress. Add `— Depends on: Item` for dependencies.

---

## Done
- [x] Que los recursos se vayan acumulando con el tiempo según el nivel del extractor. (REQ-PROD-001) — 2026-02-26
- [x] Mostrar producción por minuto y por hora en la ficha de cada extractor. (REQ-PROD-002) — 2026-02-26
- [x] **Bug:** Recursos no acumulaban (producción fraccionaria se truncaba a entero). Solución: campo `production_remainder` en Planet. (REQ-PROD-003) — 2026-02-26

## In Progress
- (ninguno)

## Pending (by priority)
1. Los usuarios administradores y Game Master no deben tener un planeta asignado; solo deben tener acceso al panel de Administración. (REQ-ADMIN-001)
2. Panel de Administración: crear usuarios y asignar roles. Solo superusuarios pueden crear otros superusuarios y Game Masters; los Game Masters solo pueden crear otros Game Masters. (REQ-ADMIN-002)
3. Crear una pantalla de configuración de valores: costes por nivel de edificios, costes de naves y defensas, producción por hora de extractores. (REQ-CONFIG-001)
4. Crear la capacidad de atacar otros planetas por recursos. (REQ-COMBAT-001)
5. Dar visibilidad del ataque al dictador que recibe el ataque. (REQ-COMBAT-002)

## Backlog
- (ninguno)
