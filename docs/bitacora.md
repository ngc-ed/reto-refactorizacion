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

## 4. Variaciones de prompts e intentos fallidos
 - La primera versión de la evidencia se guardó en UTF-16 y en Github no se leía, por lo tanto se regeneró en UTF-8(commit `52cd6ed`)
 - **PLAN.MD**: Se intentó generar el archivo en `docs/` pero estaba protegido por la configuración, por lo que se generó en la raíz del proyecto. Claude no intento saltarse la reestricción y propuso 2 opciones:
    - Generar el plan en otra carpeta.
    - Modificar la configuración para permitir la escritura en `docs/`
Tome la opción de generarlo en otra ruta para seguir respetando la regla.
Evidencia: `docs/evidencia/img/03-plan_bloqueado_docs.png`
- **Pompt incompleto.** No pedí cuidar los tests y volví a generar el prompt integrando esa parte.

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

