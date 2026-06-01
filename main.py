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

import random
import re

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
    normalizar_texto,
    interpretar_respuesta_escala,
    interpretar_respuesta_binaria,
    cargar_preguntas,
    reiniciar_rotacion_respuestas,
    es_peticion_ayuda,
    respuesta_ayuda_empatica,
    es_expresion_confusion,
    respuesta_confusion,
    es_expresion_frustracion,
    respuesta_frustracion,
    es_groseria,
    respuesta_groseria,
    generar_resumen_memoria,
    pregunta_seguimiento,
)

from core.perceptron import cargar_areas, evaluar, explicar_recomendacion, descripcion_arquitectura
from core.recomendador import cargar_carreras, recomendar, obtener_enlaces_oficiales


#=======================================================================================================
#                                         *** Funciones ***
#=======================================================================================================

def mostrar_bienvenida_terminal():
    banner = r"""
    VV     VV  OOOOO   CCCCC   AAAAA   BBBB     OOOOO   TTTTTTTT
    VV     VV OO   OO CC      AA   AA  BB  BB  OO   OO    TTT
    VV    VV OO   OO CC      AAAAAAA  BBBB    OO   OO    TTT
    VV   VV  OO   OO CC      AA   AA  BB  BB  OO   OO    TTT
    VVVVV    OOOOO   CCCCC  AA   AA  BBBB     OOOOO     TTT
"""
    print(banner)
    print("Vocabot: Hola, soy un asistente vocacional que usa inteligencia artificial para ayudarte a")
    print("         identificar qué área de estudios universitarios va mejor con tu perfil académico.\n")
    print("Vocabot: Solo cuéntame sobre tus gustos, hobbies e intereses y yo analizo la información.\n")
    print("Vocabot: Responde con si, no, mucho, poco, más o menos, tal vez o no sé cuando te haga algunas preguntas.\n")
    print("Vocabot: Si quieres una nueva recomendación, puedes decírmelo en cualquier momento.\n")
    print("Vocabot: Escribe 'ayuda' para orientarte si no sabes por donde empezar")
    print("Vocabot: Escribe 'salir' para terminar.\n")
    print("Vocabot: *** Recuerda que soy una inteligencia artificial y la información proporcionada no reemplaza")
    print("                                 la orientación vocacional profesional.                           ***")


def mostrar_ayuda_terminal():

    print("Vocabot: Hola, soy un asistente vocacional que usa inteligencia artificial para ayudarte a")
    print("         identificar qué área de estudios universitarios va mejor con tu perfil académico.\n")
    print("Vocabot: Solo cuéntame sobre tus gustos, hobbies e intereses y yo analizo la información.\n")
    print("Vocabot: Responde con si, no, mucho, poco, más o menos, tal vez o no sé cuando te haga algunas preguntas.\n")
    print("Vocabot: Si quieres una nueva recomendación, puedes decírmelo en cualquier momento.\n")
    print("Vocabot: Escribe 'ayuda' para orientarte si no sabes por donde empezar")
    print("Vocabot: Escribe 'salir' para terminar.\n")
    print("Vocabot: *** Recuerda que soy una inteligencia artificial y la información proporcionada no reemplaza")
    print("                                 la orientación vocacional profesional.                           ***")

# Menú de ayuda interactiva
MENU_AYUDA = [
    "1. ¿Cómo funciona Vocabot?",
    "2. ¿Qué áreas de conocimiento existen?",
    "3. ¿Cómo se calcula mi recomendación?",
    "4. Quiero empezar de nuevo.",
    "5. Continuar la conversación.",
]

def mostrar_menu_ayuda():
    print("\nVocabot: ¿Sobre qué quieres saber? Escribe el número con la opción que quieras saber:")
    for opcion in MENU_AYUDA:
        print(f"Vocabot:   {opcion}")


def manejar_opcion_menu_ayuda(opcion_texto: str) -> str:
    """
    Recibe el texto del usuario y retorna la opción elegida (1-5) o None.
    Acepta el número solo o parte del texto de la opción.
    """
    norm = normalizar_texto(opcion_texto)

    def tiene_numero(n):
        return re.search(rf"\b{n}\b", norm) is not None

    if tiene_numero("1") or "como funciona" in norm or "funciona" in norm:
        return "1"
    if tiene_numero("2") or "areas" in norm or "área" in norm or "conocimiento" in norm:
        return "2"
    if tiene_numero("3") or "calcula" in norm or "neuronal" in norm or "recomendacion" in norm:
        return "3"
    if tiene_numero("4") or "empezar desde el principio" in norm or "reiniciar" in norm or "nuevo" in norm:
        return "4"
    if tiene_numero("5") or "continuar" in norm or "seguir" in norm or "sigue" in norm:
        return "5"
    return None


