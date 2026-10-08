import re
import sys

sys.path.insert(0, "src")
import gestor


def preparar():
    gestor.reiniciar_sistema()
    gestor.agregarProducto("A1", "Prod A", 12.5, 5)


def estado():
    return (f"ultimo_error={gestor.ultimo_error!r} stock={gestor.INVENTARIO['A1']['stock']} "
            f"ventas={len(gestor.VENTAS)} folio={gestor.contador_ventas}")


print("== registrar_venta con datos invalidos (orden de validaciones)")
errores = [("", 1), (None, 1), ("ZZZ", 1), ("A1", 0), ("A1", -2), ("A1", None),
           ("A1", 6), (None, 0), ("", 99), ("ZZZ", 0), ("ZZZ", 99), ("A1", 0.0)]
for codigo, cantidad in errores:
    preparar()
    r = gestor.registrar_venta(codigo, cantidad)
    print(f"registrar_venta({codigo!r}, {cantidad!r}) -> {r!r} | {estado()}")

print("== cotizar con datos invalidos (conserva su propia validacion)")
for codigo, cantidad in errores:
    preparar()
    r = gestor.cotizar(codigo, cantidad)
    print(f"cotizar({codigo!r}, {cantidad!r}) -> {r!r} | ultimo_error={gestor.ultimo_error!r}")

print("== venta exitosa despues de un error (ultimo_error no se limpia)")
preparar()
gestor.registrar_venta("A1", 0)
v = gestor.registrar_venta("A1", 5, "VIP01")
print(estado())
print("claves:", list(v.keys()))
print("fecha con formato correcto:", bool(re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", v["fecha"])))
print("tipos:", {k: type(val).__name__ for k, val in v.items() if k != "fecha"})
print("ticket:", repr(v["ticket"]))

print("== dos ventas seguidas (folios y stock)")
preparar()
v1 = gestor.registrar_venta("A1", 2)
v2 = gestor.registrar_venta("A1", 3, "VIP01")
print(v1["folio"], v2["folio"], estado())
print("ticket 2:", repr(v2["ticket"]))