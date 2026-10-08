# PLAN de refactorización — Tienda "La Esquina"

Diagnóstico de `src/` y plan de refactorización. Objetivo: mejorar la calidad **sin cambiar el comportamiento observable**, sin tocar `tests/` ni `pyproject.toml`.

Línea base: `pytest -q` → 20 passed; `ruff check src` → 20 errores. Meta: 20 passed y 0 errores.

## 1. Mapa de `src/`

| archivo | responsabilidad | funciones | dependencias |
|---|---|---|---|
| `gestor.py` | Lógica de negocio y **estado global** (`INVENTARIO`, `VENTAS`, `contadorVentas`, `ultimo_error`, `MODO_DEBUG`). Señala fallos devolviendo `False`/`None` y dejando el motivo en `ultimo_error`. | `reiniciar_sistema` (vacía el estado), `agregarProducto` (valida y da de alta), `eliminar_producto`, `actualizar_stock` (suma/resta sin dejar el stock negativo), `buscarProducto` (búsqueda por nombre sin distinguir mayúsculas), `registrar_venta` (valida, calcula descuentos/IVA, descuenta stock, genera folio, arma el ticket y guarda), `cotizar` (total estimado sin VIP y sin registrar), `calcular_descuento_viejo` (muerta), `exportar_txt` (comentada) | `datetime` |
| `almacen.py` | Persistencia JSON: lee y escribe directamente el estado de `gestor` con las claves `inventario`, `ventas` y `contador`. | `guardar_datos(ruta)`, `cargar_datos(ruta)` (False si no existe o está corrupto), `hayArchivo(ruta)` | `json`, `os`, `gestor` |
| `reportes.py` | Reportes calculados sobre `gestor.INVENTARIO` y `gestor.VENTAS`; `reporte_inventario` y `resumen_ventas` imprimen **y** devuelven el texto. | `hacer_cosa` (formato `$`), `productos_stock_bajo` (stock < 5), `reporte_inventario`, `total_vendido`, `mas_vendidos(n=3)` (ordenamiento de burbuja), `resumen_ventas`, `reporteViejoCSV` (muerta) | `gestor`, `os` (sin uso) |
| `main.py` | Menú de consola: toda la E/S con el usuario. Carga `datos_ejemplo.json` al iniciar y lo guarda con la opción 8. | `pedir_numero(mensaje)` (repite hasta recibir un float válido), `menu()` (8 opciones en if/elif) | `gestor`, `almacen`, `reportes` |

Dependencias entre módulos: `main → {gestor, almacen, reportes}`, `almacen → gestor`, `reportes → gestor`. `gestor` no depende de ningún otro módulo.

## 2. Flujo de una venta (opción 2 del menú)

Ejemplo real: `A001` (Café, $185.00, stock 12), cantidad 6, cliente `VIP01`.

