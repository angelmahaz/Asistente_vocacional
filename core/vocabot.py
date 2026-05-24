
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
#                                   MODULO: CHATBOT
# ------------------------------------------------------------------------------------------
# Funciones para gestionar la conversación con el usuario, cargar intenciones y
# extraer respuestas relevantes para el análisis vocacional.
# ------------------------------------------------------------------------------------------

import json
import random
import unicodedata
import re

# --------------------------------------------------------------------------
# NORMALIZACION
# --------------------------------------------------------------------------

def normalizar(texto):
    """
    Convierte el texto a minusculas y elimina acentos/tildes.
    Ejemplo: 'Matematicas' -> 'matematicas', 'fisica' -> 'fisica'
    """
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto


# --------------------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------------------

def cargar_intenciones(ruta):
    """
    Carga el JSON de intenciones y pre-normaliza todas las palabras clave
    para busquedas rapidas y sin distincion de acentos.
    """
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    normalizado = {}
    for categoria, palabras in data.items():
        normalizado[categoria] = [normalizar(p) for p in palabras]
    return normalizado


# --------------------------------------------------------------------------
# DETECCION DE INTENCIONES ESPECIALES
# --------------------------------------------------------------------------

INTENCIONES_ESPECIALES = [
    "saludo", "despedida", "agradecimiento",
    "afirmacion", "negacion", "indecision",
    "intensidad_alta", "intensidad_baja",
    "nombre", "recomendacion", "reinicio"
]

def detectar_intencion(texto, intenciones):
    """
    Recorre las intenciones especiales y retorna la primera que coincida.
    Prioridad: recomendacion > afirmacion > negacion > indecision > resto.
    Retorna None si no hay coincidencia.
    """
    texto_n = normalizar(texto)
    # Orden de prioridad de deteccion
    orden = [
        "recomendacion", "reinicio", "despedida",
        "indecision", "afirmacion", "negacion",
        "intensidad_alta", "intensidad_baja",
        "agradecimiento", "saludo", "nombre"
    ]
    for tipo in orden:
        if tipo not in intenciones:
            continue
        for palabra in intenciones[tipo]:
            # Busqueda de palabra completa (evita falsos positivos de substring)
            patron = r'(?<!\w)' + re.escape(palabra) + r'(?!\w)'
            if re.search(patron, texto_n):
                return tipo
    return None


def detectar_nombre(texto, intenciones):
    """
    Intenta extraer el nombre del usuario del texto.
    Retorna el nombre capitalizado o None.
    """
    texto_n = normalizar(texto)
    claves = intenciones.get("nombre", [])
    for clave in claves:
        if clave in texto_n:
            # Tomar lo que viene despues de la clave
            idx = texto_n.find(clave) + len(clave)
            resto = texto[idx:].strip().strip(".,!?;:")
            palabras = resto.split()
            if palabras:
                return palabras[0].capitalize()
    return None


# --------------------------------------------------------------------------
# DETECCION DE AREAS VOCACIONALES EN TEXTO LIBRE
# --------------------------------------------------------------------------

# Las categorias vocacionales corresponden exactamente a las areas en areas.json
CATEGORIAS_VOCACIONALES = [
    "Ciencias Fisico-Matematicas y de las Ingenierias",
    "Ciencias Biologicas Quimicas y de la Salud",
    "Ciencias Sociales",
    "Humanidades y de las Artes"
]

def detectar_intereses(texto, areas_data):
    """
    Analiza un texto de cualquier longitud y cuenta cuantas palabras clave
    de cada area aparecen. Retorna una lista de areas ordenadas de mayor a
    menor coincidencia.

    Ejemplo: "me gusta la ciencia, programar y resolver problemas"
    -> ["Ciencias Fisico-Matematicas y de las Ingenierias", ...]
    """
    texto_n = normalizar(texto)
    conteo = {area: 0 for area in CATEGORIAS_VOCACIONALES}

    for area in CATEGORIAS_VOCACIONALES:
        palabras_clave = areas_data.get(area, {})
        for palabra, peso in palabras_clave.items():
            palabra_n = normalizar(palabra)
            # Busqueda de termino completo para evitar falsos positivos
            patron = r'(?<!\w)' + re.escape(palabra_n) + r'(?!\w)'
            coincidencias = len(re.findall(patron, texto_n))
            if coincidencias > 0:
                conteo[area] += coincidencias * peso

    # Filtrar areas con al menos una coincidencia
    activas = {a: v for a, v in conteo.items() if v > 0}
    if not activas:
        return []

    # Ordenar de mayor a menor
    return sorted(activas.keys(), key=lambda a: activas[a], reverse=True)


# --------------------------------------------------------------------------
# RESPUESTAS DEL BOT
# --------------------------------------------------------------------------

