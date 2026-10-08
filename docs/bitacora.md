# Bitácora de refactorización

**Nombre:** Eduardo Daniel Sánchez Delgado
**Matrícula:** 
**Fecha:** 07/10/2026
**Herramienta:** Claude Code (modo plan para explorar, modo manual para cambios)

**Línea base:** 20 tests ✅ · ruff: 20 errores

## 1. Configuración

### Versión escrita a mano.
Escribí el archivo `CLAUDE.md`, `.claudeignore` y `.claude/settings.json` para agregar las reglas y configuración de Claude Code.

### Revisión de configuración
Mediante el uso de prompt solicite a Claude la revisión de la configuración en `mode plan` para mejorar la configuración.
Prompt utilizado:
`
Eres un ingeniero senior que configura proyectos en Python para trabajar con Claude Code.
  Contexto: Complemente el archivo CLAUDE.md y la configuración con el fin de refactorizar este proyecto, sin cambiar el comportamiento ni modificar @tests\ ni @pyproject.toml
  Archivos a revisar:
  - @CLAUDE.md
  - @.claudeignore
  - @.claude\settings.json

  Restricciones:
  No modifiques ningún archivo, solo analiza y reportalo

  Formato:
  Una tabla con la siguiente estructura:
  archivo | línea| problema | sugerencia
`

Me realizo algunas observaciones y rechace 3 de ellas, mejorando mucho la configuración.

## 2. Exploración
En modo plan, pedí a Claude que explicara el proyecto identificando los smells y armará un plan, todo en un solo prompt

### Prompt 1:
```
Antes de iniciar con la refactorización, quiero que expliques el proyecto, dandome un mapa de @src\, en dónde expliques que hace cada archivo y sus funciones.
  Respondeme en una tabla:
  archivo|responsabilidad|funciones|dependencias
  También explicame en otra tabla el flujo de una venta desde su inicio hasta su fin.
  Para documentar los code smells, genera una tabla en dónde indiques por smell:
  - Archivo y función
  - Tipo de smell
  - Descripción del problema
  - Regla del ruff que lo detecto
  - Prioridad

  Para este plan, genera un archivo de tipo markdown llamado PLAN.md en @docs\

  Criterios de aceptación
  Con el diagnostico, genera un plan de refactorización de por lo menos 5 refactorizaciones, iniciando de menor a mayor riesgo, cada refactorización debe ser un commit.
  Se debe de documentar cada refactorización y aplicarla en el documento PLAN.md
```

Problema: Pedí que guardará el plan en `docs/PLAN.md`, pero `docs` está protegido por la configuración, Claude se detuvo y propuso cómo crearlo(ver sección 4).
Además, olvidé agregar que cuidará los test así que modifique el prompt y quedó de la siguiente manera:
### Prompt final
```
Antes de iniciar con la refactorización, quiero que expliques el proyecto, dándome un mapa de @src\, en dónde expliques qué hace cada archivo y sus funciones.
Respóndeme en una tabla:
archivo | responsabilidad | funciones | dependencias
También explícame en otra tabla el flujo de una venta desde su inicio hasta su fin.
Para documentar los code smells, genera una tabla en donde indiques por smell:
- Archivo y función
- Tipo de smell
- Descripción del problema
- Regla de ruff que lo detecta
- Prioridad

Cuidado de los tests:
Lee @tests\ y, sin suponer nada, genera una tabla con:
- Qué comportamientos protegen los tests (test | qué verifica)
- Qué comportamientos observables NO tienen ningún test (textos que se imprimen,
  ticket, redondeos, casos límite, orden de resultados, manejo de errores, menú)
- Qué refactorizaciones de las que propongas podrían cambiar el comportamiento sin que
  ningún test falle, y qué tendría que revisar yo a mano en el diff para detectarlo.

Para este plan, genera un archivo de tipo markdown llamado PLAN.md en la raíz del
proyecto (docs\ está protegido).

Criterios de aceptación:
Con el diagnóstico, genera un plan de refactorización de por lo menos 5
refactorizaciones, iniciando de menor a mayor riesgo; cada refactorización debe ser
un commit. Para cada una documenta en PLAN.md:
- objetivo y archivos que toca
- smells que elimina y reglas de ruff que deberían desaparecer
- riesgos (de la tabla de cuidado de los tests)
- criterios de aceptación verificables
- mensaje de commit propuesto (Conventional Commits, máximo 100 caracteres)

Criterios del plan:
- pytest 20/20 en verde después de cada refactorización
- los errores de ruff nunca aumentan y quedan en 0 al final
- tests\ y pyproject.toml sin cambios
- comportamiento observable idéntico

Restricción: no modifiques ningún archivo de src\ ni tests\; solo analiza, reporta y
genera PLAN.md.
```

