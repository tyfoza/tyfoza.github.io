---
title: "CP/M na 68k-MBC"
date: 2026-08-25T23:17:58+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

# Programování pro CP/M-68K 

Operační systém CP/M-68K poskytuje běžícím programům sadu služeb zvanou
**BDOS** (Basic Disk Operating System). Díky nim program v jazyce C
nemusí znát fyzické detaily hardwaru (např. na kterém pinu
mikrokontroléru PIC je sériová linka). Místo toho program požádá CP/M o
standardizovanou službu -- například "vypiš znak" nebo "přečti klávesu".

Na procesorech řady Motorola 68000 se tyto služby volají softwarovým
přerušením pomocí instrukce `trap #2`.

## Předávání parametrů

Když chceš zavolat funkci BDOS z assembleru, CP/M-68K očekává
následující konvenci:

1.  **Registr `d0`** (spodní word): Číslo funkce BDOS (např. 2 pro výpis
    znaku, 9 pro výpis řetězce).

2.  **Registr `d1`** (nebo `a0` pro adresy): Parametr funkce (např. jaký
    znak vypsat, nebo adresa řetězce v paměti).

3.  **Instrukce `trap #2`**: Předání řízení operačnímu systému.

4.  **Registr `d0`**: Po návratu z `trap #2` obsahuje `d0` výsledek
    operace (např. přečtený znak nebo návratový kód).

---

# Seznam nejdůležitějších funkcí BDOS

Zde je přehled základních funkcí, které se ti budou při programování
retro her a utilit na 68k-MBC nejvíce hodit:


|                  |                    |                                                                                                                                                                                             |
|:----------------------:|:-----------------------|:-----------------------|
| **Číslo v `d0`** | **Název funkce**   | **Popis a parametry**                                                                                                                                                                       |
|        0         | System Reset       | Ukončí program a vrátí uživatele do příkazové řádky (`A>`).                                                                                                                                 |
|        1         | Console Input      | Čeká na stisk klávesy a její znak zobrazí na obrazovce (echo). Výsledek v `d0`.                                                                                                             |
|        2         | Console Output     | Vypíše znak zadaný v registru `d1` na terminál.                                                                                                                                             |
|        6         | Direct Console I/O | Univerzální funkce. Pokud je v `d1` hodnota 255 (`0xFF`), pokusí se přečíst klávesu bez zobrazení (no echo). Pokud klávesa není stisknuta, vrátí v `d0` nulu. Vhodné pro neblokující čtení. |
|        9         | Print String       | Vypíše na obrazovku textový řetězec. V registru `d1` (nebo `a0`) musí být adresa řetězce ukončeného znakem dolaru (`$`).                                                                    |
|        11        | Console Status     | Zkontroluje buffer klávesnice. Pokud je klávesa připravena, vrátí `0xFF` v `d0`. Pokud ne, vrátí `0x00`.                                                                                    |


---

# Příklad 1: Neblokující čtení klávesnice 

Protože staré kompilátory jazyka C (jako Alcyon C) často nepodporují
snadné vkládání assembleru přímo do C kódu (inline assembly), řeší se
systémová volání tak, že se napíše malá funkce v assembleru, která se v
C pouze deklaruje a následně s ním slinkuje.

**Klíčové pravidlo:** Funkce volané z jazyka C musí mít v assembleru na
začátku názvu podtržítko (např. `_getch_noblock`).

## 1. Kód v Assembleru (`KEY.S`)

Zde je onen brilantní a optimalizovaný kód využívající BDOS funkci 11
(Status) a 6 (Direct I/O):

``` nasm
.text
        .globl  _getch_noblock  ; Export pro linker (C kompilátor přidává podtržítka)

_getch_noblock:
        ; Zjištění stavu klávesnice (BDOS 11)
        move.w  #11,d0
        trap    #2
        tst.w   d0              ; Je klávesa stisknuta?
        beq.s   L_empty         ; Pokud ne (d0 == 0), skoč na L_empty

        ; Přečtení znaku bez echa (BDOS 6)
        move.w  #6,d0
        move.l  #255,d1         ; 255 znamená "čti" (bez blokování a zobrazení)
        trap    #2
        andi.l  #255,d0         ; Ořízni případné smetí, ponech jen 8 bitů (ASCII)
        rts                     ; Návrat do C (výsledek je v d0)

L_empty:
        moveq   #0,d0           ; Vrať 0 (žádný znak)
        rts

        .end

```

## 2. Použití v jazyce C (K&R Standard)

Historický dialekt C (tzv. K&R) před příchodem ANSI C (C89) neznal
klíčové slovo `void`, návratový typ byl implicitně `int` a do prototypů
funkcí se nepsaly datové typy parametrů.

``` c
/* Soubor: MAIN.C */

/* Deklarace naší funkce z KEY.S */
int getch_noblock();

main()
{
    int c;

    printf("Stiskni klavesu 'q' pro ukonceni...\n");

    while(1) {
        c = getch_noblock(); /* Volame nas ASM stub */

        if (c != 0) {
            printf("Stisknuto: %c (ASCII: %d)\n", c, c);
            if (c == 'q' || c == 'Q') {
                break;
            }
        }
        /* Zde muze bezet herni smycka (pohyb ufounu, hada, atd.) */
    }

    return 0;
}

```