| # | dónde | qué pasa | ejemplo |
|---|---|---|---|
| 1 | `main.menu` | El usuario elige `2`. | — |
| 2 | `main.menu` / `pedir_numero` | Pide el código, la cantidad (`float`, truncada con `int()`) y el cliente (puede quedar vacío). | `"A001"`, `6`, `"VIP01"` |
| 3 | `gestor.registrar_venta` | Valida **en este orden**: código vacío → `"codigo vacio"`; no existe → `"producto no existe"`; cantidad `None`/≤ 0 → `"cantidad invalida"`; stock < cantidad → `"stock insuficiente"`. Si falla, devuelve `None` sin tocar el estado. | pasa |
| 4 | idem | Subtotal = precio × cantidad. | 1110.00 |
| 5 | idem | Descuento por volumen: ≥ 1000 → 10 %; ≥ 500 → 5 %. | 111.00 |
| 6 | idem | Extra VIP: si el cliente empieza con `"VIP"` **y** subtotal − descuento > 200, suma el 2 % del subtotal. | +22.20 → 133.20 |
| 7 | idem | Base = subtotal − descuento; IVA = 16 % de la base; total = `round(base + IVA, 2)`. | 976.80 / 156.29 / 1133.09 |
| 8 | idem | Descuenta el stock en sitio en `INVENTARIO`. | 12 → 6 |
| 9 | idem | `contadorVentas += 1` → folio. | 1 |
| 10 | idem | Arma el dict `venta`: campos redondeados a 2 decimales, `cliente` y `fecha` (`datetime.now`). | — |
| 11 | idem | Arma el ticket en texto. La línea `Descuento` solo aparece si el descuento > 0. | ver la salida de caracterización |
| 12 | idem | `VENTAS.append(venta)` y devuelve `venta`. | — |
| 13 | `main.menu` | Imprime `venta["ticket"]`, o `Error: <ultimo_error>` si recibió `None`. | — |
| 14 | `reportes.*` | `resumen_ventas`, `mas_vendidos` y `total_vendido` leen `VENTAS`. | — |
| 15 | `main.menu` → `almacen.guardar_datos` | Solo con la opción 8 la venta se persiste en `datos_ejemplo.json` (inventario, ventas y contador). | — |

## 3. Code smells

| # | archivo · función | tipo de smell | descripción del problema | regla ruff | prioridad |
|---|---|---|---|---|---|
| 1 | gestor · `registrar_venta` | Función larga / múltiples responsabilidades | Valida, calcula precios, muta el stock, genera el folio, arma el ticket y guarda la venta, todo en ~75 líneas. | C901 (12 > 10) | Alta |
| 2 | gestor · `registrar_venta` | Condicionales anidados (código flecha) | Las 4 validaciones están anidadas en if/else de 4 niveles en lugar de usar cláusulas de guarda. | (aporta a C901) | Alta |
| 3 | gestor · `registrar_venta` / `cotizar` | Código duplicado | El cálculo de descuento por volumen e IVA está copiado en las dos funciones. | — | Alta |
| 4 | gestor · `registrar_venta` | ifs anidados | La regla VIP usa 4 `if` anidados (`!= ""`, `is not None`, `len >= 3`, `[0:3] == "VIP"`). | SIM102 ×3 | Media |
| 5 | gestor · `registrar_venta` | else-if anidado | El `else: if aux >= 500` podría ser un `elif`/ternario. | SIM108 | Baja |
| 6 | gestor · `registrar_venta`, `cotizar`; reportes · stock bajo | Números mágicos | 1000, 500, 0.10, 0.05, 0.02, 200, 0.16 y 5 aparecen sin nombre. | — | Media |
| 7 | gestor · módulo | Nombre fuera de convención | `contadorVentas` es mixedCase en un global. | N816 | Media |
| 8 | gestor · módulo | Estado global mutable | Hay `global` en 5 funciones; `almacen` escribe en el estado de `gestor`. Se **conserva** porque es la API de los tests. | — | Baja (fuera de alcance) |
| 9 | gestor · `calcular_descuento_viejo`, `exportar_txt` (comentado); reportes · `reporteViejoCSV` | Código muerto | Nadie lo llama ("por si acaso"). | N802, SIM115 (en `reporteViejoCSV`) | Media |
| 10 | gestor · `MODO_DEBUG` | Variable sin uso | Se declara y nunca se lee. | — | Baja |
| 11 | gestor (`temp2`, `aux`, `x`, `desc`, `t`); reportes (`hacer_cosa`, `aux`, `temp`, `s`); main (`temp2`, `c`, `n`, `p`, `s`) | Nombres poco descriptivos | Los nombres no dicen qué contienen; `hacer_cosa` en realidad formatea dinero. | — | Media |
| 12 | gestor · `registrar_venta` | Mezcla de capas | La lógica de negocio construye el texto de presentación (el ticket). | — | Media |
| 13 | almacen · `guardar_datos`, `cargar_datos` | Recurso sin context manager | `open`/`close` manuales: el archivo queda abierto si ocurre una excepción. | SIM115 ×2 | Alta |
| 14 | almacen · `cargar_datos` | Excepción demasiado amplia | `except Exception` oculta cualquier error, no solo un JSON inválido. | — (BLE no está activa) | Media |
| 15 | almacen · `cargar_datos` | Argumento redundante | Pasa el modo `"r"` explícitamente. | UP015 | Baja |
| 16 | almacen · `hayArchivo` | if/else que devuelve bool + camelCase | `if cond: return True else: return False`. | SIM103, N802 | Baja |
| 17 | reportes · `mas_vendidos` | Algoritmo reinventado | Ordenamiento de burbuja hecho a mano (con un TODO de usar `sorted`). | — | Media |
| 18 | reportes · `resumen_ventas` / `total_vendido` | Lógica duplicada | Las dos suman `v["total"]` cada una por su lado. | — | Baja |
| 19 | reportes · módulo | Import sin uso | `import os`. | F401 | Baja |
| 20 | reportes · varios | Concatenación repetitiva | Construye el texto con `s = s + ...` en lugar de f-strings/`join`. | — | Baja |
| 21 | main · `menu` | Función larga / switch | if/elif de 8 ramas, cada una con su E/S inline. | C901 (17 > 10) | Media |
| 22 | main · imports | Imports desordenados | El bloque de imports no está ordenado. | I001 | Baja |
| 23 | los 4 archivos | Declaración obsoleta | `# -*- coding: utf-8 -*-` es innecesario en Python 3. | UP009 ×4 | Baja |
| 24 | varias (`agregarProducto`, `buscarProducto`, `hayArchivo`, `hacer_cosa`, `pedir_numero`) | Comentario en lugar de docstring; sin type hints | No sigue las convenciones de CLAUDE.md. | — | Baja |

