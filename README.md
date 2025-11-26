# Conversor Markdown a HTML

Conversor de archivos Markdown a HTML mediante un pipeline basado en AST (Abstract Syntax Tree) con validación automática e interfaz gráfica.

## Resumen

Herramienta que convierte archivos Markdown (`.md`) en documentos HTML válidos. Procesa el contenido mediante un pipeline de 4 fases (tokenización → parsing → validación → renderizado), genera un AST intermedio, valida la sintaxis según 10 reglas estándar y produce HTML con escape seguro. Disponible como interfaz gráfica (Flet) y línea de comandos.

## Descripción

El conversor lee archivos Markdown y genera documentos HTML válidos mediante un pipeline modular. Cada fase del proceso es independiente: el lexer tokeniza el texto, el parser construye un AST, el validador verifica reglas de sintaxis y el renderer genera HTML con escape automático para prevenir XSS.

## Características Principales

✓ **Pipeline basado en AST**: Separación clara entre tokenización, parsing, validación y renderizado  
✓ **Validación automática**: 10 reglas de validación (MD001-MD010) con errores y warnings  
✓ **Escape seguro**: Previene XSS escapando contenido HTML automáticamente  
✓ **Interfaz gráfica**: UI intuitiva con Flet para selección de archivos, estilos CSS y visualización de errores  
✓ **Selección de Estilos**: Soporte para aplicar hojas de estilo CSS personalizadas  
✓ **CLI flexible**: Modo línea de comandos para automatización  
✓ **HTML formateado**: Salida con indentación legible  
✓ **Soporte completo**: Headings, párrafos, listas, código, enlaces, imágenes, énfasis  
✓ **Generación de AST**: Guarda el árbol sintáctico en JSON para depuración

## Estructura del Proyecto

```
PROYECTO 1/
├── src/
│   ├── lexer.py          # Tokenización de Markdown (línea por línea)
│   ├── parser.py         # Construcción del AST desde tokens
│   ├── validator.py      # Validación de reglas MD001-MD010
│   ├── renderer.py       # Generación de HTML desde AST
│   ├── specs.py          # Especificaciones: regex, reglas, constantes
│   ├── utils.py          # Funciones auxiliares y gestión de CSS
│   ├── main.py           # CLI principal y orquestación del pipeline
│   ├── ui.py             # Interfaz gráfica con Flet
│   └── logging_utils.py  # Sistema de logging centralizado
├── css/                  # Hojas de estilo CSS disponibles
├── tests/
│   └── test.md           # Archivo Markdown de prueba
├── AST_GEN/              # ASTs generados (JSON con timestamp)
├── HTML_GEN/             # HTMLs generados (CLI sin especificar output)
├── logs/                 # Logs de conversión
└── requirements.txt      # Dependencias (Flet)
```

## Requisitos e Instalación

### Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `flet>=0.23.0` - Framework para la interfaz gráfica

## Uso

### Interfaz Gráfica (UI)

Para abrir la interfaz gráfica:

```bash
python src/main.py
```

O directamente:

```bash
python src/ui.py
```

**Funcionalidades de la UI:**
- Selección de archivo Markdown mediante FilePicker
- **Selección de estilo CSS** desde un menú desplegable (lee archivos de la carpeta `css/`)
- Conversión automática con validación
- Visualización de errores y warnings en tiempo real
- Vista previa del HTML generado
- Guardado del HTML con nombre timestamped
- Logs de conversión en `logs/`

### Línea de Comandos (CLI)

Para usar desde la terminal:

```bash
python src/main.py <archivo.md> [output.html]
```

**Ejemplos:**

```bash
# Guarda automáticamente en HTML_GEN/ con timestamp
python src/main.py tests/test.md

# Especifica archivo de salida personalizado
python src/main.py tests/test.md output.html

# Sin argumentos: abre la UI
python src/main.py
```

**Salida del CLI:**
- Información detallada de cada fase del pipeline (Lexer, Parser, Validator, Renderer)
- Mensajes con formato tipo IDE (colores, etiquetas de estado)
- Lista detallada de errores y warnings con números de línea
- Tracebacks completos en caso de errores
- Estadísticas de tokens, nodos y tamaño del HTML generado

## Pipeline de Conversión

El proceso de conversión sigue un pipeline de 4 fases independientes:

```
┌─────────────┐
│    Lexer    │  ← Texto Markdown → Lista de tokens
└──────┬──────┘
       ↓
┌─────────────┐
│    Parser   │  ← Tokens → AST (árbol de nodos)
└──────┬──────┘
       ↓
┌─────────────┐
│  Validator  │  ← Recorre AST, aplica reglas contextuales
└──────┬──────┘
       ↓
┌─────────────┐
│  Renderer   │  ← AST + CSS (opcional) → HTML
└─────────────┘
```

