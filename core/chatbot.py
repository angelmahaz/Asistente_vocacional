
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
import random
import re
import unicodedata
from typing import Dict, List, Optional


AREAS_VALIDAS = {"matematicas", "salud", "humanidades", "arte"}

#_______________________________________________________________________________________________________

# Frases que no representan un nombre y no deben almacenarse como tal
PALABRAS_NO_NOMBRE = {
    "estudiante", "aspirante", "persona", "alumno", "alumna", "usuario",
    "mucho", "gusto", "llamado", "llamada", "conocido", "conocida",
    "nombre", "apodo", "profesor", "maestro", "maestra"
}

#_______________________________________________________________________________________________________

TRIGGERS_NOMBRE = (
    "me llamo",
    "mi nombre es",
    "puedes llamarme",
    "llamame",
    "llámame",
    "soy",
    "yo soy",
    "soy conocido como",
    "se me dice",
    "mi apodo es",
)

#_______________________________________________________________________________________________________

STOPWORDS_POST_NOMBRE = {
    "y", "pero", "porque", "pues", "aunque", "entonces", "además", "tambien",
    "también", "con", "sin", "para", "por", "que", "donde", "cuando", "si",
    "me", "mi", "soy", "llamo"
}

#_______________________________________________________________________________________________________

SALUDOS_SIMPLES = {
    "hola", "buenas", "hey", "hello", "saludos", "alo", "buen", "dia",
    "dias", "tarde", "tardes", "noche", "noches", "que", "tal", "onda"
}

FRASES_DE_APOYO = {
    "hola", "buenas", "hey", "hello", "saludos", "alo", "que tal",
    "que onda", "buen dia", "buenos dias", "buenas tardes", "buenas noches"
}

#_______________________________________________________________________________________________________

def tiene_contenido_relevante(texto: str) -> bool:
    """
    Indica si, después de quitar saludos y muletillas, aún queda contenido útil.
    Se usa para evitar que frases como 'Hola soy Rodrigo' generen una respuesta
    de 'no entendí' después de registrar el nombre.
    """
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return False

    # Si es solo saludo, no lo tratamos como contenido relevante.
    if coincide_frases(texto_norm, list(FRASES_DE_APOYO)):
        tokens = texto_norm.split()
        if len(tokens) <= 3:
            return False

    tokens_filtrados = []
    for tok in texto_norm.split():
        if tok in SALUDOS_SIMPLES:
            continue
        if tok in STOPWORDS_POST_NOMBRE:
            continue
        tokens_filtrados.append(tok)

    return bool(tokens_filtrados)

#_______________________________________________________________________________________________________

def _abrir_json(ruta: str):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

#_______________________________________________________________________________________________________

def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos and isinstance(datos[clave], dict):
        return datos[clave]
    return datos

#_______________________________________________________________________________________________________

def cargar_intenciones(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "intenciones")
    return datos if isinstance(datos, dict) else {}

#_______________________________________________________________________________________________________

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

#_______________________________________________________________________________________________________

def coincide_frases(texto: str, frases: List[str]) -> bool:
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return False

    for frase in frases or []:
        frase_norm = normalizar_texto(frase)
        if frase_norm and frase_norm in texto_norm:
            return True
    return False

#_______________________________________________________________________________________________________

def detectar_intereses(texto: str, intenciones: dict) -> List[str]:
    """
    Devuelve una lista con la intención dominante entre:
    matematicas, salud, humanidades, arte
    """
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return []

    tokens = texto_norm.split()
    conteo = {categoria: 0.0 for categoria in AREAS_VALIDAS}

    for categoria in AREAS_VALIDAS:
        palabras = intenciones.get(categoria, []) or []
        for palabra in palabras:
            palabra_norm = normalizar_texto(palabra)
            if not palabra_norm:
                continue

            # Coincidencia de frase completa
            if " " in palabra_norm:
                if palabra_norm in texto_norm:
                    conteo[categoria] += 2.5 + (len(palabra_norm.split()) * 0.15)
                continue

            # Coincidencia por palabra exacta o por aproximación
            if palabra_norm in tokens:
                conteo[categoria] += 2.0
            else:
                for tok in tokens:
                    if tok.startswith(palabra_norm) or palabra_norm.startswith(tok):
                        conteo[categoria] += 0.85
                        break

    mejor = max(conteo, key=conteo.get)
    if conteo[mejor] <= 0:
        return []
    return [mejor]

