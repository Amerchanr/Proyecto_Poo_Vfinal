import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QGroupBox
)

class ProductosGUI(QWidget):
    """
    Clase que representa la interfaz gráfica para la gestión de productos en el sistema Neobanco.
    Permite crear, consultar y listar productos financieros como créditos o cuentas de ahorros.
    """

    def __init__(self):
        """
        Constructor de la ventana. Inicializa la conexión con la base de datos y configura la UI.
        """
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.conn = sqlite3.connect("basemibanco.db")
        self.setStyleSheet(self.estilos())  # Aplicar estilos a botones
        self.init_ui()

    def init_ui(self):
        """
        Define toda la estructura visual de la interfaz gráfica con PyQt5.
        """
        layout = QVBoxLayout()

        # ======= Grupo: Crear Producto =======
        group_crear = QGroupBox("Crear nuevo producto")
        crear_layout = QVBoxLayout()

        # Campos de entrada para nuevo producto
        self.input_id = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_tipo = QLineEdit()
        self.input_remun = QLineEdit()

        crear_layout.addWidget(QLabel("ID Producto:")); crear_layout.addWidget(self.input_id)
        crear_layout.addWidget(QLabel("Nombre del producto:")); crear_layout.addWidget(self.input_nombre)
        crear_layout.addWidget(QLabel("Tipo (1=Crédito, 2=Ahorros):")); crear_layout.addWidget(self.input_tipo)
        crear_layout.addWidget(QLabel("Tasa de Interés (%):")); crear_layout.addWidget(self.input_remun)

        # Botón para guardar producto
        btn_guardar = QPushButton("Guardar producto")
        btn_guardar.clicked.connect(self.insertar_producto)
        crear_layout.addWidget(btn_guardar)

        group_crear.setLayout(crear_layout)
        layout.addWidget(group_crear)

        # ======= Grupo: Consultar Producto =======
        group_consulta = QGroupBox("Consultar producto")
        consulta_layout = QVBoxLayout()

        self.input_consulta = QLineEdit()
        btn_consultar = QPushButton("Buscar")
        btn_consultar.clicked.connect(self.consultar_producto)
        self.resultado = QLabel("")

        consulta_layout.addWidget(QLabel("ID producto a consultar:"))
        consulta_layout.addWidget(self.input_consulta)
        consulta_layout.addWidget(btn_consultar)
        consulta_layout.addWidget(self.resultado)

        group_consulta.setLayout(consulta_layout)
        layout.addWidget(group_consulta)

        # ======= Tabla: Listar productos registrados =======
        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Interés %"])

        btn_listar = QPushButton("Listar productos")
        btn_listar.clicked.connect(self.listar_productos)

        layout.addWidget(QLabel("<h3>Listado de Productos</h3>"))
        layout.addWidget(btn_listar)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def insertar_producto(self):
        """
        Inserta un nuevo producto en la base de datos si la información es válida.
        Realiza validaciones del tipo y evita IDs repetidos.
        """
        try:
            datos = (
                int(self.input_id.text()),
                self.input_nombre.text(),
                int(self.input_tipo.text()),
                float(self.input_remun.text())
            )

            # Validación: tipo debe ser 1 o 2
            if datos[2] not in (1, 2):
                QMessageBox.warning(self, "Error", "El tipo debe ser 1 (Crédito) o 2 (Ahorros).")
                return

            c = self.conn.cursor()
            c.execute("INSERT INTO PRODUCTOS VALUES (?, ?, ?, ?)", datos)
            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Producto creado correctamente.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El ID ya existe o el nombre está duplicado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def consultar_producto(self):
        """
        Consulta un producto en la base de datos por su ID e imprime la información en pantalla.
        """
        idp = self.input_consulta.text()
        c = self.conn.cursor()
        c.execute("SELECT * FROM PRODUCTOS WHERE NoIdProducto=?", (idp,))
        fila = c.fetchone()

        if fila:
            tipo = "Crédito" if fila[2] == 1 else "Ahorros"
            self.resultado.setText(
                f"<b>ID:</b> {fila[0]}<br><b>Nombre:</b> {fila[1]}<br><b>Tipo:</b> {tipo}<br><b>Remuneración:</b> {fila[3]}%"
            )
        else:
            self.resultado.setText("Producto no encontrado.")

    def listar_productos(self):
        """
        Lista todos los productos en una tabla visual. Muestra ID, nombre, tipo y tasa de interés.
        """
        self.tabla.setRowCount(0)
        c = self.conn.cursor()
        c.execute("SELECT * FROM PRODUCTOS")
        for fila in c.fetchall():
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            tipo = "Crédito" if fila[2] == 1 else "Ahorros"
            self.tabla.setItem(row, 0, QTableWidgetItem(str(fila[0])))
            self.tabla.setItem(row, 1, QTableWidgetItem(fila[1]))
            self.tabla.setItem(row, 2, QTableWidgetItem(tipo))
            self.tabla.setItem(row, 3, QTableWidgetItem(str(fila[3])))

    def estilos(self):
        """
        Estilos para los botones: azul por defecto, rojo cuando se presionan.
        """
        return """
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 5px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #005fa3;
        }
        QPushButton:pressed {
            background-color: #c0392b;
        }
        """
