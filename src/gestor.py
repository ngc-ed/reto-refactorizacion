"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""

# ---------------------------------------------------------------
# Reglas de precio
# ---------------------------------------------------------------
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_VIP = 0.02
TASA_IVA = 0.16


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    x = {}
    x["codigo"] = codigo
    x["nombre"] = nombre
    x["precio"] = precio
    x["stock"] = stock
    INVENTARIO[codigo] = x
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    aux = INVENTARIO[codigo]["stock"] + cantidad
    if aux < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = aux
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    temp2 = []
    for k in INVENTARIO:
        if texto.lower() in INVENTARIO[k]["nombre"].lower():
            temp2.append(INVENTARIO[k])
    return temp2


def _descuento_por_volumen(subtotal):
    """Calcula el descuento por volumen de compra; 0 si no aplica."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _calcular_iva(base):
    """Calcula el IVA de la base y el total redondeado: (impuesto, total)."""
    impuesto = base * TASA_IVA
    return impuesto, round(base + impuesto, 2)


def _total_con_iva(base):
    """Suma el IVA a la base y redondea el total a 2 decimales."""
    return _calcular_iva(base)[1]


def _validar_venta(codigo, cantidad):
    """Regresa el motivo por el que la venta no procede, o None si es válida."""
    if codigo is None or codigo == "":
        return "codigo vacio"
    if codigo not in INVENTARIO:
        return "producto no existe"
    # no usar "<= 0": con NaN cambiaria el mensaje a "stock insuficiente"
    if cantidad is None or not (cantidad > 0):
        return "cantidad invalida"
    if INVENTARIO[codigo]["stock"] >= cantidad:
        return None
    return "stock insuficiente"


def _armar_ticket(venta, hubo_descuento):
    """Arma el ticket en texto plano; la línea Descuento solo si hubo descuento."""
    ticket = "TIENDA LA ESQUINA\n"
    ticket += "----------------------------\n"
    ticket += "Folio: " + str(venta["folio"]) + "\n"
    ticket += venta["nombre"] + " x" + str(venta["cantidad"]) + "\n"
    ticket += "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if hubo_descuento:
        ticket += "Descuento: -$" + str(venta["descuento"]) + "\n"
    ticket += "IVA: $" + str(venta["impuesto"]) + "\n"
    ticket += "TOTAL: $" + str(venta["total"]) + "\n"
    return ticket


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta y la regresa; None si falla (motivo en ultimo_error).

    Valida antes de tocar el estado: si la venta no procede, no cambia el
    stock, el folio ni la lista de ventas.
    """
    global contador_ventas, ultimo_error
    error = _validar_venta(codigo, cantidad)
    if error is not None:
        ultimo_error = error
        return None
    producto = INVENTARIO[codigo]
    subtotal = producto["precio"] * cantidad
    descuento = _descuento_por_volumen(subtotal)
    # los clientes cuyo codigo empieza con VIP tienen un extra sobre el
    # subtotal, pero solo si su compra (ya con descuento) pasa de cierto monto
    es_vip = cliente and cliente.startswith(PREFIJO_VIP)
    if es_vip and subtotal - descuento > MONTO_MINIMO_VIP:
        descuento = descuento + subtotal * TASA_VIP
    base = subtotal - descuento
    impuesto, total = _calcular_iva(base)
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {
        "folio": contador_ventas,
        "codigo": codigo,
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "subtotal": round(subtotal, 2),
        "descuento": round(descuento, 2),
        "impuesto": round(impuesto, 2),
        "total": total,
        "cliente": cliente,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    venta["ticket"] = _armar_ticket(venta, descuento > 0)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    aux = INVENTARIO[codigo]["precio"] * cantidad
    base = aux - _descuento_por_volumen(aux)
    return _total_con_iva(base)
