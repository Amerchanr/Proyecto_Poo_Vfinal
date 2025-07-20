import sqlite3
from sqlite3 import Error

# === Conexión ===

def conexionBD():
    try:
        con = sqlite3.connect('basemibanco.db')
        print('La conexión fue exitosa')
        return con
    except Error as e:
        print(f"Error: {e}")

def cerrarDB(con):
    con.close()
    print('Conexión cerrada')


class Transacciones:
    # === Menú ===

    def menuTransacciones(self,con):
        while True:
            op = input('''
    ======= MENU TRANSACCIONES =======

    1. Consultar cuota a pagar
    2. Pagar cuota
    3. Consultar saldo proyectado (Ahorros)
    4. Consignar o retirar (Ahorros)
    5. Salir

    Seleccione una opción >>>: 
    ''')
            if op == '1':
                consultarCuota(con)
            elif op == '2':
                pagarCuota(con)
            elif op == '3':
                consultarSaldoAhorros(con)
            elif op == '4':
                transaccionAhorros(con)
            elif op == '5':
                print("Saliendo del menú de Transacciones...")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

    # === Consultar cuota a pagar ===

    def consultarCuota(self,con):
        idCuenta = input("Número de cuenta de crédito: ")
        tipo = obtenerTipoProducto_deCuenta(con, idCuenta)
        if tipo != 1:
            print("Error: Solo válido para créditos.")
            return

        datos = obtenerDatosCredito(con, idCuenta)
        if not datos:
            print("No se encontró la cuenta de crédito.")
            return

        saldo, plazoPendiente, interes = datos
        if plazoPendiente <= 0:
            print("El crédito ya está pagado en su totalidad.")
            return

        cuotaCapital = saldo / plazoPendiente
        cuotaInteres = saldo * (interes / 100)
        cuotaTotal = cuotaCapital + cuotaInteres

        print(f'''
    === CUOTA A PAGAR ===
    Capital: {cuotaCapital:.2f}
    Interés: {cuotaInteres:.2f}
    Total: {cuotaTotal:.2f}
    Plazo pendiente: {plazoPendiente} meses
    ======================''')

    # === Pagar cuota ===

    def pagarCuota(self,con):
        idCuenta = input("Número de cuenta de crédito: ")
        tipo = obtenerTipoProducto_deCuenta(con, idCuenta)
        if tipo != 1:
            print("Error: Solo válido para créditos.")
            return

        datos = obtenerDatosCredito(con, idCuenta)
        if not datos:
            print("No se encontró la cuenta de crédito.")
            return

        saldo, plazoPendiente, interes = datos
        if plazoPendiente <= 0:
            print("El crédito ya está pagado.")
            return

        fechaPago = input("Fecha de pago (YYYY-MM-DD): ").strip()
        mes_actual = fechaPago[:7]

        cursor = con.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM Transacciones
            WHERE idCuentaCredito = ? AND substr(fechaPago, 1, 7) = ?
        ''', (idCuenta, mes_actual))
        if cursor.fetchone()[0] > 0:
            print("Ya existe un pago para este mes.")
            return

        cuotaCapital = saldo / plazoPendiente
        cuotaInteres = saldo * (interes / 100)
        cuotaTotal = cuotaCapital + cuotaInteres

        print(f"Cuota mensual: Capital: {cuotaCapital:.2f}, Interés: {cuotaInteres:.2f}, Total: {cuotaTotal:.2f}")

        try:
            valor = float(input("Valor a pagar: "))
        except ValueError:
            print("Error: Valor inválido.")
            return

        saldoNuevo = max(0, saldo - (valor - cuotaInteres))
        plazoNuevo = max(0, plazoPendiente - 1)

        interesesAnt = cursor.execute(
            "SELECT sumatoriaInteresesPagados FROM ProductosContratados WHERE idCuentaCredito = ?",
            (idCuenta,)
        ).fetchone()[0] or 0

        interesesTotal = interesesAnt + cuotaInteres

        cursor.execute('''
            INSERT INTO Transacciones (idCuentaCredito, fechaPago, valorPagado)
            VALUES (?, ?, ?)
        ''', (idCuenta, fechaPago, valor))

        cursor.execute('''
            UPDATE ProductosContratados
            SET saldoCapital = ?, plazoPendiente = ?, sumatoriaInteresesPagados = ?
            WHERE idCuentaCredito = ?
        ''', (saldoNuevo, plazoNuevo, interesesTotal, idCuenta))

        con.commit()
        imprimirFacturaCredito(idCuenta, valor, cuotaCapital, cuotaInteres, saldoNuevo, plazoNuevo)

    # === Consultar saldo ahorros ===

    def consultarSaldoAhorros(self,con):
        idCuenta = input("Número de cuenta de ahorros: ")
        tipo = obtenerTipoProducto_deCuenta(con, idCuenta)
        if tipo != 2:
            print("Error: Solo válido para cuentas de ahorros.")
            return

        datos = obtenerDatosAhorro(con, idCuenta)
        if not datos:
            print("Cuenta no encontrada.")
            return

        saldo, interes = datos
        saldoProyectado = saldo * (1 + interes / 100)

        print(f'''
    === SALDO AHORROS ===
    Saldo actual: {saldo:.2f}
    Interés mensual: {interes:.2f}%
    Saldo proyectado fin de mes: {saldoProyectado:.2f}
    ======================''')

    # === Consignar o retirar ahorros ===

    def transaccionAhorros(self,con):
        idCuenta = input("Número de cuenta de ahorros: ")
        tipo = obtenerTipoProducto_deCuenta(con, idCuenta)
        if tipo != 2:
            print("Error: Solo válido para cuentas de ahorros.")
            return

        datos = obtenerDatosAhorro(con, idCuenta)
        if not datos:
            print("Cuenta no encontrada.")
            return

        saldo, _ = datos
        print(f"Saldo actual: {saldo:.2f}")

        fechaPago = input("Fecha de transacción (YYYY-MM-DD): ").strip()

        try:
            valor = float(input("Valor a consignar (+) o retirar (-): "))
        except ValueError:
            print("Error: Valor inválido.")
            return

        saldoNuevo = saldo + valor

        cursor = con.cursor()
        cursor.execute('''
            INSERT INTO Transacciones (idCuentaCredito, fechaPago, valorPagado)
            VALUES (?, ?, ?)
        ''', (idCuenta, fechaPago, valor))

        cursor.execute('''
            UPDATE ProductosContratados
            SET saldoCapital = ?
            WHERE idCuentaCredito = ?
        ''', (saldoNuevo, idCuenta))

        con.commit()
        imprimirFacturaAhorro(idCuenta, valor, saldoNuevo)

    # === Utilidades ===

    def obtenerTipoProducto_deCuenta(self,con, idCuenta):
        cursor = con.cursor()
        cursor.execute('''
            SELECT P.tipoProducto
            FROM ProductosContratados PC
            JOIN Productos P ON PC.idProducto = P.noIdProducto
            WHERE PC.idCuentaCredito = ?
        ''', (idCuenta,))
        fila = cursor.fetchone()
        return fila[0] if fila else None

    def obtenerDatosCredito(self,con, idCuenta):
        cursor = con.cursor()
        cursor.execute('''
            SELECT PC.saldoCapital, PC.plazoPendiente, P.remuneracion
            FROM ProductosContratados PC
            JOIN Productos P ON PC.idProducto = P.noIdProducto
            WHERE PC.idCuentaCredito = ?
        ''', (idCuenta,))
        return cursor.fetchone()

    def obtenerDatosAhorro(self,con, idCuenta):
        cursor = con.cursor()
        cursor.execute('''
            SELECT PC.saldoCapital, P.remuneracion
            FROM ProductosContratados PC
            JOIN Productos P ON PC.idProducto = P.noIdProducto
            WHERE PC.idCuentaCredito = ?
        ''', (idCuenta,))
        return cursor.fetchone()

    def imprimirFacturaCredito(idCuenta, valor, cuotaCapital, cuotaInteres, saldoNuevo, plazoNuevo):
        print(f'''
    ====== FACTURA DE PAGO CRÉDITO ======
    Cuenta de crédito: {idCuenta}
    Valor pagado: {valor:.2f}
    Cuota capital: {cuotaCapital:.2f}
    Cuota interés: {cuotaInteres:.2f}
    Saldo restante: {saldoNuevo:.2f}
    Plazo pendiente: {plazoNuevo} meses
    Gracias por su pago.
    =====================================''')

    def imprimirFacturaAhorro(self,idCuenta, valor, saldoNuevo):
        print(f'''
    ====== FACTURA DE TRANSACCIÓN AHORROS ======
    Cuenta de ahorros: {idCuenta}
    Valor consignado/retirado: {valor:.2f}
    Saldo nuevo: {saldoNuevo:.2f}
    Gracias por su transacción.
    ===========================================''')