#_______________________________________________________________________________________________________

def detectar_recomendacion(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("recomendacion", []))

#_______________________________________________________________________________________________________

def es_despedida(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("despedida", []))

#_______________________________________________________________________________________________________

def es_saludo(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("saludo", []))

#_______________________________________________________________________________________________________

def es_afirmacion(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)
    return texto_norm in {"si", "sí", "claro", "ok", "vale", "va", "correcto", "de acuerdo", "por supuesto"}

#_______________________________________________________________________________________________________

def es_negacion(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)
    return texto_norm in {"no", "nop", "nel", "negativo", "para nada", "nada", "no gracias"}


_RESPUESTAS_BINARIAS_AFIRMATIVAS = {
    "si", "sí", "claro", "ok", "vale", "va", "correcto", "de acuerdo",
    "por supuesto", "sin duda", "me parece bien", "adelante", "perfecto"
}

_RESPUESTAS_BINARIAS_NEGATIVAS = {
    "no", "nop", "nel", "negativo", "para nada", "nada", "no gracias",
    "jamas", "jamás", "nunca"
}

_RESPUESTAS_BINARIAS_INDEFINIDAS = {
    "no se", "no sé", "no estoy seguro", "no estoy segura", "quizas", "quizás",
    "tal vez", "puede ser", "quien sabe", "quién sabe"
}

_RESPUESTAS_ESCALA_5 = {
    "me encanta", "me fascina", "me gusta mucho", "mucho", "bastante",
    "totalmente", "si", "sí", "claro", "por supuesto", "sin duda", "me parece excelente"
}

_RESPUESTAS_ESCALA_4 = {
    "me gusta", "algo", "un poco", "poquito", "regularmente", "regular",
    "medio", "mas o menos", "más o menos", "a medias"
}

_RESPUESTAS_ESCALA_2 = {
    "poco", "muy poco", "casi nada", "no mucho", "poquísimo", "poquisimo"
}

_RESPUESTAS_ESCALA_1 = {
    "nada", "para nada", "no", "nop", "nunca", "jamas", "jamás"
}

#_______________________________________________________________________________________________________

def _contiene_frase_normalizada(texto_norm: str, frase: str) -> bool:
    frase_norm = normalizar_texto(frase)
    if not texto_norm or not frase_norm:
        return False
    return frase_norm in texto_norm

#_______________________________________________________________________________________________________

def _contiene_token(texto_norm: str, token: str) -> bool:
    token_norm = normalizar_texto(token)
    if not texto_norm or not token_norm:
        return False
    return token_norm in texto_norm.split()

#_______________________________________________________________________________________________________

def interpretar_respuesta_binaria(texto: str) -> Optional[bool]:
    """
    Devuelve:
    - True  -> respuesta afirmativa
    - False -> respuesta negativa
    - None  -> no se pudo clasificar
    """
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None

    if any(_contiene_frase_normalizada(texto_norm, frase) for frase in _RESPUESTAS_BINARIAS_INDEFINIDAS):
        return None

    for frase in sorted(_RESPUESTAS_BINARIAS_NEGATIVAS, key=len, reverse=True):
        if " " in normalizar_texto(frase):
            if _contiene_frase_normalizada(texto_norm, frase):
                return False
        else:
            if _contiene_token(texto_norm, frase):
                return False

    for frase in sorted(_RESPUESTAS_BINARIAS_AFIRMATIVAS, key=len, reverse=True):
        if " " in normalizar_texto(frase):
            if _contiene_frase_normalizada(texto_norm, frase):
                return True
        else:
            if _contiene_token(texto_norm, frase):
                return True

    return None

#_______________________________________________________________________________________________________

