# CLAUDE.md

## Contexto

Reto de **refactorización asistida por IA**: una app de consola en Python 3.10+ (inventario y ventas de la tienda "La Esquina") que funciona, pero está llena de *code smells* a propósito. El objetivo es mejorar la calidad **sin cambiar el comportamiento observable**. Se trabaja en la rama `refactorizacion` y se entrega por PR hacia `main`, con commits atómicos (idealmente uno por refactorización).

## Reglas obligatorias

- **No modificar nada en `tests/` ni `pyproject.toml`.** Si un test falla, el error está en el cambio a `src/`, nunca en el test ni en la configuración de ruff.
- Después de **cada** refactorización correr `pytest` y `ruff check src`; ambos deben pasar antes de pasar a la siguiente.
- `agregarProducto` y `buscarProducto` conservan su nombre (los usan los tests; están en `ignore-names` de ruff). El resto de la API usada por los tests también debe mantener nombre y firma: `gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.reiniciar_sistema`, `gestor.actualizar_stock`, `gestor.eliminar_producto`, `gestor.registrar_venta`, `gestor.cotizar`, `almacen.guardar_datos`, `almacen.cargar_datos`, `reportes.mas_vendidos`, `reportes.productos_stock_bajo`, `reportes.reporte_inventario`, `reportes.total_vendido`.
- Una refactorización a la vez; los cambios cosméticos aislados no cuentan como refactorización significativa.

## Comandos (correr los dos después de CADA cambio, en este orden)
- `pytest -q` → todos en verde (línea base: 20)
- `ruff check src` → línea base: 20 errores; meta: 0
- `ruff check src --fix` solo para lo trivial (UP009, UP015, I001, F401)
- App: `cd src && python main.py` (lee `datos_ejemplo.json` relativo al cwd)

## Arquitectura

Módulos planos en `src/` que se importan entre sí sin paquete (`import gestor`); `tests/conftest.py` agrega `src/` a `sys.path` y llama a `gestor.reiniciar_sistema()` antes y después de cada test.

- **`gestor.py`** — lógica de negocio y **estado global del sistema**: `INVENTARIO` (dict `codigo -> {codigo, nombre, precio, stock}`), `VENTAS` (lista de dicts de venta), `contadorVentas` (último folio) y `ultimo_error`. Las funciones señalan fallo devolviendo `False`/`None` y dejando el motivo en `gestor.ultimo_error`, que `main.py` imprime.
- **`almacen.py`** — persistencia JSON. Lee y escribe directamente el estado de `gestor` (`gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.contadorVentas`). Las claves del JSON (`inventario`, `ventas`, `contador`) deben mantenerse para seguir leyendo `datos_ejemplo.json`.
- **`reportes.py`** — reportes calculados sobre el estado de `gestor`; `reporte_inventario` y `resumen_ventas` imprimen **y** devuelven el texto.
- **`main.py`** — menú de consola (toda la E/S con el usuario).

### Puntos delicados al refactorizar

- `INVENTARIO` y `VENTAS` se mutan en sitio (`.clear()`, asignación de claves) y otros módulos los leen como `gestor.INVENTARIO`. Si se renombra `contadorVentas` o se cambia cómo se guarda el estado, actualizar también `almacen.py` y `reiniciar_sistema`.
- Reglas de precio en `registrar_venta`: subtotal ≥ 1000 → 10 % de descuento; ≥ 500 → 5 %; cliente que empieza con `"VIP"` suma 2 % extra del subtotal **solo si** `subtotal - descuento > 200`; IVA 16 % sobre la base; redondeos a 2 decimales en cada campo de la venta.
- `cotizar` duplica el cálculo de descuento/IVA pero **no** aplica el descuento VIP (no recibe cliente). Al extraer la lógica común hay que conservar esa diferencia y que `cotizar(...) == registrar_venta(...)["total"]` sin cliente.
- `registrar_venta` debe validar todo antes de tocar el stock o el folio (un fallo no altera estado). El orden de las validaciones determina el mensaje en `ultimo_error`.
- El texto del ticket y de los reportes es comportamiento observable: mantener formato exacto (p. ej. la línea `Descuento` solo aparece si hay descuento, la marca `<-- STOCK BAJO` con stock < 5).
- Código muerto conocido (sin llamadas): `calcular_descuento_viejo`, el bloque comentado `exportar_txt` en `gestor.py`, y `reporteViejoCSV` en `reportes.py`.

## Convenciones de Python
- snake_case en funciones y variables, constantes de negocio en MAYÚSCULAS.
- Type hints con sintaxis 3.10: `float | None`, `list[dict]` (no `Optional`/`List`).
- Docstrings de una línea, en español.
- Archivos siempre con `with open(..., encoding="utf-8")`.
- Límites de ruff: líneas ≤ 88 caracteres, complejidad ≤ 10.

## Ramas y commits
- Solo se trabaja en `refactorizacion`, la entrega es en un PR de `refactorizacion` a `main`
- Convención de commmits: `tipo(alcance): descripción`(feat, fix, refactor, test, docs). El mensaje debe de ser menos a 100 caracteres, en español.
```text
Correcto:
 refactor(gestor): extrae el cálculo de descuentos a una función
 docs(claude): agrega regla sobre el orden de validaciones
Incorrecto:
 Refactoricé varias cosas del gestor
 refactor: cambios
```
- Un commit por refactorización. Propon el mensaje y los commits y push los hago yo.

## Forma de trabajo
- Una refactorización a la vez. Muestra el diff y espera el VoBo.
- Sin edición de `docs/`