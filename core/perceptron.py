
# ==========================================================================================
#                                 *** Inteligencia Artificial ***
#                            *** Proyecto Final de Inteligencia Artificial***
# 
#                                                Alumnos:
#                                    ° Cisneros Rojas Héctor Manuel
#                                    ° García Perea Pablo Emilio
#                                    ° Hernandez Andrade Miguel Angel
#                                    ° Navarro Rodriguez Angel Efren
#                                    ° Toledo Duran Jesus Rodrigo

# ==========================================================================================

# ------------------------------------------------------------------------------------------
#                                   MODULO: PERCEPTRON
# ------------------------------------------------------------------------------------------
# Clasificador simple basado en palabras clave para asignar un área vocacional.
# ------------------------------------------------------------------------------------------

import json
import math

def cargar_areas(ruta):
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluar(respuestas, areas):
    """
    Evalúa las respuestas del usuario y devuelve el área más probable.
    - respuestas: dict {area: texto}
    - areas: dict {area: {palabras_clave: peso, ...}}
    Retorna (area_principal, puntajes, probabilidades, confianza, emoji_conf)
    """
    puntajes = {area: 0.0 for area in areas.keys()}
    
    for area, texto in respuestas.items():
        texto_lower = texto.lower()
        for palabra, peso in areas[area].items():
            if palabra in texto_lower:
                puntajes[area] += peso

    # Normalizar a probabilidades
    total = sum(puntajes.values())
    if total == 0:
        total = 1
    probabilidades = {a: p/total for a, p in puntajes.items()}
    area_principal = max(probabilidades, key=probabilidades.get)
    confianza = probabilidades[area_principal] * 100
    # emoji_conf se omite
    return area_principal, puntajes, probabilidades, round(confianza, 1), ""

def descripcion_area(area):
    """Retorna una breve descripción del área vocacional."""
    descripciones = {
        "ingenieria": "Resolución de problemas técnicos, matemáticas y ciencias aplicadas.",
        "salud": "Cuidado de la salud, biología y química.",
        "administracion": "Gestión de empresas, finanzas y mercadotecnia.",
        "humanidades": "Estudio de la cultura, filosofía y lenguas.",
        "arte": "Expresión creativa, diseño y artes visuales.",
        "ciencias_sociales": "Estudio de la sociedad, psicología y educación."
    }
    return descripciones.get(area, "Área no definida.")