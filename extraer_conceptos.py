import os
import json
from pathlib import Path
from collections import defaultdict
import nltk

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Definición del directorio base
try:
    directorio_base = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Para entornos sin __file__, usar el directorio actual
    directorio_base = os.getcwd()

# Rutas de archivos
ruta_txt = os.path.join(directorio_base, "datos", "muestra.txt")

# Directorios donde se guardarán las citas exactas y enriquecidas
directorio_exactas = os.path.join(directorio_base, "datos", "citas", "citas_exactas")
directorio_enriquecidas = os.path.join(directorio_base, "datos", "citas", "citas_enriquecidas")

# Crear directorios si no existen
Path(directorio_exactas).mkdir(parents=True, exist_ok=True)
Path(directorio_enriquecidas).mkdir(parents=True, exist_ok=True)

# Conceptos a buscar dados por la cátedra
conceptos = [
    "desarrollo sustentable",
    "desarrollo sostenible",
    "oportunidad",
    "corrupción",
    "justicia social",
    "ética",
    "capitalismo"
]

# Lectura del texto
if not os.path.isfile(ruta_txt):
    raise FileNotFoundError(f"No se encontró el archivo: {ruta_txt}")

with open(ruta_txt, "r", encoding="utf-8") as f:
    texto = f.read().lower()

oraciones = sent_tokenize(texto)

# Función para guardar datos en formato JSON
def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Crear un diccionario para almacenar las citas exactas y enriquecidas
fragmentos_exactas = defaultdict(dict)

# Buscar citas exactas
for concepto in conceptos:
    contador = 1
    concepto_lower = concepto.lower()
    for oracion in oraciones:
        if concepto_lower in oracion.lower():
            fragmentos_exactas[concepto][contador] = oracion.strip()
            contador += 1

# Guardar las citas exactas en archivos JSON
for concepto, citas_dict in fragmentos_exactas.items():
    nombre_archivo = f"{concepto.replace(' ', '_')}.json"
    ruta_salida = os.path.join(directorio_exactas, nombre_archivo)
    guardar_json(citas_dict, ruta_salida)

print(f"✅ Citas exactas guardadas en JSON en: '{directorio_exactas}'")

# Crear un diccionario para almacenar las citas enriquecidas
fragmentos_enriquecidas = defaultdict(dict)
rango = 1  # oraciones antes y después

# Buscar citas enriquecidas: fragmentos de oraciones alrededor de cada concepto
for concepto in conceptos:
    contador = 1
    concepto_lower = concepto.lower()
    for i, oracion in enumerate(oraciones):
        if concepto_lower in oracion.lower():
            inicio = max(0, i - rango)
            fin = min(len(oraciones), i + rango + 1)
            fragmento = " ".join(oraciones[inicio:fin]).strip()
            fragmentos_enriquecidas[concepto][contador] = fragmento
            contador += 1

# Guardar las citas enriquecidas en archivos JSON
for concepto, citas_dict in fragmentos_enriquecidas.items():
    nombre_archivo = f"{concepto.replace(' ', '_')}.json"
    ruta_salida = os.path.join(directorio_enriquecidas, nombre_archivo)
    guardar_json(citas_dict, ruta_salida)

print(f"✅ Citas enriquecidas guardadas en JSON en: '{directorio_enriquecidas}'")
