# ==============================
# Bienvenidos
# Proyecto de Programación.
# Integrantes: Jessiel, Andrés.
# ==============================

"""Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.

Un solo archivo, sin base de datos. Simula 17 operaciones (válidas e inválidas).
Los errores y eventos se guardan en el archivo 'software_fj.log' (se crea al ejecutar).
"""
import logging  # Para escribir los eventos y errores en el archivo de logs
import re  # Para validar el formato del correo
from abc import ABC, abstractmethod  # Para crear clases abstractas

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DEL LOG
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="software_fj.log",  # Archivo donde se guardan los registros
    level=logging.DEBUG,  # Registra todos los niveles
    format="%(asctime)s | %(levelname)s | %(message)s",  # Formato de cada línea
    encoding="utf-8",
)
logger = logging.getLogger("softwarefj")


# ---------------------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# ---------------------------------------------------------------------------
class ErrorSoftwareFJ(Exception):
    """Excepción base: todas las del sistema heredan de ella."""

    def __init__(self, mensaje, codigo="ERR_GENERAL"):
        super().__init__(mensaje)  # Guarda el mensaje en la excepción padre
        self.codigo = codigo  # Código para identificar el error en los logs


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Datos de cliente inválidos."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_CLIENTE")


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Parámetros de servicio inválidos o faltantes."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_SERVICIO")


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio no está disponible."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_NO_DISPONIBLE")


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Intento de reserva incorrecto."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_RESERVA")


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Operación no permitida según el estado de la reserva."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_OPERACION")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Cálculo de costos inconsistente."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_CALCULO")


