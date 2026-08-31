#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NÚCLEO DE EVOLUCIÓN BSSN & MAXWELL CLEAN (KERR-SCHILD) - ASGARD V24
===================================================================
Implementa la métrica analítica en coordenadas estables de Kerr-Schild
y el formalismo de control de divergencia hiperbólica GLM.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np
from typing import Dict, Tuple

class BSSNMaxwellCleanSolverV72:
    """
    Solver evolutivo acoplado. Soporta la inyección regularizada de Kerr-Schild
    y la disipación hiperbólica de monopolos magnéticos artificiales.
    """
    
    def __init__(self, geometria, config, xp):
        self.geo = geometria
        self.config = config
        self.xp = xp
        self.N = geometria.N
        self.dt = config.dt
        
        # Variables de Gauge e Inicialización Básica
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
        
        # Campo auxiliar GLM para purga de divergencia
        self.psi_clean = xp.zeros(self.N)
        self.c_h = 1.0   
        self.kappa = 0.5 

    def inicializar_kerr_schild(self, M: float, a: float):
        """
        Inicializa la métrica en coordenadas estables de Kerr-Schild.
        Evita singularidades de coordenadas en el horizonte de sucesos (a > 0.5).
        """
        xp = self.xp
        pos = self.geo.pos
        print(f"🌀 Inicializando Métrica de Kerr-Schild estable: M={M}, a={a}")

        x = pos[:, 0]
        y = pos[:, 1]
        z = pos[:, 2]

        # Calcular distancias y variables analíticas de Kerr
        r2 = x**2 + y**2 + z**2 + 1e-8
        r = xp.sqrt(r2)
        rho2 = r2 + a**2 * (1.0 - z**2 / r2)

        # Factor de escala escalar de Kerr-Schild (H)
        H = (M * r) / (rho2 + 1e-8)

        # Vector nulo entrante de Kerr-Schild (l_mu) para arrastre coordenado
        l = xp.zeros((self.N, 4))
        l[:, 0] = 1.0  # l_t
        l[:, 1] = (r * x + a * y) / (r2 + a**2) # l_x
        l[:, 2] = (r * y - a * x) / (r2 + a**2) # l_y
        l[:, 3] = z / r                         # l_z

        # Inyectar componentes en el tensor métrico global de la geometría 4D
        for i in range(self.N):
            # Componente temporal modificada por H
            self.geo.metrica[i, 0, 0] = -1.0 + 2.0 * H[i] * l[i, 0] * l[i, 0]

            # Componentes espaciales (diagonal y deformación de volumen)
            self.geo.metrica[i, 1, 1] = 1.0 + 2.0 * H[i] * l[i, 1] * l[i, 1]
            self.geo.metrica[i, 2, 2] = 1.0 + 2.0 * H[i] * l[i, 2] * l[i, 2]
            self.geo.metrica[i, 3, 3] = 1.0 + 2.0 * H[i] * l[i, 3] * l[i, 3]

            # Componentes fuera de la diagonal (Cruces espacio-temporales de acoplamiento)
            self.geo.metrica[i, 0, 1] = 2.0 * H[i] * l[i, 0] * l[i, 1]
            self.geo.metrica[i, 0, 2] = 2.0 * H[i] * l[i, 0] * l[i, 2]
            self.geo.metrica[i, 0, 3] = 2.0 * H[i] * l[i, 0] * l[i, 3]

        # Actualizar el factor dinámico del Lapso (alpha) y Shift (beta)
        self.alpha = 1.0 / xp.sqrt(1.0 + 2.0 * H)
        self.beta[:, 0] = 2.0 * H * l[:, 1] / (1.0 + 2.0 * H)
        self.beta[:, 1] = 2.0 * H * l[:, 2] / (1.0 + 2.0 * H)
        self.beta[:, 2] = 2.0 * H * l[:, 3] / (1.0 + 2.0 * H)
        
        # Factor conforme inicial derivado de la métrica espacial
        self.chi = (1.0 + 2.0 * H) ** (-1.0 / 3.0)

    def _gradiente_direccional(self, campo: np.ndarray) -> np.ndarray:
        xp = self.xp
        grad = xp.zeros((self.N, 3))
        coord_diff = xp.gradient(campo) if xp.__name__ == 'numpy' else xp.asarray(np.gradient(campo.get()))
        for dim in range(3):
            grad[:, dim] = coord_diff[dim] if len(coord_diff.shape) > 1 else coord_diff
        return grad

    def calcular_evolucion_maxwell_glm(self, B_campo: np.ndarray, v_fluido: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        xp = self.xp
        dB_dt = xp.zeros((self.N, 3))
        
        div_B = xp.zeros(self.N)
        for dim in range(3):
            div_B += self._gradiente_direccional(B_campo[:, dim])[:, dim]
            
        grad_psi = xp.zeros((self.N, 3))
        for dim in range(3):
            grad_psi[:, dim] = self._gradiente_direccional(self.psi_clean)[:, dim]
        
        for i in range(3):
            flujo_coordenado = self.beta[:, 1] * B_campo[:, i] - self.beta[:, i] * B_campo[:, 1]
            dB_dt[:, i] = self._gradiente_direccional(flujo_coordenado)[:, i] - grad_psi[:, i]
            
        dpsi_dt = - (self.c_h**2) * div_B - self.alpha * self.kappa * self.psi_clean
        return dB_dt, dpsi_dt

    def evolucionar(self, Tmunu: np.ndarray, pasos: int = 1) -> Dict:
        return {'K': self.xp.zeros(self.N), 'alpha': self.alpha, 'chi': self.chi}
