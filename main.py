from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    send_from_directory,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
from twilio.rest import Client
from config import TwilioConfig
from datetime import datetime
import os

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

app = Flask(__name__)

# importar mis configuraciones
app.config.from_object("config.Config")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


client = Client(TwilioConfig.ACCOUNT_SID, TwilioConfig.AUTH_TOKEN)

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
            return redirect(url_for("login_doctor_page"))
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
            cursor.execute(
                "SELECT COUNT(*) AS total FROM paciente WHERE id_usuario = '{}'".format(
                    current_user.id
                )
            )
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
    return render_template("user.html", current_user=current_user)


@app.route("/doctor/<user>")
@login_required
def doctor_page(user):
    return render_template("doctor.html", current_user=current_user)


@app.route("/secretary/<user>")
@login_required
def secretary_page(user):
    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT secretaria.nombre AS secretaria, doctor.nombre AS doctor, secretaria.correo
            FROM secretaria 
            INNER JOIN doctor
                ON secretaria.id_doctor = doctor.id
            WHERE secretaria.id = '{}'
            """.format(current_user.id)
        )
        datos_secretaria = cursor.fetchone()
    return render_template("secretary.html", datos_secretaria=datos_secretaria)


@app.route("/agendador", methods=["GET", "POST"])
@login_required
def agendador():
    if request.method == "POST":
        id_paciente = request.form["id_paciente"]
        fecha = request.form["fecha"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nombre FROM paciente WHERE id = '{}'".format(id_paciente)
            )
            paciente = cursor.fetchone()

        nombre_paciente = paciente["nombre"]

        return redirect(
            url_for(
                "mostrar_citas_disponibles",
                fecha=fecha,
                id_paciente=id_paciente,
                nombre_paciente=nombre_paciente,
            )
        )
    # BORRAR LAS CITAS CADUCADAS PARA PODER AGENDAR NUEVAS
    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM cita WHERE fecha < CURDATE()"
        )  # TODO change this query to save this info in historial cita
        conn.commit()

        query = """
        SELECT nombre, id 
        FROM paciente
        WHERE id NOT IN (
            SELECT paciente.id
            FROM paciente
            INNER JOIN cita 
            ON paciente.id = cita.id_paciente)
        AND paciente.id_usuario = '{}'
        """.format(
            current_user.id
        )

        cursor.execute(query)
        pacientes = cursor.fetchall()

    return render_template("agendador.html", pacientes=pacientes)


@app.route("/citas_disponibles", methods=["GET", "POST"])
@login_required
def mostrar_citas_disponibles():
    if request.method == "POST":
        # eval convierte del type string al diccionario py obtenido de el form
        selected_row = request.form["selected_row"]
        data = eval(selected_row)  # puedes obteenr nombre_doctor, id_doctor, hora

        id_doctor = data["id_doctor"]
        nombre_doctor = data["nombre_doctor"]
        hora = data["hora_disponible"] * 10000
        fecha = request.form["fecha"]  # podemos obtener fecha, id_paciente
        id_paciente = request.form["id_paciente"]

        query = """INSERT INTO cita (id_doctor, id_paciente, fecha, hora)
                    VALUES (%s, %s, %s, %s)"""
        values = (id_doctor, id_paciente, fecha, hora)
        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

        flash("Has agendado tu cita exitosamente! 👩‍⚕️", "info")
        try:
            mensaje = client.messages.create(
                from_="+13394692386",
                body=f"VITAL HEALTH CARE\nTu cita ha sido registrada con fecha: {fecha} a las {hora // 10000}:00 horas, con el Dr. {nombre_doctor}",
                to=f"+52{current_user.telefono}",
            )
        except Exception as e:
            print(f"An Error ocurred {e}")
        
        return redirect(url_for("user_page", user=current_user.nombre))

    fecha = request.args.get("fecha")
    id_paciente = request.args.get("id_paciente")
    nombre_paciente = request.args.get("nombre_paciente")

    query = """
        SELECT doctor.nombre AS nombre_doctor, horario.id_doctor, horario.hora_entrada, horario.hora_salida
        FROM doctor
        INNER JOIN horario
        ON doctor.id = horario.id_doctor
    """

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        horarios_doctores = cursor.fetchall()

    # modfica los campos hora entrada y hora salida a tipos enteros
    for registro in horarios_doctores:
        registro["hora_entrada"] = int(registro["hora_entrada"].total_seconds() // 3600)
        registro["hora_salida"] = int(registro["hora_salida"].total_seconds() // 3600)

    # agregar un nuevo campo al diccionario horarios doctores con una lista de horas disponibles
    for registro in horarios_doctores:
        registro["horas_disponibles"] = [
            hora for hora in range(registro["hora_entrada"], registro["hora_salida"])
        ]

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_doctor, id_paciente, fecha, hora FROM cita WHERE fecha = '{}'".format(
                fecha
            )
        )
        citas = cursor.fetchall()

    # limpiar la lista de horas disponibles con las citas agendadas
    for registro in horarios_doctores:
        for cita in citas:
            if registro["id_doctor"] == cita["id_doctor"]:
                num = int(cita["hora"].total_seconds() // 3600)
                registro["horas_disponibles"].remove(num)

    horas_agendables = []

    for doctor in horarios_doctores:
        for hora_disponible in doctor["horas_disponibles"]:
            nuevo_elemento = {
                "nombre_doctor": doctor["nombre_doctor"],
                "id_doctor": doctor["id_doctor"],
                "hora_disponible": hora_disponible,
            }
            horas_agendables.append(nuevo_elemento)

    for item in horas_agendables:
        print(item)

    return render_template(
        "tabla_citas.html",
        horas_agendables=horas_agendables,
        num_citas=len(horas_agendables),
        fecha=fecha,
        id_paciente=id_paciente,
        nombre_paciente=nombre_paciente,
    )


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
@login_required
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

    return render_template("mostrar_quejas.html", datos=rows)


@app.route("/actualizar_horario", methods=["GET", "POST"])
@login_required
def horario_doctor():
    if request.method == "POST":
        get = request.form
        horario_entrada = get["hora_entrada"]
        horario_salida = get["hora_salida"]

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) AS hay_horario FROM horario WHERE id_doctor = '{}'".format(
                    current_user.id
                )
            )
            resultado = cursor.fetchone()

        if resultado["hay_horario"]:
            with mysql.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE horario SET hora_entrada = '{}', hora_salida = '{}' WHERE id_doctor = '{}'".format(
                        horario_entrada, horario_salida, current_user.id
                    )
                )
                conn.commit()
            flash("Horario actualizado exitosamente!", "info")
            return redirect(url_for("horario_doctor"))

        query = """INSERT INTO horario (hora_entrada, hora_salida, id_doctor) VALUES (%s, %s, %s)"""
        values = (horario_entrada, horario_salida, current_user.id)

        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

        flash("Horario registrado exitosamente!", "info")
        return redirect(url_for("horario_doctor"))
    return render_template("set_schedule.html")


@app.route("/citas")
@login_required
def ver_citas():
    query = """ SELECT nombre, fecha, DATE_FORMAT(hora, '%H:%i') AS hora
                FROM cita
                INNER JOIN paciente ON paciente.id = cita.id_paciente
                WHERE id_doctor = '{}'
                ORDER BY fecha, hora""".format(
        current_user.id
    )

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        datos = cursor.fetchall()
    return render_template("ver_citas.html", datos=datos)


@app.route("/eliminar/cita")
@login_required
def eliminar_cita():
    fecha = request.args.get("fecha")
    hora = request.args.get("hora")

    query = """DELETE FROM cita 
               WHERE id_doctor = %s
               AND fecha = %s
               AND hora = %s
            """
    values = (current_user.id, fecha, hora)

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()

    return redirect(url_for("ver_citas"))


@app.route("/subir_estudios", methods=["GET", "POST"])
@login_required
def upload_files():
    if request.method == "POST":
        id_paciente = request.form["id_paciente"]
        nombre_estudio = request.form["nombre_estudio"]

        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # debemos crear carpeta para cada paciente
            directorio = os.path.join(".", "uploads", f"{id_paciente}")
            if not os.path.exists(directorio):
                os.makedirs(directorio)

            path = "/".join([app.config["UPLOAD_FOLDER"], id_paciente, filename])

            file.save(path)  # save the file

            with mysql.connect() as conn:  # registrar en la base de datos la ruta de los archivos para cada paciente
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM estudios_medicos WHERE id_paciente = {} AND url_estudio = '{}'".format(
                        id_paciente, path
                    )
                )
                estudio_medico = cursor.fetchone()

                if not estudio_medico:
                    cursor.execute(
                        """INSERT INTO estudios_medicos (id_paciente, nombre_estudio, url_estudio)
                                    VALUES ({}, '{}', '{}')""".format(
                            id_paciente, nombre_estudio, filename
                        )
                    )
                    conn.commit()

            return redirect(
                url_for("download_file", name=filename, id_paciente=id_paciente)
            )

    query = """SELECT paciente.id AS id_paciente, paciente.nombre AS paciente, paciente.fecha_nacimiento, usuario.correo
               FROM paciente
               INNER JOIN usuario
               ON paciente.id_usuario = usuario.id
               ORDER BY paciente.nombre"""

    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        datos = cursor.fetchall()

    return render_template("subir_estudios.html", pacientes=datos)


@app.route("/uploads/<id_paciente>/<name>")
@login_required
def download_file(name, id_paciente):
    return send_from_directory(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{id_paciente}"), name
    )


@app.route("/expediente/formularios", methods=["GET", "POST"])
@login_required
def expediente_forms():
    if request.method == "POST":
        get = request.form

        if "nombre_alergia" in get.keys():
            query = """INSERT INTO alergia (id_paciente, nombre_alergia)
                        VALUES (%s, %s)"""    
            values = (get.get("id_paciente"), get.get("nombre_alergia"))
        
        elif "nombre_enfermedad" in get.keys():
            query = """INSERT INTO enfermedades_cronicas (id_paciente, nombre_enfermedad)
                        VALUES (%s, %s)"""       
            values = (get.get("id_paciente"), get.get("nombre_enfermedad"))
                
        elif "nombre_cirugia" in get.keys():
            query = """INSERT INTO historial_cirugias (id_paciente, nombre_cirugia, fecha)
                        VALUES (%s, %s, %s)"""
            values = (get.get("id_paciente"), get.get("nombre_cirugia"), get.get("fecha"))
                
        elif "nombre_medicamento" in get.keys():
            query = """INSERT INTO medicamentos_actuales 
                        (id_paciente, nombre_medicamento, duracion_tratamiento, frecuencia)
                        VALUES (%s, %s, %s, %s)"""
            values = (
                get.get("id_paciente"), 
                get.get("nombre_medicamento"), 
                get.get("duracion_tratamiento"),
                get.get("frecuencia")
            )
        
        with mysql.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
        flash("sus datos han sido insertados con exito")
        return redirect(url_for("mostrar_pacientes"))  
    
    id_paciente = request.args.get('id_paciente')
    return render_template("expediente_forms.html", id_paciente=id_paciente)


@app.route("/mostrar/pacientes", methods=["GET", "POST"])
@login_required
def mostrar_pacientes():
    if request.method == "POST":
        paciente_buscado = request.form["buscador"]
        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id AS id_paciente, nombre, fecha_nacimiento 
                FROM paciente 
                WHERE nombre LIKE '%{}%'
                """.format(paciente_buscado)
            )
            pacientes = cursor.fetchall()
        return render_template("mostrar_pacientes.html", pacientes=pacientes, length=len(pacientes))
    
    with mysql.connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id AS id_paciente, nombre, fecha_nacimiento FROM paciente ORDER BY nombre"
        )
        pacientes = cursor.fetchall()

    return render_template("mostrar_pacientes.html", pacientes=pacientes, length=len(pacientes))