## 4. Plan de refactorización (de menor a mayor riesgo; un commit cada una)

Verificación obligatoria en cada paso: se cumplen los criterios de la sección 5; se corren las dos caracterizaciones de la sección 9 antes y después del cambio, y el `diff` debe salir vacío; y se revisa a mano el diff con la lista de la sección 8 de esa refactorización.

| # | refactorización | cambios | smells | ruff (antes → después) | riesgo | commit propuesto | estado |
|---|---|---|---|---|---|---|---|
| R0 | Arreglos automáticos de ruff (preparatorio, no cuenta como refactorización) | `ruff check src --fix`: quita `coding`, el modo `"r"`, el `import os` sin uso y ordena imports | 15, 19, 22, 23 | 20 → 13 | Nulo | `style(src): aplica arreglos automáticos de ruff` | Aplicado |
| R1 | Eliminar código muerto | Borrar `calcular_descuento_viejo`, el bloque `exportar_txt`, `MODO_DEBUG` y `reporteViejoCSV` | 9, 10 | 13 → 11 | Bajo | `refactor(gestor): elimina código muerto y variables sin uso` | Aplicado |
| R2 | Persistencia segura en `almacen` | `with open(...)` en guardar/cargar; `except (ValueError, RecursionError, OSError)` en lugar de `Exception` (`ValueError` cubre `JSONDecodeError`, `UnicodeDecodeError` y enteros gigantes; `RecursionError` cubre el JSON con anidamiento muy profundo; `OSError` cubre los errores de lectura dentro de `json.load`; `open()` queda fuera del `try` y sus errores se siguen propagando); `hayArchivo` → `hay_archivo` que devuelve `os.path.exists(ruta)` y se actualiza `main.py` en el mismo commit | 13, 14, 16 | 11 → 7 | Bajo | `refactor(almacen): usa context managers y simplifica hay_archivo` | Aplicado |
| R3 | Claridad en `reportes` | `hacer_cosa` → `formatear_dinero`; constante `STOCK_MINIMO = 5`; `mas_vendidos` con `sorted(..., key=..., reverse=True)` (estable, conserva el orden de los empates); `resumen_ventas` construye el texto con f-strings sin cambiar el formato | 6 (parcial), 11, 17, 20 | 7 → 7 | Bajo-medio | `refactor(reportes): renombra helpers y reemplaza burbuja por sorted` | Aplicado |
| R4 | Renombrar `contadorVentas` | `contadorVentas` → `contador_ventas` en `gestor` (global, `reiniciar_sistema`, `registrar_venta`) y en `almacen` (guardar/cargar); la clave JSON `contador` no cambia | 7 | 7 → 6 | Medio | `refactor(gestor): renombra contadorVentas a contador_ventas` | Aplicado |
| R5 | Extraer las reglas de precio | Constantes de negocio (`UMBRAL_DESCUENTO_ALTO`, `TASA_IVA`, …); funciones `_descuento_por_volumen(subtotal)` y `_total_con_iva(base)` compartidas por `registrar_venta` y `cotizar`; regla VIP como `cliente and cliente.startswith("VIP") and subtotal - descuento > 200`. `cotizar` **sigue sin aplicar VIP** y `cotizar == registrar_venta(...)["total"]` sin cliente | 3, 4, 5, 6 | 6 → 1 (también baja la complejidad de `registrar_venta` de 12 a ~7, lo que resuelve su C901) | Medio-alto | `refactor(gestor): extrae el cálculo de descuentos e IVA a funciones` | Pendiente |
| R6 | Dividir `registrar_venta` | `_validar_venta(codigo, cantidad) -> str \| None` con cláusulas de guarda en el **mismo orden** de mensajes; `_armar_ticket(venta, hubo_descuento)` que conserva el formato exacto (la línea `Descuento` depende del descuento sin redondear); `registrar_venta` solo orquesta. Nombres descriptivos y docstrings | 1, 2, 11, 12, 24 | 1 → 1 (cambio estructural, sin regla nueva) | Alto | `refactor(gestor): divide registrar_venta en validación, cálculo y ticket` | Pendiente |
| R7 | Menú por despacho en `main` | Una función por opción (`_opcion_agregar`, `_opcion_vender`, …) y un dict `OPCIONES`; `menu()` solo hace el ciclo. Mensajes y orden de los `input()` idénticos; `temp2` → `respuesta` | 11, 21, 24 | 1 → 0 | Alto (sin tests: depende de la caracterización) | `refactor(main): reemplaza el if/elif del menú por un despacho de opciones` | Pendiente |

