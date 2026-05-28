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

# Disparadores para detectar nombre
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

# Palabras que se ignoran al limpiar el nombre
STOPWORDS_POST_NOMBRE = {
    "y", "pero", "porque", "pues", "aunque", "entonces", "además", "tambien",
    "también", "con", "sin", "para", "por", "que", "donde", "cuando", "si",
    "me", "mi", "soy", "llamo"
}

# Palabras y fragmentos de saludo
SALUDOS_SIMPLES = {
    "hola", "buenas", "hey", "hello", "saludos", "alo", "buen", "dia",
    "dias", "tarde", "tardes", "noche", "noches", "que", "tal", "onda"
}

#_______________________________________________________________________________________________________

# Frases de saludo y apoyo que se utilizan para identificar si el mensaje es solo un saludo básico.
FRASES_DE_APOYO = {
    "hola", "buenas", "hey", "hello", "saludos", "alo", "que tal",
    "que onda", "buen dia", "buenos dias", "buenas tardes", "buenas noches"
}

# Gustos musicales usados como easter egg vocacional y como pista para el área de arte
_GUSTOS_MUSICA_ROCK_METAL = {
    "rock", "metal", "metalero", "metalera", "rockero", "rockera",
    "heavy metal", "hard rock", "punk", "indie", "grunge", "alternativo"
}

_GUSTOS_MUSICA_URBANA = {
    "reggaeton", "regueton", "trap", "rap", "hip hop", "hiphop", "urbano", "corridos tumbados"
}

_RESPUESTAS_ARTE_ROCK_METAL = [
    "Se nota una mente abierta y un pensamiento crítico muy sólido.",
    "Ese gusto por el rock o el metal suele ir con perfiles creativos y muy definidos.",
    "Tienes una vibra con mucho carácter y criterio propio.",
    "Eso encaja muy bien con personas creativas, analíticas y con personalidad fuerte.",
]

_RESPUESTAS_ARTE_URBANA = [
    "Tienes una vibra urbana y rítmica; vamos a seguir afinando tu perfil vocacional.",
    "Se nota energía y gusto por lo rítmico; ahora veamos qué área te queda mejor.",
    "Tu estilo es más movido y moderno; igual podemos aterrizar bien tu orientación.",
    "Buen ritmo y mucha presencia; sigamos construyendo tu perfil académico.",
]


def tiene_contenido_relevante(texto: str) -> bool:

    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return False

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

# Abre un archivo JSON y devuelve su contenido.

def _abrir_json(ruta: str):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

#_______________________________________________________________________________________________________

# Si los datos son un diccionario y contienen una clave cuyo valor es otro diccionario,lo extrae;
# de lo contrario devuelve los datos originales.

def _desenvolver_si_viene_envuelto(datos, clave: str):
    if isinstance(datos, dict) and clave in datos and isinstance(datos[clave], dict):
        return datos[clave]
    return datos

#_______________________________________________________________________________________________________

# Carga el archivo de intenciones y normaliza su estructura interna.

def cargar_intenciones(ruta: str) -> dict:
    datos = _abrir_json(ruta)
    datos = _desenvolver_si_viene_envuelto(datos, "intenciones")
    return datos if isinstance(datos, dict) else {}

#_______________________________________________________________________________________________________

# Normaliza un texto: elimina acentos, signos de puntuación y espacios redundantes,y lo convierte a 
# minúsculas para facilitar comparaciones.

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

# Verifica si alguna de las frases dadas aparece dentro del texto normalizado.

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

# Detecta el área de interés dominante (matemáticas, salud, humanidades, arte)
# a partir del texto del usuario, usando las palabras clave definidas en intenciones.json.
# Retorna una lista con el área de mayor puntuación (puede estar vacía si no hay coincidencias).

def detectar_intereses(texto: str, intenciones: dict) -> List[str]:
    """
    Devuelve las áreas detectadas, ordenadas por evidencia descendente.
    """
    puntajes = puntuar_intereses(texto, intenciones)
    if not puntajes:
        return []
    return [categoria for categoria, _ in sorted(puntajes.items(), key=lambda item: (-item[1], item[0]))]

#_______________________________________________________________________________________________________

# Detecta si el usuario está pidiendo explícitamente una recomendación.

def detectar_recomendacion(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("recomendacion", []))

#_______________________________________________________________________________________________________

# Detecta si el usuario se está despidiendo (palabras clave como "salir", "adios", etc.).

def es_despedida(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("despedida", []))

#_______________________________________________________________________________________________________

# Detecta si el usuario está saludando.

def es_saludo(texto: str, intenciones: dict) -> bool:
    return coincide_frases(texto, intenciones.get("saludo", []))

#_______________________________________________________________________________________________________

