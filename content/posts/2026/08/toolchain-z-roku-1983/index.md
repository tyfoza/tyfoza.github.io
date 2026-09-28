---
title: "Toolchain z roku 1983"
date: 2026-08-21T23:05:32+02:00
summary: "Tradiční vývoj a kompilace přímo na fyzickém stroji 68k-MBC přináší
zásadní zdržení. Procesor M68000 na taktu 8 MHz musí pro každý průchod
překladače číst a zapisovat dočasné mezisoubory přes emulovanou SD kartu
a BIOS, což prodlužuje proces kompilace na několik minut."

cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

### aneb hostitelsky akcelerovaná nativní kompilace

# Co je `m68`?

Projekt **`m68`** (jehož autorem je David Lyttle) je emulátor pro
spouštění binárních souborů pro Motorolu 68000. Nás zajímají soubory
.68K pro operační systém CP/M-68K. Díky `m68` mohou binární soubory .68K
běžet přímo na moderních systémech linux\|windows\|macOC. Nám poslouží k
hostování a běhu originální distribuce historického překladače **Alcyon
C** z roku 1983.

kompilace `m68` na linuxu:

``` bash
git clone https://github.com/davidly/m68
cd m68
chmod +x *.sh
./mr.sh
./m.sh

```

kompilaci na Windows jsem nezvládl bez MSYS2 (`https://www.msys2.org/`)
a tam stačí v příkazovém řádku stáhnout kompilátor `gcc`, `m68` z
githubu a provést kompilaci se statickým slinkování se všemi
knihovnami - aby nám výsledný `m68.exe` fungoval nezávisle kdekoli. A
pak už si jenom celou `m68` složky vyjeme ze struktury MSYS2. Příkazem
`explorer .` otevřeme průzkumníka v aktuální složce.

kompilace `m68` na windows:

``` bash
pacman -S git
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
git clone https://github.com/davidly/m68
cd m68
g++ -O3 -DM68 -D_MSC_VER -DNDEBUG -std=c++17 -I. m68.cxx m68000.cxx -luser32 -static -o m68.exe
explorer .

```

# Jak `m68` funguje uvnitř?

Historické nástroje z distribuce (jako je preprocesor `CP68.68K` nebo
kompilátor `C068.68K`) jsou nativní CP/M-68K binárky. Projekt `m68`
funguje tak, že v reálném čase zachytává systémová volání (konkrétně
CP/M-68K BDOS trapy -- Trap 2 a Trap 3) a mapuje je přímo na standardní
POSIX volání operačního systému Linux.

Díky tomu si historické nástroje "myslí", že běží pod operačním systémem
CP/M-68K na procesoru Motorola, přestože ve skutečnosti využívají plnou
propustnost a plný výpočetní výkon moderního hostitelského počítače.

# Řádové zrychlení vývoje

Tradiční vývoj a kompilace přímo na fyzickém stroji 68k-MBC přináší
zásadní zdržení. Procesor M68000 na taktu 8 MHz musí pro každý průchod
překladače číst a zapisovat dočasné mezisoubory přes emulovanou SD kartu
a BIOS, což prodlužuje proces kompilace na několik minut.

## Toolchain z roku 1983 na moderním PC

Ve složce `cpm/` máme k dispozici originální nástroje (`CP68`, `C068`,
`C168`, `AS68`, `LO68`) společně s historickou knihovnou `libc.a`. Místo
spouštění na reálném hardwaru je voláme na Linuxu z automatizačního bash
skriptu.

Typická kompilace `m68/cpm/MC.C`, ke kterému máme připojit externí
assemblerovské rutiny proběhne takto\
v linuxu ve složce `mc68/cpm` spustíme `./build.sh MC KEY.O BDOS.O`\
ve windows ve složce `m68\cpm` spustíme `build MC KEY.O BDOS.O`\
Všimněte si, že `MC` jde do build bez přípony!\
Výpis `build.sh` a `build.bat` je připojen na konci tohoto souboru.

