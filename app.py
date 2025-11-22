import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime as dt
from server.db import crear_tabla_usuarios, agregar_usuario, obtener_usuario_por_email, obtener_usuario_por_id, crear_tabla_productos, crear_tabla_comida, crear_tabla_servicios, agregar_producto_o_servicio, mostrar_productos, mostrar_servicios
from pymongo import MongoClient
from bson import ObjectId
import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
mongo_client = MongoClient(MONGO_URI)

mongo_db = mongo_client['chats_db']
chats_collection = mongo_db['chats']

from server.db import (
    crear_tabla_usuarios, 
    agregar_usuario, 
    obtener_usuario_por_email, 
    obtener_usuario_por_id,
    crear_tabla_productos,
    crear_tabla_comida, 
    crear_tabla_servicios, 
    agregar_producto_o_servicio, 
    mostrar_productos, 
    mostrar_servicios,
    mostrar_comida,
    obtener_producto_por_id,
    obtener_usuario_por_id_completo
)

# Configuración MongoDB
#MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
#mongo_client = MongoClient(MONGO_URI)
#mongo_db = mongo_client['chats_db']
#chats_collection = mongo_db['chats']

from server.db import crear_tabla_usuarios, agregar_usuario, obtener_usuario_por_email, obtener_usuario_por_id, crear_tabla_productos, crear_tabla_comida, crear_tabla_servicios, agregar_producto_o_servicio, mostrar_productos, mostrar_servicios, mostrar_comida, obtener_producto_por_id, get_db

# AQUI SE SUBIRAN LAS IMAGENES
UPLOAD_FOLDER = 'static/uploads/'

# EXTENSIONES PERMITIDAS
EXTENSIONES_PERMITIDAS = ['png', 'jpg', 'jpeg', 'gif']

# --- Configuración Inicial ---
app = Flask(__name__, template_folder='client/templates', static_folder = "static")
# CLAVE SECRETA: NECESARIA PARA CIFRAR LAS COOKIES DE SESIÓN
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura') 
bcrypt = Bcrypt(app)

# MAS CONFIGURACIONES
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ejecutamos la creación de la tabla al inicio (si no existe)
crear_tabla_usuarios()

