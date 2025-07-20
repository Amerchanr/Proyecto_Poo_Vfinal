import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit, QFileDialog
)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

class TransaccionesGUI(QWidget):
    """
    Interfaz gráfica que permite realizar operaciones de transacciones bancarias
    para cuentas de crédito o ahorro dentro del sistema Neobanco Digital.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transacciones – Créditos y Ahorros")
        self.conn = sqlite3.connect("basemibanco.db")
        self.setStyleSheet(self.estilos())  # Aplicar estilo a los botones
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Transacciones del Neobanco</h2>"))

        # Sección: Consultar cuota de crédito
        layout.addWidget(QLabel("<b>Consultar cuota crédito</b>"))
        self.id_credito = QLineEdit()
        layout.addWidget(QLabel("ID de cuenta de crédito:"))
        layout.addWidget(self.id_credito)

        btn_cuota = QPushButton("Consultar cuota actual")
        btn_cuota.clicked.connect(self.consultar_cuota)
        layout.addWidget(btn_cuota)

        # Sección: Pagar cuota crédito
        layout.addWidget(QLabel("<b>Pagar cuota crédito</b>"))
        btn_pagar = QPushButton("Pagar cuota")
        btn_pagar.clicked.connect(self.pagar_cuota)
        layout.addWidget(btn_pagar)

        # Sección: Consultar saldo de ahorro
        layout.addWidget(QLabel("<b>Consultar saldo de ahorro</b>"))
        self.id_ahorro = QLineEdit()
        layout.addWidget(QLabel("ID de cuenta de ahorro:"))
        layout.addWidget(self.id_ahorro)

        btn_saldo = QPushButton("Consultar saldo proyectado")
        btn_saldo.clicked.connect(self.consultar_saldo_ahorros)
        layout.addWidget(btn_saldo)

        # Sección: Transacción ahorro
        layout.addWidget(QLabel("<b>Transacción de ahorro (consignar/retirar)</b>"))
        self.valor = QLineEdit()
        layout.addWidget(QLabel("Valor de transacción (+ consignar / - retirar):"))
        layout.addWidget(self.valor)

        btn_transaccion = QPushButton("Realizar transacción")
        btn_transaccion.clicked.connect(self.transaccion_ahorros)
        layout.addWidget(btn_transaccion)

        # Sección: Recibo
        layout.addWidget(QLabel("<b>Recibo</b>"))
        self.recibo = QTextEdit()
        self.recibo.setReadOnly(True)
        layout.addWidget(self.recibo)

        # Botón para guardar recibo en PDF
        btn_pdf = QPushButton("Guardar recibo en PDF")
        btn_pdf.clicked.connect(self.guardar_pdf)
        layout.addWidget(btn_pdf)

        self.setLayout(layout)

    def guardar_pdf(self):
        """
        Guarda el contenido del recibo en un archivo PDF usando QPrinter.
        """
        contenido = self.recibo.toPlainText()
        if not contenido.strip():
            QMessageBox.warning(self, "Aviso", "No hay contenido en el recibo para guardar.")
            return

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar recibo como PDF", "", "Archivos PDF (*.pdf)")
        if ruta:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(ruta)

            doc = QTextDocument()
            doc.setPlainText(contenido)
            doc.print_(printer)

            QMessageBox.information(self, "PDF Guardado", f"Recibo guardado exitosamente en:\n{ruta}")

    def tipo_producto(self, cuenta):
        c = self.conn.cursor()
        c.execute("""
            SELECT P.TipoProducto
            FROM PRODUCTOSCONTRATADOS PC
            JOIN PRODUCTOS P ON PC.idProducto = P.NoIdProducto
            WHERE PC.idCuentaCredito = ?
        """, (cuenta,))
        r = c.fetchone()
        return r[0] if r else None

    def consultar_cuota(self):
        idc = self.id_credito.text()
        if self.tipo_producto(idc) != 1:
            self.recibo.setText("No es un crédito.")
            return

        c = self.conn.cursor()
        c.execute("""
            SELECT saldoCapital, plazoPendiente, P.Remuneracion
            FROM PRODUCTOSCONTRATADOS PC
            JOIN PRODUCTOS P ON PC.idProducto = P.NoIdProducto
            WHERE PC.idCuentaCredito = ?
        """, (idc,))
        datos = c.fetchone()
        if not datos or datos[1] <= 0:
            self.recibo.setText("No hay cuotas pendientes.")
            return

        saldo, plazo, interes = datos
        capital = saldo / plazo
        interes_mensual = saldo * (interes / 100)
        total = capital + interes_mensual

        self.recibo.setText(f"""
        CUOTA A PAGAR:
        Capital: {capital:.2f}
        Interés: {interes_mensual:.2f}
        Total: {total:.2f}
        Plazo pendiente: {plazo} meses
        """)

    def pagar_cuota(self):
        idc = self.id_credito.text()
        if self.tipo_producto(idc) != 1:
            self.recibo.setText("No es un crédito.")
            return

        c = self.conn.cursor()
        c.execute("""
            SELECT saldoCapital, plazoPendiente, P.Remuneracion
            FROM PRODUCTOSCONTRATADOS PC
            JOIN PRODUCTOS P ON PC.idProducto = P.NoIdProducto
            WHERE PC.idCuentaCredito = ?
        """, (idc,))
        datos = c.fetchone()
        if not datos or datos[1] <= 0:
            self.recibo.setText("Crédito ya pagado.")
            return

        saldo, plazo, interes = datos
        capital = saldo / plazo
        interes_mes = saldo * (interes / 100)
        total = capital + interes_mes

        nuevo_saldo = max(0, saldo - capital)
        nuevo_plazo = max(0, plazo - 1)
        fecha = datetime.now().strftime('%Y-%m-%d')

        c.execute("INSERT INTO TRANSACCIONES VALUES(NULL,?,?,?)", (idc, fecha, total))
        id_transaccion = c.lastrowid

        c.execute("""
            UPDATE PRODUCTOSCONTRATADOS
            SET saldoCapital=?, plazoPendiente=?, sumatoriaInteresesPagados=sumatoriaInteresesPagados+?
            WHERE idCuentaCredito=?
        """, (nuevo_saldo, nuevo_plazo, interes_mes, idc))
        self.conn.commit()

        c.execute("SELECT idCliente FROM PRODUCTOSCONTRATADOS WHERE idCuentaCredito=?", (idc,))
        id_cliente = c.fetchone()[0]
        c.execute("SELECT nombre, apellido FROM CLIENTES WHERE noIdCliente=?", (id_cliente,))
        nombre, apellido = c.fetchone()

        self.recibo.setText(f"""
        ====== RECIBO DE PAGO CRÉDITO ======
        Factura Número: {id_transaccion}
        Cliente: {nombre} {apellido}
        Valor pagado: {total:.2f}
        Nuevo saldo: {nuevo_saldo:.2f}
        Plazo restante: {nuevo_plazo} meses
        ====================================
        """)

    def consultar_saldo_ahorros(self):
        idc = self.id_ahorro.text()
        if self.tipo_producto(idc) != 2:
            self.recibo.setText("No es una cuenta de ahorros.")
            return

        c = self.conn.cursor()
        c.execute("""
            SELECT saldoCapital, P.Remuneracion
            FROM PRODUCTOSCONTRATADOS PC
            JOIN PRODUCTOS P ON PC.idProducto = P.NoIdProducto
            WHERE PC.idCuentaCredito = ?
        """, (idc,))
        datos = c.fetchone()
        if not datos:
            self.recibo.setText("Cuenta no encontrada.")
            return

        saldo, interes = datos
        proyeccion = saldo * (1 + interes / 100)
        self.recibo.setText(f"""
        SALDO AHORROS:
        Saldo actual: {saldo:.2f}
        Interés mensual: {interes}%
        Proyección fin de mes: {proyeccion:.2f}
        """)

    def transaccion_ahorros(self):
        idc = self.id_ahorro.text()
        if self.tipo_producto(idc) != 2:
            self.recibo.setText("No es una cuenta de ahorros.")
            return

        try:
            val = float(self.valor.text())
        except ValueError:
            self.recibo.setText("Error: valor inválido.")
            return

        c = self.conn.cursor()
        c.execute("SELECT saldoCapital FROM PRODUCTOSCONTRATADOS WHERE idCuentaCredito=?", (idc,))
        row = c.fetchone()
        if not row:
            self.recibo.setText("Cuenta no encontrada.")
            return

        saldo_actual = row[0]
        nuevo_saldo = saldo_actual + val

        if nuevo_saldo < 0:
            self.recibo.setText("Fondos insuficientes.")
            return

        fecha = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO TRANSACCIONES VALUES(NULL,?,?,?)", (idc, fecha, val))
        id_transaccion = c.lastrowid

        c.execute("UPDATE PRODUCTOSCONTRATADOS SET saldoCapital=? WHERE idCuentaCredito=?", (nuevo_saldo, idc))
        self.conn.commit()

        c.execute("SELECT idCliente FROM PRODUCTOSCONTRATADOS WHERE idCuentaCredito=?", (idc,))
        id_cliente = c.fetchone()[0]
        c.execute("SELECT nombre, apellido FROM CLIENTES WHERE noIdCliente=?", (id_cliente,))
        nombre, apellido = c.fetchone()

        self.recibo.setText(f"""
        ====== RECIBO TRANSACCIÓN AHORROS ======
        Nº Factura: {id_transaccion}
        Cliente: {nombre} {apellido}
        Fecha: {fecha}
        Valor transacción: {val:.2f}
        Nuevo saldo: {nuevo_saldo:.2f}
        ========================================
        """)

    def estilos(self):
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
