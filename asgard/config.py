#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE CONFIGURACIÓN GLOBAL - ASGARD V24
===========================================
Centraliza los parámetros físicos, numéricos y de hardware de la simulación.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

class ConfigAsgardV7:
    """
    Contenedor de constantes universales, límites de la malla y 
    parámetros de control para el acoplamiento BSSN + GRMHD.
    """
    def __init__(self):
        # 1. CONSTANTES FÍSICAS FUNDAMENTALES (Unidades Geometrizadas)
        self.c = 1.0        # Velocidad de la luz
        self.G = 1.0        # Constante de gravitación de Einstein
        
        # 2. CONFIGURACIÓN DE LA MALLA / RED
        self.N = 3500       # Número de nodos o puntos en el espacio-tiempo
        self.R = 40.0       # Radio máximo de la frontera de simulación
        
        # 3. EVOLUCIÓN TEMPORAL
        self.N_pasos = 150  # Número total de iteraciones temporales en producción
        self.dt = 0.002     # Paso de tiempo físico (Delta t) para estabilidad RK4
        
        # 4. PARÁMETROS DE FLUIDO Y MATERIA
        self.w_fluido = 1.0 / 3.0 # Ecuación de estado fluido perfecto relativista (Radiación)
        self.activar_amr = True    # Refinamiento adaptativo de malla activado por defecto
        
        # 5. CONTROL DE DIAGNÓSTICOS Y PERSISTENCIA
        self.intervalo_medicion = 10   # Cada cuántos pasos se imprime telemetría
        self.dir_resultados = "./resultados_v24" # Directorio de exportación de datos
        
        # 6. CONFIGURACIÓN DE HARDWARE
        # 'auto' detecta GPU/CuPy; 'gpu' la fuerza; 'cpu' fuerza NumPy estándar
        self.backend_mode = 'cpu' 
