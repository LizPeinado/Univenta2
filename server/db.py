# server/db.py
import mysql.connector
from mysql.connector import errorcode

# Configuración de la conexión MySQL
db_config = {
    'user': 'root',
    'password': 'Cricet18',
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
        
        cursor.execute("""
            SELECT id, fname, lastname, email, password 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
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
            ID INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            NombreUsuario VARCHAR(50) NOT NULL,
            Titulo VARCHAR(50) NOT NULL,
            ImagenURL VARCHAR(50) NOT NULL,
            Precio INT NOT NULL,
            Descripcion VARCHAR(500) NOT NULL
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
            ID INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            NombreUsuario VARCHAR(50) NOT NULL,
            Titulo VARCHAR(50) NOT NULL,
            ImagenURL VARCHAR(50) NOT NULL,
            Precio INT NOT NULL,
            Descripcion VARCHAR(500) NOT NULL
        )
        """

        cursor.execute(crear_tabla_comida)
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
            ID INT AUTO_INCREMENT PRIMARY KEY,
            IDusuario INT NOT NULL,
            NombreUsuario VARCHAR(50) NOT NULL,
            Titulo VARCHAR(50) NOT NULL,
            ImagenURL VARCHAR(50) NOT NULL,
            Precio INT NOT NULL,
            Descripcion VARCHAR(500) NOT NULL
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
def agregar_producto_o_servicio(user_id, nombre, tipo, Titulo, Imagen, Precio, Descripcion):
    try:
        print("Estoy dentro")
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        if tipo == 'Producto':
            print("Es un producto")
            insertar_producto = "INSERT INTO producto (IDusuario, NombreUsuario, Titulo, ImagenURL, Precio, Descripcion) VALUES ( %s, %s, %s, %s, %s, %s)"
            cursor.execute(insertar_producto, (user_id, nombre, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close() 

        if tipo == 'Servicio':
            print("Es un servicio")
            insertar_servicio = "INSERT INTO servicio (IDusuario, NombreUsuario, Titulo, ImagenURL, Precio, Descripcion) VALUES ( %s, %s, %s, %s, %s, %s)"
            cursor.execute(insertar_servicio, (user_id, nombre, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo ")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close()

        if tipo == 'Comida':
            print("Es comida")
            insertar_comida = "INSERT INTO comida (IDusuario, NombreUsuario, Titulo, ImagenURL, Precio, Descripcion) VALUES ( %s, %s, %s, %s, %s, %s)"
            cursor.execute(insertar_comida, (user_id, nombre, Titulo, Imagen, Precio, Descripcion))
            print("Si se guardoooo ")
            cnx.commit()
            id_gen = cursor.lastrowid
            cursor.close()
            cnx.close()

        return id_gen
    except mysql.connector.Error as err:
        print("Error al agregar producto: ",err)
        return None


# MOSTRAR TODOS LOS PRODUCTOS
def mostrar_productos():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto")
        print("Aqui deberia seleccionar todo")
        prdts = cursor.fetchall()
        print("Pasando datos a una variable")
        cursor.close()
        cnx.close()

        print("Si llega hasta aqui, en teoria si se mando")
        return prdts

    except:
        print("ERROR para mandar productos")
        return None

# MOSTRAR TODOS LOS SERVICIOS
def mostrar_servicios():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicio")
        print("Aqui deberia seleccionar todo")
        servicio = cursor.fetchall()
        print("Pasando datos a una variable")
        cursor.close()
        cnx.close()

        print("Si llega hasta aqui, en teoria si se mando")
        return servicio

    except:
        print("ERROR para mandar servicios")
        return None

def mostrar_comida():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT * FROM comida")
    comidas = cursor.fetchall()

    cursor.close()
    cnx.close()

    return comidas


def obtener_producto_por_id(producto_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto WHERE ID = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()
        cnx.close()
        return producto
    except mysql.connector.Error as err:
        print("Error al obtener producto por ID:", err)
        return None
    
# Contacto
def get_db():
    return mysql.connector.connect(**db_config)