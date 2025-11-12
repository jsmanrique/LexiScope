# SPDX-FileCopyrightText: © 2025 J. Manrique Lopez de la Fuente <jsmanrique@gmail.com>
# SPDX-License-Identifier: MIT

"""api.py: API REST para extracción de tópicos y keywords de un texto usando Hugging Face API."""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from typing import List, Optional

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="LexiScope API",
    description="API REST para extracción de tópicos y keywords usando Hugging Face",
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

# Inicializar cliente de Hugging Face
client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))

# Modelo por defecto
DEFAULT_MODEL = "moonshotai/Kimi-K2-Instruct-0905"


# Modelos de datos Pydantic
class TextInput(BaseModel):
    text: str = Field(..., description="Texto a analizar", min_length=1)
    model: Optional[str] = Field(
        default=DEFAULT_MODEL,
        description="Modelo de Hugging Face a utilizar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA.",
                "model": "moonshotai/Kimi-K2-Instruct-0905"
            }
        }


class AnalysisResponse(BaseModel):
    language: str = Field(description="Idioma del texto")
    topics: List[str] = Field(description="Lista de tópicos principales (3-5)")
    keywords: List[str] = Field(description="Lista de palabras clave (5-10)")
    error: Optional[str] = Field(default=None, description="Mensaje de error si ocurrió alguno")

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
    Extrae tópicos (3–5) y keywords (5–10) del texto proporcionado.
    Devuelve un diccionario con la estructura esperada.
    """
    
    # Prompt detallado para guiar al modelo
    prompt = f"""Eres un asistente experto en NLP que extrae tópicos y palabras clave de textos en español.

Analiza el siguiente texto y extrae:
- TÓPICOS: Entre 3 y 5 etiquetas breves que resuman los temas principales
- KEYWORDS: Entre 5 y 10 términos relevantes del dominio

Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:
{{
  "language": "es",
  "topics": ["tema1", "tema2", "tema3"],
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"]
}}

TEXTO A ANALIZAR:
{texto}

RESPUESTA (solo JSON válido):"""

    try:
        # Llamada a la API de Hugging Face
        response = client.chat_completion(
            model=modelo,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extraer el contenido de la respuesta
        content = response.choices[0].message.content
        
        # Limpiar el contenido (eliminar markdown si existe)
        content = content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parsear y validar el JSON
        result = json.loads(content)
        
        # Validar estructura mínima
        if "topics" not in result or "keywords" not in result:
            raise ValueError("Respuesta no contiene topics o keywords")
        
        # Asegurar que tiene el campo language
        if "language" not in result:
            result["language"] = "es"
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        print(f"Respuesta recibida: {content}")
        return {
            "language": "es",
            "topics": ["Error al procesar"],
            "keywords": ["Error al procesar"],
            "error": f"Error al parsear JSON: {str(e)}"
        }
    except Exception as e:
        print(f"Error en la llamada a la API: {e}")
        return {
            "language": "es",
            "topics": ["Error"],
            "keywords": ["Error"],
            "error": f"Error en la llamada a la API: {str(e)}"
        }


# Endpoints de la API
@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "name": "LexiScope API",
        "version": "1.0.0",
        "description": "API para extracción de tópicos y keywords",
        "endpoints": {
            "POST /analyze": "Analizar texto y extraer tópicos y keywords",
            "GET /health": "Verificar estado de la API",
            "GET /docs": "Documentación interactiva de la API"
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Verificar el estado de salud de la API"""
    api_key_loaded = os.getenv("HUGGINGFACE_API_KEY") is not None
    return {
        "status": "healthy",
        "api_key_configured": api_key_loaded
    }


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_endpoint(input_data: TextInput):
    """
    Analiza un texto y extrae tópicos y keywords.
    
    - **text**: El texto a analizar (mínimo 1 carácter)
    - **model**: (Opcional) Modelo de Hugging Face a usar
    
    Retorna un objeto JSON con:
    - **language**: Idioma detectado del texto
    - **topics**: Lista de 3-5 tópicos principales
    - **keywords**: Lista de 5-10 palabras clave
    - **error**: Mensaje de error (si ocurrió alguno)
    """
    
    # Verificar que la API key esté configurada
    if not os.getenv("HUGGINGFACE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="API Key de Hugging Face no configurada. Por favor configura HUGGINGFACE_API_KEY en el archivo .env"
        )
    
    try:
        # Analizar el texto
        result = analyze_text(input_data.text, input_data.model)
        
        # Si hubo un error en el análisis, retornar 500
        if result.get("error") and "Error en la llamada a la API" in result.get("error", ""):
            raise HTTPException(
                status_code=500,
                detail=result.get("error")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
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
