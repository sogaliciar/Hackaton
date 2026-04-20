# Unión de extractor para diccionarios
# Iskonawa
# Popoluca

from docx import Document
import re
import json

def leer_docx(ruta):
    doc = Document(ruta)
    texto = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    return texto

# ISKONAWA

PS_PATRON = r"(n\.|v\.|adj\.|pron\.)"

def normalizar(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def separar_entradas_iskonawa(texto):
    patron = rf"\b[a-zA-Zñáéíóúɨ']+\s+{PS_PATRON}"
    matches = list(re.finditer(patron, texto))
    entradas = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        entradas.append(texto[start:end].strip())
    return entradas

def parsear_entrada_iskonawa(texto, id_counter):
    entrada = {"id": id_counter, "lx": "", "ps": "", "sn": "1", "dn": "", "de": ""}

    match = re.match(rf"^([a-zA-Zñáéíóúɨ']+)\s+{PS_PATRON}", texto)
    if not match:
        return entrada

    entrada["lx"] = match.group(1)
    entrada["ps"] = match.group(2)
    resto = texto[match.end():].strip()

    match_ps2 = re.search(rf"\b{PS_PATRON}\s+", resto)
    if match_ps2:
        esp = resto[:match_ps2.start()].strip()
        eng = resto[match_ps2.end():].strip()
        entrada["dn"] = esp if esp.endswith(".") else esp + "."
        entrada["de"] = eng.strip()
    else:
        partes = re.split(r"\.\s+", resto)
        if len(partes) >= 2:
            entrada["dn"] = partes[0].strip() + "."
            entrada["de"] = partes[1].strip()
        else:
            entrada["dn"] = resto

    entrada["de"] = re.sub(
        rf"\b[a-zA-Zñáéíóúɨ']+\s+{PS_PATRON}$",
        "",
        entrada["de"]
    ).strip()

    return entrada

def procesar_iskonawa(texto):
    texto = normalizar(texto)
    entradas = separar_entradas_iskonawa(texto)
    return [
        parsear_entrada_iskonawa(e, i)
        for i, e in enumerate(entradas, start=1)
        if len(e) > 5
    ]

# POPOLUCA

def separar_entradas_popoluca(texto):
    return texto.split("\n")

def extraer_ejemplos(texto):
    ejemplos = []
    encabezado = re.match(r"^.*?\.\s.*?\.\s", texto)
    if encabezado:
        texto = texto[encabezado.end():]

    patron = r"(.*?)\s*('[^']+')"
    for xv, xn in re.findall(patron, texto):
        xv = xv.strip(" ;\n")
        xn = xn.strip()
        if xv and xn:
            ejemplos.append({"xv": xv, "xn": xn})

    return ejemplos

def parsear_entrada_popoluca(texto, id_counter):
    entrada = {"id": id_counter, "lx": "", "ps": "", "sn": "1", "dn": "", "ejemplos": []}

    match = re.match(r"^(\S+)\s+(\w+\.)", texto)
    if match:
        entrada["lx"] = match.group(1)
        entrada["ps"] = match.group(2)

    match_dn = re.search(r"\w+\.\s*(.*?)\.\s", texto)
    if match_dn:
        entrada["dn"] = match_dn.group(1).strip()

    entrada["ejemplos"] = extraer_ejemplos(texto)
    return entrada

def procesar_popoluca(texto):
    entradas = separar_entradas_popoluca(texto)
    return [
        parsear_entrada_popoluca(e, i)
        for i, e in enumerate(entradas, start=1)
        if e.strip()
    ]

# Guarda archivos de salida
def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

DICCIONARIOS = {
    "iskonawa": {
        "archivo": "Diccionarioiskonawa.docx",
        "salida":  "salidaDiccIskonawa.json",
        "procesar": procesar_iskonawa,
    },
    "popoluca": {
        "archivo": "DiccionarioPopoluca.docx",
        "salida":  "salidaDiccPopoluca.json",
        "procesar": procesar_popoluca,
    },
}

def main():
    for nombre, cfg in DICCIONARIOS.items():
        print(f"Procesando {nombre}...")
        texto = leer_docx(cfg["archivo"])
        data  = cfg["procesar"](texto)
        guardar_json(data, cfg["salida"])
        print(f"  → {cfg['salida']} ({len(data)} entradas)\n")

if __name__ == "__main__":
    main()