def interpretar_respuesta_escala(texto: str) -> Optional[int]:
    """
    Interpreta respuestas tipo:
    - mucho / bastante / sí / claro -> 5
    - me gusta / un poco / algo / regular -> 4
    - más o menos / medio -> 3
    - poco / muy poco / casi nada -> 2
    - nada / no / para nada -> 1
    Si no puede determinarse, devuelve None.
    """
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None

    # Si el usuario expresa que no sabe, mejor no forzar clasificación.

    if any(_contiene_frase_normalizada(texto_norm, frase) for frase in _RESPUESTAS_BINARIAS_INDEFINIDAS):
        return None

    escalas = [
        (2, sorted(_RESPUESTAS_ESCALA_2, key=len, reverse=True)),
        (1, sorted(_RESPUESTAS_ESCALA_1, key=len, reverse=True)),
        (3, sorted({"mas o menos", "más o menos", "regular", "neutral", "intermedio", "mitad", "a medias"}, key=len, reverse=True)),
        (5, sorted(_RESPUESTAS_ESCALA_5, key=len, reverse=True)),
        (4, sorted(_RESPUESTAS_ESCALA_4, key=len, reverse=True)),
    ]

    # Primero se buscan frases específicas de menor a mayor para evitar
    # que "no mucho" termine clasificado como "mucho".

    for valor, patrones in escalas:
        for patron in patrones:
            patron_norm = normalizar_texto(patron)
            if " " in patron_norm:
                if _contiene_frase_normalizada(texto_norm, patron_norm):
                    return valor
            else:
                if _contiene_token(texto_norm, patron_norm):
                    return valor

    # Casos intermedios
    if any(_contiene_frase_normalizada(texto_norm, frase) for frase in _RESPUESTAS_ESCALA_4):
        return 4

    return None

#_______________________________________________________________________________________________________

def es_afirmacion(texto: str) -> bool:
    return interpretar_respuesta_binaria(texto) is True

#_______________________________________________________________________________________________________

def es_negacion(texto: str) -> bool:
    return interpretar_respuesta_binaria(texto) is False

#_______________________________________________________________________________________________________

def _limpiar_fragmento_nombre(fragmento: str) -> str:
    fragmento = fragmento.strip(" \t\r\n,.;:!?")
    partes = fragmento.split()
    limpias = []
    for p in partes:
        p_norm = normalizar_texto(p)
        if p_norm in STOPWORDS_POST_NOMBRE:
            break
        limpias.append(p)
    return " ".join(limpias).strip(" \t\r\n,.;:!?")

#_______________________________________________________________________________________________________

def extraer_nombre(texto: str) -> Optional[str]:
    """
    Intenta extraer un nombre si el usuario escribe algo como:
    - "me llamo Rodrigo"
    - "soy Ana"
    - "mi nombre es Carlos"
    """
    if not texto:
        return None

    texto_original = texto.strip()

    # Patrones que capturan el texto posterior al disparador
    for trigger in TRIGGERS_NOMBRE:
        patron = re.compile(
            rf"\b{re.escape(trigger)}\b\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\-]*(?:\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\-]*){{0,2}})",
            re.IGNORECASE,
        )
        match = patron.search(texto_original)
        if not match:
            continue

        candidato = _limpiar_fragmento_nombre(match.group(1))
        if not candidato:
            continue

        # Evitar falsos positivos como "soy estudiante"
        primer_token = normalizar_texto(candidato).split()[0]
        if primer_token in PALABRAS_NO_NOMBRE:
            continue

        return candidato.title()

    return None


#_______________________________________________________________________________________________________


def limpiar_mensaje_nombre(texto: str) -> str:
    """
    Quita del texto el fragmento relacionado con nombre para no interferir con la detección de intereses.
    """
    if not texto:
        return texto

    salida = texto
    for trigger in TRIGGERS_NOMBRE:
        patron = re.compile(
            rf"\b{re.escape(trigger)}\b\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\-\s]*",
            re.IGNORECASE,
        )
        salida = patron.sub(" ", salida)

    salida = re.sub(r"\s+", " ", salida).strip()
    return salida

#_______________________________________________________________________________________________________

def respuesta_humana(tipo: str) -> str:
    respuestas = {
        "matematicas": [
            "Eso suena muy lógico y analítico.",
            "Tienes perfil para resolver problemas complejos.",
            "Veo afinidad con áreas técnicas y de razonamiento.",
        ],
        "salud": [
            "Se nota que te importa ayudar a otros.",
            "Tienes vocación de servicio.",
            "Eso encaja muy bien con profesiones de cuidado y apoyo.",
        ],
        "humanidades": [
            "Eso refleja pensamiento crítico.",
            "Te interesa entender la sociedad.",
            "Veo interés por la comunicación y el análisis social.",
        ],
        "arte": [
            "Tienes creatividad.",
            "Eso es muy valioso en el arte.",
            "Se nota un perfil creativo y expresivo.",
        ]
    }
    opciones = respuestas.get(tipo, ["Interesante... cuéntame un poco más."])
    return random.choice(opciones)

#_______________________________________________________________________________________________________

