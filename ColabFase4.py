import os
from abc import ABC, abstractmethod
from datetime import datetime

#Archivo para guardar los errores y lo que pasa en el sistema
archivo_logs = "logs_sistema_fj.txt"

def guardar_log(tipo, mensaje):
    # Esta funcion guarda todo en un txt para que quede el registro
    try:
        archivo = open(archivo_logs, "a")
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archivo.write("[" + hora_actual + "] [" + tipo + "] " + mensaje + "\n")
        archivo.close()
    except Exception as e:
        print("No se pudo guardar el log:", e)

#Excepciones personalizdas
#Creamos nuestros propios errores para controlar mejor el sistema
class ErrorSistema(Exception):
    pass

class ErrorCliente(ErrorSistema):
    pass

class ErrorServicio(ErrorSistema):
    pass

class ErrorReserva(ErrorSistema):
    pass

class ServicioNoDisponible(ErrorSistema):
    pass

class OperacionInvalida(ErrorSistema):
    pass

#Clase astracta
# Clase base de la que heredan las demas
class Entidad(ABC):
    def __init__(self, id_entidad):
        self.id_entidad = id_entidad

    @abstractmethod
    def mostrar_info(self):
        pass

#Clase cliente
class Cliente(Entidad):
    def __init__(self, id_cliente, nombre, correo, telefono):
        super().__init__(id_cliente)
        #Aqui validamos que los datos no esten vacios o mal escritos
        if len(nombre) < 3:
            raise ErrorCliente("El nombre es muy corto")
        if "@" not in correo:
            raise ErrorCliente("El correo no es valido")
        if not telefono.isdigit() or len(telefono) < 7:
            raise ErrorCliente("El telefono debe tener minimo 7 numeros")
            
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.lista_reservas = [] #lista interna para guardar sus reservas

    def agregar_reserva(self, reserva):
        self.lista_reservas.append(reserva)

    def mostrar_info(self):
        return "Cliente: " + self.nombre + " | Correo: " + self.correo + " | Reservas: " + str(len(self.lista_reservas))

#Clase abstracta del servicio
class Servicio(Entidad):
    def __init__(self, id_servicio, nombre_servicio, precio_base):
        super().__init__(id_servicio)
        self.nombre_servicio = nombre_servicio
        self.precio_base = precio_base
        self.esta_disponible = True

    @abstractmethod
    def calcular_costo(self, duracion, **extras):
        pass

    @abstractmethod
    def mostrar_info(self):
        pass

    def validar_duracion(self, duracion):
        if duracion <= 0:
            raise ErrorServicio("La duracion debe ser mayor a cero")

#Servicios especializados
class ReservaSalas(Servicio):
    def __init__(self, id_servicio, nombre_servicio, precio_base, capacidad):
        super().__init__(id_servicio, nombre_servicio, precio_base)
        self.capacidad = capacidad

    def calcular_costo(self, duracion, **extras):
        # Metodo sobrecargado usando **extras
        self.validar_duracion(duracion)
        iva = extras.get("iva", 0)
        desc = extras.get("descuento", 0)
        costo = self.precio_base * duracion * (1 + (self.capacidad / 100))
        return round(costo * (1 + iva) * (1 - desc), 2)

    def mostrar_info(self):
        return "Sala: " + self.nombre_servicio + " | Capacidad: " + str(self.capacidad)

class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, nombre_servicio, precio_base, tipo):
        super().__init__(id_servicio, nombre_servicio, precio_base)
        self.tipo = tipo

    def calcular_costo(self, duracion, **extras):
        self.validar_duracion(duracion)
        iva = extras.get("iva", 0)
        desc = extras.get("descuento", 0)
        recargo = 0.15 if self.tipo == "proyector" else 0
        costo = self.precio_base * duracion * (1 + recargo)
        return round(costo * (1 + iva) * (1 - desc), 2)

    def mostrar_info(self):
        return "Equipo: " + self.nombre_servicio + " | Tipo: " + self.tipo

class Asesoria(Servicio):
    def __init__(self, id_servicio, nombre_servicio, precio_base, nivel):
        super().__init__(id_servicio, nombre_servicio, precio_base)
        self.nivel = nivel

    def calcular_costo(self, duracion, **extras):
        self.validar_duracion(duracion)
        iva = extras.get("iva", 0)
        desc = extras.get("descuento", 0)
        factor = 1.5 if self.nivel == "senior" else 1
        costo = self.precio_base * duracion * factor
        return round(costo * (1 + iva) * (1 - desc), 2)

    def mostrar_info(self):
        return "Asesoria: " + self.nombre_servicio + " | Nivel: " + self.nivel

