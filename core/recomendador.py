
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
#                                   MODULO: RECOMENDADOR
# ------------------------------------------------------------------------------------------
# Recomienda carreras universitarias basadas en el área vocacional.
# ------------------------------------------------------------------------------------------

import json

def cargar_carreras(ruta):
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)   # { "area": { "universidad": ["carrera1", ...] } }

def recomendar(area, carreras_data, n=4):
    """Retorna las primeras n carreras del área especificada, agrupadas por universidad."""
    resultados = {}
    carreras_por_uni = carreras_data.get(area, {})
    for uni, lista in carreras_por_uni.items():
        resultados[uni] = lista[:n]
    return resultados

def recomendar_segunda_opcion(probabilidades, carreras_data, n=3):
    """Encuentra la segunda área más probable y sus carreras."""
    areas_ordenadas = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    if len(areas_ordenadas) < 2:
        return None, {}
    segunda_area = areas_ordenadas[1][0]
    segundas_carreras = recomendar(segunda_area, carreras_data, n)
    return segunda_area, segundas_carreras

def link_universidad(uni):
    """Genera un enlace a la página de la universidad (placeholder)."""
    # Puede mapearse a URLs reales
    return f"https://www.universidades.com/{uni.replace(' ', '_')}"