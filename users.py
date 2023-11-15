from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, nombre, correo, telefono, password) -> None:
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.password = password


class Doctor(UserMixin):
    def __init__(
        self, id, nombre, cedula, telefono, direccion, correo, password
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.cedula = cedula
        self.telefono = telefono
        self.direccion = direccion
        self.correo = correo
        self.password = password


class Secretary(UserMixin):
    def __init__(self, id, id_doctor, nombre, correo, password) -> None:
        self.id = id
        self.id_doctor = id_doctor
        self.nombre = nombre
        self.correo = correo
        self.password = password
