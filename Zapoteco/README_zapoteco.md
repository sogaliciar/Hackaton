# Diccionario zapoteco → MDF (JSON)

Esta carpeta contiene la propuesta de extracción para el diccionario zapoteco del hackatón. El objetivo es convertir un diccionario en formato `.docx` a una salida estructurada en **JSON** usando etiquetas inspiradas en **MDF (Machine-Readable Dictionary Format)**.

## Archivos de esta carpeta

Se recomienda que la carpeta `zapoteco/` quede así:

```text
zapoteco/
├── README.md
├── extractorDiccZapoteco.py
├── schema_diccionario_zapoteco.yaml
├── salidaDiccZapoteco.json
└── diccionario_zapoteco.docx
```

### Descripción de cada archivo

- `README.md`: explicación de la solución, estructura y forma de uso.
- `extractorDiccZapoteco.py`: script que procesa el `.docx` y genera la salida JSON.
- `schema_diccionario_zapoteco.yaml`: definición del esquema esperado para cada entrada léxica.
- `salidaDiccZapoteco.json`: salida generada por el extractor.
- `diccionario_zapoteco.docx`: documento fuente preprocesado o base de trabajo.

## Esquema de datos

La propuesta usa etiquetas MDF centrales y algunos campos auxiliares para conservar mejor la estructura del diccionario.

### Campos principales

- `id`: identificador único de la entrada.
- `lx`: lexema o palabra principal.
- `ps`: parte de la oración.
- `sn`: número de sentido o acepción.
- `se`: subentrada.
- `ph`: transcripción fonética.
- `dn`: definición en español.
- `de`: definición en inglés.
- `xv`: ejemplo en lengua originaria.
- `xn`: traducción del ejemplo al español.
- `xe`: traducción del ejemplo al inglés.
- `cf`: referencia cruzada.
- `et`: etimología.
- `mr`: representación morfológica.
- `nt`: nota general.

### Campos auxiliares de implementación

- `entry_type`: distingue si el registro es una entrada principal, subentrada o sentido adicional.
- `parent_lx`: indica el lexema padre cuando una subentrada depende de otra.
- `raw`: conserva texto original cuando una línea no puede separarse con total seguridad.

## Qué detecta el extractor

El script intenta reconocer automáticamente:

- Lexema principal.
- Pronunciaciones entre corchetes.
- Categoría gramatical.
- Definición en español.
- Definición en inglés.
- Ejemplos y sus traducciones.
- Subentradas con sangría.
- Marcas etimológicas como `*` y `**`.
- Referencias como `cfr.` o equivalentes.

## Cómo ejecutar

Instala la dependencia necesaria:

```bash
pip install python-docx
```

Ejecuta el extractor dentro de esta carpeta:

```bash
python extractorDiccZapoteco.py
```

Si el archivo fuente se llama `diccionario_zapoteco.docx`, el script generará:

```bash
salidaDiccZapoteco.json
```

## Ejemplo de salida

```json
{
  "id": 1,
  "lx": "awá'",
  "ps": "part.",
  "sn": "1",
  "entry_type": "entry",
  "ph": ["awáʔ", "ʔawáʔ"],
  "dn": "sí",
  "de": "yes",
  "ejemplos": [
    {
      "xv": "Awa, llsedla'be' di'llwrall",
      "xn": "Sí, estoy enseñando zapoteco",
      "xe": "Yes, I am teaching Zapotec."
    }
  ]
}
```

## Decisiones de diseño

1. **No se fuerza una segmentación perfecta** cuando el texto del diccionario es ambiguo.
2. **Se preserva información original** en `raw` para no inventar estructura.
3. **Se separan subentradas y sentidos** para que la salida sea reutilizable después.
4. **Se prioriza trazabilidad** frente a una limpieza excesiva.

## Limitaciones actuales

- Algunas entradas tienen formato irregular.
- Hay líneas donde español, inglés, etimología y notas aparecen mezclados.
- Algunas subentradas pueden requerir corrección manual posterior.
- La separación exacta entre glosa, definición y nota depende de qué tan uniforme venga el `.docx`.

## Siguiente mejora sugerida

Como siguiente paso, se puede homologar completamente esta salida con el estilo exacto de los otros extractores del repositorio para que todos los idiomas compartan el mismo formato final.