### 1. Lexer (`lexer.py`)
- **Entrada**: Archivo Markdown (texto crudo)
- **Proceso**: Lee línea por línea y aplica patrones regex definidos en `specs.py`
- **Salida**: Lista de tokens `[{type, line, meta}, ...]`
- **Tokens soportados**: `HEADER`, `PARAGRAPH`, `CODE_BLOCK_START/END`, `UNORDERED_LIST_ITEM`, `ORDERED_LIST_ITEM`, `HORIZONTAL_RULE`, `BLANK_LINE`
- **Inline tokens**: `STRONG`, `EMPHASIS`, `CODE_INLINE`, `LINK`, `IMAGE`

### 2. Parser (`parser.py`)
- **Entrada**: Lista de tokens del lexer
- **Proceso**: Agrupa tokens relacionados y construye un árbol sintáctico
- **Salida**: AST (Abstract Syntax Tree) como diccionario anidado
- **Estrategias**: 
  - `o2o`: Un token → un nodo (headings, hr)
  - `m2o`: Múltiples tokens → un nodo (párrafos)
  - `series`: Secuencia de tokens → lista (listas)
  - `stateful`: Tokens con estado (code blocks)
- **Guardado**: AST se guarda automáticamente en `AST_GEN/` como JSON

### 3. Validator (`validator.py`)
- **Entrada**: AST del parser
- **Proceso**: Recorre el AST y aplica reglas de validación contextuales
- **Salida**: Lista de errores/warnings `[{code, message, severity, line}, ...]`
- **Severidades**: `error` (bloquea) o `warning` (informa)
- **Reglas**: MD001-MD010 (ver sección de Reglas de Validación)

### 4. Renderer (`renderer.py`)
- **Entrada**: AST validado y archivo CSS opcional
- **Proceso**: Convierte cada nodo del AST a su equivalente HTML
- **Salida**: String HTML completo con indentación
- **Seguridad**: Escapa automáticamente contenido HTML para prevenir XSS
- **Estilos**: Vincula automáticamente la hoja de estilos seleccionada
- **Formato**: HTML válido con indentación legible

## Sintaxis Soportada

| Markdown | HTML Generado | Descripción |
|----------|---------------|-------------|
| `# Título` | `<h1>Título</h1>` | Heading nivel 1 |
| `## Subtítulo` | `<h2>Subtítulo</h2>` | Heading nivel 2 |
| `### ...` hasta `######` | `<h3>...</h3>` hasta `<h6>...</h6>` | Headings niveles 3-6 |
| `Texto normal` | `<p>Texto normal</p>` | Párrafo |
| `- Item` o `* Item` | `<ul><li>Item</li></ul>` | Lista no ordenada |
| `1. Item` | `<ol><li>Item</li></ol>` | Lista ordenada |
| ` ```python\ncode\n``` ` | `<pre><code class="language-python">code</code></pre>` | Bloque de código con lenguaje |
| `---` o `***` | `<hr>` | Regla horizontal |
| `**negrita**` | `<strong>negrita</strong>` | Texto en negrita |
| `*cursiva*` | `<em>cursiva</em>` | Texto en cursiva |
| `` `código` `` | `<code>código</code>` | Código inline |
| `[texto](url)` | `<a href="url">texto</a>` | Enlace |
| `![alt](url)` | `<img src="url" alt="alt">` | Imagen |

## Módulos del Proyecto

### `specs.py`
**Rol**: Fuente única de verdad para especificaciones  
**Contiene**:
- Patrones regex para tokens (block e inline)
- Orden de prioridad para tokenización
- Estrategias de agrupación de tokens
- Reglas de validación (MD001-MD010)
- Constantes y transformaciones de metadatos

### `lexer.py`
**Rol**: Tokenización del texto Markdown  
**Funciones principales**:
- `tokenize(file_path)`: Tokeniza un archivo completo
- `tokenize_line(line, line_num)`: Tokeniza una línea individual
- `apply_block_meta_transforms()`: Aplica transformaciones a metadatos
- `apply_inline_meta_transforms()`: Procesa tokens inline

### `parser.py`
**Rol**: Construcción del AST desde tokens  
**Funciones principales**:
- `parse(tokens)`: Orquesta la construcción del AST
- `consume_tokens(tokens)`: Procesa tokens y genera nodos
- `save_ast_to_file(ast)`: Guarda AST en JSON con timestamp

### `validator.py`
**Rol**: Validación del AST según reglas  
**Funciones principales**:
- `validate(ast)`: Valida el AST completo y retorna errores
- `validate_heading()`: Valida reglas MD001, MD002, MD003
- `validate_code_block()`: Valida reglas MD004, MD010
- `validate_list()`: Valida reglas MD005, MD006
- `validate_paragraph()`: Valida regla MD007
- `validate_link()`: Valida regla MD008
- `validate_image()`: Valida regla MD009

### `renderer.py`
**Rol**: Generación de HTML desde AST  
**Funciones principales**:
- `to_html(node, indent, css_file)`: Convierte un nodo AST a HTML recursivamente
- Maneja todos los tipos de nodos: `heading`, `paragraph`, `list`, `list_item`, `code_block`, `hr`, `text`, `strong`, `em`, `code`, `link`, `image`
- Escape automático con `html.escape()`
- Inyección de enlaces CSS