Přímo v CP/M by proběhla kompilace souboru `C:MC.C`\
`C>SUBMIT C MC`\
`C>CLINK MC KEY BDOS`\
V případě úspěchu bude výsledkem soubor `MC.68K`

## Ošetření historických specifik

Skript se stará o to, abychom překladači předávali parametry přesně v
tom formátu, jaký z historických důvodů očekává. Překladač vyžaduje
například syntaxi logických disků CP/M (např. parametr `-i 0:`,
odkazující na aktuální disketovou jednotku) a striktně vyžaduje práci se
soubory zapsanými velkými písmeny.

## Rychlá vývojová smyčka

Pokud při psaní v Alcyon C narazíme na chybu (jako je typické překročení
tabulky symbolů nebo příliš hluboké vnoření výrazů), Linux nám chybu
vypíše do terminálu okamžitě, bez zbytečného čekání na pád kompilátoru
na fyzické Motorole. Emulátor navíc dokonce umožňuje i testovací
spuštění výsledných CP/M-68K programů přímo v Linuxovém terminálu. Pro
běžné testy je to použitelné, pro testování dynamické odezvy
terminálových her jsem neuspěl. Používám specifická CP/M volání, které v
"emulátoru" nefungují.

## Odeslání 100% kompatibilní binárky

Kód kompiloval identický Alcyon C kompilátor z CP/M-68K, vygenerovaný
soubor `.68K` je naprosto binárně shodný. Odpadají odchylky v typech
proměnných (např. striktně 16bitový `int`). Výslednou rychlou binárku
stačí po slinkování jen nahrát na SD kartu nebo poslat na 68k-MBC přes
sériovou linku a rovnou bez úprav spustit.

# Opravdu! Výsledný .68K se shoduje a je spustitelný

Ať zkompilujeme obří kód za vteřinu na Linuxu nebo za 10 minut přímo na
68K-MBC v CP/M, tak výsledný binární soubor je shodný. Jak pravil pan
Krysa ve filmu Jádro: "To je moje kung-fu a je docela silné."

# Skripty v podsložce CP/M-68K (`m68/cpm/`)

V podsložce `cpm/` se nachází historická distribuce nástrojů operačního
systému CP/M-68K, a to primárně K&R kompilátoru jazyka C od společnosti
Digital Research (Alcyon C).

> `m.bat` / `m.sh`: Spouští dávkový překlad ukázkových programů v
jazyce C. Aby celý proces fungoval na moderním PC, jsou originální
CP/M-68K nástroje (jako je preprocesor, parser, generátor kódu,
assembler a linker) v tomto skriptu spouštěny skrze nadřazený emulátor
m68.

> `ma.bat` / `ma.sh`: Podobně jako v předchozím případě, tyto skripty
kompilují zdrojové kódy, avšak jsou určeny pro soubory v čistém jazyce
symbolických adres (assembler s koncovkou `.s`). K výslednému binárnímu
souboru je přilinkována běhová knihovna (C runtime).

> `maa.bat` / `maa.sh`: Zkompilují kód v assembleru a následně
vygenerují binární soubor s minimální strukturou, do kterého není
přilinkována standardní běhová C knihovna.

> `mf.bat` / `mf.sh`: Speciální sestavovací skripty určené výhradně
pro překlad C aplikací využívajících operace s pohyblivou desetinnou
čárkou (floating-point).

> `a.sub`, `c.sub`, `ce.sub`, `clink.sub`, atd.: Nejedná se o
linuxové ani Windows dávkové soubory, ale o originální "submit"
(dávkové) skripty operačního systému CP/M-68. Obsahují sekvence příkazů
pro překladač Alcyon C a lze je spouštět přímo z příkazové řádky
CP/M-68K na původním hardwaru (jako je např. 68k-MBC). Většinu jejich
logiky pro nás emulují právě námi napsané shellové skripty (jako je
`build.sh`), abychom mohli provádět pohodlný cross-compiling.

