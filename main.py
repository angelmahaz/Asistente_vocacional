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
    normalizar_texto,
)

from core.perceptron import cargar_areas, evaluar, explicar_recomendacion, descripcion_arquitectura
from core.recomendador import cargar_carreras, recomendar, obtener_enlaces_oficiales


#=======================================================================================================
#                                         *** Funciones ***
#=======================================================================================================

def mostrar_bienvenida_terminal():
    banner = r"""
 VV     VV  OOOOO   CCCCC   AAAAA   BBBB    OOOOO   TTTTTTT
 VV     VV OO   OO CC      AA   AA  BB  BB OO   OO    TTT
  VV    VV OO   OO CC      AAAAAAA  BBBB   OO   OO    TTT
  VV   VV  OO   OO CC      AA   AA  BB  BB OO   OO    TTT
   VVVVV    OOOOO   CCCCC  AA   AA  BBBB    OOOOO     TTT

                 V O C A B O T
"""
    print(banner)
    print("Vocabot: asistente vocacional conversacional.")
    print("Vocabot: Puedes escribir materias, hobbies, gustos, intereses o ideas sobre lo que te gustaría estudiar.")
    print("Vocabot: También puedes responder con si, no, mucho, poco, más o menos, tal vez o no sé.")
    print("Vocabot: Escribe 'salir' para terminar o 'ayuda' para ver estas instrucciones otra vez.")
    print("Vocabot: Este bot es solo de apoyo y no sustituye la orientación vocacional profesional.")
    print()


def mostrar_ayuda_terminal():
    print("Vocabot: Puedes hablarme de materias, hobbies, gustos, música, tecnología, lectura o cualquier interés que tengas.")
    print("Vocabot: Responde con si, no, mucho, poco, más o menos, tal vez o no sé cuando te haga preguntas.")
    print("Vocabot: Si quieres una nueva recomendación, puedes decírmelo en cualquier momento.")
    print("Vocabot: Escribe 'salir' para terminar.")
    print("Vocabot: Recuerda que esto es solo un apoyo; no reemplaza la orientación vocacional profesional.")
    print()


