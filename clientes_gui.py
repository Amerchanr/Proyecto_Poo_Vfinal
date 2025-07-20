import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt

class ClientesGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes – Neobanco Digital")
        self.setGeometry(200, 100, 600, 400)
        self.conn = sqlite3.connect("basemibanco.db")
        self.init_ui()

    def init_ui(self):
        # Estilos para botones
        self.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #dc3545;
            }
        """)

        layout = QVBoxLayout()

        # Grupo registro cliente
        group_reg = QGroupBox("Registrar nuevo cliente")
        reg_layout = QVBoxLayout()

        self.input_id = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_apellido = QLineEdit()
        self.input_direccion = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_correo = QLineEdit()

        reg_layout.addWidget(QLabel("ID Cliente:")); reg_layout.addWidget(self.input_id)
        reg_layout.addWidget(QLabel("Nombre:")); reg_layout.addWidget(self.input_nombre)
        reg_layout.addWidget(QLabel("Apellido:")); reg_layout.addWidget(self.input_apellido)
        reg_layout.addWidget(QLabel("Dirección:")); reg_layout.addWidget(self.input_direccion)
        reg_layout.addWidget(QLabel("Teléfono:")); reg_layout.addWidget(self.input_telefono)
        reg_layout.addWidget(QLabel("Correo electrónico:")); reg_layout.addWidget(self.input_correo)

        btn_guardar = QPushButton("Registrar cliente")
        btn_guardar.clicked.connect(self.registrar_cliente)
        reg_layout.addWidget(btn_guardar)
        group_reg.setLayout(reg_layout)

        # Grupo de consulta y actualización
        group_cons = QGroupBox("Consultar / Actualizar cliente")
        cons_layout = QVBoxLayout()

        self.input_consulta = QLineEdit()
        btn_consultar = QPushButton("Consultar")
        btn_consultar.clicked.connect(self.consultar_cliente)
        cons_layout.addWidget(QLabel("ID Cliente a consultar:"))
        cons_layout.addWidget(self.input_consulta)
        cons_layout.addWidget(btn_consultar)

        self.resultado = QLabel("")
        self.resultado.setWordWrap(True)
        cons_layout.addWidget(self.resultado)

        self.input_nueva_direccion = QLineEdit()
        btn_actualizar = QPushButton("Actualizar dirección")
        btn_actualizar.clicked.connect(self.actualizar_direccion)
        cons_layout.addWidget(QLabel("Nueva dirección:"))
        cons_layout.addWidget(self.input_nueva_direccion)
        cons_layout.addWidget(btn_actualizar)

        group_cons.setLayout(cons_layout)

        layout.addWidget(group_reg)
        layout.addWidget(group_cons)
        self.setLayout(layout)
        
    def obtener_correo_valido(self):
        correo = self.input_correo.text().strip()
        partes = correo.split("@")
        if len(partes) == 2 and "." in partes[1]:
            return correo
        else:
            QMessageBox.warning(
                self,
                "Correo inválido",
                "Ingrese un correo válido con formato usuario@dominio.com"
            )
            return None

    def registrar_cliente(self):
        try:
            # Validar el correo antes de crear la tupla
            correo_valido = self.obtener_correo_valido()
            if correo_valido is None:
                return  # No continúa si el correo es inválido
            
            cliente = (
                int(self.input_id.text()),
                self.input_nombre.text(),
                self.input_apellido.text(),
                self.input_direccion.text(),
                int(self.input_telefono.text()),
                correo_valido
            )

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO CLIENTES VALUES (?, ?, ?, ?, ?, ?)", cliente)
            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Cliente registrado correctamente.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Ya existe un cliente con ese ID.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Verifica que el ID y Teléfono sean numéricos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def consultar_cliente(self):
        id_cliente = self.input_consulta.text()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM CLIENTES WHERE noIdCliente=?", (id_cliente,))
        resultado = cursor.fetchone()
        if resultado:
            self.resultado.setText(
                f"<b>ID:</b> {resultado[0]}<br><b>Nombre:</b> {resultado[1]} {resultado[2]}<br>"
                f"<b>Dirección:</b> {resultado[3]}<br><b>Tel:</b> {resultado[4]}<br><b>Correo:</b> {resultado[5]}"
            )
        else:
            self.resultado.setText("Cliente no encontrado.")

    def actualizar_direccion(self):
        id_cliente = self.input_consulta.text()
        nueva_dir = self.input_nueva_direccion.text()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE CLIENTES SET direccion=? WHERE noIdCliente=?", (nueva_dir, id_cliente))
        if cursor.rowcount > 0:
            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Dirección actualizada.")
        else:
            QMessageBox.warning(self, "Error", "Cliente no encontrado.")
