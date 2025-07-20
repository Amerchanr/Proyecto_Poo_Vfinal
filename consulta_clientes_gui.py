import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,QPushButton, QTableWidgetItem, QLabel, QAbstractItemView
)
from PyQt5.QtCore import Qt

class ConsultaClientesGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consulta Total de Clientes – Neobanco Digital")
        self.setGeometry(200, 100, 800, 500)
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

        titulo = QLabel("Consulta Total de Clientes")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #003366;")
        layout.addWidget(titulo)
        
        btn_consultarClientes = QPushButton("Consultar Clientes")
        btn_consultarClientes.clicked.connect(self.cargar_datos)
        layout.addWidget(btn_consultarClientes)


                            
        self.tabla = QTableWidget()
        self.cargar_datos()
        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def cargar_datos(self):
        cursor = self.conn.cursor()

        # Obtener número de filas
        cursor.execute("SELECT COUNT(*) FROM CLIENTES")
        total_filas = cursor.fetchone()[0]

        # Obtener los datos de todos los clientes
        cursor.execute("SELECT * FROM CLIENTES")
        datos = cursor.fetchall()

        # Definir columnas
        columnas = ["ID Cliente", "Nombre", "Apellido", "Dirección", "Teléfono", "Correo"]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.setRowCount(total_filas)

        for fila_idx, fila_dato in enumerate(datos):
            for col_idx, valor in enumerate(fila_dato):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Hacerlo no editable
                self.tabla.setItem(fila_idx, col_idx, item)

        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSortingEnabled(True)
        self.tabla.resizeColumnsToContents()