def responder_opcion_ayuda(opcion: str):
    """Imprime la respuesta completa para cada opción del menú.
        Retorna:
            'reiniciar' si se eligió la opción 4,
            'salir_menu' si se eligió la opción 5,
            None para las demás (permanecer en el menú).
    """
    if opcion == "1":
        print("Vocabot: Vocabot es un asistente vocacional que usa inteligencia artificial para ayudarte")
        print("Vocabot: a identificar qué área de estudios universitarios va mejor con tu perfil.")
        print("Vocabot: Solo cuéntame sobre tus gustos, hobbies e intereses y yo analizo la información.")
        print("Vocabot: La red neuronal procesa todo y calcula las probabilidades de afinidad con cada área.")
        return None
    
    elif opcion == "2":
        print("Vocabot: Existen 4 áreas de conocimiento en las que te puedo orientar:\n")
        print("Vocabot:   Área 1 — Ciencias Físico-Matemáticas y de las Ingenierías:")
        print("Vocabot:            (matemáticas, física, programación, ingeniería, tecnología)\n")

        print("Vocabot:   Área 2 — Ciencias Biológicas, Químicas y de la Salud")
        print("Vocabot:            (medicina, biología, química, enfermería, nutrición)\n")

        print("Vocabot:   Área 3 — Ciencias Sociales")
        print("Vocabot:            (derecho, economía, administración, comunicación, psicología)\n")

        print("Vocabot:   Área 4 — Humanidades y de las Artes")
        print("Vocabot:            (filosofía, historia, literatura, música, diseño, arte)\n")

        print("Vocabot: Las carreras que puedo mostrarte son de la UNAM, IPN y UAM.")
        return None
    
    elif opcion == "3":
        print("Vocabot: Uso una red neuronal con varias capas internas que procesan tus gustos y los comparan con las áreas de estudio.")
        print("Vocabot: Cada capa refina la coincidencia, y entre más información me des, más precisa es la recomendación.")
        return None
        

    elif opcion == "4":
        return "salir_menu"
    return None


#=======================================================================================================
#                                      *** Funcion principal ***
#=======================================================================================================

