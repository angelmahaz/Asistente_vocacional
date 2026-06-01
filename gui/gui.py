# *** Inteligencia Artificial ***
# *** Proyecto Final. Asistente vocacional***
# *** Vocabot ***
#
# Alumnos:
# ° Cisneros Rojas Hector Manuel
# ° Garcia Perea Pablo Emilio
# ° Hernández Andrade Miguel Angel
# ° Navarro Rodriguez Angel Efren
# ° Toledo Duran Jesús Rodrigo
#=======================================================================================================
import tkinter as tk
import sys
import os
import json
import re

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.chatbot import (
    cargar_intenciones,
    detectar_intereses,
    puntuar_intereses,
    detectar_recomendacion,
    extraer_nombre,
    limpiar_mensaje_nombre,
    tiene_contenido_relevante,
    respuesta_humana,
    respuesta_no_entendida,
    es_despedida,
    es_afirmacion,
    es_negacion,
    es_saludo,
    interpretar_respuesta_escala,
    interpretar_respuesta_binaria,
    cargar_preguntas,
    normalizar_texto,
    # ── Nuevas funciones v4 ──────────────────────────────────────────
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
    reiniciar_rotacion_respuestas,
)
from core.perceptron import cargar_areas, evaluar, explicar_recomendacion, descripcion_arquitectura
from core.recomendador import cargar_carreras, recomendar, obtener_enlaces_oficiales