# Verifica si la respuesta del usuario es una afirmación clara (sí, claro, ok, etc.).

def es_afirmacion(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)
    return texto_norm in {"si", "sí", "claro", "ok", "vale", "va", "correcto", "de acuerdo", "por supuesto"}

#_______________________________________________________________________________________________________

# Verifica si la respuesta es una negación (no, nop, nada, etc.).

def es_negacion(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)
    return texto_norm in {"no", "nop", "nel", "negativo", "para nada", "nada", "no gracias"}

# ------------------------------------------------------------------------------------------
# Conjuntos de palabras para interpretar respuestas binarias (sí/no) y de escala 1 a 5.
# ------------------------------------------------------------------------------------------

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

# Verifica si una frase normalizada está contenida en el texto normalizado.

def _contiene_frase_normalizada(texto_norm: str, frase: str) -> bool:
    frase_norm = normalizar_texto(frase)
    if not texto_norm or not frase_norm:
        return False
    return frase_norm in texto_norm

#_______________________________________________________________________________________________________

# Verifica si un token (palabra) normalizado está presente en el texto normalizado.

def _contiene_token(texto_norm: str, token: str) -> bool:
    token_norm = normalizar_texto(token)
    if not texto_norm or not token_norm:
        return False
    return token_norm in texto_norm.split()

#_______________________________________________________________________________________________________

# Interpreta una respuesta del usuario como afirmativa (True), negativa (False) o incierta (None).

def interpretar_respuesta_binaria(texto: str) -> Optional[bool]:

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

# Convierte una respuesta en un valor numérico de 1 a 5 según la intensidad del interés. 

def interpretar_respuesta_escala(texto: str) -> Optional[int]:

    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None

    if any(_contiene_frase_normalizada(texto_norm, frase) for frase in _RESPUESTAS_BINARIAS_INDEFINIDAS):
        return None

    escalas = [
        (2, sorted(_RESPUESTAS_ESCALA_2, key=len, reverse=True)),
        (1, sorted(_RESPUESTAS_ESCALA_1, key=len, reverse=True)),
        (3, sorted({"mas o menos", "más o menos", "regular", "neutral", "intermedio", "mitad", "a medias"}, key=len, reverse=True)),
        (5, sorted(_RESPUESTAS_ESCALA_5, key=len, reverse=True)),
        (4, sorted(_RESPUESTAS_ESCALA_4, key=len, reverse=True)),
    ]

    for valor, patrones in escalas:
        for patron in patrones:
            patron_norm = normalizar_texto(patron)
            if " " in patron_norm:
                if _contiene_frase_normalizada(texto_norm, patron_norm):
                    return valor
            else:
                if _contiene_token(texto_norm, patron_norm):
                    return valor

    if any(_contiene_frase_normalizada(texto_norm, frase) for frase in _RESPUESTAS_ESCALA_4):
        return 4

    return None

#_______________________________________________________________________________________________________

# Devuelve True si la respuesta es afirmativa según interpretar_respuesta_binaria.

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

# Extrae el nombre del usuario si el texto contiene frases como "me llamo X" o "soy Y" y retorna el 
# nombre capitalizado o None si no se detecta.


def extraer_nombre(texto: str) -> Optional[str]:

    if not texto:
        return None

    texto_original = texto.strip()

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

        primer_token = normalizar_texto(candidato).split()[0]
        if primer_token in PALABRAS_NO_NOMBRE:
            continue

        return candidato.title()

    return None


#_______________________________________________________________________________________________________

# Elimina del texto las frases que contienen el nombre para que no interfieran con la detección 
# de intereses.

def limpiar_mensaje_nombre(texto: str) -> str:

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

