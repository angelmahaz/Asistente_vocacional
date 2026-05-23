
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
import re

def cargar_intenciones(ruta):
    """Carga el archivo JSON de intenciones.
    Retorna un diccionario con las preguntas y sus etiquetas."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def iniciar_chat():
    """Mensaje de bienvenida (solo para consola). Para API no se usa."""
    print("\n--- ASISTENTE VOCACIONAL IA (versión texto) ---")
    print("Responde las siguientes preguntas para ayudarte a elegir una carrera.\n")

def conversar(intenciones, respuestas=None):
    """
    Realiza una conversación iterativa con el usuario.
    - intenciones: diccionario con preguntas agrupadas por área.
    - respuestas: diccionario opcional para continuar una conversación previa.
    Retorna un diccionario con las respuestas del usuario para cada área.
    """
    if respuestas is None:
        respuestas = {}

    for area, preguntas in intenciones.items():
        if area in respuestas:
            continue   # ya respondió esta área
        for pregunta in preguntas:
            print(f"\n{pregunta}")
            user_input = input("> ").strip()
            # Podríamos hacer un análisis simple de polaridad (positivo/negativo)
            # por ahora guardamos la respuesta textual
            respuestas[area] = user_input
            break   # una sola pregunta por área
    return respuestas