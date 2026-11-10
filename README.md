# 💈 Asistente Virtual con IA - Peluquería Paco

Aplicación de escritorio interactiva desarrollada en **Python** con **Tkinter** y la **API de Google Gemini**.  
Proyecto correspondiente al módulo de **Acceso a Datos** en el ciclo formativo de grado superior de Desarrollo de Aplicaciones Multiplataforma (**2DAM**).

---

## 📖 Descripción del Proyecto

La aplicación implementa un asistente virtual inteligente capaz de atender a clientes de la **Peluquería y Barbería Paco**, resolviendo dudas sobre servicios, tarifas en euros (€), horarios, ofertas especiales y métodos de pago.

El asistente utiliza técnicas de **In-Context Learning** para delimitar el comportamiento del modelo sin necesidad de reentrenarlo, respondiendo exclusivamente en el ámbito del negocio y devolviendo respuestas estructuradas en formato **JSON**.

---

## 🛠️ Tecnologías y Librerías

* **Python 3.10+**
* **Tkinter**: Interfaz gráfica nativa de usuario.
* **Google Gemini API (`google-generativeai`)**: Modelo de lenguaje generativo (`gemini-3.5-flash-lite`).
* **python-dotenv**: Gestión segura de credenciales y variables de entorno.
* **Threading**: Ejecución asíncrona para evitar el bloqueo de la interfaz gráfica.

---

## 📂 Estructura del Proyecto

El código sigue una arquitectura desacoplada y modular:

```text
Desafio_Asistente/
│
├── main.py                     # Punto de entrada principal y limpio de la aplicación
├── asistente_gui.py            # Módulo de la interfaz gráfica construida con Tkinter
├── ia_logica.py                # Módulo de lógica, conexión con Gemini y parseo de JSON
├── contexto.txt                # Contexto íntegro, normas de comportamiento y tarifas para la IA
├── servicios.txt               # Carta oficial de servicios, packs y horarios de la peluquería
├── requirements.txt            # Dependencias del proyecto
├── .env.example                # Plantilla de variables de entorno (sin exponer claves)
├── .gitignore                  # Protección para no subir .env ni cachés a GitHub
└── README.md                   # Documentación del proyecto
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio o descargar el proyecto
```bash
git clone https://github.com/WhakaPapa99/Asistente_Peluqueria.git
cd Desafio_Asistente
```

### 2. Crear y activar el entorno virtual
En Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la clave de la API de Google Gemini
1. Obtén una clave de API gratuita en [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Crea un archivo llamado `.env` en la raíz del proyecto (puedes duplicar `.env.example`):
   ```env
   API_KEY=tu_clave_api_aqui
   ```
> ⚠️ **Importante:** El archivo `.env` está incluido en `.gitignore` para garantizar que la clave nunca se publique en repositorios públicos.

### 5. Ejecutar la aplicación
Puedes iniciar la aplicación ejecutando cualquiera de los dos scripts:
```powershell
python main.py
# o también:
python asistente_gui.py
```

---

## 🌟 Características Técnicas Destacadas

### 1. Desacoplamiento de Contexto (*In-Context Learning*)
El prompt del sistema no está incrustado (*hardcodeado*) en el código Python. Se lee dinámicamente desde `contexto.txt`. Si cambian precios o normativas, solo se edita el archivo de texto y el asistente se actualiza de inmediato.

### 2. Experiencia de Usuario sin Congelamiento (*Threading*)
Las consultas a los servidores de Google se ejecutan en un hilo secundario (`threading.Thread`). De esta forma, la interfaz de Tkinter se mantiene fluida y responsiva mientras la IA genera la respuesta, sin mostrar el mensaje de *(No responde)*.

### 3. Respuestas Estructuradas en JSON
Se configura el modelo con `response_mime_type="application/json"` exigiendo la estructura:
```json
{
  "respuesta": "Texto de la respuesta para el usuario"
}
```
En Python se parsea el JSON con `json.loads()` y se extrae el texto limpio y sanitizado de caracteres extraños.

### 4. Delimitación Estricta y Seguridad
El asistente rechaza amablemente cualquier consulta ajena a la peluquería (por ejemplo, preguntas generales, de programación o deportes), evitando alucinaciones fuera del contexto del negocio.

---

## 👨‍💻 Autor
Proyecto realizado para el módulo de **Acceso a Datos** (2º DAM).