def respuesta_general() -> str:
    return random.choice([
        "Cuéntame más.",
        "Interesante...",
        "Sigue, te escucho.",
        "Eso me ayuda a conocerte mejor.",
        "Voy entendiendo tus gustos.",
    ])

#_______________________________________________________________________________________________________

def respuesta_no_entendida() -> str:
    return random.choice([
        "No estoy seguro de entender. ¿Puedes explicarlo de otra forma?",
        "Tal vez hubo un pequeño error al escribir. ¿Puedes repetirlo?",
        "No lo capté del todo, pero sigo contigo. ¿Me lo cuentas diferente?",
        "No entendí esa parte. ¿Puedes decirlo con otras palabras?",
    ])

#_______________________________________________________________________________________________________

def cargar_preguntas(ruta: str) -> list:
    datos = _abrir_json(ruta)
    if isinstance(datos, dict) and "preguntas" in datos and isinstance(datos["preguntas"], list):
        return datos["preguntas"]
    if isinstance(datos, list):
        return datos
    return []

# ---------------------------------------------------------------------------
# Mejora de puntuación por intereses
# ---------------------------------------------------------------------------

_PESOS_ESPECIALES_INTERESES = {
    "matematicas": {
        "computacion": 1.95,
        "informatica": 1.90,
        "programacion": 1.80,
        "programar": 1.75,
        "codigo": 1.65,
        "software": 1.65,
        "sistemas": 1.50,
        "algoritmos": 1.90,
        "algoritmia": 1.85,
        "datos": 1.45,
        "ciencia de datos": 1.85,
        "base de datos": 1.70,
        "redes": 1.55,
        "ciberseguridad": 1.85,
        "robotica": 1.75,
        "hardware": 1.55,
        "inteligencia artificial": 2.10,
        "machine learning": 2.10,
        "desarrollo web": 1.60,
        "apps": 1.35,
        "aplicaciones": 1.35,
        "videojuegos": 1.40,
        "analisis numerico": 1.75,
        "matematicas": 1.90,
        "numeros": 1.55,
        "calculo": 1.70,
        "ecuaciones": 1.70,
        "algebra": 1.65,
        "logica": 1.65,
        "estadistica": 1.55,
        "probabilidad": 1.55,
        "geometria": 1.45,
        "fisica": 1.60,
        "tecnologia": 1.35,
        "ingenieria": 1.45,
    },
    "salud": {
        "medicina": 1.95,
        "doctor": 1.60,
        "hospital": 1.55,
        "enfermeria": 1.80,
        "curar": 1.45,
        "pacientes": 1.40,
        "biologia": 1.55,
        "cuerpo humano": 1.55,
        "cirugia": 1.80,
        "farmacia": 1.70,
        "psicologia": 1.35,
        "rehabilitacion": 1.65,
        "diagnostico": 1.55,
        "tratamiento": 1.55,
        "odontologia": 1.70,
        "nutricion": 1.55,
        "veterinaria": 1.40,
        "anatomia": 1.55,
        "fisiologia": 1.55,
        "quimica": 1.30,
        "quimico": 1.15,
        "quimica medica": 1.75,
        "biomedicina": 1.80,
        "salud publica": 1.60,
        "epidemiologia": 1.60,
        "terapia fisica": 1.70,
        "laboratorio clinico": 1.55,
    },
    "humanidades": {
        "leer": 1.45,
        "historia": 1.60,
        "derecho": 1.70,
        "sociedad": 1.50,
        "politica": 1.55,
        "escribir": 1.50,
        "analizar": 1.35,
        "economia": 1.45,
        "filosofia": 1.70,
        "cultura": 1.45,
        "debate": 1.40,
        "comunicacion": 1.55,
        "relaciones": 1.30,
        "negocios": 1.30,
        "educacion": 1.35,
        "sociologia": 1.55,
        "antropologia": 1.55,
        "literatura": 1.70,
        "linguistica": 1.65,
        "etica": 1.45,
        "ciencia politica": 1.60,
        "administracion": 1.25,
        "mercadotecnia": 1.20,
        "idiomas": 1.40,
        "traduccion": 1.45,
        "bibliotecologia": 1.55,
        "arqueologia": 1.50,
    },
    "arte": {
        "dibujar": 1.70,
        "pintar": 1.70,
        "arte": 1.55,
        "diseno": 1.60,
        "creativo": 1.45,
        "musica": 1.65,
        "fotografia": 1.60,
        "animacion": 1.65,
        "ilustracion": 1.60,
        "video": 1.25,
        "cine": 1.55,
        "expresion": 1.40,
        "teatro": 1.60,
        "danza": 1.60,
        "arquitectura": 1.30,
        "creatividad": 1.55,
        "grafico": 1.50,
        "digital": 1.20,
        "escultura": 1.60,
        "manualidades": 1.45,
        "moda": 1.45,
        "joyeria": 1.40,
        "performance": 1.35,
        "multimedia": 1.45,
        "sonido": 1.35,
        "edicion": 1.30,
        "modelado 3d": 1.50,
        "videojuegos artisticos": 1.50,
        "historieta": 1.50,
        "muralismo": 1.55,
    },
}