Suma de los errores de ruff: R0 7 + R1 2 + R2 4 + R4 1 + R5 5 + R7 1 = **20 → 0**.

**Fuera de alcance:** eliminar el estado global y el patrón `ultimo_error`, porque forman parte de la API que usan los tests. `agregarProducto` y `buscarProducto` conservan su nombre.

**Nota para el usuario:** después de R4 hay que actualizar a mano `contadorVentas` en `CLAUDE.md` (está en `deny` para mí).

## 5. Criterios de aceptación

Criterios globales del plan (se comprueban después de **cada** refactorización y al final del PR):

| # | criterio | cómo se verifica |
|---|---|---|
| C1 | pytest 20/20 en verde después de cada refactorización | `.venv/Scripts/python -m pytest -q` → `20 passed` |
| C2 | Los errores de ruff nunca aumentan y quedan en 0 al final | `.venv/Scripts/python -m ruff check src`: el número es ≤ al de la fila anterior de la sección 4; tras R7 → `All checks passed!` |
| C3 | `tests/` y `pyproject.toml` sin cambios | `git diff --stat main -- tests pyproject.toml` sale vacío |
| C4 | Comportamiento observable idéntico | El `diff` de las dos caracterizaciones (sección 9) sale vacío y la revisión manual de la sección 8 no encuentra cambios |

