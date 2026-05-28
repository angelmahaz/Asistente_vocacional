
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
)
from core.perceptron import cargar_areas, evaluar, explicar_recomendacion
from core.recomendador import cargar_carreras, recomendar, obtener_enlaces_oficiales

#_______________________________________________________________________________________________________


# Constructor de la interfaz gráfica que configura la ventana principal, crea el área de chat con 
# desplazamiento (Scroll) y teclado, diseña la zona de entrada de texto y carga los datos lógicos y 
# variables de control del bot.

class ChatGUI:
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
            "lectura": {"humanidades": 0.45},
            "manual": {"arte": 0.25, "matematicas": 0.20},
            "social": {"salud": 0.35, "humanidades": 0.15},
            "tecnologia": {"matematicas": 1.25},
        }

        self.nombre = None
        self.ultima_area = None
        self.reset_estado()

        self.bot_queue = []
        self.bot_activo = False
        self._mensaje_epoch = 0

        self.mensaje_bot("Hola, soy Vocabot.")
        self.mensaje_bot("Cuéntame cuáles son tus gustos o en qué eres bueno.")
        self.mensaje_bot("Puedes escribir materias, hobbies, música, tecnología o cualquier interés que tengas.")
        self.mensaje_bot("También puedes responder con si, no, mucho, poco, más o menos, tal vez o no sé.")
        self.mensaje_bot("Escribe 'salir' para terminar o 'ayuda' si quieres ver estas instrucciones otra vez.")
        self.mensaje_bot("Este bot es solo de apoyo y no sustituye la orientación vocacional profesional.")

#_______________________________________________________________________________________________________