# Je to ještě vůbec křížová kompilace?

Při pohledu na náš vývojový řetězec, kdy na moderním počítači s Linuxem
píšeme kód, spouštíme `build.sh` a výsledkem je binárka pro CP/M-68K, se
přirozeně nabízí myšlenka: **Tohle je přece typická křížová kompilace
(cross-compilation).**

Pokud se ale na celý proces podíváme optikou puristického retro
programátora, zjistíme, že celá situace je mnohem zajímavější a
technicky pikantnější. My totiž klasickou křížovou kompilaci
**neprovádíme**.

## Iluze moderního Toolchainu

Když se dnes řekne křížová kompilace, vývojář si typicky představí
moderní nástroje jako GCC nebo Clang (např. `m68k-elf-gcc`). V takovém
případě by kompilátor byl moderní x86_64 linuxovou aplikací. Tento
moderní program by načetl náš C kód, provedl na něm pokročilou statickou
analýzu podle moderních standardů (C99, C11), aplikoval by agresivní
optimalizační stromy a nakonec by -- jako svůj datový výstup ---
"vyplivl" strojový kód pro procesor Motorola 68000. Ten ale běží přímo
na železe, takže pro spuštění v CP/M se musí přilepit spouštěč,
výsledkem je .obj soubor, který se dá převést do .68K spustitelného v
CP/M. Otázkou je přenositelnost; nemáme jak zkontrolovat, že to poběží
na každém CP/M-68K.

Při použití moderního GCC bychom ale ztratili to podstatné: **dobovou
autenticitu a surovost**. Mohli bychom používat moderní datové typy,
libovolně dlouhé názvy proměnných, složité zanořené výpočty a moderní
standardní knihovny. Vývoj by byl snadný, ale kód by ztratil svou
historickou "duši" a výsledná binárka by pro běh pod CP/M-68K
pravděpodobně vyžadovala složitě upravený startovací kód a nestandardní
knihovny.

## Emulovaná nativní kompilace

To, co provádíme s projektem **m68** a překladačem **Alcyon C**, je
zcela jiná disciplína. My na Linuxu nespouštíme linuxový kompilátor. My
spouštíme originální, historické, 16bitové CP/M-68K binární soubory
(jako je `CP68.68K` nebo `AS68.68K`), které byly součástí původní
distribuce operačního systému.

Ač používáme emulátor procesoru 68k, tak z hlediska kompilátoru probíhá
čistokrevná **nativní kompilace**.

## Nejlepší z obou světů

Tento přístup, který bychom mohli nazvat **hostitelsky akcelerovanou
nativní kompilací**, je pro retro nadšence rájem. Proč?

1.  **Absolutní hardwarová brzda neexistuje:** Nemusíme čekat 10 minut,
    než 8MHz procesor zchroustá pětifázový překlad. Fyzikální limit SD
    karty a historického procesoru jsme obelstili surovým výpočetním
    výkonem moderního PC. Překlad proběhne za zlomek sekundy.

2.  **Stoprocentní dobová restrikce:** Přestože kompilujeme bleskově,
    kompilátor nám nic nedaruje. Stále musíme psát tvrdý K&R C kód.
    Stále jsme omezováni 16bitovým typem `int`. Stále se musíme vyhýbat
    matematice překračující limity interních tabulek překladače a jména
    našich funkcí se stále rozlišují pouze na prvních 8 znacích. Kód,
    který takto vzniká, je 100% autentický.

3.  **Binární čistota:** Výsledný soubor `.68K` je na bajt shodný s tím,
    co by z historického překladače vypadlo na skutečném hardwaru po
    dlouhých minutách "hrabání" na disketu. Nepotřebujeme žádné moderní
    převodníky formátů ani speciální běhové knihovny.

