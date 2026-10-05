# Optimización de estructuras de datos en una aplicación de mensajería

**Asignatura:** Diseño y análisis de algoritmos
**Unidad:** U1 - Estructuras de datos básicas

## Contexto

La startup *Fast Message* ha detectado retrasos en la entrega de mensajes
y un uso ineficiente de memoria conforme crece el número de usuarios.
El problema raíz es que los mensajes se almacenan en **listas dinámicas**,
lo que provoca:

- Búsquedas secuenciales lentas (O(n)).
- Recorridos completos para acceder a mensajes antiguos.
- Coste lineal al insertar/eliminar en posiciones intermedias.

## Solución propuesta

Se implementa una **estructura híbrida** que separa dos necesidades de
acceso distintas:

| Necesidad | Estructura | Complejidad |
|-----------|-----------|-------------|
| Buscar por `id_msg` | Tabla hash (`dict`) | O(1) promedio |
| Recuperar por rango temporal / orden cronológico | Árbol AVL indexado por `(timestamp, id_msg)` | O(log n) garantizado |
| Insertar / eliminar | Ambas estructuras sincronizadas | O(log n) |
| Rango `[t_ini, t_fin]` | AVL con poda de ramas | O(log n + k), k = resultados |

## ¿Por qué no una única estructura?

- Un **árbol balanceado solo** obligaría a recorrer niveles incluso para
  búsquedas por ID.
- Una **lista ordenada + `bisect`** consigue O(log n) al buscar la posición,
  pero `list.insert` / `list.pop` desplazan memoria → O(n) real.
- La combinación **hash + AVL** resuelve ambos accesos sin sacrificar uno
  por el otro.

## Componentes principales

- `Mensaje`: entidad con `id_msg`, origen, destino, contenido y `timestamp`.
- `ArbolAVL`: implementación propia con rotaciones simples y dobles,
  inserción, eliminación (con sucesor in-orden) y consulta por rango.
- `SistemaMensajeria`: fachada que mantiene sincronizadas ambas estructuras.

## Ejecución

python mensajeria.py

## Análisis de complejidad

| Operación |	Lista dinámica |	Hash + AVL (este prototipo) |
|-----------|-----------|-------------|
| Buscar por ID | O(n) | O(1) |
| Insertar |	O(1) al final / O(n) en medio |	O(log n) |
| Eliminar por ID |	O(n) |	O(log n) |
| Rango temporal |	O(n) |	O(log n + k) |
| Recorrido ordenado |	O(n log n) si hay que ordenar |	O(n) |