#_______________________________________________________________________________________________________

def _peso_especial_interes(area: str, termino_norm: str) -> float:
    pesos = _PESOS_ESPECIALES_INTERESES.get(area, {})
    if termino_norm in pesos:
        return pesos[termino_norm]

    if area == "matematicas":
        pistas = (
            "comput", "informatic", "program", "codigo", "algorit", "software",
            "hardware", "robot", "dato", "red", "ciber", "web", "app", "videoj",
            "inteligencia artificial", "machine learning", "base de datos",
            "analisis numerico", "estadistic", "probabil", "geometri", "algebr",
            "calcul", "ecuac", "logica", "tecnolog", "sistema", "fisic",
        )
        if any(pista in termino_norm for pista in pistas):
            return 1.35

    elif area == "salud":
        pistas = (
            "medic", "hospital", "enferm", "pacient", "biolog", "curar", "salud",
            "anatom", "fisiolog", "farmac", "clin", "diagnost", "tratam", "odont",
            "nutric", "veterin", "rehabilit", "epidemi", "biomed", "terapia",
        )
        if any(pista in termino_norm for pista in pistas):
            return 1.25

    elif area == "humanidades":
        pistas = (
            "histori", "derech", "socied", "polit", "escrit", "comunic", "filos",
            "cultur", "debate", "educ", "sociolog", "antropolog", "literatur",
            "linguist", "idiom", "traducc", "bibliotec", "arqueolog", "etica",
            "econom", "mercadot", "administr", "negoc",
        )
        if any(pista in termino_norm for pista in pistas):
            return 1.20

    elif area == "arte":
        pistas = (
            "dibuj", "pint", "arte", "disen", "creativ", "mus", "fotograf",
            "anim", "ilustr", "cine", "teatr", "danz", "escultur", "moda",
            "multimedia", "son", "edicion", "modelado", "historiet", "mural",
        )
        if any(pista in termino_norm for pista in pistas):
            return 1.20

    return 1.0

#_______________________________________________________________________________________________________

def puntuar_intereses(texto: str, intenciones: dict) -> Dict[str, float]:
    """
    Calcula una distribución de evidencia por área a partir de un mensaje.
    Cada mensaje reparte su peso entre las áreas que realmente aparezcan,
    evitando que una frase larga distorsione el resultado.
    """
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return {}

    tokens = texto_norm.split()
    puntajes = {categoria: 0.0 for categoria in AREAS_VALIDAS}

    for categoria in AREAS_VALIDAS:
        palabras = intenciones.get(categoria, []) or []
        for palabra in palabras:
            palabra_norm = normalizar_texto(palabra)
            if not palabra_norm:
                continue

            match = 0.0

            if " " in palabra_norm:
                if palabra_norm in texto_norm:
                    match = 2.3 + (len(palabra_norm.split()) * 0.18)
            else:
                if palabra_norm in tokens:
                    match = 1.35
                else:
                    for tok in tokens:
                        if len(tok) >= 4 and (tok.startswith(palabra_norm) or palabra_norm.startswith(tok)):
                            match = 0.68
                            break

            if match > 0:
                match *= _peso_especial_interes(categoria, palabra_norm)
                puntajes[categoria] += match

    total = sum(puntajes.values())
    if total <= 0:
        return {}

    return {
        categoria: round(valor / total, 4)
        for categoria, valor in puntajes.items()
        if valor > 0
    }

#_______________________________________________________________________________________________________

def detectar_intereses(texto: str, intenciones: dict) -> List[str]:
    """
    Devuelve las áreas detectadas, ordenadas por evidencia descendente.
    """
    puntajes = puntuar_intereses(texto, intenciones)
    if not puntajes:
        return []
    return [categoria for categoria, _ in sorted(puntajes.items(), key=lambda item: (-item[1], item[0]))]