# Función principal
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
        'tecnologia':  {'matematicas': 1.25},
        'salud':       {'salud': 1.20},
        'social':      {'salud': 0.35, 'humanidades': 0.65},
        'lectura':     {'humanidades': 0.90},
        'arte':        {'arte': 1.20},
        'naturaleza':  {'salud': 0.55, 'matematicas': 0.20},
        'negocios':    {'humanidades': 0.85},
        'manual':      {'arte': 0.25, 'matematicas': 0.20},
    }

    mostrar_bienvenida_terminal()

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

    def repetir_pregunta_actual():
        if pregunta_actual:
            texto = pregunta_actual.get('texto', '')
            if texto:
                print(f'Vocabot: {texto}')
                return True
        return False

    def aplicar_respuesta_pregunta(pregunta_id, valor):
        factor = max(0.0, min(1.0, (float(valor) - 1.0) / 4.0))
        for categoria, peso in mapa_preguntas.get(pregunta_id, {}).items():
            if categoria in memoria:
                memoria[categoria] += factor * float(peso)

    def reiniciar_ciclo_vocacional():
        nonlocal memoria, turnos, estado, indice_pregunta, pregunta_actual, ultima_area
        memoria = {'matematicas': 0.0, 'salud': 0.0, 'humanidades': 0.0, 'arte': 0.0}
        turnos = 0
        estado = 'charla'
        indice_pregunta = 0
        pregunta_actual = None
        ultima_area = None

    def mostrar_carreras(area):
        """Muestra carreras y enlaces oficiales."""
        carreras = recomendar(area, carreras_data, max_por_uni=5)
        if not carreras:
            print('Vocabot: No encontre carreras registradas para esa area por ahora.')
            return

        print(f'Vocabot: Carreras de ejemplo en el area de {area}:')
        for uni, lista in carreras.items():
            print(f'Vocabot: -- {uni} --')
            if lista:
                for c in lista:
                    print(f'Vocabot:   * {c}')
            else:
                print('Vocabot:   * Sin carreras registradas por ahora.')

        enlaces = obtener_enlaces_oficiales()
        if enlaces:
            print('Vocabot: Puedes revisar la oferta educativa oficial en:')
            for uni, url in enlaces.items():
                print(f'Vocabot:   {uni}: {url}')

    def resultado():
        nonlocal estado, pregunta_actual, ultima_area

        if sum(memoria.values()) == 0:
            estado = 'charla'
            print('Vocabot: Aun no tengo suficiente informacion para recomendarte con seguridad.')
            if not preguntar_guiada():
                print('Vocabot: Cuentame un poco mas sobre lo que te gusta.')
            return

        capas = descripcion_arquitectura()
        print(f'Vocabot: Analizando tus respuestas con la red neuronal ({len(capas)} capas)...')

        area, _, prob = evaluar(memoria, areas)
        ultima_area = area

        print('Vocabot: Resultado del analisis de la red neuronal:')
        for a, p in sorted(prob.items(), key=lambda x: x[1], reverse=True):
            barra = '|' * int(p * 20)
            print(f'Vocabot:   {a}: {barra} {p:.0%}')

        if area:
            if nombre:
                print(f'Vocabot: {nombre}, la red neuronal identifica que tu perfil encaja mejor con el area de:')
            else:
                print('Vocabot: La red neuronal identifica que tu perfil encaja mejor con el area de:')
            print(f'Vocabot:   >> {area} <<')

            top = explicar_recomendacion(memoria, areas, area)
            if top:
                print(f'Vocabot: Las caracteristicas que mas influyeron en la red neuronal fueron: {", ".join(top)}.')

            print()
            print('Vocabot: Tengo algunas opciones de carreras que te pueden interesar.')
            print('Vocabot: ¿Quieres que te las muestre?')
            estado = 'ofreciendo_carreras'
        else:
            print('Vocabot: No pude calcular una recomendacion con los datos actuales.')
            print('Vocabot: ¿Quieres contarme un poco mas sobre tus intereses?')
            estado = 'charla'

        pregunta_actual = None

    print('\nVocabot: Hola, soy Vocabot.')
    print('Vocabot: Cuentame cuales son tus gustos o en que eres bueno.')
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

        if normalizar_texto(texto_original) in {'ayuda', 'help', 'instrucciones', 'como funciona'}:
            mostrar_ayuda_terminal()
            continue

        if es_despedida(texto, intenciones):
            print('Vocabot: Fue un gusto ayudarte. Mucho exito en lo que decidas.')
            break

        nombre_detectado = extraer_nombre(texto_original)
        if nombre_detectado:
            nombre = nombre_detectado
            texto_sin_nombre = limpiar_mensaje_nombre(texto_original)

            if not tiene_contenido_relevante(texto_sin_nombre):
                print(f'Vocabot: Mucho gusto, {nombre}.')
                print('Vocabot: Cuentame cuales son tus gustos.')
                continue

            print(f'Vocabot: Mucho gusto, {nombre}.')
            texto_original = texto_sin_nombre

        if detectar_recomendacion(texto_original, intenciones):
            resultado()
            continue

        if estado == 'ofreciendo_carreras':
            respuesta = interpretar_respuesta_binaria(texto_original)

            if respuesta is True:
                print(f'Vocabot: Aqui estan las carreras del area de {ultima_area}:')
                print()
                mostrar_carreras(ultima_area)
                print()
                print('Vocabot: ¿Te gustaria explorar otras recomendaciones? (si / no)')
                estado = 'post'

            elif respuesta is False:
                print('Vocabot: No hay problema. ¿Te gustaria explorar otras recomendaciones? (si / no)')
                estado = 'post'

            else:
                print('Vocabot: Solo dime si quieres ver las carreras o no.')
                print('Vocabot: ¿Quieres que te muestre las carreras disponibles? (si / no)')

            continue

        if estado == 'post':
            respuesta = interpretar_respuesta_binaria(texto_original)

            if respuesta is True:
                print('Vocabot: Perfecto. Empecemos de nuevo.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuentame nuevamente sobre tus intereses.')

            elif respuesta is False:
                print('Vocabot: Entendido.')
                print('Vocabot: ¿Deseas finalizar el programa? (si / no)')
                estado = 'confirmar'

            else:
                print('Vocabot: Puedes responder con "si" para explorar otra area o "no" para terminar.')

            continue

        if estado == 'confirmar':
            respuesta = interpretar_respuesta_binaria(texto_original)

            if respuesta is True:
                print('Vocabot: Gracias por usar el asistente. Mucho exito en lo que decidas.')
                break

            elif respuesta is False:
                print('Vocabot: Perfecto, sigamos entonces.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuentame sobre tus intereses.')

            else:
                print('Vocabot: Responde con "si" para salir o "no" para continuar.')

            continue

        if estado == 'pregunta':
            valor = interpretar_respuesta_escala(texto_original)

            if valor is None:
                print('Vocabot: No comprendi bien.')
                if not repetir_pregunta_actual():
                    print('Vocabot: Puedes responder con mucho, poco, mas o menos, bastante o nada.')
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

            print(f'Vocabot: {respuesta_humana(categoria, texto_limpio)}')

            if sum(memoria.values()) < 2 and indice_pregunta < len(preguntas):
                preguntar_guiada()
            elif nombre and turnos % 2 == 0:
                print(f'Vocabot: {nombre}, cuentame un poco mas de eso.')
        else:
            print(f'Vocabot: {respuesta_no_entendida()}')
            if sum(memoria.values()) < 2:
                if not preguntar_guiada():
                    print('Vocabot: Puedes hablarme de materias, hobbies o lo que mas disfrutas hacer.')

        turnos += 1

        if turnos >= 3 and sum(memoria.values()) > 0 and estado == 'charla':
            resultado()
        elif sum(memoria.values()) >= 2 and estado == 'charla':
            resultado()


if __name__ == '__main__':
    main()