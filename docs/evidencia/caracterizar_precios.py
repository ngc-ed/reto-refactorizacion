import sys

sys.path.insert(0, "src")
import gestor

casos = [
    (499.99, 1, ""), (500, 1, ""), (999.99, 1, ""), (1000, 1, ""),
    (21.50, 25, ""), (200, 1, "VIP01"), (200.01, 1, "VIP01"),
    (300, 1, "vip01"), (300, 1, "VI"), (300, 1, None),
    (500, 1, "VIP01"), (1000, 1, "VIP01"),
]
for precio, cantidad, cliente in casos:
    gestor.reiniciar_sistema()
    gestor.agregarProducto("X", "Prod", precio, 100)
    cot = gestor.cotizar("X", cantidad)
    v = gestor.registrar_venta("X", cantidad, cliente)
    print(f"precio={precio!r} cantidad={cantidad} cliente={cliente!r}")
    print(f"  subtotal={v['subtotal']!r} descuento={v['descuento']!r} "
          f"impuesto={v['impuesto']!r} total={v['total']!r} cotizar={cot!r}")
    print("  " + v["ticket"].replace("\n", " | "))