# Gestor de inventario y ventas — Tienda "La Esquina" (refactorizado)

Aplicación de consola en Python para administrar el inventario y las ventas de una tienda pequeña: alta de productos, ventas con descuentos por volumen, regla VIP e IVA,cotizaciones, reportes y persistencia en JSON.

Este repositorio es la entrega del **Reto M1 "Refactorización Asistida por IA"** del certificado *Next-Gen Coding* (Tec de Monterrey). El código original funcionaba pero tenía muchos *code smells*; se refactorizó con **Claude Code** sin cambiar el comportamiento observable.

| Indicador | Antes | Después |
|---|---|---|
| Tests (`pytest`) | 20/20 | 20/20 |
| Errores de linter (`ruff check src`) | 20 | **0** |
| Complejidad de `registrar_venta` | 12 | 3 |
| Complejidad de `menu` | 17 | ≤ 10 |

## Requisitos previos

- Python **3.10** o superior
- Git
- Dependencias (en `requirements.txt`): `pytest>=8.0`, `ruff>=0.6`

## Clonar e instalar

```bash
git clone https://github.com/ngc-ed/reto-refactorizacion.git
cd reto-refactorizacion
python -m venv .venv
```

Activar el entorno virtual:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar los tests

```bash
python -m pytest -q
```

Resultado esperado: `20 passed`.

## Ejecutar el linter

```bash
python -m ruff check src
```

Resultado esperado: `All checks passed!`

## Ejecutar la aplicación

Desde la **raíz** del proyecto (así encuentra `datos_ejemplo.json`):

```bash
python src/main.py
```

> ⚠️ La opción **8) Guardar y salir** sobrescribe `datos_ejemplo.json`. Para
> restaurarlo: `git restore datos_ejemplo.json`.

## Estructura del proyecto

```
.
├── CLAUDE.md               # Instrucciones y reglas para Claude Code
├── .claudeignore           # Archivos que Claude no debe leer
├── .claude/
│   ├── settings.json       # Permisos (deny/allow) y hooks
│   └── hooks/              # proteger_archivos.py (PreToolUse), verificar_cambio.py (PostToolUse)
├── PLAN.md                 # Diagnóstico, code smells y plan de refactorización R0–R7
├── src/
│   ├── gestor.py           # Productos, ventas, reglas de precio e IVA
│   ├── almacen.py          # Carga y guardado en JSON
│   ├── reportes.py         # Reportes e indicadores
│   └── main.py             # Menú de consola (despacho por opciones)
├── tests/                  # Suite original (sin modificar)
├── docs/
│   ├── bitacora.md         # Prompts, cambios, justificación y evidencia por paso
│   ├── reflexion.md        # Lecciones y reflexión final
│   └── evidencia/          # Logs de pytest/ruff, scripts y salidas de caracterización
├── datos_ejemplo.json
├── pyproject.toml          # Configuración de ruff y pytest (sin modificar)
└── requirements.txt
```

## Qué se refactorizó

| # | Refactorización | Archivo |
|---|---|---|
| R0 | Arreglos automáticos de ruff (preparación) | todos |
| R1 | Eliminar código muerto y variables sin uso | `gestor.py`, `reportes.py` |
| R2 | Persistencia segura: `with open`, excepciones específicas, `hay_archivo` | `almacen.py`, `main.py` |
| R3 | Claridad en reportes: `formatear_dinero`, `STOCK_MINIMO`, `sorted`, f-strings | `reportes.py` |
| R4 | Renombrar `contadorVentas` → `contador_ventas` (PEP 8) | `gestor.py`, `almacen.py` |
| R5 | Extraer reglas de precio: constantes de negocio, descuentos e IVA compartidos | `gestor.py` |
| R6 | Dividir `registrar_venta`: validación con guardas, cálculo y ticket | `gestor.py` |
| R7 | Menú por despacho: una función por opción y dict `OPCIONES` | `main.py` |

El detalle de cada paso (prompt, diff revisado, riesgos y evidencia) está en [`docs/bitacora.md`](docs/bitacora.md).

## Caracterización (red de seguridad)

La suite original no revisa mensajes, límites de precio, tickets ni el menú. Para esos casos se compararon salidas antes y después de cada cambio con:

```bash
python docs/evidencia/caracterizar_precios.py   # descuentos, VIP, IVA, tickets
python docs/evidencia/caracterizar_ventas.py    # validaciones, estado tras error, claves
python docs/evidencia/caracterizar_menu.py      # menú completo en carpeta temporal
```

## Reglas que se respetaron

- `tests/` (archivos originales) y `pyproject.toml` sin cambios.
- `agregarProducto` y `buscarProducto` conservan su nombre (API usada por los tests).
- Comportamiento observable idéntico (textos, mensajes, redondeos, JSON guardado).
