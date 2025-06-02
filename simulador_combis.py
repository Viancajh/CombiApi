import math
from datetime import datetime

class SimuladorCombis:
    def __init__(self):
        # Definir las rutas con sus coordenadas
        self.rutas = {
            "hidalgo_chamizal": {
                "nombre": "Col. Hidalgo - Chamizal",
                "coordenadas": [
                    [18.0021, -94.5552],  # Col. Hidalgo
                    [18.0099, -94.5513],  # Centro
                    [18.0156, -94.5489],  # Chamizal
                ]
            },
            "diaz_ordaz": {
                "nombre": "Ruta Díaz Ordaz",
                "coordenadas": [
                    [18.0078, -94.5623],  # Díaz Ordaz
                    [18.0099, -94.5513],  # Centro
                    [18.0134, -94.5467],  # Terminal
                ]
            },
            "insurgentes_patria": {
                "nombre": "Ruta Insurgentes - Patria Libre",
                "coordenadas": [
                    [17.9945, -94.5534],  # Insurgentes
                    [18.0099, -94.5513],  # Centro
                    [18.0167, -94.5456],  # Patria Libre
                ]
            },
            "naranjito_colosio": {
                "nombre": "Ruta Naranjito Colosio",
                "coordenadas": [
                    [17.9989, -94.5678],  # Naranjito
                    [18.0099, -94.5513],  # Centro
                    [18.0189, -94.5489],  # Colosio
                ]
            }
        }
        
        # Inicializar combis en las rutas
        self.combis = [
            {"id": "1", "ruta": "hidalgo_chamizal", "progreso": 0, "direccion": 1, "velocidad": 0.1},
            {"id": "2", "ruta": "diaz_ordaz", "progreso": 0.5, "direccion": 1, "velocidad": 0.08},
            {"id": "3", "ruta": "insurgentes_patria", "progreso": 0.3, "direccion": -1, "velocidad": 0.12},
            {"id": "4", "ruta": "naranjito_colosio", "progreso": 0.7, "direccion": -1, "velocidad": 0.09}
        ]

    def interpolar_posicion(self, coord1, coord2, progreso):
        """Interpola entre dos puntos según el progreso (0-1)"""
        return [
            coord1[0] + (coord2[0] - coord1[0]) * progreso,
            coord1[1] + (coord2[1] - coord1[1]) * progreso
        ]

    def actualizar_posiciones(self):
        """Actualiza las posiciones de todas las combis"""
        for combi in self.combis:
            ruta = self.rutas[combi["ruta"]]
            coords = ruta["coordenadas"]
            
            # Actualizar progreso
            combi["progreso"] += combi["velocidad"] * combi["direccion"]
            
            # Cambiar dirección si llega a los extremos
            if combi["progreso"] >= len(coords) - 1:
                combi["progreso"] = len(coords) - 1
                combi["direccion"] = -1
            elif combi["progreso"] <= 0:
                combi["progreso"] = 0
                combi["direccion"] = 1
            
            # Calcular posición actual
            segmento = int(combi["progreso"])
            progreso_segmento = combi["progreso"] - segmento
            
            if segmento < len(coords) - 1:
                pos = self.interpolar_posicion(
                    coords[segmento],
                    coords[segmento + 1],
                    progreso_segmento
                )
            else:
                pos = coords[segmento]
            
            combi["lat"] = pos[0]
            combi["lng"] = pos[1]
            combi["estado"] = "En servicio"
            combi["ultimaActualizacion"] = datetime.now().isoformat()
            combi["nombre_ruta"] = ruta["nombre"]

    def obtener_estado_combis(self):
        """Retorna el estado actual de todas las combis"""
        self.actualizar_posiciones()
        return self.combis 