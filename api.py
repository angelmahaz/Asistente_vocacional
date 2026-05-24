
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
#                               API PARA WHATSAPP — Flask + Twilio
# ------------------------------------------------------------------------------------------
# Expone un webhook que recibe mensajes de WhatsApp via Twilio Sandbox y
# mantiene el estado de conversacion de cada usuario en memoria.
#
# Flujo de la conversacion:
#   bienvenida -> preguntar_nombre -> conversacion_libre -> resultado -> post_resultado
#
# Estados de sesion:
#   "bienvenida"         -> Se acaba de crear la sesion, primer mensaje
#   "esperando_nombre"   -> El bot pidio el nombre y espera respuesta
#   "conversacion"       -> Recolectando intereses del usuario (estado principal)
#   "resultado"          -> Se mostro el resultado, esperando si/no para reiniciar
#   "fin"                -> La sesion termino (despedida)
#
# Para conectar con Twilio WhatsApp:
#   1. Crea cuenta en https://www.twilio.com
#   2. Activa el Sandbox de WhatsApp
#   3. Pon la URL de este servidor + /webhook como Webhook URL del Sandbox
#   4. Instala dependencias: pip install flask twilio
#   5. Ejecuta: python api.py
#
# Variables de entorno requeridas (crea un archivo .env):
#   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
#   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
#   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  (numero del Sandbox)
# ------------------------------------------------------------------------------------------

import os
import sys
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

# Asegurar que la raiz del proyecto este en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.vocabot import (
    cargar_intenciones,
    normalizar,
    detectar_intencion,
    detectar_nombre,
    detectar_intereses,
    respuesta_saludo,
    respuesta_humana,
    respuesta_fallback,
    respuesta_indecision,
    respuesta_agradecimiento,
    respuesta_despedida,
    respuesta_afirmacion_ambigua,
    CATEGORIAS_VOCACIONALES
)
from core.perceptron import cargar_areas, evaluar, descripcion_area
from core.recomendador import (
    cargar_carreras,
    recomendar,
    recomendar_segunda_opcion,
    formatear_recomendacion
)

# --------------------------------------------------------------------------
# INICIALIZACION DE FLASK Y CARGA DE DATOS
# --------------------------------------------------------------------------

app = Flask(__name__)

intenciones   = cargar_intenciones(os.path.join(BASE_DIR, "data", "intenciones.json"))
areas_data    = cargar_areas(os.path.join(BASE_DIR, "data", "areas.json"))
carreras_data = cargar_carreras(os.path.join(BASE_DIR, "data", "carreras.json"))

# --------------------------------------------------------------------------
# SESIONES EN MEMORIA
# En produccion reemplazar por Redis o una base de datos.
# --------------------------------------------------------------------------

sessions = {}

# --------------------------------------------------------------------------
# GESTION DE SESION
# --------------------------------------------------------------------------

def nueva_sesion():
    """Crea una sesion limpia para un usuario nuevo."""
    return {
        "estado":   "bienvenida",
        "nombre":   None,
        "memoria":  {area: 0.0 for area in CATEGORIAS_VOCACIONALES},
        "turnos":   0,
        "mensajes_pendientes": []  # cola de mensajes a enviar en partes
    }


def get_sesion(user_id):
    """Obtiene la sesion del usuario o crea una nueva."""
    if user_id not in sessions:
        sessions[user_id] = nueva_sesion()
    return sessions[user_id]


# --------------------------------------------------------------------------
# LOGICA DE CONVERSACION
# --------------------------------------------------------------------------

# Numero de turnos de conversacion antes de lanzar el resultado automaticamente
TURNOS_PARA_RESULTADO = 6

# Puntuacion minima acumulada para lanzar resultado (evita resultados vacios)
PUNTUACION_MINIMA = 3.0


def hay_suficiente_informacion(sesion):
    """
    Verifica si hay suficientes datos para generar una recomendacion confiable.
    Condicion: al menos TURNOS_PARA_RESULTADO turnos Y puntuacion minima acumulada.
    """
    total = sum(sesion["memoria"].values())
    return sesion["turnos"] >= TURNOS_PARA_RESULTADO and total >= PUNTUACION_MINIMA


