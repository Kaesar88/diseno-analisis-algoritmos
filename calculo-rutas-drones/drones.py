"""
Rutas óptimas para drones — Caso 02

Compara tres estrategias sobre EL MISMO problema exacto (recorrer todos
los puntos de entrega y volver al Depot con el coste mínimo, es decir,
un TSP) y añade una cuarta para cuando el número de puntos crece
demasiado para un enfoque exacto:

  1. Recursivo con backtracking + memoización (top-down, Held-Karp)
  2. Iterativo con programación dinámica ascendente por máscaras de bits
     (bottom-up, mismo algoritmo de Held-Karp, sin llamadas recursivas)
  3. Heurística iterativa del vecino más próximo (no óptima, escalable)

Dijkstra se incluye aparte como utilidad de referencia: resuelve el
camino mínimo ENTRE DOS puntos, un problema distinto del TSP, y no debe
tomarse como una alternativa a recorrer todos los puntos de entrega.
"""
import heapq
import random
import time
from functools import lru_cache

# ─── Grafo de ejemplo: 5 puntos de entrega (depot + 4 clientes) ───────────────
# Pesos = distancia en metros (0 = sin enlace directo)
PUNTOS = ["Depot", "A", "B", "C", "D"]
DISTANCIAS = {
    ("Depot","A"):300, ("A","Depot"):300,
    ("Depot","B"):500, ("B","Depot"):500,
    ("Depot","C"):700, ("C","Depot"):700,
    ("Depot","D"):400, ("D","Depot"):400,
    ("A","B"):200,     ("B","A"):200,
    ("A","C"):600,     ("C","A"):600,
    ("A","D"):350,     ("D","A"):350,
    ("B","C"):250,     ("C","B"):250,
    ("B","D"):450,     ("D","B"):450,
    ("C","D"):300,     ("D","C"):300,
}


def generar_grafo_aleatorio(n_clientes, semilla=42, dist_min=100, dist_max=900):
    """Genera un grafo completo simétrico (Depot + n_clientes) con distancias
    aleatorias pero reproducibles (misma semilla -> mismo grafo), para
    probar la escalabilidad de cada enfoque más allá del ejemplo de 4 clientes."""
    rng = random.Random(semilla)
    puntos = ["Depot"] + [f"P{i}" for i in range(1, n_clientes + 1)]
    distancias = {}
    for i, a in enumerate(puntos):
        for b in puntos[i + 1:]:
            d = rng.randint(dist_min, dist_max)
            distancias[(a, b)] = d
            distancias[(b, a)] = d
    return puntos, distancias


# ─── 1. RECURSIVO: backtracking + memoización sobre subconjuntos (top-down) ──
def crear_tsp_recursivo(distancias):
    """Fábrica: crea una función recursiva memoizada ligada a un 'distancias'
    concreto. Cada grafo recibe su propia caché (lru_cache), evitando mezclar
    resultados entre problemas distintos."""

    def d(a, b):
        return distancias.get((a, b), float("inf"))

    @lru_cache(maxsize=None)
    def tsp(actual, pendientes, depot):
        """Coste y ruta mínimos desde 'actual', visitando 'pendientes' y
        volviendo a 'depot'. Estado = (nodo actual, subconjunto pendiente)."""
        if not pendientes:
            return d(actual, depot), [actual, depot]

        mejor_coste = float("inf")
        mejor_ruta = []
        # sorted() fija un orden de exploración determinista: sin él, el
        # orden de iteración de un frozenset de cadenas depende del hash
        # aleatorio de cada proceso Python y, ante empates de coste, el
        # resultado impreso cambiaría de una ejecución a otra.
        for siguiente in sorted(pendientes):
            coste_salto = d(actual, siguiente)
            if coste_salto == float("inf"):
                continue
            nuevos_pendientes = pendientes - frozenset([siguiente])
            coste_resto, ruta_resto = tsp(siguiente, nuevos_pendientes, depot)
            coste_total = coste_salto + coste_resto
            if coste_total < mejor_coste:
                mejor_coste = coste_total
                mejor_ruta = [actual] + ruta_resto

        return mejor_coste, mejor_ruta

    return tsp


