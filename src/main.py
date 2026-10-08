"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"


def pedir_numero(mensaje):
    """Pide un número al usuario hasta que escriba algo válido y lo regresa."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def _opcion_agregar():
    """Opción 1: da de alta un producto."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_vender():
    """Opción 2: registra una venta e imprime su ticket."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_cotizar():
    """Opción 3: muestra el total estimado de una compra sin registrarla."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        print("Error:", gestor.ultimo_error)


def _opcion_reporte_inventario():
    """Opción 4: imprime el reporte de inventario."""
    reportes.reporte_inventario()


def _opcion_resumen_ventas():
    """Opción 5: imprime el resumen de ventas."""
    reportes.resumen_ventas()


def _opcion_mas_vendidos():
    """Opción 6: imprime los productos más vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def _opcion_stock_bajo():
    """Opción 7: imprime las alertas de productos con stock bajo."""
    bajos = reportes.productos_stock_bajo()
    if len(bajos) == 0:
        print("No hay productos con stock bajo.")
    else:
        for producto in bajos:
            print(
                "OJO:", producto["nombre"], "solo tiene", producto["stock"], "unidades"
            )


def _opcion_guardar_y_salir():
    """Opción 8: guarda los datos y regresa True para terminar el menú."""
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")
    return True


# Cada opción regresa None para seguir en el menú; solo la 8 regresa True (salir).
OPCIONES = {
    "1": _opcion_agregar,
    "2": _opcion_vender,
    "3": _opcion_cotizar,
    "4": _opcion_reporte_inventario,
    "5": _opcion_resumen_ventas,
    "6": _opcion_mas_vendidos,
    "7": _opcion_stock_bajo,
    "8": _opcion_guardar_y_salir,
}


def _mostrar_menu():
    """Imprime las opciones del menú."""
    print("")
    print("1) Agregar producto")
    print("2) Registrar venta")
    print("3) Cotizar")
    print("4) Reporte de inventario")
    print("5) Resumen de ventas")
    print("6) Mas vendidos")
    print("7) Alertas de stock bajo")
    print("8) Guardar y salir")


def menu():
    """Carga los datos si existen y atiende el menú hasta que se elige salir."""
    print("Bienvenido al gestor de la tienda La Esquina")
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)
    while True:
        _mostrar_menu()
        opcion = input("Opcion: ")
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opcion no valida.")
        elif accion():
            break


if __name__ == "__main__":
    menu()
