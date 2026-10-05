"""
Prototipo de sistema de mensajería con estructura híbrida:
  1. Tabla hash (dict) para acceso O(1) por ID de mensaje.
  2. Árbol AVL (balanceado) indexado por (timestamp, id_msg) para
     recuperar mensajes en orden cronológico y por rangos de tiempo,
     con O(log n) garantizado en el peor caso por operación.

Respecto a la versión anterior (lista ordenada + bisect.insort): buscar
la posición de inserción con bisect es O(log n), pero insort y list.pop
desplazan elementos contiguos en memoria, lo que cuesta O(n) en el peor
caso. Un árbol AVL evita ese desplazamiento: garantiza que la diferencia
de alturas entre subárboles nunca supera 1, por lo que insertar, eliminar
y localizar los límites de un rango cuestan O(log n) en el peor caso.
"""
import time


class Mensaje:
    def __init__(self, id_msg, usuario_origen, usuario_destino, contenido):
        self.id_msg = id_msg
        self.usuario_origen = usuario_origen
        self.usuario_destino = usuario_destino
        self.contenido = contenido
        self.timestamp = time.time()

    def __repr__(self):
        return f"[{self.id_msg}] {self.usuario_origen}->{self.usuario_destino}: '{self.contenido}'"


# ─── Árbol AVL: nodo y operaciones de balanceo ────────────────────────────────
class _NodoAVL:
    __slots__ = ("clave", "id_msg", "izq", "der", "altura")

    def __init__(self, clave, id_msg):
        self.clave = clave      # tupla (timestamp, id_msg); desempata timestamps iguales
        self.id_msg = id_msg
        self.izq = None
        self.der = None
        self.altura = 1


def _altura(nodo):
    return nodo.altura if nodo else 0


def _factor_balance(nodo):
    return _altura(nodo.izq) - _altura(nodo.der) if nodo else 0


def _actualizar_altura(nodo):
    nodo.altura = 1 + max(_altura(nodo.izq), _altura(nodo.der))


def _rotar_derecha(y):
    x = y.izq
    t2 = x.der
    x.der = y
    y.izq = t2
    _actualizar_altura(y)
    _actualizar_altura(x)
    return x


def _rotar_izquierda(x):
    y = x.der
    t2 = y.izq
    y.izq = x
    x.der = t2
    _actualizar_altura(x)
    _actualizar_altura(y)
    return y


def _rebalancear(nodo):
    _actualizar_altura(nodo)
    balance = _factor_balance(nodo)
    if balance > 1:
        if _factor_balance(nodo.izq) < 0:
            nodo.izq = _rotar_izquierda(nodo.izq)
        return _rotar_derecha(nodo)
    if balance < -1:
        if _factor_balance(nodo.der) > 0:
            nodo.der = _rotar_derecha(nodo.der)
        return _rotar_izquierda(nodo)
    return nodo


class ArbolAVL:
    """
    Árbol AVL que indexa claves (timestamp, id_msg). La condición de
    balanceo (|altura_izq - altura_der| <= 1 en todo nodo) garantiza una
    altura O(log n), de la que dependen los costes de insertar, eliminar
    y localizar los límites de un rango.
    """

    def __init__(self):
        self.raiz = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def insertar(self, clave, id_msg):
        self.raiz = self._insertar(self.raiz, clave, id_msg)
        self._tamano += 1

    def _insertar(self, nodo, clave, id_msg):
        if nodo is None:
            return _NodoAVL(clave, id_msg)
        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave, id_msg)
        else:
            nodo.der = self._insertar(nodo.der, clave, id_msg)
        return _rebalancear(nodo)

    def eliminar(self, clave):
        """Elimina la clave exacta si existe. Devuelve True/False."""
        self.raiz, encontrado = self._eliminar(self.raiz, clave)
        if encontrado:
            self._tamano -= 1
        return encontrado

    def _eliminar(self, nodo, clave):
        if nodo is None:
            return None, False
        if clave < nodo.clave:
            nodo.izq, encontrado = self._eliminar(nodo.izq, clave)
        elif clave > nodo.clave:
            nodo.der, encontrado = self._eliminar(nodo.der, clave)
        else:
            encontrado = True
            if nodo.izq is None:
                return nodo.der, True
            if nodo.der is None:
                return nodo.izq, True
            # Dos hijos: sustituir por el sucesor (mínimo del subárbol derecho)
            sucesor = nodo.der
            while sucesor.izq is not None:
                sucesor = sucesor.izq
            nodo.clave, nodo.id_msg = sucesor.clave, sucesor.id_msg
            nodo.der, _ = self._eliminar(nodo.der, sucesor.clave)
        return _rebalancear(nodo), encontrado

    def rango(self, clave_lo, clave_hi):
        """Devuelve [(clave, id_msg), ...] con clave_lo <= clave <= clave_hi,
        en orden cronológico. Poda las ramas que no pueden contener
        resultados en lugar de recorrer todo el árbol."""
        resultado = []
        self._rango(self.raiz, clave_lo, clave_hi, resultado)
        return resultado

    def _rango(self, nodo, lo, hi, resultado):
        if nodo is None:
            return
        if lo < nodo.clave:
            self._rango(nodo.izq, lo, hi, resultado)
        if lo <= nodo.clave <= hi:
            resultado.append((nodo.clave, nodo.id_msg))
        if nodo.clave < hi:
            self._rango(nodo.der, lo, hi, resultado)

    def en_orden(self):
        """Devuelve todos los pares (clave, id_msg) en orden cronológico."""
        resultado = []
        self._en_orden(self.raiz, resultado)
        return resultado

    def _en_orden(self, nodo, resultado):
        if nodo is None:
            return
        self._en_orden(nodo.izq, resultado)
        resultado.append((nodo.clave, nodo.id_msg))
        self._en_orden(nodo.der, resultado)


