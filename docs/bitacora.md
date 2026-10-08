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
## 3. Refactorizaciones

| # | Prompt usado | Cambio realizado | Justificación | Tests OK | Ruff | Commit |
|---|---|---|---|---|---|---|

## 4. Variaciones de prompts e intentos fallidos
 - Tropiezo: La primera versión de la evidencia se guardó en UTF-16 y en Github no se leía, por lo tanto se regeneró en UTF-8(commit `52cd6ed`)
## 5. Evidencia

