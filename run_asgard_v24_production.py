#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORQUESTADOR DE PRODUCCIÓN MAESTRO - ASGARD V24
======================================================
Pipeline unificado de Relatividad Numérica y GRMHD Evolutivo.
Maneja las importaciones modulares desde el paquete local 'asgard'.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import os
import sys
import time
import numpy as np
import pandas as pd

# Asegurar que el directorio raíz esté en el PATH para ejecuciones desde subcarpetas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ====================================================================
# PARÁMETROS DE IMPORTACIÓN INTERNOS (PAQUETE ASGARD CORREGIDO V24)
# ====================================================================
from asgard.config import ConfigAsgardV7 as ConfigAsgardV24
from asgard.core_geometry import GeometriaAsgard
from asgard.core_matter import MateriaAsgardV72 as MateriaGRMHDV24
from asgard.bssn_maxwell_clean import BSSNMaxwellCleanSolverV72 as BSSNMaxwellSolverV24
from asgard.poynting_extractor import PoyntingExtractorV72 as PoyntingExtractorV24
from asgard.ray_tracer import RayTracerKerrV72 as RayTracerV24

# Importación de la Suite de Rigor Científico para el Check-In de GitHub
from tests.test_grmhd_rigor import test_glm_divergence_damping, test_frame_dragging_velocity

def ejecutar_produccion_total():
    print("====================================================================")
    print("🌟 RUNNING PRODUCTION PIPELINE: ASGARD V24 CELESTIAL")
    print("====================================================================")
    
    # 1. Suite de Validación Pre-Vuelo
    print("\n🔬 [1/4] Corriendo Suite de Validación Científica...")
    test_glm_divergence_damping()
    test_frame_dragging_velocity()
    print("   ✅ Todas las pruebas de rigor han pasado exitosamente.")
    
    # 2. Inicialización del Entorno con alias V24
    print("\n🌀 [2/4] Configurando Agujero Negro de Kerr Magnetizado Extremo...")
    config = ConfigAsgardV24()
    config.N = 3500
    config.N_pasos = 150
    config.dt = 0.002
    xp = np  # Backend unificado
    
    geo = GeometriaAsgard(config)
    materia = MateriaGRMHDV24(geo, config, xp)
    solver = BSSNMaxwellSolverV24(geo, config, xp)
    extractor = PoyntingExtractorV24(geo, xp)
    
    # Establecer masa y espín de Kerr (a = 0.98, rotación extrema de producción)
    solver.inicializar_kerr_magnetizado(M=1.0, a=0.98)
    materia.inicializar_campo_magnetico_toroide(amplitud=0.09)
    
    # Forzar órbitas de velocidad del plasma en el disco de acreción
    for i in range(geo.N):
        x, y = geo.pos[i, 0], geo.pos[i, 1]
        r_xy = np.sqrt(x**2 + y**2) + 1e-5
        if r_xy < 10.0:
            materia.v[i, 0] = -0.2 * (y / r_xy)
            materia.v[i, 1] =  0.2 * (x / r_xy)

    # 3. Bucle de Evolución y Monitoreo Energético
    print("\n⚡ [3/4] Avanzando Sistema Acoplado BSSN + Maxwell + GLM...")
    print("-" * 80)
    print(f"{'Paso':<8} | {'Divergencia B (Máx)':<22} | {'Potencia Extraída L (BZ)':<24}")
    print("-" * 80)
    
    historial = []
    
    for paso in range(config.N_pasos):
        # Avanzar electrodinámica con control de monopolos
        dB_dt, dpsi_dt = solver.calcular_evolucion_maxwell_glm(materia.B_campo, materia.v)
        materia.B_campo += dB_dt * config.dt
        solver.psi_clean += dpsi_dt * config.dt
        
        # Medir flujo de energía de Poynting
        S_p = extractor.calcular_vector_poynting(materia.B_campo, materia.v, solver.chi)
        potencia_L = extractor.medir_potencia_extraida(S_p, radio_extraccion=5.0)
        
        if paso % 25 == 0:
            max_psi = float(np.max(np.abs(solver.psi_clean)))
            print(f"{paso:<8} | {max_psi:<22.6e} | {potencia_L:<24.6e} erg/s")
            
            historial.append({
                'paso': paso,
                'max_psi': max_psi,
                'potencia_L': potencia_L
            })
            
    print("-" * 80)
    print("   ✅ Evolución y extracción de Poynting concluidas.")
    
    # Guardar métricas en disco
    os.makedirs("./resultados_v24", exist_ok=True)
    pd.DataFrame(historial).to_csv("./resultados_v24/produccion_poynting.csv", index=False)
    
    # 4. Renderizado Final por Trazado de Rayos Relativista
    print("\n📸 [4/4] Inicializando Cámara de Ray-Tracing Relativista...")
    tracer = RayTracerV24(geo, solver)
    matriz_optica = tracer.generar_imagen_sombra(resolucion=100)
    tracer.guardar_render_optico(matriz_optica)
    
    print("\n🏆 ASGARD V24 TOTALMENTE VALIDADO, EVOLUCIONADO Y CONSOLIDADO.")
    print("   - Repositorio listo para distribución científica.")

if __name__ == "__main__":
    ejecutar_produccion_total()
