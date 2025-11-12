"""
Extractor de Topics y Keywords para textos en español
Requiere: pip install spacy scikit-learn nltk
Además: python -m spacy download es_core_news_sm
"""

import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class ExtractorNLP:
    def __init__(self):
        """Inicializa el modelo de spaCy para español"""
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            print("Descargando modelo de spaCy para español...")
            import os
            os.system("python -m spacy download es_core_news_sm")
            self.nlp = spacy.load("es_core_news_sm")
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza el texto"""
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def extraer_keywords_tfidf(self, texto, top_n=10):
        """Extrae keywords usando TF-IDF"""
        texto_limpio = self.limpiar_texto(texto)
        
        # Tokenizar con spaCy y filtrar stopwords
        doc = self.nlp(texto_limpio)
        tokens = [token.text for token in doc 
                 if not token.is_stop and not token.is_punct and len(token.text) > 2]
        
        if not tokens:
            return []
        
        # TF-IDF con un corpus mínimo
        vectorizer = TfidfVectorizer(max_features=top_n)
        try:
            # Necesitamos al menos 2 documentos, así que duplicamos
            corpus = [' '.join(tokens), ' '.join(tokens[:len(tokens)//2])]
            tfidf_matrix = vectorizer.fit_transform(corpus)
            feature_names = vectorizer.get_feature_names_out()
            
            # Obtener scores del primer documento
            scores = tfidf_matrix[0].toarray()[0]
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [kw for kw, score in keyword_scores[:top_n]]
        except:
            # Fallback: usar frecuencia simple
            return [word for word, _ in Counter(tokens).most_common(top_n)]
    
    def extraer_keywords_entidades(self, texto, top_n=10):
        """Extrae keywords basadas en entidades nombradas y sustantivos"""
        doc = self.nlp(texto)
        
        keywords = []
        
        # Entidades nombradas
        entidades = [ent.text.lower() for ent in doc.ents]
        keywords.extend(entidades)
        
        # Sustantivos y nombres propios
        sustantivos = [token.lemma_.lower() for token in doc 
                      if token.pos_ in ['NOUN', 'PROPN'] 
                      and not token.is_stop 
                      and len(token.text) > 2]
        keywords.extend(sustantivos)
        
        # Contar frecuencias
        contador = Counter(keywords)
        return [palabra for palabra, _ in contador.most_common(top_n)]
    
    def extraer_frases_clave(self, texto, top_n=5):
        """Extrae frases clave (n-gramas) relevantes"""
        doc = self.nlp(texto)
        
        # Extraer chunks nominales
        chunks = [chunk.text.lower() for chunk in doc.noun_chunks 
                 if len(chunk.text.split()) > 1]
        
        # Contar frecuencias
        contador = Counter(chunks)
        return [frase for frase, _ in contador.most_common(top_n)]
    
    def extraer_topics(self, texto):
        """Identifica los topics principales basándose en análisis semántico"""
        doc = self.nlp(texto)
        
        # Analizar las entidades por categoría
        topics_entidades = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in topics_entidades:
                topics_entidades[label] = []
            topics_entidades[label].append(ent.text)
        
        # Extraer verbos principales (acciones/temas)
        verbos = [token.lemma_ for token in doc 
                 if token.pos_ == 'VERB' 
                 and not token.is_stop]
        verbos_frecuentes = Counter(verbos).most_common(5)
        
        # Crear resumen de topics
        topics = []
        
        # Topics basados en entidades
        for label, entidades in topics_entidades.items():
            if entidades:
                topics.append({
                    'tipo': f'Entidad-{label}',
                    'elementos': list(set(entidades))[:3],
                    'frecuencia': len(entidades)
                })
        
        # Topics basados en sustantivos frecuentes
        sustantivos = [token.lemma_.lower() for token in doc 
                      if token.pos_ == 'NOUN' and not token.is_stop]
        sustantivos_top = Counter(sustantivos).most_common(5)
        
        if sustantivos_top:
            topics.append({
                'tipo': 'Conceptos principales',
                'elementos': [s for s, _ in sustantivos_top],
                'frecuencia': sum(c for _, c in sustantivos_top)
            })
        
        return topics
    
    def analizar_texto(self, texto, n_keywords=10, n_frases=5):
        """Análisis completo del texto"""
        print("=" * 60)
        print("ANÁLISIS DE TEXTO EN ESPAÑOL")
        print("=" * 60)
        print(f"\nTexto analizado ({len(texto)} caracteres):")
        print(f"{texto[:200]}..." if len(texto) > 200 else texto)
        
        # Keywords TF-IDF
        print("\n" + "-" * 60)
        print("KEYWORDS (TF-IDF):")
        print("-" * 60)
        keywords_tfidf = self.extraer_keywords_tfidf(texto, n_keywords)
        for i, kw in enumerate(keywords_tfidf, 1):
            print(f"{i}. {kw}")
        
        # Keywords por entidades
        print("\n" + "-" * 60)
        print("KEYWORDS (Entidades y Sustantivos):")
        print("-" * 60)
        keywords_ent = self.extraer_keywords_entidades(texto, n_keywords)
        for i, kw in enumerate(keywords_ent, 1):
            print(f"{i}. {kw}")
        
        # Frases clave
        print("\n" + "-" * 60)
        print("FRASES CLAVE:")
        print("-" * 60)
        frases = self.extraer_frases_clave(texto, n_frases)
        for i, frase in enumerate(frases, 1):
            print(f"{i}. {frase}")
        
        # Topics
        print("\n" + "-" * 60)
        print("TOPICS PRINCIPALES:")
        print("-" * 60)
        topics = self.extraer_topics(texto)
        for i, topic in enumerate(topics, 1):
            print(f"\n{i}. {topic['tipo']} (frecuencia: {topic['frecuencia']})")
            print(f"   Elementos: {', '.join(topic['elementos'])}")
        
        print("\n" + "=" * 60)
        
        return {
            'keywords_tfidf': keywords_tfidf,
            'keywords_entidades': keywords_ent,
            'frases_clave': frases,
            'topics': topics
        }


# Ejemplo de uso
if __name__ == "__main__":
    # Texto de ejemplo
    texto_ejemplo = """
    La inteligencia artificial está revolucionando la medicina moderna. Los algoritmos 
    de aprendizaje automático pueden ahora detectar enfermedades con mayor precisión 
    que los médicos humanos en algunos casos. El Hospital Universitario de Madrid ha 
    implementado un sistema de diagnóstico asistido por IA que analiza radiografías 
    y resonancias magnéticas. Este avance tecnológico promete mejorar significativamente 
    la atención sanitaria en España. Los investigadores del Centro Nacional de 
    Investigaciones Oncológicas están desarrollando nuevos modelos predictivos para 
    el cáncer. La tecnología blockchain también se está integrando para garantizar 
    la seguridad de los datos médicos de los pacientes.
    """
    #texto_ejemplo = "Apoyar la prohibición del reconocimiento facial en espacios públicos es un paso sensato: protege libertades civiles y reduce sesgos algorítmicos. Pero sin una auditoría tecnológica independiente y sanciones reales, la norma será solo papel mojado."
    
    # Crear extractor y analizar
    extractor = ExtractorNLP()
    resultados = extractor.analizar_texto(texto_ejemplo)
    
    print("\n\n💡 CONSEJO: Modifica la variable 'texto_ejemplo' con tu propio texto")