# Extractores de Diccionarios a Formato MDF (JSON)

Este repositorio contiene dos extractores capaces de convertir diccionarios en formato `.docx` a un esquema estructurado basado en el estándar **MDF (Machine-Readable Dictionary Format)**, generando archivos de salida en **JSON**.

## Diccionarios procesados

- **VOCABULARIO ISKONAWA-CASTELLANO-INGLÉS**
- **Vocabulario Popoluca de la Sierra – Español – Popoluca de la Sierra**



## Cómo usar

### 1. Descarga los archivos fuente

Descarga los archivos `.docx` modificados:

- `DiccionarioPopulaca.docx`
- `DiccionarioIskonawa.docx`

> **Nota:** Estos documentos fueron preprocesados para conservar únicamente las entradas léxicas. Se eliminó la introducción y cualquier sección que no correspondiera a definiciones.

### 2. Ejecuta el programa

Corre el extractor correspondiente. Al finalizar, se generarán dos archivos JSON con todas las entradas del diccionario etiquetadas en formato MDF.



## Etiquetas MDF propuestas

| Etiqueta | Descripción |
|----------|-------------|
| `\id` | Número de identificación de la entrada |
| `\lx` | Lexema / *headword* (entrada principal) |
| `\ps` | Parte de la oración |
| `\sn` | Número de sentido / acepción |
| `\se` | Subentrada (formas derivadas) |
| `\ph` | Transcripción fonética |
| `\mr` | Representación morfológica |
| `\de` | Definición en inglés |
| `\dn` | Definición en español |
| `\ge` | Glosa en inglés |
| `\gn` | Glosa en español |
| `\xv` | Ejemplo en lengua vernácula |
| `\xe` | Traducción del ejemplo al inglés |
| `\xn` | Traducción del ejemplo al español |
| `\rf` | Fuente del ejemplo |
| `\cf` | Referencia cruzada genérica |
| `\lf` | Función léxica (relación semántica) |
| `\lv` | Lexema relacionado en red semántica |
| `\wv` | Archivo de audio |
| `\vd` | Archivo de video |
| `\nt` | Notas generales |
| `\et` | Etimología |
| `\sc` | Nombre científico |
| `\lo` | Localidad de registro |
| `\pc` | Archivo de imagen |
