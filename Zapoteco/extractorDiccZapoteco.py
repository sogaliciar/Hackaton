from docx import Document
import re
import json

POS_TAGS = [
    "interj.", "cuant.", "pron.", "prep.", "conj.", "expr.", "part.", "deic.", "adj.", "adv.",
    "inter.", "det.", "num.", "neg.", "loc.", "art.", "aux.", "pref.", "suf.", "vt.", "vi.", "s."
]
POS_REGEX = r"(?:%s)" % "|".join(re.escape(x) for x in POS_TAGS)


def clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_heading(raw: str) -> bool:
    """
    Omite encabezados alfabéticos como A, B, CH, KW, RR, etc.
    """
    t = clean(raw)
    return bool(re.fullmatch(r"[A-ZÁÉÍÓÚÜÑ]{1,3}", t))


def starts_with_pos(text: str) -> bool:
    return re.match(rf"^(?:{POS_REGEX})(?=\s|$)", text) is not None


def looks_like_main_entry(text: str) -> bool:
    """
    Distingue entradas principales de subentradas con sangría.
    """
    if "[" in text and re.search(rf"\[[^\]]+\]\s*(?:\[[^\]]+\]\s*)*(?:{POS_REGEX})", text):
        return True
    if re.search(rf"^[^\[]+?\s+(?:{POS_REGEX})(?=\s|$)", text):
        return True
    return False


def extract_initial_ph(rest: str):
    """
    Extrae una o más transcripciones fonéticas iniciales: [ ... ] [ ... ]
    """
    ph = []
    rest = rest.lstrip()

    while True:
        m = re.match(r"^\[([^\]]+)\]\s*(.*)$", rest)
        if not m:
            break
        ph.append(m.group(1).strip())
        rest = m.group(2).lstrip()

    return ph, rest


def parse_definitions(rest: str):
    """
    Intenta separar:
    dn = definición en español
    de = definición en inglés
    examples = resto del texto con ejemplos
    """
    rest = clean(rest)
    if not rest:
        return "", "", ""

    segments = re.split(r"(?<=\.)\s+", rest, maxsplit=2)
    segments = [s.strip() for s in segments if s.strip()]

    dn = ""
    de = ""
    examples = ""

    if len(segments) >= 3:
        dn = segments[0].rstrip(".")
        de = segments[1].rstrip(".")
        examples = segments[2]

    elif len(segments) == 2:
        first = segments[0].rstrip(".")
        second = segments[1].strip()

        if "|" in second or any(ch in second for ch in "¿¡"):
            if first.count(",") == 1:
                dn, de = [x.strip() for x in first.split(",", 1)]
            else:
                dn = first
            examples = second
        else:
            dn = first
            de = second.rstrip(".")

    elif len(segments) == 1:
        first = segments[0].rstrip(".")
        if first.count(",") == 1:
            dn, de = [x.strip() for x in first.split(",", 1)]
        else:
            dn = first

    return dn, de, examples


def extract_metadata(text: str):
    """
    Extrae campos auxiliares:
    - mr: representación morfológica {...}
    - lv: variantes o lexemas relacionados ≈...
    - cf: referencias cruzadas cfr.
    - et: etimología/protoformas *...
    - nt: notas generales, por ejemplo préstamos Esp.
    """
    data = {}
    if not text:
        return data

    mr = re.findall(r"\{([^{}]+)\}", text)
    if mr:
        data["mr"] = [clean(x) for x in mr]

    lv = re.findall(r"≈\s*([^≈*{}]+?)(?=(?:≈|\*{1,2}|cfr\.|Esp\.|$))", text)
    if lv:
        data["lv"] = [clean(x).rstrip(".") for x in lv]

    cf = re.findall(r"cfr\.\s*([^*.]+?)(?=(?:\*{1,2}|Esp\.|$))", text, flags=re.IGNORECASE)
    if cf:
        data["cf"] = [clean(x).rstrip(".") for x in cf]

    et = re.findall(r"\*{1,2}([^*]+)", text)
    if et:
        data["et"] = [clean(x).rstrip(".") for x in et]

    notes = []
    esp = re.findall(r"Esp\.\s*([^*.]+?)(?=(?:\*{1,2}|$))", text)
    notes.extend([f"Esp. {clean(x).rstrip('.')}" for x in esp])

    if notes:
        data["nt"] = " | ".join(notes)

    return data


def parse_examples(text: str):
    """
    Busca ejemplos del tipo:
    xv | xn | xe

    Cuando solo se logran detectar dos partes, conserva xv y xn.
    """
    text = clean(text)
    if not text or "|" not in text:
        return []

    # corta metadatos que suelen venir al final
    text = re.split(r"\s(?=(?:≈|cfr\.|Esp\.|\*{1,2}|\{))", text, maxsplit=1)[0]
    parts = [p.strip() for p in text.split("|") if p.strip()]

    examples = []
    i = 0

    while i < len(parts):
        if i + 2 < len(parts):
            examples.append({
                "xv": parts[i],
                "xn": parts[i + 1],
                "xe": parts[i + 2]
            })
            i += 3

        elif i + 1 < len(parts):
            second = parts[i + 1]
            m = re.match(r"(.+?\.)\s+([A-Z].+)", second)
            if m:
                examples.append({
                    "xv": parts[i],
                    "xn": m.group(1).strip(),
                    "xe": m.group(2).strip()
                })
            else:
                examples.append({
                    "xv": parts[i],
                    "xn": second
                })
            i += 2

        else:
            break

    return examples