# ---------------------------------------------------------------------------
# CLASE ABSTRACTA GENERAL Y CLIENTE
# ---------------------------------------------------------------------------
class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad del sistema."""

    _contador = 0  # Contador compartido para generar ids únicos

    def __init__(self):
        Entidad._contador += 1  # Suma 1 al contador global
        self._id = Entidad._contador  # Atributo protegido con el id

    @property
    def id(self):
        return self._id  # El id es de solo lectura (encapsulación)

    @abstractmethod
    def describir(self):
        """Cada entidad debe describirse (polimorfismo)."""


class Cliente(Entidad):
    """Cliente con datos privados y validados."""

    def __init__(self, nombre, correo, telefono):
        super().__init__()  # Genera el id
        self.__nombre = None  # Atributos privados (doble guion bajo)
        self.__correo = None
        self.__telefono = None
        self.nombre = nombre  # Se asignan con los setters para que se validen
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        # Debe ser texto con mínimo 3 caracteres
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres")
        self.__nombre = valor.strip()

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        # Formato básico usuario@dominio.ext
        if not isinstance(valor, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ClienteInvalidoError(f"Correo inválido: {valor!r}")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        # Solo dígitos, entre 7 y 10 números
        if not isinstance(valor, str) or not valor.isdigit() or not 7 <= len(valor) <= 10:
            raise ClienteInvalidoError(f"Teléfono inválido: {valor!r}")
        self.__telefono = valor

    def describir(self):
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | {self.telefono}"


# ---------------------------------------------------------------------------
# SERVICIOS (CLASE ABSTRACTA + 3 ESPECIALIZADOS)
# ---------------------------------------------------------------------------
class Servicio(Entidad):
    """Clase abstracta: define lo que todo servicio debe implementar."""

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio requiere un nombre")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser un número positivo")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self.disponible = disponible  # True si se puede reservar

    @property
    def nombre(self):
        return self._nombre

    @abstractmethod
    def calcular_costo(self, horas):
        """Costo base (cada servicio lo calcula distinto)."""

    @abstractmethod
    def validar_parametros(self, horas):
        """Validaciones propias de cada servicio."""

    def calcular_costo_total(self, horas, impuesto=0.19, descuento=0.0):
        """Método sobrecargado mediante parámetros opcionales.

        calcular_costo_total(2)              -> con IVA 19 %
        calcular_costo_total(2, 0.0)         -> sin impuesto
        calcular_costo_total(2, 0.19, 0.10)  -> con IVA y 10 % de descuento
        """
        self.validar_parametros(horas)  # Lanza excepción si los datos no sirven
        if not 0 <= impuesto <= 1 or not 0 <= descuento < 1:
            raise CalculoInconsistenteError("Impuesto o descuento fuera de rango")
        base = self.calcular_costo(horas)  # Polimorfismo
        return round(base * (1 - descuento) * (1 + impuesto), 2)


class ReservaSala(Servicio):
    """Reserva de salas."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero positivo")
        self.capacidad = capacidad

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 8:
            raise ServicioInvalidoError("Las salas se reservan entre 1 y 8 horas")

    def calcular_costo(self, horas):
        return self._tarifa_hora * horas  # Tarifa simple por hora

    def describir(self):
        return f"Sala '{self.nombre}' (cap. {self.capacidad}) - ${self._tarifa_hora:,.0f}/h"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos."""

    def __init__(self, nombre, tarifa_hora, tipo_equipo, seguro=False, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("Debe indicar el tipo de equipo")
        self.tipo_equipo = tipo_equipo
        self.seguro = seguro  # Con seguro cuesta 15 % más

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 72:
            raise ServicioInvalidoError("Los equipos se alquilan entre 1 y 72 horas")

    def calcular_costo(self, horas):
        recargo = 1.15 if self.seguro else 1.0
        return self._tarifa_hora * horas * recargo

    def describir(self):
        seguro = "con seguro" if self.seguro else "sin seguro"
        return f"Equipo '{self.nombre}' ({self.tipo_equipo}, {seguro}) - ${self._tarifa_hora:,.0f}/h"


class Asesoria(Servicio):
    """Asesorías especializadas."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Multiplicador por nivel

    def __init__(self, nombre, tarifa_hora, nivel, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido: {nivel!r}. Use {list(self.NIVELES)}")
        self.nivel = nivel

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 4:
            raise ServicioInvalidoError("Las asesorías duran entre 1 y 4 horas")

    def calcular_costo(self, horas):
        return self._tarifa_hora * horas * self.NIVELES[self.nivel]

    def describir(self):
        return f"Asesoría '{self.nombre}' (nivel {self.nivel}) - ${self._tarifa_hora:,.0f}/h"


# ---------------------------------------------------------------------------
# RESERVA
# ---------------------------------------------------------------------------
class Reserva(Entidad):
    """Reserva con estados: PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA."""

    def __init__(self, cliente, servicio, horas):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"'{servicio.nombre}' no está disponible")
        try:
            servicio.validar_parametros(horas)  # Valida la duración
        except ErrorSoftwareFJ as e:
            # Encadenamiento de excepciones: se conserva el error original
            raise ReservaInvalidaError(f"Duración inválida ({horas}): {e}") from e
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"  # Estado inicial

    def confirmar(self):
        if self.estado != "PENDIENTE":  # Solo se confirma lo pendiente
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self.estado}")
        self.estado = "CONFIRMADA"
        logger.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        if self.estado in ("CANCELADA", "PROCESADA"):  # No se cancela dos veces ni lo procesado
            raise OperacionNoPermitidaError(f"No se puede cancelar una reserva {self.estado}")
        self.estado = "CANCELADA"
        logger.info("Reserva #%s cancelada", self.id)

    def procesar(self, impuesto=0.19, descuento=0.0):
        """Procesa la reserva con try/except/else/finally."""
        try:
            if self.estado != "CONFIRMADA":
                raise OperacionNoPermitidaError("Solo se procesan reservas confirmadas")
            total = self.servicio.calcular_costo_total(self.horas, impuesto, descuento)
        except ErrorSoftwareFJ as e:
            logger.error("[%s] Fallo al procesar reserva #%s: %s", e.codigo, self.id, e)
            raise  # Se relanza para que lo maneje quien llamó
        else:
            # Se ejecuta solo si NO hubo error
            self.estado = "PROCESADA"
            logger.info("Reserva #%s procesada. Total: $%s", self.id, f"{total:,.2f}")
            return total
        finally:
            # Se ejecuta siempre
            logger.debug("Fin del intento de procesar la reserva #%s", self.id)

    def describir(self):
        return (f"Reserva #{self.id} [{self.estado}] {self.cliente.nombre} -> "
                f"{self.servicio.nombre} x {self.horas}h")


