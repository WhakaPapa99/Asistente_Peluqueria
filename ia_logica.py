import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


class AsistentePeluqueria:
    def __init__(self, ruta_contexto="contexto.txt", ruta_servicios="servicios.txt"):
        """
        Constructor:
        1. Carga las variables de entorno desde el archivo .env usando python-dotenv.
        2. Configura la API Key de forma segura sin exponerla en el código.
        3. Carga el contexto de la función del asistente desde contexto.txt y la información de servicios desde servicios.txt.
        4. Inicializa el modelo generativo de Gemini con las instrucciones del sistema cargadas.
        """
        # Cargar variables del archivo .env al entorno de ejecución del sistema operativo
        load_dotenv()
        
        # Recuperar la clave API de las variables de entorno para cumplir la política de seguridad
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                "No se encontró la variable 'API_KEY' en el archivo .env. "
                "Por favor, crea un archivo .env con: API_KEY=tu_clave_aqui"
            )

        # Configurar la librería oficial de Gemini con la clave obtenida
        genai.configure(api_key=self.api_key)

        # Leer íntegramente el contexto de su función (contexto.txt) y los servicios (servicios.txt)
        # De esta forma evitamos texto 'hardcodeado' en el código: todo el comportamiento,
        # servicios, precios y reglas se configuran en los archivos externos.
        self.instrucciones_sistema = self._cargar_contexto(ruta_contexto, ruta_servicios)

        # Usamos gemini-3.5-flash-lite: es el modelo actual recomendado por Google para respuestas rápidas y cuota gratuita
        nombre_modelo = os.getenv("MODELO_GEMINI", "gemini-3.5-flash-lite")
        self.modelo = genai.GenerativeModel(
            model_name=nombre_modelo,
            system_instruction=self.instrucciones_sistema,
            generation_config={"response_mime_type": "application/json"}
        )

    def _leer_archivo(self, ruta_archivo: str) -> str:
        """Lee y devuelve el contenido de un archivo de texto en UTF-8."""
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            raise FileNotFoundError(
                f"No se encontró el archivo '{ruta_archivo}' en la raíz del proyecto."
            )
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
        if not contenido:
            raise ValueError(f"El archivo '{ruta_archivo}' está vacío.")
        return contenido

    def _cargar_contexto(self, ruta_contexto: str, ruta_servicios: str) -> str:
        """
        Lee el archivo de contexto de la función del asistente (contexto.txt) y el archivo
        con la información de los servicios (servicios.txt), combinándolos para la IA.
        Permite desacoplar totalmente los datos y el rol del código fuente de la aplicación.
        """
        contexto_funcion = self._leer_archivo(ruta_contexto)
        info_servicios = self._leer_archivo(ruta_servicios)

        return f"{contexto_funcion}\n\n{info_servicios}"

    def consultar(self, pregunta: str) -> str:
        """
        Envía la consulta del usuario a Gemini y procesa la respuesta JSON.
        Retorna la cadena de texto limpia lista para ser mostrada en la interfaz gráfica.
        """
        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta válida."

        try:
            # Enviar la consulta al modelo
            respuesta_api = self.modelo.generate_content(pregunta)
            texto_crudo = respuesta_api.text

            # Manejo del objeto JSON según los requisitos de la práctica
            try:
                datos_json = json.loads(texto_crudo)
                # Extraemos únicamente el campo 'respuesta' evitando caracteres o metadatos innecesarios
                mensaje_final = datos_json.get("respuesta", texto_crudo)
            except json.JSONDecodeError:
                # Fallback defensivo: si por algún motivo no vino un JSON estricto, mostramos el texto limpio
                mensaje_final = texto_crudo

            # Limpiamos asteriscos residuales de Markdown (**negrita**) para que el texto se vea impecable en Tkinter
            mensaje_final = mensaje_final.replace("**", "").replace("__", "")

            return mensaje_final.strip()

        except Exception as error:
            # Reenviamos el error para que la interfaz gráfica pueda capturarlo y mostrar un aviso al usuario
            raise RuntimeError(f"Error al comunicar con la IA: {error}")