@app.route('/expediente', methods=["POST"])
@login_required
def mostrar_expediente():
    if request.method == "POST":
    
        id_paciente = request.form['id_selected']
        
        with mysql.connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT nombre_alergia FROM alergia WHERE id_paciente = {}".format(id_paciente))
            alergias = cursor.fetchall()
            cursor.execute("SELECT * FROM historial_cirugias WHERE id_paciente = {}".format(id_paciente))
            historial_cirugias = cursor.fetchall()
            cursor.execute("SELECT * FROM medicamentos_actuales WHERE id_paciente = {}".format(id_paciente))
            medicamentos_actuales = cursor.fetchall()
            cursor.execute("SELECT * FROM enfermedades_cronicas WHERE id_paciente = {}".format(id_paciente))
            enfermedades_cronicas = cursor.fetchall()
            cursor.execute("SELECT * FROM estudios_medicos WHERE id_paciente = {}".format(id_paciente))
            estudios_medicos = cursor.fetchall()
            cursor.execute("SELECT * FROM paciente WHERE id = {}".format(id_paciente))
            paciente = cursor.fetchone()
            
        return render_template(
            "mostrar_expediente.html", 
            paciente=paciente,
            alergias=alergias, 
            historial_cirugias=historial_cirugias, 
            medicamentos_actuales=medicamentos_actuales, 
            enfermedades_cronicas=enfermedades_cronicas,
            estudios_medicos=estudios_medicos
        )
    
    abort(404)
    
