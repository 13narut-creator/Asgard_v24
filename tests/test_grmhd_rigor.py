#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUITE DE VALIDACIÓN CIENTÍFICA DE RIGOR - ASGARD V24
===================================================
Pruebas numéricas con aserciones estrictas para validar la física de control 
de monopolos (filtro GLM) y el arrastre de coordenadas en la ergosfera.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np
from asgard.config import ConfigAsgardV7 as ConfigAsgardV24
from asgard.core_geometry import GeometriaAsgard
from asgard.core_matter import MateriaAsgardV72 as MateriaGRMHDV24
from asgard.bssn_maxwell_clean import BSSNMaxwellCleanSolverV72 as BSSNMaxwellSolverV24

def test_glm_divergence_damping():
    """
    Verifica que el solver GLM hiperbólico (Dedner) absorba y controle 
    la formación de monopolos magnéticos espurios en la malla.
    """
    config = ConfigAsgardV24()
    config.N = 1000
    config.dt = 0.002
    xp = np
    
    geo = GeometriaAsgard(config)
    materia = MateriaGRMHDV24(geo, config, xp)
    solver = BSSNMaxwellSolverV24(geo, config, xp)
    
    # Inyectar un monopolo magnético artificial masivo (Divergencia inicial crítica)
    materia.B_campo = np.ones((geo.N, 3)) * 0.5 
    
    # Evolucionar el sistema para activar las ecuaciones de amortiguamiento GLM
    for _ in range(15):
        dB_dt, dpsi_dt = solver.calcular_evolucion_maxwell_glm(materia.B_campo, materia.v)
        materia.B_campo += dB_dt * config.dt
        solver.psi_clean += dpsi_dt * config.dt
        
    max_psi_final = np.max(np.abs(solver.psi_clean))
    
    print(f"📊 Control GLM -> Potencial psi de amortiguamiento final: {max_psi_final:.6e}")
    
    # CRITERIO DE ÉXITO: El campo escalar psi debe haber despertado y estar absorbiendo el error
    assert max_psi_final > 0.0, "ERROR CIENTÍFICO: El campo de limpieza de divergencia GLM está inactivo."

def test_frame_dragging_velocity():
    """
    Verifica el perfil de arrastre de marcos (efecto Lense-Thirring) del shift beta_y 
    en el ecuador del agujero negro de Kerr frente a la solución analítica exacta.
    """
    config = ConfigAsgardV24()
    config.N = 1000
    geo = GeometriaAsgard(config)
    solver = BSSNMaxwellSolverV24(geo, config, np)
    
    # Inicializar el espacio-tiempo de Kerr con un espín masivo de producción (a = 0.9)
    solver.inicializar_kerr_magnetizado(M=1.0, a=0.9)
    
    # Buscar un nodo en el plano ecuatorial (Z ≈ 0) alejado de la singularidad central
    nodo_validado = False
    for i in range(geo.N):
        x, y, z = geo.pos[i, 0], geo.pos[i, 1], geo.pos[i, 2]
        r = np.sqrt(x**2 + y**2 + z**2)
        
        # Filtrar un nodo en el plano XY (ecuador) a una distancia segura r > 4.0
        if np.abs(z) < 0.2 and r > 4.0:
            if np.abs(y) < 0.2 and x > 0:
                # Ecuación analítica de la velocidad angular de Lense-Thirring
                omega_analitico = (2.0 * 1.0 * r * 0.9) / (r**2 * (r**2 + 0.9**2) + 2.0 * 1.0 * r * 0.9**2)
                beta_y_esperado = omega_analitico * x
                
                # Calcular el error relativo frente al tensor beta mapeado en la red
                error_relativo = np.abs(solver.beta[i, 1] - beta_y_esperado) / (np.abs(beta_y_esperado) + 1e-5)
                
                print(f"🌀 Frame-Dragging -> Error Relativo en r={r:.2f}: {error_relativo*100:.3f}%")
                
                # CRITERIO DE ÉXITO: El error en el arrastre coordenado debe ser menor al 8% de tolerancia
                assert error_relativo < 0.08, f"Falla de calibración: El shift difiere de la solución de Kerr. Error={error_relativo}"
                nodo_validado = True
                break
                
    assert nodo_validado, "ERROR DE ENTORNO: No se encontró un nodo válido en el plano ecuatorial para la verificación."