# Ajusta dinámicamente el ancho del contenedor interno al tamaño de la ventana 
# para mantener la interfaz adaptativa y evitar desbordamientos horizontales.

    def _ajustar_ancho(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

#_______________________________________________________________________________________________________


# Intercepta el evento de la rueda del ratón para desplazar verticalmente el área del chat de forma 
# fluida y proporcional en la interfaz.

    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        self.canvas.yview_scroll(delta, "units")

#_______________________________________________________________________________________________________

# Restablece las variables lógicas, los contadores de interacción y la puntuación de las áreas 
# vocacionales de la sesión de chat a sus valores iniciales predeterminados.

    def reset_estado(self):
        self.memoria = {"matematicas": 0.0, "salud": 0.0, "humanidades": 0.0, "arte": 0.0}
        self.turnos = 0
        self.estado = "charla"
        self.indice_pregunta = 0
        self.pregunta_actual = None
        self.ultima_area = None

#_______________________________________________________________________________________________________

# Cancela los mensajes pendientes en la cola del chatbot, incrementa el identificador de época para 
# ignorar procesos asíncronos activos y limpia todas las variables de estado para reiniciar de cero 
# el test.

    def reiniciar_ciclo_vocacional(self):
        """Limpia por completo la ronda actual para comenzar una nueva recomendación."""
        self._mensaje_epoch += 1
        self.bot_queue.clear()
        self.bot_activo = False
        self.reset_estado()
        self.ultima_area = None

#_______________________________________________________________________________________________________


    def _scroll_abajo(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

#_______________________________________________________________________________________________________


# Actualiza los elementos gráficos pendientes en la interfaz y desplaza automáticamente la barra de 
# scroll hasta el extremo inferior para mostrar el mensaje más reciente del chat.

    def bubble(self, texto, lado):
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

#_______________________________________________________________________________________________________

# Genera e inserta dinámicamente un contenedor de tipo etiqueta en el área de chat, configurándolo 
# visualmente como una burbuja de diálogo alineada a la izquierda para representar las respuestas del bot.

    def _crear_burbuja_bot(self, texto_inicial=""):
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

#_______________________________________________________________________________________________________

# Gestiona la cola de mensajes del bot, extrayendo el siguiente texto pendiente y validando su época 
# para iniciar su animación en la interfaz de forma secuencial y asíncrona.

    def _procesar_siguiente_mensaje_bot(self):
        if self.bot_activo or not self.bot_queue:
            return

        epoch, texto = self.bot_queue.pop(0)
        if epoch != self._mensaje_epoch:
            # Mensaje viejo: se descarta y se continúa con el siguiente
            self.root.after(0, self._procesar_siguiente_mensaje_bot)
            return

        self.bot_activo = True
        lbl = self._crear_burbuja_bot("")
        self._animar_texto(lbl, texto, 0, epoch)

#_______________________________________________________________________________________________________

# Simula un efecto de escritura a máquina al insertar caracteres secuencialmente en la burbuja de texto,
#  cancelando el proceso si el estado del ciclo es reiniciado.

    def _animar_texto(self, lbl, texto, indice, epoch):
        
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

#_______________________________________________________________________________________________________

# Finaliza el estado de animación del bot actual, estabiliza el scroll de la ventana y programa el 
# procesamiento del siguiente mensaje en cola si existe.

    def _terminar_animacion(self, epoch):
        if epoch != self._mensaje_epoch:
            self.bot_activo = False
            return

        self.bot_activo = False
        self._scroll_abajo()
        if self.bot_queue:
            self.root.after(50, self._procesar_siguiente_mensaje_bot)

#_______________________________________________________________________________________________________

# Añade un nuevo texto a la cola de salida del chatbot vinculándolo con la época actual e inicia 
# automáticamente su procesamiento si el bot se encuentra inactivo.

    def mensaje_bot(self, texto):
        self.bot_queue.append((self._mensaje_epoch, str(texto)))
        if not self.bot_activo:
            self.root.after(0, self._procesar_siguiente_mensaje_bot)

#_______________________________________________________________________________________________________

# Envía el texto ingresado por el usuario al gestor visual para renderizarlo inmediatamente dentro 
# de una burbuja de diálogo formateada para el usuario.

    def mensaje_user(self, texto):
        self.bubble(texto, "user")

#_______________________________________________________________________________________________________

# Evalúa si el texto del usuario coincide con una intención de solicitud de recomendación mediante 
# el analizador de intenciones.

    def _es_recomendacion(self, texto):
        return detectar_recomendacion(texto, self.intenciones)

#_______________________________________________________________________________________________________

# Selecciona y envía al chat la siguiente pregunta del test vocacional, actualizando el 
# índice y cambiando el estado de la sesión a modo pregunta.

    def _pregunta_guiada(self):
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

#_______________________________________________________________________________________________________

# Reenvía al chat el texto de la pregunta activa en caso de que el usuario proporcione una respuesta 
# inválida o ambigua.

    def _repetir_pregunta_actual(self):
        if self.pregunta_actual:
            texto = self.pregunta_actual.get("texto", "")
            if texto:
                self.mensaje_bot(texto)
                return True
        return False

#_______________________________________________________________________________________________________

# Evalúa si el usuario desea terminar la sesión mediante palabras clave de despedida, respondiendo 
# con un saludo de cierre y programando la destrucción de la ventana principal.

    def _manejar_finalizacion(self, texto_lower):
        if any(p in texto_lower for p in ["salir", "adios", "adiós", "terminar", "finalizar", "bye", "cerrar"]):
            self.mensaje_bot("Fue un gusto ayudarte.")
            self.root.after(1500, self.root.destroy)
            return True
        return False

#_______________________________________________________________________________________________________

# Valida si el mensaje del usuario contiene estrictamente un saludo, asegurando que no se hayan 
# incluido intereses o preferencias vocacionales en el mismo texto.

    def _es_solo_saludo(self, texto):
        texto_limpio = limpiar_mensaje_nombre(texto)
        return es_saludo(texto_limpio, self.intenciones) and not detectar_intereses(texto_limpio, self.intenciones)

#_______________________________________________________________________________________________________

# Busca y retorna el diccionario de mapeo de categorías y puntajes asociado a un identificador 
# de pregunta específico.

    def _categoria_por_pregunta(self, pregunta_id):
        return self.mapa_preguntas.get(pregunta_id, {})

#_______________________________________________________________________________________________________

# Calcula la ponderación de una respuesta numérica, normaliza su valor entre 0 y 1, y acumula el puntaje 
# proporcional en las categorías vocacionales correspondientes dentro de la memoria.

    def _aplicar_respuesta_pregunta(self, pregunta_id, valor):
        contribuciones = self._categoria_por_pregunta(pregunta_id)
        if not contribuciones:
            return

        factor = max(0.0, min(1.0, (float(valor) - 1.0) / 4.0))
        for categoria, peso in contribuciones.items():
            if categoria in self.memoria:
                self.memoria[categoria] += factor * float(peso)

#_______________________________________________________________________________________________________

# Método de control que normaliza el texto recibido y evalúa si corresponde a una afirmación, 
# negación o respuesta binaria en lenguaje natural, retornando un valor booleano o None si es ambigua.

    def _respuesta_texto_post(self, texto):
        texto_norm = texto.strip().lower()

        if es_afirmacion(texto_norm):
            return True
        if es_negacion(texto_norm):
            return False

        # Acepta respuestas expresadas con lenguaje natural que no sean binarios exactos.
        binaria = interpretar_respuesta_binaria(texto_norm)
        if binaria is not None:
            return binaria

        return None

#_______________________________________________________________________________________________________

#

    def _respuesta_escala(self, texto):
        valor = interpretar_respuesta_escala(texto)
        return valor

#_______________________________________________________________________________________________________

# Analiza el texto ingresado por el usuario y extrae un valor numérico correspondiente a una respuesta 
# en escala predefinida mediante el intérprete de respuestas.

    def _resultado_detallado(self):
        if sum(self.memoria.values()) == 0:
            self.estado = "charla"
            self.mensaje_bot("Aún no tengo suficiente información para recomendarte con seguridad.")
            if not self._pregunta_guiada():
                self.mensaje_bot("Cuéntame un poco más sobre lo que te gusta.")
            return

        self.estado = "post"

        area, _, prob = evaluar(self.memoria, self.areas)
        self.ultima_area = area

        mensajes = ["Estoy analizando tus respuestas con IA..."]

        for a, p in sorted(prob.items(), key=lambda x: x[1], reverse=True):
            mensajes.append(f"{a}: {p:.2f}")

        if area:
            msg = f"Te recomiendo el área de {area}."
            if self.nombre:
                msg = f"{self.nombre}, {msg}"
            mensajes.append(msg)

            top = explicar_recomendacion(self.memoria, self.areas, area)
            if top:
                mensajes.append(f"Tomé en cuenta principalmente: {', '.join(top)}.")

            carreras = recomendar(area, self.carreras)

            if not carreras:
                mensajes.append("No encontré carreras disponibles por ahora.")
            else:
                for uni, lista in carreras.items():
                    mensajes.append(f"{uni}:")
                    if lista:
                        mensajes.append(" - " + "\n - ".join(lista))
                    else:
                        mensajes.append(" - Sin carreras registradas por ahora")

            enlaces = obtener_enlaces_oficiales()
            if enlaces:
                mensajes.append("Consulta la oferta educativa oficial:")
                for uni, url in enlaces.items():
                    mensajes.append(f"{uni}: {url}")
        else:
            mensajes.append("No pude calcular una recomendación por ahora.")

        mensajes.append("¿Te gustaría explorar otras recomendaciones?")

        self.mostrar_mensajes(mensajes)

#_______________________________________________________________________________________________________

# Recorre una lista de mensajes del bot, enviándolos a la interfaz de manera secuencial y recursiva 
# con un intervalo de retraso de 1.2 segundos entre cada uno.

    def mostrar_mensajes(self, mensajes, i=0):
        if i < len(mensajes):
            self.mensaje_bot(mensajes[i])
            self.root.after(1200, lambda: self.mostrar_mensajes(mensajes, i + 1))

#_______________________________________________________________________________________________________

# Procesa las entradas del usuario para extraer información contextual (nombre, intereses, comandos de 
# salida o respuestas a tests), actualiza los puntajes de las categorías vocacionales, realiza 
# transiciones de estado de la máquina de conversación y ejecuta las respuestas pertinentes en la 
# interfaz visual.

    def enviar(self, event=None):
        try:
            texto = self.entry.get().strip()
            self.entry.delete(0, tk.END)

            if not texto:
                return

            self.mensaje_user(texto)
            texto_original = texto
            texto_norm = normalizar_texto(texto_original)

            if texto_norm in {"ayuda", "help", "instrucciones", "como funciona"}:
                self.mensaje_bot("Puedes hablarme de materias, hobbies, gustos, música, tecnología o cualquier interés que tengas.")
                self.mensaje_bot("Responde con si, no, mucho, poco, más o menos, tal vez o no sé cuando te haga preguntas.")
                self.mensaje_bot("Escribe 'salir' para terminar.")
                self.mensaje_bot("Recuerda que esto es solo un apoyo y no sustituye la orientación vocacional profesional.")
                return

            if self._manejar_finalizacion(texto_norm):
                return

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

            if self._es_recomendacion(texto_original):
                self._resultado_detallado()
                return

            if self.estado == "post":
                respuesta = self._respuesta_texto_post(texto_original)

                if respuesta is True:
                    self.mensaje_bot("Perfecto. Empecemos de nuevo.")
                    self.reiniciar_ciclo_vocacional()
                    self.mensaje_bot("Cuéntame nuevamente sobre tus intereses.")
                    return

                if respuesta is False:
                    self.mensaje_bot("Creo que no comprendí bien. ¿Quieres finalizar el programa?")
                    self.estado = "confirmar"
                    return

                self.mensaje_bot("Creo que no comprendí bien. ¿Quieres explorar otras recomendaciones?")
                return

            if self.estado == "confirmar":
                respuesta = self._respuesta_texto_post(texto_original)

                if respuesta is True:
                    self.mensaje_bot("Gracias por usar el asistente.")
                    self.root.after(1500, self.root.destroy)
                    return

                if respuesta is False:
                    self.mensaje_bot("Perfecto. Sigamos entonces.")
                    self.reiniciar_ciclo_vocacional()
                    self.mensaje_bot("Cuéntame sobre tus intereses.")
                    return

                self.mensaje_bot("Creo que no comprendí bien. ¿Quieres finalizar el programa?")
                return

            if self.estado == "pregunta":
                valor = self._respuesta_escala(texto_original)

                if valor is None:
                    self.mensaje_bot("Creo que no comprendí bien.")
                    if not self._repetir_pregunta_actual():
                        self.mensaje_bot("Puedes responder con mucho, poco, más o menos o nada.")
                    return

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

            if es_saludo(texto_original, self.intenciones) and not detectar_intereses(texto_original, self.intenciones):
                self.mensaje_bot("Hola, soy Vocabot, dime cuáles son tus gustos.")
                return

            texto_limpio = limpiar_mensaje_nombre(texto_original)
            contribuciones = puntuar_intereses(texto_limpio, self.intenciones)

            if contribuciones:
                categoria = max(contribuciones, key=contribuciones.get)
                for area, peso in contribuciones.items():
                    if area in self.memoria:
                        self.memoria[area] += float(peso)

                self.mensaje_bot(respuesta_humana(categoria, texto_limpio))

                if self.nombre and self.turnos % 2 == 0:
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