def generar_resultado(sesion):
    """
    Ejecuta el perceptron y construye la lista de mensajes de resultado.
    Retorna una lista de strings listos para enviar.
    """
    area, _, prob, confianza, nivel = evaluar(sesion["memoria"], areas_data)
    desc = descripcion_area(area)
    carreras = recomendar(area, carreras_data, n=5)
    segunda_area, segunda_carreras = recomendar_segunda_opcion(prob, carreras_data, n=3)

    mensajes = formatear_recomendacion(
        area=area,
        carreras=carreras,
        descripcion=desc,
        confianza=confianza,
        nivel=nivel,
        segunda_area=segunda_area,
        segunda_carreras=segunda_carreras,
        nombre=sesion["nombre"]
    )
    return mensajes


def procesar_mensaje(user_id, texto_usuario):
    """
    Funcion central. Recibe el texto del usuario y retorna UNA respuesta (string).
    Maneja todos los estados de la conversacion y nunca deja de responder.

    Los mensajes largos del resultado se guardan en la cola sesion["mensajes_pendientes"]
    y se envian de uno en uno en los siguientes turnos si el usuario escribe algo.
    """
    sesion = get_sesion(user_id)
    texto_n = normalizar(texto_usuario)
    estado  = sesion["estado"]

    # ------------------------------------------------------------------
    # COLA DE MENSAJES PENDIENTES (para mensajes de resultado en partes)
    # ------------------------------------------------------------------
    if sesion["mensajes_pendientes"]:
        siguiente = sesion["mensajes_pendientes"].pop(0)
        # Si la cola quedo vacia, cambiar estado a resultado
        if not sesion["mensajes_pendientes"]:
            sesion["estado"] = "resultado"
        return siguiente

    # ------------------------------------------------------------------
    # ESTADO: bienvenida
    # Primer contacto. Saludar y pedir nombre.
    # ------------------------------------------------------------------
    if estado == "bienvenida":
        sesion["estado"] = "esperando_nombre"
        return respuesta_saludo()

    # ------------------------------------------------------------------
    # ESTADO: fin
    # La sesion termino. Cualquier mensaje reinicia.
    # ------------------------------------------------------------------
    if estado == "fin":
        sessions[user_id] = nueva_sesion()
        sesion = get_sesion(user_id)
        sesion["estado"] = "esperando_nombre"
        return "Hola de nuevo. Soy Vocabot. Para empezar, me dices tu nombre?"

    # ------------------------------------------------------------------
    # DETECCION DE INTENCIONES GLOBALES (funcionan en cualquier estado)
    # ------------------------------------------------------------------
    intencion = detectar_intencion(texto_usuario, intenciones)

    # Despedida (cualquier estado)
    if intencion == "despedida":
        sesion["estado"] = "fin"
        return respuesta_despedida(sesion["nombre"])

    # Reinicio (cualquier estado)
    if intencion == "reinicio":
        sessions[user_id] = nueva_sesion()
        sesion = get_sesion(user_id)
        sesion["estado"] = "esperando_nombre"
        return "De acuerdo, empecemos de nuevo. Como te llamas?"

    # Agradecimiento (cualquier estado)
    if intencion == "agradecimiento" and estado not in ("esperando_nombre", "conversacion"):
        return respuesta_agradecimiento()

    # ------------------------------------------------------------------
    # ESTADO: esperando_nombre
    # ------------------------------------------------------------------
    if estado == "esperando_nombre":
        nombre = detectar_nombre(texto_usuario, intenciones)

        if nombre:
            sesion["nombre"] = nombre
            sesion["estado"] = "conversacion"
            return (
                f"Mucho gusto, {nombre}. Voy a hacerte algunas preguntas para conocer tus intereses "
                f"y ayudarte a identificar que area de estudios va mejor contigo.\n\n"
                f"Para empezar, cuentame: que materias o actividades disfrutas mas? "
                f"Puedes escribir lo que quieras, no hay respuestas incorrectas."
            )

        # Si no detectamos nombre pero el usuario escribio algo, tomarlo como nombre directamente
        palabras = texto_usuario.strip().split()
        if palabras and len(palabras) <= 3:
            nombre = palabras[0].capitalize()
            sesion["nombre"] = nombre
            sesion["estado"] = "conversacion"
            return (
                f"Perfecto, {nombre}. Vamos a empezar.\n\n"
                f"Cuentame: que materias, temas o actividades disfrutas o te llaman la atencion? "
                f"Escribe con tus propias palabras."
            )

        # Si escribio algo largo sin presentarse, continuar igual
        sesion["estado"] = "conversacion"
        return (
            "Entendido. No me dijiste tu nombre pero no hay problema, podemos continuar.\n\n"
            "Cuentame: que materias, temas o actividades disfrutas o te llaman la atencion?"
        )

    # ------------------------------------------------------------------
    # ESTADO: resultado
    # El bot ya dio la recomendacion. Espera si/no para reiniciar o terminar.
    # ------------------------------------------------------------------
    if estado == "resultado":
        if intencion == "afirmacion":
            sessions[user_id] = nueva_sesion()
            sesion = get_sesion(user_id)
            sesion["estado"] = "esperando_nombre"
            return "De acuerdo, empecemos de nuevo. Como te llamas?"

        if intencion == "negacion":
            sesion["estado"] = "fin"
            return respuesta_despedida(sesion["nombre"])

        if intencion == "indecision":
            return (
                "Tomatelo con calma. Cuando quieras explorar otra area, escribe 'si'. "
                "Si ya terminaste, escribe 'no'."
            )

        # Cualquier otra cosa: re-preguntar
        return "Escribe 'si' para explorar otra recomendacion o 'no' para terminar."

    # ------------------------------------------------------------------
    # ESTADO: conversacion
    # Estado principal. Analiza el texto, acumula en memoria, responde.
    # ------------------------------------------------------------------
    if estado == "conversacion":

        # --- Solicitud directa de recomendacion ---
        if intencion == "recomendacion":
            total = sum(sesion["memoria"].values())
            if total < PUNTUACION_MINIMA:
                return (
                    "Todavia no tengo suficiente informacion para darte una buena recomendacion. "
                    "Cuentame un poco mas sobre tus gustos o intereses."
                )
            mensajes = generar_resultado(sesion)
            sesion["mensajes_pendientes"] = mensajes[1:]
            sesion["estado"] = "enviando_resultado"
            return mensajes[0]

        # --- Indecision ---
        if intencion == "indecision":
            sesion["turnos"] += 1
            return respuesta_indecision()

        # --- Intensidad alta: refuerzo positivo en memoria ---
        if intencion == "intensidad_alta":
            # Refuerza todas las areas que ya tienen algo acumulado
            for area in CATEGORIAS_VOCACIONALES:
                if sesion["memoria"][area] > 0:
                    sesion["memoria"][area] *= 1.2
            sesion["turnos"] += 1
            return (
                "Perfecto, esa intensidad en tus intereses es muy util. "
                "Sigue contandome mas sobre lo que te apasiona."
            )

        # --- Intensidad baja: reduccion leve ---
        if intencion == "intensidad_baja":
            sesion["turnos"] += 1
            return (
                "Entendido. Aunque sea un interes pequeño, ayuda a trazar tu perfil. "
                "Hay algo que te llame mas la atencion?"
            )

        # --- Agradecimiento en conversacion ---
        if intencion == "agradecimiento":
            return (
                "Con gusto. Sigamos. "
                "Hay algo mas que quieras contarme sobre tus gustos o habilidades?"
            )

        # --- Deteccion de intereses en el texto ---
        intereses = detectar_intereses(texto_usuario, areas_data)

        if intereses:
            # Acumular en memoria: peso * 1 por cada deteccion
            for area in intereses:
                sesion["memoria"][area] = sesion["memoria"].get(area, 0) + 1

            sesion["turnos"] += 1
            area_dominante = intereses[0]
            respuesta = respuesta_humana(area_dominante)

            # Hacer una pregunta de seguimiento segun el area detectada
            seguimiento = _pregunta_seguimiento(area_dominante, sesion["turnos"])
            respuesta_completa = f"{respuesta}\n\n{seguimiento}"

            # Si ya hay suficiente informacion, lanzar resultado automaticamente
            if hay_suficiente_informacion(sesion):
                mensajes = generar_resultado(sesion)
                sesion["mensajes_pendientes"] = mensajes[1:]
                sesion["estado"] = "enviando_resultado"
                return respuesta_completa + "\n\nCon eso ya tengo suficiente informacion. Aqui esta tu recomendacion:"

            return respuesta_completa

        # --- No se detecto nada reconocible ---
        sesion["turnos"] += 1
        # Evitar que el contador de turnos suba indefinidamente sin datos utiles
        if sesion["turnos"] > 10 and sum(sesion["memoria"].values()) == 0:
            return (
                "Llevamos un rato hablando y aun no tengo claro cuales son tus intereses. "
                "Intentemos algo diferente: de las siguientes opciones, cual te llama mas la atencion?\n\n"
                "1. Matematicas, fisica o tecnologia\n"
                "2. Biologia, quimica o salud\n"
                "3. Derecho, economia o sociedad\n"
                "4. Arte, musica o humanidades\n\n"
                "Solo escribe el numero o el nombre del area."
            )

        return respuesta_fallback()

    # ------------------------------------------------------------------
    # ESTADO: enviando_resultado
    # Hay mensajes en la cola. El siguiente turno los desencola.
    # Este estado no deberia recibir mensajes directamente, pero por
    # si acaso se procesa el mensaje como si fuera conversacion normal.
    # ------------------------------------------------------------------
    if estado == "enviando_resultado":
        if sesion["mensajes_pendientes"]:
            siguiente = sesion["mensajes_pendientes"].pop(0)
            if not sesion["mensajes_pendientes"]:
                sesion["estado"] = "resultado"
            return siguiente
        sesion["estado"] = "resultado"
        return "Escribe 'si' para explorar otra recomendacion o 'no' para terminar."

    # Fallback de estado desconocido (nunca deberia ocurrir)
    sesion["estado"] = "conversacion"
    return respuesta_fallback()


