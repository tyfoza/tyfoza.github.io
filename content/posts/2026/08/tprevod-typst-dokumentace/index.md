---
title: "Typst a převod na blog"
date: 2026-08-19T01:11:08+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.16bit"]
draft: false
---
# Budou delší články na blogu
K programům a projektům tvořím místy rozsáhlou dokumentaci ve formátu Typst.\
Takový moderní nástupce LaTeXu. Má pěknou sazbu a umí hezky matematiku.

Hotový `.typ` umíme převést do `.md` pomocí `pandoc`. A výsledný `.md` soubor lze
s minimálními úpravami vložit na tento blog, tedy do systému `hugo`.

Nebudu muset odkazovat hotové PDF, ale můžu text převést do blogové příspěvku a
zachovat matematickou sazbu s využitím KaTeX. Vtipné je, že jsem na Typst přešel
především proto, že v něm píše výrazně komfortněji než v LyXu, který jsem používal
roky.

[výborná přednáška o Typst](https://www.youtube.com/watch?v=iPT5Kbf_EJs)

### Převod Typst na Markdown
`pandoc vstup.typ -f typst -t markdown+tex_math_dollars+pipe_tables-grid_tables-multiline_tables -o vystup.md`

### převodní skript `typ2md`

``` bash
#!/bin/bash

# Kontrola, zda byl zadán vstupní parametr
if [ -z "$1" ]; then
    echo "Použití: $0 <soubor.typ>"
    exit 1
fi

INPUT_FILE="$1"

# Kontrola, zda vstupní soubor existuje
if [ ! -f "$INPUT_FILE" ]; then
    echo "Chyba: Soubor '$INPUT_FILE' nebyl nalezen."
    exit 1
fi

# Nahrazení koncovky .typ za .md
OUTPUT_FILE="${INPUT_FILE%.typ}.md"

echo "Převádím: $INPUT_FILE -> $OUTPUT_FILE"

# Samotný převod s optimalizacemi pro Hugo (matematika + pipe tabulky)
pandoc "$INPUT_FILE" \
    -f typst \
    -t markdown+tex_math_dollars+pipe_tables-grid_tables-multiline_tables \
    -o "$OUTPUT_FILE"

# Vyhodnocení výsledku
if [ $? -eq 0 ]; then
    echo "Převod byl úspěšný!"
else
    echo "Při převodu došlo k chybě."
    exit 1
fi
```