## 6. Cuidado de los tests: qué protegen

Leí los 4 archivos de `tests/`. `conftest.py` no tiene tests: es un fixture `autouse` que llama a `gestor.reiniciar_sistema()` antes y después de cada test. Solo dejo constancia de lo que cada `assert` comprueba literalmente.

| test | qué verifica |
|---|---|
| `test_gestor::test_agregar_producto_queda_en_inventario` | `agregarProducto` devuelve exactamente `True`; la clave queda en `INVENTARIO`; se guardan `nombre` y `stock`. (No revisa `precio` ni `codigo`). |
| `test_gestor::test_rechaza_altas_invalidas` | Devuelve `False` con código duplicado, precio 0, precio negativo y stock −1. (No revisa el mensaje, el código vacío ni que el rechazado no se haya insertado). |
| `test_gestor::test_actualizar_stock_suma_y_resta` | +5 → `True` y stock 15; −15 → `True` y stock 0 (el 0 se permite); −1 → `False`. (No revisa que el stock no cambie al fallar ni el caso de producto inexistente). |
| `test_gestor::test_eliminar_producto` | Devuelve `True` y quita el producto; la segunda vez devuelve `False`. |
| `test_gestor::test_buscar_producto_por_nombre` | `"café"` encuentra `"Café de grano"` (no distingue mayúsculas); exactamente 1 resultado con `codigo` A1. |
| `test_gestor::test_venta_descuenta_stock_y_asigna_folio` | La venta no es `None`, folio 1 (indirectamente: `reiniciar_sistema` reinicia el contador), stock 50 → 47, `len(VENTAS) == 1`. |
| `test_gestor::test_venta_sin_descuento_aplica_iva` | 2 × $10 → `total == 23.2`. |
| `test_gestor::test_venta_con_descuento_por_volumen_medio` | 6 × $100 = 600 → 5 % → `total == 661.2`. |
| `test_gestor::test_venta_con_descuento_por_volumen_alto` | 20 × $100 = 2000 → 10 % → `total == 2088.0`. |
| `test_gestor::test_venta_cliente_vip_recibe_descuento_extra` | 600 con `"VIP007"` → 5 % + 2 % → `total == 647.28`. |
| `test_gestor::test_venta_rechaza_stock_insuficiente` | Pedir 3 con stock 2 → `None`; el stock sigue en 2 y `VENTAS` vacío. |
| `test_gestor::test_venta_rechaza_producto_inexistente_y_cantidad_invalida` | `"ZZZ"`, cantidad 0 y cantidad −2 → `None`. (No revisa los mensajes). |
| `test_gestor::test_cotizar_coincide_con_el_total_de_la_venta` | `cotizar("A1", 6) == registrar_venta("A1", 6)["total"]` (un solo caso: 600, 5 %, sin cliente). |
| `test_almacen::test_guardar_y_cargar_conserva_los_datos` | `guardar_datos` devuelve `True`; tras reiniciar, `INVENTARIO == {}`; `cargar_datos` devuelve `True` y restaura stock 48, 1 venta y `total == 232.0`. |
| `test_almacen::test_el_folio_continua_despues_de_recargar` | Después de guardar y cargar, la siguiente venta tiene folio 2 (el contador se guarda y se restaura). |
| `test_almacen::test_cargar_archivo_inexistente_regresa_false` | `cargar_datos` de una ruta inexistente → `False`. |
| `test_reportes::test_stock_bajo_detecta_los_correctos` | Con stock 3, 40 y 2 devuelve exactamente A1 y A3. (Compara con `sorted`: **no** protege el orden). |
| `test_reportes::test_total_vendido_suma_las_ventas` | Sin ventas → `== 0`; dos ventas de $23.20 → `46.4`. |
| `test_reportes::test_mas_vendidos_ordena_por_unidades` | Suma por código y ordena descendente: `("A1", 6)`, `("B1", 2)` con `n=2`. (Sin empates). |
| `test_reportes::test_reporte_inventario_marca_stock_bajo` | El texto devuelto contiene `"Leche"` y `"STOCK BAJO"`. (Nada más del formato). |

