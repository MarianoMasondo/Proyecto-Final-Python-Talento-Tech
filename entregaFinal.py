import sqlite3
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)


# ------------------------------------------------------------
# CONEXIÓN Y CREACIÓN DE TABLA
# ------------------------------------------------------------

def conectar_db():
    """
    Conecta con la base de datos inventario.db.
    Si la tabla productos no existe, la crea.
    """

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL CHECK(precio > 0),
            cantidad INTEGER NOT NULL CHECK(cantidad >= 0),
            fecha_registro TEXT NOT NULL
        )
    """)

    conexion.commit()
    return conexion


# ------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN
# ------------------------------------------------------------

def pedir_texto(mensaje, campo):
    """
    Pide un texto al usuario y valida que no esté vacío.
    """

    while True:
        texto = input(mensaje).strip()

        if texto:
            return texto

        print(Fore.RED + f"❌ El campo {campo} no puede estar vacío.")


def pedir_precio():
    """
    Pide un precio y valida que sea un número mayor a cero.
    """

    while True:
        try:
            precio = float(input(" Precio: $").replace(",", "."))

            if precio > 0:
                return precio

            print(Fore.RED + "❌ El precio debe ser mayor a 0.")

        except ValueError:
            print(Fore.RED + "❌ Ingresá un número válido. Ejemplo: 1200.50")


def pedir_cantidad():
    """
    Pide una cantidad y valida que sea un número entero mayor o igual a cero.
    """

    while True:
        try:
            cantidad = int(input(" Cantidad: "))

            if cantidad >= 0:
                return cantidad

            print(Fore.RED + "❌ La cantidad no puede ser negativa.")

        except ValueError:
            print(Fore.RED + "❌ La cantidad debe ser un número entero.")


# ------------------------------------------------------------
# OPERACIONES CRUD
# ------------------------------------------------------------

def agregar_producto(conexion):
    """
    Agrega un nuevo producto a la base de datos.
    """

    print(Fore.CYAN + "\n--- Nuevo producto ---")

    nombre = pedir_texto(" Nombre: ", "nombre").capitalize()
    categoria = pedir_texto(" Categoría: ", "categoría").capitalize()
    precio = pedir_precio()
    cantidad = pedir_cantidad()
    fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO productos (nombre, categoria, precio, cantidad, fecha_registro)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, categoria, precio, cantidad, fecha_registro))

        conexion.commit()
        print(Fore.GREEN + f"✅ Producto '{nombre}' agregado correctamente.")

    except sqlite3.Error as error:
        conexion.rollback()
        print(Fore.RED + f"❌ Error al guardar el producto: {error}")


def ver_productos(conexion):
    """
    Muestra todos los productos guardados en la base de datos.
    """

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT id, nombre, categoria, precio, cantidad, fecha_registro
            FROM productos
            ORDER BY id
        """)

        filas = cursor.fetchall()

        if not filas:
            print(Fore.YELLOW + "\nNo hay productos cargados.")
            return

        print(Fore.CYAN + "\n" + "-" * 100)
        print(f"{'ID':<5} {'NOMBRE':<20} {'CATEGORÍA':<15} {'PRECIO':>12} {'CANTIDAD':>10} {'FECHA':>25}")
        print("-" * 100)

        for id_, nombre, categoria, precio, cantidad, fecha in filas:
            print(f"{id_:<5} {nombre:<20} {categoria:<15} ${precio:>11.2f} {cantidad:>10} {fecha:>25}")

        print("-" * 100)
        print(Fore.GREEN + f"Total de productos: {len(filas)}")

    except sqlite3.Error as error:
        print(Fore.RED + f"❌ Error al consultar productos: {error}")