Místo abychom minulost přepisovali moderními nástroji, vytvořili jsme
pro ni virtuální inkubátor, ve kterém může běžet tisíckrát rychleji.
Není to křížová kompilace v moderním slova smyslu. Je to záchrana
historického softwaru před fyzikálním stárnutím samotného hardwaru.

### Linux verze `m68\cpm\build.sh` 

``` bash
#!/bin/bash
#!/bin/bash
set -e

M68="../m68"

# Vezme první argument, odstraní případnou příponu .C a převede na velká písmena
BASE=$(echo "$1" | sed -E 's/\.[cC]$//' | tr 'a-z' 'A-Z')
shift
# Všechny další argumenty se použijí jako dodatečné objektové soubory (např. KEY.O)
EXTRA_OBJS="$@"

echo "=== [1/5] Preprocesing (CP68) ==="
$M68 CP68.68K -I 0: "${BASE}.C" "${BASE}.I"

echo "=== [2/5] Parser (C068) ==="
$M68 C068.68K "${BASE}.I" "${BASE}.1" "${BASE}.2" "${BASE}.3" -F

echo "=== [3/5] Code Generator (C168) ==="
$M68 C168.68K "${BASE}.1" "${BASE}.2" "${BASE}.S"

echo "=== [4/5] Assembler (AS68) ==="
$M68 AS68.68K -L -U -S 0: "${BASE}.S"

echo "=== [5/5] Linker (LO68) ==="
# Připojíme S.O, hlavní program, dodatečné objekty a knihovnu CLIB
$M68 LO68.68K -R -U_NOFLOAT -O "${BASE}.68K" S.O "${BASE}.O" $EXTRA_OBJS CLIB

# Úklid mezisouborů
rm -f "${BASE}.I" "${BASE}.1" "${BASE}.2" "${BASE}.3" "${BASE}.S" "${BASE}.O"

echo "=== HOTOVO: Vytvořen soubor ${BASE}.68K ==="
ls -lh "${BASE}.68K"


```

### Windows verze `m68\cpm\build.bat`

``` bat
@echo off
setlocal enabledelayedexpansion

set M68=..\m68.exe

:: Vezme první argument a získá z něj název bez přípony (.C/.c)
set BASE=%~n1

:: Posunutí argumentů
shift

:: Načtení všech dalších argumentů (např. KEY.O) do proměnné EXTRA_OBJS
set EXTRA_OBJS=
:gather_args
if "%~1"=="" goto build_start
set EXTRA_OBJS=!EXTRA_OBJS! %1
shift
goto gather_args

:build_start
echo === [1/5] Preprocesing (CP68) ===
%M68% CP68.68K -I 0: "%BASE%.C" "%BASE%.I"
if %errorlevel% neq 0 goto error

echo === [2/5] Parser (C068) ===
%M68% C068.68K "%BASE%.I" "%BASE%.1" "%BASE%.2" "%BASE%.3" -F
if %errorlevel% neq 0 goto error

echo === [3/5] Code Generator (C168) ===
%M68% C168.68K "%BASE%.1" "%BASE%.2" "%BASE%.S"
if %errorlevel% neq 0 goto error

echo === [4/5] Assembler (AS68) ===
%M68% AS68.68K -L -U -S 0: "%BASE%.S"
if %errorlevel% neq 0 goto error

echo === [5/5] Linker (LO68) ===
%M68% LO68.68K -R -U_NOFLOAT -O "%BASE%.68K" S.O "%BASE%.O" !EXTRA_OBJS! CLIB
if %errorlevel% neq 0 goto error

:: Úklid mezisouborů
del /Q "%BASE%.I" "%BASE%.1" "%BASE%.2" "%BASE%.3" "%BASE%.S" "%BASE%.O" 2>nul

echo === HOTOVO: Vytvoren soubor %BASE%.68K ===
dir "%BASE%.68K" | findstr /i "%BASE%.68K"
goto :EOF

:error
echo === CHYBA: Kompilace selhala! ===
exit /b 1
```
