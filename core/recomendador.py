import json

def _abrir_json(ruta: str):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos:
        valor = datos[clave]
        if isinstance(valor, dict):
            return valor
    return datos

def cargar_carreras(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "carreras")
    return datos if isinstance(datos, dict) else {}

def _buscar_clave_similar(diccionario: dict, clave: str):
    if clave in diccionario:
        return clave
    clave_norm = _normalizar_texto(clave)
    for k in diccionario:
        if _normalizar_texto(k) == clave_norm:
            return k
    return None

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

def recomendar(area: str, data: dict, max_por_uni: int = 12) -> dict:
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