RESPUESTAS_HUMANAS = {
    "Ciencias Fisico-Matematicas y de las Ingenierias": [
        "Parece que te llaman la atencion la logica, los numeros y la tecnologia.",
        "Interesante, ese pensamiento analitico es clave en ingenieria y ciencias exactas.",
        "Se nota que disfrutas resolver problemas y trabajar con sistemas o maquinas.",
        "Esa inclinacion hacia la tecnologia y las matematicas es muy valiosa hoy en dia.",
        "El area de ciencias e ingenieria encaja bien con lo que describes."
    ],
    "Ciencias Biologicas Quimicas y de la Salud": [
        "Se nota que te interesan los seres vivos, la salud o la quimica.",
        "Ese interes por cuidar o entender el cuerpo y la naturaleza es muy valioso.",
        "El area de ciencias de la salud y biologia parece resonar contigo.",
        "Quienes se inclinan por la salud suelen tener una vocacion de servicio muy fuerte.",
        "La biologia, la quimica y la medicina son mundos apasionantes que van bien con lo que describes."
    ],
    "Ciencias Sociales": [
        "Parece que te importa entender como funciona la sociedad y las personas.",
        "Ese interes por la economia, el derecho o la comunicacion es muy amplio y util.",
        "Las ciencias sociales encajan con quienes quieren generar cambios en su entorno.",
        "Trabajar con personas, analizar datos sociales o gestionar organizaciones suena a lo tuyo.",
        "Ese perfil orientado a la sociedad y los negocios tiene mucho campo de accion."
    ],
    "Humanidades y de las Artes": [
        "Se nota que la creatividad, la expresion y la cultura son parte de ti.",
        "El arte, la filosofia y las letras son areas que dan mucho a quienes las eligen con pasion.",
        "Ese gusto por crear, leer o reflexionar habla de una mente critica y sensible.",
        "Las humanidades y las artes forman profesionales capaces de transformar la cultura.",
        "Esa inclinacion creativa y humanista es un rasgo que pocas disciplinas desarrollan tan bien."
    ]
}

FALLBACKS = [
    "Cuentame mas sobre lo que te gusta hacer en tu tiempo libre.",
    "No termine de entender. Puedes describir que materias o actividades disfrutas?",
    "Intentalo de otra forma. Por ejemplo, habla de lo que mas te gusta estudiar o hacer.",
    "Eso no lo reconoci bien. Puedes contarme sobre algun tema que te apasione?",
    "No estoy seguro de haber comprendido. Que actividades o materias te llaman la atencion?"
]

INDECISIONES = [
    "Entiendo que no tienes todo claro todavia, es completamente normal. Piensa en que tipo de actividades disfrutas mas y cuentame.",
    "La indecision es parte del proceso. Cuéntame que materias te gustaban en la escuela o que haces cuando tienes tiempo libre.",
    "No hay problema si no tienes claro. Dime: que prefieres, trabajar con numeros, con personas, con arte o con la naturaleza?",
    "Es normal tener dudas a esta edad. Piensa en algo que hayas hecho y te haya gustado mucho, y cuentamelo.",
    "Tomalo con calma. No necesitas tener todo resuelto. Solo cuentame que cosas te llaman la atencion en general."
]

RESPUESTAS_SALUDO = [
    "Hola, soy Vocabot. Estoy aqui para ayudarte a descubrir que area de estudios va mejor contigo. Cuentame, como te llamas?",
    "Bienvenido. Soy Vocabot, tu asistente vocacional. Antes de empezar, me dices tu nombre?",
    "Hola. Soy Vocabot y voy a ayudarte a encontrar tu vocacion. Primero, como te llamas?"
]

def respuesta_saludo():
    return random.choice(RESPUESTAS_SALUDO)

def respuesta_humana(area):
    return random.choice(RESPUESTAS_HUMANAS.get(area, FALLBACKS))

def respuesta_fallback():
    return random.choice(FALLBACKS)

def respuesta_indecision():
    return random.choice(INDECISIONES)

def respuesta_agradecimiento():
    return random.choice([
        "Con gusto. Si tienes mas preguntas, aqui estoy.",
        "Es un placer ayudarte. Cualquier duda, me avisas.",
        "Me alegra haber sido util. Mucho exito en lo que decidas."
    ])

def respuesta_despedida(nombre=None):
    base = "Fue un gusto hablar contigo"
    if nombre:
        base += f", {nombre}"
    return base + ". Te deseo mucho exito en tu camino. Hasta luego."

def respuesta_afirmacion_ambigua():
    return random.choice([
        "Perfecto. Siguiendo con la conversacion, cuentame algo mas sobre tus gustos.",
        "De acuerdo. Habla mas sobre lo que te gusta hacer o estudiar.",
        "Bien. Sigueme contando sobre tus intereses para poder darte una mejor recomendacion."
    ])


# --------------------------------------------------------------------------
# FUNCION AUXILIAR: iniciar_chat (solo consola, no se usa en API)
# --------------------------------------------------------------------------

def iniciar_chat():
    print("\n--- VOCABOT: Asistente Vocacional IA ---")
    print("Escribe 'salir' en cualquier momento para terminar.\n")
