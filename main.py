
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

from core.chatbot import (
    cargar_intenciones,
    detectar_intereses,
    puntuar_intereses,
    detectar_recomendacion,
    extraer_nombre,
    limpiar_mensaje_nombre,
    tiene_contenido_relevante,
    respuesta_humana,
    respuesta_general,
    respuesta_no_entendida,
    es_despedida,
    es_saludo,
    interpretar_respuesta_escala,
    interpretar_respuesta_binaria,
    cargar_preguntas,
)

from core.perceptron import cargar_areas, evaluar, explicar_recomendacion
from core.recomendador import cargar_carreras, recomendar


#=======================================================================================================
#                                         *** Funciones ***
#=======================================================================================================


#_______________________________________________________________________________________________________

# Función principal
#   Inicializa el entorno de ejecución, carga la base de conocimientos en formato JSON, 
#   establece el estado inicial de la sesión y define la matriz de pesos 

def main():
    intenciones = cargar_intenciones('data/intenciones.json')
    areas = cargar_areas('data/areas.json')
    carreras_data = cargar_carreras('data/carreras.json')
    preguntas = cargar_preguntas('data/preguntas.json')

    nombre = None
    memoria = {'matematicas': 0.0, 'salud': 0.0, 'humanidades': 0.0, 'arte': 0.0}
    turnos = 0
    estado = 'charla'
    indice_pregunta = 0
    pregunta_actual = None
    ultima_area = None

    mapa_preguntas = {
        'matematicas': {'matematicas': 1.15},
        'lectura': {'humanidades': 0.45},
        'manual': {'arte': 0.25, 'matematicas': 0.20},
        'social': {'salud': 0.35, 'humanidades': 0.15},
        'tecnologia': {'matematicas': 1.25},
    }

#_______________________________________________________________________________________________________


# Función de despliegue de preguntas
#   Gestiona de manera secuencial la asignación y el despliegue de las preguntas del test vocacional, 
#   actualizando la máquina de estados del chatbot mientras queden reactivos disponibles.

    def preguntar_guiada():
        nonlocal estado, indice_pregunta, pregunta_actual
        if indice_pregunta < len(preguntas):
            pregunta_actual = preguntas[indice_pregunta]
            indice_pregunta += 1
            estado = 'pregunta'
            texto = pregunta_actual.get('texto', '')
            if texto:
                print(f'Vocabot: {texto}')
                return True
        return False


#_______________________________________________________________________________________________________

# Función Repetir la pregunta
#   Reenvía y vuelve a imprimir en consola el texto del reactivo vigente en ese momento, útil cuando 
#   el usuario introduce una respuesta inválida, solicita una aclaración o activa una pausa.


    def repetir_pregunta_actual():
        if pregunta_actual:
            texto = pregunta_actual.get('texto', '')
            if texto:
                print(f'Vocabot: {texto}')
                return True
        return False


#_______________________________________________________________________________________________________

# Función para calcular la respuesta
#   Calcula el impacto cuantitativo de la respuesta del usuario sobre su perfil vocacional, normalizando
#   la puntuación recibida a una escala de 0.0 a 1.0 y aplicando los coeficientes ponderados a la memoria
#   de aptitudes.

    def aplicar_respuesta_pregunta(pregunta_id, valor):
        factor = max(0.0, min(1.0, (float(valor) - 1.0) / 4.0))
        for categoria, peso in mapa_preguntas.get(pregunta_id, {}).items():
            if categoria in memoria:
                memoria[categoria] += factor * float(peso)


#_______________________________________________________________________________________________________


# Función que reinicia la memoria
#   Restablece todas las variables de control, puntuaciones vocacionales y estados de la sesión, 
#   permitiendo al usuario volver a iniciar el test y la interacción desde cero sin necesidad de 
#   reiniciar la ejecución del programa.

    def reiniciar_ciclo_vocacional():
        nonlocal memoria, turnos, estado, indice_pregunta, pregunta_actual, ultima_area
        memoria = {'matematicas': 0.0, 'salud': 0.0, 'humanidades': 0.0, 'arte': 0.0}
        turnos = 0
        estado = 'charla'
        indice_pregunta = 0
        pregunta_actual = None
        ultima_area = None


#_______________________________________________________________________________________________________


