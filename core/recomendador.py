
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

# URLs oficiales de informacion de oferta educativa
LINKS_UNIVERSIDADES = {
    "UNAM": "https://www.unam.mx/oferta-educativa",
    "IPN":  "https://www.ipn.mx/oferta-educativa/",
    "UAM":  "https://www.uam.mx/licenciaturas/"
}


def cargar_carreras(ruta):
    """
    Carga el archivo carreras.json.
    Estructura esperada:
        { "Area": { "Universidad": ["Carrera1", "Carrera2", ...] } }
    """
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def recomendar(area, carreras_data, n=5, universidad=None):
    """
    Retorna las primeras n carreras del area especificada, agrupadas por universidad.

    Parametros:
        area          (str)  Nombre del area (debe coincidir con clave en carreras.json)
        carreras_data (dict) Datos cargados de carreras.json
        n             (int)  Numero maximo de carreras por universidad (default 5)
        universidad   (str)  Si se especifica, filtra solo esa universidad

    Retorna:
        dict { "Universidad": ["Carrera1", ...] }
    """
    if area not in carreras_data:
        return {}

    resultado = {}
    datos_area = carreras_data[area]

    unis = [universidad] if universidad else list(datos_area.keys())
    for uni in unis:
        if uni in datos_area:
            resultado[uni] = datos_area[uni][:n]

    return resultado


def recomendar_segunda_opcion(probabilidades, carreras_data, n=4):
    """
    Encuentra la segunda area mas probable y retorna sus carreras.

    Parametros:
        probabilidades (dict) Salida del perceptron {area: prob}
        carreras_data  (dict) Datos de carreras
        n              (int)  Numero de carreras por universidad

    Retorna:
        (segunda_area: str, carreras: dict)
    """
    areas_ordenadas = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    if len(areas_ordenadas) < 2:
        return None, {}

    segunda_area = areas_ordenadas[1][0]
    return segunda_area, recomendar(segunda_area, carreras_data, n)


def link_universidad(uni):
    """Retorna la URL oficial de informacion de la universidad."""
    return LINKS_UNIVERSIDADES.get(uni, f"https://www.{uni.lower().replace(' ', '')}.mx")


def formatear_recomendacion(area, carreras, descripcion, confianza, nivel, segunda_area=None, segunda_carreras=None, nombre=None):
    """
    Genera el texto completo de recomendacion listo para enviar por WhatsApp.
    Sin emojis, en lenguaje natural y claro.

    Retorna una lista de mensajes (strings) para enviarlos en partes
    y no superar el limite de caracteres de WhatsApp (~4096 chars por mensaje).
    """
    partes = []

    # Encabezado
    saludo = f"Muy bien{', ' + nombre if nombre else ''}."
    partes.append(
        f"{saludo} Basandome en todo lo que me contaste, el perceptron analizo tus respuestas y "
        f"te ubica principalmente en el area de:\n\n"
        f"{area}\n\n"
        f"{descripcion}\n\n"
        f"Nivel de confianza del analisis: {nivel} ({confianza}%)"
    )

    # Carreras por universidad
    for uni, lista in carreras.items():
        link = link_universidad(uni)
        carreras_txt = "\n".join(f"  - {c}" for c in lista)
        partes.append(
            f"Carreras recomendadas en {uni}:\n{carreras_txt}\n\nMas informacion: {link}"
        )

    # Segunda opcion
    if segunda_area and segunda_carreras:
        partes.append(
            f"Como segunda opcion, tambien hay afinidad con:\n{segunda_area}\n\n"
            f"Algunas carreras de esta area:"
        )
        for uni, lista in segunda_carreras.items():
            carreras_txt = "\n".join(f"  - {c}" for c in lista[:3])
            partes.append(f"{uni}:\n{carreras_txt}")

    # Cierre
    partes.append(
        "Recuerda que esta recomendacion es orientativa. Lo mas importante es que explores "
        "cada opcion con calma y hables con personas que ya estudien esas carreras.\n\n"
        "Quieres que empecemos de nuevo para explorar otra area? Escribe 'si' o 'no'."
    )

    return partes
