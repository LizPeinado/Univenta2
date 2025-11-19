import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime as dt
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

    return render_template(
        'auth/verProducto.html',
        ver = producto,
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
    user_data = obtener_usuario_por_id(user_id)
    
    # RENDERIZA LA NUEVA PLANTILLA DENTRO DE AUTH/
    return render_template('auth/settings.html', user=user_data)


# --- Inicio del Servidor ---
if __name__ == '__main__':
    app.run(debug=True)