## 7. Comportamientos observables SIN ningún test

Los valores de la columna "comportamiento actual" se comprobaron ejecutando la app (secciones 2 y 9), no se supusieron.

| área | comportamiento sin test | comportamiento actual |
|---|---|---|
| Ticket | Todo el texto de `venta["ticket"]` | `TIENDA LA ESQUINA` / 28 guiones / `Folio: N` / `<nombre> x<cant>` / `Subtotal: $…` / `Descuento: -$…` (solo si el descuento > 0) / `IVA: $…` / `TOTAL: $…`, cada línea con `\n` |
| Ticket | Formato del dinero | `"$" + str(round(v, 2))` → `$210.0`, `$0.5`, `$1.6` (**no** usa 2 decimales fijos) |
| Venta | Campos distintos de `total` y `folio` | Ningún test revisa `subtotal`, `descuento`, `impuesto`, `cliente`, `fecha` (`%Y-%m-%d %H:%M:%S`), `codigo`, `nombre`, `cantidad` |
| Venta | Tipo de `descuento` cuando no hay descuento | `0` **entero** (sale `"descuento": 0` en el JSON), no `0.0` |
| Venta | Orden de las claves del dict `venta` | `folio, codigo, nombre, cantidad, subtotal, descuento, impuesto, total, cliente, fecha, ticket`: es el orden en que se escriben en el JSON |
| Redondeos | Cada campo se redondea por separado; el total se calcula sin redondear los parciales | `impuesto = base * 0.16`; `total = round(base + impuesto, 2)` |
| Límites de precio | Subtotal exactamente 500 y 1000 (usa `>=`) | 500 → 5 % (cotizar 50 × $10 = `$551.0`); 1000 → 10 % |
| Límites VIP | `subtotal − descuento` exactamente 200 (usa `>`); VIP sin descuento por volumen; prefijo en minúsculas; cliente `None` | VIP con subtotal 210 sin volumen → descuento 4.2; `"vip"` no es VIP (`startswith` distingue mayúsculas) |
| Límites de stock | Vender exactamente el stock disponible (`>=`) | Se permite |
| Stock bajo | Umbral exacto (`< 5`) y orden de la lista | stock 5 no es bajo; orden de inserción en `INVENTARIO` |
| Más vendidos | Empates, `n` por defecto (3), `n` mayor que el número de productos | Empates en el orden de primera venta (burbuja estable) |
| Búsqueda | Orden de los resultados, texto vacío, que devuelve referencias a los dicts de `INVENTARIO` | Orden de inserción; `""` devuelve todos |
| Mensajes de error | **Ningún** test revisa `ultimo_error` | `codigo vacio`, `el producto ya existe`, `precio invalido`, `stock invalido`, `producto no existe`, `el stock no puede quedar negativo`, `cantidad invalida`, `stock insuficiente`, `el archivo no existe`, `archivo corrupto` |
| Orden de validaciones | Qué mensaje gana si hay varios errores | `registrar_venta`: vacío → inexistente → cantidad → stock. `cotizar`: inexistente → cantidad (no revisa el código vacío **ni el stock**) |
| Estado tras fallo | El folio no avanza si la venta falla; `actualizar_stock` fallido no cambia el stock | Solo se prueba el stock y `VENTAS` en el caso de stock insuficiente |
| Altas | Código vacío o `None`; stock 0 permitido; el producto rechazado no se inserta; claves del dict de producto | — |
| Persistencia | Formato del archivo: `indent=2`, `ensure_ascii=False` (acentos sin escapar), claves `inventario`/`ventas`/`contador` | Se lee `datos_ejemplo.json` con esas claves |
| Persistencia | Archivo corrupto → `False` + `archivo corrupto`; `cargar_datos` reemplaza (no mezcla) el estado; sin clave `contador` → 0 | — |
| Reportes | Formato completo de `reporte_inventario` (incluido `Valor total del inventario`) y que también imprime | Líneas `COD \| nombre \| $precio \| stock: N` + `  <-- STOCK BAJO` |
| Reportes | `resumen_ventas` completo (sin ningún test) | `Folio N: <nombre> x<cant> = $total`, `Numero de ventas: N`, `Total del dia: $…` |
| Menú | Todo `main.py` | Textos del menú y de los `input()`, `Opcion no valida.`, `Eso no es un numero, intenta de nuevo.`, `Producto agregado.`, `Error: <msg>`, `Total estimado (con IVA): $…`, `A -> N unidades`, `OJO: … solo tiene N unidades`, `No hay productos con stock bajo.`, `Datos cargados de …` (solo si el archivo existe), `Datos guardados. Hasta luego.` |
| Menú | Conversión de cantidades | `int(pedir_numero())` **trunca**: 1.9 → 1; 4.9 → 4 |

