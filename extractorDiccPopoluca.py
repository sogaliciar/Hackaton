from docx import Document
import re
import json

# lee el documento
def leer_docx(ruta):
    doc = Document(ruta)
    texto = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    return texto

def separar_entradas(texto):
    return texto.split("\n")


# Separa los ejemplos
def extraer_ejemplos(texto):
    ejemplos = []

    encabezado = re.match(r"^.*?\.\s.*?\.\s", texto)
    if encabezado:
        texto = texto[encabezado.end():]

    patron = r"(.*?)\s*(‘[^’]+’)"
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

def entrada(texto, id_counter):
    entrada = {
        "id": id_counter,
        "lx": "",
        "ps": "",
        "sn": "1",
        "dn": "",
        "ejemplos": []
    }

    # lx y ps

    match = re.match(r"^(\S+)\s+(\w+\.)", texto)
    if match:
        entrada["lx"] = match.group(1)
        entrada["ps"] = match.group(2)

    # definición (dn)

    match_dn = re.search(r"\w+\.\s*(.*?)\.\s", texto)
    if match_dn:
        entrada["dn"] = match_dn.group(1).strip()

    # ejemplos 

    entrada["ejemplos"] = extraer_ejemplos(texto)

    return entrada

def procesar(texto):
    entradas = separar_entradas(texto)
    resultado = []

    for i, e in enumerate(entradas, start=1):
        if e.strip():
            parsed = entrada(e, i)
            resultado.append(parsed)

    return resultado

# Guarda el archivo de salida
def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    archivo = "DiccionarioPopoluca.docx"
    salida = "salidaDiccPopoluca.json"

    texto = leer_docx(archivo)
    data = procesar(texto)
    guardar_json(data, salida)

    print("Diccionario listo:", salida)

if __name__ == "__main__":
    main()