---

# Příklad 2: Vlastní výpis řetězce
Který se obejde bez těžkopádné funkce printf.

Procesor MC68008 na 68k-MBC je při parsování funkce `printf` docela
vytížený (zabírá cenné takty). Pokud chceme vypsat čistý text (např.
ANSI sekvenci) co nejrychleji, můžeme obalit BDOS funkci 9 (Print
String).

## 1. Kód v Assembleru (`PRINT.S`)

``` nasm
.text
        .globl  _print_cpm

_print_cpm:
        ; Starý K&R C předává parametry přes zásobník.
        ; Návratová adresa je na 4(sp), první parametr (adresa textu) je na 8(sp).
        move.l  8(sp), d1       ; Načti adresu řetězce do d1 pro BDOS
        move.w  #9, d0          ; BDOS funkce 9 (Print String)
        trap    #2
        rts
        .end

```

## 2. Použití v jazyce C

U BDOS funkce 9 musíme pamatovat na to, že CP/M ukončuje řetězce znakem
`$`, nikoliv nulou `\0` jako jazyk C!

``` c
/* Deklarace nasi ASM funkce */
int print_cpm();

main()
{
    /* Retezec musi byt ukonceny znakem dolaru! */
    char *clear_screen = "\033[2J\033[1;1H$";
    char *message = "Tento text se vypsal bleskove pres BDOS volani!$";

    /* Rychle smazani obrazovky a presun kurzoru */
    print_cpm(clear_screen);

    /* Vypsani hlašky */
    print_cpm(message);

    return 0;
}

```

---

# Jak se to celé překládá na 68k-MBC?

Když píšešeme programy na reálném stroji nebo v historickém toolchainu
přímo pro operační systém CP/M-68K, proces probíhá následovně:

> 1.  **Překlad C kódu (Alcyon C):** Kompilátor vezme `MAIN.C` a přeloží
    ho do objektového souboru. Zpracování zaštiťuje dávkový příkaz (přes
    preprocesor, C kompilátor a optimalizátor).

> 2.  **Překlad Assembleru:**

Systémový assembler převede .s do objektových kódů. \
`A> AS68 KEY.S` `A> AS68 PRINT.S`

> 3.  **Slinkování (CLINK):**

Linker spojí objektový soubor Céčka, tvoje zkompilované ASM knihovny a
systémovou céčkovou knihovnu (clib) do spustitelného souboru s příponou
`.68K`.\
`A> CLINK MAIN KEY PRINT`

> 4.  **Spuštění:**

Na obrazovce napíšeš jen jméno vzniklého programu:\
`A> MAIN`

# Parametry z příkazové řádky

Aby program v C mohl přijímat parametry (argumenty) z příkazové řádky,
stačí lehce upravit definici hlavní funkce `main`. Místo prázdných
závorek přidáme dvě speciální proměnné: tradičně se nazývají `argc` a
`argv`.

## Základní syntaxe

``` c
int main(int argc, char *argv[]) {
    // tvůj kód
    return 0;
}

```

## Co tyto proměnné znamenají?

**`argc` (Argument Count):** Celočíselná proměnná, která systému říká,
**kolik** parametrů bylo programu předáno.\
**`argv` (Argument Vector):** Pole textových řetězců (ukazatelů na
znaky), které obsahuje samotné předané parametry.

**Důležité pravidlo:** První parametr, tedy `argv[0]`, je **vždy název
samotného spuštěného programu** (nebo cesta k němu). Skutečné argumenty,
které uživatel zadá, začínají až od indexu `argv[1]`. Proto je hodnota
`argc` vždy minimálně 1, i když programu nepředáš žádný dodatečný
parametr.

---

## Příklad použití

Tady je jednoduchý kód, který projde všechny předané parametry a vypíše
je na obrazovku:

``` c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Celkovy pocet parametru: %d\n", argc);

    for (int i = 0; i < argc; i++) {
        printf("Parametr %d: %s\n", i, argv[i]);
    }

    return 0;
}

```

**Jak to vypadá po spuštění v terminálu:**\
Pokud tento program zkompilujeme (např. jako `program`) a spustíme s
parametry: `./program test 123`

Výstup bude: `Celkovy pocet parametru: 3` `Parametr 0: ./program`
`Parametr 1: test` `Parametr 2: 123`

---

## Převod textu na čísla

Je důležité pamatovat na to, že všechno v poli `argv` je text
(string). I když do příkazové řádky napíšeme číslo `123`, program ho
vidí jako text `"123"`.

Pokud chceme parametr použít k matematickým výpočtům, musíme ho převést
pomocí vestavěných funkcí z knihovny `<stdlib.h>`:

> **`atoi()` (ASCII to Integer)** -- pro převod na celé číslo.

> **`atof()` (ASCII to Float)** -- pro převod na desetinné číslo.

Příklad převodu:

``` c
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc > 1) {
        int cislo = atoi(argv[1]);
        printf("Dvojnasobek zadaneho cisla je: %d\n", cislo * 2);
    }
    return 0;
}

```
