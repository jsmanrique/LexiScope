# SPDX-FileCopyrightText: © 2025 J. Manrique Lopez de la Fuente <jsmanrique@gmail.com>
# SPDX-License-Identifier: MIT

"""huggingface.py: Script para extracción de tópicos y keywords de un texto usando Hugging Face API."""

import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Hugging Face Inference Client
client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
print("API Key loaded:", os.getenv("HUGGINGFACE_API_KEY") is not None)

model: str = "google/gemma-2-9b-it"
model: str = "moonshotai/Kimi-K2-Instruct-0905"

def topics_and_keywords(texto: str, modelo: str = model):
    """
    Extrae tópicos (3–5) y keywords (5–10).
    Devuelve un JSON con la estructura esperada.
    """
    
    # Prompt detallado para guiar a Gemma
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
        
        # Intentar parsear el JSON de la respuesta
        # A veces el modelo puede incluir markdown, así que limpiamos
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
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        print(f"Respuesta recibida: {content}")
        # Retornar estructura por defecto en caso de error
        return json.dumps({
            "language": "es",
            "topics": ["Error al procesar"],
            "keywords": ["Error al procesar"],
            "error": str(e)
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error en la llamada a la API: {e}")
        return json.dumps({
            "language": "es",
            "topics": ["Error"],
            "keywords": ["Error"],
            "error": str(e)
        }, ensure_ascii=False, indent=2)


# ---------- Ejemplo de uso ----------
if __name__ == "__main__":
    # Ejemplo 1: Texto sobre digitalización industrial
    texto = "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
    
    # Ejemplo 2: Texto sobre reconocimiento facial
    # texto = "Apoyar la prohibición del reconocimiento facial en espacios públicos es un paso sensato: protege libertades civiles y reduce sesgos algorítmicos. Pero sin una auditoría tecnológica independiente y sanciones reales, la norma será solo papel mojado."
    
    print("\n=== Extracción de tópicos y keywords ===")
    resultado = topics_and_keywords(texto)
    print(resultado)
