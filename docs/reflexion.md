# Reflexión

## Notas en curso (lecciones aprendidas durante el reto)

### 1. La configuración también hay que revisarla y probarla (Paso 1)

Escribí la configuración a mano pensando que con eso Claude ya no podría tocar los
tests. Cuando le pedí que la revisara, encontró cosas que yo no había visto: el
comando que puse para correr la app arrancaba sin datos, el `CLAUDE.md` se
contradecía con la línea base de ruff y, lo más importante, mis permisos solo
bloqueaban la edición "normal" de archivos. Con un comando de terminal se podían
modificar los tests igual, y yo solo había bloqueado `git push` en Bash cuando mi
terminal es PowerShell.

Lo que más me gustó fue comprobar que sí funcionaba lo que había bloqueado bien:
cuando le pedí aplicar los cambios, no pudo escribir en `CLAUDE.md` ni en `.claude/`
y tuvo que dejarme los archivos para que yo los revisara y copiara.

Lo que me llevo:
- El `CLAUDE.md` *pide*, los permisos *impiden*, y aun así hay huecos. Las defensas
  van en capas: permisos + hooks + revisar yo el diff.
- Que el mismo agente revise su configuración en modo plan es barato y encuentra cosas
  reales. Pero la decisión de qué aceptar fue mía: rechacé 3 sugerencias porque
  chocaban con las reglas del reto o con lo que quiero hacer después.
- Tenía activado "auto mode" sin darme cuenta. Eso contradice mi propia regla de
  aprobar cada diff. ‹qué hiciste al respecto›

### 2. ‹siguiente lección›

---

## Reflexión final (10–15 líneas; se escribe al terminar)

**¿Qué tan útil fue Claude Code para detectar y corregir los problemas?**

**¿Qué propuso la IA que yo no había notado?**

**¿En qué casos tuve que corregir o rechazar sus sugerencias?**

**¿Qué técnicas de prompting funcionaron mejor?**

**¿Qué delegaría y qué no delegaría, y por qué?**

**¿Qué aprendí sobre refactorizar con apoyo de IA?**