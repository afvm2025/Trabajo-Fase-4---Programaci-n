# Sistema Integral de Gestión - Software FJ (Fase 4)

# Descripción General
Este repositorio aloja el desarrollo del componente práctico de la Fase 4 para el curso de **Programación (213023)** de la UNAD. 
El sistema es una aplicación de consola orientada a objetos, desarrollada en Python y estructurada bajo una arquitectura sin bases de datos (persistencia en memoria y logs).

El núcleo del negocio resuelve la gestión de clientes, servicios (reservas de salas, alquiler de equipos y asesorías) y reservas para la empresa *Software FJ*. 
Todo esto construido con un manejo de excepciones de alto nivel, garantizando que la aplicación sea robusta y nunca se detenga abruptamente ante fallos de usuario o del sistema.

# Características Técnicas (Arquitectura del Sistema)

El sistema está construido aplicando a cabalidad los pilares de la Programación Orientada a Objetos:

**Abstracción:** Implementada mediante las clases base `Entidad` y `Servicio`, las cuales definen los contratos (métodos abstractos) que las clases derivadas deben cumplir de forma obligatoria.

**Herencia y Polimorfismo:** Los servicios especializados (`ReservaSalas`, `AlquilerEquipos`, `AsesoriaEspecializada`) heredan de `Servicio` y redefinen sus propios métodos `calcular_costo` y `mostrar_info`.
  Cada entidad ejecuta sus cálculos de forma independiente y sin enredos.

**Encapsulamiento y Validaciones Estrictas:** La clase `Cliente` cuenta con validaciones rigurosas en su constructor para garantizar la integridad de los datos:
  nombres muy cortos, correos con formatos inválidos o teléfonos erróneos son rechazados de inmediato.

**Sobrecarga de Métodos (Simulada):** Dado que Python no soporta sobrecarga nativa (a diferencia de Java o C++), la implementamos de manera elegante usando `**extras` (kwargs) en el método `calcular_costo`.
  Esto permite flexibilidad para calcular el precio base, aplicar IVA (19%) o descuentos, sin duplicar código.

**Manejo Avanzado de Excepciones:** 
  *   Jerarquía de **excepciones personalizadas** (`ErrorCliente`, `ErrorServicio`, `OperacionInvalida`, etc.).
  *   Uso intensivo y correcto de bloques `try/except`, `try/except/else`, `try/except/finally`.
  *   **Encadenamiento de excepciones** (`raise ... from ...`) para mantener la trazabilidad del error original.
  *   **Archivo de Logs:** Todo evento o error queda registrado con fecha y hora en `logs_sistema_fj.txt`, garantizando una auditoría completa del sistema.

# Requisitos del Entorno
*   Python 3.8 o superior.
*   Consola o terminal (Bash, Zsh, PowerShell, etc.).

#  Despliegue y Ejecución
Sigue estos pasos para ejecutar el proyecto de forma local:

1. Clona el repositorio o descarga los archivos fuente.
2. Abre la terminal en la carpeta raíz del proyecto.
3. Ejecuta el script principal:
   "bash"
   python3 trabajo_4.py

 # El sistema desplegará en consola la simulación de 12 operaciones (válidas e inválidas).
  Adicionalmente, se generará el archivo logs_sistema_fj.txt en la misma ruta, 
  el cual contiene el registro detallado de la ejecución.  

 El script incluye un bloque de simulación integral que ejecuta una batería de 12 operaciones. Entre las pruebas realizadas se demuestran:

 Creación de clientes con datos válidos.

 Intentos de crear clientes con correos y teléfonos inválidos (detectados correctamente por las excepciones).

 Creación de servicios y cálculos de costos con y sin parámetros adicionales.

 Reservas exitosas, cancelaciones y procesamientos correctos.

 Intentos de procesar reservas canceladas o usar servicios no disponibles (controlados sin que la aplicación colapse).


Autor:
Tomás Alfonso Pacheco Costa
Jessiel Alvares Hurtado
Andres Velez Mora

Estudiantes de Ingeniería de Sistemas - UNAD.
Grupo - 96


