#!/usr/bin/env python3
"""
Interfaz de línea de comandos para el sistema de seguimiento de casos.
"""
import argparse
import sys
from typing import Optional

from gestor_casos import GestorCasos
from caso import EstadoCaso, PrioridadCaso


def listar_casos_cmd(gestor: GestorCasos, args) -> None:
    """Lista los casos con filtros opcionales."""
    estado = None
    if args.estado:
        try:
            estado = EstadoCaso(args.estado)
        except ValueError:
            print(f"Estado inválido: {args.estado}")
            print(f"Estados válidos: {', '.join([e.value for e in EstadoCaso])}")
            return
    
    prioridad = None
    if args.prioridad:
        try:
            prioridad = PrioridadCaso(args.prioridad)
        except ValueError:
            print(f"Prioridad inválida: {args.prioridad}")
            print(f"Prioridades válidas: {', '.join([p.value for p in PrioridadCaso])}")
            return
    
    casos = gestor.listar_casos(estado=estado, prioridad=prioridad)
    
    if not casos:
        print("No se encontraron casos.")
        return
    
    print(f"\nTotal de casos: {len(casos)}\n")
    for caso in casos:
        print("=" * 60)
        print(caso)
        if caso.descripcion:
            print(f"Descripción: {caso.descripcion}")
        print()


def crear_caso_cmd(gestor: GestorCasos, args) -> None:
    """Crea un nuevo caso."""
    prioridad = PrioridadCaso.MEDIA
    if args.prioridad:
        try:
            prioridad = PrioridadCaso(args.prioridad)
        except ValueError:
            print(f"Prioridad inválida: {args.prioridad}")
            print(f"Prioridades válidas: {', '.join([p.value for p in PrioridadCaso])}")
            return
    
    caso = gestor.crear_caso(
        titulo=args.titulo,
        descripcion=args.descripcion,
        prioridad=prioridad,
        asignado_a=args.asignado_a
    )
    
    print(f"\n✓ Caso creado exitosamente:")
    print(caso)


def ver_caso_cmd(gestor: GestorCasos, args) -> None:
    """Muestra los detalles de un caso."""
    caso = gestor.obtener_caso(args.id)
    if not caso:
        print(f"No se encontró el caso #{args.id}")
        return
    
    print("\n" + "=" * 60)
    print(caso)
    print(f"\nDescripción: {caso.descripcion}")
    if caso.notas:
        print(f"\nNotas:\n{caso.notas}")
    print("=" * 60)


def actualizar_caso_cmd(gestor: GestorCasos, args) -> None:
    """Actualiza un caso existente."""
    kwargs = {}
    
    if args.titulo:
        kwargs['titulo'] = args.titulo
    
    if args.descripcion:
        kwargs['descripcion'] = args.descripcion
    
    if args.estado:
        try:
            kwargs['estado'] = EstadoCaso(args.estado)
        except ValueError:
            print(f"Estado inválido: {args.estado}")
            print(f"Estados válidos: {', '.join([e.value for e in EstadoCaso])}")
            return
    
    if args.prioridad:
        try:
            kwargs['prioridad'] = PrioridadCaso(args.prioridad)
        except ValueError:
            print(f"Prioridad inválida: {args.prioridad}")
            print(f"Prioridades válidas: {', '.join([p.value for p in PrioridadCaso])}")
            return
    
    if args.asignado_a:
        kwargs['asignado_a'] = args.asignado_a
    
    if not kwargs:
        print("No se especificaron campos para actualizar.")
        return
    
    caso = gestor.actualizar_caso(args.id, **kwargs)
    if caso:
        print(f"\n✓ Caso actualizado exitosamente:")
        print(caso)
    else:
        print(f"No se encontró el caso #{args.id}")


def agregar_nota_cmd(gestor: GestorCasos, args) -> None:
    """Agrega una nota a un caso."""
    caso = gestor.obtener_caso(args.id)
    if not caso:
        print(f"No se encontró el caso #{args.id}")
        return
    
    caso.agregar_nota(args.nota)
    gestor.guardar_casos()
    print(f"\n✓ Nota agregada al caso #{args.id}")


def eliminar_caso_cmd(gestor: GestorCasos, args) -> None:
    """Elimina un caso."""
    if gestor.eliminar_caso(args.id):
        print(f"\n✓ Caso #{args.id} eliminado exitosamente.")
    else:
        print(f"No se encontró el caso #{args.id}")


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Seguimiento de Casos",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--archivo',
        default='casos.json',
        help='Archivo de datos para casos (default: casos.json)'
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # Comando: listar
    listar_parser = subparsers.add_parser('listar', help='Lista los casos')
    listar_parser.add_argument('--estado', help='Filtrar por estado')
    listar_parser.add_argument('--prioridad', help='Filtrar por prioridad')
    
    # Comando: crear
    crear_parser = subparsers.add_parser('crear', help='Crea un nuevo caso')
    crear_parser.add_argument('titulo', help='Título del caso')
    crear_parser.add_argument('descripcion', help='Descripción del caso')
    crear_parser.add_argument('--prioridad', help='Prioridad del caso')
    crear_parser.add_argument('--asignado-a', help='Persona asignada al caso')
    
    # Comando: ver
    ver_parser = subparsers.add_parser('ver', help='Ver detalles de un caso')
    ver_parser.add_argument('id', type=int, help='ID del caso')
    
    # Comando: actualizar
    actualizar_parser = subparsers.add_parser('actualizar', help='Actualiza un caso')
    actualizar_parser.add_argument('id', type=int, help='ID del caso')
    actualizar_parser.add_argument('--titulo', help='Nuevo título')
    actualizar_parser.add_argument('--descripcion', help='Nueva descripción')
    actualizar_parser.add_argument('--estado', help='Nuevo estado')
    actualizar_parser.add_argument('--prioridad', help='Nueva prioridad')
    actualizar_parser.add_argument('--asignado-a', help='Nueva persona asignada')
    
    # Comando: nota
    nota_parser = subparsers.add_parser('nota', help='Agrega una nota a un caso')
    nota_parser.add_argument('id', type=int, help='ID del caso')
    nota_parser.add_argument('nota', help='Texto de la nota')
    
    # Comando: eliminar
    eliminar_parser = subparsers.add_parser('eliminar', help='Elimina un caso')
    eliminar_parser.add_argument('id', type=int, help='ID del caso')
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    gestor = GestorCasos(args.archivo)
    
    comandos = {
        'listar': listar_casos_cmd,
        'crear': crear_caso_cmd,
        'ver': ver_caso_cmd,
        'actualizar': actualizar_caso_cmd,
        'nota': agregar_nota_cmd,
        'eliminar': eliminar_caso_cmd
    }
    
    if args.comando in comandos:
        comandos[args.comando](gestor, args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