@app.route('/crear_receta', methods=["GET", "POST"])
def crear_receta():
    if request.method == "POST":
        id_selected = request.form.get("id_selected")
        if id_selected:
            return render_template("form_receta.html", id_selected=id_selected)
        
        id_paciente = request.form.get("id_paciente")
        temperatura = request.form.get("temperatura")
        presion_arterial = request.form.get("presion_arterial")
        diagnostico = request.form.get("diagnostico")
        indicaciones_generales = request.form.get("indicaciones_generales")
        
        query = """
        INSERT INTO receta_medica (
            id_paciente,
            id_doctor, 
            temperatura, 
            presion_arterial, 
            diagnostico, 
            indicaciones_generales )
        VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            id_paciente, 
            current_user.id, 
            temperatura, 
            presion_arterial, 
            diagnostico, 
            indicaciones_generales )
        
        with mysql.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            
            cursor.execute("""
                SELECT telefono FROM paciente
                INNER JOIN usuario
                ON usuario.id = paciente.id_usuario
                WHERE paciente.id = {}""".format(id_paciente) )
            telefono = cursor.fetchone()
            
        cur_date = datetime.today().strftime("%d/%m/%Y")
        try:
            mensaje = client.messages.create(
                from_="+13394692386",
                body=f"""VITAL HEALTH CARE - RECETA:
                Diagnostico: {diagnostico}
                Indicaciones Generales: {indicaciones_generales}
                Niveles de presion arterial: {presion_arterial}
                Temperatura: {temperatura}
                fecha: {cur_date}""",
                to=f"+52{telefono['telefono']}"
            )
        except Exception as e:
            print(f"An Error ocurred {e}")
            
        return redirect(url_for("doctor_page", user=current_user.nombre))
    abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == "__main__":
    app.run()
