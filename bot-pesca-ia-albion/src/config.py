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