def respuesta_humana(tipo: str, contexto: str = "") -> str:
    contexto_norm = normalizar_texto(contexto)

    if tipo == "arte" and contexto_norm:
        if coincide_frases(contexto_norm, list(_GUSTOS_MUSICA_ROCK_METAL)):
            return random.choice(_RESPUESTAS_ARTE_ROCK_METAL)
        if coincide_frases(contexto_norm, list(_GUSTOS_MUSICA_URBANA)):
            return random.choice(_RESPUESTAS_ARTE_URBANA)

    respuestas = {
        "matematicas": [
            "Eso suena muy lógico y analítico.",
            "Tienes perfil para resolver problemas complejos.",
            "Veo afinidad con áreas técnicas y de razonamiento.",
            "Ese tipo de pensamiento es muy valioso en ingeniería y ciencias exactas.",
            "La tecnología y las matemáticas son campos con un enorme futuro.",
            "Interesante, ese perfil encaja muy bien con las ingenierías.",
            "Los sistemas, los datos y la lógica son tu mundo, se nota.",
            "Esa inclinación hacia lo técnico abre muchas puertas profesionales.",
        ],
        "salud": [
            "Se nota que te importa ayudar a otros.",
            "Tienes vocación de servicio.",
            "Eso encaja muy bien con profesiones de cuidado y apoyo.",
            "El área de salud necesita personas con esa sensibilidad.",
            "Quienes se orientan a la salud suelen tener un gran compromiso humano.",
            "La biología y las ciencias de la salud son apasionantes.",
            "Ese interés por el cuerpo humano y la vida es muy valioso.",
            "Cuidar a los demás es una de las vocaciones más significativas.",
        ],
        "humanidades": [
            "Eso refleja pensamiento crítico.",
            "Te interesa entender la sociedad.",
            "Veo interés por la comunicación y el análisis social.",
            "Las humanidades forman personas capaces de interpretar el mundo.",
            "Ese perfil analítico y social tiene mucho campo de acción.",
            "Las ciencias sociales ofrecen una visión muy completa de la realidad.",
            "Entender cómo funciona la sociedad es fundamental hoy en día.",
            "Ese interés por la cultura, las ideas y las personas dice mucho de ti.",
        ],
        "arte": [
            "Tienes creatividad.",
            "Eso es muy valioso en el arte.",
            "Se nota un perfil creativo y expresivo.",
            "La expresión artística es una habilidad que pocas personas desarrollan bien.",
            "El diseño, el arte y la cultura necesitan personas como tú.",
            "Esa sensibilidad creativa es un rasgo muy particular y valioso.",
            "El arte y el diseño tienen cada vez más presencia en el mundo profesional.",
            "Crear, diseñar y expresar son habilidades que abren muchas puertas.",
        ],
    }
    opciones = respuestas.get(tipo, ["Interesante, cuéntame un poco más."])
    return random.choice(opciones)

#_______________________________________________________________________________________________________

# Respuesta del bot cuando quiere seguir animando la conversación.

def respuesta_general() -> str:
    return random.choice([
        "Cuéntame más.",
        "Interesante...",
        "Sigue, te escucho.",
        "Eso me ayuda a conocerte mejor.",
        "Voy entendiendo tus gustos.",
    ])

#_______________________________________________________________________________________________________

# Respuesta cuando el bot no logra entender el mensaje del usuario.

def respuesta_no_entendida() -> str:
    return random.choice([
        "No estoy seguro de entender. ¿Puedes explicarlo de otra forma?",
        "Tal vez hubo un pequeño error al escribir. ¿Puedes repetirlo?",
        "No lo capté del todo, pero sigo contigo. ¿Me lo cuentas diferente?",
        "No entendí esa parte. ¿Puedes decirlo con otras palabras?",
        "Creo que no comprendí bien. Puedes hablarme de materias, hobbies o actividades que disfrutes.",
        "No logré identificar tus intereses en eso. ¿Puedes ser un poco más específico?",
        "Creo que no comprendí bien. ¿Qué materias o actividades te llaman la atención?",
    ])

#_______________________________________________________________________________________________________

# Carga la lista de preguntas desde el archivo JSON

def cargar_preguntas(ruta: str) -> list:
    datos = _abrir_json(ruta)
    if isinstance(datos, dict) and "preguntas" in datos and isinstance(datos["preguntas"], list):
        return datos["preguntas"]
    if isinstance(datos, list):
        return datos
    return []


# ---------------------------------------------------------------------------
# Pesos adicionales para ciertas palabras clave en cada área (refuerzan la puntuación).x
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

# 

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
            "rock", "metal", "reggaeton", "regueton", "trap", "rap", "hip hop",
            "jazz", "blues", "punk", "indie", "electro", "electron", "urban",
            "musica", "cancion", "canciones", "concierto", "banda",
        )
        if any(pista in termino_norm for pista in pistas):
            if any(pista in termino_norm for pista in ("rock", "metal")):
                return 1.55
            if any(pista in termino_norm for pista in ("reggaeton", "regueton", "trap", "rap", "hip hop", "urban")):
                return 1.10
            return 1.20

    return 1.0

#_______________________________________________________________________________________________________

# Puntúa el texto del usuario asignando evidencia a cada área (matemáticas, salud, etc.)
# usando las palabras clave y los pesos especiales. Normaliza los puntajes para que sumen 1.

def puntuar_intereses(texto: str, intenciones: dict) -> Dict[str, float]:

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

# Devuelve las áreas detectadas ordenadas por mayor evidencia (la primera es la más probable).

def detectar_intereses(texto: str, intenciones: dict) -> List[str]:

    puntajes = puntuar_intereses(texto, intenciones)
    if not puntajes:
        return []
    return [categoria for categoria, _ in sorted(puntajes.items(), key=lambda item: (-item[1], item[0]))]