import os
import re
import json
import fitz  # PyMuPDF
from docx import Document

class ExtractorMDF:
    def __init__(self):
        pass

    def leer_archivo(self, ruta):
        ext = os.path.splitext(ruta)[1].lower()
        if ext == '.docx':
            doc = Document(ruta)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == '.pdf':
            texto = ""
            with fitz.open(ruta) as doc:
                for pagina in doc:
                    texto += pagina.get_text()
            return texto
        return open(ruta, 'r', encoding='utf-8').read()

    def segmentar_mdf(self, texto_crudo):
        entradas = []
        # Regex adaptada para capturar Palabra + Categoría + Definición
        regex_patron = r"(\w+)\s+(adj\.|adv\.|s\.|vt\.|vi\.|va\.)\s+(.*?)(?=\n\w+\s+(?:s\.|v\.|adj)|$)"
        coincidencias = re.finditer(regex_patron, texto_crudo, re.DOTALL)
        
        for i, m in enumerate(coincidencias, 1):
            entrada = {
                "id": str(i),
                "lx": m.group(1),
                "ps": m.group(2).strip(),
                "sn": "1",
                "dn": m.group(3).split('\n')[0].strip(),
                "xv": m.group(3).split('\n')[1].strip() if '\n' in m.group(3) else ""
            }
            entradas.append(entrada)
        return entradas

    def guardar_formatos(self, datos, nombre_base):
        # Guardar JSON
        with open(f"{nombre_base}.json", 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        
        print(f"Archivo creado: {nombre_base}.json")

# --- Lógica de ejecución ---
if __name__ == "__main__":
    extractor = ExtractorMDF()
    
    # 1. Nombre del archivo
    archivo_entrada = "Diccionario Maya Yucateco.docx" 
    
    if os.path.exists(archivo_entrada):
        texto = extractor.leer_archivo(archivo_entrada)
        datos = extractor.segmentar_mdf(texto)
        extractor.guardar_formatos(datos, "salidaDiccMaya")
    else:
        print(f"Error: No se encuentra el archivo '{archivo_entrada}' en la carpeta.")