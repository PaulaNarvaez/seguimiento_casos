"""
Sistema de Seguimiento de Casos

Un sistema simple y eficiente para gestionar casos con estados, prioridades,
asignaciones y notas.
"""

from caso import Caso, EstadoCaso, PrioridadCaso
from gestor_casos import GestorCasos

__version__ = "1.0.0"
__all__ = ['Caso', 'EstadoCaso', 'PrioridadCaso', 'GestorCasos']
