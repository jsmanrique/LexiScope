import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="LexiScope API - OpenAI",
    description="API REST para extracción de tópicos y keywords usando OpenAI",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modelo por defecto
DEFAULT_MODEL = "gpt-4o-mini"


# Modelos de datos Pydantic
class TextInput(BaseModel):
    text: str = Field(..., description="Texto a analizar", min_length=1)
    model: Optional[str] = Field(
        default=DEFAULT_MODEL,
        description="Modelo de OpenAI a utilizar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.",
                "model": "gpt-4o-mini"
            }
        }


class AnalysisResponse(BaseModel):
    language: str = Field(description="Idioma del texto")
    topics: List[str] = Field(description="Lista de tópicos principales (3-5)")
    keywords: List[str] = Field(description="Lista de palabras clave (5-10)")

    class Config:
        json_schema_extra = {
            "example": {
                "language": "es",
                "topics": ["digitalización industrial", "inteligencia artificial", "industria 4.0"],
                "keywords": ["digitalización", "industrial", "España", "gemelos digitales", "mantenimiento predictivo", "IA"]
            }
        }


# Función principal de análisis
def analyze_text(texto: str, modelo: str = DEFAULT_MODEL) -> dict:
    """
    Extrae tópicos (3–5) y keywords (5–10) del texto proporcionado usando OpenAI.
    Devuelve un diccionario con la estructura esperada.
    """
    
    # Esquema JSON para validación estructurada
    schema = {
        "type": "object",
        "properties": {
            "language": {"type": "string", "example": "es"},
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3, "maxItems": 5
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 5, "maxItems": 10,
                "examples": ["IA", "gemelo digital"]
            }
        },
        "required": ["language", "topics", "keywords"],
        "additionalProperties": False,
        "examples": [{
            "language": "es",
            "topics": ["Digitalización", "Tecnologías emergentes", "Industria 4.0"],
            "keywords": ["gemelo digital", "mantenimiento predictivo", "IA", "transformación digital", "tecnología"]
        }]
    }

    try:
        # Llamada a la API de OpenAI con respuesta estructurada
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en NLP que extrae tópicos y keywords con formato JSON."},
                {"role": "user", "content": f"""
Extrae tópicos y palabras clave del texto en español de la siguiente forma:
TÓPICOS: (3–5) etiquetas breves 
KEYWORDS: (5–10) términos relevantes en el dominio
Devuelve SOLO un JSON válido que cumpla el esquema

{texto}
"""}
            ],
            response_format={
                "type": "json_schema", 
                "json_schema": {
                    "name": "topics_keywords_schema",
                    "schema": schema
                }
            },
            temperature=1.0
        )
        
        # Extraer y parsear el contenido de la respuesta
        content = response.choices[0].message.content
        result = json.loads(content)
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        print(f"Respuesta recibida: {content}")
        raise Exception(f"Error al parsear JSON: {str(e)}")
    except Exception as e:
        print(f"Error en la llamada a la API: {e}")
        raise Exception(f"Error en la llamada a la API de OpenAI: {str(e)}")


# Endpoints de la API
@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "name": "LexiScope API - OpenAI",
        "version": "1.0.0",
        "description": "API para extracción de tópicos y keywords usando OpenAI",
        "endpoints": {
            "POST /analyze": "Analizar texto y extraer tópicos y keywords",
            "GET /health": "Verificar estado de la API",
            "GET /docs": "Documentación interactiva de la API"
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Verificar el estado de salud de la API"""
    api_key_loaded = os.getenv("OPENAI_API_KEY") is not None
    return {
        "status": "healthy",
        "api_key_configured": api_key_loaded
    }


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_endpoint(input_data: TextInput):
    """
    Analiza un texto y extrae tópicos y keywords usando OpenAI.
    
    - **text**: El texto a analizar (mínimo 1 carácter)
    - **model**: (Opcional) Modelo de OpenAI a usar (por defecto: gpt-4o-mini)
    
    Retorna un objeto JSON con:
    - **language**: Idioma detectado del texto
    - **topics**: Lista de 3-5 tópicos principales
    - **keywords**: Lista de 5-10 palabras clave
    """
    
    # Verificar que la API key esté configurada
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="API Key de OpenAI no configurada. Por favor configura OPENAI_API_KEY en el archivo .env"
        )
    
    try:
        # Analizar el texto
        result = analyze_text(input_data.text, input_data.model)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
