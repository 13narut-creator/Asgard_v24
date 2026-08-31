#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE EXTRACCIÓN DE ENERGÍA ELECTROMAGNÉTICA - ASGARD V24
=============================================================
Calcula el Vector de Poynting relativista en la ergosfera y la potencia 
total extraída del agujero negro de Kerr (Mecanismo Blandford-Znajek).

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np

class PoyntingExtractorV72:
    """
    Analizador de flujo energético electromagnético en espaciostiempos curvos.
    Mide la eficiencia de extracción de energía rotacional de agujeros negros.
    """
    
    def __init__(self, geometria, xp):
        """
        Inicializa el extractor de Poynting enlazado al backend de hardware.
        
        Args:
            geometria: Objeto GeometriaAsgard con las posiciones de la malla
            xp: Backend numérico (numpy o cupy)
        """
        self.geo = geometria
        self.xp = xp
        self.N = geometria.N
        
        # Símbolo de Levi-Civita tridimensional (tensor completamente antisimétrico)
        epsilon = np.zeros((3, 3, 3))
        epsilon[0, 1, 2] = epsilon[1, 2, 0] = epsilon[2, 0, 1] = 1.0
        epsilon[0, 2, 1] = epsilon[2, 1, 0] = epsilon[1, 0, 2] = -1.0
        self.epsilon = xp.asarray(epsilon)

    def calcular_vector_poynting(self, B_campo: np.ndarray, v_fluido: np.ndarray, chi: np.ndarray) -> np.ndarray:
        """
        Calcula el vector de Poynting espacial S_i = epsilon_{ijk} E^j B^k.
        Determina E^j a partir de la condición de GRMHD ideal (E = -v x B).
        
        Args:
            B_campo: Tensor del campo magnético del laboratorio (N x 3)
            v_fluido: Tensor de velocidad de tres componentes (N x 3)
            chi: Factor conforme de BSSN (N)
            
        Returns:
            Tensor del flujo de Poynting covariante (N x 3)
        """
        xp = self.xp
        
        # 1. Calcular el Campo Eléctrico inducido en el laboratorio: E_i = - epsilon_{ijk} v^j B^k
        E_campo = xp.zeros((self.N, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    E_campo[:, i] -= self.epsilon[i, j, k] * v_fluido[:, j] * B_campo[:, k]
                    
        # 2. Calcular el Vector de Poynting espacial: S_i = epsilon_{ijk} E^j B^k
        S_poynting = xp.zeros((self.N, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    S_poynting[:, i] += self.epsilon[i, j, k] * E_campo[:, j] * B_campo[:, k]
                    
        # Proyección métrica: Corrección relativista generalizada usando el factor conforme chi
        # S_i_relativista = chi^(-3/2) * S_i_plano
        factor_metrico = (chi + 1e-8) ** (-1.5)
        return S_poynting * factor_metrico[:, xp.newaxis]

    def medir_potencia_extraida(self, S_poynting: np.ndarray, radio_extraccion: float = 5.0) -> float:
        """
        Calcula la luminosidad electromagnética (L) total integrando el flujo neto saliente 
        en una capa esférica de control que rodea la ergosfera.
        
        Args:
            S_poynting: Tensor del flujo de Poynting calculado (N x 3)
            radio_extraccion: Radio de la superficie de control esférica
            
        Returns:
            Potencia electromagnética neta extraída (escalar flotante)
        """
        xp = self.xp
        r = xp.linalg.norm(self.geo.pos, axis=1)
        
        # Seleccionar los nodos geométricos que caen dentro de la capa esférica de muestreo
        capa_mask = xp.abs(r - radio_extraccion) < 1.0
        if xp.sum(capa_mask) == 0:
            return 0.0
            
        # Determinar los vectores normales radiales unitarios (dSigma) para el producto punto
        n_radial = self.geo.pos[capa_mask] / r[capa_mask, xp.newaxis]
        S_capa = S_poynting[capa_mask]
        
        # Producto punto covariante S_i * n^i para aislar el flujo radial saliente
        flujo_radial = xp.sum(S_capa * n_radial, axis=1)
        
        # Integral discreta de superficie: Flujo radial promedio multiplicado por el área de la esfera
        area_esfera = 4.0 * xp.pi * (radio_extraccion ** 2)
        potencia_L = float(xp.mean(flujo_radial) * area_esfera)
        
        return max(0.0, potencia_L) # Retorna solo flujos de extracción positivos (salientes)