# ---------------------------------------------------------------------------
# SIMULACIÓN
# ---------------------------------------------------------------------------
def ejecutar(descripcion, accion):
    """Ejecuta una operación; si falla, registra el error y el programa continúa."""
    print(f"\n▶ {descripcion}")
    try:
        resultado = accion()
    except ErrorSoftwareFJ as e:
        logger.error("[%s] %s: %s", e.codigo, descripcion, e)  # Error controlado
        print(f"  ✗ Error controlado [{e.codigo}]: {e}")
        if e.__cause__:  # Muestra la causa si hubo encadenamiento
            print(f"    causa: {e.__cause__}")
    except Exception as e:  # Error inesperado: tampoco detiene el sistema
        logger.critical("Error inesperado en %s: %r", descripcion, e)
        print(f"  ✗ Error inesperado: {e!r}")
    else:
        logger.info("OK: %s", descripcion)
        texto = resultado.describir() if hasattr(resultado, "describir") else resultado
        print(f"  ✓ {texto}")
        return resultado
    finally:
        logger.debug("Operación finalizada: %s", descripcion)


def main():
    logger.info("===== Inicio de la simulación =====")
    reservas = []  # Lista interna que reemplaza a la base de datos

    # --- Clientes ---
    ejecutar("1. Registrar cliente válido",
             lambda: Cliente("Ana Gómez", "ana@correo.com", "3001234567"))
    ejecutar("2. Registrar cliente con correo inválido",
             lambda: Cliente("Luis Pérez", "luis-correo", "3109876543"))
    ejecutar("3. Registrar cliente con teléfono inválido",
             lambda: Cliente("Marta Ruiz", "marta@correo.com", "12ab"))
    cliente = Cliente("Carlos Díaz", "carlos@correo.com", "3201112233")

    # --- Servicios ---
    sala = ejecutar("4. Crear sala válida", lambda: ReservaSala("Sala Innovación", 50000, 12))
    ejecutar("5. Crear sala con capacidad inválida", lambda: ReservaSala("Sala X", 50000, -3))
    ejecutar("6. Crear asesoría con nivel inexistente",
             lambda: Asesoria("Asesoría Cloud", 80000, "maestro"))
    equipo = AlquilerEquipo("Portátil Pro", 12000, "Portátil", seguro=True)
    asesoria = Asesoria("Asesoría Python", 80000, "senior")
    no_disponible = AlquilerEquipo("Proyector", 9000, "Proyector", disponible=False)

    # --- Reservas ---
    r1 = ejecutar("7. Reserva válida de sala (3h)", lambda: Reserva(cliente, sala, 3))
    ejecutar("8. Reserva con duración inválida (20h en sala)", lambda: Reserva(cliente, sala, 20))
    ejecutar("9. Reserva de servicio no disponible", lambda: Reserva(cliente, no_disponible, 2))
    ejecutar("10. Reserva sin cliente válido", lambda: Reserva(None, sala, 2))

    # --- Confirmar, procesar y cancelar ---
    if r1:
        reservas.append(r1)
        ejecutar("11. Procesar reserva sin confirmar", lambda: r1.procesar())
        ejecutar("12. Confirmar reserva", lambda: (r1.confirmar(), r1.describir())[1])
        ejecutar("13. Procesar con IVA y 10% de descuento",
                 lambda: f"Total: ${r1.procesar(0.19, 0.10):,.2f}")
        ejecutar("14. Cancelar reserva ya procesada", lambda: r1.cancelar())

    r2 = ejecutar("15. Reserva de equipo (24h)", lambda: Reserva(cliente, equipo, 24))
    if r2:
        reservas.append(r2)
        ejecutar("16. Confirmar y procesar sin impuesto",
                 lambda: (r2.confirmar(), f"Total: ${r2.procesar(impuesto=0.0):,.2f}")[1])
    ejecutar("17. Cálculo con descuento inválido (150%)",
             lambda: asesoria.calcular_costo_total(2, 0.19, 1.5))

    print("\n===== Resumen =====")
    for r in reservas:
        print(" ", r.describir())
    logger.info("===== Fin de la simulación =====")
    print("\nRevisa 'software_fj.log' para ver el registro de eventos y errores.")


if __name__ == "__main__":
    main()
