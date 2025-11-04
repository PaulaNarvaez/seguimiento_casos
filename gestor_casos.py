"""
Gestor de casos para el sistema de seguimiento.
"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from caso import Caso, EstadoCaso, PrioridadCaso


class GestorCasos:
    """
    Clase para gestionar casos en el sistema de seguimiento.
    Maneja operaciones CRUD y persistencia de datos.
    """
    
    def __init__(self, archivo_datos: str = "casos.json"):
        """
        Inicializa el gestor de casos.
        
        Args:
            archivo_datos: Ruta del archivo JSON para persistencia
        """
        self.archivo_datos = Path(archivo_datos)
        self.casos: Dict[int, Caso] = {}
        self.siguiente_id = 1
        self.cargar_casos()
    
    def crear_caso(self, titulo: str, descripcion: str, 
                   prioridad: PrioridadCaso = PrioridadCaso.MEDIA,
                   asignado_a: Optional[str] = None) -> Caso:
        """
        Crea un nuevo caso.
        
        Args:
            titulo: Título del caso
            descripcion: Descripción del caso
            prioridad: Prioridad del caso
            asignado_a: Persona asignada al caso
        
        Returns:
            El caso creado
        """
        caso = Caso(
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            asignado_a=asignado_a,
            id=self.siguiente_id
        )
        self.casos[self.siguiente_id] = caso
        self.siguiente_id += 1
        self.guardar_casos()
        return caso
    
    def obtener_caso(self, caso_id: int) -> Optional[Caso]:
        """
        Obtiene un caso por su ID.
        
        Args:
            caso_id: ID del caso a buscar
        
        Returns:
            El caso si existe, None en caso contrario
        """
        return self.casos.get(caso_id)
    
    def listar_casos(self, estado: Optional[EstadoCaso] = None,
                     prioridad: Optional[PrioridadCaso] = None) -> List[Caso]:
        """
        Lista todos los casos, opcionalmente filtrados por estado y/o prioridad.
        
        Args:
            estado: Filtrar por estado (opcional)
            prioridad: Filtrar por prioridad (opcional)
        
        Returns:
            Lista de casos que cumplen los filtros
        """
        casos = list(self.casos.values())
        
        if estado:
            casos = [c for c in casos if c.estado == estado]
        
        if prioridad:
            casos = [c for c in casos if c.prioridad == prioridad]
        
        return sorted(casos, key=lambda c: c.fecha_creacion, reverse=True)
    
    def actualizar_caso(self, caso_id: int, **kwargs) -> Optional[Caso]:
        """
        Actualiza un caso existente.
        
        Args:
            caso_id: ID del caso a actualizar
            **kwargs: Atributos a actualizar
        
        Returns:
            El caso actualizado si existe, None en caso contrario
        """
        caso = self.obtener_caso(caso_id)
        if not caso:
            return None
        
        for key, value in kwargs.items():
            if hasattr(caso, key):
                setattr(caso, key, value)
        
        caso.fecha_actualizacion = datetime.now()
        self.guardar_casos()
        return caso
    
    def eliminar_caso(self, caso_id: int) -> bool:
        """
        Elimina un caso.
        
        Args:
            caso_id: ID del caso a eliminar
        
        Returns:
            True si se eliminó el caso, False si no existe
        """
        if caso_id in self.casos:
            del self.casos[caso_id]
            self.guardar_casos()
            return True
        return False
    
    def guardar_casos(self) -> None:
        """Guarda los casos en el archivo JSON."""
        datos = []
        for caso in self.casos.values():
            datos.append({
                'id': caso.id,
                'titulo': caso.titulo,
                'descripcion': caso.descripcion,
                'estado': caso.estado.value,
                'prioridad': caso.prioridad.value,
                'fecha_creacion': caso.fecha_creacion.isoformat(),
                'fecha_actualizacion': caso.fecha_actualizacion.isoformat(),
                'asignado_a': caso.asignado_a,
                'notas': caso.notas
            })
        
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    def cargar_casos(self) -> None:
        """Carga los casos desde el archivo JSON."""
        if not self.archivo_datos.exists():
            return
        
        try:
            # Check file size (limit to 10MB)
            if self.archivo_datos.stat().st_size > 10 * 1024 * 1024:
                print(f"Advertencia: Archivo de casos muy grande (>10MB). No se cargará.")
                return
            
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            for caso_data in datos:
                caso = Caso(
                    titulo=caso_data['titulo'],
                    descripcion=caso_data['descripcion'],
                    id=caso_data['id'],
                    estado=EstadoCaso(caso_data['estado']),
                    prioridad=PrioridadCaso(caso_data['prioridad']),
                    fecha_creacion=datetime.fromisoformat(caso_data['fecha_creacion']),
                    fecha_actualizacion=datetime.fromisoformat(caso_data['fecha_actualizacion']),
                    asignado_a=caso_data.get('asignado_a'),
                    notas=caso_data.get('notas', '')
                )
                self.casos[caso.id] = caso
                if caso.id >= self.siguiente_id:
                    self.siguiente_id = caso.id + 1
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Advertencia: Error al cargar casos - {e}. Iniciando con datos vacíos.")
            self.casos = {}
            self.siguiente_id = 1
