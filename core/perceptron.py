#                                     *** Inteligencia Artificial ***
#                              *** Proyecto Final. Asistente vocacional***
#                                            *** Vocabot ***
#
#                                                Alumnos:
#
#                                    ° Cisneros Rojas Hector Manuel
#                                    ° Garcia Perea Pablo Emilio
#                                    ° Hernández Andrade Miguel Angel
#                                    ° Navarro Rodriguez Angel Efren
#                                    ° Toledo Duran Jesús Rodrigo

#=======================================================================================================

import json
import math
from typing import Dict, List


INPUT_ORDER = ("matematicas", "salud", "humanidades", "arte")


#_______________________________________________________________________________________________________
# Abre un archivo JSON y devuelve su contenido.
def _abrir_json(ruta: str):
    """
    Abre un archivo JSON y devuelve su contenido.
    Si el archivo no existe o el JSON está corrupto, retorna un diccionario vacío.
    """
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


#_______________________________________________________________________________________________________
# Si los datos contienen una clave que envuelve un diccionario interno, lo extrae.
def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos:
        valor = datos[clave]
        if isinstance(valor, dict):
            return valor
    return datos


#_______________________________________________________________________________________________________
# Carga el archivo de áreas y normaliza su estructura.
def cargar_areas(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "areas")
    return datos if isinstance(datos, dict) else {}


#_______________________________________________________________________________________________________
# Función sigmoide con clamp para evitar desbordamiento.
def _sigmoid(x: float) -> float:
    x = max(-30.0, min(30.0, float(x)))
    return 1.0 / (1.0 + math.exp(-x))


#_______________________________________________________________________________________________________
# Normaliza las entradas (valores 0-5) a un vector de 0 a 1.
def _normalizar_entradas(entradas: Dict[str, float]) -> List[float]:
    vector = []
    for clave in INPUT_ORDER:
        valor = float((entradas or {}).get(clave, 0.0))
        valor = max(0.0, min(5.0, valor))
        vector.append(valor / 5.0)
    return vector


#_______________________________________________________________________________________________________
# Capa densa de una red neuronal: multiplica, suma, aplica sigmoide y conexión residual.
def _capa_densa(vector: List[float], pesos: List[List[float]], bias: List[float], residual: float = 0.0) -> List[float]:
    salida = []
    for i, fila in enumerate(pesos):
        suma = bias[i]
        for x, w in zip(vector, fila):
            suma += x * w
        activacion = _sigmoid(suma)
        if residual:
            activacion = (1.0 - residual) * activacion + residual * vector[i]
        salida.append(max(0.0, min(1.0, activacion)))
    return salida


#_______________________________________________________________________________________________________
# 7 capas en total:
# 1 de entrada + 5 ocultas + 1 de salida
# Se usan pesos fijos para conservar el enfoque sin entrenamiento.
_CAPAS_OCULTAS = [
    (
        [
            [1.25, 0.10, 0.05, 0.10],
            [0.08, 1.20, 0.12, 0.06],
            [0.10, 0.10, 1.18, 0.08],
            [0.12, 0.06, 0.10, 1.22],
        ],
        [0.05, 0.03, 0.02, 0.04],
        0.96,
    ),
    (
        [
            [1.10, 0.12, 0.06, 0.08],
            [0.08, 1.08, 0.08, 0.05],
            [0.07, 0.07, 1.10, 0.10],
            [0.10, 0.05, 0.08, 1.12],
        ],
        [0.04, 0.02, 0.03, 0.03],
        0.95,
    ),
    (
        [
            [1.08, 0.08, 0.05, 0.05],
            [0.05, 1.05, 0.10, 0.04],
            [0.06, 0.10, 1.08, 0.08],
            [0.08, 0.05, 0.08, 1.10],
        ],
        [0.03, 0.02, 0.02, 0.03],
        0.94,
    ),
    (
        [
            [1.04, 0.08, 0.04, 0.06],
            [0.06, 1.03, 0.06, 0.04],
            [0.05, 0.07, 1.04, 0.07],
            [0.07, 0.04, 0.07, 1.05],
        ],
        [0.02, 0.02, 0.02, 0.02],
        0.93,
    ),
    (
        [
            [1.02, 0.06, 0.04, 0.05],
            [0.05, 1.02, 0.05, 0.04],
            [0.05, 0.05, 1.02, 0.06],
            [0.06, 0.04, 0.06, 1.03],
        ],
        [0.01, 0.01, 0.01, 0.01],
        0.92,
    ),
]


#_______________________________________________________________________________________________________
# Propaga la entrada a través de las capas ocultas.
def _paso_forward(vector: List[float]) -> List[float]:
    salida = vector
    for pesos, bias, residual in _CAPAS_OCULTAS:
        salida = _capa_densa(salida, pesos, bias, residual=residual)
    return salida


#_______________________________________________________________________________________________________
# Red neuronal multicapa manual.
# Mantiene 7 capas en total y preserva mejor la señal original
# para que los gustos dominantes no se diluyan demasiado.
def evaluar(entradas: Dict[str, float], areas: Dict[str, Dict[str, float]]):
    vector_entrada = _normalizar_entradas(entradas)
    representacion_oculta = _paso_forward(vector_entrada)

    # Mezcla conservadora: se respeta sobre todo la entrada original.
    representacion_final = [
        (0.88 * v_in) + (0.12 * v_out)
        for v_in, v_out in zip(vector_entrada, representacion_oculta)
    ]

    caracteristicas = {
        clave: representacion_final[i] * 5.0
        for i, clave in enumerate(INPUT_ORDER)
    }

    resultados = {}
    for area, pesos in areas.items():
        score_suavizado = 0.0
        score_directo = 0.0

        for clave in INPUT_ORDER:
            peso_area = float(pesos.get(clave, 0.0))
            valor_caracteristica = caracteristicas.get(clave, 0.0)
            valor_directo = float((entradas or {}).get(clave, 0.0))

            score_suavizado += valor_caracteristica * peso_area
            score_directo += valor_directo * peso_area

        resultados[area] = (0.82 * score_suavizado) + (0.18 * score_directo)

    total = sum(resultados.values())
    if total <= 0:
        n = len(resultados) or 1
        prob = {k: 1 / n for k in resultados} if resultados else {}
    else:
        prob = {k: v / total for k, v in resultados.items()}

    mejor = max(prob, key=prob.get) if prob else None
    return mejor, resultados, prob


#_______________________________________________________________________________________________________
# Explica qué características contribuyeron más a la recomendación.
def explicar_recomendacion(
    entradas: Dict[str, float],
    areas: Dict[str, Dict[str, float]],
    area: str,
    top_n: int = 2
) -> List[str]:

    if not area or area not in areas:
        return []

    pesos = areas.get(area, {})
    contribuciones = []

    for clave in INPUT_ORDER:
        peso = float(pesos.get(clave, 0.0))
        valor = float((entradas or {}).get(clave, 0.0))
        contribuciones.append((clave, valor * peso))

    contribuciones.sort(key=lambda x: x[1], reverse=True)
    relevantes = [k for k, v in contribuciones if v > 0][:top_n]
    return relevantes


#_______________________________________________________________________________________________________
# Devuelve los nombres de las capas de la red neuronal para depuración.
def descripcion_arquitectura() -> List[str]:
    return [
        "Capa de entrada",
        "Capa oculta 1",
        "Capa oculta 2",
        "Capa oculta 3",
        "Capa oculta 4",
        "Capa oculta 5",
        "Capa de salida",
    ]