## 8. Refactorizaciones que podrían cambiar el comportamiento sin que falle ningún test

| ref. | qué podría cambiar sin que falle ningún test | qué revisar a mano en el diff |
|---|---|---|
| R0 | Casi nada: `--fix` solo debería tocar `coding`, el modo `"r"`, `import os` y el orden de imports. | `git diff --stat`: solo líneas de import/encabezado; ninguna otra línea modificada; `tests/` intacto. |
| R1 | Borrar algo que sí se usa. Ningún test llama a `reporteViejoCSV` ni a `MODO_DEBUG`, así que si algo los usara, nada fallaría. | `grep -rn "calcular_descuento_viejo\|exportar_txt\|reporteViejoCSV\|MODO_DEBUG" src` vacío; el diff solo tiene líneas `-`. |
| R2 | (a) Una excepción que antes se atrapaba ahora se propaga (no hay test de archivo corrupto). (b) Cambian los textos `el archivo no existe` / `archivo corrupto`. (c) Cambia `indent=2` o `ensure_ascii=False` del JSON. (d) Cambia el orden de limpiar/llenar el estado. (e) `main.py` sigue llamando a `hayArchivo`. | Tupla del `except` (debe cubrir `ValueError`, `RecursionError` y `OSError`; `open()` fuera del `try`); mensajes idénticos; argumentos de `json.dump` idénticos; `encoding="utf-8"` y modos; llamada en `main.py` renombrada. |
| R3 | (a) `formatear_dinero` pasa a `f"{v:.2f}"` → `$185.00` en lugar de `$185.0`. (b) `STOCK_MINIMO` con `<=` en lugar de `<`. (c) `sorted` con criterio o dirección distinta → orden de los empates. (d) f-strings que cambian espacios, saltos de línea o el doble salto de `print(s)`. (e) Se quita el `print` o el `return`. | Expresión exacta `"$" + str(round(v, 2))`; operador `<`; `key` solo por unidades con `reverse=True` (estable); cada literal de texto contra el original; `print(s)` y `return s` presentes. |
| R4 | (a) Cambiar la clave JSON `"contador"`: guardar y cargar siguen siendo simétricos, **los tests pasan**, pero `datos_ejemplo.json` y los archivos existentes reinician los folios en 1. (b) `almacen` asigna el nombre viejo (`gestor.contadorVentas = …`) y crea un atributo nuevo; esto sí lo detecta `test_el_folio_continua…`. | La cadena `"contador"` sin cambios en `guardar_datos`/`cargar_datos`; `global contador_ventas` en cada función que lo asigna; `grep -rn contadorVentas src` vacío. |
| R5 | (a) `>=` ↔ `>` en los umbrales 500/1000 o `>` ↔ `>=` en el 200 del VIP (no hay test en los límites). (b) El 2 % VIP calculado sobre la base en lugar del subtotal, o la condición evaluada después de sumar el VIP. (c) `startswith("VIP")` con `.upper()` o `.lower()`. (d) `round(base * 1.16, 2)` en lugar de `round(base + base * 0.16, 2)` (puede cambiar el último centavo). (e) `cotizar` empieza a aplicar VIP o cambia su firma. (f) `desc = 0.0` en lugar de `0` → el JSON guarda `0.0`. | Operadores de comparación; base del 2 % y del 200; mayúsculas y minúsculas; expresión exacta del IVA y del total; firma `cotizar(codigo, cantidad)`; literal `0` inicial del descuento. |
| R6 | (a) Orden de las validaciones o texto de los mensajes (los tests solo esperan `None`). (b) Mutar el stock o el folio antes de terminar de validar (solo se prueba el caso de stock insuficiente). (c) Formato del ticket: guiones, `x` pegada, la condición de la línea `Descuento`, el `\n` final. (d) Orden de las claves del dict `venta` → cambia el JSON guardado. (e) Formato de `fecha`. (f) `cotizar` reutiliza `_validar_venta` → aparecen los mensajes `codigo vacio` y `stock insuficiente` en cotizar. | Secuencia de guardas idéntica (vacío/`None` → inexistente → cantidad `None`/≤0 → stock `<`); mutaciones después de validar; cada línea del ticket contra el original; orden de las asignaciones a `venta`; `strftime` idéntico; `cotizar` conserva su propia validación. |
| R7 | Todo `main.py` carece de tests: textos de menú y prompts, orden de los `input()`, `int()` truncando, separador de `print` con coma (`"Error:", msg`), opción 8 = guardar **y** salir, opción inválida, mensaje de carga solo si existe el archivo. | Cada cadena literal contra el original; mismo número y orden de `input()`; `print(a, b)` sin convertir a f-string con otro espaciado; `break` solo en la opción 8; diff vacío de las caracterizaciones. |

