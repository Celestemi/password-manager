from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QWidget, QListWidget, QInputDialog
)
from PySide6.QtCore import Qt
from cryptography.fernet import Fernet
import os
import json
from datetime import datetime

# Generar y guardar clave de cifrado
def generate_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("key.key", "rb") as key_file:
            key = key_file.read()
    return Fernet(key)

cipher = generate_key()

# Función para registrar acciones en el historial
def log_action(action):
    with open("historial.log", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")

# Cargar usuarios
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    return {}

users = load_users()

# Guardar usuarios
def save_users():
    with open("users.json", "w") as file:
        json.dump(users, file)

# Cargar contraseñas
def load_passwords():
    if os.path.exists("passwords.json"):
        with open("passwords.json", "rb") as file:
            encrypted_data = file.read()
            try:
                return json.loads(cipher.decrypt(encrypted_data).decode())
            except:
                return {}
    return {}

passwords = load_passwords()

# Guardar contraseñas
def save_passwords():
    encrypted_data = cipher.encrypt(json.dumps(passwords).encode())
    with open("passwords.json", "wb") as file:
        file.write(encrypted_data)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.resize(300, 200)

        # Estilos CSS para la interfaz
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ba0;
            }
        """)

        layout = QVBoxLayout()

        self.username_label = QLabel("Usuario:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Iniciar Sesión")
        self.register_button = QPushButton("Registrarse")

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username in users and users[username] == password:
            log_action(f"Inicio de sesión exitoso: {username}")
            QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
            self.open_password_manager()
        else:
            log_action(f"Inicio de sesión fallido: {username}")
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def register(self):
        username, ok1 = QInputDialog.getText(self, "Registro", "Elige un nombre de usuario:")
        if not ok1 or not username:
            return

        if username in users:
            QMessageBox.critical(self, "Error", "Este usuario ya existe.")
            return

        password, ok2 = QInputDialog.getText(self, "Registro", "Elige una contraseña:", QLineEdit.Password)
        if not ok2 or not password:
            return

        users[username] = password
        save_users()
        log_action(f"Nuevo usuario registrado: {username}")
        QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")

    def open_password_manager(self):
        self.manager = PasswordManagerWindow()
        self.manager.show()
        self.close()


class PasswordManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Contraseñas")
        self.resize(400, 300)

        # Estilos CSS para la interfaz
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: 2px solid #27ae60;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QVBoxLayout, QHBoxLayout {
                margin: 10px;
            }
        """)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.add_button = QPushButton("Añadir")
        self.view_button = QPushButton("Ver")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.log_button = QPushButton("Historial")

        self.add_button.clicked.connect(self.add_password)
        self.view_button.clicked.connect(self.view_password)
        self.update_button.clicked.connect(self.update_password)
        self.delete_button.clicked.connect(self.delete_password)
        self.log_button.clicked.connect(self.view_log)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.log_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for site in passwords.keys():
            self.list_widget.addItem(site)

    def add_password(self):
        site, ok1 = QInputDialog.getText(self, "Añadir Contraseña", "Nombre del sitio:")
        if not ok1 or not site:
            return

        user, ok2 = QInputDialog.getText(self, "Añadir Contraseña", "Usuario:")
        if not ok2 or not user:
            return

        password, ok3 = QInputDialog.getText(self, "Añadir Contraseña", "Contraseña:", QLineEdit.Password)
        if not ok3 or not password:
            return

        passwords[site] = {"usuario": user, "contraseña": password}
        save_passwords()
        log_action(f"Contraseña añadida para el sitio: {site}")
        self.update_list()

    def view_password(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "No se seleccionó ninguna contraseña para ver.")
            return

        site = selected.text()
        user = passwords[site]["usuario"]
        password = passwords[site]["contraseña"]
        log_action(f"Contraseña vista para el sitio: {site}")
        QMessageBox.information(self, "Detalles", f"Usuario: {user}\nContraseña: {password}")

    def update_password(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "No se seleccionó ninguna contraseña para actualizar.")
            return

        site = selected.text()
        new_password, ok = QInputDialog.getText(self, "Actualizar Contraseña", "Nueva contraseña:", QLineEdit.Password)
        if not ok or not new_password:
            return

        passwords[site]["contraseña"] = new_password
        save_passwords()
        log_action(f"Contraseña actualizada para el sitio: {site}")
        QMessageBox.information(self, "Éxito", f"Contraseña actualizada para '{site}'.")

    def delete_password(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "No se seleccionó ninguna contraseña para eliminar.")
            return

        site = selected.text()
        confirm = QMessageBox.question(self, "Confirmar", f"¿Estás seguro de eliminar la contraseña para '{site}'?")
        if confirm == QMessageBox.Yes:
            del passwords[site]
            save_passwords()
            log_action(f"Contraseña eliminada para el sitio: {site}")
            self.update_list()

    def view_log(self):
        if not os.path.exists("historial.log"):
            QMessageBox.information(self, "Historial", "No hay acciones registradas.")
            return

        with open("historial.log", "r") as log_file:
            logs = log_file.readlines()

        log_text = "\n".join(logs)
        QMessageBox.information(self, "Historial de Acciones", log_text)


app = QApplication([])
window = LoginWindow()
window.show()
app.exec()
