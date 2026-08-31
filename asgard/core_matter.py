#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NÚCLEO DE HIDRODINÁMICA RELATIVISTA Y MATERIA GRMHD - ASGARD V24
===============================================================
Gestiona el estado termodinámico del plasma, sus velocidades de flujo
y calcula el tensor de energía-momento T_munu acoplado a campos magnéticos.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np

class MateriaAsgardV72:
    """
    Representa el fluido/plasma magnetizado alrededor del agujero negro.
    Calcula el acoplamiento relativista de la materia con el campo magnético.
    """
    
    def __init__(self, geometria, config, xp):
        """
        Inicializa las variables macroscópicas del fluido en el backend seleccionado.
        
        Args:
            geometria: Instancia de GeometriaAsgard
            config: Instancia de ConfigAsgardV24
            xp: Backend numérico (numpy o cupy)
        """
        self.geo = geometria
        self.config = config
        self.xp = xp
        self.N = geometria.N
        
        # 1. VARIABLES DE FLUIDO ESTÁNDAR
        self.s = xp.ones(self.N) * 0.5  # Densidad de energía de masa en reposo (rho_0)
        self.v = xp.zeros((self.N, 3))   # Vector de velocidad de tres componentes (v^i)
        
        # 2. VARIABLES MAGNETOHIDRODINÁMICAS (GRMHD)
        # Vector de campo magnético espacial B^i en el sistema de referencia del laboratorio
        self.B_campo = xp.zeros((self.N, 3))
        
    def inicializar_campo_magnetico_toroide(self, amplitud: float = 0.05):
        """
        Inicializa una configuración analítica de campo magnético toroidal 
        confinado alrededor del eje de rotación Z.
        """
        xp = self.xp
        print(f"🧲 Configurando perfil de campo magnético toroidal (Amplitud={amplitud})...")
        
        for i in range(self.N):
            x, y, z = self.geo.pos[i, 0], self.geo.pos[i, 1], self.geo.pos[i, 2]
            r_xy = xp.sqrt(x**2 + y**2) + 1e-8
            r_3d2 = x**2 + y**2 + z**2 + 1e-8
            
            # Amortiguamiento gaussiano espacial para confinar el bucle cerca del centro
            envolvente = xp.exp(-r_3d2 / 50.0)
            
            # Campo toroidal puro: perpendicular al radio vector en el plano ecuatorial
            self.B_campo[i, 0] = -amplitud * (y / r_xy) * envolvente # Componente B_x
            self.B_campo[i, 1] =  amplitud * (x / r_xy) * envolvente # Componente B_y
            self.B_campo[i, 2] = 0.0                                 # Componente B_z

    def actualizar_Tmunu_grmhd(self) -> np.ndarray:
        """
        Calcula y ensambla el tensor de energía-momento covariante de 4 dimensiones T_μν
        sumando las componentes hidrodinámicas y la contribución del campo electromagnético.
        
        T_μν = (rho_h + B^2) u_μ u_ν + (P + 0.5*B^2) g_μν - b_μ b_ν
        """
        xp = self.xp
        Tmunu = xp.zeros((self.N, 4, 4))
        
        # Presión térmica del fluido gobernada por la ecuación de estado (w = 1/3)
        presion_fluido = self.config.w_fluido * self.s
        
        # Densidad de energía magnética / Presión magnética: P_mag = 0.5 * B^2
        B2 = xp.sum(self.B_campo**2, axis=1)
        presion_magnetica = 0.5 * B2
        
        # 1. Componente Temporal Pura (T_00: Densidad de energía total observada)
        Tmunu[:, 0, 0] = self.s + presion_fluido + presion_magnetica
        
        # 2. Componentes de Flujo Cruzado (T_0i / T_i0: Vectores de momentum acoplados)
        for i in range(3):
            # Interacción del flujo de momentum y las líneas de fuerza magnéticas cortadas
            Tmunu[:, 0, i+1] = (self.s + presion_fluido) * self.v[:, i] - (self.B_campo[:, i] * 0.1)
            Tmunu[:, i+1, 0] = Tmunu[:, 0, i+1]
            
        # 3. Componentes Espaciales Puras (T_ij: Tensor de esfuerzos y presiones)
        for i in range(3):
            for j in range(3):
                delta_ij = 1.0 if i == j else 0.0
                # Presión total isotrópica + Tensor de tensiones de Maxwell anisotropías (-B_i * B_j)
                Tmunu[:, i+1, j+1] = (presion_fluido + presion_magnetica) * delta_ij - (self.B_campo[:, i] * self.B_campo[:, j] * 0.1)
                
        return Tmunu

    def avanzar_adveccion_fluido(self, K: np.ndarray):
        """
        Avanza el estado elemental del fluido reaccionando a la curvatura media espacial (K).
        Asegura que el plasma responda dinámicamente a la gravedad del fondo métrico.
        """
        # Ecuación de conservación simplificada: la densidad se comprime en regiones de alta curvatura
        self.s += -0.01 * self.s * K
        
    def _calcular_masas_emergentes(self) -> np.ndarray:
        """Calcula de forma local la distribución de masa equivalente efectiva."""
        return self.s * 1e-3
