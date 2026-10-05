"""
Gestión de procesos en un sistema operativo — Caso 03
Simula un planificador que combina dos estructuras:
  1. Cola de prioridad (montículo binario vía heapq) para los procesos
     listos para ejecutarse: la prioridad más urgente siempre queda en
     cabeza, con coste logarítmico tanto al encolar como al extraer.
  2. Pila (lista de Python usada como LIFO) para los procesos bloqueados
     o en espera: el último proceso que se suspendió es el primero que
     se reanuda, lo que encaja con bloqueos anidados (una interrupción
     dentro de otra interrupción).
"""
import heapq
import itertools


class GestorProcesos:
    """
    Planificador de procesos con dos estructuras complementarias:
      - _heap: montículo binario (heapq) de tuplas (prioridad, orden, nombre).
        La prioridad menor indica mayor urgencia (0 = interrupción crítica).
        'orden' es un contador estrictamente creciente que desempata
        procesos con la misma prioridad por orden de llegada, evitando
        además comparar los nombres (strings) cuando la prioridad coincide.
      - _pila_bloqueados: lista usada como pila (LIFO) para los procesos
        que están en espera y aún no pueden volver a la cola de listos.
    """

    def __init__(self):
        self._heap = []
        self._contador = itertools.count()
        self._pila_bloqueados = []

    def encolar(self, nombre, prioridad):
        # prioridad menor = mayor urgencia (0 = interrupcion critica)
        orden = next(self._contador)
        heapq.heappush(self._heap, (prioridad, orden, nombre))
        print(f"[COLA] Se encola '{nombre}' con prioridad {prioridad}")

    def ejecutar_siguiente(self):
        if not self._heap:
            print("[COLA] No hay procesos pendientes")
            return None
        prioridad, orden, nombre = heapq.heappop(self._heap)
        print(f"[EJECUCION] Se ejecuta '{nombre}' (prioridad {prioridad})")
        return nombre

    def bloquear(self, nombre):
        self._pila_bloqueados.append(nombre)
        print(f"[PILA] Se bloquea '{nombre}' y se apila en espera")

    def reanudar_ultimo_bloqueado(self):
        if not self._pila_bloqueados:
            print("[PILA] No hay procesos bloqueados")
            return None
        nombre = self._pila_bloqueados.pop()
        print(f"[PILA] Se reanuda '{nombre}' desde la pila de bloqueados")
        self.encolar(nombre, prioridad=1)
        return nombre


if __name__ == "__main__":
    gestor = GestorProcesos()
    gestor.encolar("actualizacion_interfaz", prioridad=5)
    gestor.encolar("interrupcion_reloj", prioridad=0)
    gestor.encolar("lectura_sensor", prioridad=2)
    gestor.encolar("guardado_registro", prioridad=4)
    gestor.ejecutar_siguiente()
    gestor.ejecutar_siguiente()
    gestor.bloquear("lectura_sensor")
    gestor.encolar("interrupcion_watchdog", prioridad=0)
    gestor.ejecutar_siguiente()
    gestor.reanudar_ultimo_bloqueado()
    gestor.ejecutar_siguiente()
    gestor.ejecutar_siguiente()