class ChatGUI:
    """
    Constructor de la interfaz gráfica que configura la ventana principal,
    crea el área de chat con desplazamiento (Scroll) y teclado, diseña la
    zona de entrada de texto y carga los datos lógicos y variables de control del bot.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Vocabot")
        self.root.geometry("980x720")
        self.root.configure(bg="#1e1e2f")
        self.fuente_base = ("Arial", 12)

        container = tk.Frame(root, bg="#1e1e2f")
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, bg="#1e1e2f", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e2f")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._ajustar_ancho)

        footer = tk.Frame(root, bg="#171725")
        footer.pack(fill=tk.X)
        self.entry = tk.Entry(footer, font=("Arial", 12), bd=0, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 6), pady=10)
        self.entry.bind("<Return>", self.enviar)

        self.boton_enviar = tk.Button(
            footer,
            text="Enviar",
            command=self.enviar,
            bg="#3949ab",
            fg="white",
            bd=0,
            font=("Arial", 11, "bold"),
            padx=14,
            pady=6,
            activebackground="#5362d6",
            activeforeground="white",
        )
        self.boton_enviar.pack(side=tk.RIGHT, padx=(0, 10), pady=10)

        self.intenciones = cargar_intenciones("data/intenciones.json")
        self.areas = cargar_areas("data/areas.json")
        self.carreras = cargar_carreras("data/carreras.json")
        self.preguntas = cargar_preguntas("data/preguntas.json")
        self.mapa_preguntas = {
            "matematicas": {"matematicas": 1.15},
            "lectura":     {"humanidades": 0.45},
            "manual":      {"arte": 0.25, "matematicas": 0.20},
            "social":      {"salud": 0.35, "humanidades": 0.15},
            "tecnologia":  {"matematicas": 1.25},
            "salud":       {"salud": 1.20},
            "arte":        {"arte": 1.20},
            "naturaleza":  {"salud": 0.55, "matematicas": 0.20},
            "negocios":    {"humanidades": 0.85},
            "biologia_animales": {"salud": 1.10},
            "plantas_ecosistemas": {"salud": 1.05},
            "laboratorio": {"salud": 1.00, "matematicas": 0.25},
            "equipo": {"humanidades": 0.45, "salud": 0.25},
            "comunicacion": {"humanidades": 1.00},
            "creatividad_visual": {"arte": 1.10},
            "musica": {"arte": 1.05},
            "emprendimiento": {"humanidades": 0.75},
            "investigacion": {"matematicas": 0.35, "salud": 0.35, "humanidades": 0.35},
            "servicio_social": {"salud": 0.65, "humanidades": 0.35},

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
        self.nombre = None
        self.ultima_area = None
        self.reset_estado()

        self.bot_queue = []
        self.bot_activo = False
        self._mensaje_epoch = 0

        # ── Banner ASCII y disclaimers (se muestran antes que cualquier mensaje) ──
        banner_txt = (
            " VV     VV  OOOOO   CCCCC   AAAAA   BBBB    OOOOO   TTTTTTT\n"
            " VV     VV OO   OO CC      AA   AA  BB  BB OO   OO    TTT\n"
            "  VV    VV OO   OO CC      AAAAAAA  BBBB   OO   OO    TTT\n"
            "  VV   VV  OO   OO CC      AA   AA  BB  BB OO   OO    TTT\n"
            "   VVVVV    OOOOO   CCCCC  AA   AA  BBBB    OOOOO     TTT\n"
            "\n"
            "              V O C A B O T"
        )
        self.bubble_banner(banner_txt)

        disclaimers = [
            "Asistente vocacional conversacional.",
            "Puedes escribir materias, hobbies, gustos, intereses o ideas sobre lo que te gustaria estudiar.",
            "Tambien puedes responder con si, no, mucho, poco, mas o menos, tal vez o no se.",
            "Escribe 'salir' para terminar o 'ayuda' para ver estas instrucciones.",
            "Este bot es solo de apoyo y no sustituye la orientacion vocacional profesional.",
        ]
        for d in disclaimers:
            self.bubble_disclaimer(d)

        # ── Mensajes de bienvenida ──
        self.mensaje_bot("Hola, soy Vocabot.")
        self.mensaje_bot("Cuéntame cuáles son tus gustos o en qué eres bueno.")
        

    # -------------------------------------------------------------------
    def _ajustar_ancho(self, event):
        """
        Ajusta dinámicamente el ancho del contenedor interno al tamaño de la ventana
        para mantener la interfaz adaptativa y evitar desbordamientos horizontales.
        """
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # -------------------------------------------------------------------
    def _on_mousewheel(self, event):
        """
        Intercepta el evento de la rueda del ratón para desplazar verticalmente
        el área del chat de forma fluida y proporcional en la interfaz.
        """
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        self.canvas.yview_scroll(delta, "units")

    # -------------------------------------------------------------------
    def reset_estado(self):
        """
        Restablece las variables lógicas, los contadores de interacción y la puntuación
        de las áreas vocacionales de la sesión de chat a sus valores iniciales predeterminados.
        """
        self.memoria = {"matematicas": 0.0, "salud": 0.0, "humanidades": 0.0, "arte": 0.0}
        self.turnos = 0
        self.estado = "charla"
        self.indice_pregunta = 0
        self.pregunta_actual = None
        self.ultima_area = None
        self.intentos_pregunta = 0

    # -------------------------------------------------------------------
    def reiniciar_ciclo_vocacional(self):
        """
        Cancela los mensajes pendientes en la cola del chatbot, incrementa el identificador
        de época para ignorar procesos asíncronos activos y limpia todas las variables de estado
        para reiniciar de cero el test.
        """
        self._mensaje_epoch += 1
        self.bot_queue.clear()
        self.bot_activo = False
        reiniciar_rotacion_respuestas()
        self.reset_estado()
        self.ultima_area = None

    # -------------------------------------------------------------------
    def _scroll_abajo(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # -------------------------------------------------------------------
    def bubble(self, texto, lado):
        """
        Actualiza los elementos gráficos pendientes en la interfaz y desplaza
        automáticamente la barra de scroll hasta el extremo inferior para mostrar
        el mensaje más reciente del chat.
        """
        color = "#4fc3f7" if lado == "bot" else "#81c784"
        anchor = "w" if lado == "bot" else "e"
        contenedor = tk.Frame(self.scrollable_frame, bg="#1e1e2f")
        contenedor.pack(fill=tk.X, pady=4, padx=12)
        lbl = tk.Label(
            contenedor,
            text=texto,
            bg=color,
            fg="black",
            wraplength=560,
            padx=12,
            pady=8,
            justify="left",
            font=self.fuente_base,
        )
        lbl.pack(anchor=anchor)
        self._scroll_abajo()

    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    def bubble_banner(self, texto):
        """
        Muestra el banner ASCII de Vocabot con fuente monoespaciada
        para respetar el espaciado del arte ASCII y sin animacion de tipeo.
        Se llama una sola vez al arrancar la aplicacion.
        """
        contenedor = tk.Frame(self.scrollable_frame, bg="#0d0d1a")
        contenedor.pack(fill=tk.X, pady=(10, 2), padx=12)
        lbl = tk.Label(
            contenedor,
            text=texto,
            bg="#0d0d1a",
            fg="#4fc3f7",
            font=("Courier", 9, "bold"),
            justify="left",
            anchor="w",
            wraplength=0,
            padx=12,
            pady=10,
        )
        lbl.pack(anchor="w")
        self._scroll_abajo()

    # -------------------------------------------------------------------
    def bubble_disclaimer(self, texto):
        """
        Muestra una linea de disclaimer/instruccion inicial con un estilo
        diferenciado (fondo gris oscuro) para distinguirla de los mensajes
        normales del bot.
        """
        contenedor = tk.Frame(self.scrollable_frame, bg="#1e1e2f")
        contenedor.pack(fill=tk.X, pady=1, padx=12)
        lbl = tk.Label(
            contenedor,
            text=texto,
            bg="#2a2a40",
            fg="#aaaacc",
            font=("Arial", 10, "italic"),
            justify="left",
            anchor="w",
            wraplength=700,
            padx=10,
            pady=4,
        )
        lbl.pack(anchor="w")
        self._scroll_abajo()

    # -------------------------------------------------------------------
    def _mostrar_carreras(self, area):
        """
        Muestra todas las carreras del area recomendada agrupadas por universidad
        y los enlaces oficiales. Se invoca solo cuando el usuario acepta verlas.
        """
        carreras = recomendar(area, self.carreras, max_por_uni=999)
        if not carreras:
            self.mensaje_bot("No encontre carreras registradas para esa area por ahora.")
            return
        for uni, lista in carreras.items():
            self.mensaje_bot(f"-- {uni} --")
            if lista:
                bloque = "\n".join(f"  * {c}" for c in lista)
                self.mensaje_bot(bloque)
            else:
                self.mensaje_bot("  * Sin carreras registradas por ahora.")
        enlaces = obtener_enlaces_oficiales()
        if enlaces:
            self.mensaje_bot("Consulta la oferta educativa oficial:")
            for uni, url in enlaces.items():
                self.mensaje_bot(f"{uni}: {url}")

    def _crear_burbuja_bot(self, texto_inicial=""):
        """
        Genera e inserta dinámicamente un contenedor de tipo etiqueta en el área de chat,
        configurándolo visualmente como una burbuja de diálogo alineada a la izquierda
        para representar las respuestas del bot.
        """
        contenedor = tk.Frame(self.scrollable_frame, bg="#1e1e2f")
        contenedor.pack(fill=tk.X, pady=4, padx=12)
        lbl = tk.Label(
            contenedor,
            text=texto_inicial,
            bg="#4fc3f7",
            fg="black",
            wraplength=560,
            padx=12,
            pady=8,
            justify="left",
            font=self.fuente_base,
        )
        lbl.pack(anchor="w")
        self._scroll_abajo()
        return lbl

    # -------------------------------------------------------------------
    def _procesar_siguiente_mensaje_bot(self):
        """
        Gestiona la cola de mensajes del bot, extrayendo el siguiente texto pendiente
        y validando su época para iniciar su animación en la interfaz de forma secuencial y asíncrona.
        """
        if self.bot_activo or not self.bot_queue:
            return
        epoch, texto = self.bot_queue.pop(0)
        if epoch != self._mensaje_epoch:
            self.root.after(0, self._procesar_siguiente_mensaje_bot)
            return
        self.bot_activo = True
        lbl = self._crear_burbuja_bot("")
        self._animar_texto(lbl, texto, 0, epoch)

    # -------------------------------------------------------------------
    def _animar_texto(self, lbl, texto, indice, epoch):
        """
        Simula un efecto de escritura a máquina al insertar caracteres secuencialmente
        en la burbuja de texto, cancelando el proceso si el estado del ciclo es reiniciado.
        """
        if epoch != self._mensaje_epoch:
            try:
                lbl.destroy()
            except Exception:
                pass
            self.bot_activo = False
            if self.bot_queue:
                self.root.after(0, self._procesar_siguiente_mensaje_bot)
            return
        if indice <= len(texto):
            lbl.config(text=texto[:indice])
            self._scroll_abajo()
            self.root.after(15, lambda: self._animar_texto(lbl, texto, indice + 1, epoch))
        else:
            self.root.after(250, lambda: self._terminar_animacion(epoch))

    # -------------------------------------------------------------------
    def _terminar_animacion(self, epoch):
        """
        Finaliza el estado de animación del bot actual, estabiliza el scroll de la ventana
        y programa el procesamiento del siguiente mensaje en cola si existe.
        """
        if epoch != self._mensaje_epoch:
            self.bot_activo = False
            return
        self.bot_activo = False
        self._scroll_abajo()
        if self.bot_queue:
            self.root.after(50, self._procesar_siguiente_mensaje_bot)

    # -------------------------------------------------------------------
    def mensaje_bot(self, texto):
        """
        Añade un nuevo texto a la cola de salida del chatbot vinculándolo con la época actual
        e inicia automáticamente su procesamiento si el bot se encuentra inactivo.
        """
        self.bot_queue.append((self._mensaje_epoch, str(texto)))
        if not self.bot_activo:
            self.root.after(0, self._procesar_siguiente_mensaje_bot)

    # -------------------------------------------------------------------
    def mensaje_user(self, texto):
        """
        Envía el texto ingresado por el usuario al gestor visual para renderizarlo inmediatamente
        dentro de una burbuja de diálogo formateada para el usuario.
        """
        self.bubble(texto, "user")

    # -------------------------------------------------------------------
    def _es_recomendacion(self, texto):
        """
        Evalúa si el texto del usuario coincide con una intención de solicitud de recomendación
        mediante el analizador de intenciones.
        """
        return detectar_recomendacion(texto, self.intenciones)

    # -------------------------------------------------------------------
    def _pregunta_guiada(self):
        """
        Selecciona y envía al chat la siguiente pregunta del test vocacional,
        actualizando el índice y cambiando el estado de la sesión a modo pregunta.
        """
        if self.indice_pregunta < len(self.preguntas):
            pregunta = self.preguntas[self.indice_pregunta]
            self.indice_pregunta += 1
            self.pregunta_actual = pregunta
            self.estado = "pregunta"
            texto = pregunta.get("texto", "")
            if texto:
                self.mensaje_bot(texto)
            return True
        return False

    # -------------------------------------------------------------------
    def _repetir_pregunta_actual(self):
        """
        Reenvía al chat el texto de la pregunta activa en caso de que el usuario
        proporcione una respuesta inválida o ambigua.
        """
        if self.pregunta_actual:
            texto = self.pregunta_actual.get("texto", "")
            if texto:
                self.mensaje_bot(texto)
            return True
        return False

    # -------------------------------------------------------------------
    def _manejar_finalizacion(self, texto_lower):
        """
        Evalúa si el usuario desea terminar la sesión mediante palabras clave de despedida,
        respondiendo con un saludo de cierre y programando la destrucción de la ventana principal.
        """
        if any(p in texto_lower for p in ["salir", "adios", "adiós", "terminar", "finalizar", "bye", "cerrar"]):
            self.mensaje_bot("Fue un gusto ayudarte.")
            self.root.after(1500, self.root.destroy)
            return True
        return False

    # -------------------------------------------------------------------
    def _categoria_por_pregunta(self, pregunta_id):
        """
        Busca y retorna el diccionario de mapeo de categorías y puntajes asociado
        a un identificador de pregunta específico.
        """
        return self.mapa_preguntas.get(pregunta_id, {})

    # -------------------------------------------------------------------
    def _aplicar_respuesta_pregunta(self, pregunta_id, valor):
        """
        Calcula la ponderación de una respuesta numérica, normaliza su valor entre 0 y 1,
        y acumula el puntaje proporcional en las categorías vocacionales correspondientes
        dentro de la memoria.
        """
        contribuciones = self._categoria_por_pregunta(pregunta_id)
        if not contribuciones:
            return
        factor = max(0.0, min(1.0, (float(valor) - 1.0) / 4.0))
        for categoria, peso in contribuciones.items():
            if categoria in self.memoria:
                self.memoria[categoria] += factor * float(peso)

    # -------------------------------------------------------------------
    def _respuesta_texto_post(self, texto):
        """
        Método de control que normaliza el texto recibido y evalúa si corresponde a una afirmación,
        negación o respuesta binaria en lenguaje natural, retornando un valor booleano o None si es ambigua.
        """
        texto_norm = texto.strip().lower()
        if es_afirmacion(texto_norm):
            return True
        if es_negacion(texto_norm):
            return False
        binaria = interpretar_respuesta_binaria(texto_norm)
        if binaria is not None:
            return binaria
        return None

    # -------------------------------------------------------------------
    def _respuesta_escala(self, texto):
        """
        Analiza el texto ingresado por el usuario y extrae un valor numérico correspondiente
        a una respuesta en escala predefinida mediante el intérprete de respuestas.
        """
        valor = interpretar_respuesta_escala(texto)
        return valor

    # -------------------------------------------------------------------
    def _mostrar_menu_ayuda(self):
        """
        Muestra el menú de ayuda interactiva con 5 opciones numeradas.
        El usuario puede escribir el número o el nombre de la opción.
        """
        self.mensaje_bot("¿Sobre qué quieres saber? Elige una opción:")
        opciones = (
            "1. ¿Cómo funciona Vocabot?\n"
            "2. ¿Qué áreas de conocimiento existen?\n"
            "3. ¿Cómo se calcula mi recomendación?\n"
            "4. Quiero empezar de nuevo.\n"
            "5. Continuar la conversación."
        )
        self.mensaje_bot(opciones)

    # -------------------------------------------------------------------
    def _manejar_opcion_ayuda(self, texto: str) -> bool:
        """
        Interpreta la opción elegida del menú de ayuda y responde en consecuencia.
        Retorna True si se procesó una opción válida, False si no se reconoció.
        """
        norm = normalizar_texto(texto)
        opcion = None

        def tiene_numero(n):
            return re.search(rf"\b{n}\b", norm) is not None

        if tiene_numero("1") or "como funciona" in norm or "funciona" in norm:
            opcion = "1"
        elif tiene_numero("2") or "areas" in norm or "conocimiento" in norm:
            opcion = "2"
        elif tiene_numero("3") or "calcula" in norm or "neuronal" in norm:
            opcion = "3"
        elif tiene_numero("4") or "empezar de nuevo" in norm or "reiniciar" in norm or "nuevo" in norm:
            opcion = "4"
        elif tiene_numero("5") or "continuar" in norm or "seguir" in norm or "sigue" in norm:
            opcion = "5"

        if opcion == "1":
            self.mensaje_bot(
                "Vocabot es un asistente vocacional con inteligencia artificial.\n\n"
                "Solo cuéntame sobre tus gustos, hobbies e intereses y yo analizo la información.\n"
                "La red neuronal procesa todo y calcula las probabilidades de afinidad con cada área de conocimiento."
            )
            self.estado = "charla"
            return True

        if opcion == "2":
            self.mensaje_bot(
                "Existen 4 áreas de conocimiento:\n\n"
                "  Área 1 — Ciencias Físico-Matemáticas y de las Ingenierías\n"
                "             (matemáticas, física, programación, ingeniería, tecnología)\n\n"
                "  Área 2 — Ciencias Biológicas, Químicas y de la Salud\n"
                "             (medicina, biología, química, enfermería, nutrición)\n\n"
                "  Área 3 — Ciencias Sociales\n"
                "             (derecho, economía, administración, comunicación, psicología)\n\n"
                "  Área 4 — Humanidades y de las Artes\n"
                "             (filosofía, historia, literatura, música, diseño, arte)\n\n"
                "Las carreras disponibles son de la UNAM, IPN y UAM."
            )
            self.estado = "charla"
            return True

        if opcion == "3":
            capas = descripcion_arquitectura()
            detalle = "\n".join(f"  Capa {i+1}: {c}" for i, c in enumerate(capas))
            self.mensaje_bot(
                f"La recomendación se calcula con una red neuronal de {len(capas)} capas:\n\n"
                f"{detalle}\n\n"
                "Mientras más información me des, más precisa es la recomendación."
            )
            self.estado = "charla"
            return True

        if opcion == "4":
            self.mensaje_bot("Perfecto. Empecemos de nuevo.")
            self.reiniciar_ciclo_vocacional()
            self.mensaje_bot("Cuéntame sobre tus intereses.")
            return True

        if opcion == "5":
            self.mensaje_bot("Perfecto, sigamos donde estábamos. Cuéntame más sobre tus gustos.")
            self.estado = "charla"
            return True

        return False

    # -------------------------------------------------------------------
    def _resultado_detallado(self):
        if sum(self.memoria.values()) == 0:
            self.estado = "charla"
            self.mensaje_bot("Aún no tengo suficiente información para recomendarte con seguridad.")
            if not self._pregunta_guiada():
                self.mensaje_bot("Cuéntame un poco más sobre lo que te gusta.")
            return

        # Obtener info de la red neuronal y calcular resultado
        capas   = descripcion_arquitectura()
        area, _, prob = evaluar(self.memoria, self.areas)
        self.ultima_area = area

        # Mensaje de analisis con contexto de la red neuronal
        mensajes = [f"Analizando tus respuestas con la red neuronal ({len(capas)} capas)..."]

        # Probabilidades con barra visual
        mensajes.append("Resultado del análisis de la red neuronal:")
        for a, p in sorted(prob.items(), key=lambda x: x[1], reverse=True):
            barra = "|" * int(p * 20)
            mensajes.append(f"{a}:\n{barra} {p:.0%}")

        if area:
            # Area recomendada
            msg_area = f"La red neuronal identifica que tu perfil encaja mejor con:\n>> {area} <<"
            if self.nombre:
                msg_area = f"{self.nombre}, " + msg_area
            mensajes.append(msg_area)

            # Factores que influyeron
            top = explicar_recomendacion(self.memoria, self.areas, area)
            if top:
                mensajes.append(f"Las características que más influyeron en la red neuronal fueron: {', '.join(top)}.")

            # Ofrecer carreras — el usuario decide si las ve
            mensajes.append("Tengo algunas opciones de carreras que te pueden interesar.")
            mensajes.append("¿Quieres que te las muestre?")
            self.mostrar_mensajes(mensajes)
            self.estado = "ofreciendo_carreras"

        else:
            mensajes.append("No pude calcular una recomendación con los datos actuales.")
            mensajes.append("¿Quieres contarme un poco más sobre tus intereses?")
            self.mostrar_mensajes(mensajes)
            self.estado = "charla"

    # -------------------------------------------------------------------
    def mostrar_mensajes(self, mensajes, i=0):
        """
        Recorre una lista de mensajes del bot, enviándolos a la interfaz de manera
        secuencial y recursiva con un intervalo de retraso de 1.2 segundos entre cada uno.
        """
        if i < len(mensajes):
            self.mensaje_bot(mensajes[i])
            self.root.after(1200, lambda: self.mostrar_mensajes(mensajes, i + 1))

    # -------------------------------------------------------------------
    def enviar(self, event=None):
        """
        Procesa las entradas del usuario para extraer información contextual (nombre, intereses,
        comandos de salida o respuestas a tests), actualiza los puntajes de las categorías vocacionales,
        realiza transiciones de estado de la máquina de conversación y ejecuta las respuestas
        pertinentes en la interfaz visual.
        """
        try:
            texto = self.entry.get().strip()
            self.entry.delete(0, tk.END)
            if not texto:
                return
            self.mensaje_user(texto)

            texto_original = texto
            texto_norm = normalizar_texto(texto_original)

            # ── GUARDIA GLOBAL 1: Groserías ────────────────────────────
            # Se evalúa primero para que nunca rompa la conversación.
            if es_groseria(texto_original, self.intenciones):
                self.mensaje_bot(respuesta_groseria())
                return

            # ── GUARDIA GLOBAL 2: Despedida ────────────────────────────
            if self._manejar_finalizacion(texto_norm):
                resumen = generar_resumen_memoria(self.memoria, self.nombre)
                self.mensaje_bot(resumen)
                return

            # ── GUARDIA GLOBAL 3: Petición de ayuda interactiva ───────
            # Solo se dispara fuera del menú de ayuda para no crear bucles.
            if self.estado != "ayuda_menu" and es_peticion_ayuda(texto_original, self.intenciones):
                self.mensaje_bot(respuesta_ayuda_empatica(self.nombre))
                self._mostrar_menu_ayuda()
                self.estado = "ayuda_menu"
                return

            # ── GUARDIA GLOBAL 4: Comando de ayuda rápida (palabras exactas) ─
            if texto_norm in {"ayuda", "help", "instrucciones", "como funciona"}:
                self.mensaje_bot("Puedes hablarme de materias, hobbies, gustos, música, tecnología o cualquier interés que tengas.")
                self.mensaje_bot("Responde con si, no, mucho, poco, más o menos, tal vez o no sé cuando te haga preguntas.")
                self.mensaje_bot("Escribe 'salir' para terminar.")
                self.mensaje_bot("Recuerda que esto es solo un apoyo y no sustituye la orientación vocacional profesional.")
                return

            # ── Detectar nombre ────────────────────────────────────────
            nombre = extraer_nombre(texto_original)
            if nombre:
                self.nombre = nombre
                texto_sin_nombre = limpiar_mensaje_nombre(texto_original)
                if not tiene_contenido_relevante(texto_sin_nombre):
                    self.mensaje_bot(f"Mucho gusto, {self.nombre}.")
                    self.mensaje_bot("Cuéntame cuáles son tus gustos.")
                    return
                self.mensaje_bot(f"Mucho gusto, {self.nombre}.")
                texto_original = texto_sin_nombre
                texto_norm = texto_original.lower()

            # ── Recomendación explícita ────────────────────────────────
            if self._es_recomendacion(texto_original):
                self._resultado_detallado()
                return

            # ── Estado: ayuda_menu ─────────────────────────────────────
            if self.estado == "ayuda_menu":
                if not self._manejar_opcion_ayuda(texto_original):
                    self.mensaje_bot("No entendí la opción. Elige un número del 1 al 5.")
                    self._mostrar_menu_ayuda()
                return

            # ── Estado: ofreciendo_carreras ────────────────────────────
            if self.estado == "ofreciendo_carreras":
                respuesta = self._respuesta_texto_post(texto_original)
                if respuesta is True:
                    self.mensaje_bot(f"Aquí están las carreras del área de {self.ultima_area}:")
                    self._mostrar_carreras(self.ultima_area)
                    self.mensaje_bot("¿Te gustaría explorar otras recomendaciones? (si / no)")
                    self.estado = "post"
                    return
                if respuesta is False:
                    self.mensaje_bot("No hay problema. ¿Te gustaría explorar otras recomendaciones? (si / no)")
                    self.estado = "post"
                    return
                self.mensaje_bot("Solo dime si quieres ver las carreras o no.")
                self.mensaje_bot("¿Quieres que te muestre las carreras disponibles? (si / no)")
                return

            # ── Estado: post ───────────────────────────────────────────
            if self.estado == "post":
                respuesta = self._respuesta_texto_post(texto_original)
                if respuesta is True:
                    self.mensaje_bot("Perfecto. Empecemos de nuevo.")
                    self.reiniciar_ciclo_vocacional()
                    self.mensaje_bot("Cuéntame nuevamente sobre tus intereses.")
                    return
                if respuesta is False:
                    self.mensaje_bot("Entendido. ¿Deseas finalizar el programa? (si / no)")
                    self.estado = "confirmar"
                    return
                self.mensaje_bot("Puedes responder con 'si' para explorar otra área o 'no' para terminar.")
                return

            # ── Estado: confirmar ──────────────────────────────────────
            if self.estado == "confirmar":
                respuesta = self._respuesta_texto_post(texto_original)
                if respuesta is True:
                    resumen = generar_resumen_memoria(self.memoria, self.nombre)
                    self.mensaje_bot(resumen)
                    self.mensaje_bot("Gracias por usar el asistente. ¡Hasta luego!")
                    self.root.after(2500, self.root.destroy)
                    return
                if respuesta is False:
                    self.mensaje_bot("Perfecto. Sigamos entonces.")
                    self.reiniciar_ciclo_vocacional()
                    self.mensaje_bot("Cuéntame sobre tus intereses.")
                    return
                self.mensaje_bot("Responde con 'si' para salir o 'no' para continuar.")
                return

            # ── Estado: pregunta ───────────────────────────────────────
            if self.estado == "pregunta":
                valor = self._respuesta_escala(texto_original)
                if valor is None:
                    self.intentos_pregunta += 1
                    if es_expresion_confusion(texto_original, self.intenciones):
                        self.mensaje_bot(respuesta_confusion())
                    else:
                        self.mensaje_bot("Creo que no comprendí bien.")
                    if self.intentos_pregunta >= 2:
                        self.mensaje_bot("No pasa nada, voy a pasar a otra pregunta para seguir con calma.")
                        self.estado = "charla"
                        self.pregunta_actual = None
                        self.intentos_pregunta = 0
                        if self.indice_pregunta < len(self.preguntas):
                            self._pregunta_guiada()
                        return
                    if not self._repetir_pregunta_actual():
                        self.mensaje_bot("Puedes responder con mucho, poco, más o menos o nada.")
                    return
                self.intentos_pregunta = 0
                pregunta_id = (self.pregunta_actual or {}).get("id", "")
                self._aplicar_respuesta_pregunta(pregunta_id, valor)
                if valor >= 4:
                    self.mensaje_bot("Entendido, parece que te interesa bastante.")
                elif valor == 3:
                    self.mensaje_bot("Entendido, veo un interés moderado.")
                else:
                    self.mensaje_bot("Entendido, veo poco interés en eso.")
                self.estado = "charla"
                self.pregunta_actual = None
                if sum(self.memoria.values()) < 2 and self.indice_pregunta < len(self.preguntas):
                    self._pregunta_guiada()
                return

            # ── Solo saludo, sin intereses ─────────────────────────────
            if es_saludo(texto_original, self.intenciones) and not detectar_intereses(texto_original, self.intenciones):
                self.mensaje_bot("Hola, soy Vocabot, dime cuáles son tus gustos.")
                return

            # ── Confusión en charla libre ──────────────────────────────
            if es_expresion_confusion(texto_original, self.intenciones):
                self.mensaje_bot(respuesta_confusion())
                if not self._pregunta_guiada():
                    self.mensaje_bot("¿Hay alguna materia o actividad que hayas disfrutado alguna vez?")
                return

            # ── Frustración en charla libre ────────────────────────────
            if es_expresion_frustracion(texto_original, self.intenciones):
                self.mensaje_bot(respuesta_frustracion())
                self.mensaje_bot("Cuéntame algo que hayas disfrutado hacer, aunque parezca pequeño.")
                return

            # ── Detección y puntuación de intereses ────────────────────
            texto_limpio = limpiar_mensaje_nombre(texto_original)
            contribuciones = puntuar_intereses(texto_limpio, self.intenciones)
            if contribuciones:
                categoria = max(contribuciones, key=contribuciones.get)
                for area, peso in contribuciones.items():
                    if area in self.memoria:
                        self.memoria[area] += float(peso)
                self.mensaje_bot(respuesta_humana(categoria, texto_limpio))
                if sum(self.memoria.values()) < 2:
                    seguimiento = pregunta_seguimiento(categoria, texto_limpio)
                    if seguimiento:
                        self.mensaje_bot(seguimiento)
                    elif self.indice_pregunta < len(self.preguntas):
                        self._pregunta_guiada()
                    elif self.nombre and self.turnos % 2 == 0:
                        self.mensaje_bot(f"{self.nombre}, cuéntame un poco más de eso.")
                elif self.nombre and self.turnos % 2 == 0:
                    self.mensaje_bot(f"{self.nombre}, cuéntame un poco más de eso.")
            else:
                self.mensaje_bot(respuesta_no_entendida())
                if sum(self.memoria.values()) < 2:
                    if not self._pregunta_guiada():
                        self.mensaje_bot("Puedes hablarme de materias, hobbies o lo que más disfrutas hacer.")

            self.turnos += 1
            if self.turnos >= 5 and sum(self.memoria.values()) > 0 and self.estado == "charla":
                self._resultado_detallado()

        except Exception as e:
            print("Error:", e)
            self.mensaje_bot("Ocurrió un pequeño error, pero podemos seguir. Intenta otra vez.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()