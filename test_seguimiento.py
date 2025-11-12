"""
Tests para el sistema de seguimiento de casos.
"""
import unittest
import os
import tempfile
from datetime import datetime

from caso import Caso, EstadoCaso, PrioridadCaso
from gestor_casos import GestorCasos


class TestCaso(unittest.TestCase):
    """Tests para la clase Caso."""
    
    def test_crear_caso_basico(self):
        """Test crear un caso básico."""
        caso = Caso(titulo="Test", descripcion="Descripción de prueba")
        self.assertEqual(caso.titulo, "Test")
        self.assertEqual(caso.descripcion, "Descripción de prueba")
        self.assertEqual(caso.estado, EstadoCaso.ABIERTO)
        self.assertEqual(caso.prioridad, PrioridadCaso.MEDIA)
        self.assertIsNone(caso.asignado_a)
    
    def test_actualizar_estado(self):
        """Test actualizar el estado de un caso."""
        caso = Caso(titulo="Test", descripcion="Desc")
        fecha_inicial = caso.fecha_actualizacion
        caso.actualizar_estado(EstadoCaso.EN_PROGRESO)
        self.assertEqual(caso.estado, EstadoCaso.EN_PROGRESO)
        self.assertGreater(caso.fecha_actualizacion, fecha_inicial)
    
    def test_actualizar_prioridad(self):
        """Test actualizar la prioridad de un caso."""
        caso = Caso(titulo="Test", descripcion="Desc")
        caso.actualizar_prioridad(PrioridadCaso.ALTA)
        self.assertEqual(caso.prioridad, PrioridadCaso.ALTA)
    
    def test_asignar_a(self):
        """Test asignar un caso a una persona."""
        caso = Caso(titulo="Test", descripcion="Desc")
        caso.asignar_a("Juan Pérez")
        self.assertEqual(caso.asignado_a, "Juan Pérez")
    
    def test_agregar_nota(self):
        """Test agregar notas a un caso."""
        caso = Caso(titulo="Test", descripcion="Desc")
        caso.agregar_nota("Primera nota")
        self.assertIn("Primera nota", caso.notas)
        caso.agregar_nota("Segunda nota")
        self.assertIn("Primera nota", caso.notas)
        self.assertIn("Segunda nota", caso.notas)
    
    def test_string_representation(self):
        """Test representación en string del caso."""
        caso = Caso(titulo="Test", descripcion="Desc", id=1)
        string_repr = str(caso)
        self.assertIn("Caso #1", string_repr)
        self.assertIn("Test", string_repr)


class TestGestorCasos(unittest.TestCase):
    """Tests para la clase GestorCasos."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        # Crear archivo temporal para tests
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.gestor = GestorCasos(self.temp_file.name)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_crear_caso(self):
        """Test crear un nuevo caso."""
        caso = self.gestor.crear_caso(
            titulo="Test Caso",
            descripcion="Descripción de prueba"
        )
        self.assertIsNotNone(caso.id)
        self.assertEqual(caso.titulo, "Test Caso")
        self.assertEqual(len(self.gestor.casos), 1)
    
    def test_crear_multiples_casos(self):
        """Test crear múltiples casos con IDs únicos."""
        caso1 = self.gestor.crear_caso("Caso 1", "Descripción 1")
        caso2 = self.gestor.crear_caso("Caso 2", "Descripción 2")
        self.assertNotEqual(caso1.id, caso2.id)
        self.assertEqual(len(self.gestor.casos), 2)
    
    def test_obtener_caso(self):
        """Test obtener un caso por ID."""
        caso = self.gestor.crear_caso("Test", "Descripción")
        caso_obtenido = self.gestor.obtener_caso(caso.id)
        self.assertIsNotNone(caso_obtenido)
        self.assertEqual(caso_obtenido.titulo, "Test")
    
    def test_obtener_caso_inexistente(self):
        """Test obtener un caso que no existe."""
        caso = self.gestor.obtener_caso(999)
        self.assertIsNone(caso)
    
    def test_listar_casos(self):
        """Test listar todos los casos."""
        self.gestor.crear_caso("Caso 1", "Desc 1")
        self.gestor.crear_caso("Caso 2", "Desc 2")
        self.gestor.crear_caso("Caso 3", "Desc 3")
        casos = self.gestor.listar_casos()
        self.assertEqual(len(casos), 3)
    
    def test_listar_casos_por_estado(self):
        """Test listar casos filtrados por estado."""
        caso1 = self.gestor.crear_caso("Caso 1", "Desc 1")
        caso2 = self.gestor.crear_caso("Caso 2", "Desc 2")
        caso1.actualizar_estado(EstadoCaso.EN_PROGRESO)
        
        casos_abiertos = self.gestor.listar_casos(estado=EstadoCaso.ABIERTO)
        casos_en_progreso = self.gestor.listar_casos(estado=EstadoCaso.EN_PROGRESO)
        
        self.assertEqual(len(casos_abiertos), 1)
        self.assertEqual(len(casos_en_progreso), 1)
    
    def test_listar_casos_por_prioridad(self):
        """Test listar casos filtrados por prioridad."""
        self.gestor.crear_caso("Caso 1", "Desc 1", prioridad=PrioridadCaso.ALTA)
        self.gestor.crear_caso("Caso 2", "Desc 2", prioridad=PrioridadCaso.BAJA)
        
        casos_alta = self.gestor.listar_casos(prioridad=PrioridadCaso.ALTA)
        self.assertEqual(len(casos_alta), 1)
    
    def test_actualizar_caso(self):
        """Test actualizar un caso."""
        caso = self.gestor.crear_caso("Original", "Desc")
        caso_actualizado = self.gestor.actualizar_caso(
            caso.id,
            titulo="Actualizado",
            estado=EstadoCaso.RESUELTO
        )
        self.assertEqual(caso_actualizado.titulo, "Actualizado")
        self.assertEqual(caso_actualizado.estado, EstadoCaso.RESUELTO)
    
    def test_actualizar_caso_inexistente(self):
        """Test actualizar un caso que no existe."""
        resultado = self.gestor.actualizar_caso(999, titulo="Test")
        self.assertIsNone(resultado)
    
    def test_eliminar_caso(self):
        """Test eliminar un caso."""
        caso = self.gestor.crear_caso("Test", "Desc")
        self.assertTrue(self.gestor.eliminar_caso(caso.id))
        self.assertEqual(len(self.gestor.casos), 0)
    
    def test_eliminar_caso_inexistente(self):
        """Test eliminar un caso que no existe."""
        self.assertFalse(self.gestor.eliminar_caso(999))
    
    def test_persistencia_casos(self):
        """Test guardar y cargar casos desde archivo."""
        # Crear casos
        self.gestor.crear_caso("Caso 1", "Desc 1")
        self.gestor.crear_caso("Caso 2", "Desc 2", prioridad=PrioridadCaso.ALTA)
        
        # Crear nuevo gestor con el mismo archivo
        gestor2 = GestorCasos(self.temp_file.name)
        
        # Verificar que los casos se cargaron correctamente
        self.assertEqual(len(gestor2.casos), 2)
        casos = gestor2.listar_casos()
        self.assertEqual(casos[0].titulo, "Caso 2")  # Ordenados por fecha
        self.assertEqual(casos[0].prioridad, PrioridadCaso.ALTA)


if __name__ == '__main__':
    unittest.main()
