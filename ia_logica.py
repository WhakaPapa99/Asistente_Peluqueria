
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


class AsistentePeluqueria:
    def __init__(self, ruta_contexto="contexto.txt"):
        """
        Constructor:
        1. Carga las variables de entorno desde el archivo .env usando python-dotenv.
        2. Configura la API Key de forma segura sin exponerla en el código.
        3. Carga el contexto y las reglas del asistente desde el archivo externo (contexto.txt o servicios.txt).
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

        # Leer íntegramente el contexto y las instrucciones desde el archivo externo
        # De esta forma evitamos texto 'hardcodeado' en el código: todo el comportamiento,
        # servicios, precios y reglas se configuran en el archivo .txt/.md externo.
        self.instrucciones_sistema = self._cargar_contexto(ruta_contexto)

        # Usamos gemini-3.5-flash-lite: es el modelo actual recomendado por Google para respuestas rápidas y cuota gratuita
        nombre_modelo = os.getenv("MODELO_GEMINI", "gemini-3.5-flash-lite")
        self.modelo = genai.GenerativeModel(
            model_name=nombre_modelo,
            system_instruction=self.instrucciones_sistema,
            generation_config={"response_mime_type": "application/json"}
        )

    def _cargar_contexto(self, ruta_archivo):
        """
        Lee el archivo externo con el contexto y las instrucciones del asistente (.txt o .md).
        Permite desacoplar totalmente los datos del código fuente de la aplicación.
        """
        # Lista de rutas prioritarias donde buscar el archivo de contexto
        rutas_candidatas = [ruta_archivo, "contexto.txt", "contexto.md", "servicios.txt"]

        for ruta in rutas_candidatas:
            if ruta and os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()
                    if contenido:
                        return contenido

        raise FileNotFoundError(
            f"No se pudo cargar el contexto para la IA. "
            f"Asegúrate de que existe '{ruta_archivo}', 'contexto.txt' o 'servicios.txt' en la raíz del proyecto."
        )

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
