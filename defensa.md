# 🎓 Guía Maestra para la Defensa del Proyecto (Acceso a Datos - RA1)

> **Criterio de Evaluación Prioritario (35% de la nota final):**  
> *"El alumno explica con fluidez cómo funciona la comunicación con Gemini. Entiende la diferencia entre 'entrenar' y 'dar contexto'. Sabe explicar línea por línea cómo se cargan las variables de entorno. Indicios de código sin saber explicar partes críticas = Suspenso automático."*

---

## 1. El Resumen de 30 Segundos (Elevator Pitch)
Si el profesor te dice: *«Cuéntame qué has hecho y cómo funciona tu proyecto»*, responde con esto:

> *"He desarrollado un asistente virtual de escritorio para la **Peluquería Paco** utilizando **Python**, una interfaz gráfica en **Tkinter** y la **API de Google Gemini**.  
> El sistema aplica **In-Context Learning** leyendo un archivo externo de contexto con las tarifas y normas del negocio, forzando a la IA a responder exclusivamente sobre la peluquería y a devolver los datos en formato estructurado **JSON**.  
> Para que la aplicación sea robusta y profesional, las consultas a la nube se ejecutan en **segundo plano mediante hilos (`threading`)**, evitando que la ventana se congele, y la clave API se mantiene oculta y segura mediante variables de entorno con **`python-dotenv`**."*

---

## 2. El Flujo de Datos (Arquitectura de 4 Pasos)
Ten muy clara la secuencia de cómo viaja la información desde que el usuario pulsa una tecla hasta que lee la respuesta:

```text
[ Usuario escribe en Entry y pulsa Enter o clic en botón ]
                          ↓
[ Interfaz gráfica (asistente_gui.py) ]
  - Pinta el mensaje del usuario en el chat.
  - Vaciá el campo Entry y bloquea el botón para evitar spam.
  - Lanza un hilo secundario (Thread) con la consulta.
                          ↓
[ Hilo de Lógica (ia_logica.py) ]
  - Inyecta la pregunta al modelo Gemini (gemini-3.5-flash-lite).
  - El modelo ya tiene cargado el contexto desde contexto.txt.
  - Gemini procesa y devuelve una respuesta estructurada en formato JSON.
                          ↓
[ Parseo y Vuelta a la Interfaz ]
  - Se valida y extrae el texto del JSON con json.loads().
  - Se limpia cualquier residuo de formato.
  - Mediante ventana.after(), se actualiza el chat en el hilo principal y se reactiva el botón.
```

---

## 3. Las 6 Preguntas Clave que te va a hacer el Profesor

### Pregunta 1: ¿Por qué usas variables de entorno y cómo se cargan? (Línea por línea)
* **¿Por qué?**  
  > *"Por seguridad y buenas prácticas. Las claves API son credenciales privadas con coste y cuotas. Si la escribo directamente en el código (`API_KEY = "AIza..."`), cualquiera que vea el archivo o lo clone de GitHub podría robarla. Además, la rúbrica penaliza con suspenso inmediato hardcodear claves."*
* **Explicación del código en `ia_logica.py`**:
  ```python
  from dotenv import load_dotenv
  import os

  load_dotenv()                       # 1. Busca el archivo .env en la raíz y carga sus claves en la memoria del sistema
  self.api_key = os.getenv("API_KEY") # 2. Lee el valor asociado a la clave 'API_KEY' del entorno del sistema operativo
  if not self.api_key:
      raise ValueError(...)           # 3. Validación defensiva: si el archivo no existe o está vacío, detiene la app con aviso claro
  genai.configure(api_key=self.api_key) # 4. Configura el cliente oficial de Google con la clave recuperada
  ```

---

### Pregunta 2: ¿Qué diferencia hay entre "entrenar un modelo" y "dar contexto" (*In-Context Learning*)?
* **Entrenar (Fine-Tuning / Pre-entrenamiento)**:  
  > *"Implica modificar los pesos matemáticos de las capas de la red neuronal mediante miles de ejemplos y un gran coste computacional y de tiempo. Se usa para enseñar habilidades nuevas desde cero."*
* **Dar Contexto (*In-Context Learning*)**:  
  > *"Aprovecha que Gemini ya es un modelo gigante que sabe hablar, razonar y redactar. Nosotros no cambiamos sus pesos matemáticos, simplemente le suministramos información específica en el prompt del sistema (`system_instruction`). Gemini lee nuestros precios y normas como si fuera un examen a libro abierto y responde ciñéndose a ellos. Es inmediato, flexible y no tiene coste de entrenamiento."*

---

### Pregunta 3: ¿Por qué desacoplaste el contexto en `contexto.txt` en vez de escribirlo en el código Python?
> *"Para cumplir con el principio de separación de responsabilidades. Si el dueño de la peluquería cambia los precios, añade un nuevo pack o modifica el horario, **no tiene que tocar ni compilar código Python**. Solo edita el archivo de texto y el asistente se adapta al instante. Además, el código queda mucho más limpio y profesional."*

---

### Pregunta 4: ¿Por qué usas el modelo `gemini-3.5-flash-lite` y no `gemini-1.5-flash`?
> *"Porque investigué la disponibilidad de modelos con `genai.list_models()`. Google descatalogó las versiones 1.5 para nuevas cuentas de desarrollador (daban error HTTP 404 Not Found). `gemini-3.5-flash-lite` es el modelo moderno recomendado oficialmente para asistentes conversacionales ligeros: ofrece respuestas prácticamente instantáneas, bajo consumo de cuota gratuita y soporte nativo para salidas JSON estructuradas."*

---

