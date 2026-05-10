# Configuracion global del bot. Editar aqui antes de ejecutar.

# ── Pantalla ─────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080

# ── Teclas ───────────────────────────────────────────────────────────────────
TECLA_MONTURA      = 'a'
TECLA_COMIDA       = '2'
TECLA_AUTO_TARGET  = 'tab'
TECLAS_HABILIDADES = ['q', 'w', 'e' , 'r']

# ── Regiones de deteccion (pixeles absolutos en pantalla) ────────────────────
REGION_PIQUE = {
    'left': 100, 'top': 350, 'width': 400, 'height': 300,
}

REGION_PUZZLE = {
    'left':   (SCREEN_WIDTH  - 400) // 2,
    'top':    (SCREEN_HEIGHT - 200) // 2 + 50,
    'width':  400,
    'height': 200,
}

# ATENCION: calibrar segun tu resolucion y UI de Albion Online
REGION_HP = {
    'left': 780, 'top': 985, 'width': 360, 'height': 14,
}

# ── Colores HSV (como tuplas; los modulos los convierten a np.array) ─────────
BOBBER_ROJO_1_LOW  = (0,   100, 80)
BOBBER_ROJO_1_HIGH = (10,  255, 255)
BOBBER_ROJO_2_LOW  = (170, 100, 80)
BOBBER_ROJO_2_HIGH = (179, 255, 255)
PUZZLE_NARANJA_LOW  = (15, 180, 200)
PUZZLE_NARANJA_HIGH = (25, 255, 255)

# ── Umbrales de deteccion ────────────────────────────────────────────────────
UMBRAL_HP_BAJO       = 0.30   # huir si HP cae por debajo de este porcentaje
UMBRAL_BAJADA_BOBBER = 4      # pixeles de bajada para detectar picada
FRAMES_SIN_BOBBER    = 5      # frames sin bobber antes de click de seguridad
AREA_MIN_BOBBER      = 50     # area minima del contorno del bobber rojo
AREA_MIN_PUZZLE      = 78     # area minima del contorno del bobber naranja
PUZZLE_ZONA_IZQ      = 25     # limite izquierdo de la zona segura del puzzle
PUZZLE_ZONA_DER      = 215    # limite derecho de la zona segura del puzzle

# ── Spot de pesca (calibrar segun posicion del personaje en pantalla) ────────
SPOT_X = 300
SPOT_Y = 450

# ── Minimapa (calibrar segun resolucion y escala de UI de Albion Online) ─────
# Region del minimapa en pantalla (esquina superior derecha)
REGION_MINIMAP = {
    'left': 11, 'top': 730, 'width': 487, 'height': 331,
}
# Color HSV de la flecha del jugador en el minimapa — cyan/celeste de Albion Online
MINIMAP_JUGADOR_LOW  = (85,  100, 150)
MINIMAP_JUGADOR_HIGH = (105, 255, 255)
# Color HSV del agua en el minimapa
MINIMAP_AGUA_LOW  = (59, 0, 90)
MINIMAP_AGUA_HIGH = (83, 90, 190)
# Tolerancia en pixeles de minimapa para dar un waypoint por alcanzado
WAYPOINT_RADIO   = 10
# Segundos maximos esperando llegar a un waypoint antes de continuar
WAYPOINT_TIMEOUT = 30
# Nombre del archivo JSON de ruta a cargar desde waypoints/
RUTA_DEFAULT = "ruta_default"
# Distancia en pixeles desde el centro de pantalla al hacer click en el mundo 3D
NAV_CLICK_DISTANCIA = 200
# Segundos manteniendo el boton izquierdo presionado por cada paso
NAV_DURACION_HOLD = 0.6
# Pixeles alrededor del centro del minimapa para detectar llegada al agua
NAV_AGUA_RADIO = 10
# Clicks consecutivos sin cambio de direccion antes de intentar rodear obstaculo
NAV_STUCK_INTENTOS = 5

# ── Deteccion de spots de pesca ──────────────────────────────────────────────
# Region del mundo 3D (excluye UI, minimapa y barras)
REGION_MUNDO = {
    'left': 1270, 'top': 272, 'width': 178, 'height': 100,
}
# Color HSV del agua en la vista 3D — calibrar con calibrar_spot.py --agua3d
SPOT_AGUA3D_LOW  = (98, 62, 0)
SPOT_AGUA3D_HIGH = (124, 201, 139)
# Fraccion minima de pixeles de agua dentro del circulo para aceptarlo como spot
SPOT_AGUA3D_MIN_FRAC = 0.25
# Segundos entre los dos frames para detectar movimiento de olas
SPOT_FRAMES_INTERVALO = 0.25
# Si mas de esta fraccion de pixeles cambia = camara en movimiento = saltar deteccion
SPOT_MAX_MOVIMIENTO_GLOBAL = 0.10
# Umbral de diferencia de pixel para considerar movimiento (0-255)
SPOT_MOVIMIENTO_UMBRAL = 18
# Rango de radio de circulo para spots (pixeles en pantalla)
SPOT_RADIO_MIN = 20
SPOT_RADIO_MAX = 120
# Confianza minima para template matching (0-1)
SPOT_TEMPLATE_UMBRAL = 0.60
# Circularidad minima (0=cualquier forma, 1=circulo perfecto)
SPOT_CIRCULARIDAD_MIN = 0.35
# Colores HSV de los peces dentro del spot (calibrar con calibrar_spot.py --colores)
SPOT_PEZ_AZUL_LOW    = (0, 0, 0)
SPOT_PEZ_AZUL_HIGH   = (12, 50, 87)
SPOT_PEZ_NARANJA_LOW  = (8,  150, 150)
SPOT_PEZ_NARANJA_HIGH = (25, 255, 255)
# Minimo de pixeles de color pez para confirmar que el circulo es un spot real
SPOT_PEZ_PIXELS_MIN = 8

# ── Fishing ──────────────────────────────────────────────────────────────────
TIEMPO_COMIDA       = 1800   # segundos entre usos de comida (30 min)
TIEMPO_ESPERA_EQUIP = 11     # segundos tras equipar comida antes de usarla
CEBO_CADA_N_PECES   = 10     # reaplicar cebo cada N peces
TIEMPO_LANZO        = 2.7    # segundos con mouseDown al lanzar la linea
TIMEOUT_SIN_PICADA  = 180    # segundos sin picada antes de cambiar spot (Fase 2)

# ── Montura ──────────────────────────────────────────────────────────────────
TIEMPO_MONTAR   = 3.5   # segundos de cast de montura
TIEMPO_DESMONTAR = 1.5

# ── Combate ──────────────────────────────────────────────────────────────────
DELAY_HABILIDAD     = 0.5   # segundos entre habilidades 1 → 2 → 3
CICLOS_COMBATE_MAX  = 20    # ciclos maximos de habilidades antes de huir
TIEMPO_HUIDA        = 5.0   # segundos corriendo antes de verificar seguridad
