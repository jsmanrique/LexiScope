import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API Key loaded:", client.api_key is not None)

def topics_and_keywords_openai(texto: str, modelo: str = "gpt-5-nano"):
    """
    Extrae tópicos (3–5) y keywords (5–10) en español con salida JSON validada por esquema.
    """
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

    # Create completion API call within function
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
    return response.choices[0].message.content

# ---------- Ejemplo de uso ----------
if __name__ == "__main__":
    # texto = "La digitalización industrial en España acelera con gemelos digitales y mantenimiento predictivo basado en IA."
    texto = "Apoyar la prohibición del reconocimiento facial en espacios públicos es un paso sensato: protege libertades civiles y reduce sesgos algorítmicos. Pero sin una auditoría tecnológica independiente y sanciones reales, la norma será solo papel mojado."
    print(topics_and_keywords_openai(texto))