### `utils.py`
**Rol**: Funciones auxiliares  
**Funciones principales**:
- `read_lines(file_path)`: Generador para leer archivos línea por línea
- `list_css_files(css_dir)`: Lista archivos CSS disponibles
- `get_css_path(css_name)`: Resuelve rutas relativas para CSS
- Transformaciones: `transform_level()`, `transform_indent_level()`, `transform_to_int()`, etc.

### `main.py`
**Rol**: Punto de entrada CLI y orquestación  
**Funciones principales**:
- `run_pipeline(file_path)`: Ejecuta el pipeline completo (lexer → parser → validator → renderer)
- `save_html_to_file(html, input_file)`: Guarda HTML con timestamp
- `main(argv)`: Maneja argumentos de línea de comandos y abre UI si no hay argumentos

### `ui.py`
**Rol**: Interfaz gráfica con Flet  
**Funcionalidades**:
- FilePicker para selección de archivos `.md`
- Dropdown para selección de estilos CSS
- Botones para convertir y guardar
- Visualización de errores y warnings en tiempo real
- Vista previa del HTML generado
- Logging integrado a archivo y UI

## Reglas de Validación

El validador implementa 10 reglas basadas en estándares de Markdown:

| Código | Nombre | Severidad | Descripción |
|--------|--------|-----------|-------------|
| **MD001** | `heading-increment` | Warning | Los niveles de heading deben incrementar de uno en uno (no saltar de h1 a h3) |
| **MD002** | `heading-level-range` | Error | Los niveles de heading deben estar entre 1 y 6 |
| **MD003** | `heading-content-required` | Error | Los headings deben tener contenido |
| **MD004** | `code-block-closed` | Error | Los bloques de código deben estar cerrados (```) |
| **MD005** | `list-has-items` | Warning | Las listas deben tener al menos un item |
| **MD006** | `list-item-has-content` | Warning | Los items de lista deben tener contenido |
| **MD007** | `paragraph-has-content` | Warning | Los párrafos deben tener contenido |
| **MD008** | `link-has-url` | Error | Los enlaces deben tener una URL válida |
| **MD009** | `image-has-url` | Error | Las imágenes deben tener una URL válida |
| **MD010** | `code-block-has-content` | Warning | Los bloques de código deben tener contenido |

**Nota**: Los errores (`error`) bloquean la conversión, mientras que los warnings (`warning`) solo informan pero permiten continuar.

## Archivos Generados

### AST_GEN/
Contiene los ASTs generados en formato JSON con nombres timestamped:
```
AST_GEN/ast_YYYYMMDD_HHMMSS.json
```

Cada AST representa la estructura sintáctica del documento Markdown procesado, útil para depuración y análisis.

### HTML_GEN/
Contiene los archivos HTML generados cuando se usa el CLI sin especificar un archivo de salida:
```
HTML_GEN/<nombre_archivo>_YYYYMMDD_HHMMSS.html
```

### logs/
Contiene logs de conversión diarios:
```
logs/conversion_YYYYMMDD.log
```

## Ejemplo de Uso Completo

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Convertir un archivo desde CLI
python src/main.py tests/test.md

# Salida esperada (con formato tipo IDE):
# [INFO] Procesando archivo: test.md
# [INFO] Ruta completa: C:\...\tests\test.md
#
# [LEXER] Tokenizando archivo Markdown...
# [✓] Tokenización completada: 45 tokens generados
# [PARSER] Construyendo AST...
# [✓] AST construido: 8 nodos principales
# [INFO] AST guardado en: AST_GEN/ast_20241110_185057.json
# [VALIDATOR] Validando AST...
# [✗ ERROR] Se encontraron 1 error(es) y 1 advertencia(s):
#   [ERROR] MD003: Headings must have content
#     → Línea 10
#   [WARNING] MD001: Heading levels must increment by one
#     → Línea 5
# [RENDERER] Generando HTML...
# [✓] HTML generado: 15234 caracteres
# [SAVE] Guardando archivo HTML...
# [✓] HTML guardado en: HTML_GEN/test_20241110_185057.html
# [✓] Conversión completada exitosamente

# 3. O usar la interfaz gráfica
python src/main.py
# Selecciona archivo → Convierte → Revisa errores → Guarda HTML
```

## Arquitectura

El proyecto está diseñado con una arquitectura modular que separa claramente las responsabilidades:

- **Separación de responsabilidades**: Cada módulo tiene una función única y bien definida
- **Extensibilidad**: Agregar nuevas construcciones Markdown solo requiere ajustar `specs.py`
- **Testabilidad**: Módulos independientes fáciles de testear de forma aislada
- **Flujo de datos explícito**: La comunicación entre módulos se realiza mediante estructuras de datos simples (dicts, lists)

Cada módulo procesa su entrada y genera una salida bien definida, permitiendo un flujo de datos predecible y fácil de depurar.
