# Gestión de procesos en un sistema operativo con pilas y colas

**Asignatura:** Diseño y análisis de algoritmos
**Unidad:** U5 — Pilas y colas

## Contexto

Un sistema operativo para dispositivos embebidos gestiona las tareas
con **listas**, lo que provoca:

- Ausencia de prioridades reales (todo se ejecuta FIFO).
- Coste lineal al buscar el siguiente proceso a ejecutar.
- Dificultad para manejar bloqueos anidados.

## Solución propuesta

Se combinan **dos estructuras complementarias**:

| Estructura | Uso | Complejidad |
|-----------|-----|-------------|
| Cola de prioridad (`heapq`) | Procesos listos, ordenados por urgencia | O(log n) insertar/extraer |
| Pila LIFO (lista) | Procesos bloqueados o en espera | O(1) push/pop |

## Ejecución

python gestor_procesos.py

## Salida esperada (resumen)

```
[COLA] Se encola 'actualizacion_interfaz' con prioridad 5
[COLA] Se encola 'interrupcion_reloj' con prioridad 0
[COLA] Se encola 'lectura_sensor' con prioridad 2
[COLA] Se encola 'guardado_registro' con prioridad 4
[EJECUCION] Se ejecuta 'interrupcion_reloj' (prioridad 0)
[EJECUCION] Se ejecuta 'lectura_sensor' (prioridad 2)
[PILA] Se bloquea 'lectura_sensor' y se apila en espera
[COLA] Se encola 'interrupcion_watchdog' con prioridad 0
[EJECUCION] Se ejecuta 'interrupcion_watchdog' (prioridad 0)
[PILA] Se reanuda 'lectura_sensor' desde la pila de bloqueados
[COLA] Se encola 'lectura_sensor' con prioridad 1
[EJECUCION] Se ejecuta 'lectura_sensor' (prioridad 1)
[EJECUCION] Se ejecuta 'guardado_registro' (prioridad 4)
```