def buscar_producto(conexion):
    """
    Busca productos por nombre.
    """

    termino = input("\nIngresá el nombre a buscar: ").strip()

    if not termino:
        print(Fore.RED + "❌ El término de búsqueda no puede estar vacío.")
        return

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT id, nombre, categoria, precio, cantidad, fecha_registro
            FROM productos
            WHERE nombre LIKE ?
            ORDER BY id
        """, (f"%{termino}%",))

        filas = cursor.fetchall()

        if not filas:
            print(Fore.YELLOW + f"No se encontraron productos con el nombre '{termino}'.")
            return

        print(Fore.CYAN + f"\nSe encontraron {len(filas)} resultado(s):")

        for id_, nombre, categoria, precio, cantidad, fecha in filas:
            print(f"ID: {id_} | {nombre} | {categoria} | ${precio:.2f} | Stock: {cantidad} | Fecha: {fecha}")

    except sqlite3.Error as error:
        print(Fore.RED + f"❌ Error al buscar producto: {error}")


def actualizar_producto(conexion):
    """
    Actualiza los datos de un producto existente.
    """

    ver_productos(conexion)

    try:
        id_actualizar = int(input("\nIngresá el ID del producto a actualizar: ").strip())

    except ValueError:
        print(Fore.RED + "❌ El ID debe ser un número entero.")
        return

    cursor = conexion.cursor()

    cursor.execute("SELECT nombre FROM productos WHERE id = ?", (id_actualizar,))
    fila = cursor.fetchone()

    if not fila:
        print(Fore.RED + f"❌ No existe ningún producto con el ID {id_actualizar}.")
        return

    nombre_actual = fila[0]

    print(Fore.CYAN + f"\nProducto seleccionado: {nombre_actual}")
    print("Dejá el campo vacío si no querés modificar ese dato.")

    nuevo_nombre = input(" Nuevo nombre: ").strip()
    nueva_categoria = input(" Nueva categoría: ").strip()
    nuevo_precio_texto = input(" Nuevo precio: $").strip().replace(",", ".")
    nueva_cantidad_texto = input(" Nueva cantidad: ").strip()

    try:
        if nuevo_nombre:
            cursor.execute(
                "UPDATE productos SET nombre = ? WHERE id = ?",
                (nuevo_nombre.capitalize(), id_actualizar)
            )

        if nueva_categoria:
            cursor.execute(
                "UPDATE productos SET categoria = ? WHERE id = ?",
                (nueva_categoria.capitalize(), id_actualizar)
            )

        if nuevo_precio_texto:
            nuevo_precio = float(nuevo_precio_texto)

            if nuevo_precio <= 0:
                print(Fore.RED + "❌ El precio debe ser mayor a 0.")
                conexion.rollback()
                return

            cursor.execute(
                "UPDATE productos SET precio = ? WHERE id = ?",
                (nuevo_precio, id_actualizar)
            )

        if nueva_cantidad_texto:
            nueva_cantidad = int(nueva_cantidad_texto)

            if nueva_cantidad < 0:
                print(Fore.RED + "❌ La cantidad no puede ser negativa.")
                conexion.rollback()
                return

            cursor.execute(
                "UPDATE productos SET cantidad = ? WHERE id = ?",
                (nueva_cantidad, id_actualizar)
            )

        conexion.commit()
        print(Fore.GREEN + "✅ Producto actualizado correctamente.")

    except ValueError:
        conexion.rollback()
        print(Fore.RED + "❌ Precio o cantidad inválidos.")

    except sqlite3.Error as error:
        conexion.rollback()
        print(Fore.RED + f"❌ Error al actualizar el producto: {error}")


def eliminar_producto(conexion):
    """
    Elimina un producto por ID, pidiendo confirmación antes.
    """

    ver_productos(conexion)

    try:
        id_eliminar = int(input("\nIngresá el ID del producto a eliminar: ").strip())

    except ValueError:
        print(Fore.RED + "❌ El ID debe ser un número entero.")
        return

    cursor = conexion.cursor()

    cursor.execute("SELECT nombre FROM productos WHERE id = ?", (id_eliminar,))
    fila = cursor.fetchone()

    if not fila:
        print(Fore.RED + f"❌ No existe ningún producto con el ID {id_eliminar}.")
        return

    nombre = fila[0]

    print(Fore.YELLOW + f"\nProducto encontrado: {nombre}")
    respuesta = input(f"¿Confirmás que querés eliminar '{nombre}'? (s/n): ").strip().lower()

    if respuesta != "s":
        print(Fore.YELLOW + "Operación cancelada.")
        return

    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_eliminar,))
        conexion.commit()

        print(Fore.GREEN + f"✅ Producto '{nombre}' eliminado correctamente.")

    except sqlite3.Error as error:
        conexion.rollback()
        print(Fore.RED + f"❌ Error al eliminar el producto: {error}")


def productos_bajo_stock(conexion):
    """
    Muestra los productos con cantidad menor o igual al límite indicado.
    """

    try:
        limite = int(input("\nMostrar productos con stock menor o igual a: ").strip())

        if limite < 0:
            print(Fore.RED + "❌ El límite no puede ser negativo.")
            return

    except ValueError:
        print(Fore.RED + "❌ El límite debe ser un número entero.")
        return

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT id, nombre, categoria, precio, cantidad
            FROM productos
            WHERE cantidad <= ?
            ORDER BY cantidad ASC
        """, (limite,))

        filas = cursor.fetchall()

        if not filas:
            print(Fore.GREEN + "No hay productos con bajo stock.")
            return

        print(Fore.YELLOW + "\n=== Productos con bajo stock ===")

        for id_, nombre, categoria, precio, cantidad in filas:
            print(f"ID: {id_} | {nombre} | {categoria} | ${precio:.2f} | Stock: {cantidad}")

    except sqlite3.Error as error:
        print(Fore.RED + f"❌ Error al consultar bajo stock: {error}")


# ------------------------------------------------------------
# FUNCIONES DEL MENÚ
# ------------------------------------------------------------

def limpiar_pantalla():
    """
    Limpia la pantalla de la terminal.
    """

    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """
    Pausa el programa hasta que el usuario presione Enter.
    """

    input("\nPresioná Enter para continuar...")


def main():
    """
    Función principal del programa.
    Muestra el menú y permite utilizar el sistema.
    """

    conexion = conectar_db()

    while True:
        limpiar_pantalla()

        print(Fore.BLUE + "\n" + "=" * 60)
        print(Fore.BLUE + "        SISTEMA DE GESTIÓN DE PRODUCTOS")
        print(Fore.BLUE + "=" * 60)
        print("  1. Agregar producto")
        print("  2. Ver todos los productos")
        print("  3. Buscar producto por nombre")
        print("  4. Actualizar producto")
        print("  5. Eliminar producto")
        print("  6. Ver productos con bajo stock")
        print("  7. Salir")
        print("-" * 60)

        opcion = input("Seleccioná una opción (1-7): ").strip()

        if opcion == "1":
            agregar_producto(conexion)
            pausar()

        elif opcion == "2":
            ver_productos(conexion)
            pausar()

        elif opcion == "3":
            buscar_producto(conexion)
            pausar()

        elif opcion == "4":
            actualizar_producto(conexion)
            pausar()

        elif opcion == "5":
            eliminar_producto(conexion)
            pausar()

        elif opcion == "6":
            productos_bajo_stock(conexion)
            pausar()

        elif opcion == "7":
            print(Fore.GREEN + "\nGracias por usar el sistema. Hasta luego.")
            break

        else:
            print(Fore.RED + "Opción inválida. Ingresá un número del 1 al 7.")
            pausar()

    conexion.close()


if __name__ == "__main__":
    main()