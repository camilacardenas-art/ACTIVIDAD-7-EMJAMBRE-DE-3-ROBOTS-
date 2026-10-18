import pybullet as p
import pybullet_data
import time
import math

# ==========================================
# 1. INICIALIZACIÓN Y CONFIGURACIÓN FÍSICA
# ==========================================
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# Cargar el plano base
planeId = p.loadURDF("plane.urdf")

# Configuración de la cámara para vista superior del laberinto
p.resetDebugVisualizerCamera(
    cameraDistance=7.5,
    cameraYaw=0,
    cameraPitch=-89,
    cameraTargetPosition=[0, 0, 0]
)

# ==========================================
# 2. CONSTRUCCIÓN DEL LABERINTO / ALMACÉN
# ==========================================
def crear_bloque(pos, size, color=[0.3, 0.3, 0.3, 1]):
    """Crea una pared u obstáculo en la simulación."""
    visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=size, rgbaColor=color)
    collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=size)
    body = p.createMultiBody(
        baseMass=0,  # Masa 0 = Objeto estático
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=visual_shape,
        basePosition=pos
    )
    return body

def construir_escenario():
    print("[ESCENARIO] Construyendo laberinto y meta...")
    
    # Paredes exteriores del laberinto (Ancho: 6m x 6m)
    crear_bloque([0, 3, 0.25], [3, 0.1, 0.25])   # Pared Norte
    crear_bloque([0, -3, 0.25], [3, 0.1, 0.25])  # Pared Sur
    crear_bloque([3, 0, 0.25], [0.1, 3, 0.25])   # Pared Este
    crear_bloque([-3, 0, 0.25], [0.1, 3, 0.25])  # Pared Oeste

    # Pasillos interiores (Obstáculos del laberinto)
    crear_bloque([-1.0, 1.0, 0.25], [1.0, 0.1, 0.25])
    crear_bloque([0.5, 0.0, 0.25], [0.1, 1.5, 0.25])
    crear_bloque([-0.5, -1.5, 0.25], [1.0, 0.1, 0.25])
    crear_bloque([1.5, -1.0, 0.25], [0.8, 0.1, 0.25])

    # Área de Meta (Plataforma Verde)
    crear_bloque([2.0, 2.0, 0.01], [0.5, 0.5, 0.01], color=[0, 1, 0, 0.6])
    
    # Marcar el punto A (Inicio) con una zona azul
    crear_bloque([-2.0, -2.0, 0.01], [0.5, 0.5, 0.01], color=[0, 0, 1, 0.4])

# ==========================================
# 3. SPANNING DE LOS 3 CARRITOS (ENJAMBRE)
# ==========================================
def crear_carrito(pos, color):
    """Crea un vehículo sencillo simulando los nodos del enjambre."""
    visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.15, 0.1, 0.08], rgbaColor=color)
    collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.15, 0.1, 0.08])
    carrito_id = p.createMultiBody(
        baseMass=1.0,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=visual_shape,
        basePosition=pos
    )
    return carrito_id

# Construir mapa
construir_escenario()

# Posiciones iniciales en el Punto A (con ligeros desfaces para que no se traslapen)
carritos = {
    "robot_1": {
        "id": crear_carrito([-2.2, -2.2, 0.1], [1, 0, 0, 1]), # Rojo
        "pos_actual": [-2.2, -2.2, 0.1]
    },
    "robot_2": {
        "id": crear_carrito([-2.0, -2.0, 0.1], [1, 0.5, 0, 1]), # Naranja
        "pos_actual": [-2.0, -2.0, 0.1]
    },
    "robot_3": {
        "id": crear_carrito([-1.8, -1.8, 0.1], [0, 0.8, 1, 1]), # Azul claro
        "pos_actual": [-1.8, -1.8, 0.1]
    }
}

# ==========================================
# 4. FUNCIONES DE ACTUALIZACIÓN DE POSICIÓN
# ==========================================
def mover_robot(nombre_robot, nueva_pos_2d):
    """Actualiza la posición del robot virtual en el gemelo digital."""
    if nombre_robot in carritos:
        robot_id = carritos[nombre_robot]["id"]
        x, y = nueva_pos_2d
        p.resetBasePositionAndOrientation(
            robot_id, 
            [x, y, 0.1], 
            p.getQuaternionFromEuler([0, 0, 0])
        )
        carritos[nombre_robot]["pos_actual"] = [x, y, 0.1]

# ==========================================
# 5. BUCLE DE SIMULACIÓN Y PRUEBA
# ==========================================
print("\n" + "="*50)
print(" GEMELO DIGITAL DE ENJAMBRE LISTO EN PYBULLET ")
print(" - Marcador Azul: Punto A (Inicio)")
print(" - Marcador Verde: Meta (Punto B)")
print(" - Carritos: Rojo (ESP1), Naranja (ESP2), Azul (ESP3)")
print("="*50 + "\n")

try:
    # Ejemplo de prueba de movimiento autónomo por coordenadas
    paso = 0
    while True:
        p.stepSimulation()
        time.sleep(1. / 60.)
        
        # Prueba visual: Simulación de avance hacia la meta
        paso += 0.01
        if paso < 3.0:
            # El robot 1 avanza por una ruta
            mover_robot("robot_1", [-2.2 + paso*1.2, -2.2 + paso*0.5])
            # El robot 2 explora otra ruta
            mover_robot("robot_2", [-2.0 + paso*0.3, -2.0 + paso*1.2])
            # El robot 3 explora por el centro
            mover_robot("robot_3", [-1.8 + paso*0.8, -1.8 + paso*0.8])

except KeyboardInterrupt:
    p.disconnect()