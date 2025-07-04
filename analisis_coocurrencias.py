import os
import json
from pathlib import Path
from nltk.tokenize import sent_tokenize
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import pandas as pd

nltk.download('punkt')

# Definicion de conceptos a buscar
conceptos = [
    "desarrollo sustentable",
    "desarrollo sostenible",
    "oportunidad",
    "corrupción",
    "justicia social",
    "ética",
    "capitalismo"
]

# Directorio base
directorio_base = os.path.dirname(os.path.abspath(__file__))

# Directorios donde están las citas exactas y enriquecidas
directorio_exactas = os.path.join(directorio_base, "datos", "citas_exactas")
directorio_enriquecidas = os.path.join(directorio_base, "datos", "citas_enriquecidas")

def cargar_texto_por_concepto(directorio):
    """
    Carga los textos de cada concepto desde JSON en el directorio dado.
    Retorna dict {concepto: texto concatenado}
    """
    textos = {}
    for concepto in conceptos:
        nombre_archivo = f"{concepto.replace(' ', '_')}.json"
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                citas_dict = json.load(f)
            textos[concepto] = " ".join(citas_dict.values()).lower()
        else:
            textos[concepto] = ""
    return textos

def analizar_textos(textos_por_concepto):
    texto_completo = " ".join(textos_por_concepto.values())
    oraciones = sent_tokenize(texto_completo)
    frecuencias = {c: texto_completo.count(c.lower()) for c in conceptos}
    coocurrencias = {c1: {c2: 0 for c2 in conceptos} for c1 in conceptos}

    for oracion in oraciones:
        presentes = [c for c in conceptos if c in oracion]
        for i in range(len(presentes)):
            for j in range(i + 1, len(presentes)):
                c1, c2 = presentes[i], presentes[j]
                coocurrencias[c1][c2] += 1
                coocurrencias[c2][c1] += 1

    modelo = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = modelo.encode(conceptos)
    matriz_similitud = cosine_similarity(embeddings)
    return frecuencias, coocurrencias, matriz_similitud

def imprimir_resultados(tipo, frecuencias, coocurrencias, matriz_similitud):
    print(f"\n=== Resultados para {tipo} ===")
    print("\nFrecuencias de conceptos:")
    for c, f in frecuencias.items():
        print(f"{c}: {f}")
    print("\nCo-ocurrencias:")
    for c1, valores in coocurrencias.items():
        print(f"{c1}: {valores}")
    print("\nMatriz de similitud:")
    df_sim = pd.DataFrame(matriz_similitud, index=conceptos, columns=conceptos)
    print(df_sim.round(3))

# Análisis citas exactas
textos_exactas = cargar_texto_por_concepto(directorio_exactas)
freq_exactas, cooc_exactas, sim_exactas = analizar_textos(textos_exactas)
imprimir_resultados("Citas Exactas", freq_exactas, cooc_exactas, sim_exactas)

# Análisis citas enriquecidas
textos_enriquecidas = cargar_texto_por_concepto(directorio_enriquecidas)
freq_enriq, cooc_enriq, sim_enriq = analizar_textos(textos_enriquecidas)
imprimir_resultados("Citas Enriquecidas", freq_enriq, cooc_enriq, sim_enriq)

# Guardar coocurrencias exactas a CSV
df_cooc = pd.DataFrame(cooc_exactas)
ruta_csv = os.path.join(directorio_base, "datos", "coocurrencias_exactas.csv")
df_cooc.to_csv(ruta_csv, encoding='utf-8-sig')

print(f"\n✅ Archivo CSV de coocurrencias exactas guardado en: {ruta_csv}")