# Función que despliega las recomendaciones de las áreas
#   Procesa y despliega las recomendaciones de áreas de estudio y carreras universitarias,o solicita 
#   más datos al usuario si la información recopilada en memoria es insuficiente.

    def resultado():
        nonlocal estado, pregunta_actual, ultima_area
        if sum(memoria.values()) == 0:
            estado = 'charla'
            print('Vocabot: Aun no tengo suficiente informacion para recomendarte con seguridad.')
            if not preguntar_guiada():
                print('Vocabot: Cuentame un poco mas sobre lo que te gusta.')
            return

        estado = 'post'
        area, _, prob = evaluar(memoria, areas)
        ultima_area = area

        print('Vocabot: Estoy analizando tus respuestas con IA...')
        for a, p in sorted(prob.items(), key=lambda x: x[1], reverse=True):
            print(f'Vocabot: {a}: {p:.2f}')

        if area:
            if nombre:
                print(f'Vocabot: {nombre}, te recomiendo el area de {area}.')
            else:
                print(f'Vocabot: Te recomiendo el area de {area}.')

            top = explicar_recomendacion(memoria, areas, area)
            if top:
                print(f'Vocabot: Tome en cuenta principalmente: {", ".join(top)}.')

            carreras = recomendar(area, carreras_data)
            if not carreras:
                print('Vocabot: No encontre carreras disponibles por ahora.')
            else:
                print('Vocabot: Carreras sugeridas:')
                for uni, lista in carreras.items():
                    print(f'Vocabot: {uni}:')
                    if lista:
                        for c in lista:
                            print(f'Vocabot: - {c}')
                    else:
                        print('Vocabot: - Sin carreras registradas por ahora')
        else:
            print('Vocabot: No pude calcular una recomendacion por ahora.')

        print('Vocabot: ¿Te gustaria explorar otras recomendaciones?')
        pregunta_actual = None

    print('\nVocabot: Hola, soy Vocabot.')
    print('Vocabot: Cuéntame cuales son tus gustos o en que eres bueno.')
    print("Vocabot: Escribe 'salir' para terminar.\n")

    while True:
        try:
            texto = input('Tú: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nVocabot: Fue un gusto ayudarte.')
            break

        if not texto:
            continue

        texto_original = texto

        if es_despedida(texto, intenciones):
            print('Vocabot: Fue un gusto ayudarte.')
            break

        nombre_detectado = extraer_nombre(texto_original)
        if nombre_detectado:
            nombre = nombre_detectado
            texto_sin_nombre = limpiar_mensaje_nombre(texto_original)

            if not tiene_contenido_relevante(texto_sin_nombre):
                print(f'Vocabot: Mucho gusto, {nombre}.')
                print('Vocabot: Cuéntame cuales son tus gustos.')
                continue

            print(f'Vocabot: Mucho gusto, {nombre}.')
            texto_original = texto_sin_nombre

        if detectar_recomendacion(texto_original, intenciones):
            resultado()
            continue

        if estado == 'post':
            respuesta = interpretar_respuesta_binaria(texto_original)

            if respuesta is True:
                print('Vocabot: Perfecto. Empecemos de nuevo.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuéntame nuevamente sobre tus intereses.')
                continue

            if respuesta is False:
                print('Vocabot: Creo que no comprendí bien. ¿Quieres finalizar el programa?')
                estado = 'confirmar'
                continue

            print('Vocabot: Creo que no comprendí bien. ¿Quieres explorar otras recomendaciones?')
            continue

        if estado == 'confirmar':
            respuesta = interpretar_respuesta_binaria(texto_original)

            if respuesta is True:
                print('Vocabot: Gracias por usar el asistente.')
                break

            if respuesta is False:
                print('Vocabot: Perfecto. Sigamos entonces.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuéntame sobre tus intereses.')
                continue

            print('Vocabot: Creo que no comprendí bien. ¿Quieres finalizar el programa?')
            continue

        if estado == 'pregunta':
            valor = interpretar_respuesta_escala(texto_original)

            if valor is None:
                print('Vocabot: Creo que no comprendí bien.')
                if not repetir_pregunta_actual():
                    print('Vocabot: Puedes responder con mucho, poco, mas o menos o nada.')
                continue

            pregunta_id = (pregunta_actual or {}).get('id', '')
            aplicar_respuesta_pregunta(pregunta_id, valor)

            if valor >= 4:
                print('Vocabot: Entendido, parece que te interesa bastante.')
            elif valor == 3:
                print('Vocabot: Entendido, veo un interes moderado.')
            else:
                print('Vocabot: Entendido, veo poco interes en eso.')

            estado = 'charla'
            pregunta_actual = None

            if sum(memoria.values()) < 2 and indice_pregunta < len(preguntas):
                preguntar_guiada()

            continue

        if es_saludo(texto_original, intenciones) and not detectar_intereses(texto_original, intenciones):
            print('Vocabot: Hola, soy Vocabot, dime cuales son tus gustos.')
            continue

        texto_limpio = limpiar_mensaje_nombre(texto_original)
        contribuciones = puntuar_intereses(texto_limpio, intenciones)

        if contribuciones:
            categoria = max(contribuciones, key=contribuciones.get)
            for area, peso in contribuciones.items():
                if area in memoria:
                    memoria[area] += float(peso)

            print(f'Vocabot: {respuesta_humana(categoria)}')

            if nombre and turnos % 2 == 0:
                print(f'Vocabot: {nombre}, cuentame un poco mas de eso.')
        else:
            print(f'Vocabot: {respuesta_no_entendida()}')
            if sum(memoria.values()) < 2:
                if not preguntar_guiada():
                    print('Vocabot: Puedes hablarme de materias, hobbies o lo que mas disfrutas hacer.')

        turnos += 1

        if turnos >= 5 and sum(memoria.values()) > 0 and estado == 'charla':
            resultado()

#_______________________________________________________________________________________________________


if __name__ == '__main__':
    main()