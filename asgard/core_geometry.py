#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NÚCLEO DE GEOMETRÍA Y MALLA TRIDIMENSIONAL - ASGARD V24
======================================================
Maneja la distribución espacial de los nodos, las matrices de adyacencia
del grafo euclidiano, el Laplaciano de la red y el tensor métrico 4D.

Autor: Yenderson Guevara
Versión: 24.0.0 (Official Release)
"""

import numpy as np
from scipy.sparse import csr_matrix

class GeometriaAsgard:
    """
    Gestiona el tejido discreto del espacio-tiempo.
    Representa los puntos del espacio mediante una red de nodos interconectados.
    """
    
    def __init__(self, config):
        """
        Inicializa la topología tridimensional y los tensores de fondo.
        
        Args:
            config: Instancia de ConfigAsgardV24 con los límites físicos
        """
        self.config = config
        self.N = config.N
        self.R = config.R
        
        # 1. GENERACIÓN DE POSICIONES ESPACIALES (X, Y, Z)
        # Distribución de nodos en una esfera de radio R de forma uniforme
        print(f"📐 Generando topología de red espacial para N={self.N} nodos...")
        phi = np.arccos(1.0 - 2.0 * np.random.uniform(0, 1, self.N))
        theta = np.random.uniform(0, 2.0 * np.pi, self.N)
        r = self.R * (np.random.uniform(0, 1, self.N) ** (1.0 / 3.0))
        
        # Conversión a coordenadas cartesianas euclidianas
        self.pos = np.zeros((self.N, 3))
        self.pos[:, 0] = r * np.sin(phi) * np.cos(theta) # Eje X
        self.pos[:, 1] = r * np.sin(phi) * np.sin(theta) # Eje Y
        self.pos[:, 2] = r * np.cos(phi)                 # Eje Z
        
        # 2. INICIALIZACIÓN DEL TENSOR MÉTRICO 4D (g_munu)
        # Inicialmente plano (Métrica de Minkowski: Minkowski = diag(-1, 1, 1, 1))
        self.metrica = np.zeros((self.N, 4, 4))
        for i in range(self.N):
            self.metrica[i, 0, 0] = -1.0 # Componente temporal g_tt
            self.metrica[i, 1, 1] = 1.0  # Componente espacial g_xx
            self.metrica[i, 2, 2] = 1.0  # Componente espacial g_yy
            self.metrica[i, 3, 3] = 1.0  # Componente espacial g_zz
            
        # 3. CONSTRUCCIÓN DE LA INFRAESTRUCTURA DEL GRAFO (CONEXIONES VECINAS)
        self.grados = np.zeros(self.N)
        self.lap = None
        self._construir_grafo()

    def _construir_grafo(self, k_vecinos: int = 6):
        """
        Construye la matriz de adyacencia y el Laplaciano disperso 
        conectando cada nodo con sus 'k' vecinos más cercanos.
        """
        from scipy.spatial import cKDTree
        tree = cKDTree(self.pos)
        
        # Buscar los vecinos más cercanos para cada punto de la malla
        distancias, indices = tree.query(self.pos, k=k_vecinos + 1)
        
        # Estructurar las matrices dispersas para optimización en memoria y GPU
        filas = []
        columnas = []
        datos = []
        
        for i in range(self.N):
            # El índice 0 es el propio nodo, lo ignoramos para las conexiones vecinas
            for j in range(1, k_vecinos + 1):
                idx_vecino = indices[i, j]
                dist = distancias[i, j] + 1e-6
                
                filas.append(i)
                columnas.append(idx_vecino)
                datos.append(1.0 / dist) # Peso inversamente proporcional a la distancia
                self.grados[i] += 1
                
        # Construir Matriz de Adyacencia en formato CSR (Compressed Sparse Row)
        W = csr_matrix((datos, (filas, columnas)), shape=(self.N, self.N))
        
        # Crear el Laplaciano estándar del grafo: L = D - W
        # Donde D es la matriz diagonal de los grados condensados
        D_data = np.array(W.sum(axis=1)).flatten()
        D = csr_matrix((D_data, (range(self.N), range(self.N))), shape=(self.N, self.N))
        self.lap = D - W

    def aplicar_amr_malla(self, indicador_curvatura: np.ndarray):
        """
        Refinamiento Adaptativo de Malla (AMR) elemental.
        Desplaza ligeramente los nodos hacia las zonas donde la curvatura es extrema
        para aumentar la resolución espacial alrededor del agujero negro.
        """
        if not self.config.activar_amr:
            return
            
        # Normalizar el indicador para evitar distorsiones inestables en el grafo
        max_val = np.max(np.abs(indicator_curvatura)) + 1e-8
        peso_refinamiento = np.abs(indicator_curvatura) / max_val
        
        # Desplazamiento radial controlado hacia las zonas críticas de gravedad
        for dim in range(3):
            centro_atraccion = np.mean(self.pos[:, dim])
            direccion = centro_atraccion - self.pos[:, dim]
            # Mover un máximo de 0.5% de la distancia por paso en zonas de alta curvatura
            self.pos[:, dim] += 0.005 * direccion * peso_refinamiento
            
        # Reconstruir el mapa de adyacencia con las nuevas posiciones espaciales
        self._construir_grafo()
