# Uso de recursión en el cálculo de rutas óptimas para drones de entrega

**Asignatura:** Diseño y análisis de algoritmos
**Unidad:** U2 — Programación recursiva

## Contexto

*Sky Delivery* usa drones para repartir paquetes en zonas urbanas. El
algoritmo iterativo actual basado en aproximaciones no siempre encuentra
la mejor ruta. Se busca una solución **recursiva** que garantice el
óptimo y que sea eficiente en tiempo y memoria.

El problema real es un **TSP** (Traveling Salesman Problem): recorrer
todos los puntos de entrega partiendo y volviendo al Depot con coste
mínimo.

## Solución propuesta

El script implementa y compara **tres estrategias** sobre el mismo
problema exacto, más una utilidad auxiliar:

| # | Estrategia | Tipo | Complejidad | Óptimo |
|---|-----------|------|-------------|--------|
| 1 | Backtracking recursivo + memoización (Held-Karp top-down) | Recursivo | O(n²·2ⁿ) | Sí |
| 2 | Programación dinámica por máscaras (Held-Karp bottom-up) | Iterativo | O(n²·2ⁿ) | Sí |
| 3 | Vecino más próximo | Heurística voraz | O(n²) | No |
| 4 | Dijkstra (utilidad auxiliar) | Iterativo | O((V+E)·log V) | - (resuelve otro problema) |

## Ejecución

python drones.py

## Salida esperada (resumen)

```
[1. RECURSIVO]      Ruta: Depot → A → B → C → D → Depot   Coste: 1450 m
[2. ITERATIVO]      Ruta: Depot → A → B → C → D → Depot   Coste: 1450 m
[3. HEURÍSTICA]     Ruta: ...                              Coste: 1450 m (+0.0 %)
[4. ESCALABILIDAD]  13 clientes: recursivo ~0.5 s, iterativo ~0.1 s
[5. DIJKSTRA]       Suma de trayectos independientes: 1900 m (≠ TSP)
```