# --------------------------------------------------------------------------
# PREGUNTAS DE SEGUIMIENTO SEGUN AREA
# --------------------------------------------------------------------------

PREGUNTAS_SEGUIMIENTO = {
    "Ciencias Fisico-Matematicas y de las Ingenierias": [
        "Que es lo que mas te gusta de esa area: la teoria matematica, la programacion o el diseno de sistemas?",
        "Te gustaria trabajar mas en desarrollo de software, en ingenieria fisica o en inteligencia artificial?",
        "Prefieres trabajar en proyectos practicos y de construccion o mas en investigacion y teoria?",
        "Hay alguna tecnologia en especifico que te llame la atencion, como robotica, redes o ciencia de datos?"
    ],
    "Ciencias Biologicas Quimicas y de la Salud": [
        "Te atrae mas el contacto directo con pacientes o prefieres el trabajo en laboratorio e investigacion?",
        "Hay alguna rama en especifico que te llame la atencion: medicina, biologia, quimica o nutricion?",
        "Te interesa la salud humana, la salud animal o mas bien el medio ambiente y los ecosistemas?",
        "Prefieres trabajar en hospitales, clinicas, laboratorios o en campo abierto?"
    ],
    "Ciencias Sociales": [
        "Te atrae mas el derecho, la economia, la comunicacion o la psicologia?",
        "Te gustaria trabajar con organizaciones, con individuos o con politicas publicas?",
        "Piensas mas en emprender un negocio, en trabajar en gobierno o en investigacion social?",
        "Hay algun problema social que te preocupe especialmente y que te gustaria atacar desde tu carrera?"
    ],
    "Humanidades y de las Artes": [
        "Te inclinas mas por la expresion artistica, el pensamiento filosofico o el analisis historico y literario?",
        "Te gustaria trabajar en educacion, en medios culturales, en produccion artistica o en investigacion?",
        "Hay algun arte o disciplina en especifico que practiques o te llame mucho la atencion?",
        "Prefieres el trabajo creativo individual o colaborar con equipos en proyectos culturales o artisticos?"
    ]
}

