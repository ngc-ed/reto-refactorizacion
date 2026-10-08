# Reflexión

## Notas en curso (lecciones aprendidas durante el reto)

### 1. Configuración de Claude Code(Paso 1)
Escribí la configuración a mano, después pedí a Claude en modo plan que la revisará para mejorar la misma. Esto me demostró que siempre hay algo que mejorar, ya que pueden quedar huecos que quizá no vemos y que podrían afectar a futuro, como la ejecución de comandos no deseados.

### 2. Permisos de escritura de documentos bloqueados (Paso 2)
Le pedí que guardará el plan en `docs/` pero previamente había configurado para que esa carpeta no la pudiera modificar, lo que hizo que Claude no se saltará dicha regla y propuso algunas opciones.
Esto evidenció que siempre es bueno planear y configurar correctamente Claude.

### 3. Renombrar código (R4)
Al renombrar código también deja desactualizada la configuración: CLAUDE.md documentaba `contadorVentas`. Como el Claude no puede editar su propia configuración es necesario simpre estár actualizando el documento en casos necesarios.

---

## Reflexión final

**¿Qué tan útil fue Claude Code para detectar y corregir los problemas?**
Muy útil para diagnosticar, ya que con un prompt bien definido, mapeo y encontró los code smells, ejecutó pruebas y realizo recomendaciones que quiza a cualquier desarrollador le hubiera tomado más tiempo del que se llevó.

**¿Qué propuso la IA que yo no había notado?**
`RecursionError` en R2, el caso NaN en R6 y que `reporte_inventario()` y `resumen_ventas()` devuelven texto, lo que habría cerrado el menú en R7 si se ponían directo en el despacho.

**¿En qué casos tuve que corregir o rechazar sus sugerencias?**
Rechacé 3 sugerencias de configuración.
Ajusté el plan de R2.

**¿Qué técnicas de prompting funcionaron mejor?**
Las etiquetas `<tarea>`, `<antes_de_cambiar>` y `<restricciones>`, utilizando la técnica de delimitadores xml.
Chain-of-thought al pedir que explicará el proyecto y razonará como un error puede desencadenar una excepción.

**¿Qué delegaría y qué no?**
Delegaría el analisís del proyecto, pruebas, planeación del plan a implementar.
No delegaría la desición de aplicar el plan sin el VoBo, la revisión de los diff y los commits, ya que a fin de cuentas el desarrollador es responsable de su código.

**¿Qué aprendí sobre refactorizar con apoyo de IA?**
Que la IA ayuda en cuanto a la velocidad de codificar, pruebas y detección de código que pueda fallar cuando a un desarrollador le tomaría más tiempo. Y que a final de cuentas, la IA puede ser un buen ayudante si lo sabemos dirigir correctamente.
