# Capítulo 1 — Introducción y flujo general (guía paso a paso)

Este proyecto construye, paso a paso y sin POO, un validador de Markdown que:
- Analiza texto en tokens (lexer)
- Construye un árbol de sintaxis de alto nivel (AST) (parser)
- Aplica reglas de validación (validator)
- Genera un esquema tipo DTD a partir del AST (schema)
- (Opcional) Renderiza HTML a partir del mismo AST (html)

Objetivo: al finalizar este capítulo sabrás qué piezas construirás, por qué existen y cómo se conectan, con un mapa claro para avanzar.

---

## 1) Vocabulario mínimo (con ejemplos mentales)

- Lexer: trocea el texto en piezas etiquetadas (tokens). Piensa en “palabras con etiqueta de tipo”. Ej: `HEADING`, `LIST_MARKER`, `TEXT`, `NEWLINE`.
- Parser: agrupa tokens en estructura (AST). Piensa en “árbol de secciones y bloques”. Ej: `DOCUMENT > HEADING + PARAGRAPH + LIST`.
- Validator: mira el árbol y te dice si hay problemas. Ej: “salto de H1 a H3”, “lista con ítem vacío”.
- DTD Generator: a partir de lo que aparece en el árbol, redacta un esquema que describe qué nodos existen y cómo pueden anidarse.
- Renderer HTML (opcional): dibuja el árbol como HTML.

Diagrama de flujo (conceptual):

Texto Markdown → Lexer → Tokens → Parser → AST → Validator → {OK | Issues}
                                              ↘ DTD (esquema)
                                              ↘ HTML (opcional)

---

## 2) Formatos de datos (contratos simples que usaremos)

- Token (dict): `{"type": "HEADING"|"TEXT"|..., "value": str, "position": {"line": int, "column": int}}`

- AST (dict anidado):
  - Raíz: `{"type": "DOCUMENT", "children": [...]}`
  - Hijos típicos: `{"type":"HEADING","level":int,"text":str}`, `{"type":"PARAGRAPH","text":str}`, `{"type":"LIST","ordered":bool,"items":[...]}`

- Issue (dict): `{"message": str, "node_type": str|None, "position": {..}|None}`

Mantener estos formatos simples facilita imprimir y testear.

---

## 3) Pseudocódigo de orquestación (visión global)

```text
function run_pipeline(text):
  tokens = tokenize(text)                 # lexer
  ast = parse(tokens)                     # parser (bloques)
  ast = process_inline(ast)               # inline (énfasis, links) — más adelante
  issues = validate(ast)                  # reglas declarativas
  # opcional: dtd = generate_dtd(ast)
  # opcional: html = to_html(ast)
  return { "ast": ast, "issues": issues }
```

Checklist mental al implementar:
- Primero bloques (headings, párrafos, listas, code fences). Inline después.
- Empieza con 1-2 reglas de validación sencillas; añade más luego.

---

## 4) Ejemplo conceptual (de texto a árbol)

Entrada Markdown:

```md
# Título

Un párrafo con texto.

- Item 1
- Item 2
```

Tokens esperados (idea simplificada; exactitud no crítica aquí):

```text
HEADING("# ") TEXT("Título") NEWLINE
NEWLINE
TEXT("Un") WHITESPACE TEXT("párrafo") WHITESPACE TEXT("con") WHITESPACE TEXT("texto.") NEWLINE
NEWLINE
LIST_MARKER("-") WHITESPACE TEXT("Item") WHITESPACE TEXT("1") NEWLINE
LIST_MARKER("-") WHITESPACE TEXT("Item") WHITESPACE TEXT("2") NEWLINE
```

AST esperado (bloques, indentado):

```text
DOCUMENT
  HEADING(level=1, text="Título")
  PARAGRAPH(text="Un párrafo con texto.")
  LIST(ordered=false)
    LIST_ITEM(text="Item 1")
    LIST_ITEM(text="Item 2")
```

---

## 5) Pseudocódigo del lexer (resumen; Cap. 2 lo detalla)

```text
function tokenize(text):
  init tokens = []
  for each line in text:
    if line starts with "#" -> emitir HEADING + resto como TEXT
    else if line starts with list marker ("- ", "+ ", "* ", "1. ") -> LIST_MARKER + resto como TEXT
    else if line is code fence ("```") -> CODE_FENCE
    else if line is empty -> NEWLINE (y quizá otra marca de separación)
    else -> dividir en TEXT/WHITESPACE/NEWLINE básicos
  return tokens
```

Regla de oro: patrones más específicos antes que genéricos (ej., `HEADING` antes que `TEXT`).

---

## 6) Pseudocódigo del parser (resumen)

```text
function parse(tokens):
  root = DOCUMENT
  current_paragraph = []
  for tok in tokens:
    if tok.type == HEADING:
      flush_paragraph_if_any()
      add_node(HEADING(level, text))
    else if tok.type == LIST_MARKER:
      flush_paragraph_if_any()
      start_or_append_list_item()
    else if tok.type == CODE_FENCE:
      flush_paragraph_if_any()
      toggle_code_block_until_next_fence()
    else if tok.type == NEWLINE:
      maybe_flush_paragraph_on_blank_line()
    else:
      current_paragraph.append(tok)
  flush_paragraph_if_any()
  return root
```

Claves prácticas:
- “Flush”: convertir el buffer de texto acumulado en `PARAGRAPH` y vaciarlo.
- Las listas agrupan varios `LIST_ITEM` consecutivos; detecta inicio/fin por líneas en blanco o cambio de tipo.

---

## 7) Validaciones que implementaremos primero

- Saltos de nivel de heading (no pasar de H1 a H3 sin H2 intermedio).
- Ítems de lista vacíos.
- Fences de código sin cierre.

Cada regla es una función que inspecciona el AST y devuelve issues.

---

## 8) Ejercicios (opcionales, cortos, autocontenidos)

1) Escribe a mano los tokens que producirías para:

```md
## Subtítulo

Texto simple.
```

2) Dibuja el AST (en texto) para:

```md
- Uno
- Dos

Parrafo.
```

3) Propón una regla simple (p. ej., “un párrafo no puede superar 500 caracteres”). Describe cómo la detectarías recorriendo el AST.

---

Siguiente: Capítulo 2 — diseñaremos el lexer con pseudocódigo detallado y ejemplos de entrada/salida.


