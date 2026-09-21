---
title: "PIP v CP/M"
date: 2026-08-24T23:14:52+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

**PIP** (zkratka pro **Peripheral Interchange Program**) je jedním z
nejdůležitějších příkazů v historickém operačním systému
**CP/M**.

Zjednodušeně řečeno je to dobový ekvivalent dnešního příkazu `copy` (ve
Windows) nebo `cp` (v Linuxu), ale uměl toho mnohem víc. Sloužil
primárně ke **kopírování souborů a přesouvání dat mezi různými fyzickými
i logickými zařízeními** (např. mezi disketami, tiskárnou, obrazovkou
nebo děrnou páskou).

# Zvláštní syntaxe (Cíl = Zdroj)

Na rozdíl od pozdějšího MS-DOSu nebo dnešních systémů, kde zadáváme
nejdřív to, **co** kopírujeme, a pak to, **kam** to kopírujeme (např.
`copy ODKUD KAM`), PIP používal opačnou logiku, která připomínala
matematickou rovnici:

**`CÍL = ZDROJ`**

# Běžné příklady použití v praxi

### Kopírování souboru na jiný disk: 
`PIP B:TEXT.TXT = A:TEXT.TXT`

(Zkopíruje soubor TEXT.TXT z disku A na disk B.)

### Tisk souboru (odeslání dat na zařízení):
`PIP LST: = A:DOPIS.TXT` \
(Vezme soubor a odešle ho přímo na fyzickou tiskárnu -- LST jako List device.)

### Spojování více souborů do jednoho:
`PIP KNIHA.TXT = KAPITOLA1.TXT, KAPITOLA2.TXT`\
(Vezme oba zdrojové soubory a plynule je spojí do jednoho nového
souboru.)

### Zobrazení textu na obrazovce:
`PIP CON: = READ.ME`\
(Pošle obsah souboru na konzoli -- CON, tedy na obrazovku.)

## 68k-MBC

Na CP/M-68k máme `PIP` na disketě `A:` tedy pak píšeme příkaz `A:PIP`\
Typický příklad -- na disketě `F:` máme `SKED` editor. Vyvoříme zdrojový
kód `POKUS.C`\
Na disketě `C:` máme céčkový kompilátor.\
`C:` se přepnu na disk `C:`\
`C>A:PIP POKUS.C=F:POKUS.C` zkopírujeme si soubor z diskety `F:` na
aktuální disketu (`C:`)\
a pak už jenom `SUBMIT C POKUS` pro kompilaci a pak `CLINK POKUS` pro
linkování a máme hotový `POKUS.68K`

# Zajímavosti z historie

-   Název ani samotný koncept příkazu PIP nevymyslel tvůrce CP/M Gary
    Kildall. Tento nástroj pochází už ze 60. let z velkých počítačů a
    operačních systémů společnosti **DEC** (Digital Equipment
    Corporation), jako byly TOPS-10 nebo OS/8. Kildall ho do CP/M
    převzal, protože tehdejší programátoři na něj byli zvyklí.

-   K příkazu bylo možné přidávat různé parametry do hranatých závorek.
    Například `[V]` znamenalo, že po zkopírování se má provést
    verifikace (kontrola), zda jsou data zapsaná správně.

-   Když později vznikl systém MS-DOS (který se z CP/M silně
    inspiroval), nahradil PIP příkazem `COPY` a otočil syntaxi na
    přirozenější ZDROJ -\> CÍL.

-   Ve zkratce: V éře 8bitových mikropočítačů byl PIP naprosto
    nezbytou utilitou, bez kterého uživatelé nedostali data z jedné
    diskety na druhou ani z počítače na papír.
