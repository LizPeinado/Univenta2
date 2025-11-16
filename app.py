import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from server.db import crear_tabla_usuarios, agregar_usuario, obtener_usuario_por_email, obtener_usuario_por_id

# --- Configuración Inicial ---
app = Flask(__name__, template_folder='client/templates')
# CLAVE SECRETA: NECESARIA PARA CIFRAR LAS COOKIES DE SESIÓN
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura') 
bcrypt = Bcrypt(app)
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

@app.route('/contact')
def contact():
    # Estas vistas usan el navbar público si la sesión está cerrada
    return render_template('contact.html')


# --- Rutas sesion iniciada --- 

@app.route("/Producto")
def productos():
    productos = [
        {
            "titulo": "Laptop",
            "precio": "$4,000 Mx",
            "descripcion": "Excelente estado, Intel i5, 8GB RAM, SSD 250GB"
        },
        {
            "titulo": "Pines",
            "precio": "$60 Mx",
            "descripcion": "Pines de resina personalizados, varios colores disponibles"
        }
    ]
    print(">>> Productos cargados:", productos)  # Prueba de depuración
    return render_template("auth/Producto.html", productos=productos)

@app.route('/Servicio')
def Servicio():
    # Esta vistas usan el navbar si la sesión está iniciada
    return render_template('auth/Servicio.html')

@app.route('/Comida')
def Comida():
    # Esta vistas usan el navbar si la sesión está iniciada
    return render_template('auth/Comida.html')

@app.route("/perfil/<int:id_usuario>")
def perfil(id_usuario):

    # Ejemplo de usuarios (luego conectar con BD)
    usuarios = {
        1: {
            "nombre": "Ruby Mendez",
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
    productos_todos = [
        {"usuario_id": 1, "titulo": "Laptop", "precio": "$4,000 Mx", "imagen": "img/laptop.jpg"},
        {"usuario_id": 1, "titulo": "Ropa", "precio": "$100 - 200 Mx", "imagen": "img/ropa.jpg"},
        {"usuario_id": 2, "titulo": "Mouse Gamer", "precio": "$350 Mx", "imagen": "img/mouse.jpg"},
    ]

    # Validar usuario
    if id_usuario not in usuarios:
        return "Usuario no encontrado", 404

    perfil = usuarios[id_usuario]

    # Filtrar solo productos del usuario
    productos_usuario = [p for p in productos_todos if p["usuario_id"] == id_usuario]

    return render_template(
        'auth/perfil.html',
        usuario=perfil,
        productos=productos_usuario,
        id_usuario=id_usuario
    )

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
    # 1. Verificar si la sesión está abierta
    if session.get('logged_in'):
        # SESIÓN ABIERTA: Mostrar contenido privado (home.html)
        user_id = session.get('user_id')
        user_data = obtener_usuario_por_id(user_id)
        
        # Renderiza la vista de sesión
        return render_template('auth/home.html', user=user_data)
    else:
        # SESIÓN CERRADA: Mostrar contenido público (index.html)
        # Asumimos que index.html es la página pública de bienvenida
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


