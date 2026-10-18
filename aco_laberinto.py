import numpy as np
import random

# ==========================================
# 1. MAPA DE NODOS Y CONEXIONES (GRAFO)
# ==========================================
# Coordenadas (x, y) en el espacio de PyBullet
nodos_coords = {
    0: (-2.0, -2.0), # Inicio (Punto A)
    1: (-0.5, -2.0), # Pasillo inferior
    2: (-2.0,  0.0), # Pasillo centro-oeste
    3: ( 0.0,  0.0), # Intersección central
    4: ( 1.5,  0.0), # Pasillo centro-este
    5: (-0.5,  1.5), # Pasillo superior
    6: ( 2.0,  2.0)  # Meta (Punto B)
}

NUM_NODOS = len(nodos_coords)
INICIO = 0
META = 6

# Matriz de Distancias (0 significa sin conexión directa)
# Calculamos distancias entre nodos adyacentes permitidos por el laberinto
distancias = np.zeros((NUM_NODOS, NUM_NODOS))

def conectar_nodos(n1, n2):
    p1 = np.array(nodos_coords[n1])
    p2 = np.array(nodos_coords[n2])
    dist = np.linalg.norm(p1 - p2)
    distancias[n1][n2] = dist
    distancias[n2][n1] = dist

# Definición de pasillos transitables (evitando paredes)
conectar_nodos(0, 1) # Inicio -> Pasillo Inferior
conectar_nodos(0, 2) # Inicio -> Pasillo Oeste
conectar_nodos(1, 3) # Pasillo Inferior -> Centro
conectar_nodos(2, 5) # Pasillo Oeste -> Pasillo Superior
conectar_nodos(3, 4) # Centro -> Pasillo Este
conectar_nodos(3, 5) # Centro -> Pasillo Superior
conectar_nodos(4, 6) # Pasillo Este -> Meta
conectar_nodos(5, 6) # Pasillo Superior -> Meta

# ==========================================
# 2. PARÁMETROS DEL ALGORITMO ACO
# ==========================================
ALPHA = 1.0     # Importancia de la feromona
BETA = 2.0      # Importancia de la distancia (visibilidad)
EVAPORACION = 0.5 # Tasa de evaporación
Q = 100.0       # Cantidad de feromona a depositar

# Inicialización de la matriz de feromonas (valor base pequeño)
feromonas = np.ones((NUM_NODOS, NUM_NODOS)) * 0.1

# ==========================================
# 3. LÓGICA DE DECISIÓN DE LA HORMIGA
# ==========================================
def seleccionar_siguiente_nodo(nodo_actual, visitados):
    vecinos = []
    probabilidades = []
    
    for vecino in range(NUM_NODOS):
        if distancias[nodo_actual][vecino] > 0 and vecino not in visitados:
            vecinos.append(vecino)
            
            # Heurística: Inversa de la distancia
            eta = 1.0 / distancias[nodo_actual][vecino]
            tau = feromonas[nodo_actual][vecino]
            
            # Fórmula probabilística del ACO
            prob = (tau ** ALPHA) * (eta ** BETA)
            probabilidades.append(prob)
            
    if not vecinos:
        return None # Sin salida o atrapado
        
    probabilidades = np.array(probabilidades)
    suma_prob = np.sum(probabilidades)
    
    if suma_prob == 0:
        probabilidades = np.ones(len(vecinos)) / len(vecinos)
    else:
        probabilidades /= suma_prob
        
    return np.random.choice(vecinos, p=probabilidades)

def simular_hormiga():
    nodo_actual = INICIO
    camino = [nodo_actual]
    visitados = set([nodo_actual])
    
    while nodo_actual != META:
        siguiente = seleccionar_siguiente_nodo(nodo_actual, visitados)
        if siguiente is None:
            return None # La hormiga llegó a un callejón sin salida
        camino.append(siguiente)
        visitados.add(siguiente)
        nodo_actual = siguiente
        
    return camino

def calcular_distancia_camino(camino):
    dist_total = 0.0
    for i in range(len(camino) - 1):
        dist_total += distancias[camino[i]][camino[i+1]]
    return dist_total

# ==========================================
# 4. EJECUCIÓN DEL ENJAMBRE (3 HORMIGAS)
# ==========================================
print("=== SIMULACIÓN LOCAL DEL ALGORITMO DE HORMIGAS (ACO) ===")

num_iteraciones = 10

for iteracion in range(1, num_iteraciones + 1):
    caminos_enjambre = []
    
    # 3 Robots / Nodos simulando en paralelo
    for robot_id in range(1, 4):
        camino = simular_hormiga()
        if camino:
            caminos_enjambre.append(camino)
            
    # Evaporación general de feromonas
    feromonas *= (1.0 - EVAPORACION)
    
    # Depósito de feromonas por los caminos completados
    for camino in caminos_enjambre:
        distancia = calcular_distancia_camino(camino)
        deposito = Q / distancia
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i+1]
            feromonas[u][v] += deposito
            feromonas[v][u] += deposito
            
    print(f"Iteración {iteracion}: Trazados de los 3 robots -> {caminos_enjambre}")

print("\n--- MATRIZ DE FEROMONAS FINAL ---")
print(np.round(feromonas, 2))