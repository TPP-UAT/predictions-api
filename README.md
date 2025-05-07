# 📄 API de Predicciones

Este proyecto es una API desarrollada con FastAPI que permite realizar predicciones o análisis de texto utilizando modelos de procesamiento de lenguaje natural (NLP) y otras herramientas.

## 🛠️ Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.8 o superior

## Instalación

1. Instala las siguientes librerías (pueden instalarse con pip):

   ```bash
   pip install fastapi uvicorn spacy pymupdf python-multipart
   ```

2. Descarga el modelo de spaCy requerido:

   ```bash
   python -m spacy download en_core_web_md
   ```

3. Crea un archivo `.env` en la raíz del proyecto y añade la URL del host de la base de datos:

    ```
    DATABASE_URL=tu_url_de_base_de_datos
    ```

## ▶️ Ejecución

Para iniciar el servidor de desarrollo, ejecuta:

```bash
uvicorn main:app --reload
```

## 🚀 Uso

Una vez iniciado el servidor, puedes acceder a la documentación interactiva de la API mediante swagger en:

- [http://localhost:8000/docs](http://localhost:8000/docs)

### Endpoints Disponibles

- **Predicción de Palabras Clave**: Envía uno o más archivos en formato PDF a este endpoint para obtener las palabras clave predichas. El endpoint `/predict` procesa el archivo y devuelve las predicciones basadas en el contenido del PDF.

- **Recomendación de Artículos Similares**: Envía uno o más archivos en formato PDF a este endpoint para recibir recomendaciones de artículos similares alojados en la base de datos. El endpoint `/recommend` utiliza las predicciones para sugerir artículos relacionados basado en los descriptores de los artículos almacenados en la base de datos.


