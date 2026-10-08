# R2 — Excepciones de `json.load` con un archivo corrupto

Análisis previo a cambiar `except Exception` en `almacen.cargar_datos` (refactorización R2 de `PLAN.md`). Las pruebas se corrieron sobre el código **antes** del cambio.

## Qué excepciones lanza `json.load` con un archivo corrupto

`json.load(f)` equivale a `json.loads(f.read())`, así que puede fallar en dos momentos: al **leer** el archivo y al **interpretar** el JSON. Esto es lo que salió al probarlo:

| caso | excepción | ¿es `ValueError`? | resultado actual |
|---|---|---|---|
| sintaxis inválida (`{,}`) | `JSONDecodeError` | Sí (subclase) | False / "archivo corrupto" |
| archivo vacío | `JSONDecodeError` | Sí | False / "archivo corrupto" |
| bytes que no son UTF-8 | `UnicodeDecodeError` (al leer) | Sí (subclase) | False / "archivo corrupto" |
| UTF-8 con BOM | `JSONDecodeError` | Sí | False / "archivo corrupto" |
| entero de más de 4300 dígitos | `ValueError` | Sí | False / "archivo corrupto" |
| anidamiento muy profundo (`[[[…]]]`) | **`RecursionError`** | **No** (es `RuntimeError`) | False / "archivo corrupto" |
| la ruta es una carpeta | `PermissionError`, lanzado por `open()` | — | **se propaga** (está fuera del `try`) |

**Conclusión:**
- **`ValueError`** cubre 5 de los 6 casos.
- **`RecursionError`** también hace falta. El plan solo decía `(ValueError, OSError)`, pero sin `RecursionError` un JSON muy anidado empezaría a lanzar una excepción en lugar de devolver "archivo corrupto". Es un cambio de comportamiento y ningún test lo detectaría.

## ¿Va `OSError` en el except?

Sí:
- Hoy la lectura (`f.read()`, dentro de `json.load`) ocurre **dentro** del `try`, así que un error de E/S al leer acaba en "archivo corrupto". Para conservar ese comportamiento, `OSError` debe seguir atrapándose.
- No es para los errores de `open()`: `open()` sigue **fuera** del `try` y sus errores siguen propagándose. El caso "carpeta" lo comprueba.

## Lo que se deja de atrapar

`except Exception` sí atrapaba `MemoryError` y cualquier fallo de programación como `TypeError` o `AttributeError`. No vienen de un archivo corrupto sino de falta de memoria o de bugs, así que es preferible que se vean.

## Decisión aplicada

```python
with open(ruta, encoding="utf-8") as f:
    try:
        d = json.load(f)
    except (ValueError, RecursionError, OSError):
        gestor.ultimo_error = "archivo corrupto"
        return False
```
