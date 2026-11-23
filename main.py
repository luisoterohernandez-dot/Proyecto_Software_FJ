
# ============================================================
# PROYECTO: SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ
# Curso: Programacion
# Codigo: 213023
# Universidad Nacional Abierta y a Distancia - UNAD
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# ============================================================
# 1. CONFIGURACION DEL SISTEMA DE REGISTROS (LOGS)
# ============================================================

logging.basicConfig(
    filename="registro_software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorSistema(Exception):
    """Excepcion general del sistema."""
    pass


class ErrorValidacion(ErrorSistema):
    """Error en los datos ingresados."""
    pass


class ServicioNoDisponible(ErrorSistema):
    """Error cuando un servicio no esta disponible."""
    pass


class ErrorReserva(ErrorSistema):
    """Error durante el proceso de reserva."""
    pass


# ============================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ============================================================

class Entidad(ABC):

    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise ErrorValidacion("El identificador es obligatorio.")

        self._identificador = str(identificador)

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ============================================================
# 4. CLASE CLIENTE
# ============================================================

class Cliente(Entidad):

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not nombre or not nombre.strip():
            raise ErrorValidacion("El nombre es obligatorio.")

        if "@" not in correo or "." not in correo:
            raise ErrorValidacion("El correo electronico no es valido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise ErrorValidacion("El telefono debe contener minimo 7 digitos.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | "
            f"Documento: {self.identificador} | "
            f"Correo: {self.__correo} | "
            f"Telefono: {self.__telefono}"
        )


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(Entidad, ABC):

    def __init__(self, identificador, nombre, precio, disponible=True):
        super().__init__(identificador)

        if not nombre or not nombre.strip():
            raise ErrorValidacion("El nombre del servicio es obligatorio.")

        if not isinstance(precio, (int, float)) or isinstance(precio, bool) or precio <= 0:
            raise ErrorValidacion("El precio debe ser mayor que cero.")

        self._nombre = nombre
        self._precio = float(precio)
        self._disponible = disponible

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Metodo con parametros opcionales.
        Permite calcular el costo con o sin impuestos y descuentos.
        """

        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
            raise ErrorValidacion("La duracion debe ser mayor que cero.")

        if not 0 <= impuesto <= 100:
            raise ErrorValidacion("El impuesto debe estar entre 0 y 100.")

        if not 0 <= descuento <= 100:
            raise ErrorValidacion("El descuento debe estar entre 0 y 100.")

        subtotal = self._precio * duracion
        total = subtotal + (subtotal * impuesto / 100)
        total = total - (total * descuento / 100)

        return round(total, 2)

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    def mostrar_informacion(self):
        return (
            f"{self._nombre} | "
            f"Precio: ${self._precio:,.2f} | "
            f"Disponible: {self._disponible}"
        )


# ============================================================
# 6. SERVICIO ESPECIALIZADO: RESERVA DE SALAS
# ============================================================

class ServicioSala(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or not 1 <= duracion <= 12:
            raise ErrorValidacion(
                "La reserva de sala debe durar entre 1 y 12 horas."
            )

    def describir_servicio(self):
        return "Servicio de reserva de salas para reuniones y actividades empresariales."


# ============================================================
# 7. SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ============================================================

class ServicioEquipo(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or not 1 <= duracion <= 30:
            raise ErrorValidacion(
                "El alquiler de equipos debe durar entre 1 y 30 dias."
            )

    def describir_servicio(self):
        return "Servicio de alquiler de equipos tecnologicos y audiovisuales."


# ============================================================
# 8. SERVICIO ESPECIALIZADO: ASESORIAS
# ============================================================

class ServicioAsesoria(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or not 1 <= duracion <= 8:
            raise ErrorValidacion(
                "La asesoria debe durar entre 1 y 8 horas."
            )

    def describir_servicio(self):
        return "Servicio de asesoria especializada y acompanamiento profesional."


# ============================================================
# 9. CLASE RESERVA
# ============================================================

class Reserva(Entidad):

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("Debe ingresar un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("Debe ingresar un servicio valido.")

        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha = datetime.now()

    def confirmar(self):

        if self.estado != "Pendiente":
            raise ErrorReserva(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.servicio.disponible:
            raise ServicioNoDisponible(
                "El servicio seleccionado no esta disponible."
            )

        self.estado = "Confirmada"

        logging.info(
            "Reserva %s confirmada para el cliente %s.",
            self.identificador,
            self.cliente.nombre
        )

        return "Reserva confirmada correctamente."

    def cancelar(self):

        if self.estado != "Confirmada" and self.estado != "Pendiente":
            raise ErrorReserva(
                "La reserva no puede cancelarse en su estado actual."
            )

        self.estado = "Cancelada"

        logging.info(
            "Reserva %s cancelada.",
            self.identificador
        )

        return "Reserva cancelada correctamente."

    def procesar(self, impuesto=0, descuento=0):

        try:
            if self.estado != "Confirmada":
                raise ErrorReserva(
                    "La reserva debe estar confirmada para procesarse."
                )

            total = self.servicio.calcular_costo(
                self.duracion,
                impuesto,
                descuento
            )

            logging.info(
                "Reserva %s procesada. Total: $%.2f",
                self.identificador,
                total
            )

            return total

        except ErrorSistema:
            logging.exception("Error al procesar la reserva.")
            raise

    def mostrar_informacion(self):

        return (
            f"Reserva: {self.identificador} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} | "
            f"Estado: {self.estado}"
        )


# ============================================================
# 10. CLASE PRINCIPAL DEL SISTEMA
# ============================================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):

        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("El objeto no es un cliente valido.")

        if any(c.identificador == cliente.identificador
               for c in self.clientes):
            raise ErrorValidacion("El cliente ya se encuentra registrado.")

        self.clientes.append(cliente)

        logging.info("Cliente registrado: %s", cliente.nombre)

        return "Cliente registrado correctamente."

    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("El objeto no es un servicio valido.")

        if any(s.identificador == servicio.identificador
               for s in self.servicios):
            raise ErrorValidacion("El servicio ya se encuentra registrado.")

        self.servicios.append(servicio)

        logging.info("Servicio registrado: %s", servicio.nombre)

        return "Servicio registrado correctamente."

    def registrar_reserva(self, reserva):

        if not isinstance(reserva, Reserva):
            raise ErrorValidacion("La reserva ingresada no es valida.")

        if any(r.identificador == reserva.identificador
               for r in self.reservas):
            raise ErrorValidacion("La reserva ya existe.")

        self.reservas.append(reserva)

        logging.info(
            "Reserva registrada: %s",
            reserva.identificador
        )

        return "Reserva registrada correctamente."

    def listar_clientes(self):

        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def listar_servicios(self):

        for servicio in self.servicios:
            print(servicio.describir_servicio())

    def listar_reservas(self):

        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# ============================================================
# 11. FUNCION PARA REGISTRAR OPERACIONES
# ============================================================

def ejecutar_operacion(descripcion, operacion):

    print("\n" + "=" * 65)
    print(descripcion)

    try:
        resultado = operacion()
        print("RESULTADO:", resultado)

    except ErrorSistema as error:
        print("ERROR CONTROLADO:", error)
        logging.error(
            "%s: %s",
            descripcion,
            error
        )

    except Exception as error:
        print("ERROR INESPERADO:", error)
        logging.exception(
            "Error inesperado en %s",
            descripcion
        )

    else:
        print("Operacion ejecutada sin errores.")

    finally:
        print("Finalizacion de la operacion.")


# ============================================================
# 12. PROGRAMA PRINCIPAL Y PRUEBAS DEL SISTEMA
# ============================================================

def main():

    print("\n")
    print("*" * 65)
    print("       SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ")
    print("*" * 65)

    sistema = SistemaSoftwareFJ()

    # --------------------------------------------------------
    # CREACION DE CLIENTES
    # --------------------------------------------------------

    cliente1 = Cliente(
        "1001",
        "Carlos Rodriguez",
        "carlos@gmail.com",
        "3001234567"
    )

    cliente2 = Cliente(
        "1002",
        "Maria Gonzalez",
        "maria@gmail.com",
        "3101234567"
    )

    cliente3 = Cliente(
        "1003",
        "Andres Martinez",
        "andres@gmail.com",
        "3201234567"
    )

    ejecutar_operacion(
        "OPERACION 1: Registrar primer cliente",
        lambda: sistema.registrar_cliente(cliente1)
    )

    ejecutar_operacion(
        "OPERACION 2: Registrar segundo cliente",
        lambda: sistema.registrar_cliente(cliente2)
    )

    ejecutar_operacion(
        "OPERACION 3: Registrar cliente con documento duplicado",
        lambda: sistema.registrar_cliente(cliente1)
    )

    ejecutar_operacion(
        "OPERACION 4: Registrar cliente con correo invalido",
        lambda: Cliente(
            "1004",
            "Pedro Lopez",
            "correo_invalido",
            "3001234567"
        )
    )

    # --------------------------------------------------------
    # CREACION DE SERVICIOS
    # --------------------------------------------------------

    sala = ServicioSala(
        "S01",
        "Sala de reuniones",
        50000
    )

    equipo = ServicioEquipo(
        "E01",
        "Alquiler de computador",
        30000
    )

    asesoria = ServicioAsesoria(
        "A01",
        "Asesoria en programacion",
        80000
    )

    ejecutar_operacion(
        "OPERACION 5: Registrar servicio de sala",
        lambda: sistema.registrar_servicio(sala)
    )

    ejecutar_operacion(
        "OPERACION 6: Registrar servicio de equipos",
        lambda: sistema.registrar_servicio(equipo)
    )

    ejecutar_operacion(
        "OPERACION 7: Registrar servicio de asesoria",
        lambda: sistema.registrar_servicio(asesoria)
    )

    ejecutar_operacion(
        "OPERACION 8: Intentar crear servicio con precio negativo",
        lambda: ServicioSala(
            "S02",
            "Sala adicional",
            -10000
        )
    )

    # --------------------------------------------------------
    # CREACION Y PROCESAMIENTO DE RESERVAS
    # --------------------------------------------------------

    reserva1 = Reserva(
        "R001",
        cliente1,
        sala,
        3
    )

    reserva2 = Reserva(
        "R002",
        cliente2,
        equipo,
        2
    )

    reserva3 = Reserva(
        "R003",
        cliente3,
        asesoria,
        2
    )

    ejecutar_operacion(
        "OPERACION 9: Registrar reserva de sala",
        lambda: sistema.registrar_reserva(reserva1)
    )

    ejecutar_operacion(
        "OPERACION 10: Confirmar reserva de sala",
        lambda: reserva1.confirmar()
    )

    ejecutar_operacion(
        "OPERACION 11: Procesar reserva con impuesto y descuento",
        lambda: reserva1.procesar(19, 10)
    )

    ejecutar_operacion(
        "OPERACION 12: Intentar procesar reserva pendiente",
        lambda: reserva2.procesar()
    )

    ejecutar_operacion(
        "OPERACION 13: Confirmar reserva de equipos",
        lambda: reserva2.confirmar()
    )

    ejecutar_operacion(
        "OPERACION 14: Procesar reserva de equipos",
        lambda: reserva2.procesar()
    )

    ejecutar_operacion(
        "OPERACION 15: Intentar crear reserva con duracion incorrecta",
        lambda: Reserva(
            "R004",
            cliente1,
            sala,
            20
        )
    )

    ejecutar_operacion(
        "OPERACION 16: Cancelar reserva confirmada",
        lambda: reserva1.cancelar()
    )

    # --------------------------------------------------------
    # ENCADENAMIENTO DE EXCEPCIONES
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("PRUEBA DE ENCADENAMIENTO DE EXCEPCIONES")

    try:
        try:
            numero = int("dato incorrecto")
        except ValueError as error:
            raise ErrorValidacion(
                "No fue posible convertir el dato a numero."
            ) from error

    except ErrorValidacion as error:
        print("Error controlado mediante encadenamiento:", error)
        logging.exception("Prueba de encadenamiento de excepciones.")

    # --------------------------------------------------------
    # TRY / EXCEPT / FINALLY
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("PRUEBA DE MANEJO DE ERRORES Y FINALIZACION")

    try:
        print("Verificando el funcionamiento del sistema.")
        resultado = 100 / 0

    except ZeroDivisionError as error:
        print("Se detecto una division por cero:", error)
        logging.exception("Error matematico controlado.")

    finally:
        print("El sistema continua funcionando correctamente.")

    # --------------------------------------------------------
    # CONSULTA DE INFORMACION
    # --------------------------------------------------------

    print("\n")
    print("*" * 65)
    print("                 CLIENTES REGISTRADOS")
    print("*" * 65)

    sistema.listar_clientes()

    print("\n")
    print("*" * 65)
    print("                 SERVICIOS DISPONIBLES")
    print("*" * 65)

    sistema.listar_servicios()

    print("\n")
    print("*" * 65)
    print("                 RESERVAS REGISTRADAS")
    print("*" * 65)

    sistema.listar_reservas()

    # --------------------------------------------------------
    # FINALIZACION
    # --------------------------------------------------------

    print("\n")
    print("*" * 65)
    print("RESUMEN DEL SISTEMA")
    print("*" * 65)

    print("Total de clientes:", len(sistema.clientes))
    print("Total de servicios:", len(sistema.servicios))
    print("Total de reservas:", len(sistema.reservas))

    print("\nEl sistema finalizo correctamente.")
    print("Los eventos y errores quedaron registrados en el archivo LOG.")


# ============================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":
    main()
