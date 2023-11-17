from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from users import User, Doctor, Secretary


app = Flask(__name__)
# importar mis configuraciones
app.config.from_object("config.Config")

# inicial la conexion con mysql
mysql = MySQL(app, cursorclass=DictCursor)

# configuracion de flask login manager
login_manager = LoginManager()
login_manager.init_app(app)


# create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    with mysql.connect() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuario WHERE id = '{}'".format(user_id))
        user_data = cursor.fetchone()

        cursor.execute("SELECT * FROM doctor WHERE id = '{}'".format(user_id))
        doctor_data = cursor.fetchone()

        cursor.execute("SELECT * FROM secretaria WHERE id = '{}'".format(user_id))
        secretary_data = cursor.fetchone()

    if user_data:
        return User(
            id=user_data["id"],
            nombre=user_data["nombre"],
            correo=user_data["correo"],
            telefono=user_data["telefono"],
            password=user_data["password"],
        )
    elif doctor_data:
        return Doctor(
            id=doctor_data["id"],
            nombre=doctor_data["nombre"],
            cedula=doctor_data["cedula"],
            telefono=doctor_data["telefono"],
            direccion=doctor_data["direccion"],
            correo=doctor_data["correo"],
            password=doctor_data["password"],
        )
    elif secretary_data:
        return Secretary(
            id=secretary_data["id"],
            id_doctor=secretary_data["id_doctor"],
            nombre=secretary_data["nombre"],
            correo=secretary_data["correo"],
            password=secretary_data["password"],
        )

    return None


@app.route("/")
def home():
    return render_template(
        "index.html",
        logged_in=current_user.is_authenticated,
        user_name=current_user,
    )


@app.route("/register")
def register():
    return render_template("auth/register.html")


@app.route("/login")
def login():
    return render_template("auth/login.html")


# login function for Users
@app.route("/login/user", methods=["GET", "POST"])
def login_user_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]
        password = get["password"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        if not user:
            flash("Ese correo no ha sido registrado aun, intenta de nuevo.")
            return redirect(url_for("login_user_page"))
        # revisar si el hash de la contraseña ingresa es igual que en la base de datos
        elif not check_password_hash(user["password"], password):
            flash("Contraseña incorrecta, por favor intente de nuevo.")
            return redirect(url_for("login"))
        else:
            new_user = User(
                id=user["id"],
                nombre=user["nombre"],
                correo=user["correo"],
                telefono=user["telefono"],
                password=user["password"],
            )
            login_user(new_user)
            return redirect(url_for("user_page", user=user["nombre"]))

    return render_template(
        "auth/login_user.html", logged_in=current_user.is_authenticated
    )


# login function for Doctors
@app.route("/login/doctor", methods=["GET", "POST"])
def login_doctor_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]
        password = get["password"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctor WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        if not user:
            flash("Ese correo no ha sido registrado aun, intenta de nuevo.")
            return redirect(url_for("login_doctor_page"))
        # revisar si el hash de la contraseña ingresa es igual que en la base de datos
        elif not check_password_hash(user["password"], password):
            flash("Contraseña incorrecta, por favor intente de nuevo.")
            return redirect(url_for("login"))
        else:
            new_user = Doctor(
                id=user["id"],
                nombre=user["nombre"],
                cedula=user["cedula"],
                telefono=user["telefono"],
                direccion=user["direccion"],
                correo=user["correo"],
                password=user["password"],
            )
            login_user(new_user)
            return redirect(url_for("doctor_page", user=user["nombre"]))

    return render_template(
        "auth/login_doctor.html", logged_in=current_user.is_authenticated
    )


# login function for Secretary
@app.route("/login/secretary", methods=["GET", "POST"])
def login_secretary_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]
        password = get["password"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM secretaria WHERE correo = '{}'".format(correo)
            )
            user = cursor.fetchone()

        if not user:
            flash("Ese correo no ha sido registrado aun, intenta de nuevo.")
            return redirect(url_for("login_secretary_page"))
        # revisar si el hash de la contraseña ingresa es igual que en la base de datos
        elif not check_password_hash(user["password"], password):
            flash("Contraseña incorrecta, por favor intente de nuevo.")
            return redirect(url_for("login"))
        else:
            new_user = Secretary(
                id=user["id"],
                id_doctor=user["id_doctor"],
                nombre=user["nombre"],
                correo=user["correo"],
                password=user["password"],
            )
            login_user(new_user)
            return redirect(url_for("secretary_page", user=user["nombre"]))
    return render_template("auth/login_secretary.html")


@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for("home"))


# register user
@app.route("/register/user", methods=["GET", "POST"])
def register_user_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        if user:
            # User already exists
            flash("Ya has registrado este correo antes, mejor intenta ingresar!")
            return redirect(url_for("login_user_page"))

        hash_and_salt_password = generate_password_hash(
            get["password"], method="pbkdf2:sha256", salt_length=8
        )

        query = """INSERT INTO usuario (nombre, correo, telefono, password) 
                VALUES (%s, %s, %s, %s)"""
        values = (get["nombre"], get["correo"], get["telefono"], hash_and_salt_password)

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()  # registra los datos en la base de datos

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        new_user = User(
            id=user["id"],
            nombre=user["nombre"],
            correo=user["correo"],
            telefono=user["telefono"],
            password=user["password"],
        )
        login_user(new_user)
        return redirect(url_for("user_page", user=current_user.nombre))
    return render_template(
        "auth/register_user.html", logged_in=current_user.is_authenticated
    )


