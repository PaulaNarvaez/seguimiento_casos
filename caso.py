"""
Modelo de datos para casos en el sistema de seguimiento.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoCaso(Enum):
    """Estados posibles de un caso."""
    ABIERTO = "abierto"
    EN_PROGRESO = "en_progreso"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"


class PrioridadCaso(Enum):
    """Niveles de prioridad de un caso."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "crítica"


@dataclass
class Caso:
    """
    Clase que representa un caso en el sistema de seguimiento.
    
    Atributos:
        id: Identificador único del caso
        titulo: Título descriptivo del caso
        descripcion: Descripción detallada del caso
        estado: Estado actual del caso
        prioridad: Nivel de prioridad del caso
        fecha_creacion: Fecha y hora de creación del caso
        fecha_actualizacion: Fecha y hora de última actualización
        asignado_a: Persona asignada al caso (opcional)
        notas: Notas adicionales sobre el caso
    """
    titulo: str
    descripcion: str
    id: Optional[int] = None
    estado: EstadoCaso = EstadoCaso.ABIERTO
    prioridad: PrioridadCaso = PrioridadCaso.MEDIA
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    asignado_a: Optional[str] = None
    notas: str = ""
    
    def actualizar_estado(self, nuevo_estado: EstadoCaso) -> None:
        """Actualiza el estado del caso."""
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.now()
    
    def actualizar_prioridad(self, nueva_prioridad: PrioridadCaso) -> None:
        """Actualiza la prioridad del caso."""
        self.prioridad = nueva_prioridad
        self.fecha_actualizacion = datetime.now()
    
    def asignar_a(self, persona: str) -> None:
        """Asigna el caso a una persona."""
        self.asignado_a = persona
        self.fecha_actualizacion = datetime.now()
    
    def agregar_nota(self, nota: str) -> None:
        """Agrega una nota al caso."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.notas:
            self.notas += f"\n[{timestamp}] {nota}"
        else:
            self.notas = f"[{timestamp}] {nota}"
        self.fecha_actualizacion = datetime.now()
    
    def __str__(self) -> str:
        """Representación en string del caso."""
        return (f"Caso #{self.id}: {self.titulo}\n"
                f"Estado: {self.estado.value}, Prioridad: {self.prioridad.value}\n"
                f"Asignado a: {self.asignado_a or 'Sin asignar'}\n"
                f"Creado: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
                f"Actualizado: {self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M')}")
