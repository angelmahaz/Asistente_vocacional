
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


# --------------------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------------------

def cargar_areas(ruta):
    """Carga el diccionario de areas con sus palabras clave y pesos desde areas.json."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


# --------------------------------------------------------------------------
# FUNCIONES DE ACTIVACION
# --------------------------------------------------------------------------

def _sigmoide(x):
    """
    Funcion sigmoide: transforma cualquier valor real en el rango (0, 1).
    Introduce no-linealidad entre la capa de pesos y la de salida.
    """
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _softmax(vector):
    """
    Funcion Softmax: convierte un vector de valores reales en una distribucion
    de probabilidad (todos los valores entre 0 y 1, sumando exactamente 1).
    Usada en la capa de salida para obtener probabilidades comparables.
    """
    max_v = max(vector.values()) if vector else 0
    exp_vals = {k: math.exp(v - max_v) for k, v in vector.items()}
    total = sum(exp_vals.values()) or 1
    return {k: v / total for k, v in exp_vals.items()}


def _minmax(vector):
    """
    Normalizacion Min-Max: escala los valores al rango [0, 1].
    Capa 2 de la red. Evita que areas con muchas palabras clave dominen por volumen.
    """
    if not vector:
        return {}
    min_v = min(vector.values())
    max_v = max(vector.values())
    rango = max_v - min_v
    if rango == 0:
        return {k: 0.5 for k in vector}
    return {k: (v - min_v) / rango for k, v in vector.items()}


# --------------------------------------------------------------------------
# RED NEURONAL DE 5 CAPAS
# --------------------------------------------------------------------------

def evaluar(puntuaciones_brutas, areas_data):
    """
    Ejecuta las 5 capas del perceptron y retorna el area recomendada.

    Parametros:
        puntuaciones_brutas: dict {area: puntaje_bruto}
            Puntaje bruto = suma de (coincidencias * peso) de cada keyword detectada.
            Viene del modulo vocabot.detectar_intereses acumulado en la sesion.
        areas_data: dict cargado de areas.json

    Retorna:
        area_principal   (str)   Area con mayor probabilidad
        puntajes_capa3   (dict)  Salida de la capa de pesos (antes de activacion)
        probabilidades   (dict)  Salida softmax, valores entre 0 y 1
        confianza        (float) Porcentaje de confianza (0-100)
        nivel_confianza  (str)   "Alta", "Media" o "Baja"
    """

    areas = list(areas_data.keys())

    # ------------------------------------------------------------------
    # CAPA 1 — ENTRADA
    # Asegura que todas las areas esten representadas, incluso con 0.
    # ------------------------------------------------------------------
    capa1 = {area: float(puntuaciones_brutas.get(area, 0.0)) for area in areas}

    # ------------------------------------------------------------------
    # CAPA 2 — NORMALIZACION (Min-Max)
    # Escala los puntajes brutos al rango [0, 1].
    # ------------------------------------------------------------------
    capa2 = _minmax(capa1)

    # ------------------------------------------------------------------
    # CAPA 3 — PESOS
    # Multiplica cada valor normalizado por el numero total de palabras
    # clave del area (proxy del "peso sinAptico" del area).
    # Areas con vocabulario mas rico y especifico reciben mayor peso.
    # ------------------------------------------------------------------
    capa3 = {}
    for area in areas:
        num_keywords = len(areas_data.get(area, {}))
        factor_keywords = math.log(num_keywords + 1)  # log para suavizar diferencias
        capa3[area] = capa2.get(area, 0.0) * factor_keywords

    # ------------------------------------------------------------------
    # CAPA 4 — ACTIVACION (Sigmoide)
    # Introduce no-linealidad: penaliza puntajes muy bajos y refuerza
    # los medios-altos. Bias de -0.5 para centrar la sigmoide.
    # ------------------------------------------------------------------
    capa4 = {}
    for area in areas:
        x = capa3[area] - 0.5
        capa4[area] = _sigmoide(x)

    # ------------------------------------------------------------------
    # CAPA 5 — SALIDA (Softmax)
    # Convierte las activaciones en probabilidades comparables que suman 1.
    # El area con mayor probabilidad es la recomendada.
    # ------------------------------------------------------------------
    probabilidades = _softmax(capa4)

    # Seleccionar area principal
    area_principal = max(probabilidades, key=probabilidades.get)

    # Calcular nivel de confianza segun el gap entre 1er y 2do lugar
    probs_ordenadas = sorted(probabilidades.values(), reverse=True)
    gap = probs_ordenadas[0] - probs_ordenadas[1] if len(probs_ordenadas) > 1 else probs_ordenadas[0]

    confianza = round(probabilidades[area_principal] * 100, 1)

    if gap >= 0.25:
        nivel_confianza = "Alta"
    elif gap >= 0.10:
        nivel_confianza = "Media"
    else:
        nivel_confianza = "Baja"

    return area_principal, capa3, probabilidades, confianza, nivel_confianza


# --------------------------------------------------------------------------
# DESCRIPCION DE AREA
# --------------------------------------------------------------------------

DESCRIPCIONES = {
    "Ciencias Fisico-Matematicas y de las Ingenierias": (
        "Abarca matematicas, fisica, computacion, ingenieria y tecnologia. "
        "Ideal para quienes disfrutan resolver problemas, programar, disenar sistemas "
        "o construir soluciones tecnicas."
    ),
    "Ciencias Biologicas Quimicas y de la Salud": (
        "Comprende medicina, biologia, quimica, farmacia, nutricion y ciencias ambientales. "
        "Va bien con quienes se interesan por la vida, la salud y el cuidado del ser humano y la naturaleza."
    ),
    "Ciencias Sociales": (
        "Incluye derecho, economia, administracion, comunicacion, psicologia y sociologia. "
        "Adecuada para quienes quieren entender y transformar la sociedad, las organizaciones y las personas."
    ),
    "Humanidades y de las Artes": (
        "Engloba filosofia, historia, letras, linguistica, musica, artes visuales, teatro y diseno. "
        "Pensada para mentes creativas, criticas y con sensibilidad cultural."
    )
}

def descripcion_area(area):
    """Retorna la descripcion completa del area vocacional."""
    return DESCRIPCIONES.get(area, "Area con amplias posibilidades de desarrollo profesional.")
