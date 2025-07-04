import os
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from pathlib import Path
import json

nltk.download('vader_lexicon')

# Directorio base
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Rutas de archivos
RUTA_TEXTO_CRUDO = os.path.join(directorio_base, "datos", "muestra.txt")
CARPETA_CITAS_EXACTAS = os.path.join(directorio_base, "datos", "citas_exactas")
CARPETA_CITAS_ENRIQUECIDAS = os.path.join(directorio_base, "datos", "citas_enriquecidas")
Path(CARPETA_CITAS_EXACTAS).mkdir(parents=True, exist_ok=True)
Path(CARPETA_CITAS_ENRIQUECIDAS).mkdir(parents=True, exist_ok=True)

sia = SentimentIntensityAnalyzer()

# Función para analizar el sentimiento de un texto en chunks
def analizar_texto_en_chunks(texto, chunk_size=25000):
    chunks = [texto[i:i+chunk_size] for i in range(0, len(texto), chunk_size)]
    puntajes = {'neg': 0, 'neu': 0, 'pos': 0}
    for idx, chunk in enumerate(chunks):
        score = sia.polarity_scores(chunk)
        for k in puntajes:
            puntajes[k] += score[k]
        print(f"Chunk {idx+1}/{len(chunks)} procesado.")
    num_chunks = len(chunks)
    return {k: puntajes[k]/num_chunks for k in puntajes}

# Función para analizar citas en una carpeta
def analizar_citas_en_carpeta(ruta_carpeta):
    """Analiza sentimiento de cada archivo de citas en una carpeta y devuelve resultados por concepto."""
    resultados = {}
    for archivo in os.listdir(ruta_carpeta):
        if not archivo.endswith(".json"):
            continue
        concepto = archivo[:-5]  # quitar ".json"
        ruta_archivo = os.path.join(ruta_carpeta, archivo)
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            citas_dict = json.load(f)
        
        puntajes_citas = []
        for cita in citas_dict.values():
            cita = cita.strip().replace('\n', ' ')
            puntaje = sia.polarity_scores(cita)
            puntajes_citas.append(puntaje)
        if puntajes_citas:
            avg_neg = sum(p['neg'] for p in puntajes_citas) / len(puntajes_citas)
            avg_neu = sum(p['neu'] for p in puntajes_citas) / len(puntajes_citas)
            avg_pos = sum(p['pos'] for p in puntajes_citas) / len(puntajes_citas)
        else:
            avg_neg = avg_neu = avg_pos = 0
        resultados[concepto] = {
            "num_citas": len(puntajes_citas),
            "avg_neg": avg_neg,
            "avg_neu": avg_neu,
            "avg_pos": avg_pos,
        }
    return resultados


# Analizar texto completo crudo (en chunks)
with open(RUTA_TEXTO_CRUDO, "r", encoding="utf-8") as f:
    texto_completo = f.read().replace('\n', ' ')

# Asegurarse de que el texto completo no exceda el tamaño máximo
sentimiento_texto_completo = analizar_texto_en_chunks(texto_completo, chunk_size=25000)

# Analizar citas exactas
resultados_citas_exactas = analizar_citas_en_carpeta(CARPETA_CITAS_EXACTAS)

# Analizar citas enriquecidas
resultados_citas_enriquecidas = analizar_citas_en_carpeta(CARPETA_CITAS_ENRIQUECIDAS)

# Mostrar resumen (redondeado a 3 decimales)
print("=== Análisis Sentimiento Texto Completo ===")
print({k: round(v, 3) for k, v in sentimiento_texto_completo.items()})
print("\n=== Análisis Sentimiento Citas Exactas ===")

# Mostrar resultados de citas exactas
for concepto, datos in resultados_citas_exactas.items():
    datos_redondeados = {k: round(v, 3) if isinstance(v, float) else v for k, v in datos.items()}
    print(f"{concepto}: {datos_redondeados}")

# Mostrar resultados de citas enriquecidas
print("\n=== Análisis Sentimiento Citas Enriquecidas ===")
for concepto, datos in resultados_citas_enriquecidas.items():
    datos_redondeados = {k: round(v, 3) if isinstance(v, float) else v for k, v in datos.items()}
    print(f"{concepto}: {datos_redondeados}")

# Función para comparar sentimientos entre texto completo, citas exactas y citas enriquecidas
def comparar_sentimientos(texto_completo, citas_exactas, citas_enriquecidas):
    print("=== Comparación Sentimientos por Concepto ===")
    for concepto in citas_exactas:
        if concepto in citas_enriquecidas:
            exactas = citas_exactas[concepto]
            enriquecidas = citas_enriquecidas[concepto]
            
            print(f"\nConcepto: {concepto}")
            for k in ['avg_neg', 'avg_neu', 'avg_pos']:
                val_exactas = exactas[k]
                val_enriquecidas = enriquecidas[k]
                val_texto = texto_completo[k.replace('avg_', '')]
                
                diff_citas = val_enriquecidas - val_exactas
                diff_texto_exactas = val_exactas - val_texto
                diff_texto_enriq = val_enriquecidas - val_texto
                
                print(f" {k}:")
                print(f"  - Citas Exactas: {val_exactas:.3f}")
                print(f"  - Citas Enriquecidas: {val_enriquecidas:.3f}")
                print(f"  - Diferencia Enriquecidas - Exactas: {diff_citas:+.3f}")
                print(f"  - Diferencia Exactas - Texto Completo: {diff_texto_exactas:+.3f}")
                print(f"  - Diferencia Enriquecidas - Texto Completo: {diff_texto_enriq:+.3f}")
        else:
            print(f"\nConcepto {concepto} no encontrado en citas enriquecidas.")

# Comparar sentimientos entre texto completo, citas exactas y enriquecidas
comparar_sentimientos(sentimiento_texto_completo, resultados_citas_exactas, resultados_citas_enriquecidas)