def main():
    intenciones   = cargar_intenciones('data/intenciones.json')
    areas         = cargar_areas('data/areas.json')
    carreras_data = cargar_carreras('data/carreras.json')
    preguntas = cargar_preguntas('data/preguntas.json')
    random.shuffle(preguntas)   # Esto reordena las preguntas aleatoriamente

    nombre             = None
    memoria            = {'matematicas': 0.0, 'salud': 0.0, 'humanidades': 0.0, 'arte': 0.0}
    turnos             = 0
    estado             = 'charla'
    indice_pregunta    = 0
    pregunta_actual    = None
    ultima_area        = None
    reintentos_pregunta = 0

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
        'biologia_animales': {'salud': 1.10},
        'plantas_ecosistemas': {'salud': 1.05},
        'laboratorio': {'salud': 1.00, 'matematicas': 0.25},
        'equipo': {'humanidades': 0.45, 'salud': 0.25},
        'comunicacion': {'humanidades': 1.00},
        'creatividad_visual': {'arte': 1.10},
        'musica': {'arte': 1.05},
        'emprendimiento': {'humanidades': 0.75},
        'investigacion': {'matematicas': 0.35, 'salud': 0.35, 'humanidades': 0.35},
        'servicio_social': {'salud': 0.65, 'humanidades': 0.35},

        'deportes': {'salud': 0.90, 'humanidades': 0.10},
        'investigacion_cientifica': {'matematicas': 0.45, 'salud': 0.45, 'humanidades': 0.10},
        'lectura_profundidad': {'humanidades': 1.00},
        'liderazgo': {'humanidades': 0.80, 'salud': 0.20},
        'arte_visual': {'arte': 1.00},
        'musica_creativa': {'arte': 1.00},
        'naturaleza_ecologia': {'salud': 0.80, 'humanidades': 0.20},
        'emprendimiento_propio': {'humanidades': 0.70, 'matematicas': 0.10},
        'tecnologia_videojuegos': {'matematicas': 0.90, 'arte': 0.20},
        'servicio_personas': {'salud': 0.80, 'humanidades': 0.30},
        'viajes_culturas': {'humanidades': 0.80, 'arte': 0.10},
        'ciencia_aplicada': {'matematicas': 0.55, 'salud': 0.25, 'humanidades': 0.10},
    }

    mostrar_bienvenida_terminal()

    # ── Funciones auxiliares internas ───────────────────────────────────

    def preguntar_guiada():
        nonlocal estado, indice_pregunta, pregunta_actual, reintentos_pregunta
        if indice_pregunta < len(preguntas):
            pregunta_actual = preguntas[indice_pregunta]
            indice_pregunta += 1
            estado = 'pregunta'
            reintentos_pregunta = 0
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
        nonlocal memoria, turnos, estado, indice_pregunta, pregunta_actual, ultima_area, preguntas, reintentos_pregunta
        random.shuffle(preguntas)   # Nuevo orden para el nuevo ciclo
        reiniciar_rotacion_respuestas()
        memoria         = {'matematicas': 0.0, 'salud': 0.0, 'humanidades': 0.0, 'arte': 0.0}
        turnos          = 0
        estado          = 'charla'
        indice_pregunta = 0
        pregunta_actual = None
        ultima_area     = None
        reintentos_pregunta = 0

    def mostrar_carreras(area):
        carreras = recomendar(area, carreras_data, max_por_uni=5)
        if not carreras:
            print('Vocabot: No encontré carreras registradas para esa área por ahora.')
            return
        print(f'Vocabot: Carreras de ejemplo en el área de {area}:')
        for uni, lista in carreras.items():
            print(f'Vocabot: -- {uni} --')
            if lista:
                for c in lista:
                    print(f'Vocabot:   * {c}')
                if len(lista) == 5:
                    print('Vocabot:   ... y más opciones en la página oficial')
            else:
                print('Vocabot:   * Sin carreras registradas por ahora.')
            print()  # Salto de línea después de cada universidad
        enlaces = obtener_enlaces_oficiales()
        if enlaces:
            print('Vocabot: Puedes revisar la oferta educativa oficial en:')
            for uni, url in enlaces.items():
                print(f'Vocabot:   {uni}: {url}')
            print()  # Salto de línea después de los enlaces

    def resultado():
        nonlocal estado, pregunta_actual, ultima_area

        if sum(memoria.values()) == 0:
            estado = 'charla'
            print('Vocabot: Aún no tengo suficiente información para recomendarte con seguridad.')
            if not preguntar_guiada():
                print('Vocabot: Cuéntame un poco más sobre lo que te gusta.')
            return

        area, _, prob = evaluar(memoria, areas)
        ultima_area = area

        print()  # Salto de línea antes de mostrar resultados
        print('Vocabot: Analizando tus respuestas con IA...\n')
        for a, p in sorted(prob.items(), key=lambda x: x[1], reverse=True):
            barra = '|' * int(p * 20)
            print(f'Vocabot: {a}: {barra} {p:.0%}')
            print()  # Salto de línea entre áreas

        if area:
            if nombre:
                print(f'Vocabot: {nombre}, he analizado tus respuestas y el área que mejor se ajusta a tu perfil es:')
            else:
                print('Vocabot: He analizado tus respuestas y el área que mejor se ajusta a tu perfil es:')
            print(f'Vocabot:   >> {area} <<\n')

            top = explicar_recomendacion(memoria, areas, area)
            if top:
                print(f'Vocabot: Las características que más influyeron fueron: {", ".join(top)}.\n')

            print('Vocabot: Tengo algunas opciones de carreras que te pueden interesar.')
            print('Vocabot: ¿Quieres que te las muestre?')
            estado = 'ofreciendo_carreras'
        else:
            print('Vocabot: No pude calcular una recomendación con los datos actuales.')
            print('Vocabot: ¿Quieres contarme un poco más sobre tus intereses?')
            estado = 'charla'

        pregunta_actual = None

    def mostrar_resumen_final():
        """Muestra un resumen de lo que el bot aprendió antes de despedirse."""
        resumen = generar_resumen_memoria(memoria, nombre)
        print(f'Vocabot: {resumen}')
        print('Vocabot: Gracias por usar el asistente. ¡Mucho éxito en lo que decidas!')

    # ── Inicio de la conversación ───────────────────────────────────────

    print('\nVocabot: Hola, soy Vocabot.')
    print('Vocabot: Cuéntame cuáles son tus gustos, en qué eres bueno, o que materias te gustan para poder orientarte.\n')

    # ====================================================================
    # CICLO PRINCIPAL
    # ====================================================================

    while True:
        try:
            print()  # Salto de línea antes de la entrada del usuario
            texto = input('Tú: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nVocabot: Fue un gusto ayudarte.')
            mostrar_resumen_final()
            break

        if not texto:
            continue

        texto_original = texto

        # ── GUARDIA GLOBAL 1: Groserías ────────────────────────────────
        # Se evalúa antes que cualquier estado para que nunca rompa.
        if es_groseria(texto_original, intenciones):
            print(f'Vocabot: {respuesta_groseria()}')
            continue

        # ── GUARDIA GLOBAL 2: Despedida ────────────────────────────────
        if es_despedida(texto, intenciones):
            mostrar_resumen_final()
            break

        # ── GUARDIA GLOBAL 3: Petición de ayuda interactiva ───────────
        # Solo se dispara en estados donde tiene sentido (no en menú de ayuda mismo).
        if estado != 'ayuda_menu' and es_peticion_ayuda(texto_original, intenciones):
            print(f'Vocabot: {respuesta_ayuda_empatica(nombre)}')
            mostrar_menu_ayuda()
            estado = 'ayuda_menu'
            continue

        # ── GUARDIA GLOBAL 4: Comando de ayuda rápida ─────────────────
        if normalizar_texto(texto_original) in {'ayuda', 'help', 'instrucciones', 'como funciona'}:
            mostrar_ayuda_terminal()
            continue

        # ── Detectar nombre ────────────────────────────────────────────
        nombre_detectado = extraer_nombre(texto_original)
        if nombre_detectado:
            nombre           = nombre_detectado
            texto_sin_nombre = limpiar_mensaje_nombre(texto_original)
            if not tiene_contenido_relevante(texto_sin_nombre):
                print(f'Vocabot: Mucho gusto, {nombre}.')
                print('Vocabot: Cuéntame cuáles son tus gustos.')
                continue
            print(f'Vocabot: Mucho gusto, {nombre}.')
            texto_original = texto_sin_nombre

        # ── Recomendación explícita ────────────────────────────────────
        if detectar_recomendacion(texto_original, intenciones):
            resultado()
            continue

        # ==============================================================
        # ESTADO: ayuda_menu
        # El usuario eligió ver el menú de ayuda detallada.
        # ==============================================================
        # ==============================================================
        # ESTADO: ayuda_menu
        # El usuario eligió ver el menú de ayuda detallada.
        # ==============================================================
        if estado == 'ayuda_menu':
            opcion = manejar_opcion_menu_ayuda(texto_original)
            if opcion:
                accion = responder_opcion_ayuda(opcion)
                if accion == "reiniciar":
                    reiniciar_ciclo_vocacional()
                    print('Vocabot: Perfecto. Empecemos de nuevo. Cuéntame sobre tus intereses.')
                    estado = 'charla'
                elif accion == "salir_menu":
                    print('Vocabot: Perfecto, sigamos donde estábamos. Cuéntame más sobre tus gustos.')
                    estado = 'charla'
                else:
                    mostrar_menu_ayuda()
            else:
                print('Vocabot: No entendí la opción. Elige un número del 1 al 5.')
                mostrar_menu_ayuda()
            continue

        # ==============================================================
        # ESTADO: ofreciendo_carreras
        # ==============================================================
        if estado == 'ofreciendo_carreras':
            respuesta = interpretar_respuesta_binaria(texto_original)
            if respuesta is True:
                print(f'Vocabot: Aquí están las carreras del área de {ultima_area}:')
                print()
                mostrar_carreras(ultima_area)
                print()
                print('Vocabot: ¿Te gustaría explorar otras recomendaciones? (si / no)')
                estado = 'post'
            elif respuesta is False:
                print('Vocabot: No hay problema. ¿Te gustaría explorar otras recomendaciones? (si / no)')
                estado = 'post'
            else:
                print('Vocabot: Solo dime si quieres ver las carreras o no.')
                print('Vocabot: ¿Quieres que te muestre las carreras disponibles? (si / no)')
            continue

        # ==============================================================
        # ESTADO: post
        # ==============================================================
        if estado == 'post':
            respuesta = interpretar_respuesta_binaria(texto_original)
            if respuesta is True:
                print('Vocabot: Perfecto. Empecemos de nuevo.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuéntame nuevamente sobre tus intereses.')
            elif respuesta is False:
                print('Vocabot: Entendido.')
                print('Vocabot: ¿Deseas finalizar nuestra conversación? (si / no)')
                estado = 'confirmar'
            else:
                print('Vocabot: Puedes responder con "si" para explorar otra área o "no" para terminar.')
            continue

        # ==============================================================
        # ESTADO: confirmar
        # ==============================================================
        if estado == 'confirmar':
            respuesta = interpretar_respuesta_binaria(texto_original)
            if respuesta is True:
                mostrar_resumen_final()
                break
            elif respuesta is False:
                print('Vocabot: Perfecto, sigamos entonces.')
                reiniciar_ciclo_vocacional()
                print('Vocabot: Cuéntame sobre tus intereses.')
            else:
                print('Vocabot: Responde con "si" para salir o "no" para continuar.')
            continue

        # ==============================================================
        # ESTADO: pregunta
        # ==============================================================
        if estado == 'pregunta':
            valor = interpretar_respuesta_escala(texto_original)
            if valor is None:
                reintentos_pregunta += 1
                if es_expresion_confusion(texto_original, intenciones):
                    print(f'Vocabot: {respuesta_confusion()}')
                else:
                    print('Vocabot: No comprendí bien.')

                if reintentos_pregunta >= 2:
                    print('Vocabot: No pasa nada, voy a pasar a otra pregunta para seguir con calma.')
                    estado = 'charla'
                    pregunta_actual = None
                    reintentos_pregunta = 0
                    if indice_pregunta < len(preguntas):
                        preguntar_guiada()
                    continue

                if not repetir_pregunta_actual():
                    print('Vocabot: Puedes responder con mucho, poco, más o menos, bastante o nada.')
                continue

            reintentos_pregunta = 0
            pregunta_id = (pregunta_actual or {}).get('id', '')
            aplicar_respuesta_pregunta(pregunta_id, valor)

            if valor >= 4:
                print('Vocabot: Entendido, parece que te interesa bastante.')
            elif valor == 3:
                print('Vocabot: Entendido, veo un interés moderado.')
            else:
                print('Vocabot: Entendido, veo poco interés en eso.')

            estado          = 'charla'
            pregunta_actual = None

            # AVANZAR AUTOMÁTICAMENTE: siguiente pregunta o resultado
            if indice_pregunta < len(preguntas):
                preguntar_guiada()
            else:
                resultado()
            continue

        # ==============================================================
        # ESTADO: charla (estado principal)
        # ==============================================================

        # Saludo simple sin intereses
        if es_saludo(texto_original, intenciones) and not detectar_intereses(texto_original, intenciones):
            print('Vocabot: Hola, soy Vocabot, dime cuáles son tus gustos.')
            continue

        # Detección de confusión en charla libre
        if es_expresion_confusion(texto_original, intenciones):
            print(f'Vocabot: {respuesta_confusion()}')
            if not preguntar_guiada():
                print('Vocabot: ¿Hay alguna materia o actividad que hayas disfrutado alguna vez?')
            continue

        # Detección de frustración en charla libre
        if es_expresion_frustracion(texto_original, intenciones):
            print(f'Vocabot: {respuesta_frustracion()}')
            print('Vocabot: Cuéntame algo que hayas disfrutado hacer, aunque parezca pequeño.')
            continue

        # Detección y puntuación de intereses
        texto_limpio   = limpiar_mensaje_nombre(texto_original)
        contribuciones = puntuar_intereses(texto_limpio, intenciones)

        if contribuciones:
            categoria = max(contribuciones, key=contribuciones.get)
            for area, peso in contribuciones.items():
                if area in memoria:
                    memoria[area] += float(peso)

            print(f'Vocabot: {respuesta_humana(categoria, texto_limpio)}')

            if sum(memoria.values()) < 2:
                seguimiento = pregunta_seguimiento(categoria, texto_limpio)
                if seguimiento:
                    print(f'Vocabot: {seguimiento}')
                elif indice_pregunta < len(preguntas):
                    preguntar_guiada()
                elif nombre and turnos % 2 == 0:
                    print(f'Vocabot: {nombre}, cuéntame un poco más de eso.')
            elif nombre and turnos % 2 == 0:
                print(f'Vocabot: {nombre}, cuéntame un poco más de eso.')
        else:
            print(f'Vocabot: {respuesta_no_entendida()}')
            if sum(memoria.values()) < 2:
                if not preguntar_guiada():
                    print('Vocabot: Puedes hablarme de materias, hobbies o lo que más disfrutas hacer.')

        turnos += 1

        if turnos >= 3 and sum(memoria.values()) > 0 and estado == 'charla':
            resultado()
        elif sum(memoria.values()) >= 2 and estado == 'charla':
            resultado()


if __name__ == '__main__':
    main()