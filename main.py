import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from tablas import crearTablas

from clientes_gui import ClientesGUI
from productos_gui import ProductosGUI
from contratar_gui import ContratarGUI
from transacciones_gui import TransaccionesGUI
from consulta_clientes_gui import ConsultaClientesGUI



#creacion y conexion con la bas ede datos
def conexionBD():
    try:
        # se crea repositorio fisico-objeto de conexcion a la base de datos 
        con=sqlite3.connect('basemibanco.db')
        print('la conexion fue exitosa')
        return con
    except Error:
        print(Error)
#cierre conexion

def cerrarBD(con):
    con.close()


class NeobancoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neobanco Digital S.A.")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(self.estilos())  
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # ======= Menú lateral =======
        self.menu = QListWidget()
        self.menu.setFixedWidth(200)
        self.menu.setFont(QFont("Segoe UI Semibold", 12))
        self.menu.addItem(QListWidgetItem("Inicio"))
        self.menu.addItem(QListWidgetItem("Clientes"))
        self.menu.addItem(QListWidgetItem("Consulta Clientes"))  
        self.menu.addItem(QListWidgetItem("Productos"))
        self.menu.addItem(QListWidgetItem("Contratar Producto"))
        self.menu.addItem(QListWidgetItem("Transacciones"))
        self.menu.addItem(QListWidgetItem("Salir"))
        self.menu.setCurrentRow(0)
        self.menu.currentRowChanged.connect(self.change_view)

        # ======= Vista principal (derecha) =======
        self.stack = QStackedWidget()

        # Vista 0: Bienvenida
        bienvenida = QWidget()
        bienvenida_layout = QVBoxLayout()
        bienvenida_layout.setAlignment(Qt.AlignCenter)

        titulo = QLabel("Neobanco Digital S.A.")
        fuente_titulo = QFont("Segoe UI", 36)
        fuente_titulo.setBold(True)
        titulo.setFont(fuente_titulo)
        titulo.setStyleSheet("color: #002244;")
        titulo.setAlignment(Qt.AlignCenter)

        grupo = QLabel("""
<b>Integrantes del Grupo:</b><br>
Johan Santiago Monroy Bolaños<br>
Arnold Joseph Merchan Rojas<br>
William Alexander Bohorquez<br><br>
<b>Profesor:</b><br>
Jorge Enrique Amaya Cala<br>
jeamayac@unal.edu.co
""")
        grupo.setFont(QFont("Segoe UI", 13))
        grupo.setAlignment(Qt.AlignCenter)

        bienvenida_layout.addWidget(titulo)
        bienvenida_layout.addWidget(grupo)
        bienvenida.setLayout(bienvenida_layout)

        # Agregar vistas al stack (en el mismo orden del menú)
        self.stack.addWidget(bienvenida)                  # Índice 0
        self.stack.addWidget(ClientesGUI())               # Índice 1
        self.stack.addWidget(ConsultaClientesGUI())       # Índice 2
        self.stack.addWidget(ProductosGUI())              # Índice 3
        self.stack.addWidget(ContratarGUI())              # Índice 4
        self.stack.addWidget(TransaccionesGUI())          # Índice 5
        self.stack.addWidget(QWidget())                   # Índice 6: Salir

        # Organizar Layout Principal
        layout.addWidget(self.menu)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def change_view(self, index):
        if index == 6:  # Salir
            sys.exit()
        self.stack.setCurrentIndex(index)

    def estilos(self):
        """
        Retorna una hoja de estilos (QSS) para mejorar la estética del menú y botones.
        """
        return """
        QWidget {
            background-color: #f5f5f5;
        }
        QListWidget {
            background-color: #003366;
            color: white;
            font-size: 16px;
        }
        QListWidget::item:selected {
            background-color: white;
            color: #003366;
            font-weight: bold;
        }
        QLabel {
            color: #003366;
        }
        """

if __name__ == "__main__":
    Micon = conexionBD()
    crearTablas(Micon)
    app = QApplication(sys.argv)
    win = NeobancoApp()
    win.show()
    sys.exit(app.exec_())
    cerrarBD(Micon)
