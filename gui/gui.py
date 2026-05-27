
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
    respuesta_general,
    respuesta_no_entendida,
    es_despedida,
    es_afirmacion,
    es_negacion,
    es_saludo,
    interpretar_respuesta_escala,
    interpretar_respuesta_binaria,
    cargar_preguntas,
)
from core.perceptron import cargar_areas, evaluar, explicar_recomendacion
from core.recomendador import cargar_carreras, recomendar

#_______________________________________________________________________________________________________


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

#_______________________________________________________________________________________________________


    def _ajustar_ancho(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

#_______________________________________________________________________________________________________


    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        self.canvas.yview_scroll(delta, "units")

#_______________________________________________________________________________________________________


    def reset_estado(self):
        self.memoria = {"matematicas": 0.0, "salud": 0.0, "humanidades": 0.0, "arte": 0.0}
        self.turnos = 0
        self.estado = "charla"
        self.indice_pregunta = 0
        self.pregunta_actual = None
        self.ultima_area = None

#_______________________________________________________________________________________________________


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


    def _animar_texto(self, lbl, texto, indice, epoch):
        # Si cambió la ronda, la animación vieja no debe seguir escribiendo
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


    def _terminar_animacion(self, epoch):
        if epoch != self._mensaje_epoch:
            self.bot_activo = False
            return

        self.bot_activo = False
        self._scroll_abajo()
        if self.bot_queue:
            self.root.after(50, self._procesar_siguiente_mensaje_bot)

#_______________________________________________________________________________________________________


    def mensaje_bot(self, texto):
        self.bot_queue.append((self._mensaje_epoch, str(texto)))
        if not self.bot_activo:
            self.root.after(0, self._procesar_siguiente_mensaje_bot)

#_______________________________________________________________________________________________________


    def mensaje_user(self, texto):
        self.bubble(texto, "user")

#_______________________________________________________________________________________________________


    def _es_recomendacion(self, texto):
        return detectar_recomendacion(texto, self.intenciones)

#_______________________________________________________________________________________________________


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


    def _repetir_pregunta_actual(self):
        if self.pregunta_actual:
            texto = self.pregunta_actual.get("texto", "")
            if texto:
                self.mensaje_bot(texto)
                return True
        return False

#_______________________________________________________________________________________________________


    def _manejar_finalizacion(self, texto_lower):
        if any(p in texto_lower for p in ["salir", "adios", "adiós", "terminar", "finalizar", "bye", "cerrar"]):
            self.mensaje_bot("Fue un gusto ayudarte.")
            self.root.after(1500, self.root.destroy)
            return True
        return False

#_______________________________________________________________________________________________________


    def _es_solo_saludo(self, texto):
        texto_limpio = limpiar_mensaje_nombre(texto)
        return es_saludo(texto_limpio, self.intenciones) and not detectar_intereses(texto_limpio, self.intenciones)

#_______________________________________________________________________________________________________


    def _categoria_por_pregunta(self, pregunta_id):
        return self.mapa_preguntas.get(pregunta_id, {})

#_______________________________________________________________________________________________________


    def _aplicar_respuesta_pregunta(self, pregunta_id, valor):
        contribuciones = self._categoria_por_pregunta(pregunta_id)
        if not contribuciones:
            return

        factor = max(0.0, min(1.0, (float(valor) - 1.0) / 4.0))
        for categoria, peso in contribuciones.items():
            if categoria in self.memoria:
                self.memoria[categoria] += factor * float(peso)

#_______________________________________________________________________________________________________


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


    def _respuesta_escala(self, texto):
        valor = interpretar_respuesta_escala(texto)
        return valor

#_______________________________________________________________________________________________________


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
        else:
            mensajes.append("No pude calcular una recomendación por ahora.")

        mensajes.append("¿Te gustaría explorar otras recomendaciones?")

        self.mostrar_mensajes(mensajes)

#_______________________________________________________________________________________________________


    def mostrar_mensajes(self, mensajes, i=0):
        if i < len(mensajes):
            self.mensaje_bot(mensajes[i])
            self.root.after(1200, lambda: self.mostrar_mensajes(mensajes, i + 1))

#_______________________________________________________________________________________________________


    def enviar(self, event=None):
        try:
            texto = self.entry.get().strip()
            self.entry.delete(0, tk.END)

            if not texto:
                return

            self.mensaje_user(texto)
            texto_original = texto
            texto_norm = texto.lower()

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

                self.mensaje_bot(respuesta_humana(categoria))

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