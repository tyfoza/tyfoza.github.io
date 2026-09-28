---
title: "Co je VT100 a jak fungují Escape Sekvence"
date: 2026-08-19T23:50:54+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

Terminál DEC VT100 (uvedený na trh v roce 1978) se stal průmyslovým
standardem pro textovou komunikaci. Namísto přímého zápisu do
videopaměti (framebufferu) komunikuje počítač s terminálem výhradně
pomocí proudu znaků po sériové lince.

Pokud terminál obdrží běžný ASCII znak (např. litera 'A', kód 65),
vykreslí ho na aktuální pozici kurzoru. Pokud však obdrží speciální
**Escape znak** (`ASCII 27` / `0x1B` / `CHR$(27)`), přepne se do režimu
zpracování příkazu.



**ESC + `[` + \[Parametry\] + Příkazový znak**


Sekvence začínající dvojicí `ESC [` se označují jako **CSI** (*Control
Sequence Introducer*). Většina příkazů má formát
`ESC [ číslo1 ; číslo2 ... příkaz`.

---

# Kompletní Přehled VT100 / ANSI Escape Sekvencí

Při práci s terminálem (např. v nástroji `tio`, `PuTTY` nebo na fyzickém
terminálu) můžete využít širokou škálu příkazů:

## Řízení Kurzoru

|                        |                  |                                      |
|:-----------------------|:---------------:|:-------------------------------|
| **Escape Sekvence**    | **Zkrácený Kód** | **Popis Funkce**                     |
| `ESC [ H`              |      `CUP`       | Posun na pozici \[1,1\] (Home)       |
| `ESC [ Y ; X H`        |      `CUP`       | Posun kurzoru na řádek Y a sloupec X |
| `ESC [ Y ; X f`        |      `HVP`       | Ekvivalentní příkaz k `H`            |
| `ESC [ N A`            |      `CUU`       | Posun kurzoru o N řádků NAHORU       |
| `ESC [ N B`            |      `CUD`       | Posun kurzoru o N řádků DOLŮ         |
| `ESC [ N C`            |      `CUF`       | Posun kurzoru o N sloupců DOPRAVA    |
| `ESC [ N D`            |      `CUB`       | Posun kurzoru o N sloupců DOLEVA     |
| `ESC [ ? 25 l`         |    `DECTCEM`     | Skryje blikající kurzor              |
| `ESC [ ? 25 h`         |    `DECTCEM`     | Zobrazí kurzor                       |
| `ESC 7` nebo `ESC [ s` |     `DECSC`      | Uloží aktuální pozici kurzoru        |
| `ESC 8` nebo `ESC [ u` |     `DECRC`      | Obnoví uloženou pozici kurzoru       |

## Mazání Obrazovky a Řádků

|                              |                  |                                       |
|:-----------------------|:---------------:|:-------------------------------|
| **Escape Sekvence**          | **Zkrácený Kód** | **Popis Funkce**                      |
| `ESC [ 2 J`                  |      `ED2`       | Smaže celou obrazovku                 |
| `ESC [ 0 J` (nebo `ESC [ J`) |      `ED0`       | Smaže obrazovku od kurzoru do konce   |
| `ESC [ 1 J`                  |      `ED1`       | Smaže obrazovku od začátku do kurzoru |
| `ESC [ 2 K`                  |      `EL2`       | Smaže celý aktuální řádek             |
| `ESC [ 0 K` (nebo `ESC [ K`) |      `EL0`       | Smaže řádek od kurzoru do konce       |
| `ESC [ 1 K`                  |      `EL1`       | Smaže řádek od začátku do kurzoru     |

## Formátování Textu a Barvy (SGR - Select Graphic Rendition)

Atributy textu se nastavují pomocí `ESC [ N m`. Více parametrů lze
řetězit pomocí středníku (např. `ESC [ 1;31;40m` nastaví tučný červený
text na černém pozadí).

|           |               |                                                                                                      |
|:-----------------:|:-----------------:|:-----------------------------------|
| **Kód N** | **Kategorie** | **Význam / Účinek**                                                                                  |
|    `0`    |     Reset     | Vypne všechny atributy a barvy (návrat k výchozímu)                                                  |
|    `1`    |     Styl      | Tučné písmo (Bold / Zvýšená intenzita)                                                               |
|    `4`    |     Styl      | Podtržené písmo (Underline)                                                                          |
|    `5`    |     Styl      | Blikání (Blink)                                                                                      |
|    `7`    |     Styl      | Inverzní zobrazení (Invertuje pozadí a popředí)                                                      |
| `30 - 37` | Barva popředí | Černá (30), Červená (31), Zelená (32), Žlutá (33), Modrá (34), Fialová (35), Azurová (36), Bílá (37) |
| `40 - 47` | Barva pozadí  | Černá (40), Červená (41), Zelená (42), Žlutá (43), Modrá (44), Fialová (45), Azurová (46), Bílá (47) |
| `90 - 97` | Jasné popředí | Jasné varianty základních barev (ANSI rozšíření)                                                     |

## Pokročilé Řízení Terminálu

-   **Nastavení oblasti rolování (Scroll Region):**
    `ESC [ top ; bottom r` -- Omezí rolování textu pouze na zadané
    řádky.

-   **Měkký reset terminálu:** `ESC ! p` -- Obnoví výchozí stav
    nastavení.

-   **Dotaz na pozici kurzoru:** `ESC [ 6 n` -- Terminál odpoví do
    sériové linky sekvencí `ESC [ Y ; X R`.

---

# Ukázky Použití

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Ehanced BASIC (68k-MBC)</strong></p>
<pre class="basic"><code>10 E$ = CHR$(27) + &quot;[&quot;
20 PRINT E$;&quot;2J&quot;; E$;&quot;1;1H&quot;;
30 PRINT E$;&quot;1;31mCerveny text&quot;;E$;&quot;0m&quot;
</code></pre></td>
<td><p><strong>Jazyk C (CP/M-68K / GCC)</strong></p>
<div class="sourceCode" id="cb2"><pre
class="sourceCode c"><code class="sourceCode c"><span id="cb2-1"><a href="#cb2-1" aria-hidden="true" tabindex="-1"></a><span class="pp">#include </span><span class="im">&lt;stdio.h&gt;</span></span>
<span id="cb2-2"><a href="#cb2-2" aria-hidden="true" tabindex="-1"></a><span class="dt">void</span> clear<span class="op">(</span><span class="dt">void</span><span class="op">)</span> <span class="op">{</span></span>
<span id="cb2-3"><a href="#cb2-3" aria-hidden="true" tabindex="-1"></a>    printf<span class="op">(</span><span class="st">&quot;</span><span class="sc">\033</span><span class="st">[2J</span><span class="sc">\033</span><span class="st">[H&quot;</span><span class="op">);</span></span>
<span id="cb2-4"><a href="#cb2-4" aria-hidden="true" tabindex="-1"></a>    printf<span class="op">(</span><span class="st">&quot;</span><span class="sc">\033</span><span class="st">[1;32mZeleny text</span><span class="sc">\033</span><span class="st">[0m</span><span class="sc">\n</span><span class="st">&quot;</span><span class="op">);</span></span>
<span id="cb2-5"><a href="#cb2-5" aria-hidden="true" tabindex="-1"></a><span class="op">}</span></span></code></pre></div></td>
</tr>
</tbody>
</table>


