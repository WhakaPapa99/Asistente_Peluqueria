import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from ia_logica import AsistentePeluqueria


class AsistenteGUI:
    def __init__(self):
        # 1. Creación y configuración de la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Asistente de Peluquería Paco")
        self.ventana.geometry("540x620")
        self.ventana.minsize(400, 450)
        self.ventana.configure(bg="#F4F4F6")

        # 2. Inicialización de la lógica del asistente IA
        # Si las claves o dependencias fallan, capturamos el error para avisar al usuario
        self.asistente = None
        self._inicializar_ia()

        # 3. Construcción de los componentes gráficos
        self._construir_interfaz()

    def _inicializar_ia(self):
        """Intenta instanciar el cliente de IA; si falta la API Key, muestra advertencia."""
        try:
            self.asistente = AsistentePeluqueria()
        except Exception as error:
            messagebox.showwarning(
                "Configuración requerida",
                f"No se pudo inicializar la IA:\n{error}\n\n"
                "Asegúrate de crear tu archivo .env con la API_KEY."
            )

    def _construir_interfaz(self):
        """Crea y posiciona todos los widgets de la ventana."""
        # Área superior: Historial del chat con scroll
        # wrap=tk.WORD evita partir palabras y state=DISABLED protege contra edición manual
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

        # Mensaje de bienvenida inicial tal como en el ejemplo del enunciado
        self._agregar_mensaje(
            "Bienvenido al Asistente de Peluquería Paco.\n"
            "-----------------------------------------------------------\n\n",
            es_sistema=True
        )

        # Contenedor inferior: barra de herramientas para input y botón
        self.marco_inferior = tk.Frame(self.ventana, bg="#F4F4F6")
        self.marco_inferior.pack(padx=12, pady=(0, 12), fill=tk.X)

        # Campo de entrada de texto
        self.campo_pregunta = tk.Entry(
            self.marco_inferior,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            bd=1
        )
        self.campo_pregunta.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 8))
        self.campo_pregunta.focus_set()  # Coloca el cursor directamente en el cuadro de texto

        # Botón de enviar (soporta icono o texto)
        self.boton_enviar = self._crear_boton_enviar(self.marco_inferior)
        self.boton_enviar.pack(side=tk.RIGHT)

        # Atajo: presionar la tecla 'Enter' envía el mensaje directamente
        self.ventana.bind("<Return>", lambda event: self.enviar_mensaje())

    def _crear_boton_enviar(self, contenedor):
        """
        Crea el botón de envío.
        Si existe una imagen 'assets/send.png' o 'send.png', carga el icono gráfico.
        De lo contrario, utiliza un símbolo Unicode elegante (➤ Enviar).
        """
        ruta_icono = "assets/send.png" if os.path.exists("assets/send.png") else "send.png"

        if os.path.exists(ruta_icono):
            try:
                # Cargar imagen en formato PNG nativo de Tkinter
                icono = tk.PhotoImage(file=ruta_icono)
                # NOTA TÉCNICA: Guardamos la referencia en el botón para evitar que
                # el Garbage Collector de Python la elimine de la memoria RAM
                boton = tk.Button(
                    contenedor,
                    image=icono,
                    command=self.enviar_mensaje,
                    bg="#0066CC",
                    activebackground="#0052A3",
                    relief=tk.FLAT,
                    cursor="hand2",
                    padx=10,
                    pady=5
                )
                boton.image = icono  # Referencia obligatoria en Tkinter
                return boton
            except Exception:
                pass  # Si la imagen falla, caemos en el botón con símbolo Unicode

        # Botón con símbolo / texto estilizado
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

    def _agregar_mensaje(self, texto: str, es_sistema: bool = False):
        """
        Inserta texto en el ScrolledText habilitándolo temporalmente y
        desplazando la vista hasta el final para que el usuario vea lo último.
        """
        self.chat_historial.config(state=tk.NORMAL)
        self.chat_historial.insert(tk.END, texto)
        self.chat_historial.see(tk.END)
        self.chat_historial.config(state=tk.DISABLED)

    def enviar_mensaje(self):
        """Acción ejecutada al pulsar el botón o la tecla Enter."""
        pregunta = self.campo_pregunta.get().strip()

        # Si el usuario no ha escrito nada, ignoramos la acción
        if not pregunta:
            return

        # 1. Comprobamos si la IA está inicializada
        if not self.asistente:
            self._inicializar_ia()
            if not self.asistente:
                messagebox.showerror(
                    "Error de Configuración",
                    "No se puede consultar a la IA porque no hay una API Key válida configurada en el archivo .env."
                )
                return

        # 2. Mostramos la pregunta en el historial del chat
        self._agregar_mensaje(f"👤 Tú: {pregunta}\n\n")

        # 3. Vaciamos el cuadro de entrada (requisito explícito de la rúbrica)
        self.campo_pregunta.delete(0, tk.END)

        # 4. Deshabilitamos botón e input temporalmente para evitar peticiones duplicadas
        self.boton_enviar.config(state=tk.DISABLED)
        self.campo_pregunta.config(state=tk.DISABLED)

        # 5. Ejecutamos la consulta en un HILO SECUNDARIO (Threading)
        # Esto es crucial: evita que la interfaz gráfica se congele mientras Gemini responde
        hilo = threading.Thread(target=self._hilo_consultar_ia, args=(pregunta,))
        hilo.daemon = True  # Permite cerrar la app de inmediato aunque el hilo siga corriendo
        hilo.start()

    def _hilo_consultar_ia(self, pregunta: str):
        """Se ejecuta en segundo plano para no congelar la ventana principal."""
        try:
            # Llamada al módulo de lógica (conecta con Google Gemini)
            respuesta = self.asistente.consultar(pregunta)
            texto_a_mostrar = f"💬 Asistente: {respuesta}\n\n"
        except Exception as error:
            # Si ocurre un fallo de red o cuota, avisamos al usuario amablemente
            texto_a_mostrar = (
                "⚠️ Asistente: Ocurrió un error al procesar tu consulta. "
                "Verifica tu conexión a internet o tu clave de API.\n\n"
            )
            # Mostramos también ventana emergente de aviso sin cerrar la aplicación
            self.ventana.after(
                0,
                lambda: messagebox.showerror(
                    "Error de Conexión",
                    f"No fue posible contactar con Gemini:\n{error}"
                )
            )

        # Usamos .after() o inserción directa para actualizar la interfaz en el hilo principal
        self.ventana.after(0, lambda: self._agregar_mensaje(texto_a_mostrar))
        # Reactivamos el botón de enviar y el cuadro de entrada
        self.ventana.after(0, lambda: self.boton_enviar.config(state=tk.NORMAL))
        self.ventana.after(0, lambda: self.campo_pregunta.config(state=tk.NORMAL))
        self.ventana.after(0, lambda: self.campo_pregunta.focus_set())

    def ejecutar(self):
        """Inicia el bucle de eventos de la aplicación."""
        self.ventana.mainloop()


if __name__ == "__main__":
    # Permite ejecutar el script directamente según lo solicitado en el enunciado
    app = AsistenteGUI()
    app.ejecutar()
