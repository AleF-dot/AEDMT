import os
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configuración del modelo
model_name = "finiteautomata/beto-sentiment-analysis"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

id2label = {0: 'NEG', 1: 'NEU', 2: 'POS'}

def analizar_cita(texto):
    enc = tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
    out = model(**enc)
    probs = torch.softmax(out.logits, dim=-1)[0].tolist()
    etiqueta_raw = id2label[int(torch.argmax(out.logits, dim=-1))]
    etiquetas_traducidas = {'NEG': 'negativo', 'NEU': 'neutral', 'POS': 'positivo'}
    etiqueta = etiquetas_traducidas[etiqueta_raw]
    return {
        'probs': {'neg': probs[0], 'neu': probs[1], 'pos': probs[2]},
        'label': etiqueta
    }

# Función para procesar una carpeta
def procesar_carpeta(nombre_conjunto, ruta_carpeta):
    resultados_por_concepto = {}

    for archivo in os.listdir(ruta_carpeta):
        if not archivo.endswith(".json"):
            continue

        concepto = archivo[:-5]
        ruta = os.path.join(ruta_carpeta, archivo)
        with open(ruta, encoding="utf-8") as f:
            citas = json.load(f)

        resultados = {}
        suma = {'neg': 0, 'neu': 0, 'pos': 0}
        conteo = {'negativo': 0, 'neutral': 0, 'positivo': 0}

        for cid, texto in citas.items():
            resultado = analizar_cita(texto.replace('\n', ' '))
            resultados[cid] = resultado

            for k in suma:
                suma[k] += resultado['probs'][k]
            conteo[resultado['label']] += 1

        total = len(resultados)
        media = {k: suma[k] / total for k in suma}

        tops = {}
        for clase in ['neg', 'neu', 'pos']:
            orden = sorted(resultados.items(), key=lambda x: x[1]['probs'][clase], reverse=True)
            tops[clase] = [cid for cid, _ in orden[:5]]

        resultados_por_concepto[concepto] = {
            'media': media,
            'conteo': conteo,
            'top': tops
        }

    # Mostrar resultados por consola
    print(f"\n==============================")
    print(f"  RESULTADOS: {nombre_conjunto}")
    print(f"==============================")
    for concepto, info in resultados_por_concepto.items():
        print(f"\n=== Concepto: {concepto} ===")
        print("Media de scores:", {k: round(v, 3) for k, v in info['media'].items()})
        print("Conteo por etiqueta:", info['conteo'])
        print("Top 5 negativos:", info['top']['neg'])
        print("Top 5 neutrales:", info['top']['neu'])
        print("Top 5 positivos:", info['top']['pos'])

    return resultados_por_concepto

# Función para analizar el texto completo en chunks
def analizar_texto_completo(ruta_archivo, chunk_size=512):
    with open(ruta_archivo, encoding="utf-8") as f:
        texto = f.read().replace('\n', ' ')

    trozos = [texto[i:i+chunk_size] for i in range(0, len(texto), chunk_size)]
    suma = {'neg': 0, 'neu': 0, 'pos': 0}
    total = len(trozos)

    for idx, chunk in enumerate(trozos):
        resultado = analizar_cita(chunk)
        for k in suma:
            suma[k] += resultado['probs'][k]
        print(f"Chunk {idx+1}/{total} analizado.")

    media = {k: suma[k] / total for k in suma}
    return media

# Rutas
BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_EXACTAS = os.path.join(BASE, "datos", "citas", "citas_exactas")
CARPETA_ENRIQUECIDAS = os.path.join(BASE, "datos", "citas", "citas_enriquecidas")
CARPETA_SALIDA = os.path.join(BASE, "datos", "sentimientos")
Path(CARPETA_SALIDA).mkdir(parents=True, exist_ok=True)

# Ejecutar y guardar resultados
resultados_citas_exactas = procesar_carpeta("CITAS EXACTAS", CARPETA_EXACTAS)
resultados_citas_enriquecidas = procesar_carpeta("CITAS ENRIQUECIDAS", CARPETA_ENRIQUECIDAS)

with open(os.path.join(CARPETA_SALIDA, "citas_exactas.json"), "w", encoding="utf-8") as f:
    json.dump(resultados_citas_exactas, f, ensure_ascii=False, indent=2)

with open(os.path.join(CARPETA_SALIDA, "citas_enriquecidas.json"), "w", encoding="utf-8") as f:
    json.dump(resultados_citas_enriquecidas, f, ensure_ascii=False, indent=2)

# Analizar el texto completo muestra.txt
ruta_muestra = os.path.join(BASE, "datos", "muestra.txt")
media_muestra = analizar_texto_completo(ruta_muestra, chunk_size=512)

with open(os.path.join(CARPETA_SALIDA, "media_muestra.json"), "w", encoding="utf-8") as f:
    json.dump(media_muestra, f, ensure_ascii=False, indent=2)

print("\n=== Media de scores para texto completo 'muestra.txt' ===")
print({k: round(v, 3) for k, v in media_muestra.items()})
