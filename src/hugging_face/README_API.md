# LexiScope API - API REST para Análisis de Texto

API REST construida con FastAPI que permite analizar textos y extraer tópicos y keywords automáticamente usando modelos de Hugging Face.

## 🚀 Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar la API Key de Hugging Face:
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key
HUGGINGFACE_API_KEY=tu_api_key_aquí
```

## 🏃 Ejecución

### Opción 1: Ejecutar directamente
```bash
python api.py
```

### Opción 2: Usar uvicorn
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación

Una vez ejecutada la API, accede a:

- **Documentación interactiva (Swagger UI)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 🔌 Endpoints

### `GET /`
Información general de la API.

**Respuesta:**
```json
{
  "name": "LexiScope API",
  "version": "1.0.0",
  "description": "API para extracción de tópicos y keywords",
  "endpoints": {
    "POST /analyze": "Analizar texto y extraer tópicos y keywords",
    "GET /health": "Verificar estado de la API",
    "GET /docs": "Documentación interactiva de la API"
  }
}
```

### `GET /health`
Verificar el estado de salud de la API.

**Respuesta:**
```json
{
  "status": "healthy",
  "api_key_configured": true
}
```

### `POST /analyze`
Analizar texto y extraer tópicos y keywords.

**Cuerpo de la petición:**
```json
{
  "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.",
  "model": "moonshotai/Kimi-K2-Instruct-0905"
}
```

**Parámetros:**
- `text` (requerido): El texto a analizar
- `model` (opcional): Modelo de Hugging Face a usar. Por defecto: `moonshotai/Kimi-K2-Instruct-0905`

**Respuesta exitosa:**
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

## 💡 Ejemplos de Uso

### cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
  }'
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/analyze"
data = {
    "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
}

response = requests.post(url, json=data)
print(response.json())
```

### Python (httpx - async)

```python
import httpx
import asyncio

async def analyze_text():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/analyze",
            json={
                "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
            }
        )
        return response.json()

result = asyncio.run(analyze_text())
print(result)
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### JavaScript (axios)

```javascript
const axios = require('axios');

axios.post('http://localhost:8000/analyze', {
  text: 'La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.'
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error('Error:', error);
});
```

## 🔧 Configuración Avanzada

### Cambiar el puerto

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

### Usar un modelo diferente

Puedes especificar un modelo diferente en cada petición:

```python
data = {
    "text": "Tu texto aquí",
    "model": "google/gemma-2-9b-it"  # Modelo alternativo
}
```

### CORS

La API está configurada para aceptar peticiones desde cualquier origen. Si necesitas restringir esto, edita la configuración de CORS en `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Especifica orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Manejo de Errores

La API retorna códigos de estado HTTP apropiados:

- `200`: Éxito
- `422`: Error de validación (parámetros inválidos)
- `500`: Error del servidor (problema con la API de Hugging Face o configuración)

Ejemplo de respuesta con error:

```json
{
  "detail": "API Key de Hugging Face no configurada. Por favor configura HUGGINGFACE_API_KEY en el archivo .env"
}
```

## 📝 Notas

- La API usa el modelo `moonshotai/Kimi-K2-Instruct-0905` por defecto
- Se requiere una API key válida de Hugging Face
- Los textos son procesados en español por defecto
- La temperatura está configurada en 0.7 para equilibrar creatividad y consistencia
- El límite de tokens de respuesta es 500

## 🤝 Comparación con el Script Original

| Característica | Script Original | API REST |
|---------------|-----------------|----------|
| Interfaz | CLI | HTTP REST API |
| Uso | Ejecutar script | Petición HTTP |
| Integración | Limitada | Universal |
| Formato salida | Imprime JSON | Retorna JSON |
| Documentación | Manual | Auto-generada (Swagger) |
| Validación | Manual | Automática (Pydantic) |
| Escalabilidad | Proceso único | Multi-proceso/async |

## 📄 Licencia

Mismo que el proyecto LexiScope principal.
