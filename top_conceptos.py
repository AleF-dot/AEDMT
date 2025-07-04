import re
import os
from pathlib import Path
from collections import Counter

# Configuración de agrupaciones de conceptos
agrupaciones = {
    "elon_musk": ["elon_musk", "elon", "musk"],
    "local": ["local", "locales"],
}

# Stopwords básicas en minúscula
stopwords = {
    "de", "y", "la", "en", "el", "las", "que", "del", "los", "a",
    "un", "una", "por", "con", "se", "no", "es", "para", "como",
    "más", "pero", "su", "al", "le", "lo", "sí", "ya", "o", "este",
    "son", "también", "entre", "ha", "ser", "fue", "sus", "fueron",
    "porque", "desde", "hasta", "cuando", "donde", "todo", "todos",
    "sino", "sin", "cómo", "qué", "quién", "cuál", "cuándo", "dónde",
    "por qué", "puede", "sobre", "esta"
}

# Ruta al texto
base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
ruta_txt = os.path.join(base, "datos", "muestra.txt")
if not os.path.isfile(ruta_txt):
    raise FileNotFoundError(f"No se encontró el archivo: {ruta_txt}")

# Lectura y tokenización
with open(ruta_txt, "r", encoding="utf-8") as f:
    texto = f.read().lower()

# Se unen variantes de conceptos
texto = re.sub(r'\belon\s+musk\b', 'elon_musk', texto)

# Se extraen tokens alfanumericos
palabras = re.findall(r'\b\w+\b', texto)

# Se filtran stopwords
palabras = [w for w in palabras if w not in stopwords]

# Conteo de palabras
contador = Counter(palabras)

# Agrupación final
for concepto, variantes in agrupaciones.items():
    total = 0
    for var in variantes:
        total += contador.get(var, 0)
        contador.pop(var, None)
    contador[concepto] = total

# Se muestra el resultado
print(f"Top 25 conceptos más frecuentes:")
for concepto, cuenta in contador.most_common(25):
    print(f"{concepto.replace('_', ' ').title()}: {cuenta}")
