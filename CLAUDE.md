# CLAUDE.md

## Contexto

Reto de **refactorización asistida por IA**: una app de consola en Python 3.10+ (inventario y ventas de la tienda "La Esquina") que funciona, pero está llena de *code smells* a propósito. El objetivo es mejorar la calidad **sin cambiar el comportamiento observable**. Se trabaja en la rama `refactorizacion` y se entrega por PR hacia `main`, con commits atómicos (idealmente uno por refactorización).

## Reglas obligatorias

- **No modificar nada en `tests/` ni `pyproject.toml`.** Si un test falla, el error está en el cambio a `src/`, nunca en el test ni en la configuración de ruff.
- Después de **cada** refactorización: `pytest` siempre 20/20 en verde y el número de errores de `ruff check src` **nunca aumenta** (línea base: 20). Al final del PR, ruff debe quedar en 0.
- `agregarProducto` y `buscarProducto` conservan su nombre (los usan los tests; están en `ignore-names` de ruff). El resto de la API usada por los tests también debe mantener nombre, firma, valores de retorno (`False`/`None` en fallo) y mensajes de `gestor.ultimo_error`: `gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.reiniciar_sistema`, `gestor.actualizar_stock`, `gestor.eliminar_producto`, `gestor.registrar_venta`, `gestor.cotizar`, `almacen.guardar_datos`, `almacen.cargar_datos`, `reportes.mas_vendidos`, `reportes.productos_stock_bajo`, `reportes.reporte_inventario`, `reportes.total_vendido`.
- `almacen.hayArchivo` no la usan los tests pero sí `main.py`: si se renombra, actualizar `main.py` en el mismo commit.
- Una refactorización a la vez; los cambios cosméticos aislados no cuentan como refactorización significativa.

## Comandos

Usar siempre el Python del entorno virtual (la sesión no activa `.venv`; el `python` global es otro). Correr los dos primeros después de CADA cambio, en este orden:

- `.venv/Scripts/python -m pytest -q` → todos en verde (línea base: 20)
- `.venv/Scripts/python -m ruff check src` → línea base: 20 errores; meta: 0
- `.venv/Scripts/python -m ruff check src --diff` y luego `--fix` solo para lo trivial (UP009, UP015, I001, F401). Esos arreglos van juntos en un commit aparte (`style(...)`), que no cuenta como refactorización.
- **No ejecutar `ruff format`** sobre archivos completos: rompe los commits atómicos.
- App (desde la raíz, donde está `datos_ejemplo.json`): `.venv/Scripts/python src/main.py`. La opción 8 sobrescribe `datos_ejemplo.json`, que está versionado: no commitear ese cambio; pedir al usuario que lo restaure con `git restore datos_ejemplo.json`.

### Caracterización (comportamiento no cubierto por tests)

Los tests no cubren `main.py`, el texto del ticket ni `resumen_ventas`. Si una refactorización los toca, comparar la salida antes y después del cambio (no usa la opción 8, así que no modifica archivos):

```bash
printf '4\n2\nA001\n6\nVIP01\n2\nA002\n16\n\n2\nA003\n9\n\n3\nB001\n12\n5\n6\n7\n4\n' \
  | PYTHONIOENCODING=utf-8 .venv/Scripts/python src/main.py 2>/dev/null > "$TMP/caract_antes.txt"
# ...aplicar el cambio y repetir con > "$TMP/caract_despues.txt"
diff "$TMP/caract_antes.txt" "$TMP/caract_despues.txt"   # debe salir vacío
```

La secuencia cubre: inventario, venta con descuento del 10 % + VIP, venta con 5 %, error de stock insuficiente, cotización, resumen, más vendidos y stock bajo.

## Arquitectura

Módulos planos en `src/` que se importan entre sí sin paquete (`import gestor`); `tests/conftest.py` agrega `src/` a `sys.path` y llama a `gestor.reiniciar_sistema()` antes y después de cada test.

- **`gestor.py`** — lógica de negocio y **estado global del sistema**: `INVENTARIO` (dict `codigo -> {codigo, nombre, precio, stock}`), `VENTAS` (lista de dicts de venta), `contador_ventas` (último folio) y `ultimo_error`. Las funciones señalan fallo devolviendo `False`/`None` y dejando el motivo en `gestor.ultimo_error`, que `main.py` imprime.
- **`almacen.py`** — persistencia JSON. Lee y escribe directamente el estado de `gestor` (`gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.contador_ventas`). Las claves del JSON (`inventario`, `ventas`, `contador`) deben mantenerse para seguir leyendo `datos_ejemplo.json`.
- **`reportes.py`** — reportes calculados sobre el estado de `gestor`; `reporte_inventario` y `resumen_ventas` imprimen **y** devuelven el texto.
- **`main.py`** — menú de consola (toda la E/S con el usuario).

### Puntos delicados al refactorizar

- `INVENTARIO` y `VENTAS` se mutan en sitio (`.clear()`, asignación de claves) y otros módulos los leen como `gestor.INVENTARIO`. Si se renombra `contador_ventas` o se cambia cómo se guarda el estado, actualizar también `almacen.py` y `reiniciar_sistema`.
- Reglas de precio en `registrar_venta`: subtotal ≥ 1000 → 10 % de descuento; ≥ 500 → 5 %; cliente que empieza con `"VIP"` suma 2 % extra del subtotal **solo si** `subtotal - descuento > 200`; IVA 16 % sobre la base; redondeos a 2 decimales en cada campo de la venta.
- `cotizar` duplica el cálculo de descuento/IVA pero **no** aplica el descuento VIP (no recibe cliente). Al extraer la lógica común hay que conservar esa diferencia y que `cotizar(...) == registrar_venta(...)["total"]` sin cliente.
- `registrar_venta` debe validar todo antes de tocar el stock o el folio (un fallo no altera estado). El orden de las validaciones determina el mensaje en `ultimo_error`.
- El texto del ticket y de los reportes es comportamiento observable: mantener formato exacto (p. ej. la línea `Descuento` solo aparece si hay descuento, la marca `<-- STOCK BAJO` con stock < 5).
- Código muerto conocido (sin llamadas): `calcular_descuento_viejo`, el bloque comentado `exportar_txt` en `gestor.py`, y `reporteViejoCSV` en `reportes.py`. Se puede eliminar, en un commit propio (`refactor(<módulo>): elimina código muerto ...`).

## Convenciones de Python
- snake_case en funciones y variables, constantes de negocio en MAYÚSCULAS.
- Type hints con sintaxis 3.10: `float | None`, `list[dict]` (no `Optional`/`List`).
- Docstrings de una línea, en español.
- Archivos siempre con `with open(..., encoding="utf-8")`.
- Límites de ruff: líneas ≤ 88 caracteres, complejidad ≤ 10.

## Ramas y commits
- Solo se trabaja en `refactorizacion`, la entrega es en un PR de `refactorizacion` a `main`.
- Convención de commits: `tipo(alcance): descripción`, en español, con la primera línea de menos de 100 caracteres.
  - Tipos: `feat`, `fix`, `refactor`, `style`, `test`, `docs`, `chore`.
  - Alcances: `gestor`, `almacen`, `reportes`, `main`, `claude`.
```text
Correcto:
 refactor(gestor): extrae el cálculo de descuentos a una función
 docs(claude): agrega regla sobre el orden de validaciones
Incorrecto:
 Refactoricé varias cosas del gestor
 refactor: cambios
```
- Un commit por refactorización. Propón el mensaje; los commits y el push los hago yo.

## Forma de trabajo
- Una refactorización a la vez. Muestra el diff y espera el VoBo.
- Sin edición de `docs/`.