# ─── 2. ITERATIVO: programación dinámica ascendente por máscaras (bottom-up) ─
def tsp_iterativo_bitmask(distancias, puntos):
    """Resuelve el MISMO TSP exacto que tsp_recursivo, pero de forma
    iterativa (algoritmo de Held-Karp clásico, sin recursión): construye
    la tabla dp[mask][i] = coste mínimo para visitar exactamente los
    clientes de 'mask' terminando en el cliente i, partiendo del Depot.

    Misma complejidad teórica O(n²·2ⁿ) que la versión recursiva
    memoizada; comparar ambas mide la sobrecarga real de la recursión
    (llamadas de función, hash de frozensets) frente a un bucle
    explícito con arrays, no una diferencia algorítmica de fondo."""
    depot = puntos[0]
    clientes = puntos[1:]
    n = len(clientes)

    def d(a, b):
        return distancias.get((a, b), float("inf"))

    dist_depot = [d(depot, c) for c in clientes]
    dist_regreso = [d(c, depot) for c in clientes]
    dist_entre = [[d(clientes[i], clientes[j]) for j in range(n)] for i in range(n)]

    NINF = float("inf")
    dp = [[NINF] * n for _ in range(1 << n)]
    padre = [[-1] * n for _ in range(1 << n)]

    for i in range(n):
        dp[1 << i][i] = dist_depot[i]

    for mask in range(1 << n):
        for i in range(n):
            if not (mask & (1 << i)) or dp[mask][i] == NINF:
                continue
            coste_actual = dp[mask][i]
            for j in range(n):
                if mask & (1 << j):
                    continue
                nuevo_mask = mask | (1 << j)
                nuevo_coste = coste_actual + dist_entre[i][j]
                if nuevo_coste < dp[nuevo_mask][j]:
                    dp[nuevo_mask][j] = nuevo_coste
                    padre[nuevo_mask][j] = i

    mask_completo = (1 << n) - 1
    mejor_coste, mejor_ultimo = NINF, -1
    for i in range(n):
        if dp[mask_completo][i] == NINF:
            continue
        coste = dp[mask_completo][i] + dist_regreso[i]
        if coste < mejor_coste:
            mejor_coste, mejor_ultimo = coste, i

    # Reconstrucción de la ruta a partir de los punteros 'padre'
    ruta_idx, mask, actual = [], mask_completo, mejor_ultimo
    while actual != -1:
        ruta_idx.append(actual)
        anterior = padre[mask][actual]
        mask ^= (1 << actual)
        actual = anterior
    ruta_idx.reverse()
    ruta = [depot] + [clientes[i] for i in ruta_idx] + [depot]

    tamano_tabla = len(dp) * n  # memoria asignada: 2^n * n celdas
    estados_validos = sum(1 for fila in dp for v in fila if v != NINF)  # subproblemas realmente alcanzables
    return mejor_coste, ruta, tamano_tabla, estados_validos


# ─── 3. HEURÍSTICA ITERATIVA: vecino más próximo (no óptima, escalable) ──────
def tsp_vecino_mas_proximo(distancias, puntos):
    """Heurística voraz: en cada paso salta al cliente pendiente más
    cercano. No garantiza el óptimo, pero es O(n²) en tiempo y O(n) en
    memoria: la alternativa práctica cuando el número de puntos de
    entrega crece demasiado para un enfoque exacto (recursivo o
    iterativo por máscaras, ambos O(n²·2ⁿ))."""
    depot = puntos[0]
    pendientes = set(puntos[1:])
    actual = depot
    ruta = [depot]
    coste_total = 0.0

    while pendientes:
        siguiente = min(pendientes, key=lambda p: distancias.get((actual, p), float("inf")))
        coste_total += distancias.get((actual, siguiente), float("inf"))
        ruta.append(siguiente)
        pendientes.remove(siguiente)
        actual = siguiente

    coste_total += distancias.get((actual, depot), float("inf"))
    ruta.append(depot)
    return coste_total, ruta


# ─── 4. Dijkstra: camino mínimo ENTRE DOS puntos (utilidad auxiliar) ─────────
def dijkstra(origen, destino, nodos, dist_fn):
    """Dijkstra clásico con cola de prioridad. Resuelve el camino mínimo
    entre dos nodos concretos: un problema distinto del TSP. Se incluye
    como referencia del enfoque iterativo clásico del temario, no como
    alternativa para visitar todos los puntos de entrega."""
    distancias = {n: float("inf") for n in nodos}
    distancias[origen] = 0
    previo = {n: None for n in nodos}
    cola = [(0, origen)]

    while cola:
        coste_actual, nodo = heapq.heappop(cola)
        if nodo == destino:
            break
        if coste_actual > distancias[nodo]:
            continue
        for vecino in nodos:
            d = dist_fn(nodo, vecino)
            if d < float("inf"):
                nuevo_coste = distancias[nodo] + d
                if nuevo_coste < distancias[vecino]:
                    distancias[vecino] = nuevo_coste
                    previo[vecino] = nodo
                    heapq.heappush(cola, (nuevo_coste, vecino))

    ruta, nodo = [], destino
    while nodo:
        ruta.append(nodo)
        nodo = previo[nodo]
    ruta.reverse()
    return distancias[destino], ruta


