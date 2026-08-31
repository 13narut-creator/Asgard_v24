#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE CONFIGURACIÓN Y CONSTANTES - ASGARD V24
=================================================
Estructura los parámetros de física teórica y de software del simulador.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

class PhysicsConstants:
    """
    Contenedor de constantes universales y parámetros físicos
    para el agujero negro de Kerr y el plasma GRMHD.
    """
    def __init__(self):
        # Constantes Universales Geometrizadas (G = c = 1)
        self.c = 1.0
        self.G = 1.0
        
        # Parámetros del Agujero Negro de Kerr
        self.M = 1.0              # Masa geométrica de referencia
        self.a = 0.90             # Espín adimensional de producción extrema
        
        # Condiciones de Gauge Relativista
        self.g_slicing = "1+log"   # Rebanado temporal estable anti-colapso
        self.gamma_driver_eta = 0.5 # Parámetro de amortiguación del vector shift
        
        # Parámetros de la Materia (GRMHD)
        self.w_fluido = 1.0 / 3.0 # Ecuación de estado (Radiación/Plasma relativista)
        self.amplitud_B = 0.05     # Intensidad inicial del bucle de campo magnético


class ExecutionConfig:
    """
    Gestiona la configuración del entorno de cómputo, límites de la malla,
    pasos temporales (CFL) y persistencia de datos.
    """
    def __init__(self):
        # Configuración de Malla y Hardware
        self.N_global = 128        # Resolución espacial adaptada local
        self.backend = "auto"      # Detección automática CPU/GPU (NumPy/CuPy)
        
        # Evolución Temporal (CFL)
        self.N_pasos = 100         # Iteraciones máximas para pruebas de estabilidad
        self.dt = 0.001            # Paso temporal (Se recalcula dinámicamente en el orquestador)
        
        # Refinamiento Adaptativo de Malla (AMR)
        self.activar_amr = True
        self.umbral_curvatura_amr = 1.2e-6
        self.amr_niveles_max = 3   # Límite de subdivisiones de la red
        
        # Persistencia Científica HDF5 y Resultados
        self.intervalo_checkpoint = 20
        self.dir_resultados = "./resultados_kerr_a09"


class ConfigAsgardV7:
    """
    Clase de compatibilidad hacia atrás (Wrapper Legacy).
    Mapea las solicitudes de la interfaz V7 al nuevo motor estructural V24.
    """
    def __init__(self):
        physics = PhysicsConstants()
        execution = ExecutionConfig()
        
        # Conservar variables planas para compatibilidad con módulos anteriores
        self.c = physics.c
        self.G = physics.G
        self.w_fluido = physics.w_fluido
        self.N = execution.N_global
        self.N_pasos = execution.N_pasos
        self.dt = execution.dt
        self.activar_amr = execution.activar_amr
        self.dir_resultados = execution.dir_resultados