### Resultado
El documento se encuentra en /PLAN.md

## 3. Refactorizaciones

| # | Prompt usado | Cambio realizado | Justificación | Tests OK | Ruff | Commit |
|---|---|---|---|---|---|---|
| R0 | "Iniciamos con R0 del PLAN.md… muéstrame lo que cambia `--fix` y espera mi VoBo…" (completo abajo) | `ruff --fix`: quitó 4 `# -*- coding -*-`, el modo `"r"` y el `import os` sin uso; ordenó imports | Quita ruido para que los siguientes diffs muestren solo cambios reales. Es preparación, no cuenta como refactorización | ✅ 20/20 | 20 → 13 | `709409a` |
| R1 | Continuemos con R1 del plan. Pero antes de borrar busca tanto en @src\ y @tests\ alguna referencia de calcular_descuento_viejo, exportar_txt, MODO_DEBUG y reporteViejoCSV, y muéstrame el resultado. Si alguno se usa en algún lado, detente y avísame. - Corre la caracterización "antes" - Muestra el diff de lo que se va borrando y espera el VoBo - Corre pytest, ruff, la caracterización "despues" y los diff - Dime tests antes => despues, errores ruff antes=> despues, si la caracterización salió igual y dame el mensaje del commit." | Se eliminaron `calcular_descuento_viejo`, el bloque comentado `exportar_txt`, `MODO_DEBUG` y `reporteViejoCSV` | Código que nadie llama igual hay que leerlo y mantenerlo; "por si acaso" ya lo cubre git | ✅ 20/20 | 13 → 11 | `7527ae5` |
| R2 | Continuemos con R2 del plan... revisar las notas para el prompt completo.| `with open` en guardar/cargar; `except Exception` => ‹excepciones elegidas›; `hayArchivo` => `hay_archivo` (actualizado en `main.py`) | Antes, si `json.dump` fallaba, el archivo quedaba abierto; `except Exception` ocultaba cualquier error, no solo un JSON inválido | ✅ 20/20 | 11 => 7 | `bb5b723` |
| R3 | "Continuemos con R3 del plan...revisar las notas para el prompt completo. | `hacer_cosa` => `formatear_dinero`; constante `STOCK_MINIMO`; `sorted` en lugar de burbuja en `mas_vendidos`; f-strings en los reportes | `hacer_cosa` no decía qué hacía; el 5 estaba repetido; la burbuja reinventaba `sorted`; la concatenación era difícil de leer | ✅ 20/20 | 7 => 7 | `07374a1` |
| R4 | "Vamos con R4 del PLAN.md... revisar las notas para el prompt completo | `contadorVentas` => `contador_ventas` en `gestor.py` y `almacen.py`; la clave JSON `"contador"` no cambia | Nombre en mixedCase en un global (N816); PEP 8 pide snake_case | ✅ 20/20 | 7 => 6 | `25b23e4` |
| R5 | Vamos con R5 del PLAN.md: extraer... revisar notas para ver el prompt completo | Constantes de negocio; `_descuento_por_volumen` y `_total_con_iva` compartidas por `registrar_venta` y `cotizar`; regla VIP en una sola condición con `startswith` | Números mágicos y lógica duplicada entre `registrar_venta` y `cotizar`; if anidados (SIM102 ×3, SIM108, C901 de `registrar_venta`) | ✅ 20/20 | 6 => 1 | `a3d0e8b` |