# ─── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clientes = frozenset(PUNTOS[1:])

    print("=" * 70)
    print("  RUTAS ÓPTIMAS PARA DRONES — recursivo vs. iterativo vs. heurística")
    print("=" * 70)

    # --- 1) Recursivo (top-down, memoizado) ---
    tsp_rec = crear_tsp_recursivo(DISTANCIAS)
    t0 = time.perf_counter()
    coste_rec, ruta_rec = tsp_rec("Depot", clientes, "Depot")
    t_rec = (time.perf_counter() - t0) * 1000
    estados_rec = tsp_rec.cache_info().currsize

    print("\n[1. RECURSIVO — backtracking + memoización, top-down]")
    print(f"  Ruta óptima : {' -> '.join(ruta_rec)}")
    print(f"  Coste total : {coste_rec} m")
    print(f"  Tiempo      : {t_rec:.4f} ms")
    print(f"  Subproblemas en caché: {estados_rec}")

    # --- 2) Iterativo (bottom-up, mismo problema exacto) ---
    t0 = time.perf_counter()
    coste_it, ruta_it, tamano_tabla_it, estados_it = tsp_iterativo_bitmask(DISTANCIAS, PUNTOS)
    t_it = (time.perf_counter() - t0) * 1000

    print("\n[2. ITERATIVO — programación dinámica por máscaras, bottom-up]")
    print(f"  Ruta óptima : {' -> '.join(ruta_it)}")
    print(f"  Coste total : {coste_it} m")
    print(f"  Tiempo      : {t_it:.4f} ms")
    print(f"  Subproblemas alcanzables: {estados_it}  (tabla dp asignada: {tamano_tabla_it} celdas)")
    print(f"  ¿Coincide con el recursivo? {'sí' if coste_it == coste_rec else 'NO'}")

    # --- 3) Heurística (vecino más próximo) ---
    t0 = time.perf_counter()
    coste_vmp, ruta_vmp = tsp_vecino_mas_proximo(DISTANCIAS, PUNTOS)
    t_vmp = (time.perf_counter() - t0) * 1000
    desviacion = (coste_vmp / coste_rec - 1) * 100

    print("\n[3. HEURÍSTICA — vecino más próximo (no garantiza el óptimo)]")
    print(f"  Ruta obtenida : {' -> '.join(ruta_vmp)}")
    print(f"  Coste total   : {coste_vmp} m")
    print(f"  Tiempo        : {t_vmp:.4f} ms")
    print(f"  Desviación sobre el óptimo: {desviacion:.1f} %")

    # --- 4) Escalabilidad: grafo sintético con más puntos de entrega ---
    N_GRANDE = 13
    print(f"\n[4. ESCALABILIDAD — grafo sintético de {N_GRANDE} clientes, semilla fija]")
    puntos_g, distancias_g = generar_grafo_aleatorio(n_clientes=N_GRANDE, semilla=42)
    clientes_g = frozenset(puntos_g[1:])

    tsp_rec_g = crear_tsp_recursivo(distancias_g)
    t0 = time.perf_counter()
    coste_rec_g, _ = tsp_rec_g("Depot", clientes_g, "Depot")
    t_rec_g = time.perf_counter() - t0

    t0 = time.perf_counter()
    coste_it_g, _, tamano_tabla_it_g, estados_it_g = tsp_iterativo_bitmask(distancias_g, puntos_g)
    t_it_g = time.perf_counter() - t0

    t0 = time.perf_counter()
    coste_vmp_g, _ = tsp_vecino_mas_proximo(distancias_g, puntos_g)
    t_vmp_g = time.perf_counter() - t0

    print(f"  Recursivo (exacto)  : {coste_rec_g} m en {t_rec_g:.3f} s "
          f"({tsp_rec_g.cache_info().currsize} subproblemas en caché)")
    print(f"  Iterativo (exacto)  : {coste_it_g} m en {t_it_g:.3f} s "
          f"({estados_it_g} subproblemas alcanzables)")
    print(f"  Heurística (aprox.) : {coste_vmp_g} m en {t_vmp_g * 1000:.3f} ms "
          f"(+{(coste_vmp_g / coste_rec_g - 1) * 100:.1f} % sobre el óptimo)")
    print(f"  Nota: con {N_GRANDE} clientes hay 2^{N_GRANDE} = {1 << N_GRANDE} subconjuntos;")
    print("        añadir un cliente más duplica el trabajo de ambos enfoques")
    print("        exactos, mientras la heurística sigue creciendo como n².")

    # --- 5) Dijkstra: utilidad auxiliar de camino mínimo puntual ---
    print("\n[5. DIJKSTRA — camino mínimo Depot -> cada cliente (no resuelve el TSP)]")
    total_dijkstra = 0
    for cliente in sorted(clientes):
        coste_d, ruta_d = dijkstra(
            "Depot", cliente, PUNTOS,
            lambda a, b: DISTANCIAS.get((a, b), float("inf"))
        )
        total_dijkstra += coste_d
        print(f"  Depot -> {cliente}: {' -> '.join(ruta_d)}  ({coste_d} m)")
    print(f"  Suma de trayectos independientes: {total_dijkstra} m (no es una ruta circular)")

    print("\n" + "=" * 70)
    print("  COMPARATIVA FINAL (grafo de ejemplo, 4 clientes)")
    print(f"  Recursivo  : {coste_rec} m")
    print(f"  Iterativo  : {coste_it} m")
    print(f"  Heurística : {coste_vmp} m  (+{desviacion:.1f} %)")
    print("=" * 70)
