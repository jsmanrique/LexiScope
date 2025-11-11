# LexiScope

**LexiScope** es una prueba de concepto (PoC) minimalista de un servicio y conjunto de herramientas para extraer tópicos y palabras clave de textos en español utilizando modelos de lenguaje avanzados.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
  - [Script de Hugging Face](#script-de-hugging-face)
  - [Script de OpenAI](#script-de-openai)
  - [API REST (Hugging Face)](#api-rest-hugging-face)
  - [API REST (OpenAI)](#api-rest-openai)
- [Ejemplos de Salida](#-ejemplos-de-salida)
- [Documentación Adicional](#-documentación-adicional)
- [Licencia](#-licencia)

## ✨ Características

- 🤖 **Dos implementaciones**: Hugging Face y OpenAI
- 🌐 **API REST**: Servicio web completo con FastAPI
- 📊 **Extracción inteligente**: 3-5 tópicos y 5-10 keywords por texto
- 🔒 **Seguridad**: Gestión de API keys mediante variables de entorno
- 📝 **Documentación automática**: Swagger UI y ReDoc integrados
- 🇪🇸 **Optimizado para español**: Análisis especializado en textos en castellano

## 📁 Estructura del Proyecto

```
LexiScope/
├── src/
│   ├── hugging_face/
│   │   ├── .env.example          # Plantilla de configuración
│   │   ├── huggingface.py        # Script CLI para extracción
│   │   ├── api.py                # API REST con FastAPI
│   │   └── requirements.txt      # Dependencias de Hugging Face
│   └── openai/
│       ├── .env.example          # Plantilla de configuración
│       ├── nopenai.py            # Script CLI para extracción
│       ├── api.py                # API REST con FastAPI
│       └── requirements.txt      # Dependencias de OpenAI
├── LICENSE                       # Licencia MIT
└── README.md                     # Este archivo
```

## 🔧 Requisitos Previos

- **Python 3.8+**
- **pip** (gestor de paquetes de Python)
- Una cuenta en [Hugging Face](https://huggingface.co/) o [OpenAI](https://openai.com/) según la implementación que vayas a usar

## 📦 Instalación

### Instalación para Hugging Face

```bash
cd src/hugging_face
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `huggingface-hub` - Cliente para la API de Hugging Face
- `python-dotenv` - Gestión de variables de entorno
- `fastapi` - Framework para la API REST
- `uvicorn[standard]` - Servidor ASGI para FastAPI
- `pydantic` - Validación de datos

### Instalación para OpenAI

```bash
cd src/openai
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `openai` - Cliente oficial de OpenAI
- `python-dotenv` - Gestión de variables de entorno
- `fastapi` - Framework para la API REST
- `uvicorn[standard]` - Servidor ASGI para FastAPI
- `pydantic` - Validación de datos

## ⚙️ Configuración

### Configurar Hugging Face

1. Navega al directorio de Hugging Face:
```bash
cd src/hugging_face
```

2. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

3. Edita el archivo `.env` y añade tu API key:
```
HUGGINGFACE_API_KEY=tu_api_key_aquí
```

> 💡 **Obtener API Key**: Regístrate en [Hugging Face](https://huggingface.co/), ve a Settings → Access Tokens y crea un nuevo token.

### Configurar OpenAI

1. Navega al directorio de OpenAI:
```bash
cd src/openai
```

2. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

3. Edita el archivo `.env` y añade tu API key:
```
OPENAI_API_KEY=tu_api_key_aquí
```

> 💡 **Obtener API Key**: Inicia sesión en [OpenAI Platform](https://platform.openai.com/), ve a API keys y crea una nueva.

## 🚀 Uso

### Script de Hugging Face

El script `huggingface.py` extrae tópicos y keywords desde la línea de comandos.

**Ejecutar el script:**

```bash
cd src/hugging_face
python huggingface.py
```

**Personalizar el texto a analizar:**

Edita el archivo `huggingface.py` y modifica la variable `texto` en la sección `if __name__ == "__main__":`:

```python
if __name__ == "__main__":
    # Modifica este texto con el contenido que quieras analizar
    texto = "Tu texto aquí..."
    
    resultado = topics_and_keywords(texto)
    print(resultado)
```

**Modelos disponibles:**

Por defecto usa `moonshotai/Kimi-K2-Instruct-0905`. Puedes cambiarlo editando la variable `model` en el archivo:

```python
model: str = "moonshotai/Kimi-K2-Instruct-0905"
# model: str = "google/gemma-2-9b-it"  # Alternativa
```

### Script de OpenAI

El script `nopenai.py` utiliza la API de OpenAI con validación de esquema JSON.

**Ejecutar el script:**

```bash
cd src/openai
python nopenai.py
```

**Personalizar el texto a analizar:**

Edita el archivo `nopenai.py` y modifica la variable `texto`:

```python
if __name__ == "__main__":
    texto = "Tu texto aquí..."
    print(topics_and_keywords_openai(texto))
```

**Modelos disponibles:**

Por defecto usa `gpt-4o-mini`. Puedes cambiarlo pasando el parámetro `modelo`:

```python
resultado = topics_and_keywords_openai(texto, modelo="gpt-4")
```

### API REST (OpenAI)

La implementación de OpenAI también incluye una API REST construida con FastAPI.

#### Iniciar el servidor

**Opción 1: Ejecución directa**
```bash
cd src/openai
python api.py
```

**Opción 2: Usando uvicorn (recomendado)**
```bash
cd src/openai
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

> 💡 **Nota**: Se recomienda usar un puerto diferente (8001) si ya tienes la API de Hugging Face ejecutándose en el puerto 8000.

La API estará disponible en: `http://localhost:8001`

#### Documentación interactiva

Una vez iniciado el servidor:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

#### Endpoints disponibles

Los endpoints son idénticos a la versión de Hugging Face:

**`GET /`** - Información general de la API

**`GET /health`** - Estado de salud del servicio

**`POST /analyze`** - Analizar texto y extraer tópicos y keywords

**Ejemplo de petición:**

```bash
curl -X POST "http://localhost:8001/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
  }'
```

**Ejemplo con Python:**

```python
import requests

response = requests.post(
    "http://localhost:8001/analyze",
    json={
        "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.",
        "model": "gpt-4o-mini"  # Opcional
    }
)

print(response.json())
```

**Modelos disponibles:**

- `gpt-4o-mini` (por defecto) - Rápido y económico
- `gpt-4o` - Mayor capacidad y precisión
- `gpt-4-turbo` - Balance entre rendimiento y coste
- `gpt-4` - Modelo más potente

### API REST (Hugging Face)

La API REST proporciona un servicio web completo para análisis de textos.

#### Iniciar el servidor

**Opción 1: Ejecución directa**
```bash
cd src/hugging_face
python api.py
```

**Opción 2: Usando uvicorn (recomendado)**
```bash
cd src/hugging_face
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

#### Documentación interactiva

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Endpoints disponibles

**`GET /`** - Información general de la API

**`GET /health`** - Estado de salud del servicio

**`POST /analyze`** - Analizar texto y extraer tópicos y keywords

**Ejemplo de petición:**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
  }'
```

**Ejemplo con Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
    }
)

print(response.json())
```

**Parámetros opcionales:**

```json
{
  "text": "Tu texto aquí",
  "model": "google/gemma-2-9b-it"
}
```

## 📊 Ejemplos de Salida

### Ejemplo 1: Digitalización Industrial

**Entrada:**
```
La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.
```

**Salida:**
```json
{
  "language": "es",
  "topics": [
    "digitalización industrial",
    "inteligencia artificial",
    "industria 4.0"
  ],
  "keywords": [
    "digitalización",
    "industrial",
    "España",
    "gemelos digitales",
    "mantenimiento predictivo",
    "IA"
  ]
}
```

### Ejemplo 2: Reconocimiento Facial

**Entrada:**
```
Apoyar la prohibición del reconocimiento facial en espacios públicos es un paso sensato: protege libertades civiles y reduce sesgos algorítmicos. Pero sin una auditoría tecnológica independiente y sanciones reales, la norma será solo papel mojado.
```

**Salida:**
```json
{
  "language": "es",
  "topics": [
    "privacidad",
    "reconocimiento facial",
    "regulación tecnológica",
    "derechos civiles"
  ],
  "keywords": [
    "reconocimiento facial",
    "espacios públicos",
    "libertades civiles",
    "sesgos algorítmicos",
    "auditoría tecnológica",
    "regulación",
    "privacidad"
  ]
}
```


## 🛠️ Desarrollo y Contribución

### Ejecutar en modo desarrollo

```bash
# API con recarga automática
uvicorn api:app --reload

# Ver logs detallados
uvicorn api:app --reload --log-level debug
```

### Cambiar puerto

```bash
uvicorn api:app --reload --port 8080
```

## ❗ Solución de Problemas

### Error: "API Key no configurada"

Asegúrate de haber creado el archivo `.env` y configurado correctamente la API key:

```bash
# Verifica que el archivo existe
ls -la .env

# Verifica el contenido (oculta la key real)
cat .env | grep API_KEY
```

### Error: "Module not found"

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Error de conexión con Hugging Face

Verifica tu conexión a internet y que la API key sea válida. Puedes probar la conexión directamente:

```python
from huggingface_hub import InferenceClient
import os

client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
print("Conexión exitosa!" if client else "Error de conexión")
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 LexiScope

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🤝 Contacto y Soporte

Para reportar problemas o sugerir mejoras, abre un issue en el repositorio del proyecto.

---

**Desarrollado con ❤️ para facilitar el análisis de textos en español**