### Notas
**Prompt R2 completo.**
```
Continuemos con R2 del plan.
  <tarea>
  1. Usa with open(...) en guardar_datos y cargar_datos.
  2. Cambia except Exception por las excepciones específicas que puede lanzar
     json.load con un archivo corrupto.
  3. Renombra hayArchivo a hay_archivo, con un solo return, y actualiza main.py
     en el mismo cambio.
     </tarea>

  <antes_de_cambiar>
  - Corre la caracterización "antes".
  - Explícame qué excepciones puede lanzar json.load con un archivo corrupto y si OSError debe ir en el except.
  - Para tomar en cuenta: hoy, si open() falla, el error se puede propagar
    porque open() está fuera del try. Eso no debe cambiar.
  </antes_de_cambiar>

  <restricciones>
  - Los mensajes "el archivo no existe" y "archivo corrupto" no cambian.
  - No toques nada fuera de almacen.py y la llamada en main.py.
  </restricciones>

  Muéstrame el diff y espera mi VoBo. Después corre pytest, ruff, la caracterización
  "después" y los diff; prueba además cargar un JSON corrupto antes y después
  (debe dar False y "archivo corrupto" en los dos casos). Dame el
  mensaje de commit.
```
**Prompt R3 Completo.**
```
Continuemos con R3 del plan:
  Vamos con R3 del PLAN.md: claridad en reportes.py.

  <tarea>
  1. Renombra hacer_cosa a formatear_dinero.
  2. Extrae la constante STOCK_MINIMO = 5 y úsala en productos_stock_bajo y reporte_inventario.
  3. Reemplaza el ordenamiento de burbuja de mas_vendidos por sorted
  4. Construye el texto de resumen_ventas y reporte_inventario con f-strings
  </tarea>

  <antes_de_cambiar>
  - Corre la caracterización "antes"
  - Prueba mas_vendidos con el código actual en estos casos y guarda los resultados:
    empate de unidades, n=0, n=1, n=-1, n mayor que el número de productos y sin ventas.
  </antes_de_cambiar>

  <restricciones>
  - formatear_dinero debe seguir produciendo "$" + str(round(v, 2)) (ej. $210.0, no $210.00)
  - No uses Counter.most_common(n), debe seguir siendo un slice [:n]
  - reporte_inventario y resumen_ventas siguen imprimiendo Y regresando el texto.
  - No toques gestor.py, almacen.py ni main.py.
  </restricciones>

  Muéstrame el diff y espera el VoBo, después corre pytest, ruff, la caracterización "después", los diff y repite las pruebas de mas_vendidos: deben
  dar exactamente lo mismo. Dame el resumen y el mensaje de commit.
  ```

  ***Prompt R4 completo.**
  ```
  Vamos con R4 del PLAN.md
  <tarea>
  Renombra la variable global contadorVentas a contador_ventas en gestor.py declaración, reiniciar_sistema y registrar_venta y en almacen.py guardar_datos y cargar_datos
  </tarea>

  <antes_de_cambiar>
  - Corre la caracterización "antes".
  - Lista todas las apariciones de contadorVentas en src/ y tests/.
  </antes_de_cambiar>

  <restricciones>
  - La clave del JSON sigue siendo "contador"; no la cambies.
  - Cada función que asigna la variable debe declarar `global contador_ventas`.
  - No renombres nada más en este paso.
  </restricciones>

  Muéstrame el diff y espera mi VoBo. Después corre pytest, ruff, la caracterización "después" y los diff, y confirma que no queda ninguna referencia a contadorVentas en src/.
  Marca R4 como "Aplicado" en el PLAN.md y dame el mensaje de commit
  ```

**Prompt R5 Completo**
```
Vamos con R5 del PLAN.md: extraer las reglas de precio de src/gestor.py.

  <tarea>
  1. Crea constantes de negocio a nivel de módulo para los umbrales y tasas: descuento alto
     (1000 → 10 %), descuento medio (500 → 5 %), prefijo VIP "VIP", monto mínimo VIP (200),
     tasa VIP (2 %) e IVA (16 %).
  2. Extrae _descuento_por_volumen(subtotal) y _total_con_iva(base), y úsalas tanto en
     registrar_venta como en cotizar.
  3. Reemplaza los if anidados de la regla VIP por una sola condición:
     cliente and cliente.startswith(PREFIJO_VIP) and subtotal - descuento > MONTO_MINIMO_VIP
  4. Agrega docstrings a las funciones nuevas.
  </tarea>

  <antes_de_cambiar>
  - Corre la caracterización "antes" de la sección 9 del PLAN.md
  - Revisa la fila R5 de la sección 8 y explícame cómo tu diff evita cada riesgo (a) a (f)
  </antes_de_cambiar>

  <restricciones>
  - Los umbrales conservan exactamente sus operadores: >= 1000, >= 500 y > 200 (VIP)
  - El 2 % VIP se calcula sobre el subtotal, y la condición de los 200 se evalúa con el descuento por volumen ANTES de sumar el VIP
  - El IVA conserva el orden de operaciones: impuesto = base * TASA_IVA y total = round(base + impuesto, 2). Prohibido base * 1.16
  - Cuando no hay descuento, _descuento_por_volumen devuelve el entero 0, no 0.0
  - cotizar mantiene su firma cotizar(codigo, cantidad) y NO aplica VIP
  - No toques la validación, el ticket ni el registro de la venta (eso es R6)
  - No cambies el texto de ningún mensaje ni las claves del dict venta
  </restricciones>

  Muéstrame el diff, confirma punto por punto cada tarea y cada restricción, y espera mi VoBo
  Después corre pytest y ruff (esperado: 20 passed y 6 => 1), y la caracterización "después".
  ```