def _pregunta_seguimiento(area, turno):
    """Retorna una pregunta de seguimiento apropiada segun el area y el turno."""
    preguntas = PREGUNTAS_SEGUIMIENTO.get(area, [
        "Hay algo mas que quieras contarme sobre ese interes?",
        "Puedes contarme un poco mas al respecto?",
        "Que otras cosas relacionadas con ese tema te interesan?"
    ])
    return preguntas[turno % len(preguntas)]


# --------------------------------------------------------------------------
# SELECCION DE AREA POR NUMERO (para el menu de emergencia)
# --------------------------------------------------------------------------

AREAS_POR_NUMERO = {
    "1": "Ciencias Fisico-Matematicas y de las Ingenierias",
    "2": "Ciencias Biologicas Quimicas y de la Salud",
    "3": "Ciencias Sociales",
    "4": "Humanidades y de las Artes"
}


# --------------------------------------------------------------------------
# WEBHOOK DE WHATSAPP (Twilio)
# --------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint que recibe mensajes de WhatsApp via Twilio.
    Twilio envia un POST con los campos:
        From    -> numero del usuario (ej: whatsapp:+521234567890)
        Body    -> texto del mensaje
    Y espera una respuesta TwiML con la respuesta del bot.
    """
    user_id  = request.form.get("From", "").strip()
    mensaje  = request.form.get("Body", "").strip()

    if not user_id or not mensaje:
        resp = MessagingResponse()
        resp.message("No pude procesar tu mensaje. Por favor intentalo de nuevo.")
        return Response(str(resp), mimetype="application/xml")

    # Manejar seleccion por numero del menu de emergencia
    if mensaje.strip() in AREAS_POR_NUMERO:
        area_elegida = AREAS_POR_NUMERO[mensaje.strip()]
        sesion = get_sesion(user_id)
        sesion["memoria"][area_elegida] += 5  # puntuacion alta directa
        sesion["turnos"] += TURNOS_PARA_RESULTADO  # forzar resultado en siguiente turno
        respuesta_txt = f"Entendido, te interesa el area de {area_elegida}. Generando tu recomendacion..."
        sesion_mensajes = generar_resultado(sesion)
        sesion["mensajes_pendientes"] = sesion_mensajes[1:]
        sesion["estado"] = "enviando_resultado"
    else:
        respuesta_txt = procesar_mensaje(user_id, mensaje)

    resp = MessagingResponse()
    resp.message(respuesta_txt)
    return Response(str(resp), mimetype="application/xml")


# --------------------------------------------------------------------------
# ENDPOINT DE HEALTH CHECK (para verificar que el servidor esta activo)
# --------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "bot": "Vocabot", "version": "2.0"}, 200


# --------------------------------------------------------------------------
# ENDPOINT DE TEST (para probar sin WhatsApp, via curl o Postman)
# --------------------------------------------------------------------------

@app.route("/test", methods=["POST"])
def test_endpoint():
    """
    Endpoint de prueba. Recibe JSON: {"from": "test_user", "message": "hola"}
    Retorna JSON: {"response": "..."}
    Uso:
        curl -X POST http://localhost:5000/test \
             -H "Content-Type: application/json" \
             -d '{"from": "test_user", "message": "hola"}'
    """
    data    = request.get_json(force=True)
    user_id = data.get("from", "test_user")
    mensaje = data.get("message", "").strip()

    if not mensaje:
        return {"error": "Campo 'message' vacio"}, 400

    respuesta_txt = procesar_mensaje(user_id, mensaje)
    return {"response": respuesta_txt}, 200


# --------------------------------------------------------------------------
# PUNTO DE ENTRADA
# --------------------------------------------------------------------------

if __name__ == "__main__":
    print("="*60)
    print("  Vocabot — Asistente Vocacional IA v2.0")
    print("  Webhook: http://0.0.0.0:5000/webhook")
    print("  Test:    http://0.0.0.0:5000/test")
    print("  Health:  http://0.0.0.0:5000/health")
    print("="*60)
    app.run(host="0.0.0.0", port=5000, debug=False)
