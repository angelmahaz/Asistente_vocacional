import json
import math
import unicodedata
from typing import Dict, List, Tuple


INPUT_ORDER = ("matematicas", "salud", "humanidades", "arte")

AREAS_CANONICAS = {
    "Área 1: Ciencias Físico-Matemáticas y de las Ingenierías": {
        "matematicas": 2.4,
        "salud": 0.15,
        "humanidades": 0.05,
        "arte": 0.05,
    },
    "Área 2: Ciencias Biológicas, Químicas y de la Salud": {
        "matematicas": 0.35,
        "salud": 2.35,
        "humanidades": 0.45,
        "arte": 0.05,
    },
    "Área 3: Ciencias Sociales": {
        "matematicas": 0.15,
        "salud": 0.45,
        "humanidades": 2.25,
        "arte": 0.35,
    },
    "Área 4: Humanidades y de las Artes": {
        "matematicas": 0.05,
        "salud": 0.10,
        "humanidades": 1.05,
        "arte": 2.45,
    },
}


def _abrir_json(ruta: str):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos:
        valor = datos[clave]
        if isinstance(valor, dict):
            return valor
    return datos


def _normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    return " ".join(texto.lower().split())


def _normalizar_areas(areas: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Fuerza las cuatro áreas vocacionales solicitadas y conserva pesos del JSON
    cuando sus nombres coinciden, incluso si vienen sin acentos.
    """
    if not isinstance(areas, dict):
        return dict(AREAS_CANONICAS)

    por_nombre = {_normalizar_texto(nombre): pesos for nombre, pesos in areas.items()}
    normalizadas = {}

    for nombre_canonico, pesos_default in AREAS_CANONICAS.items():
        pesos_json = por_nombre.get(_normalizar_texto(nombre_canonico), {})
        pesos = {}
        for clave in INPUT_ORDER:
            pesos[clave] = float(pesos_json.get(clave, pesos_default[clave]))
        normalizadas[nombre_canonico] = pesos

    return normalizadas


def cargar_areas(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "areas")
    return _normalizar_areas(datos)


def _sigmoid(x: float) -> float:
    x = max(-30.0, min(30.0, float(x)))
    return 1.0 / (1.0 + math.exp(-x))


def _softmax(resultados: Dict[str, float], temperatura: float = 2.6) -> Dict[str, float]:
    if not resultados:
        return {}

    escala = max(0.05, float(temperatura))
    maximo = max(resultados.values())
    exp_values = {
        area: math.exp((puntaje - maximo) / escala)
        for area, puntaje in resultados.items()
    }
    total = sum(exp_values.values())

    if total <= 0:
        n = len(resultados) or 1
        return {k: 1 / n for k in resultados}

    return {k: v / total for k, v in exp_values.items()}


def _normalizar_entradas(entradas: Dict[str, float]) -> List[float]:
    vector = []
    for clave in INPUT_ORDER:
        valor = float((entradas or {}).get(clave, 0.0))
        valor = max(0.0, min(5.0, valor))
        vector.append(valor / 5.0)
    return vector


def _capa_densa(
    vector: List[float],
    pesos: List[List[float]],
    bias: List[float],
    residual: float = 0.0,
) -> List[float]:
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


# 11 capas en total:
# 1 de entrada + 9 ocultas + 1 de salida.
# Los pesos son fijos porque este proyecto no entrena con un dataset externo.
_CAPAS_OCULTAS = [
    (
        [
            [1.35, 0.08, 0.04, 0.06],
            [0.10, 1.30, 0.12, 0.04],
            [0.05, 0.12, 1.28, 0.08],
            [0.06, 0.04, 0.10, 1.34],
        ],
        [0.04, 0.03, 0.03, 0.04],
        0.82,
    ),
    (
        [
            [1.24, 0.10, 0.04, 0.05],
            [0.08, 1.22, 0.10, 0.04],
            [0.05, 0.10, 1.20, 0.08],
            [0.06, 0.04, 0.09, 1.23],
        ],
        [0.03, 0.03, 0.02, 0.03],
        0.84,
    ),
    (
        [
            [1.18, 0.06, 0.06, 0.05],
            [0.06, 1.17, 0.11, 0.04],
            [0.04, 0.10, 1.18, 0.09],
            [0.05, 0.04, 0.10, 1.18],
        ],
        [0.025, 0.025, 0.025, 0.025],
        0.86,
    ),
    (
        [
            [1.14, 0.07, 0.04, 0.04],
            [0.05, 1.13, 0.09, 0.03],
            [0.04, 0.08, 1.14, 0.08],
            [0.04, 0.03, 0.09, 1.15],
        ],
        [0.02, 0.02, 0.02, 0.02],
        0.88,
    ),
    (
        [
            [1.10, 0.05, 0.04, 0.04],
            [0.04, 1.10, 0.08, 0.03],
            [0.03, 0.07, 1.11, 0.07],
            [0.04, 0.03, 0.08, 1.11],
        ],
        [0.015, 0.015, 0.015, 0.015],
        0.90,
    ),
    (
        [
            [1.08, 0.05, 0.03, 0.03],
            [0.04, 1.07, 0.07, 0.03],
            [0.03, 0.07, 1.08, 0.06],
            [0.03, 0.03, 0.07, 1.09],
        ],
        [0.012, 0.012, 0.012, 0.012],
        0.91,
    ),
    (
        [
            [1.06, 0.04, 0.03, 0.03],
            [0.03, 1.06, 0.06, 0.02],
            [0.03, 0.06, 1.06, 0.05],
            [0.03, 0.02, 0.06, 1.07],
        ],
        [0.01, 0.01, 0.01, 0.01],
        0.92,
    ),
    (
        [
            [1.04, 0.04, 0.02, 0.02],
            [0.03, 1.04, 0.05, 0.02],
            [0.02, 0.05, 1.04, 0.05],
            [0.02, 0.02, 0.05, 1.05],
        ],
        [0.008, 0.008, 0.008, 0.008],
        0.93,
    ),
    (
        [
            [1.03, 0.03, 0.02, 0.02],
            [0.02, 1.03, 0.04, 0.02],
            [0.02, 0.04, 1.03, 0.04],
            [0.02, 0.02, 0.04, 1.04],
        ],
        [0.006, 0.006, 0.006, 0.006],
        0.94,
    ),
]


def _paso_forward(vector: List[float]) -> List[float]:
    salida = vector
    for pesos, bias, residual in _CAPAS_OCULTAS:
        salida = _capa_densa(salida, pesos, bias, residual=residual)
    return salida


def _bono_por_dominancia(entrada: float, promedio_otros: float) -> float:
    diferencia = max(0.0, entrada - promedio_otros)
    return diferencia * 0.35


def evaluar(entradas: Dict[str, float], areas: Dict[str, Dict[str, float]]):
    """
    Red neuronal multicapa manual:
    - Capa de entrada: 4 variables vocacionales.
    - 9 capas ocultas con pesos fijos y conexiones residuales.
    - Capa de salida: calcula puntaje por las cuatro áreas vocacionales.

    Devuelve:
    - mejor_area
    - resultados (puntajes)
    - probabilidad relativa por área
    """
    areas_normalizadas = _normalizar_areas(areas)
    vector_entrada = _normalizar_entradas(entradas)
    representacion_oculta = _paso_forward(vector_entrada)

    # Mezcla conservadora: las capas refinan, pero no borran el gusto declarado.
    representacion_final = [
        (0.78 * v_in) + (0.22 * v_out)
        for v_in, v_out in zip(vector_entrada, representacion_oculta)
    ]

    caracteristicas = {
        clave: representacion_final[i] * 5.0
        for i, clave in enumerate(INPUT_ORDER)
    }
    entradas_directas = {
        clave: max(0.0, min(5.0, float((entradas or {}).get(clave, 0.0))))
        for clave in INPUT_ORDER
    }

    resultados = {}
    for area, pesos in areas_normalizadas.items():
        score_neuronal = 0.0
        score_directo = 0.0

        for clave in INPUT_ORDER:
            peso_area = float(pesos.get(clave, 0.0))
            score_neuronal += caracteristicas.get(clave, 0.0) * peso_area
            score_directo += entradas_directas.get(clave, 0.0) * peso_area

        dominante = max(pesos, key=pesos.get)
        otros = [v for k, v in entradas_directas.items() if k != dominante]
        promedio_otros = sum(otros) / len(otros) if otros else 0.0
        bono = _bono_por_dominancia(entradas_directas[dominante], promedio_otros)

        resultados[area] = (0.72 * score_neuronal) + (0.28 * score_directo) + bono

    prob = _softmax(resultados)
    mejor = max(prob, key=prob.get) if prob else None
    return mejor, resultados, prob


def explicar_recomendacion(
    entradas: Dict[str, float],
    areas: Dict[str, Dict[str, float]],
    area: str,
    top_n: int = 2,
) -> List[str]:
    """
    Devuelve las características que más contribuyeron al área recomendada.
    Útil para explicar el resultado al usuario.
    """
    areas_normalizadas = _normalizar_areas(areas)
    if not area or area not in areas_normalizadas:
        return []

    pesos = areas_normalizadas.get(area, {})
    contribuciones: List[Tuple[str, float]] = []

    for clave in INPUT_ORDER:
        peso = float(pesos.get(clave, 0.0))
        valor = float((entradas or {}).get(clave, 0.0))
        contribuciones.append((clave, valor * peso))

    contribuciones.sort(key=lambda x: x[1], reverse=True)
    relevantes = [k for k, v in contribuciones if v > 0][:top_n]
    return relevantes


def descripcion_arquitectura() -> List[str]:
    capas = ["Capa de entrada"]
    capas.extend(f"Capa oculta {i}" for i in range(1, len(_CAPAS_OCULTAS) + 1))
    capas.append("Capa de salida")
    return capas
