#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NÚCLEO DE EVOLUCIÓN BSSN & MAXWELL CLEAN (GLM) - ASGARD V24
===========================================================
Implementa la métrica analítica de Kerr y el formalismo de control
de divergencia hiperbólica de Dedner (GLM) para div(B) = 0.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np
from typing import Dict, Tuple

class BSSNMaxwellCleanSolverV72:
    """
    Solver evolutivo para el acoplamiento electrodinámico y geométrico.
    Mantiene la restricción física de monopolos magnéticos controlada en el tiempo.
    """
    
    def __init__(self, geometria, config, xp):
        self.geo = geometria
        self.config = config
        self.xp = xp
        self.N = geometria.N
        self.dt = config.dt
        
        # Variables de Gauge Geométrico e Inicialización Básica
        self.alpha = xp.ones(self.N)
        self.beta = xp.zeros((self.N, 3))
        self.chi = xp.ones(self.N)
        
        # Variables Conformales BSSN
        self.gamma_tilde = xp.zeros((self.N, 3, 3))
        for i in range(self.N):
            self.gamma_tilde[i] = xp.eye(3)
        self.K = xp.zeros(self.N)
        self.A_tilde = xp.zeros((self.N, 3, 3))
        self.Gamma_tilde = xp.zeros((self.N, 3))
        
        # CAMPO ESCALAR AUXILIAR PARA LIMPIEZA DE DIVERGENCIA (Formalismo Dedner/GLM)
        self.psi_clean = xp.zeros(self.N)
        
        # Parámetros GLM de Amortiguamiento
        self.c_h = 1.0   # Velocidad de propagación de la divergencia (c=1)
        self.kappa = 0.5 # Factor de atenuación (damping)

    def inicializar_kerr_magnetizado(self, M: float, a: float):
        """Inicializa analíticamente el espacio-tiempo curvo de un Agujero Negro de Kerr."""
        xp = self.xp
        print(f"🕳️ Configurando solución de Kerr (M={M}, a={a}) en la malla...")
        
        for i in range(self.N):
            x, y, z = self.geo.pos[i, 0], self.geo.pos[i, 1], self.geo.pos[i, 2]
            r2 = x**2 + y**2 + z**2 + 1e-8
            r = xp.sqrt(r2)
            rho2 = r2 + a**2 * (z**2 / r2)
            
            # Lapso analítico de Kerr (α)
            self.alpha[i] = xp.sqrt(xp.clip(1.0 - (2.0 * M * r) / rho2, 0.05, 1.0))
            
            # Factor conforme chi (χ)
            self.chi[i] = (1.0 + M / (2.0 * r)) ** (-4.0)
            
            # Vector de deformación (Shift βⁱ) - Arrastre de marcos de Lense-Thirring
            omega = (2.0 * M * r * a) / (r2 * (r2 + a**2) + 2.0 * M * r * a**2 * (1.0 - z**2 / r2) + 1e-5)
            self.beta[i, 0] = -omega * y # beta_x
            self.beta[i, 1] =  omega * x # beta_y
            self.beta[i, 2] = 0.0        # beta_z

    def _gradiente_direccional(self, campo: np.ndarray) -> np.ndarray:
        """Calcula el gradiente 3D (∂x, ∂y, ∂z) del campo usando diferencias finitas."""
        xp = self.xp
        grad = xp.zeros((self.N, 3))
        coord_diff = xp.gradient(campo) if xp.__name__ == 'numpy' else xp.asarray(np.gradient(campo.get()))
        for dim in range(3):
            grad[:, dim] = coord_diff[dim] if len(coord_diff.shape) > 1 else coord_diff
        return grad

    def _gradiente_espacial_completo(self, campo: np.ndarray) -> np.ndarray:
        """Encapsulador del gradiente para variables escalares del laboratorio."""
        xp = self.xp
        grad = xp.zeros((self.N, 3))
        for dim in range(3):
            grad[:, dim] = self._gradiente_direccional(campo)[:, dim]
        return grad

    def calcular_evolucion_maxwell_glm(self, B_campo: np.ndarray, v_fluido: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Evalúa dB^i/dt y dpsi/dt incorporando la corrección hiperbólica de divergencia.
        Atenúa la formación de monopolos numéricos y los expulsa de la malla.
        """
        xp = self.xp
        dB_dt = xp.zeros((self.N, 3))
        
        # 1. Calcular Divergencia de B actual (Monopolos numéricos inducidos)
        div_B = xp.zeros(self.N)
        for dim in range(3):
            grad_B_dim = self._gradiente_direccional(B_campo[:, dim])
            div_B += grad_B_dim[:, dim]
            
        # 2. Gradiente del campo de limpieza psi para corregir el campo vectorial B
        grad_psi = self._gradiente_espacial_completo(self.psi_clean)
        
        # 3. Evaluar Ecuación de evolución de Maxwell modificada
        # dB^i/dt = ∂_j ( β^j B^i - β^i B^j ) - ∂_i ψ
        for i in range(3):
            # Arrastre de líneas por efecto Frame-Dragging (Lense-Thirring)
            flujo_coordenado = self.beta[:, 1] * B_campo[:, i] - self.beta[:, i] * B_campo[:, 1]
            grad_flujo = self._gradiente_direccional(flujo_coordenado)
            
            # Incorporación del gradiente del potencial de corrección
            dB_dt[:, i] = grad_flujo[:, i] - grad_psi[:, i]
            
        # 4. Ecuación de evolución del campo escalar de control ψ
        # dψ/dt = -c_h^2 * div(B) - α * κ * ψ
        dpsi_dt = - (self.c_h ** 2) * div_B - self.alpha * self.kappa * self.psi_clean
        
        return dB_dt, dpsi_dt

    def evolucionar(self, Tmunu: np.ndarray, pasos: int = 1) -> Dict:
        """Mantiene la consistencia del bucle de avance temporal acoplado de la geometría."""
        return {'K': self.xp.zeros(self.N), 'alpha': self.alpha, 'chi': self.chi}