## 9. Caracterización (red de seguridad para lo que no cubren los tests)

Se corre **antes** del cambio (`antes`) y **después** (`despues`); los dos `diff` deben salir vacíos.

**A. Con los datos de ejemplo (opciones 2–7, no escribe archivos):** el comando de `CLAUDE.md`.

**B. Ampliada, en una carpeta temporal vacía:** cubre el arranque sin archivo, el alta, el código duplicado, una entrada no numérica, la truncación con `int()`, una opción inválida, VIP sin descuento por volumen, una venta sin descuento, los 3 mensajes de error de venta y cotizar, el límite de 500, todos los reportes y el guardado en JSON (opción 8). No toca `datos_ejemplo.json` del repo.

```bash
caract() {  # uso: caract antes | caract despues
  R="$PWD"; D="$TMP/caract_$1"; rm -rf "$D"; mkdir -p "$D"; cd "$D"
  printf '1\nZ001\nProducto zeta\nabc\n0.5\n4.9\n1\nZ001\nDup\n10\n1\n1\nZ002\nBarato\n10\n100\n9\n2\nZ001\n1000\nVIP9\n2\nZ002\n21\nVIP1\n2\nZ002\n1.9\nvip\n2\n\n1\n\n3\nNOPE\n1\n3\nZ001\n0\n3\nZ002\n50\n4\n6\n7\n5\n8\n' \
    | PYTHONIOENCODING=utf-8 "$R/.venv/Scripts/python" "$R/src/main.py" > salida.txt 2>&1
  grep -v '"fecha"' *.json > guardado.txt   # la fecha cambia en cada corrida
  cd "$R"
}
caract antes   # ...aplicar la refactorización...
caract despues
diff "$TMP/caract_antes/salida.txt"   "$TMP/caract_despues/salida.txt"
diff "$TMP/caract_antes/guardado.txt" "$TMP/caract_despues/guardado.txt"
```
