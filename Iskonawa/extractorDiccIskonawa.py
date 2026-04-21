from docx import Document
import re
import json

PARTES_ORACION = {"n.", "v.", "adj.", "adv.", "pron.", "prep.", "conj.", "interj.", "art.", "num.", "suf.", "pref.", "loc.", "expr."}

def leer_docx(ruta):
    doc = Document(ruta)
    texto = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    return texto

def separar_entradas(texto):
    return texto.split("\n")

# Detecta el lexema (puede ser compuesto)
def extraer_lx_ps(texto):
    tokens = texto.split()
    for i, tok in enumerate(tokens):
        if tok in PARTES_ORACION:
            lx = " ".join(tokens[:i])
            ps = tok
            return lx, ps
    return "", ""

# Separa español e inglés
def extraer_dn_de(texto, ps):
    resto = re.split(re.escape(ps), texto, maxsplit=1)[-1].strip()
    tokens = resto.split()
    for i, tok in enumerate(tokens):
        if tok in PARTES_ORACION:
            dn = " ".join(tokens[:i]).strip()
            de = " ".join(tokens[i + 1:]).strip()
            return dn, de
    return resto, ""

# nombre científico
def extraer_sc(texto):
    match = re.search(r'\b([A-Z][a-z]+\s+[a-z]+)\.', texto)
    return match.group(1) if match else ""

def entrada(texto, id_counter):
    lx, ps = extraer_lx_ps(texto)
    dn, de = extraer_dn_de(texto, ps) if ps else ("", "")
    sc = extraer_sc(texto)

    if sc:
        dn = re.sub(re.escape(sc) + r'\.?', '', dn).strip()
        de = re.sub(re.escape(sc) + r'\.?', '', de).strip()

    resultado = {
        "id": id_counter,
        "lx": lx,
        "ps": ps,
        "sn": "1",
        "dn": dn,
        "de": de,
    }

    if sc:
        resultado["sc"] = sc

    return resultado

def procesar(texto):
    entradas = separar_entradas(texto)
    resultado = []

    for i, e in enumerate(entradas, start=1):
        if e.strip():
            parsed = entrada(e, i)
            resultado.append(parsed)

    return resultado

def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    archivo = "Diccionarioiskonawa.docx"
    salida = "salidaDiccIskonawa.json"

    texto = leer_docx(archivo)
    data = procesar(texto)
    guardar_json(data, salida)

    print("Diccionario listo:", salida)

if __name__ == "__main__":
    main()