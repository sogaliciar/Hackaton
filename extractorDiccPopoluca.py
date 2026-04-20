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


def separar_entradas_iskonawa(texto):
    patron = r"\b[a-zA-Zñáéíóúɨ']+\s+(n\.|v\.|adj\.|pron\.)"
    matches = list(re.finditer(patron, texto))

    entradas = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(texto)
        entradas.append(texto[start:end].strip())

    return entradas


def entrada_iskonawa(texto, id_counter):
    entrada = {
        "id": id_counter,
        "lx": "",
        "ps": "",
        "sn": "1",
        "dn": "",
        "de": ""
    }

    match = re.match(r"^([a-zA-Zñáéíóúɨ']+)\s+(n\.|v\.|adj\.|pron\.)", texto)
    if not match:
        return entrada

    entrada["lx"] = match.group(1)
    entrada["ps"] = match.group(2)

    resto = texto[match.end():].strip()
    match_ps2 = re.search(r"\b(n\.|v\.|adj\.|pron\.)\s+", resto)

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
        r"\b[a-zA-Zñáéíóúɨ']+\s+(n\.|v\.|adj\.|pron\.)$",
        "",
        entrada["de"]
    ).strip()

    return entrada


def procesar_iskonawa(texto):
    texto = normalizar(texto)
    entradas = separar_entradas_iskonawa(texto)

    resultado = []
    for i, e in enumerate(entradas, start=1):
        if len(e) > 5:
            resultado.append(entrada_iskonawa(e, i))

    return resultado


def separar_entradas_popoluca(texto):
    return texto.split("\n")


def extraer_ejemplos(texto):
    ejemplos = []

    encabezado = re.match(r"^.*?\.\s.*?\.\s", texto)
    if encabezado:
        texto = texto[encabezado.end():]

    patron = r"(.*?)\s*('[^']+')"
    matches = re.findall(patron, texto)

    for xv, xn in matches:
        xv = xv.strip(" ;\n")
        xn = xn.strip()

        if xv and xn:
            ejemplos.append({
                "xv": xv,
                "xn": xn
            })

    return ejemplos


def entrada_popoluca(texto, id_counter):
    entrada = {
        "id": id_counter,
        "lx": "",
        "ps": "",
        "sn": "1",
        "dn": "",
        "ejemplos": []
    }

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
    resultado = []

    for i, e in enumerate(entradas, start=1):
        if e.strip():
            parsed = entrada_popoluca(e, i)
            resultado.append(parsed)

    return resultado


def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    archivo_iskonawa = "Diccionarioiskonawa.docx"
    salida_iskonawa = "salidaDiccIskonawa.json"
    texto = leer_docx(archivo_iskonawa)
    data = procesar_iskonawa(texto)
    guardar_json(data, salida_iskonawa)
    print("Diccionario generado:", salida_iskonawa)

    archivo_popoluca = "DiccionarioPopoluca.docx"
    salida_popoluca = "salidaDiccPopoluca.json"
    texto = leer_docx(archivo_popoluca)
    data = procesar_popoluca(texto)
    guardar_json(data, salida_popoluca)
    print("Diccionario listo:", salida_popoluca)


if __name__ == "__main__":
    main()