def build_entry(lx="", ps="", ph=None, dn="", de="", examples_text="", meta_text="",
                entry_type="entry", parent_lx=""):
    entry = {
        "lx": clean(lx),
        "ps": ps.strip(),
        "sn": "1",
        "entry_type": entry_type
    }

    if parent_lx:
        entry["parent_lx"] = parent_lx

    if ph:
        entry["ph"] = ph
    if dn:
        entry["dn"] = dn
    if de:
        entry["de"] = de

    examples = parse_examples(examples_text)
    if examples:
        entry["ejemplos"] = examples

    entry.update(extract_metadata(meta_text))
    return entry


def parse_main(text: str):
    text = clean(text)

    if "[" in text:
        lx, rest = text.split("[", 1)
        lx = clean(lx)
        rest = "[" + rest
        ph, rest = extract_initial_ph(rest)

        m = re.match(rf"^(?P<ps>{POS_REGEX})(?=\s|$)\s*(?P<rest>.*)$", rest)
        ps = m.group("ps") if m else ""
        rest = m.group("rest") if m else rest
    else:
        m = re.search(rf"(?P<ps>{POS_REGEX})(?=\s|$)", text)
        if m:
            lx = clean(text[:m.start()])
            ps = m.group("ps")
            rest = text[m.end():]
        else:
            first, _, rest = text.partition(".")
            lx = clean(first)
            ps = ""
        ph = []

    dn, de, examples_text = parse_definitions(rest)

    return build_entry(
        lx=lx,
        ps=ps,
        ph=ph,
        dn=dn,
        de=de,
        examples_text=examples_text or rest,
        meta_text=rest,
        entry_type="entry"
    )


def parse_sense(text: str, parent_lx: str):
    text = clean(text)

    m = re.match(rf"^(?P<ps>{POS_REGEX})(?=\s|$)\s*(?P<rest>.*)$", text)
    ps = m.group("ps")
    rest = m.group("rest")

    dn, de, examples_text = parse_definitions(rest)

    return build_entry(
        lx=parent_lx,
        ps=ps,
        dn=dn,
        de=de,
        examples_text=examples_text or rest,
        meta_text=rest,
        entry_type="sense",
        parent_lx=parent_lx
    )


def parse_subentry(text: str, parent_lx: str):
    text = clean(text)

    # Subentrada con lexema propio y una o más transcripciones
    if "[" in text:
        lx, rest = text.split("[", 1)
        lx = clean(lx)
        rest = "[" + rest
        ph, rest = extract_initial_ph(rest)

        m = re.match(rf"^(?P<ps>{POS_REGEX})(?=\s|$)\s*(?P<rest>.*)$", rest)
        ps = m.group("ps") if m else ""
        rest = m.group("rest") if m else rest

        dn, de, examples_text = parse_definitions(rest)

        return build_entry(
            lx=lx,
            ps=ps,
            ph=ph,
            dn=dn,
            de=de,
            examples_text=examples_text or rest,
            meta_text=rest,
            entry_type="subentry",
            parent_lx=parent_lx
        )

    # Sentido alterno del mismo lexema, ej. "beo' mes. month."
    if text.startswith(parent_lx + " "):
        rest = text[len(parent_lx):].strip()
        dn, de, examples_text = parse_definitions(rest)

        return build_entry(
            lx=parent_lx,
            dn=dn,
            de=de,
            examples_text=examples_text or rest,
            meta_text=rest,
            entry_type="sense",
            parent_lx=parent_lx
        )

    # Fallback: conservar el texto bruto en vez de inventar campos
    entry = build_entry(
        lx=text,
        entry_type="subentry",
        parent_lx=parent_lx
    )
    entry["raw"] = text
    return entry


def leer_docx(ruta: str):
    doc = Document(ruta)
    return [p.text for p in doc.paragraphs if p.text.strip()]


def procesar_docx(ruta: str):
    paragraphs = leer_docx(ruta)
    resultado = []
    current_lx = ""

    for raw in paragraphs:
        if is_heading(raw):
            continue

        trimmed = clean(raw)
        leading_ws = bool(raw[:1].isspace())

        if starts_with_pos(trimmed) and current_lx:
            entry = parse_sense(trimmed, current_lx)

        elif leading_ws and current_lx and not looks_like_main_entry(trimmed):
            entry = parse_subentry(trimmed, current_lx)

        else:
            entry = parse_main(trimmed)
            current_lx = entry["lx"]

        entry["id"] = len(resultado) + 1
        resultado.append(entry)

    return resultado


def guardar_json(data, ruta_salida: str):
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    archivo = "diccionario_zapoteco.docx"
    salida = "salidaDiccZapoteco.json"

    data = procesar_docx(archivo)
    guardar_json(data, salida)
    print(f"Diccionario listo: {salida} ({len(data)} entradas)")


if __name__ == "__main__":
    main()
