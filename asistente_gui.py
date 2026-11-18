import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from ia_logica import AsistentePeluqueria


class AsistenteGUI:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Asistente de Peluquería Paco")
        self.ventana.geometry("540x620")
        self.ventana.minsize(400, 450)
        self.ventana.configure(bg="#F4F4F6")

        self.asistente = None
        self._inicializar_ia()

        self._construir_interfaz()

    def _inicializar_ia(self):
        try:
            self.asistente = AsistentePeluqueria()
        except Exception as error:
            messagebox.showwarning(
                "Configuración requerida",
                f"No se pudo inicializar la IA:\n{error}\n\n"
                "Asegúrate de crear tu archivo .env con la API_KEY."
            )

    def _construir_interfaz(self):
        self.chat_historial = scrolledtext.ScrolledText(
            self.ventana,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#222222",
            padx=12,
            pady=12,
            relief=tk.FLAT
        )
        self.chat_historial.pack(padx=12, pady=(12, 6), fill=tk.BOTH, expand=True)

        self._agregar_mensaje(
            "Bienvenido al Asistente de Peluquería Paco.\n"
            "-----------------------------------------------------------\n\n"
        )

        self.marco_inferior = tk.Frame(self.ventana, bg="#F4F4F6")
        self.marco_inferior.pack(padx=12, pady=(0, 12), fill=tk.X)

        self.campo_pregunta = tk.Entry(
            self.marco_inferior,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            bd=1
        )
        self.campo_pregunta.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 8))
        self.campo_pregunta.focus_set()

        self.boton_enviar = self._crear_boton_enviar(self.marco_inferior)
        self.boton_enviar.pack(side=tk.RIGHT)

        self.ventana.bind("<Return>", lambda event: self.enviar_mensaje())

    def _crear_boton_enviar(self, contenedor):
        return tk.Button(
            contenedor,
            text="➤",
            font=("Segoe UI", 10, "bold"),
            bg="#0066CC",
            fg="#FFFFFF",
            activebackground="#0052A3",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=4,
            command=self.enviar_mensaje
        )

    def _agregar_mensaje(self, texto: str):
        self.chat_historial.config(state=tk.NORMAL)
        self.chat_historial.insert(tk.END, texto)
        self.chat_historial.see(tk.END)
        self.chat_historial.config(state=tk.DISABLED)

    def enviar_mensaje(self):
        pregunta = self.campo_pregunta.get().strip()

        if not pregunta:
            return

        if not self.asistente:
            self._inicializar_ia()
            if not self.asistente:
                messagebox.showerror(
                    "Error de Configuración",
                    "No se puede consultar a la IA porque no hay una API Key válida configurada en el archivo .env."
                )
                return

        self._agregar_mensaje(f"👤 Tú: {pregunta}\n\n")

        self.campo_pregunta.delete(0, tk.END)

        self.boton_enviar.config(state=tk.DISABLED)
        self.campo_pregunta.config(state=tk.DISABLED)

        hilo = threading.Thread(target=self._hilo_consultar_ia, args=(pregunta,))
        hilo.daemon = True
        hilo.start()

    def _hilo_consultar_ia(self, pregunta: str):
        try:
            respuesta = self.asistente.consultar(pregunta)
            texto_a_mostrar = f"💬 Asistente: {respuesta}\n\n"
        except Exception as error:
            texto_a_mostrar = (
                "⚠️ Asistente: Ocurrió un error al procesar tu consulta. "
                "Verifica tu conexión a internet o tu clave de API.\n\n"
            )
            self.ventana.after(
                0,
                lambda: messagebox.showerror(
                    "Error de Conexión",
                    f"No fue posible contactar con Gemini:\n{error}"
                )
            )

        self.ventana.after(0, lambda: self._agregar_mensaje(texto_a_mostrar))
        self.ventana.after(0, lambda: self.boton_enviar.config(state=tk.NORMAL))
        self.ventana.after(0, lambda: self.campo_pregunta.config(state=tk.NORMAL))
        self.ventana.after(0, lambda: self.campo_pregunta.focus_set())

    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    app = AsistenteGUI()
    app.ejecutar()
