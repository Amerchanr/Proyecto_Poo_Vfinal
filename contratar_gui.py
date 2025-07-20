import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QDateEdit
)
from PyQt5.QtCore import QDate

class ContratarGUI(QWidget):
    """
    Ventana gráfica que permite contratar un producto financiero (Crédito o Ahorros)
    por parte de un cliente ya existente en la base de datos.
    """

    def __init__(self):
        """
        Constructor de la clase. Establece la conexión con la base de datos
        y configura la interfaz gráfica.
        """
        super().__init__()
        self.setWindowTitle("Contratar Producto")
        self.conn = sqlite3.connect("basemibanco.db")
        self.setStyleSheet(self.estilos())  # Aplicar estilos a los botones
        self.init_ui()

    def init_ui(self):
        """
        Define y organiza los elementos visuales de la interfaz de contratación.
        """
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Contratar producto financiero</h2>"))

        # Campo: ID del cliente
        self.input_id_cliente = QLineEdit()
        layout.addWidget(QLabel("ID del cliente existente:"))
        layout.addWidget(self.input_id_cliente)

        # ComboBox: productos disponibles
        self.productos_combo = QComboBox()
        layout.addWidget(QLabel("Seleccione el producto:"))
        layout.addWidget(self.productos_combo)

        # Capital y plazo
        self.input_capital = QLineEdit()
        self.input_plazo = QLineEdit()
        layout.addWidget(QLabel("Capital inicial (>= 100000 para ahorro):"))
        layout.addWidget(self.input_capital)
        layout.addWidget(QLabel("Plazo en meses (0 si es ahorro):"))
        layout.addWidget(self.input_plazo)

        # Fecha de entrega
        self.fecha_entrega = QDateEdit()
        self.fecha_entrega.setCalendarPopup(True)
        self.fecha_entrega.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Fecha de entrega del producto:"))
        layout.addWidget(self.fecha_entrega)

        # Botón: contratar producto
        btn = QPushButton("Contratar")
        btn.clicked.connect(self.contratar)
        layout.addWidget(btn)

        self.setLayout(layout)

        # Cargar productos desde base de datos al ComboBox
        self.cargar_productos()

    def cargar_productos(self):
        """
        Llena el ComboBox con los productos disponibles en la base de datos.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT NoIdProducto, NombreProducto, TipoProducto FROM PRODUCTOS")
        productos = cursor.fetchall()
        self.productos_combo.clear()
        for idp, nombre, tipo in productos:
            tipo_str = "Crédito" if tipo == 1 else "Ahorros"
            self.productos_combo.addItem(f"{idp} - {nombre} ({tipo_str})", (idp, tipo))

    def contratar(self):
        """
        Registra un nuevo producto contratado por un cliente, validando los datos según el tipo de producto.
        """
        # Leer ID cliente y producto seleccionado
        id_cliente = self.input_id_cliente.text()
        idp, tipo = self.productos_combo.currentData()

        # Leer capital y plazo
        try:
            capital = float(self.input_capital.text())
            plazo = int(self.input_plazo.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Capital y plazo deben ser numéricos.")
            return

        # Obtener la fecha en formato "dd/mm/yyyy"
        fecha = self.fecha_entrega.date().toString("dd/MM/yyyy")

        # Validar que el cliente exista en la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM CLIENTES WHERE noIdCliente=?", (id_cliente,))
        if not cursor.fetchone():
            QMessageBox.warning(self, "Error", "El cliente no existe.")
            return

        # Validaciones específicas según tipo de producto
        if tipo == 1:  # Crédito
            if capital <= 0 or plazo <= 0:
                QMessageBox.warning(self, "Error", "Crédito debe tener capital y plazo > 0.")
                return
        else:  # Ahorros
            if capital < 100000:
                QMessageBox.warning(self, "Error", "Ahorros mínimo de $100.000")
                return
            plazo = 0  # Ahorros no tiene plazo

        # Insertar registro en tabla ProductosContratados
        saldo = capital
        plazo_pend = plazo
        try:
            cursor.execute('''
                INSERT INTO PRODUCTOSCONTRATADOS
                (idProducto, idCliente, capitalInicial, plazoMeses, fechaEntrega, saldoCapital, sumatoriaInteresesPagados, plazoPendiente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (idp, id_cliente, capital, plazo, fecha, saldo, 0, plazo_pend))
            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Producto contratado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def estilos(self):
        """
        Estilos para los botones: azul por defecto, rojo al presionar.
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
