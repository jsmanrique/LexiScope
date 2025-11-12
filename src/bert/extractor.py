# SPDX-FileCopyrightText: © 2025 J. Manrique Lopez de la Fuente <jsmanrique@gmail.com>
# SPDX-License-Identifier: MIT

"""extractor.py: Extractor de Topics y Keywords usando BERT y modelos Transformer"""

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
import warnings
warnings.filterwarnings('ignore')

class ExtractorBERT:
    def __init__(self, modelo='paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Inicializa modelos BERT para español
        
        Modelos recomendados:
        - 'paraphrase-multilingual-MiniLM-L12-v2': Rápido, multilingüe
        - 'hiiamsid/sentence_similarity_spanish_es': Específico español
        - 'dccuchile/bert-base-spanish-wwm-uncased': BETO (BERT español)
        """
        print(f"Cargando modelo: {modelo}...")
        
        # KeyBERT para extracción de keywords
        self.kw_model = KeyBERT(model=modelo)
        
        # Sentence Transformer para embeddings
        self.sentence_model = SentenceTransformer(modelo)
        
        print("✓ Modelos cargados correctamente\n")
    
    def extraer_keywords_bert(self, texto, top_n=10, ngram_range=(1, 2), 
                              diversidad=0.5):
        """
        Extrae keywords usando KeyBERT con embeddings contextuales
        
        Args:
            texto: Texto a analizar
            top_n: Número de keywords a extraer
            ngram_range: Rango de n-gramas (1,1)=palabras, (1,2)=palabras+bigramas
            diversidad: 0-1, mayor valor = keywords más diversas (usa MMR)
        """
        keywords = self.kw_model.extract_keywords(
            texto,
            keyphrase_ngram_range=ngram_range,
            stop_words=None,
            top_n=top_n,
            use_mmr=True,  # Maximal Marginal Relevance para diversidad
            diversity=diversidad
        )
        return keywords
    
    def extraer_temas_clustering(self, texto, n_clusters=3, min_oraciones=5):
        """
        Agrupa oraciones en temas usando clustering de embeddings
        """
        # Dividir en oraciones
        oraciones = [s.strip() for s in texto.split('.') if len(s.strip()) > 20]
        
        if len(oraciones) < min_oraciones:
            return [{
                'tema': 'Tema único',
                'oraciones_representativas': oraciones[:3],
                'keywords': []
            }]
        
        # Generar embeddings
        embeddings = self.sentence_model.encode(oraciones)
        
        # Clustering
        n_clusters = min(n_clusters, len(oraciones))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(embeddings)
        
        # Analizar cada cluster
        temas = []
        for i in range(n_clusters):
            indices = np.where(clusters == i)[0]
            oraciones_cluster = [oraciones[idx] for idx in indices]
            
            # Encontrar oración más representativa (cercana al centroide)
            embeddings_cluster = embeddings[indices]
            centroid = kmeans.cluster_centers_[i]
            distancias = cosine_similarity([centroid], embeddings_cluster)[0]
            idx_representativo = indices[np.argmax(distancias)]
            
            # Extraer keywords del cluster
            texto_cluster = '. '.join(oraciones_cluster)
            keywords_cluster = self.kw_model.extract_keywords(
                texto_cluster,
                keyphrase_ngram_range=(1, 2),
                stop_words=None,
                top_n=5,
                use_mmr=True,
                diversity=0.7
            )
            
            temas.append({
                'tema': f'Tema {i+1}',
                'num_oraciones': len(oraciones_cluster),
                'oracion_representativa': oraciones[idx_representativo],
                'keywords': [kw for kw, _ in keywords_cluster],
                'todas_oraciones': oraciones_cluster[:3]  # Mostrar solo 3
            })
        
        return temas
    
    def encontrar_oraciones_clave(self, texto, top_n=3):
        """
        Identifica las oraciones más importantes del texto
        usando similitud con el embedding del texto completo
        """
        oraciones = [s.strip() for s in texto.split('.') if len(s.strip()) > 20]
        
        if not oraciones:
            return []
        
        # Embeddings
        embedding_texto = self.sentence_model.encode([texto])
        embeddings_oraciones = self.sentence_model.encode(oraciones)
        
        # Calcular similitud
        similitudes = cosine_similarity(embedding_texto, embeddings_oraciones)[0]
        
        # Ordenar por similitud
        indices_top = np.argsort(similitudes)[-top_n:][::-1]
        
        return [(oraciones[i], similitudes[i]) for i in indices_top]
    
    def analizar_texto_completo(self, texto, n_keywords=10, n_temas=3, 
                               n_oraciones_clave=3):
        """
        Análisis completo usando BERT
        """
        print("=" * 70)
        print("ANÁLISIS CON MODELOS TRANSFORMER (BERT)")
        print("=" * 70)
        print(f"\nTexto analizado ({len(texto)} caracteres, "
              f"{len(texto.split())} palabras):")
        print(f"{texto[:200]}..." if len(texto) > 200 else texto)
        
        # 1. Keywords individuales
        print("\n" + "-" * 70)
        print("🔑 KEYWORDS (palabras individuales)")
        print("-" * 70)
        keywords_simples = self.extraer_keywords_bert(
            texto, 
            top_n=n_keywords, 
            ngram_range=(1, 1),
            diversidad=0.3
        )
        for i, (keyword, score) in enumerate(keywords_simples, 1):
            print(f"{i:2d}. {keyword:30s} (relevancia: {score:.3f})")
        
        # 2. Frases clave (bigramas)
        print("\n" + "-" * 70)
        print("📝 FRASES CLAVE (bigramas y términos compuestos)")
        print("-" * 70)
        frases_clave = self.extraer_keywords_bert(
            texto,
            top_n=8,
            ngram_range=(2, 2),
            diversidad=0.7
        )
        for i, (frase, score) in enumerate(frases_clave, 1):
            print(f"{i}. {frase:40s} (relevancia: {score:.3f})")
        
        # 3. Oraciones más importantes
        print("\n" + "-" * 70)
        print("⭐ ORACIONES MÁS RELEVANTES")
        print("-" * 70)
        oraciones_clave = self.encontrar_oraciones_clave(texto, n_oraciones_clave)
        for i, (oracion, similitud) in enumerate(oraciones_clave, 1):
            print(f"\n{i}. (similitud: {similitud:.3f})")
            print(f"   {oracion}")
        
        # 4. Temas identificados por clustering
        print("\n" + "-" * 70)
        print("🎯 TOPICS PRINCIPALES (clustering semántico)")
        print("-" * 70)
        temas = self.extraer_temas_clustering(texto, n_clusters=n_temas)
        for i, tema in enumerate(temas, 1):
            print(f"\n{tema['tema']} ({tema['num_oraciones']} oraciones)")
            print(f"  └─ Representativa: {tema['oracion_representativa']}")
            print(f"  └─ Keywords: {', '.join(tema['keywords'])}")
        
        print("\n" + "=" * 70)
        
        return {
            'keywords': keywords_simples,
            'frases_clave': frases_clave,
            'oraciones_clave': oraciones_clave,
            'topics': temas
        }


class ExtractorBERTAvanzado(ExtractorBERT):
    """Versión con capacidades adicionales usando otros modelos"""
    
    def __init__(self):
        super().__init__(modelo='paraphrase-multilingual-MiniLM-L12-v2')
        print("Cargando pipeline de zero-shot classification...")
        self.clasificador = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        print("✓ Pipeline cargado\n")
    
    def clasificar_en_categorias(self, texto, categorias):
        """
        Clasifica el texto en categorías predefinidas
        usando zero-shot classification
        """
        resultado = self.clasificador(
            texto,
            candidate_labels=categorias,
            multi_label=True
        )
        return list(zip(resultado['labels'], resultado['scores']))


# Ejemplo de uso
if __name__ == "__main__":
    # Texto de ejemplo más largo
    texto_ejemplo = """
    El cambio climático representa uno de los mayores desafíos de nuestro tiempo.
    Las temperaturas globales han aumentado aproximadamente 1.1°C desde la era preindustrial.
    Los científicos del Panel Intergubernamental sobre Cambio Climático (IPCC) advierten
    que debemos limitar el calentamiento a 1.5°C para evitar consecuencias catastróficas.
    
    Las energías renovables están experimentando un crecimiento sin precedentes. La energía
    solar y eólica son ahora las formas más baratas de generar electricidad en muchos países.
    España ha instalado más de 5 GW de capacidad solar fotovoltaica en los últimos años.
    
    La transición hacia una economía baja en carbono requiere inversiones masivas en
    infraestructura verde. Los vehículos eléctricos están reemplazando gradualmente a
    los de combustión interna. Las ciudades están implementando zonas de bajas emisiones
    para mejorar la calidad del aire urbano.
    """
    
    print("\n🚀 OPCIÓN 1: Análisis estándar con KeyBERT")
    print("=" * 70)
    extractor = ExtractorBERT()
    resultados = extractor.analizar_texto_completo(
        texto_ejemplo,
        n_keywords=12,
        n_temas=3,
        n_oraciones_clave=3
    )
    
    # OPCIÓN 2: Usar ExtractorBERTAvanzado con clasificación
    print("\n\n🚀 OPCIÓN 2: Análisis avanzado con clasificación por categorías")
    print("=" * 70)
    
    extractor_avanzado = ExtractorBERTAvanzado()
    
    # Análisis completo (hereda todos los métodos de ExtractorBERT)
    resultados_avanzado = extractor_avanzado.analizar_texto_completo(
        texto_ejemplo,
        n_keywords=8,
        n_temas=3,
        n_oraciones_clave=3
    )
    
    # Clasificación adicional por categorías
    print("\n" + "-" * 70)
    print("🏷️  CLASIFICACIÓN POR CATEGORÍAS (Zero-Shot)")
    print("-" * 70)
    categorias = [
        "medio ambiente",
        "tecnología",
        "economía",
        "política",
        "energía renovable",
        "cambio climático"
    ]
    
    clasificacion = extractor_avanzado.clasificar_en_categorias(
        texto_ejemplo, 
        categorias
    )
    
    print("\nCategorías detectadas (ordenadas por relevancia):")
    for i, (categoria, score) in enumerate(clasificacion, 1):
        barra = "█" * int(score * 50)
        print(f"{i}. {categoria:25s} {score:.3f} {barra}")
    
    print("\n" + "=" * 70)
    
    print("\n\n" + "=" * 70)
    print("📊 COMPARACIÓN DE MODELOS RECOMENDADOS PARA ESPAÑOL:")
    print("=" * 70)
    print("""
    1. paraphrase-multilingual-MiniLM-L12-v2
       ✓ Rápido y eficiente
       ✓ Multilingüe de alta calidad
       ✓ Bueno para keywords y similitud
       
    2. hiiamsid/sentence_similarity_spanish_es
       ✓ Entrenado específicamente en español
       ✓ Excelente para similitud semántica
       ✓ Menor que el anterior
       
    3. dccuchile/bert-base-spanish-wwm-uncased (BETO)
       ✓ BERT completo entrenado en español
       ✓ Mejor comprensión contextual
       ✓ Más pesado pero más preciso
    """)
    
    print("\n💡 USO BÁSICO:")
    print("-" * 70)
    print("""
    # Opción 1: Análisis estándar
    extractor = ExtractorBERT()
    resultados = extractor.analizar_texto_completo(texto)
    
    # Opción 2: Con clasificación por categorías
    extractor_avanzado = ExtractorBERTAvanzado()
    resultados = extractor_avanzado.analizar_texto_completo(texto)
    categorias = ['medio ambiente', 'tecnología', 'economía']
    clasificacion = extractor_avanzado.clasificar_en_categorias(texto, categorias)
    
    # Cambiar modelo
    extractor = ExtractorBERT(modelo='dccuchile/bert-base-spanish-wwm-uncased')
    """)
