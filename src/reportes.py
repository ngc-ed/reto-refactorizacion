"""Reportes de la tienda: inventario, ventas y mas vendidos."""


import gestor

STOCK_MINIMO = 5


def formatear_dinero(valor):
    """Da formato de dinero a un número: "$" seguido del valor redondeado."""
    return "$" + str(round(valor, 2))


def productos_stock_bajo():
    """Regresa la lista de productos con stock por debajo del minimo."""
    bajos = []
    for producto in gestor.INVENTARIO.values():
        if producto["stock"] < STOCK_MINIMO:
            bajos.append(producto)
    return bajos


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    texto = "===== INVENTARIO =====\n"
    valor_total = 0
    for p in gestor.INVENTARIO.values():
        linea = (
            f"{p['codigo']} | {p['nombre']} | "
            f"{formatear_dinero(p['precio'])} | stock: {p['stock']}"
        )
        if p["stock"] < STOCK_MINIMO:
            linea += "  <-- STOCK BAJO"
        texto += f"{linea}\n"
        valor_total = valor_total + p["precio"] * p["stock"]
    texto += f"Valor total del inventario: {formatear_dinero(valor_total)}\n"
    print(texto)
    return texto


def total_vendido():
    """Suma el total (con IVA) de todas las ventas registradas."""
    t = 0
    for v in gestor.VENTAS:
        t = t + v["total"]
    return round(t, 2)


def mas_vendidos(n=3):
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades = {}
    for v in gestor.VENTAS:
        if v["codigo"] in unidades:
            unidades[v["codigo"]] = unidades[v["codigo"]] + v["cantidad"]
        else:
            unidades[v["codigo"]] = v["cantidad"]
    # sorted es estable: los empates conservan el orden de la primera venta
    ranking = sorted(unidades.items(), key=lambda par: par[1], reverse=True)
    return ranking[:n]


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    texto = "===== RESUMEN DE VENTAS =====\n"
    total = 0
    for v in gestor.VENTAS:
        texto += (
            f"Folio {v['folio']}: {v['nombre']} x{v['cantidad']} = "
            f"{formatear_dinero(v['total'])}\n"
        )
        total = total + v["total"]
    texto += f"Numero de ventas: {len(gestor.VENTAS)}\n"
    texto += f"Total del dia: {formatear_dinero(total)}\n"
    print(texto)
    return texto
