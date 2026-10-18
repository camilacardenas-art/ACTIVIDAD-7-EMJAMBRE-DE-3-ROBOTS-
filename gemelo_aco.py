import pybullet as p
import pybullet_data
import numpy as np
import time

# ==========================================
# 1. GRAFO Y PARÁMETROS ACO
# ==========================================
nodos_coords = {
    0: (-2.0, -2.0),
    1: (-0.5, -2.0),
    2: (-2.0,  0.0),
    3: ( 0.0,  0.0),
    4: ( 1.5,  0.0),
    5: (-0.5,  1.5),
    6: ( 2.0,  2.0)
}

NUM_NODOS = len(nodos_coords)
INICIO, META = 0, 6

distancias = np.zeros((NUM_NODOS, NUM_NODOS))
def conectar(n1, n2):
    d = np.linalg.norm(np.array(nodos_coords[n1]) - np.array(nodos_coords[n2]))
    distancias[n1][n2] = distancias[n2][n1] = d

conectar(0, 1); conectar(0, 2); conectar(1, 3); conectar(2, 5)
conectar(3, 4); conectar(3, 5); conectar(4, 6); conectar(5, 6)

ALPHA, BETA, EVAPORACION, Q = 1.0, 2.0, 0.4, 100.0
feromonas = np.ones((NUM_NODOS, NUM_NODOS)) * 0.1

def seleccionar_siguiente(actual, visitados):
    vecinos, probs = [], []
    for v in range(NUM_NODOS):
        if distancias[actual][v] > 0 and v not in visitados:
            vecinos.append(v)
            eta = 1.0 / distancias[actual][v]
            tau = feromonas[actual][v]
            probs.append((tau ** ALPHA) * (eta ** BETA))
    if not vecinos: return None
    probs = np.array(probs)
    s = np.sum(probs)
    probs = probs / s if s > 0 else np.ones(len(vecinos)) / len(vecinos)
    return np.random.choice(vecinos, p=probs)

def simular_hormiga():
    actual = INICIO
    camino, visitados = [actual], set([actual])
    while actual != META:
        sig = seleccionar_siguiente(actual, visitados)
        if sig is None: return None
        camino.append(sig)
        visitados.add(sig)
        actual = sig
    return camino

# ==========================================
# 2. ENTORNO 3D PYBULLET
# ==========================================
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.loadURDF("plane.urdf")

p.resetDebugVisualizerCamera(cameraDistance=7.5, cameraYaw=0, cameraPitch=-89, cameraTargetPosition=[0, 0, 0])

def crear_bloque(pos, size, color=[0.3, 0.3, 0.3, 1]):
    v = p.createVisualShape(p.GEOM_BOX, halfExtents=size, rgbaColor=color)
    c = p.createCollisionShape(p.GEOM_BOX, halfExtents=size)
    return p.createMultiBody(0, c, v, pos)

# Paredes del laberinto
crear_bloque([0, 3, 0.25], [3, 0.1, 0.25])
crear_bloque([0, -3, 0.25], [3, 0.1, 0.25])
crear_bloque([3, 0, 0.25], [0.1, 3, 0.25])
crear_bloque([-3, 0, 0.25], [0.1, 3, 0.25])
crear_bloque([-1.0, 1.0, 0.25], [1.0, 0.1, 0.25])
crear_bloque([0.5, 0.0, 0.25], [0.1, 1.5, 0.25])
crear_bloque([-0.5, -1.5, 0.25], [1.0, 0.1, 0.25])
crear_bloque([1.5, -1.0, 0.25], [0.8, 0.1, 0.25])

# Marcadores
crear_bloque([2.0, 2.0, 0.01], [0.5, 0.5, 0.01], color=[0, 1, 0, 0.5])   # Meta
crear_bloque([-2.0, -2.0, 0.01], [0.5, 0.5, 0.01], color=[0, 0, 1, 0.5]) # Inicio

def crear_carrito(color):
    v = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.12, 0.1, 0.08], rgbaColor=color)
    c = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.12, 0.1, 0.08])
    return p.createMultiBody(1.0, c, v, [-2.0, -2.0, 0.1])

robots = [
    {"id": crear_carrito([1, 0, 0, 1]), "color": [1, 0, 0]},       # Robot 1: Rojo
    {"id": crear_carrito([1, 0.5, 0, 1]), "color": [1, 0.5, 0]},   # Robot 2: Naranja
    {"id": crear_carrito([0, 0.8, 1, 1]), "color": [0, 0.8, 1]}    # Robot 3: Azul
]

lineas_dibujadas = []

def actualizar_visualizacion_feromonas():
    global lineas_dibujadas
    for line_id in lineas_dibujadas:
        p.removeUserDebugItem(line_id)
    lineas_dibujadas.clear()
    
    max_f = np.max(feromonas) if np.max(feromonas) > 0 else 1.0
    for u in range(NUM_NODOS):
        for v in range(u + 1, NUM_NODOS):
            if distancias[u][v] > 0:
                f_val = feromonas[u][v]
                intensidad = min(1.0, f_val / max_f)
                color = [intensidad, 0, 1.0 - intensidad]
                p1 = [nodos_coords[u][0], nodos_coords[u][1], 0.05]
                p2 = [nodos_coords[v][0], nodos_coords[v][1], 0.05]
                l_id = p.addUserDebugLine(p1, p2, lineColorRGB=color, lineWidth=1 + intensidad*5)
                lineas_dibujadas.append(l_id)

def mover_robot_suave(robot_id, p_inicio, p_fin, pasos=20):
    for t in np.linspace(0, 1, pasos):
        x = p_inicio[0] + t * (p_fin[0] - p_inicio[0])
        y = p_inicio[1] + t * (p_fin[1] - p_inicio[1])
        p.resetBasePositionAndOrientation(robot_id, [x, y, 0.1], [0, 0, 0, 1])
        p.stepSimulation()
        time.sleep(0.015)

# ==========================================
# 3. BUCLE PRINCIPAL DE ANIMACIÓN ACO
# ==========================================
print("\n" + "="*50)
print(" GEMELO DIGITAL ACO ANIMADO EN PYBULLET ")
print(" Se simularán 5 iteraciones del enjambre.")
print("="*50 + "\n")

for iteracion in range(1, 6):
    print(f"--- Iteración ACO #{iteracion} ---")
    caminos = []
    for r in range(3):
        c = simular_hormiga()
        if c: caminos.append(c)
        
    # Animar desplazamiento simultáneo/secuencial de los robots
    max_pasos = max(len(c) for c in caminos) if caminos else 0
    for paso in range(max_pasos - 1):
        for idx, camino in enumerate(caminos):
            if paso < len(camino) - 1:
                n_origen = camino[paso]
                n_destino = camino[paso+1]
                pos_a = nodos_coords[n_origen]
                pos_b = nodos_coords[n_destino]
                mover_robot_suave(robots[idx]["id"], pos_a, pos_b)

    # Actualizar feromonas
    global feromonas
    feromonas *= (1.0 - EVAPORACION)
    for c in caminos:
        dist = sum(distancias[c[i]][c[i+1]] for i in range(len(c)-1))
        dep = Q / dist
        for i in range(len(c)-1):
            feromonas[c[i]][c[i+1]] += dep
            feromonas[c[i+1]][c[i]] += dep
            
    actualizar_visualizacion_feromonas()
    time.sleep(1.0)

print("\n[OK] Simulación completada. Los robots han convergido en el mapa 3D.")
while True:
    p.stepSimulation()
    time.sleep(0.1)