# --- Decorador de Autenticación (Middleware) ---
def login_required(f):
    """Decorador para restringir el acceso si no hay sesión activa."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            # Si no hay sesión, redirige al login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas Públicas (Enrutamiento Estático) ---

@app.route('/about')
def about():
    # Estas vistas usan el navbar público si la sesión está cerrada
    return render_template('about.html')

# Contacto
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')

        try:
            conn = get_db()
            cursor = conn.cursor()

            sql = """
            INSERT INTO contacto (nombre, email, mensaje)
            VALUES (%s, %s, %s)
            """

            cursor.execute(sql, (nombre, email, mensaje))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template('contact.html', success=True)

        except Exception as e:
            print("ERROR:", e)
            flash("Error al guardar en la base de datos.")
            return render_template('contact.html', success=False)

    return render_template('contact.html')



# --- Rutas sesion iniciada --- 

@app.route("/Producto", methods=['GET','POST'])
def productos():

    productos = mostrar_productos()

    print(">>> Productos cargados:", productos)  # Prueba de depuración
    return render_template("auth/Producto.html", producto=productos)

@app.route('/Servicio', methods=['GET','POST'])
def Servicio():
    # Esta vistas usan el navbar si la sesión está iniciada
    servicios = mostrar_servicios()

    print(">>> Servicios cargados:", servicios)  # Prueba de depuración
    return render_template('auth/Servicio.html', servicio=servicios)

@app.route('/Comida')
def Comida():
    # Esta vistas usan el navbar si la sesión está iniciada
    comidas = mostrar_comida()
    print(">>> Comida cargada:", comidas)
    return render_template('auth/Comida.html', comida=comidas)

# --- Rutas para el Chat ---

def obtener_o_crear_chat(user_id, other_user_id, product_id):
    """Busca un chat existente o crea uno nuevo"""
    # Buscar chat existente
    chat_existente = chats_collection.find_one({
        'participantes': {'$all': [user_id, other_user_id]},
        'producto_id': product_id
    })
    
    if chat_existente:
        return str(chat_existente['_id'])
    
    # Crear nuevo chat
    producto = obtener_producto_por_id(product_id)
    if not producto:
        return None
    
    nuevo_chat = {
        'participantes': [user_id, other_user_id],
        'producto_id': product_id,
        "producto_imagen": producto["ImagenURL"],
        'producto_titulo': producto['Titulo'],
        'creado_en': dt.now(),
        'mensajes': []
    }
    
    resultado = chats_collection.insert_one(nuevo_chat)
    return str(resultado.inserted_id)

def obtener_chats_usuario(user_id):
    """Obtiene todos los chats de un usuario"""
    chats = chats_collection.find({
        'participantes': user_id
    }).sort('creado_en', -1)
    
    chats_lista = []
    for chat in chats:
        # Encontrar el otro participante
        otro_id = [p for p in chat['participantes'] if p != user_id][0]
        otro_usuario = obtener_usuario_por_id_completo(otro_id)
        
        chats_lista.append({
            '_id': str(chat['_id']),
            'producto_titulo': chat['producto_titulo'],
            'con_nombre': otro_usuario['nombre_completo'] if otro_usuario else 'Usuario',
            'ultimo_mensaje': chat['mensajes'][-1]['mensaje'] if chat['mensajes'] else 'Sin mensajes',
            'fecha_ultimo_mensaje': chat['mensajes'][-1]['timestamp'] if chat['mensajes'] else chat['creado_en']
        })
    
    return chats_lista

@app.route('/Chats')
@login_required
def chats():
    user_id = session.get('user_id')
    chats_usuario = obtener_chats_usuario(user_id)
    
    return render_template("auth/Chats.html", chats=chats_usuario)

# RUTA PARA INICIAR/CREAR CHAT - USA ESTA EN EL BOTÓN
@app.route('/iniciar_chat/<int:product_id>/<int:other_user_id>')
@login_required
def iniciar_chat(product_id, other_user_id):
    """Ruta para iniciar o crear un chat - USA ESTA EN EL BOTÓN"""
    user_id = session.get('user_id')
    
    # Obtener o crear chat
    chat_id = obtener_o_crear_chat(user_id, other_user_id, product_id)
    
    if not chat_id:
        return "Producto no encontrado", 404
    
    # Redirigir a chat_detalle
    return redirect(url_for('chat_detalle', chat_id=chat_id))

@app.route('/enviar_mensaje', methods=['POST'])
@login_required
def enviar_mensaje_route():
    """Ruta para enviar mensajes"""
    user_id = session.get('user_id')
    chat_id = request.form.get('chat_id')
    mensaje_texto = request.form.get('mensaje')
    
    if not all([chat_id, mensaje_texto]):
        return "Datos incompletos", 400
    
    try:
        nuevo_mensaje = {
            'sender_id': user_id,
            'mensaje': mensaje_texto,
            'timestamp': dt.now()
        }
        
        resultado = chats_collection.update_one(
            {'_id': ObjectId(chat_id)},
            {'$push': {'mensajes': nuevo_mensaje}}
        )
        
        if resultado.modified_count > 0:
            return redirect(url_for('chat_detalle', chat_id=chat_id))
        else:
            return "Error al enviar mensaje", 500
            
    except Exception as e:
        print("Error:", e)
        return "Error interno del servidor", 500
# ACTUALIZA TU RUTA chat_detalle EXISTENTE
@app.route('/chat_detalle/<chat_id>')
@login_required
def chat_detalle(chat_id):
    """Ruta para ver el detalle del chat"""
    user_id = session.get('user_id')
    
    try:
        chat = chats_collection.find_one({'_id': ObjectId(chat_id)})
    except:
        return "Chat no encontrado", 404
    
    if not chat or user_id not in chat['participantes']:
        return "Chat no encontrado", 404
    
    # Obtener información del producto
    producto = obtener_producto_por_id(chat['producto_id'])
    
    # Obtener el otro participante
    other_id = [p for p in chat['participantes'] if p != user_id][0]
    other_user = obtener_usuario_por_id_completo(other_id)
    
    return render_template('auth/chat_detalle.html',
                         chat_id=chat_id,
                         mensajes=chat['mensajes'],
                         producto=producto,
                         producto_titulo=chat['producto_titulo'],
                         producto_imagen=chat.get('producto_imagen'), 
                         nombre_otro=other_user['nombre_completo'] if other_user else 'Usuario',
                         other_id=other_id)

@app.route("/perfil/<int:id_usuario>")
def perfil(id_usuario):

    # Ejemplo de usuarios (luego conectar con BD)
    usuarios = {
        1: {
            "nombre": "Mi Perfil",
            "descripcion": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod...",
            "foto": "img/perfiles/user1.jpg",
            "registro": "Octubre 2025",
            "rating": 5
        },
        2: {
            "nombre": "Carlos López",
            "descripcion": "Vendedor de tecnología y accesorios...",
            "foto": "img/perfiles/user2.jpg",
            "registro": "Junio 2024",
            "rating": 4
        }
    }

    # Productos publicados por usuario (ejemplo)
    #productos_todos = mostrar_productos()
    productos_todos = mostrar_productos()

    # Validar usuario
    if id_usuario not in usuarios:
        return "Usuario no encontrado", 404

    perfil = usuarios[id_usuario]

    # aseguramos que rating exista
    perfil.setdefault("rating", 0)

    # Filtrar solo productos del usuario
    productos_usuario = [p for p in productos_todos if p["IDusuario"] == id_usuario]

    print("PRODUCTOS_USUARIO ENVIADOS A PERFIL:", productos_usuario)

    return render_template(
        'auth/perfil.html',
        usuario=perfil,
        producto=productos_usuario,
        id_usuario=id_usuario
    )


# Pagina de producto individual
@app.route('/verProducto/<int:id_producto>', methods=['GET','POST'])
def verProducto(id_producto):

    productos = mostrar_productos()

    producto = [p for p in productos if p["ID"] == id_producto]

   # if id_producto not in producto:
    #    return "Hmm... No pudimos encontrar este producto", 404

    print(producto[0]["Titulo"])
    return render_template(
        'auth/verProducto.html',
        ver = producto[0],
        id_producto=id_producto
    )

#FORMATOS PERMITIDOS PARA SUBIR IMAGENES
formatos_validos = {'jpg', 'jpeg', 'png', 'gif'}

def formatos_validos_imagen(archivo):
    return '.' in archivo and archivo.rsplit('.', 1)[1].lower() in formatos_validos



# AGREGAR PRODUCTO A UNA BASE DE DATOS
@app.route('/nuevoProducto', methods=['GET', 'POST'])

# CREAR PRODUCTO EN EL PERFIL DEL USUARIO
def crearProducto():
    if request.method == 'POST':

        tipo = request.form['tipo']
        Titulo = request.form['Titulo']
        Precio = request.form['Precio']
        Descripcion = request.form['Descripcion']
        user_id = session.get('user_id') # Agarrando el ID del usuario con la sesion iniciada

        user_data = obtener_usuario_por_id(user_id) #Sacando los datos de la sesion del usuario
        nombre = user_data['fname']

        if 'Imagen' not in request.files: # ASEGURAR QUE SE SUBA UNA IMAGEN
            flash('Falta subir la imagen')
            return redirect(request.url)

        image = request.files['Imagen'] # TRAER LA IMAGEN

        if image.filename == '':
            flash('Ninguna imagen seleccionada')
            return redirect(request.url)

        # Verificar si la extension es permitida
        if image and image.filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS:

            dt_now = dt.now().strftime("%Y%m%d%H%M%S%f") # Para nombrar el archivo
            nombre_imagen = dt_now + '.jpg'
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)) 

            img_dir = './static/uploads/'
            path_img = img_dir + nombre_imagen # DIRECTORIO de la imagen
        
        else:
            # Manejar el error o redirigir
            return "Error: Imagen inválida o no enviada", 400

        Imagen = path_img
    
        print("Se recibieron los datos")
        id_gen = agregar_producto_o_servicio(user_id, nombre, tipo, Titulo, Imagen, Precio, Descripcion)

        #SI se agrego, regresa a la pagina de home
        if id_gen:
            return redirect(url_for('home'))
        else: #En caso de que NO, vuelve a cargar la pagina de inicio
            return render_template('auth/nuevoProducto.html', error="No se pudo agregar producto")

    return render_template('auth/nuevoProducto.html')


# --- Rutas de Autenticación (Login/Signup) ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Si el usuario ya está logueado, redirigir a Home Protegido (/)
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        fname = request.form['fname']
        lastname = request.form.get('lastname','')
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['cpassword']

        # 1. Validación de Confirmación
        if password != confirm_password:
            return render_template('signup.html', error="Error: Las contraseñas no coinciden.")

        # 2. Cifrar la contraseña con Bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 3. Guardar el usuario en la DB
        user_id = agregar_usuario(fname, lastname, email, password_hash)
        
        if user_id:
            # Registro exitoso: redirige al login
            return redirect(url_for('login'))
        else:
            # Error de registro (ej. email duplicado)
            return render_template('signup.html', error="Error al registrar usuario. El email ya existe.")
            
    # Muestra el formulario GET
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, redirigir a Home Protegido (/)
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        usuario = obtener_usuario_por_email(email)
        
        if usuario:
            # 1. Verificar la contraseña con Bcrypt
            if bcrypt.check_password_hash(usuario['password'], password):
                # 2. Éxito: Establecer la sesión de Flask
                session['logged_in'] = True
                session['user_id'] = usuario['id']
                session['user_email'] = usuario['email']
                
                # 3. Redirigir al Home Protegido
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Contraseña o email incorrectos.")
        else:
            return render_template('login.html', error="Contraseña o email incorrectos.")
            
    # Muestra el formulario GET
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Cierra la sesión (elimina todas las claves)
    session.clear()
    # Redirige al login
    return redirect(url_for('login'))


# --- Rutas Protegidas y Dinámicas ---

@app.route('/')
def home():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        user_data = obtener_usuario_por_id(user_id)

        # Obtener datos usando las funciones del proyecto
        productos = mostrar_productos() or []
        servicios = mostrar_servicios() or []
        comida = mostrar_comida() or []

        return render_template(
            'auth/home.html',
            user=user_data,
            productos=productos,
            servicios=servicios,
            comidas=comida
        )

    return render_template('index.html')


@app.route('/settings')
@login_required
def settings():
    user_id = session.get('user_id')
    user = obtener_usuario_por_id(user_id)
    return render_template('auth/settings.html', user=user)

# cambio de contraseña
@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    user_id = session.get('user_id')

    actual = request.form.get('password_actual')
    nueva = request.form.get('password_nueva')
    confirma = request.form.get('password_confirm')

    user = obtener_usuario_por_id(user_id)

    print("USER DATA:", user)

    if not bcrypt.check_password_hash(user['password'], actual):
        flash("La contraseña actual es incorrecta.")
        return redirect('/settings')

    if nueva != confirma:
        flash("Las contraseñas nuevas no coinciden.")
        return redirect('/settings')

    nueva_hash = bcrypt.generate_password_hash(nueva).decode('utf-8')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = %s WHERE id = %s", (nueva_hash, user_id))
    conn.commit()

    flash("Contraseña actualizada exitosamente.")
    return redirect('/settings')


# --- Inicio del Servidor ---
if __name__ == '__main__':
    app.run(debug=True)



