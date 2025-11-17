# server/db.py
import mysql.connector
from mysql.connector import errorcode

# Configuración de la conexión MySQL
db_config = {
    'user': 'root',
    'password': 'MySQL1357',
    'host': 'localhost',
    'database': 'prueba'
}

def crear_tabla_usuarios():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # TABLA DE USUARIOS ACTUALIZADA CON EL CAMPO password_hash
        crear_tabla = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fname VARCHAR(50) NOT NULL,
            lastname VARCHAR(50),
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL 
        )
        """
        cursor.execute(crear_tabla)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Tabla 'users' creada o ya existe.")
    except mysql.connector.Error as err:
        print("Error al crear la tabla:", err)

# La función ahora acepta y guarda el hash de la contraseña
def agregar_usuario(fname, lastname, email, password_hash): 
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        insertar_usuario = "INSERT INTO users (fname, lastname, email, password) VALUES (%s, %s,%s, %s)"
        cursor.execute(insertar_usuario, (fname, lastname, email, password_hash))
        cnx.commit()
        last_id = cursor.lastrowid # Obtener el ID del nuevo usuario
        cursor.close()
        cnx.close()
        return last_id
    except mysql.connector.Error as err:
        print("Error al agregar usuario:", err)
        return None

def obtener_usuario_por_email(email):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario:", err)
        return None

def obtener_usuario_por_id(user_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, fname, lastname, email FROM users WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario por ID:", err)
        return None


#PRODUCTOS
def crear_tabla_productos():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        crear_tabla_productos = """
        CREATE TABLE IF NOT EXISTS producto(
            IDproducto INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            TituloProducto VARCHAR(50) NOT NULL,
            ImagenURLProducto VARCHAR(50) NOT NULL,
            PrecioProducto INT NOT NULL,
            DescProducto VARCHAR(500) NOT NULL
        )
        """

        cursor.execute(crear_tabla_productos)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Tabla 'productos' creada o ya existe")

    except mysql.connector.Error as arr:
        print("Error al crear tabla producto")
        return None

#COMIDA
def crear_tabla_comida():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        crear_tabla_comida = """
        CREATE TABLE IF NOT EXISTS comida(
            IDcomida INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            TituloComida VARCHAR(50) NOT NULL,
            ImagenURLComida VARCHAR(50) NOT NULL,
            PrecioComida INT NOT NULL,
            DescComida VARCHAR(500) NOT NULL
        )
        """

        cursor.execute(crear_tabla_servicios)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Tabla 'comida' creada o ya existe")

    except mysql.connector.Error as err:
        print("Error al crear tabla comida")
        return None

#SERVICIOS
def crear_tabla_servicios():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        crear_tabla_servicios = """
        CREATE TABLE IF NOT EXISTS servicio(
            IDservicio INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            TituloServicio VARCHAR(50) NOT NULL,
            ImagenURLServicio VARCHAR(50) NOT NULL,
            PrecioServicio INT NOT NULL,
            DescServicio VARCHAR(500) NOT NULL
        )
        """

        cursor.execute(crear_tabla_servicios)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Tabla 'servicio' creada o ya existe")

    except mysql.connector.Error as err:
        print("Error al crear tabla servicio")
        return None
        
#AGREGA LOS PRODUCTOS A SUS RESPECTIVAS TABLAS SEGUN EL TIPO
def agregar_producto_o_servicio(user_id, tipo, Titulo, Imagen, Precio, Descripcion):
    try:
        print("Estoy dentro")
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        if tipo == 'Producto':
            print("Es un producto")
            insertar_producto = "INSERT INTO producto (IDusuario, TituloProducto, ImagenURLProducto, PrecioProducto, DescProducto) VALUES ( %s, %s, %s, %s, %s)"
            cursor.execute(insertar_producto, (user_id, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close() 

        if tipo == 'Servicio':
            print("Es un servicio")
            insertar_servicio = "INSERT INTO servicio (IDusuario, TituloServicio, ImagenURLServicio, PrecioServicio, DescServicio) VALUES ( %s, %s, %s, %s, %s)"
            cursor.execute(insertar_servicio, (user_id, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo ")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close()

        if tipo == 'Comida':
            print("Es comida")
            insertar_comida = "INSERT INTO comida (IDusuario, TituloComida, ImagenURLComida, PrecioComida, DescComida) VALUES ( %s, %s, %s, %s, %s)"
            cursor.execute(insertar_comida, (user_id, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo ")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close()

        return id_gen
    except mysql.connector.Error as err:
        print("Error al agregar producto: ",err)
        return None