## 4. Variaciones de prompts e intentos fallidos
 - La primera versión de la evidencia se guardó en UTF-16 y en Github no se leía, por lo tanto se regeneró en UTF-8(commit `52cd6ed`)
 - **PLAN.MD**: Se intentó generar el archivo en `docs/` pero estaba protegido por la configuración, por lo que se generó en la raíz del proyecto. Claude no intento saltarse la reestricción y propuso 2 opciones:
    - Generar el plan en otra carpeta.
    - Modificar la configuración para permitir la escritura en `docs/`
Tome la opción de generarlo en otra ruta para seguir respetando la regla.
Evidencia: `docs/evidencia/img/03-plan_bloqueado_docs.png`
- **Pompt incompleto.** No pedí cuidar los tests y volví a generar el prompt integrando esa parte.
- **El plan se quedaba corto en R2.** El PLAN.md proponía `except (ValueError, OSError)`.
  Antes de aplicarlo le pedí a Claude explicar qué excepciones lanza `json.load`, y probó 7 casos de archivo corrupto con el código original. Encontró que un JSON con anidamiento muy profundo lanza `RecursionError`, que no es `ValueError`: con el plan tal cual, ese caso habría dejado de dar "archivo corrupto" y habría tronado el programa, sin que ningún test fallara. También confirmé que `open()` quedara fuera del `try`, para que los errores al abrir se sigan propagando como antes. 
  Evidencia: `docs/evidencia/R2_excepciones.md`.

## 5. Evidencia

| Paso | Archivo | Qué demuestra |
|---|---|---|
| 0 | `docs/evidencia/00_pytest_inicial.txt` | Línea base: 20 passed |
| 0 | `docs/evidencia/00_ruff_inicial.txt` | Línea base: 20 errores |
| 1 | `docs/evidencia/img/01-configuracion.PNG` |Prompt para la revisión de la configuración |
| 1 | `docs/evidencia/01-plan_configuracion_.md` | Informe de la revisión |
| 1 | `docs/evidencia/img/02-revision_de_configuracion_claude.PNG` | Tabla de hallazgos |
| 2 | `PLAN.md` | Plan de refactorización y explicación del proyecto  |
| 2 | `docs/evidencia/img/03-plan_bloqueado_docs.png` | Claude respeta la configuración |
| R0 | `docs/evidencia/R0_pytest.txt` | 20 passed después de R0 |
| R0 | `docs/evidencia/R0_ruff.txt` | 13 errores (antes 20) |
| R1 | `docs/evidencia/R1_pytest.txt` | 20 passed después de eliminar el código muerto |
| R1 | `docs/evidencia/R1_ruff.txt` | 11 errores (antes 13): se fueron N802 y SIM115 de `reporteViejoCSV` |
| R2 | `docs/evidencia/R2_pytest.txt` | 20 passed después de la persistencia segura |
| R2 | `docs/evidencia/R2_ruff.txt` | 7 errores (antes 11): se fueron SIM115 ×2, N802 y SIM103 |
| R2 | `docs/evidencia/R2_excepciones.md` | Los 7 casos de archivo corrupto dan el mismo resultado antes y después; `RecursionError` agregado |
| R3 | `docs/evidencia/R3_pytest.txt` | 20 passed después de simplificar los reportes |
| R3 | `docs/evidencia/R3_ruff.txt` | 7 errores (sin cambio: refactorización de legibilidad) |
|R4 | `docs/evidencia/R4_pytest.txt` | 20 passed después del renombre |
| R4 | `docs/evidencia/R4_ruff.txt` | 6 errores (antes 7): se fue N816 |
| R4 | docs/evidencia/R4_referencias.txt | No queda ningún `contadorVentas` en src/; la clave JSON `"contador"` sigue igual |
| R5 | `docs/evidencia/caracterizar_precios.py` | Script con 12 casos límite de descuentos, VIP e IVA |
| R5 | `docs/evidencia/R5_precios_antes.txt` | Precios, descuentos, IVA y tickets antes de R5 |
| R5 | `docs/evidencia/R5_precios_despues.txt` | Los mismos casos después de R5 |
| R5 | `docs/evidencia/R5_precios_diff.txt` | Antes y después son idénticos |
| R5 | `docs/evidencia/R5_pytest.txt` | 20 passed después de R5 |
| R5 | `docs/evidencia/R5_ruff.txt` | 1 error (antes 6): solo queda el C901 de `menu` |
