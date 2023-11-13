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
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor


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
    if user_data:
        return User(
            id=user_data["id"],
            nombre=user_data["nombre"],
            correo=user_data["correo"],
            telefono=user_data["telefono"],
            password=user_data["password"],
        )
    return None


class User(UserMixin):
    def __init__(self, id, nombre, correo, telefono, password) -> None:
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.password = password


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
            return redirect(url_for("login"))
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
        return redirect(url_for("user_page", user=current_user.name))
    return render_template(
        "auth/register_user.html", logged_in=current_user.is_authenticated
    )


@app.route("/register/doctor")
def register_doctor():
    return render_template("auth/register_doctor.html")


@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for("home"))


@app.route("/user/<user>")
@login_required
def user_page(user):
    return render_template("user.html")


@app.route("/doctor")
def doctor_page():
    return render_template("doctor.html")


@app.route("/secretary")
def secretary_page():
    return render_template("secretary.html")


@app.route("/agendador")
def agendador():
    return render_template("agendador.html")


@app.route("/quejas", methods=["GET", "POST"])
@login_required
def quejas():
    if request.method == "POST":
        get = request.form

        query = "SELECT COUNT(*) AS existe_comentario FROM feedback WHERE id_usuario = {}".format(
            current_user.id
        )
        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            datos = cursor.fetchone()

        if datos["existe_comentario"]:
            query = """UPDATE feedback SET evaluacion = {}, comentario = '{}' WHERE id_usuario = {}""".format(
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

    query = "SELECT evaluacion, comentario FROM feedback WHERE id_usuario = {}".format(
        current_user.id
    )

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        datos = cursor.fetchone()

    if datos:
        evaluacion = ""
        for _ in range(int(datos["evaluacion"])):
            evaluacion += "⭐"

    return render_template("quejas.html", evaluacion=evaluacion, datos=datos)


if __name__ == "__main__":
    app.run()
