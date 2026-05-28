
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

#_______________________________________________________________________________________________________

# Abre un archivo en formato JSON desde una ruta específica

def _abrir_json(ruta: str):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

#_______________________________________________________________________________________________________

# Inspecciona si un diccionario contiene una clave específica cuyo valor es otro diccionario, 
# "desenvolviendo" este subdiccionario interno si existe o retornando la estructura original de lo 
# contrario.

def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos:
        valor = datos[clave]
        if isinstance(valor, dict):
            return valor
    return datos

#_______________________________________________________________________________________________________

# Carga el catálogo de carreras desde un archivo JSON, extrae el diccionario interno correspondiente si 
# la estructura viene envuelta bajo la clave "carreras" y valida que el resultado final sea un diccionario.

def cargar_carreras(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "carreras")
    return datos if isinstance(datos, dict) else {}

#_______________________________________________________________________________________________________

# Busca una clave dentro de un diccionario, validando primero una coincidencia exacta y, en su defecto, 
# comparando las claves mediante sus versiones normalizadas de texto hasta encontrar una equivalencia.

def _buscar_clave_similar(diccionario: dict, clave: str):
    if clave in diccionario:
        return clave
    clave_norm = _normalizar_texto(clave)
    for k in diccionario:
        if _normalizar_texto(k) == clave_norm:
            return k
    return None

#_______________________________________________________________________________________________________

# Estandariza una cadena de texto eliminando acentos, caracteres diacríticos, signos de puntuación y 
# espaciados redundantes, transformándola completamente a minúsculas para facilitar comparaciones precisas.

def _normalizar_texto(texto: str) -> str:
    import unicodedata, re
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

#_______________________________________________________________________________________________________

# Busca las carreras universitarias asociadas a un área vocacional específica dentro del conjunto de 
# datos y agrupa los resultados por institución, limitando la cantidad de opciones por universidad 
# para optimizar la visualización en la interfaz

def recomendar(area: str, data: dict, max_por_uni: int = 4) -> dict:
    """
    Devuelve un diccionario con carreras sugeridas por universidad.
    Limita la cantidad de carreras por universidad para no saturar la interfaz.
    """
    if not area or not data:
        return {}

    clave_real = _buscar_clave_similar(data, area)
    if not clave_real:
        return {}

    resultado = {}
    for uni, lista in data.get(clave_real, {}).items():
        if isinstance(lista, list):
            resultado[uni] = lista[:max_por_uni]
        else:
            resultado[uni] = []
    return resultado