import os
import json
from pathlib import Path
from collections import defaultdict
import nltk
import re

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Definicion de directorios base
try:
    directorio_base = os.path.dirname(os.path.abspath(__file__))
except NameError:
    directorio_base = os.getcwd()

# Rutas de archivos
ruta_txt = os.path.join(directorio_base, "datos", "muestra.txt")

directorio_exactas = os.path.join(directorio_base, "datos", "citas", "citas_extra", "exactas")
directorio_enriquecidas = os.path.join(directorio_base, "datos", "citas", "citas_extra", "enriquecidas")
Path(directorio_exactas).mkdir(parents=True, exist_ok=True)
Path(directorio_enriquecidas).mkdir(parents=True, exist_ok=True)

# Agrupaciones de conceptos y sus variantes
agrupaciones = {
    "elon_musk": ["elon musk", "elon", "musk"],
    "local": ["local", "locales"],
}

otros_conceptos = [
    "espacio",
    "global",
    "litio",
    "argentina",
    "empresas",
    "modelo",
    "ortiz",
    "nacional",
    "tesla",
    "desarrollo",
    "starlink",
    "transnacionales",
    "modelos",
    "recursos",
    "energy",
    "extractivista",
    "globalización",
    "industrial",
    "territorio",
    "territorialidad",
    "comunidades",
    "público",
    "privado"
]


# Combinar todos los conceptos
todos_conceptos = {}
todos_conceptos.update(agrupaciones)
for c in otros_conceptos:
    todos_conceptos[c] = [c]

# Lectura del texto y unificacion de variantes
if not os.path.isfile(ruta_txt):
    raise FileNotFoundError(f"No se encontró el archivo: {ruta_txt}")

with open(ruta_txt, "r", encoding="utf-8") as f:
    texto = f.read().lower()

# Reemplazo de variantes por conceptos
for concepto, variantes in todos_conceptos.items():
    for variante in sorted(variantes, key=lambda x: -len(x)):  # primero los más largos
        texto = re.sub(rf'\b{re.escape(variante)}\b', concepto, texto)

# Tokenización de oraciones
oraciones = sent_tokenize(texto)

# Función para guardar JSON
def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Creación de un diccionario para almacenar las citas exactas
fragmentos_exactas = defaultdict(dict)
for concepto in todos_conceptos.keys():
    contador = 1
    for oracion in oraciones:
        if concepto in oracion:
            fragmentos_exactas[concepto][contador] = oracion.strip()
            contador += 1

# Guardar las citas exactas en archivos JSON
for concepto, citas_dict in fragmentos_exactas.items():
    nombre_archivo = f"{concepto}.json"
    ruta_salida = os.path.join(directorio_exactas, nombre_archivo)
    guardar_json(citas_dict, ruta_salida)

print(f"✅ Citas exactas guardadas en: '{directorio_exactas}'")

# Citas enriquecidas: fragmentos de oraciones alrededor de cada concepto
fragmentos_enriquecidas = defaultdict(dict)
rango = 1
for concepto in todos_conceptos.keys():
    contador = 1
    for i, oracion in enumerate(oraciones):
        if concepto in oracion:
            inicio = max(0, i - rango)
            fin = min(len(oraciones), i + rango + 1)
            fragmento = " ".join(oraciones[inicio:fin]).strip()
            fragmentos_enriquecidas[concepto][contador] = fragmento
            contador += 1

# Guardar las citas enriquecidas en archivos JSON
for concepto, citas_dict in fragmentos_enriquecidas.items():
    nombre_archivo = f"{concepto}.json"
    ruta_salida = os.path.join(directorio_enriquecidas, nombre_archivo)
    guardar_json(citas_dict, ruta_salida)

print(f"✅ Citas enriquecidas guardadas en: '{directorio_enriquecidas}'")
