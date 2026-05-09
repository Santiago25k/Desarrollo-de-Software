# WATCHMAN BOT DE PESCA IA — Albion Online

## Que es este proyecto

Bot de pesca automatizado para Albion Online con IA integrada (v3.0).
Automatiza el ciclo completo: montar, navegar al spot, pescar, combatir si es atacado, desmontar.

## Arquitectura

Ver `arquitectura.txt` para el diagrama completo de estados y modulos.

### Modulos principales (`src/`)

| Modulo | Descripcion | Fase |
|---|---|---|
| `state_machine.py` | Maquina de estados central | 1 |
| `config.py` | Configuracion global (teclas, resoluciones, umbrales) | 1 |
| `fishing/` | Bot de pesca refactorizado desde v2.1 | 1 |
| `mount/controller.py` | Montar y desmontar | 1 |
| `perception/hp_reader.py` | Lector de barra de HP por color | 1 |
| `navigation/` | Waypoints y click-to-move | 2 |
| `perception/yolo_detector.py` | Deteccion YOLO de mobs/jugadores/spots | 3 |
| `combat/handler.py` | Combate completo con logica de huida | 4 |

### Estados de la maquina

```
DETENIDO → INICIO → MONTANDO → NAVEGANDO → DESMONTANDO → PESCANDO
                                                              ↓
                                            MUERTO ← HUYENDO ← COMBATE
```

## Setup

```bash
pip install -r requirements.txt
```

### Imagenes requeridas

Copiar desde `../bot-pesca-albion-2.1/bot/img/` a `img/`:
- `cebo.PNG`, `ceboausar.PNG`, `ceboclose.PNG`
- `alga.PNG`, `comida.PNG`

### Ejecutar

```bash
python interfaz.py
```

## Configuracion

Editar `src/config.py`:
- `TECLA_MONTURA` — tecla para montar/desmontar (default: `'5'`)
- `TECLA_AUTO_TARGET` — tecla para seleccionar enemigo mas cercano (default: `'tab'`)
- `SCREEN_WIDTH / SCREEN_HEIGHT` — resolucion (default: 1920x1080)
- `REGION_HP` — region de la barra de HP **(requiere calibracion manual)**
- `UMBRAL_HP_BAJO` — porcentaje de HP para activar huida (default: 0.30)

## Fases de desarrollo

- **Fase 1** (actual): Estructura limpia + State Machine + Mount Controller + HP reader basico
- **Fase 2**: Waypoints + navegacion click-to-move entre spots
- **Fase 3**: Modelo YOLO (mobs, jugadores, fishing spots)
- **Fase 4**: Combate completo con logica de targeting y huida
- **Fase 5**: Integracion total y pruebas

## Reglas para Claude

- No implementar logica de fases futuras, solo la fase actual
- Leer el archivo completo antes de modificarlo
- NUNCA hacer git commit/push sin autorizacion explicita del usuario
- Los tests se hacen con el juego corriendo en Albion Online
- Configurar siempre a traves de `src/config.py`, no hardcodear valores
