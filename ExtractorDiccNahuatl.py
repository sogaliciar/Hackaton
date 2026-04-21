import os
import re
import json
from docx import Document

def leer_docx(ruta):
    doc = Document(ruta)
    texto = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    return texto

def agrupar_entradas(texto):
    lineas = texto.split('\n')
    entradas = []
    entrada_actual = ""
    patron_inicio = re.compile(r'^([A-ZÁÉÍÓÚÑCHTZKWX,\s]+)\s+(s\.|v\.[1-5]|v\. irr\.|v\. intr\.|adv\.|adj\.|expr\.|ap\.|cont\.|part\.|hon\.|pron\.|véa\.)')

    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith('('): 
            continue
        if patron_inicio.match(linea):
            if entrada_actual:
                entradas.append(entrada_actual.strip())
            entrada_actual = linea
        else:
            entrada_actual += " " + linea

    if entrada_actual:
        entradas.append(entrada_actual.strip())

    return entradas

def extraer_ejemplos(texto_ejemplos):
    ejemplos = []
    fragmentos = texto_ejemplos.split(';')
    for frag in fragmentos:
        if '–' in frag or '-' in frag:
            partes = re.split(r'[–-]', frag, 1)
            if len(partes) == 2:
                ejemplos.append({"xv": partes[0].strip(), "xn": partes[1].strip()})
    return ejemplos

def procesar_entrada(texto, id_counter):
    entrada = {"id": id_counter, "lx": "", "ps": "", "sn": "1", "dn": "", "xv_xn": [], "nt": "", "cf": ""}
    match_cabecera = re.match(r'^([A-ZÁÉÍÓÚÑCHTZKWX,\s]+)\s+([a-z0-9.,\s]+?)\s*[–-]\s*(.*)', texto)

    if match_cabecera:
        entrada["lx"] = match_cabecera.group(1).strip()
        entrada["ps"] = match_cabecera.group(2).strip()
        resto = match_cabecera.group(3).strip()
    else:
        match_ref = re.match(r'^([A-ZÁÉÍÓÚÑCHTZKWX,\s]+)\s+(véa\..*)', texto)
        if match_ref:
            entrada["lx"] = match_ref.group(1).strip()
            entrada["cf"] = match_ref.group(2).strip().replace("véa. ", "")
            return entrada
        return None

    match_def = re.match(r'^(.*?)(?:(?:Ej\.|R\.|Sin\.|Dícese|véa\.)|$)', resto)
    if match_def:
        entrada["dn"] = match_def.group(1).strip()

    if 'Ej.' in resto:
        bloque = resto.split('Ej.')[1].split('R.')[0].split('Sin.')[0].split('véa.')[0].strip()
        entrada["xv_xn"] = extraer_ejemplos(bloque)

    return entrada

def main():
    archivo = "DiccionarioNahuatl.docx"
    salida = "salidaDiccNahuatl.json"

    if not os.path.exists(archivo):
        print(f"Error: No encontré '{archivo}' en esta carpeta.")
        return

    print("Procesando diccionario...")
    try:
        texto = leer_docx(archivo)
        entradas = agrupar_entradas(texto)
        resultado = []
        for i, e in enumerate(entradas, start=1):
            p = procesar_entrada(e, i)
            if p:
                resultado.append(p)

        with open(salida, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
        print(f"¡Hecho!")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()