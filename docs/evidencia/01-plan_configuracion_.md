# Revisión de configuración para el reto de refactorización

## Contexto
Revisé `CLAUDE.md`, `.claudeignore` y `.claude/settings.json` para ver si sirven para refactorizar `src/` sin cambiar el comportamiento y sin tocar `tests/` ni `pyproject.toml`. **No modifiqué ningún archivo.** Lo que comprobé en el repositorio:

- Hay 20 tests (3 en almacen, 13 en gestor, 4 en reportes). La lista de API de `CLAUDE.md` coincide con la que usan los tests.
- `datos_ejemplo.json` está en la **raíz** del repo, no en `src/`.
- `main.py` usa `ARCHIVO = "datos_ejemplo.json"` (ruta relativa) y también lo **sobrescribe** en la opción de guardar (línea 78). Ese archivo está versionado en git.
- `main.py` llama a `almacen.hayArchivo`, que no está en snake_case y no aparece en la lista de API protegida.
- `CLAUDE.md`, `.claudeignore` y `.claude/` todavía no están versionados (`??` en git status).

## Hallazgos

| archivo | línea | problema | sugerencia |
|---|---|---|---|
| CLAUDE.md | 18 | `cd src && python main.py` no encuentra `datos_ejemplo.json`, porque está en la raíz. La app arranca vacía sin avisar. Además, `&&` no funciona en PowerShell 5.1, que es el shell principal. | Cambiar a: "Desde la raíz: `python src/main.py`". |
| CLAUDE.md | 18 | Si se usa la opción guardar del menú, se sobrescribe `datos_ejemplo.json`, que está versionado. Ese cambio puede acabar en un commit. | Añadir: "No commitear cambios a `datos_ejemplo.json`; restaurar con `git restore datos_ejemplo.json` después de probar la app". |
| CLAUDE.md | 10 vs 16 | Hay una contradicción. La línea 10 dice que pytest y ruff "deben pasar" después de cada refactorización, pero la línea 16 dice que la línea base de ruff es 20 errores. Las primeras refactorizaciones no pueden dejar ruff en 0. | Redactar como: "pytest siempre 20/20 en verde; el número de errores de ruff nunca aumenta; al final del PR debe ser 0". |
| CLAUDE.md | 15–17 | Los comandos dan por hecho que `.venv` está activado. La sesión de Claude Code no lo activa sola, así que `pytest` o `ruff` pueden no encontrarse o usar otra versión. | Usar `.venv\Scripts\python -m pytest -q` y `.venv\Scripts\python -m ruff check src`, o indicar que hay que activar el venv antes de abrir `claude`. |
| CLAUDE.md | 17 | No se prohíbe `ruff format`. Si se ejecuta, reformatea archivos completos y rompe los commits atómicos. | Añadir: "No ejecutar `ruff format` sobre archivos completos"; y revisar con `ruff check src --diff` antes de usar `--fix`. |
| CLAUDE.md | 11 | El contrato menciona nombre y firma, pero no **valores de retorno**: `False`/`None` y el texto de `ultimo_error`, que los tests y `main.py` comprueban. Tampoco menciona `almacen.hayArchivo`, que usa `main.py`. | Cambiar a "nombre, firma, valores de retorno y mensajes de `ultimo_error`". Aclarar que si se renombra `hayArchivo` hay que actualizar `main.py` en el mismo commit. |
| CLAUDE.md | 14–18 | Los tests no cubren `main.py`, el texto del ticket ni `resumen_ventas`, aunque la línea 35 los define como comportamiento observable. No hay ninguna forma indicada de comprobarlos. | Añadir un paso de caracterización: guardar la salida antes y después (por ejemplo, pasar una secuencia fija de entradas a `python src/main.py` y comparar con `diff`) cuando la refactorización toque reportes, ticket o `main.py`. |
| CLAUDE.md | 36 | Lista el código muerto, pero no dice qué hacer con él. | Indicar de forma explícita: "Se puede eliminar, en un commit propio `refactor(...): elimina código muerto ...`". |
| CLAUDE.md | 12 vs 17 | La línea 12 dice que los cambios cosméticos no cuentan, pero la línea 17 permite `--fix` para cambios triviales. No queda claro cómo se registran esos arreglos. | Indicar que los arreglos triviales de ruff van juntos en un commit aparte, que no cuenta como refactorización. |
| CLAUDE.md | 47 | La lista de tipos (feat, fix, refactor, test, docs) no incluye `chore`/`style`, pero el historial ya usa `chore:`. Hay erratas: "commmits" y "menos a" (debería ser "menor a"). No se dice si el límite de 100 caracteres aplica solo al título. | Añadir `chore` y `style`, corregir las erratas, decir "primera línea < 100 caracteres" y listar los alcances válidos: gestor, almacen, reportes, main, claude. |
| CLAUDE.md | 56 | Dice "Propon" (debería ser "Propón"). La regla dice que el usuario hace los commits, pero `settings.json` solo bloquea `git push`, no `git commit`. | Corregir la errata y bloquear también `git commit` en settings (ver más abajo). |
| CLAUDE.md | 60 | La regla "Sin edición de `docs/`" no se aplica en `settings.json`. | Añadir `Edit(./docs/**)` a `deny`. |
| CLAUDE.md | — | `CLAUDE.md`, `.claudeignore` y `.claude/settings.json` no están versionados, así que no llegan al PR. | Commitearlos al inicio de la rama (`docs(claude): ...` / `chore(claude): ...`). |
| .claudeignore | 1–14 | Que yo sepa, Claude Code **no lee** `.claudeignore`. Lo que se aplica de verdad es `permissions.deny` en `settings.json`. El archivo da una falsa sensación de protección. | Tratarlo solo como documentación, o eliminarlo y dejar todo en `settings.json`. |
| .claudeignore | 3, 5 | `venv/` y `*.pyc` no tienen su equivalente en `settings.json`, que solo bloquea `.venv` y `__pycache__`. | Mantener los dos archivos alineados: añadir `Read(./venv/**)` y `Read(./**/*.pyc)` a settings. |
| .claudeignore | — | Faltan `.DS_Store` y `__MACOSX/`, que sí están en `.gitignore`. | Añadirlos para que sea coherente con `.gitignore`. |
| .claude/settings.json | 12–15 | Los archivos de tests están listados uno por uno, así que un test nuevo o un `tests/__init__.py` no quedaría protegido. | Usar `Edit(./tests/**)` en su lugar. |
| .claude/settings.json | 12–20 | `deny` solo cubre las herramientas Edit y Read. Se puede saltar con Bash o PowerShell, por ejemplo `sed -i`, `Set-Content`, `git checkout -- tests/`, `git restore` o `ruff format tests`. | Añadir un hook `PreToolUse` que bloquee cualquier comando que escriba en `tests/` o `pyproject.toml`. Como mínimo, bloquear `Bash(git checkout:*)`, `Bash(git restore:*)`, `Bash(git reset:*)` y `Bash(ruff format:*)`. |
| .claude/settings.json | 20 | Solo se bloquea `Bash(git push:*)`. Falta `git commit`, que según la línea 56 de `CLAUDE.md` lo hace el usuario. Tampoco hay reglas equivalentes para la herramienta PowerShell, que es el shell principal. | Añadir `Bash(git commit:*)`, `PowerShell(git push*)` y `PowerShell(git commit*)`. |
| .claude/settings.json | 18 | `Edit(./CLAUDE.md)` impide que Claude complemente `CLAUDE.md`, que es justo lo que se pide, y entra en conflicto con el ejemplo `docs(claude): agrega regla...`. | Si se quiere que Claude solo proponga los cambios, dejarlo y documentarlo. Si no, quitarlo, o pasarlo a `ask` en vez de `deny`. |
| .claude/settings.json | 3–21 | Falta `Edit(./docs/**)` (`CLAUDE.md` línea 60) y `Edit(./datos_ejemplo.json)`, que son datos de ejemplo versionados. | Añadir esas dos reglas a `deny`. |
| .claude/settings.json | 9–10 | `Read(./.env)` solo cubre la raíz del repo. | Usar `Read(./**/.env)` y `Read(./**/.env.*)`. |
| .claude/settings.json | 2 | No hay bloque `allow`. `pytest` y `ruff` se ejecutan después de cada cambio, así que cada vez pedirán permiso. | Añadir `allow` con `Bash(python -m pytest:*)`, `Bash(python -m ruff check:*)`, `Bash(git diff:*)`, `Bash(git status:*)` y sus equivalentes en PowerShell. |
| .claude/settings.json | — | No hay `hooks`. La regla "correr pytest y ruff tras cada cambio" depende de que el modelo se acuerde. | Añadir un hook `PostToolUse` con matcher `Edit\|Write` sobre `src/**` que ejecute `python -m pytest -q` y `python -m ruff check src --statistics`. |
| .claude/settings.json | 1 | Falta `$schema`, así que el editor no valida el archivo. | Añadir `"$schema": "https://json.schemastore.org/claude-code-settings.json"`. |

## Siguiente paso (si se aprueba)
Ninguno de los archivos revisados se modifica. El informe es la tabla de arriba. Si después quieres aplicar los cambios, `CLAUDE.md` y `.claude/**` están en `deny`, así que tendrás que editarlos tú o quitar temporalmente esas reglas.

## Hallazgos NO aceptados
- Eliminar .claudeignore porque Claude Code no lo lee
- Cambiar los tests listados uno por uno por Edit(./tests/**)
- Edit(./CLAUDE.md) impide complementar el CLAUDE.md