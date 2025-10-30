# Capítulo 2 — Lexer (pseudocódigo detallado y guiado)

Meta del capítulo: tener una receta clara para transformar texto en tokens, lista para implementar en el Cap. 3.

El lexer convierte texto en una secuencia de tokens. Empezaremos por los bloques más útiles de Markdown básico:
- Encabezados: líneas que empiezan con `#` (1 a 6), seguidos de espacio y texto
- Listas: marcadores `-`, `+`, `*` (no ordenadas) y `1.` (ordenadas)
- Cercas de código: líneas que son solo ``` (abrir/cerrar bloque)
- Texto, espacios y saltos de línea

Clave #1 del lexer: ORDEN. Primero patrones más específicos, luego los genéricos.

---

## 1) Reglas (versión simple, comentadas)

- HEADING: `^#{1,6}[\t ]+`  (al inicio de línea, 1-6 almohadillas + espacio)
- LIST_MARKER: `^(?:[-*+][\t ]+|\d+[.][\t ]+)`  (viñetas o numeradas tipo `1.`)
- CODE_FENCE: `^```[\t ]*$`  (línea que es solo ``` con espacios opc.)
- NEWLINE: `\n`  (salto de línea)
- WHITESPACE: `[\t ]+`  (espacios/tabuladores)
- TEXT: todo lo demás que no caiga en las anteriores (no vacío)

Nota: en la implementación real podrás usar un “regex maestro” con grupos nombrados para escanear de forma eficiente.

---

## 2) Pseudocódigo de tokenize(text) (paso a paso)

```text
function tokenize(text):
  tokens = []
  line = 1
  col = 1

  i = 0
  while i < len(text):
    # 1) Específicos de comienzo de línea
    if match_at_position(text, i, CODE_FENCE):
      value = matched_string
      tokens.append({type: 'CODE_FENCE', value, position: {line, column: col}})
      advance(i, value)
      update(line, col, value)
      continue

    if match_line_start(text, i) and match_at_position(text, i, HEADING):
      value = matched_string  # incluye los # y el espacio
      tokens.append({type: 'HEADING', value, position: {line, column: col}})
      rest_of_line = consume_until_newline(text, i + len(value))
      if rest_of_line:
        tokens.append({type: 'TEXT', value: rest_of_line, position: {line, column: col + len(value)}})
        advance(i, rest_of_line)
        update(line, col, rest_of_line)
      continue

    if match_line_start(text, i) and match_at_position(text, i, LIST_MARKER):
      value = matched_string  # p.ej., "- ", "1. "
      tokens.append({type: 'LIST_MARKER', value, position: {line, column: col}})
      continue  # el resto de la línea caerá en TEXT/WHITESPACE

    # 2) Patrones generales
    if match_at_position(text, i, NEWLINE):
      tokens.append({type: 'NEWLINE', value: "\n", position: {line, column: col}})
      advance(i, "\n"); line += 1; col = 1
      continue

    if match_at_position(text, i, WHITESPACE):
      value = matched_spaces
      tokens.append({type: 'WHITESPACE', value, position: {line, column: col}})
      advance(i, value); col += len(value)
      continue

    # 3) Si nada de lo anterior, consumir TEXT hasta el próximo punto de corte
    value = read_until(text, i, stop_patterns=[NEWLINE, WHITESPACE, CODE_FENCE])
    tokens.append({type: 'TEXT', value, position: {line, column: col}})
    advance(i, value); col += len(value)

  return tokens
```

Detalles prácticos:
- `match_line_start`: ciertas reglas (heading/list/code fence) solo se prueban al inicio de la línea.
- Alternativa: partir por líneas y procesar cada línea con reglas de comienzo de línea primero.

---

## 3) Ejemplos de entrada/salida (esperada, guiados)

Entrada 1:
```md
# Titulo

Texto
```
Salida (tokens, esquemática): explica en una línea por qué aparece cada token.
```text
HEADING("# ") TEXT("Titulo") NEWLINE
NEWLINE
TEXT("Texto") NEWLINE
```

Entrada 2:
```md
- Item 1
- Item 2
```
Salida:
```text
LIST_MARKER("- ") TEXT("Item") WHITESPACE TEXT("1") NEWLINE
LIST_MARKER("- ") TEXT("Item") WHITESPACE TEXT("2") NEWLINE
```

Entrada 3 (cerca de código):
```md
```
linea
```
```
Salida:
```text
CODE_FENCE("```") NEWLINE
TEXT("linea") NEWLINE
CODE_FENCE("```") NEWLINE
```

---

## 4) Errores y decisiones (guía de diseño)
- Si una cerca se abre y no se cierra, el lexer no falla: el parser/validador reportará el problema más adelante.
- El lexer no resuelve inline (énfasis, links); eso se hará en otra fase.

---

## 5) Ejercicios (con pistas)
1) Ajusta `HEADING` para aceptar `###` sin espacio (pista: `^#{1,6}(?:\s+|$)`).
2) Añade marcadores numéricos con paréntesis: acepta `\d+[)]` además de `\d+[.]`.
3) Decide qué hacer con líneas de solo espacios: ¿colapsar a `NEWLINE` o emitir `WHITESPACE` y luego `NEWLINE`?
