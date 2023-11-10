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


@app.route("/login", methods=["GET", "POST"])
def login():
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
        # revisar si el hash de la contraseña ingresa es igual que en la base de dastos
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
            return redirect(url_for("user_page"))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
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
            return redirect(url_for("login"))

        hash_and_salt_password = generate_password_hash(
            get["password"], method="pbkdf2:sha256", salt_length=8
        )

        with mysql.connect() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO usuario (nombre, correo, telefono, password) 
                    VALUES (%s, %s, %s, %s)"""
            values = (
                get["nombre"],
                get["correo"],
                get["telefono"],
                hash_and_salt_password,
            )
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
        return redirect(url_for("user_page"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for("home"))


@app.route("/user")
@login_required
def user_page():
    return render_template("user.html")


@app.route("/agendador")
def agendador():
    return render_template("agendador.html")


@app.route("/quejas")
def quejas():
    return render_template("quejas.html")


if __name__ == "__main__":
    app.run(debug=True)