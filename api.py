
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
#                                   API PARA WHATSAPP
# ------------------------------------------------------------------------------------------
# Exposición de endpoints para integrar el asistente vocacional con WhatsApp.
# Gestiona sesiones de usuario para mantener el estado de la conversación.
# ------------------------------------------------------------------------------------------

import os
from flask import Flask, request, jsonify
from core.vocabot import cargar_intenciones, conversar
from core.perceptron import cargar_areas, evaluar, descripcion_area
from core.recomendador import cargar_carreras, recomendar, recomendar_segunda_opcion, link_universidad

app = Flask(__name__)

# Cargar datos al inicio
base_dir = os.path.dirname(os.path.abspath(__file__))
intenciones = cargar_intenciones(os.path.join(base_dir, "data", "intenciones.json"))
areas = cargar_areas(os.path.join(base_dir, "data", "areas.json"))
carreras_data = cargar_carreras(os.path.join(base_dir, "data", "carreras.json"))

# Estado de conversación por usuario (en producción usar Redis o base de datos)
sessions = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe mensajes de WhatsApp (formato JSON)."""
    data = request.get_json()
    user_id = data.get('from')   # número de teléfono o ID de usuario
    message = data.get('message', '').strip()

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    # Obtener o crear sesión
    session = sessions.get(user_id, {})
    if not session:
        session = {"step": "init", "respuestas": {}}

    respuesta_texto = process_message(message, session)
    
    # Guardar sesión actualizada
    sessions[user_id] = session

    return jsonify({"response": respuesta_texto})

def process_message(msg, session):
    """Procesa el mensaje según el paso actual de la conversación."""
    step = session.get("step")
    respuestas = session.get("respuestas", {})

    if step == "init":
        # Enviar primera pregunta
        primer_area = list(intenciones.keys())[0]
        primera_pregunta = intenciones[primer_area][0]
        session["step"] = "collecting"
        session["current_area_index"] = 0
        session["areas_list"] = list(intenciones.keys())
        return primera_pregunta

    elif step == "collecting":
        # Guardar respuesta del área actual
        idx = session.get("current_area_index", 0)
        areas_list = session.get("areas_list", [])
        if idx < len(areas_list):
            area = areas_list[idx]
            respuestas[area] = msg
            session["respuestas"] = respuestas
            session["current_area_index"] = idx + 1

            # Si aún hay más áreas, enviar siguiente pregunta
            if idx + 1 < len(areas_list):
                siguiente_area = areas_list[idx+1]
                pregunta = intenciones[siguiente_area][0]
                return pregunta
            else:
                # Fin de recolección, proceder a recomendación
                area_principal, _, prob, confianza, _ = evaluar(respuestas, areas)
                recomendaciones = recomendar(area_principal, carreras_data)
                segunda_area, segundas_carreras = recomendar_segunda_opcion(prob, carreras_data)

                # Construir mensaje de respuesta
                respuesta = f"Area vocacional recomendada: {area_principal}\n"
                respuesta += f"Descripcion: {descripcion_area(area_principal)}\n"
                respuesta += f"Confianza: {confianza}%\n\n"
                respuesta += "Carreras sugeridas:\n"
                for uni, carreras in recomendaciones.items():
                    respuesta += f"- {uni}: {', '.join(carreras)}\n"
                if segunda_area:
                    respuesta += f"\nOpcion secundaria: {segunda_area}\n"
                    for uni, carreras in segundas_carreras.items():
                        respuesta += f"  {uni}: {', '.join(carreras)}\n"
                respuesta += "\n¿Quieres explorar otra recomendacion? (responde si/no)"
                session["step"] = "waiting_confirmation"
                return respuesta

    elif step == "waiting_confirmation":
        if "si" in msg.lower():
            # Reiniciar proceso
            session["step"] = "init"
            session["respuestas"] = {}
            session["current_area_index"] = 0
            return "Reiniciando el cuestionario. Responde las siguientes preguntas:"
        else:
            return "Gracias por usar el asistente vocacional. !Mucho exito en tu futuro academico!"

    return "Lo siento, no entendi. Por favor responde si o no."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)