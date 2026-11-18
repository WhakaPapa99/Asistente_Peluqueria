import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


class AsistentePeluqueria:
    def __init__(self, ruta_contexto="contexto.txt", ruta_servicios="servicios.txt"):
        load_dotenv()

        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                "No se encontró la variable 'API_KEY' en el archivo .env. "
                "Por favor, crea un archivo .env con: API_KEY=tu_clave_aqui"
            )

        genai.configure(api_key=self.api_key)

        self.instrucciones_sistema = self._cargar_contexto(ruta_contexto, ruta_servicios)

        nombre_modelo = os.getenv("MODELO_GEMINI", "gemini-3.5-flash-lite")
        self.modelo = genai.GenerativeModel(
            model_name=nombre_modelo,
            system_instruction=self.instrucciones_sistema,
            generation_config={"response_mime_type": "application/json"}
        )

    def _leer_archivo(self, ruta_archivo: str) -> str:
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

        contexto_funcion = self._leer_archivo(ruta_contexto)
        info_servicios = self._leer_archivo(ruta_servicios)

        return f"{contexto_funcion}\n\n{info_servicios}"

    def consultar(self, pregunta: str) -> str:

        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta válida."

        try:
            respuesta_api = self.modelo.generate_content(pregunta)
            texto_crudo = respuesta_api.text

            try:
                datos_json = json.loads(texto_crudo)
                mensaje_final = datos_json.get("respuesta", texto_crudo)
            except json.JSONDecodeError:
                mensaje_final = texto_crudo

            mensaje_final = mensaje_final.replace("**", "").replace("__", "")

            return mensaje_final.strip()

        except Exception as error:
            raise RuntimeError(f"Error al comunicar con la IA: {error}")
