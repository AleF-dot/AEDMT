import os
import fitz
from docx import Document
import re

# Extraer texto de archivos PDF y DOCX, limpiarlo y guardarlo en un archivo de texto
def extraer_texto_pdf(ruta):
    texto = ""
    with fitz.open(ruta) as pdf:
        for pagina in pdf:
            # Usamos get_text("text") para mejor extracción del texto plano
            texto += pagina.get_text("text") + "\n"
    return texto

# Extraer texto de archivos DOCX
def extraer_texto_docx(ruta):
    doc = Document(ruta)
    return "\n".join(parrafo.text for parrafo in doc.paragraphs)

# Formatear el texto extraído para mejorar la legibilidad
def formatear_texto_minimo(texto):
    texto = texto.replace('\r', '')              # Se elimina retorno de carro
    texto = re.sub(r'\n{3,}', '\n\n', texto)     # Se reemplazan saltos de línea múltiples por dos
    texto = re.sub(r'[ \t]+', ' ', texto)        # Se reemplazan espacios y tabulaciones múltiples por uno solo
    texto = texto.strip()                        # Se eliminan espacios al inicio y al final
    return texto

# Rutas relativas
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_entrada = os.path.join(directorio_actual, "muestras")
directorio_salida = os.path.join(directorio_actual, "datos")

os.makedirs(directorio_salida, exist_ok=True)

texto_total = ""

# Procesar todos los archivos en el directorio de entrada
for archivo in os.listdir(directorio_entrada):
    ruta_completa = os.path.join(directorio_entrada, archivo)
    
    if archivo.lower().endswith(".pdf"):
        texto = extraer_texto_pdf(ruta_completa)
    elif archivo.lower().endswith(".docx"):
        texto = extraer_texto_docx(ruta_completa)
    else:
        continue

    texto = formatear_texto_minimo(texto)

    # Separador claro para cada archivo
    texto_total += f"\n--- {archivo} ---\n{texto}\n"

# Se guarda todo en un solo archivo
ruta_salida = os.path.join(directorio_salida, "muestra.txt")
with open(ruta_salida, "w", encoding="utf-8") as f:
    f.write(texto_total)

print(f"✅ Texto combinado (casi completo) guardado en: {ruta_salida}")