@app.route("/register/patient", methods=["GET", "POST"])
@login_required
def register_patient_page():
    if request.method == "POST":
        get = request.form

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM paciente")
            pacientes = cursor.fetchone()

        if pacientes["total"] >= 5:
            flash("Ya has registrado el numero maximo de pacientes", "error")
            return redirect(url_for("user_page", user=get["nombre_usuario"]))

        query = """
            INSERT INTO paciente (id_usuario, nombre, fecha_nacimiento, genero, direccion, peso_kg, estatura_mts, relacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            get["id_usuario"],
            get["nombre"],
            get["fecha_nacimiento"],
            get["genero"],
            get["direccion"],
            get["peso"],
            get["estatura"],
            get["relacion"],
        )

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

        flash("Has registrado a un nuevo paciente exitosamente ^_^", "info")
        return redirect(url_for("user_page", user=get["nombre_usuario"]))
    return render_template("auth/register_patient.html")


@app.route("/register/secretary", methods=["GET", "POST"])
@login_required
def register_secretary_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM secretaria WHERE correo = '{}'".format(correo)
            )
            user = cursor.fetchone()

        if user:
            flash("Ya has registrado ese correo, intenta con otra cuenta", "error")
            return redirect(url_for("register_secretary_page"))

        hash_and_salt_password = generate_password_hash(
            get["password"], method="pbkdf2:sha256", salt_length=8
        )

        query = """INSERT INTO secretaria (id_doctor, nombre, correo, password)
                    VALUES (%s, %s, %s, %s)"""
        values = (get["id_doctor"], get["nombre"], correo, hash_and_salt_password)

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

        flash("Has registrado un nuevo perfil administrativo exitosamente ^_^", "info")
        return redirect(url_for("register_secretary_page"))

    return render_template("auth/register_secretary.html")


@app.route("/register/doctor", methods=["GET", "POST"])
def register_doctor_page():
    if request.method == "POST":
        get = request.form
        correo = get["correo"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctor WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        if user:
            # if User already exists
            flash("Ya has registrado este correo antes, mejor intenta ingresar!")
            return redirect(url_for("login_doctor_page"))

        hash_and_salt_password = generate_password_hash(
            get["password"], method="pbkdf2:sha256", salt_length=8
        )

        query = """INSERT INTO doctor (nombre, cedula, telefono, direccion, correo, password) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            get["nombre"],
            get["cedula"],
            get["telefono"],
            get["direccion"],
            get["correo"],
            hash_and_salt_password,
        )

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()  # registra los datos en la base de datos

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctor WHERE correo = '{}'".format(correo))
            user = cursor.fetchone()

        new_user = Doctor(
            id=user["id"],
            nombre=user["nombre"],
            cedula=user["cedula"],
            telefono=user["telefono"],
            direccion=user["direccion"],
            correo=user["correo"],
            password=user["password"],
        )
        login_user(new_user)
        return redirect(url_for("doctor_page", user=current_user.nombre))

    return render_template(
        "auth/register_doctor.html", logged_in=current_user.is_authenticated
    )


@app.route("/user/<user>")
@login_required
def user_page(user):
    for key, value in current_user.__dict__.items():
        print(f"{key}: {value}")

    return render_template("user.html")


@app.route("/doctor/<user>")
@login_required
def doctor_page(user):
    for key, value in current_user.__dict__.items():
        print(f"{key}: {value}")

    return render_template("doctor.html")


@app.route("/secretary/<user>")
def secretary_page(user):
    for key, value in current_user.__dict__.items():
        print(f"{key}: {value}")
    return render_template("secretary.html")


@app.route("/agendador")
def agendador():
    return render_template("agendador.html")


@app.route("/quejas", methods=["GET", "POST"])
@login_required
def quejas():
    if request.method == "POST":
        get = request.form

        query = "SELECT COUNT(*) AS existe_comentario FROM feedback WHERE id_usuario = '{}'".format(
            current_user.id
        )
        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            datos = cursor.fetchone()

        if datos["existe_comentario"]:
            query = "UPDATE feedback SET evaluacion = {}, comentario = '{}' WHERE id_usuario = '{}'".format(
                get["evaluacion"], get["comentario"], current_user.id
            )
            with mysql.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()

            flash("Tu evaluacion ha sido actualizado correctamente")
            return redirect(url_for("quejas"))

        query = """INSERT INTO feedback (id_usuario, comentario, evaluacion) VALUES (%s, %s, %s)"""
        values = (current_user.id, get["comentario"], get["evaluacion"])

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

        return render_template("quejas.html")

    query = (
        "SELECT evaluacion, comentario FROM feedback WHERE id_usuario = '{}'".format(
            current_user.id
        )
    )

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        datos = cursor.fetchone()

    evaluacion = ""
    if datos:
        for _ in range(int(datos["evaluacion"])):
            evaluacion += "⭐"

    return render_template("quejas.html", evaluacion=evaluacion, datos=datos)


@app.route("/ver_quejas")
def mostrar_quejas():
    query = """SELECT nombre, comentario, evaluacion
                FROM feedback
                INNER JOIN usuario
                ON usuario.id = feedback.id_usuario
                ORDER BY evaluacion DESC"""
    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

    print(rows)

    return render_template("mostrar_quejas.html", datos=rows)


if __name__ == "__main__":
    app.run()