class SistemaMensajeria:
    """
    Almacena mensajes en dos estructuras complementarias:
      1. tabla_hash: dict {id_msg -> Mensaje}                  -> O(1) por ID
      2. indice_temporal: ArbolAVL sobre (timestamp, id_msg)   -> O(log n)
         por operación (insertar, eliminar, límites de un rango)
    """

    def __init__(self):
        self.tabla_hash = {}
        self.indice_temporal = ArbolAVL()

    def insertar(self, mensaje: Mensaje):
        if mensaje.id_msg in self.tabla_hash:
            raise ValueError(f"ID duplicado: {mensaje.id_msg}")
        self.tabla_hash[mensaje.id_msg] = mensaje
        self.indice_temporal.insertar((mensaje.timestamp, mensaje.id_msg), mensaje.id_msg)
        print(f"  [INSERT] {mensaje}")

    def buscar_por_id(self, id_msg):
        """Búsqueda O(1) por identificador (tabla hash)."""
        resultado = self.tabla_hash.get(id_msg)
        if resultado:
            print(f"  [SEARCH id={id_msg}] encontrado: {resultado}")
        else:
            print(f"  [SEARCH id={id_msg}] no encontrado")
        return resultado

    def mensajes_entre(self, t_inicio, t_fin):
        """Recupera mensajes en el rango [t_inicio, t_fin], en O(log n + k)
        con k = mensajes devueltos, mediante el árbol AVL."""
        lo = (t_inicio, "")
        hi = (t_fin, "\xff" * 100)
        pares = self.indice_temporal.rango(lo, hi)
        resultado = [self.tabla_hash[id_msg] for _, id_msg in pares]
        print(f"  [RANGE] {len(resultado)} mensaje(s) en el rango solicitado:")
        for m in resultado:
            print(f"    {m}")
        return resultado

    def eliminar(self, id_msg):
        """Elimina de ambas estructuras en O(log n)."""
        if id_msg not in self.tabla_hash:
            print(f"  [DELETE id={id_msg}] no existe")
            return False
        msg = self.tabla_hash.pop(id_msg)
        self.indice_temporal.eliminar((msg.timestamp, id_msg))
        print(f"  [DELETE] eliminado: {msg}")
        return True


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  PROTOTIPO: Sistema de mensajería con tabla hash + árbol AVL")
    print("=" * 60)

    sistema = SistemaMensajeria()
    t_base = time.time()

    print("\n1) Inserción de mensajes:")
    m1 = Mensaje("msg-001", "ana",    "bea", "Hola, ¿cómo estás?")
    m1.timestamp = t_base
    m2 = Mensaje("msg-002", "bea",    "ana", "Todo bien, ¿y tú?")
    m2.timestamp = t_base + 5
    m3 = Mensaje("msg-003", "carlos", "ana", "¿Quedamos el viernes?")
    m3.timestamp = t_base + 10
    m4 = Mensaje("msg-004", "ana",    "carlos", "Claro, a las 18h.")
    m4.timestamp = t_base + 15

    for m in [m1, m2, m3, m4]:
        sistema.insertar(m)

    print("\n2) Búsqueda por ID (O(1)):")
    sistema.buscar_por_id("msg-003")
    sistema.buscar_por_id("msg-999")

    print("\n3) Recuperación por rango temporal (O(log n + k)):")
    sistema.mensajes_entre(t_base + 4, t_base + 12)

    print("\n4) Eliminación (O(log n)):")
    sistema.eliminar("msg-002")
    sistema.eliminar("msg-002")   # intento de eliminar lo que ya no existe

    print("\n5) Estado final del índice temporal (recorrido en orden):")
    for (ts, id_msg), _ in sistema.indice_temporal.en_orden():
        print(f"    t+{ts - t_base:.0f}s -> {sistema.tabla_hash[id_msg]}")

    print("\n" + "=" * 60)
    print(f"  Mensajes almacenados: {len(sistema.tabla_hash)}")
    print("=" * 60)
