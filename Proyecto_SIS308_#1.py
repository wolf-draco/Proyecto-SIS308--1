"""Sistema de control de inventario."""

import json
from datetime import datetime
from pathlib import Path

ARCHIVO = Path(__file__).with_name("inventario.json")


class Producto:
    def __init__(self, codigo, nombre, precio, stock, stock_minimo=5):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.stock_minimo = stock_minimo

    def a_dict(self):
        return self.__dict__

    def bajo_minimo(self):
        return self.stock <= self.stock_minimo


class Inventario:
    def __init__(self):
        self.productos = {}
        self.ventas = []
        self.cargar()

    def cargar(self):
        if not ARCHIVO.exists():
            return

        try:
            with ARCHIVO.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return

        for producto in datos.get("productos", []):
            self.productos[producto["codigo"]] = Producto(**producto)
        self.ventas = datos.get("ventas", [])

    def guardar(self):
        datos = {
            "productos": [p.a_dict() for p in self.productos.values()],
            "ventas": self.ventas,
        }
        with ARCHIVO.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)

    def registrar(self, codigo, nombre, precio, stock, minimo):
        codigo = codigo.strip()
        nombre = nombre.strip()
        if not codigo or not nombre:
            return "Error: código y nombre son obligatorios."
        if codigo in self.productos:
            return "Error: ya existe un producto con ese código."
        if stock < 0 or minimo < 0:
            return "Error: stock y mínimo no pueden ser negativos."

        self.productos[codigo] = Producto(codigo, nombre, precio, stock, minimo)
        self.guardar()
        return "Producto registrado correctamente."

    def reponer(self, codigo, cantidad):
        if codigo not in self.productos:
            return "Error: producto no encontrado."
        if cantidad <= 0:
            return "Error: la cantidad debe ser mayor que cero."
        self.productos[codigo].stock += cantidad
        self.guardar()
        return "Stock actualizado."

    def vender(self, codigo, cantidad):
        producto = self.productos.get(codigo)
        if producto is None:
            return "Error: producto no encontrado."
        if cantidad <= 0:
            return "Error: la cantidad debe ser mayor que cero."
        if cantidad > producto.stock:
            return f"Error: stock insuficiente (disponible: {producto.stock})."

        producto.stock -= cantidad
        total = producto.precio * cantidad
        self.ventas.append(
            {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "codigo": codigo,
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "total": total,
            }
        )
        self.guardar()
        aviso = "  ¡ALERTA: stock bajo!" if producto.bajo_minimo() else ""
        return f"Venta registrada. Total: Bs {total:.2f}{aviso}"

    def eliminar(self, codigo):
        if codigo not in self.productos:
            return "Error: producto no encontrado."
        del self.productos[codigo]
        self.guardar()
        return "Producto eliminado."


def leer_numero(msg, tipo=float, minimo=0):
    while True:
        try:
            valor = tipo(input(msg))
            if valor < minimo:
                print(f"  El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("  Entrada inválida, intente de nuevo.")


def mostrar_productos(inv):
    if not inv.productos:
        print("\n  (No hay productos registrados)")
        return

    print(f"\n{'Código':<8}{'Nombre':<22}{'Precio':>9}{'Stock':>8}{'Mín':>6}")
    print("-" * 53)
    for producto in inv.productos.values():
        marca = " *" if producto.bajo_minimo() else ""
        print(
            f"{producto.codigo:<8}{producto.nombre:<22}{producto.precio:>9.2f}"
            f"{producto.stock:>8}{producto.stock_minimo:>6}{marca}"
        )
    print("(* = stock bajo)")


def reporte_ventas(inv):
    if not inv.ventas:
        print("\n  (Aún no hay ventas)")
        return

    print(f"\n{'Fecha':<18}{'Producto':<20}{'Cant':>6}{'Total':>10}")
    print("-" * 54)
    for venta in inv.ventas:
        print(f"{venta['fecha']:<18}{venta['nombre']:<20}{venta['cantidad']:>6}{venta['total']:>10.2f}")
    print(f"\nTOTAL VENDIDO: Bs {sum(venta['total'] for venta in inv.ventas):.2f}")


def menu():
    print(
        """
=== CONTROL DE INVENTARIO ===
1. Registrar producto
2. Ver productos
3. Reponer stock
4. Registrar venta
5. Reporte de ventas
6. Eliminar producto
0. Salir
"""
    )


def main():
    inv = Inventario()
    while True:
        menu()
        opcion = input("Opción: ").strip()

        if opcion == "1":
            codigo = input("Código: ").strip()
            nombre = input("Nombre: ").strip()
            if not codigo or not nombre:
                print("Código y nombre son obligatorios.")
                continue

            precio = leer_numero("Precio (Bs): ")
            stock = leer_numero("Stock inicial: ", int)
            minimo = leer_numero("Stock mínimo: ", int)
            print(inv.registrar(codigo, nombre, precio, stock, minimo))
        elif opcion == "2":
            mostrar_productos(inv)
        elif opcion == "3":
            codigo = input("Código: ").strip()
            cantidad = leer_numero("Cantidad a agregar: ", int, 1)
            print(inv.reponer(codigo, cantidad))
        elif opcion == "4":
            codigo = input("Código: ").strip()
            cantidad = leer_numero("Cantidad a vender: ", int, 1)
            print(inv.vender(codigo, cantidad))
        elif opcion == "5":
            reporte_ventas(inv)
        elif opcion == "6":
            print(inv.eliminar(input("Código: ").strip()))
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()