from docx import Document
import re
import json

def leer_docx(ruta):
    doc = Document(ruta)
    texto = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    return texto

def normalizar(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def separar_entradas(texto):
    patron = r"\b[a-zA-Zñáéíóúɨ’]+\s+(n\.|v\.|adj\.|pron\.)"
    matches = list(re.finditer(patron, texto))

    entradas = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(texto)
        entradas.append(texto[start:end].strip())

    return entradas

def entrada(texto, id_counter):
    entrada = {
        "id": id_counter,
        "lx": "",
        "ps": "",
        "sn": "1",
        "dn": "",
        "de": ""
    }

    match = re.match(r"^([a-zA-Zñáéíóúɨ’]+)\s+(n\.|v\.|adj\.|pron\.)", texto)
    if not match:
        return entrada

    entrada["lx"] = match.group(1)
    entrada["ps"] = match.group(2)

    resto = texto[match.end():].strip()
    #busca el segundo ps
    match_ps2 = re.search(r"\b(n\.|v\.|adj\.|pron\.)\s+", resto)

    if match_ps2:
        # español = antes del segundo ps
        esp = resto[:match_ps2.start()].strip()

        # ingles = después del segundo ps
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

    # ---------------------
    # 3. limpiar siguiente entrada en inglés
    # ---------------------
    entrada["de"] = re.sub(
        r"\b[a-zA-Zñáéíóúɨ’]+\s+(n\.|v\.|adj\.|pron\.)$",
        "",
        entrada["de"]
    ).strip()

    return entrada

def procesar(texto):
    texto = normalizar(texto)
    entradas = separar_entradas(texto)

    resultado = []
    for i, e in enumerate(entradas, start=1):
        if len(e) > 5:
            resultado.append(entrada(e, i))

    return resultado


# Guarda el archivo de salida
def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    archivo = "Diccionarioiskonawa.docx"
    salida = "salidaDiccIskonawa.json"

    texto = leer_docx(archivo)
    data = procesar(texto)
    guardar_json(data, salida)

    print("✅ JSON generado correctamente:", salida)


if __name__ == "__main__":
    main()