### Pregunta 5: ¿Por qué utilizas hilos (`threading.Thread`) en Tkinter?
> *"Tkinter tiene un único hilo principal de ejecución donde corre `ventana.mainloop()`. Este bucle se encarga de escuchar los clics del ratón, redibujar la ventana y responder al sistema operativo.  
> La petición a la API de Google tarda entre 1 y 2 segundos en viajar por internet. Si hiciera esa llamada en el hilo principal, la interfaz gráfica se congelaría por completo y Windows mostraría el aviso de **'(No responde)'**.  
> Al lanzarlo en un `Thread` secundario (`daemon=True`), la consulta ocurre en paralelo y la ventana sigue respondiendo con fluidez."*

---

### Pregunta 6: ¿Cómo manejas las respuestas JSON y evitas caracteres extraños?
> *"En la llamada a Gemini activamos `generation_config={"response_mime_type": "application/json"}` y en las instrucciones exigimos la estructura `{"respuesta": "..."}`.  
> Al recibir el texto crudo en Python:
> 1. Usamos `json.loads(texto_crudo)` para transformarlo en un diccionario nativo de Python.
> 2. Obtenemos el texto con `.get("respuesta", texto_crudo)`.
> 3. Eliminamos posibles asteriscos de Markdown (`**`) para que en la ventana de Tkinter el texto se lea limpio y sin códigos de formato rotos."*

---

## 4. Partes del Código que debes Saber Señalar

Abre tus archivos en el editor y ten localizadas estas líneas exactas:

### En [ia_logica.py](file:///f:/2DAM/Acceso_de_datos/RA1/Desafio_Asistente/ia_logica.py):
* **Carga de variables**: Líneas 18 a 30 (`load_dotenv()` y `os.getenv`).
* **Carga del archivo de contexto**: Método `_cargar_contexto()` (busca `contexto.txt` o `servicios.txt` con codificación `utf-8`).
* **Inicialización del modelo**: Líneas 40 a 45 (pasando `system_instruction` y `response_mime_type="application/json"`).
* **Parseo JSON y limpieza**: Método `consultar()` (bloque `try / except json.JSONDecodeError` y `.replace("**", "")`).

### En [asistente_gui.py](file:///f:/2DAM/Acceso_de_datos/RA1/Desafio_Asistente/asistente_gui.py):
* **Creación del área de texto con scroll**: `scrolledtext.ScrolledText(..., wrap=tk.WORD, state=tk.DISABLED)`.
  * *¿Por qué `state=DISABLED`?* Para que el usuario no pueda borrar o editar el historial con el teclado.
* **Inserción de texto en chat**: Método `_agregar_mensaje()`, donde se pone temporalmente `state=NORMAL`, se hace `insert(tk.END, ...)`, `see(tk.END)` para hacer auto-scroll al fondo, y se vuelve a poner `state=DISABLED`.
* **Vaciado del cuadro de entrada**: `self.campo_pregunta.delete(0, tk.END)`.
* **Atajo de la tecla Enter**: `self.ventana.bind("<Return>", lambda event: self.enviar_mensaje())`.
* **Lanzamiento del hilo en segundo plano**: `threading.Thread(target=self._hilo_consultar_ia, args=(pregunta,))`.
* **Actualización segura de la GUI**: `self.ventana.after(0, ...)`, porque en Tkinter solo el hilo principal debe modificar directamente los widgets.

---

## 5. Preguntas Trampa que el Profesor puede Escribir en el Chat durante la Demo

Para probar si tu asistente realmente tiene contexto o si alucina, el profesor tecleará preguntas como estas. Conoce de antemano lo que responderá:

| Pregunta del Profesor | Qué responderá el Asistente | Por qué gana puntos |
| :--- | :--- | :--- |
| *«¿Tenéis ofertas si me hago corte y barba?»* | Responderá recomendando el **Pack Completo Paco por 20 €**, indicando que se ahorra 5 €. | Demuestra que la IA comprende las ofertas del contexto y las promociona. |
| *«¿Puedo pagar con Bizum?»* | Responderá afirmativamente, indicando que se acepta Bizum, tarjeta y efectivo. | Confirma que lee la sección de pagos de [contexto.txt](file:///f:/2DAM/Acceso_de_datos/RA1/Desafio_Asistente/contexto.txt). |
| *«¿Cuánto cuesta el corte para mi abuelo de 70 años?»* | Responderá con la tarifa de **Corte para jubilados y pensionistas (8 €)**. | Reconoce sinónimos semánticos y categorías de clientes. |
| *«¿Cuál es la fórmula del agua?»* o *«¿Quién es el presidente de Francia?»* | Rechazará educadamente la pregunta diciendo que **solo está capacitado para responder dudas sobre Peluquería Paco**. | Demuestra delimitación estricta de seguridad contra alucinaciones fuera del negocio. |
| *«¿Qué pasa si desconecto el cable de internet y le pregunto algo?»* | Saldrá una ventana emergente (`messagebox.showerror`) avisando del fallo de conexión y la app **no crasheará**. | Cumple el requisito de gestión defensiva de excepciones. |

---

## 6. Checklist Mental antes de Sentarte frente al Profesor

- [x] El repositorio de GitHub está creado y sincronizado: `https://github.com/WhakaPapa99/Asistente_Peluqueria`.
- [x] El archivo `.env` **NO** está en GitHub (lo protege `.gitignore`).
- [x] El archivo `requirements.txt` contiene `google-generativeai` y `python-dotenv`.
- [x] El archivo `servicios.txt` y `contexto.txt` existen y están actualizados con las tarifas en euros de Peluquería Paco.
- [x] Sabes explicar qué es un hilo (`Thread`) y por qué evita que la ventana se cuelgue.
- [x] Sabes explicar la diferencia entre reentrenar y dar contexto (*In-Context Learning*).
