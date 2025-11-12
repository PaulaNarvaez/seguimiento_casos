# Sistema de Seguimiento de Casos

Sistema simple y eficiente para el seguimiento y gestión de casos.

## Características

- ✅ Crear, leer, actualizar y eliminar casos
- ✅ Estados de casos: abierto, en progreso, resuelto, cerrado
- ✅ Niveles de prioridad: baja, media, alta, crítica
- ✅ Asignación de casos a personas
- ✅ Sistema de notas con timestamps
- ✅ Persistencia de datos en JSON
- ✅ Interfaz de línea de comandos (CLI)

## Requisitos

- Python 3.7 o superior
- No requiere dependencias externas

## Instalación

```bash
git clone https://github.com/PaulaNarvaez/seguimiento_casos.git
cd seguimiento_casos
```

## Uso

### Interfaz de Línea de Comandos

#### Crear un nuevo caso

```bash
python cli.py crear "Título del caso" "Descripción del caso"
python cli.py crear "Bug en login" "El usuario no puede iniciar sesión" --prioridad alta --asignado-a "Juan Pérez"
```

#### Listar todos los casos

```bash
python cli.py listar
python cli.py listar --estado abierto
python cli.py listar --prioridad alta
```

#### Ver detalles de un caso

```bash
python cli.py ver 1
```

#### Actualizar un caso

```bash
python cli.py actualizar 1 --estado en_progreso
python cli.py actualizar 1 --titulo "Nuevo título" --prioridad critica
python cli.py actualizar 1 --asignado-a "María García"
```

#### Agregar una nota a un caso

```bash
python cli.py nota 1 "Investigando el problema"
```

#### Eliminar un caso

```bash
python cli.py eliminar 1
```

### Uso como Módulo Python

```python
from gestor_casos import GestorCasos
from caso import EstadoCaso, PrioridadCaso

# Crear gestor
gestor = GestorCasos()

# Crear caso
caso = gestor.crear_caso(
    titulo="Bug crítico",
    descripcion="Sistema no responde",
    prioridad=PrioridadCaso.CRITICA,
    asignado_a="Juan Pérez"
)

# Listar casos
casos = gestor.listar_casos()
for caso in casos:
    print(caso)

# Actualizar caso
gestor.actualizar_caso(caso.id, estado=EstadoCaso.EN_PROGRESO)

# Agregar nota
caso.agregar_nota("Iniciando investigación")
gestor.guardar_casos()
```

## Estructura del Proyecto

```
seguimiento_casos/
├── caso.py              # Modelo de datos para casos
├── gestor_casos.py      # Lógica de gestión de casos
├── cli.py               # Interfaz de línea de comandos
├── test_seguimiento.py  # Tests unitarios
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Documentación
```

## Testing

Ejecutar los tests:

```bash
python -m unittest test_seguimiento.py
```

Ejecutar tests con verbose:

```bash
python -m unittest test_seguimiento.py -v
```

## Estados de Casos

- **abierto**: Caso recién creado
- **en_progreso**: Caso en proceso de resolución
- **resuelto**: Caso resuelto, pendiente de cerrar
- **cerrado**: Caso cerrado definitivamente

## Prioridades

- **baja**: Prioridad baja
- **media**: Prioridad media (default)
- **alta**: Prioridad alta
- **crítica**: Prioridad crítica

## Almacenamiento de Datos

Los casos se almacenan en formato JSON en el archivo `casos.json`. El archivo se crea automáticamente al crear el primer caso.

## Ejemplos

### Flujo de trabajo típico

```bash
# 1. Crear un caso
python cli.py crear "Implementar nueva característica" "Añadir funcionalidad de exportación" --prioridad alta

# 2. Ver todos los casos
python cli.py listar

# 3. Actualizar el caso a en progreso
python cli.py actualizar 1 --estado en_progreso --asignado-a "Ana López"

# 4. Agregar notas de progreso
python cli.py nota 1 "Comenzando implementación"
python cli.py nota 1 "50% completado"

# 5. Marcar como resuelto
python cli.py actualizar 1 --estado resuelto

# 6. Ver detalles finales
python cli.py ver 1
```

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