#Clase de reserva
class Reserva(Entidad):
    def __init__(self, id_reserva, el_cliente, el_servicio, duracion):
        super().__init__(id_reserva)
        if not isinstance(el_cliente, Cliente):
            raise ErrorReserva("El cliente no es valido")
        if not isinstance(el_servicio, Servicio):
            raise ErrorReserva("El servicio no es valido")
        self.el_cliente = el_cliente
        self.el_servicio = el_servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.costo_final = 0

    def confirmar(self):
        try:
            if not self.el_servicio.esta_disponible:
                #Encadenamiento de excepciones
                raise ServicioNoDisponible("El servicio no esta disponible") from ValueError("No disponible")
            
            if self.estado != "Pendiente":
                raise OperacionInvalida("La reserva ya fue procesada o cancelada")
                
            self.costo_final = self.el_servicio.calcular_costo(self.duracion, iva=0.19)
            self.estado = "Confirmada"
            self.el_cliente.agregar_reserva(self)
            guardar_log("INFO", "Reserva " + self.id_entidad + " confirmada")
            
        except ErrorSistema as error:
            guardar_log("ERROR", "Error al confirmar reserva: " + str(error))
            raise
        else:
            #Esto se ejecuta si todo salio bien
            guardar_log("INFO", "Exito confirmando la reserva")
        finally:
            #Esto se ejecuta siempre
            guardar_log("INFO", "Termino el intento de confirmacion")

    def cancelar(self):
        try:
            if self.estado == "Cancelada":
                raise OperacionInvalida("Esta reserva ya esta cancelada")
            self.estado = "Cancelada"
            guardar_log("INFO", "Reserva " + self.id_entidad + " cancelada")
        except ErrorSistema as e:
            guardar_log("ERROR", "Error cancelando: " + str(e))
            raise

    def procesar(self):
        try:
            if self.estado != "Confirmada":
                raise OperacionInvalida("Solo se procesan reservas confirmadas")
            self.estado = "Procesada"
            guardar_log("INFO", "Reserva procesada con exito")
        except ErrorSistema as e:
            guardar_log("ERROR", "Error procesando: " + str(e))
            raise

    def mostrar_info(self):
        return "Reserva: " + self.id_entidad + " | Cliente: " + self.el_cliente.nombre + " | Estado: " + self.estado

#Simulacion de 12 operaciones
def correr_simulacion():
    print("INICIANDO SIMULACION SOFTWARE FJ ")
    guardar_log("INFO", "Inicio de simulacion")

    #1 Cliente valido
    try:
        cliente1 = Cliente("C01", "andrea guzman", "andrea@mail.com", "3123456789")
        print("1. ok ", cliente1.mostrar_info())
    except Exception as e:
        print("1. Error:", e)

    #2 Cliente invalido (correo malo)
    try:
        cliente_malo = Cliente("C02", "Luis", "correo_malo", "3001234567")
    except ErrorCliente as e:
        print("2. Error esperado ", e)
        guardar_log("ERROR", str(e))

    #3 Cliente invalido (telefono malo)
    try:
        cliente_malo2 = Cliente("C03", "angela", "angela@mail.com", "abc")
    except ErrorCliente as e:
        print("3. error esperado ", e)
        guardar_log("ERROR", str(e))

    #4 Servicio valido
    try:
        sala = ReservaSalas("S01", "Sala Grande", 50000, 20)
        print("4. ok ", sala.mostrar_info())
    except Exception as e:
        print("4. Error:", e)

    #5 Servicio invalido (duracion negativa)
    try:
        equipo = AlquilerEquipos("E01", "Proyector", 30000, "proyector")
        equipo.calcular_costo(-5)
    except ErrorServicio as e:
        print("5. error esperado ", e)
        guardar_log("ERROR", str(e))

    #6 Servicio valido (asesoria)
    try:
        asesoria = Asesoria("A01", "Asesoria IA", 80000, "senior")
        print("6. ok ", asesoria.mostrar_info())
    except Exception as e:
        print("6. Error:", e)

    #7 Reserva exitosa
    try:
        reserva1 = Reserva("R01", cliente1, sala, 4)
        reserva1.confirmar()
        reserva1.procesar()
        print("7. ok ", reserva1.mostrar_info())
    except Exception as e:
        print("7. Error:", e)

    #8 Reserva fallida (servicio no disponible)
    try:
        asesoria.esta_disponible = False
        reserva2 = Reserva("R02", cliente1, asesoria, 2)
        reserva2.confirmar()
    except ServicioNoDisponible as e:
        print("8. error esperado ", e)

    #9 Cancelar reserva
    try:
        reserva3 = Reserva("R03", cliente1, sala, 3)
        reserva3.confirmar()
        reserva3.cancelar()
        print("9. ok ", reserva3.mostrar_info())
    except Exception as e:
        print("9. Error:", e)

    #10 Procesar reserva cancelada (fallo)
    try:
        reserva3.procesar()
    except OperacionInvalida as e:
        print("10. Error esperado ", e)

    #11 Cancelar dos veces (fallo)
    try:
        reserva3.cancelar()
    except OperacionInvalida as e:
        print("11. Error esperado ", e)

    #12 Sobrecarga de metodos (varios calculos)
    try:
        c1 = sala.calcular_costo(2)
        c2 = sala.calcular_costo(2, iva=0.19)
        c3 = sala.calcular_costo(2, iva=0.19, descuento=0.1)
        print("12. ok  Calculos: base", c1, " con IVA", c2, " con descuento", c3)
    except Exception as e:
        print("12. Error:", e)

    print("Fin de la ejecucion")

if __name__ == "__main__":
    try:
        correr_simulacion()
    except Exception as e:
        print("Fallo grave en el sistema:", e)
        guardar_log("CRITICAL", str(e))
    finally:
        print("Revisar logs en:", os.path.abspath(archivo_logs))

