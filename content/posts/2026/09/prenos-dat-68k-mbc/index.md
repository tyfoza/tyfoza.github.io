---
title: "Přenos dat mezi PC a 68k-MBC"
date: 2026-08-22T16:36:35+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
math: true
---

Přenos dat (ať už textových zdrojových kódů nebo zkompilovaných
binárních programů) z moderního počítače do retro počítače 68k-MBC
s operačním systémem CP/M-68K představuje technickou výzvu.

Terminálové emulátory a sériové linky jsou historicky navrženy primárně
pro textová data, obvykle reprezentovaná 7bitovými nebo 8bitovými ASCII
znaky. Pokud se přes takovou linku pokusíme odeslat surový binární
soubor, nedopadne to dobře. Speciální řídící znaky obsažené v binárních
datech vyvolávají nechtěné reakce operačního systému. Například byte
`0x03` interpretuje systém jako přerušení (Ctrl+C), `0x1A` jako konec
souboru (EOF) a `0x04` jako konec vysílání (EOT). Výsledkem je poškození
přenášeného souboru nebo úplný pád přenosu.

Vkládání prostého textu pomocí schránky (Ctrl-V v emulátoru) je zase
velmi pomalé, vyžaduje umělé vkládání pauz po každém znaku i řádku a
neřeší problém s nekompatibilními znaky, jako je UTF-8 diakritika.

Tradičním řešením pro bezpečný binární přenos bývaly protokoly s
kontrolou chyb, jako je XMODEM nebo Kermit.

Postavíme si svůj kompletní systém `68k-ser` (skládající se z Python
skriptu `68k-ser.py` na PC a programu `68KSER.C` na CP/M).

{{< youtube zlX931DcYSI >}}

# Duální sériový port

Základem rychlé a plynulé práce je využití obou sériových portů, kterými
deska 68k-MBC (ve verzi FULL) disponuje:

-   **Port J4 (AUX):** Obsahuje integrovaný sériový budič MAX323
    (RS-232) a v moderním OS se typicky hlásí jako `/dev/ttyUSB1`.
    Slouží pro připojení fyzického terminálu nebo emulátoru (např.
    `tio`) a je vyhrazen pro interaktivní zadávání příkazů.

-   **Port J2 (SER1):** Port v TTL logice, hlásící se typicky jako
    `/dev/ttyUSB0`. Tento port slouží výhradně jako vyhrazený datový
    kanál pro běh přenosových skriptů.

Výhoda tohoto "duálního portu" spočívá v tom, že při přenosu souborů
není vůbec nutné zavírat okno terminálu. Oba procesy běží po fyzicky
oddělených linkách (přestože směřují do stejného procesoru), takže
nedochází ke kolizím a použití je pohodlné.

# Softwarového řešení

Zpracování dat při vysílání i příjmu stojí má tři části:

## 1. Komprese dat (LZ4)

Protože maximální rychlost sériové linky 68k-MBC je fyzicky omezena
(typicky na 115200 baudů), je výhodné objem přenášených dat zmenšit. 
Python skript i CP/M program umí využít rychlé kompresní jádro LZ4. 
Surová data jsou na vysílací straně zkomprimována
pomocí LZ4 s nastavením vysoké komprese, čímž se radikálně snižuje čas
potřebný k jejich fyzickému propasírování sériovým kabelem.

LZ4 funguje pouze při posílání souborů z PC do 68k-MBC, protože
komprese je náročná (PC) a dekomprese je rychlá a nenáročná (Motorola 68k).

## 2. Textové kódování (Base64)

Aby komprimovaná (čistě binární) data prošla sériovým portem bez
interpretace řídících znaků, jsou následně překódována algoritmem
Base64.

-   Base64 bere vždy 3 byty binárních dat a rozloží je do 4 znaků
    bezpečné abecedy.

-   Tato abeceda obsahuje pouze znaky `A-Z`, `a-z`, `0-9`, `+` a `/`,
    doplněné o `=` pro výplň na konci.

-   Tyto bezpečné ASCII znaky projdou bez úhony libovolným prostředím.

-   Stream Base64 dat je zabalen do jasně rozpoznatelných textových
    značek `===BEGIN_FILE===` a `===END_FILE:`, díky kterým přijímací
    strana pozná, kdy přenos začal a kdy bezpečně skončil.

## 3. Kontrola integrity (DJB2 Hash)

Pro garanci bezchybnatosti přenosu, se před začátkem přenosu spočítá
matematický otisk (Hash).

-   Je použit algoritmus **DJB2** (od Daniela J. Bernsteina) s magickou
    inicializační hodnotou 5381.

-   Zvolený algoritmus je nekryptografický, ale extrémně rychlý, což je
    pro historický procesor Motorola 68000 klíčové.

-   Jeho hlavní síla tkví v tom, že výpočet nevyužívá pomalé násobení,
    ale nahrazuje ho efektivním bitovým posunem doleva o 5 pozic
    (`<< 5`) a obyčejným sčítáním.

-   Hash se počítá na straně odesílatele a odešle se na úplném konci
    streamu. Přijímací strana si během zápisu souboru spočítá Hash
    vlastní a obě hodnoty následně porovná.

# Automatická správa textového formátu

Kromě binárních dat systém inteligentně přistupuje i k textovým
zdrojovým kódům, u kterých by historické CP/M kompilátory hlásily chyby.

-   Skript na straně PC automaticky provádí takzvanou Unicode NFKD
    normalizaci.

-   Všechny nepodporované znaky s českou diakritikou rozloží, odstraní
    háčky a čárky, a zahodí neslučitelné UTF-8 symboly, čímž vznikne
    historicky korektní a čisté ASCII.

-   Zároveň se stará o automatickou konverzi moderních linuxových konců
    řádků (`\n`) na formát nezbytný pro běh CP/M (`\r\n`).

-   Pokud je text odesílán s využitím dekompresního programu na straně
    CP/M (`RXTXT`), doplní dekodér na samotný konec rozbaleného souboru
    znak `0x1A` (Ctrl+Z), který CP/M vyžaduje jako standardní označení
    konce textového souboru.

# Proč a jak počítáme Hash

Při přenosu dat přes sériovou linku hrozí riziko ztráty nebo poškození
informací vlivem rušení či přetečení bufferu. Zatímco u obyčejného textu
ztráta jednoho písmene obvykle nevadí, u zkompilovaného binárního
programu vede změna jediného bitu k pádu systému (např. chyba
`Illegal Instruction`). Proto je naprosto nezbytné mít mechanismus,
který stoprocentně zaručí, že přenesený soubor je identický s originálem
na PC.

K tomuto účelu systém `68KSER` využívá hašovací funkci. Hash je
matematický algoritmus, který vezme vstupní data libovolné délky (např.
200kB soubor) a převede je na výstup pevné, předem dané délky --
takzvaný otisk (fingerprint).

Aby byla hashovací funkce v našem projektu použitelná, musí splňovat tři
klíčové vlastnosti:

-   **Determinismus:** Zcela stejný vstupní soubor musí vždy vygenerovat
    naprosto stejný hash.

-   **Lavinový efekt (Avalanche effect):** Změna i jediného bitu ve
    zdrojových datech musí změnit výsledný hash k nepoznání.

-   **Rychlost:** Algoritmus se spouští na historickém hardwaru, výpočet
    tedy musí být dostatečně rychlý a nesmí příliš zdržovat samotný
    zápis na disk.

Spočítáním hashe na odesílajícím PC a následným spočítáním hashe z
přijatých dat na CP/M získáme dvě hodnoty. Pokud se tyto hodnoty (v
podobě osmimístného hexadecimálního řetězce) shodují, máme jistotu, že
se při přenosu nezměnil ani jediný byte.

## Algoritmus DJB2

Protože kryptografické funkce (jako SHA-256) jsou pro procesor Motorola
68008 zbytečně pomalé a složité, využívá systém nekryptografický
hashovací algoritmus **DJB2**. Jeho autorem je Daniel J. Bernstein a
tento algoritmus byl navržen speciálně pro maximální rychlost s
minimálním množstvím kolizí.

Podrobněji: [wiki](https://en.wikipedia.org/wiki/Universal_hashing#Hashing_strings) 
a [přehled hash funkcí](http://www.cse.yorku.ca/~oz/hash.html)

Vysoká rychlost algoritmu spočívá v tom, že výpočet nevyžaduje na
procesoru žádné násobení či dělení, ale využívá pouze obyčejné sčítání a
rychlý bitový posun.

Výpočet probíhá iterativně (byte po bytu) následovně:

1.  **Inicializace:** Hodnota hashe se na samém začátku nastaví na
    magické číslo, které u DJB2 historicky činí $5381$. $H_{0} = 5381$

2.  **Iterace:** Pro každý byte vstupního souboru ($c_{i}$) se nová
    hodnota hashe spočítá tak, že se dosavadní hash vynásobí číslem $33$
    a následně se k němu přičte hodnota aktuálního bytu.
    $H_{i} = \left( H_{i - 1} \times 33 \right) + c_{i}$

3.  **Hardwarová optimalizace (Bitový posun):** Násobení je na
    historických procesorech výpočetně poměrně drahá a pomalá operace.
    Vynásobení číslem 33 lze ale matematicky rozložit na vynásobení
    číslem 32 a přičtení původní hodnoty
    ($x \times 33 = (x \times 32) + x$). Protože číslo 32 je mocninou
    dvojky ($2^{5}$), lze toto násobení nahradit na úrovni procesoru
    velmi rychlým bitovým posunem doleva o 5 bitů (`<< 5`). Vzorec pro
    programátory tak vypadá takto:
    $H_{i} = \left( \left( H_{i - 1}{< <}5 \right) + H_{i - 1} \right) + c_{i}$

4.  **Přetečení (Modulo):** Výsledek se ukládá do 32bitového registru.
    Vlivem neustálého posouvání a sčítání proměnná velmi rychle překročí
    svou maximální 32bitovou kapacitu. Algoritmus toto přetečení očekává
    a využívá ho, což matematicky odpovídá operaci modulo $2^{32}$.

## Úskalí implementace: C vs Python

Přestože je algoritmus jednoduchý, jeho naprogramování v jazyce C pro
procesor m68k a na PC v moderním Pythonu vyžaduje odlišný přístup, aby
výsledky byly na obou platformách identické.

### Přirozené přetečení v jazyce C (CP/M-68K)

Na architektuře Motorola 68000 s překladačem Alcyon C je implementace
velmi přímá. Proměnná typu `long` má velikost přesně 32 bitů (4 byty).
Procesor zpracuje bitový posun doleva nativní instrukcí `LSL.L` (Logical
Shift Left) a sčítání instrukcí `ADD.L`.

``` c
/* Jádro výpočtu hashe v 68KSER.C */
long my_hash = 5381L;
for (h_idx = 0; h_idx < padded_len; h_idx++) {
    /* Vlastni posun a soucet. Pri prekroceni 32 bitu
       procesor jednoduse zahodi horni bity. */
    my_hash = ((my_hash << 5) + my_hash) + c_val;
}
```

Když hodnota `my_hash `přesáhne 32 bitů, procesor horní "přebytečné"
bity přirozeně odřízne (hardwarový overflow), což přesně naplňuje
matematické požadavky algoritmu DJB2. Výsledná hodnota je poté
formátována do 8místného HEX řetězce (např. to_hex(my_hash,
my_hash_str);) pro odeslání do PC nebo kontrolu.

### Umělé přetečení v Pythonu (PC)

Na rozdíl od starého céčka nemá moderní Python 3 pevně danou velikost
celých čísel (int). Celočíselné proměnné se zde dynamicky natahují podle
potřeby a mohou mít teoreticky neomezenou velikost. Pokud bychom v
Pythonu napsali iteraci algoritmu bez úprav, číslo by se po několika
cyklech nafouklo do obřích rozměrů, nespadlo by zpět přes nulu a jeho
finální hodnota by absolutně neodpovídala tomu, co spočítal retro
procesor. Python musí 32bitové chování starého hardwaru uměle
nasimulovat.

``` python
#Jádro výpočtu hashe v 68k-ser.py
hash_val = 5381
for b in padded_payload:
    # Ochranná maska & 0xFFFFFFFF simuluje 32bit hardware
    hash_val = ((hash_val << 5) + hash_val + b) & 0xFFFFFFFF
# Převod na 8místný velký HEX řetězec
expected_hash_hex = f"{hash_val:08X}"
```

Aplikováním masky `& 0xFFFFFFFF` (což je bitové AND s hodnotou složenou
z 32 jedniček) na každý krok cyklu se zachová pouze spodních 32 bitů a
zbytek výpočtu nad touto hranicí se natvrdo odřízne. Díky této korekci
vygenerují obě naprosto odlišné platformy na chlup stejný kontrolní
součet, který se do odesílaného Base64 streamu zabalí do značky konce
souboru (např. `===END_FILE:A1B2C3D4===`).

# Kódování dat pro sériový přenos

Základním problémem při komunikaci s historickým systémem CP/M přes
sériovou linku je skutečnost, že tyto linky a terminálové emulátory byly
primárně navrženy pro přenos textových dat (konkrétně 7bitových nebo
8bitových ASCII znaků). Přenášený binární soubor (ať už zkompilovaný
program, nebo LZ4 komprimovaný archiv) obsahuje data v celém rozsahu
hodnot 0 až 255. Běžně se v něm tak vyskytují byty, které mají pro
terminál nebo operační systém CP/M speciální řídící význam.

Například byte `0x03` je interpretován jako přerušení (Ctrl+C), byte
`0x1A` označuje konec souboru (EOF) a `0x04` konec vysílání (EOT). Pokud
by operační systém během příjmu binárního streamu na takový znak
narazil, vyvolal by nechtěnou reakci, což by vedlo k poškození
přijímaných dat nebo k úplnému zhroucení přenosu. Ošetření této situace
vyžaduje převod binárních dat na bezpečný, tisknutelný text.

## Od UUencode k Base64

Historicky existovalo více přístupů, jak bezpečně enkódovat binární
soubory do textu (Binary-to-Text). Starším zástupcem je kódování
**UUencode** z roku 1980. Tento algoritmus rozděloval 3 byty do 4
šestibitových bloků a přičtením hodnoty 32 (znak mezera) je posouval do
tisknutelné oblasti ASCII tabulky. Zásadním problémem UUencode ovšem
bylo používání znaku mezery (ASCII 32) nebo zpětného apostrofu. Tyto
specifické znaky byly na některých ne-unixových terminálech, sériových
linkách či e-mailových branách ořezávány nebo interpretovány chybně, což
nenávratně poškozovalo přenášená data.

Systém `68KSER` proto pro vrstvu sériového přenosu využívá modernější a
spolehlivější standard **Base64**. Tento algoritmus odstraňuje vady
UUencode tím, že používá výhradně striktní a stoprocentně bezpečnou
64znakovou abecedu, která bez úhony projde libovolnou linkou či
copy-paste schránkou. Tato abeceda obsahuje:

-   Velká a malá písmena latinky: `A-Z`, `a-z`

-   Číslice: `0-9`

-   Zvláštní znaky: `+` a `/`

Pokud navíc původní délka binárních dat není přesně dělitelná třemi,
algoritmus doplní na úplný konec přenosu znak rovnítka (`=`) jako jasnou
výplň (padding).

## Matematický princip transformace

Základní myšlenka algoritmu Base64 spočívá v mapování 24 bitů dat na 4
ASCII znaky. Probíhá to následovně:

1.  Algoritmus vezme z originálního souboru 3 standardní 8bitové byty.
    Ty mají dohromady 24 bitů ($3 \times 8 = 24$).

2.  Tento 24bitový blok je následně "rozřezán" na 4 menší části, z nichž
    každá má délku přesně 6 bitů ($4 \times 6 = 24$).

3.  Šestibitové číslo může nabývat hodnot pouze od 0 do 63, což
    matematicky perfektně lícuje s vybranou 64znakovou bezpečnou
    abecedou.

## Implementace vysílače na straně PC (Python)

Skript `68k-ser.py` na straně moderního PC nejprve připraví binární data
(případně data zkomprimuje algoritmem LZ4) a získá řetězec znaků v
Base64.

Velmi důležitým konstrukčním prvkem vysílače je následné formátování
tohoto streamu. Dlouhé nepřerušené řetězce textu by při vysokých
rychlostech mohly na starém počítači způsobit přetečení vstupního
přijímacího bufferu terminálu. Python skript proto výsledný Base64
řetězec rozdělí na bezpečné kratší řádky o délce 64 znaků, přičemž každý
řádek ukončí standardním odřádkováním `\r\n` (CR+LF). Celý tento blok
dat je navíc jasně ohraničen značkami `===BEGIN_FILE===` na začátku a
`===END_FILE:xxx===` na konci, takže přijímač na straně CP/M přesně ví,
které znaky má ignorovat a kdy má zahájit parsování dat.

## Dekódování dat uvnitř CP/M-68K (C Program)

Nejcitlivější operací je převod kódovaných znaků zpět na binární
strukturu přímo na čipu Motorola 68000. Program `68KSER.C` využívá
stavový automat (čte linku znak po znaku), obdržené ASCII znaky převede
přes funkci na hodnoty 0-63 a postupně tyto 6bitové dílky vrací zpět do
původních 8bitových bytů.

Probíhá to ve speciální pracovní proměnné `accum` (akumulátor) za pomoci
efektivních bitových operací:

1.  **Posun a uložení:** Každý načtený 6bitový zlomek (`val`) se vloží
    do akumulátoru operací `accum = (accum << 6) | val;`. Operátor
    bitového posunu (`<< 6`) vytvoří napravo šest prázdných míst (nul),
    které operátor bitového součtu (`|`) elegantně přepíše nově příchozí
    hodnotou z Base64.

2.  **Počítání bitů:** Proměnná `bits` hlídá, kolik bitů je v
    akumulátoru aktuálně k dispozici. Po načtení znaku se k ní přičte
    číslo 6 (`bits += 6;`).

3.  **Odkrojení bytu:** Jakmile akumulátor nasbírá dostatek bitů pro
    sestavení standardního bytu (`if (bits >= 8)`), dojde k jeho
    odříznutí a zápisu. Program z počítadla bitů odečte osmičku
    (`bits -= 8;`) a aplikuje posun doprava `(accum >> bits)`.

4.  **Čistý řez:** K odseknutí případných přebytečných bitů vlevo se
    používá ochranná maska (`& 0xFF`). Ta funguje jako gilotina a
    zaručí, že do přijímacího paměťového bufferu se pošle vždy jen a
    pouze přesný původní 8bitový bajt bez jakýchkoliv nechtěných zbytků.

Jakmile dekódovací smyčka z přijímané linky detekuje znak rovnítka
(`=`), proces rozbalování dat se elegantně ukončí, protože program
bezpečně pozná, že narazil na konec kódovaného bloku souboru.

# Komprese dat (LZ4): Zrychlení přenosu sériovou linkou

Sériová komunikace na historickém hardwaru je ze své podstaty pomalá.
Přenosová rychlost desky 68k-MBC je při tomto zapojení omezena na 115200
baudů. U přenosu větších zkompilovaných programů (například v řádu
stovek kilobajtů) by hrubý textový Base64 stream trval nepříjemně
dlouho.

Proto systém `68KSER` vkládá do řetězce zpracování dat další vrstvu --
bezeztrátovou kompresi. Komprese radikálně zmenšuje objem binárních dat
ještě předtím, než se vůbec zakódují do Base64 formátu pro odeslání.

## Proč právě algoritmus LZ4?

Při vývoji pro retro platformu bylo nutné vybrat kompresní algoritmus,
který je silně asymetrický. To znamená, že:

1.  **Komprese** může být náročná, protože probíhá na moderním a
    výkonném PC. Skript `68k-ser.py` proto volá LZ4 kompresi v režimu
    maximálního stlačení (`mode='high_compression'`). Zde získáme
    maximální úsporu dat. Skript ihned vypočítá kompresní poměr a
    efektivitu, kterou zobrazí uživateli.

2.  **Dekomprese** musí být naopak co nejlehčí, protože běží na
    16bitovém procesoru Motorola 68000 s velmi omezeným výkonem a v
    prostředí CP/M-68K.

Algoritmus LZ4 je pro tento scénář naprosto ideální. Jeho dekompresor
nepracuje se složitými matematickými transformacemi ani nestaví náročné
Huffmanovy stromy v paměti. Celý proces dekódování spočívá čistě v
kopírování bloků paměti -- operaci, ve které procesor m68k exceluje.

## Architektura paměti v CP/M a LZ4

Proces rozbalování vyžaduje dostatek paměti pro uložení celého proudu
dat naráz. Program `68KSER.C` garantuje přítomnost velkých datových
struktur přímo v paměti RAM. Využívá staticky alokované paměťové bloky o
velikosti 320 kB pro přijatá (zkomprimovaná) data (`in_buf`) a 320 kB
pro rozbalený výsledek (`out_buf`). Tím, že se vyhne postupnému zápisu
po malých blocích na pomalou SD kartu v průběhu rozbalování, dosahuje
nejvyšší možné rychlosti dekomprese. Až po úplném rozbalení se data v
kuse zapíší z bufferu fyzicky na disk.

## Princip fungování LZ4: Token, Literály a Shody

Komprimovaná data ve formátu LZ4 se skládají ze sekvencí. Před samotnými
daty předá PC skript do CP/M první 4 byty, ve kterých je (ve formátu
little-endian) zakódována originální, nekomprimovaná velikost souboru
(`orig_sz`). Díky tomu 68k-MBC ví, kolik paměti má přesně zpracovat, a
může zkontrolovat, zda soubor nepřesahuje povolených 320 kB.

Každá kompresní sekvence začíná jedním řídícím bajtem, kterému říkáme
**Token**. Dekompresní smyčka v `68KSER.C` s tímto tokenem provádí dvě
základní operace, které se neustále střídají: **Kopírování literálů**
(nových dat) a **Kopírování shod** (opakujících se dat).

### 1. Token (Rozdělení instrukcí)

Jeden 8bitový bajt tokenu je softwarově rozdělen na dvě poloviny (4 bity
a 4 bity):

-   Horní 4 bity určují **délku literálů** (počet bajtů, které se
    nezkomprimovaly a je nutné je prostě přepsat). Získají se bitovým
    posunem `(token >> 4) & 0x0F`.

-   Spodní 4 bity určují **délku shody** (počet bajtů, které se budou
    kopírovat z historie). Získají se maskou `token & 0x0F`.

### 2. Kopírování literálů (Surová data)

Pokud jsou nějaká nová, neopakující se data, algoritmus je vezme z
komprimovaného bufferu a opíše je jedna k jedné do výstupu.

-   **Problém délky:** Čtyři bity dokážou vyjádřit číslo jen od 0 do 15.
    Co když je nekomprimovaných dat více než 15 bytů v kuse?

-   **Řešení:** Pokud je hodnota z tokenu rovna maximu (15), program
    začne číst následující byty ze vstupu. Dokud čte bajty s hodnotou
    255, přičítá je k celkové délce. Jakmile načte bajt s hodnotou menší
    než 255, přičte ho jako poslední a je hotovo.

-   **Kopírování:** Následně jednoduchý cyklus `for` zkopíruje přesný
    počet zjištěných bajtů ze vstupního (`in_buf`) do výstupního bufferu
    (`out_buf`).

### 3. Zpracování shody (Historie)

Zde se děje samotná "komprese". Pokud algoritmus narazí na data, která
se v souboru již objevila dříve, neukládá je znovu, ale vloží instrukci
ve smyslu **"Běž se podívat o X bytů zpět a opiš odtamtud Y bytů"**.

-   **Offset (Vzdálenost):** Ihned za zkopírovanými literály si
    dekompresor přečte 2 byty, které tvoří 16bitovou hodnotu (tzv.
    `offset`). Tato hodnota udává, o kolik kroků zpět v již
    dekomprimovaném výstupním bufferu se má procesor podívat.

-   **Výpočet délky shody:** Ke zjištění, kolik bytů má program z
    historie opsat, se použije druhá (spodní) polovina původního tokenu.
    Pokud je číslo rovno 15, opět se čtou další byty (sčítají se
    dvěstěpadesátpětky), dokud se nezíská celá délka. Na závěr se k
    získané délce automaticky přičte hodnota 4 (`mat_len += 4L;`),
    protože kompresor LZ4 by nikdy nekomprimoval řetězec kratší než 4
    byty (nevyplatilo by se to prostorově).

-   **Kopírování shody:** C program si vytvoří pracovní ukazatel do
    historie výstupního bufferu (`m_idx = o_idx - offset;`) a spustí
    cyklus, kterým zkopíruje daný počet bajtů znovu na konec tohoto
    samého bufferu.

Tento jednoduchý a elegantní proces (čti token $\rightarrow$ opiš
literály $\rightarrow$ opiš historii $\rightarrow$ opakuj) běží tak
dlouho, dokud výstupní index `o_idx` nedosáhne originální velikosti
souboru. Výpočetní složitost pro Motorolu 68000 se omezuje téměř
výhradně na jednoduché iterace v cyklu a zvyšování hodnot u indexů pole,
což představuje tu vůbec nejrychlejší metodu zpracování objemných dat v
jazyce C pro tento retro systém.

# Úskalí historického jazyka C (Alcyon C) na CP/M-68K

Programování pro platformu 68k-MBC s procesorem Motorola 68000 a
operačním systémem CP/M-68K nelze srovnávat s vývojem v moderním
standardu ANSI C nebo C99. Historický kompilátor Alcyon C, který je na
této platformě dostupný, vychází z prapůvodní specifikace K&R (Kernighan
& Ritchie) a vyžaduje vysoce specifický přístup.

Během vývoje dekódovacího a přijímacího programu `68KSER.C` bylo nutné
vyřešit hned několik kritických problémů spojených s architekturou
procesoru a vlastnostmi starého překladače.

## 1. Paměťový model, zásobník a `Exception $03`

Jedním z nejčastějších důvodů pádů programů na CP/M-68K je tzv.
`Address Error` (Exception `$03`). Procesor Motorola 68000 striktně
vyžaduje, aby k vícebajtovým proměnným (jako jsou 16bitové `int` nebo
32bitové `long` ukazatele) bylo přistupováno pouze na sudých adresách v
paměti.

Moderní překladače se o správné zarovnání (alignment) starají
automaticky, ale u starého Alcyon C hrozí obrovské riziko při použití
lokálních proměnných. Lokální proměnné jsou ukládány na zásobník, který
má v CP/M velmi omezenou velikost. Pokud bychom obrovské buffery
deklarovali uvnitř funkce `main`, zásobník by okamžitě přetekl, porušilo
by se zarovnání a systém by zhavaroval.

**Řešení:** Veškeré kritické a rozsáhlé proměnné musí být deklarovány
globálně. V kódu `68KSER.C` tak vidíme statickou alokaci obřích polí pro
LZ4 dekompresi zcela mimo těla funkcí:

``` c
/* Buffery nastaveny pro garantovanych 750 kB volne RAM */
char in_buf[320000L];  /* Pro přijatá LZ4 data */
char out_buf[320000L]; /* Pro rozbalená data */
long fcb_wd[10];       /* File Control Block */
long dma_wd[32];       /* 128 Bytes - Presne jeden sektor! */
```

Tímto způsobem se proměnné vloží do datového (BSS) segmentu programu a o
jejich bezpečné zarovnání a umístění v paměti se postará linker ještě
před spuštěním programu.

## 2. Zrádné bitové posuny a skryté rozšiřování znaménka (Sign Extension)

Při manipulaci s binárními daty program neustále skládá 8bitové znaky
(char) do větších struktur (například při výpočtu 32bitového Hashe nebo
adresních offsetů u LZ4 dekomprese). V historickém C je typ char
defaultně chápán jako číslo se znaménkem (od -128 do 127). Pokud má
načtený byte nastavený nejvyšší bit (je větší než 127) a my ho přiřadíme
do proměnné typu long, kompilátor provede tzv. rozšíření znaménka (sign
extension) a vyplní všechny vyšší bity jedničkami. To kompletně zničí
jakýkoliv matematický výpočet.

Řešení prvního problému (Maskování): Při každém čtení znaku z paměti je
nezbytné natvrdo vynulovat horní bity pomocí logického součinu (AND) s
maskou 0xFF. V kódu se tento vzor opakuje neustále:

``` c
c = p_rd[i] & 0xFF;
/* nebo u LZ4 dekomprese: */
token = in_buf[i_idx++] & 0xFF;
```

Řešení druhého problému (Pořadí přetypování): Při implementaci dekodéru
LZ4 se narazilo na další kritickou chybu historického kompilátoru při
skládání 16bitového offsetu ze dvou bajtů. Pokud se provede bitový posun
(`<< 8`) přímo na hodnotě typu `char` nebo `int` a teprve výsledek se
uloží do proměnné typu `long`, starý překladač horní bity ořízne nebo
posune chybně. V kódu 68KSER.C je proto explicitní oprava chování
kompilátoru -- nejprve se načtený byte přetypuje na 32bitový long a
teprve v tomto obřím prostoru se provede posun:

``` c
/* Pretypovani na (long) PRED bitovym posunem */
offset = (long)(in_buf[i_idx++] & 0xFF); 
offset |= ((long)(in_buf[i_idx++] & 0xFF) << 8);
```

## 3. Nespolehlivost standardní knihovny

(zbavme `STDIO.H`)

Při prvních pokusech o zápis binárních dat na CP/M se obvykle zjistí, že
standardní funkce jako fopen(), fgetc() nebo fputc() (z knihovny
`stdio.h`) jsou naprosto nespolehlivé. Byly totiž navrženy pro práci
s textem. Pokud taková funkce narazí uprostřed binárního souboru na bajt
s hodnotou 0x1A (Ctrl+Z), tiše si usmyslí, že soubor skončil, a zbytek
dat zahodí.

Řešení (Přímá BDOS volání): Spolehlivý systém přenosu musí standardní
knihovnu zcela ignorovat a operovat přímo na úrovni systémových
přerušení operačního systému. V 68KSER.C nenajdete `#include <stdio.h>`.

Namísto toho program komunikuje přímo s kernelem CP/M pomocí univerzální
funkce bdos(). Zápis a čtení ze sériové linky: Provádí se přímým voláním
BDOS služby číslo 6 (Direct Console I/O).

``` c
c = (int)(bdos(6, 255L) & 0xFFL); /* Nízkourovňové čtení bajtu */
```

Zápis a čtení z disku: Pro zápis se používá systém FCB (File Control
Block). Aplikace manuálně nastaví adresu v paměti (dma_wd) voláním BDOS
služby 26 (Set DMA address) a poté zapisuje celá bloková data (128 bajtů
= 1 sektor) pomocí volání 21 (Write Sequential).

## 4. K&R syntaxe deklarace funkcí

Pro moderního programátora představuje úskalí i samotný zápis kódu.
Alcyon C nepodporuje deklaraci parametrů uvnitř závorek funkce.
Parametry se musí nejprve vyjmenovat a jejich datový typ se definuje až
před otevírací složenou závorkou. Příklad deklarace funkce z kódu
68KSER.C:

``` c
void do_rx(fname, is_text) 
char *fname; 
int is_text; 
{
    /* Telo funkce */
}
```

Stejný archaický přístup je aplikován i na funkci main, která postrádá
explicitní typ návratové hodnoty a argumenty deklaruje v K&R stylu
`(main(argc, argv) int argc; char **argv; { ... })`.

# Specifika CP/M: Sektorové zarovnání a problém s Hashováním

Historický operační systém CP/M má jeden zásadní architektonický rozdíl
oproti moderním operačním systémům, který představuje obrovskou překážku
pro ověřování integrity binárních souborů. CP/M totiž ve své adresářové
struktuře vůbec neeviduje přesnou délku souboru v bajtech. Udržuje si
pouze informaci o počtu alokovaných bloků -- takzvaných záznamů či
sektorů, které mají v CP/M vždy fixní velikost 128 bajtů.

Jak ukazuje kód `SHASH.C`, nízkoúrovňové čtení souboru z disku probíhá
přes BDOS volání výhradně po celých 128bajtových sektorech.

## Rozdíl mezi PC a CP/M

Tato vlastnost představuje zásadní problém pro náš výpočet DJB2 hashe.
Představme si, že posíláme z PC binární soubor o přesné velikosti 100
bajtů.

-   Pokud bychom na straně PC spočítali hash pouze z těchto 100 bajtů,
    získali bychom určitý výsledek.

-   Jakmile se ale soubor uloží na disk v CP/M-68K, operační systém pro
    něj vyhradí celý jeden sektor o velikosti 128 bajtů. Zbylých 28
    bajtů na konci sektoru je typicky vyplněno vycpávkovým znakem
    (paddingem) nebo předchozím "smetím" z paměti.

-   Pokud na tomto uloženém souboru v CP/M spustíme kontrolní program
    `SHASH.C`, ten přečte celý 128bajtový blok a spočítá hash z něj.

-   Výsledkem by byl naprostý nesoulad -- kontrolní součet na PC a na
    CP/M by se lišil a my bychom falešně detekovali poškozený přenos.

## Řešení na straně vysílače (PC)

Aby se tomuto problému předešlo, musí Python skript `68k-ser.py`
nasimulovat chování CP/M disku ještě předtím, než začne počítat
kontrolní hash.

Skript provádí zarovnání velikosti původních surových dat (`raw_data`)
matematickým výpočtem `pad_len = (128 - (len(raw_data) % 128)) % 128`.
Tím zjistí, kolik znaků přesně chybí do násobku 128. Následně za původní
data připojí příslušný počet znaků `0x1A` (v CP/M znak EOF, tedy Ctrl+Z)
a vytvoří takzvaný zarovnaný blok (`padded_payload`).

Očekávaný hash, který se následně kóduje do hlavičky streamu, se pak
počítá právě z tohoto vycpaného a zarovnaného bloku dat:

``` python
# Simulace CP/M sektoru v Pythonu (68k-ser.py)
pad_len = (128 - (len(raw_data) % 128)) % 128
padded_payload = raw_data + (b'\x1A' * pad_len)

hash_val = 5381
for b in padded_payload:
    hash_val = ((hash_val << 5) + hash_val + b) & 0xFFFFFFFF
```

## Řešení na straně přijímače a dekodéru (CP/M)

Analogická oprava se nachází i v přijímacím C programu 68KSER.C.
Přestože LZ4 dekompresor dokáže rozbalit data na naprosto přesnou
původní velikost (orig_sz), hashovací rutina nepočítá otisk pouze z této
délky. Nejprve si matematicky určí zarovnanou velikost
`(padded_len = ((orig_sz + 127) / 128) * 128L;)`.

Poté v cyklu prochází tento zarovnaný prostor -- pokud je čtecí index v
oblasti platných dat, bere znak z bufferu (out_buf\[h_idx\] & 0xFF), a
pokud už čte za koncem platných dat, uměle podvrhne do výpočtu hashe
hodnotu 26 (dekadický zápis pro 0x1A).

``` c
/* Hashování se simulací vycpávky (68KSER.C) */
padded_len = ((orig_sz + 127) / 128) * 128L;
for (h_idx = 0; h_idx < padded_len; h_idx++) {
    c_val = (h_idx < orig_sz) ? (out_buf[h_idx] & 0xFF) : 26;
    my_hash = ((my_hash << 5) + my_hash) + c_val;
}
```

Aby byla iluze dokonalá a trvalá, musí se tato vycpávka promítnout i do
fyzického zápisu na SD kartu. Kód pro zápis souboru má speciální blok,
který poslední nekompletní sektor ("ocas" dat) natvrdo vyplní číslem 26
(znakem EOF). Následně provede zápis na disk.

# Utility `SHASH` a `B64CODER`

## Nezávislé ověření (SHASH.C)

Díky obousměrnému zarovnání funguje kontrolní hash
zcela univerzálně. Pokud si uživatel zkontroluje soubor na PC, obdrží
platný kontrolní součet. A pokud na retro desce spustí nezávislý
jednoúčelový program SHASH.C pro ověření dat přímo na disku, dopadne to
stejně úspěšně. Nativní program SHASH.C pomocí systémového volání
(BDOS funkce 20) postupně načítá celé bloky dat přímo z disku do
vyhrazeného pole dma_wd, které má velikost přesně 64 celých čísel (tedy
64 × 2 = 128 bajtů). Celých těchto 128 bajtů je pak odesláno do DJB2
smyčky. Vzhledem k tomu, že soubor byl přijímacím modulem již dříve
pečlivě vycpán znaky 0x1A do celého sektoru, vypočítá se vždy navlas
stejný kontrolní otisk souboru jako na původním odesílajícím PC.

# Samostatný převod na disku (B64CODER)

Zatímco program `68KSER` je navržen pro dynamický přenos dat (vysílání a
příjem) přes sériovou linku spojený s kompresí, často vyvstává potřeba
převést data do bezpečného formátu Base64 (či z něj) přímo lokálně, tedy
bez použití sériového spojení s moderním PC. K tomuto účelu slouží
jednoúčelový program `B64CODER.C`.

Tento program představuje nativní kodér a dekodér formátu Base64 napsaný
v Alcyon C přímo pro CP/M-68K.

Použití utility z příkazového řádku je velmi přímočaré:

-   **Zakódování binárního souboru do textu:**
    `B64CODER CODE SOUBOR.BIN SOUBOR.B64`

-   **Dekódování textu zpět do binární formy:**
    `B64CODER DECODE SOUBOR.B64 SOUBOR.BIN`

## Nízkoúrovňová architektura a bezpečnost 

Nástroj `B64CODER` architektonicky sdílí ta nejlepší řešení ze svých
sesterských nástrojů a vyhýbá se známým pastem historického překladače.

**Bezpečné zarovnání paměti:** Aby program nezpůsobil pád systému
(Exception `$03` neboli Address Error), jsou čtecí a zápisové paměťové
bloky deklarovány globálně jako pole celých čísel (`int dma_rd_wd[64]` a
`int dma_wr_wd[64]`). Tím se zajistí, že paměť (64 prvků typu `int`
odpovídá přesně 128 bajtům jednoho CP/M sektoru) bude v operační paměti
zarovnána na sudou adresu a zásobník nepřeteče.

**Ignorování vadné knihovny stdio.h:** Program zcela obchází standardní
knihovnu I/O. Čtení (funkce `do_encode` a `do_decode`) probíhá pomocí
přímých volání systému BDOS -- využívají se CP/M struktury FCB (File
Control Block) a funkce číslo 15, 19, 20, 21 a 22. Díky blokovému čtení
přes BDOS 20 kodér `do_encode` ignoruje znaky `0x1A` (Ctrl+Z)
nacházející se uvnitř binárního souboru a nepřeruší čtení předčasně, což
je pro zpracování komprimovaných nebo spouštěcích souborů zcela
kritické.

## Proces převodu dat (do_encode)

Při spuštění v režimu `CODE` načítá program surové 128bajtové sektory do
paměti a bere z nich postupně trojice bajtů. Ty převádí pomocí bitového
posunu a jednoduché mapovací tabulky `b64_table` na čtyři znaky z
bezpečné Base64 abecedy.

Každý vygenerovaný znak se vkládá do paměti funkcí `put_wr()`. Jakmile
se výstupní buffer zaplní (dosáhne 128 bajtů), funkce automaticky
provede systémové volání BDOS 21 a sektor fyzicky zapíše na kartu.
Algoritmus zároveň hlídá formátování -- po každých 64 znacích vloží
znaky pro zalomení řádku (`\r\n`). Na úplném konci procesu, po případném
doplnění výplně rovnítky (`=`), kodér manuálně vloží znak 26 (`Ctrl+Z`),
aby byl výsledný soubor chápán systémem CP/M jako validní text.

## Zpětné dekódování a sektorové zarovnání (do_decode)

Režim `DECODE` dělá proces opačně. Prochází zdrojový Base64 text bajt po
bajtu, a jakmile narazí na výplň (`=`) nebo znak konce textu (`26`),
proces parsování okamžitě ukončí.

Zde se opět setkáváme s nezbytností vyřešit CP/M sektorové zarovnání.
Dekódovaná originální binární data málokdy vyjdou na přesný násobek 128
bajtů (velikost sektoru). Zápis posledního "zbytkového" bloku dat do
souboru má proto na starosti speciální funkce `flush_wr()`. Pokud na
konci převodu zůstanou ve výstupním bufferu neuložená data (index
`wr_idx > 0`), funkce celou zbývající mezeru až do velikosti 128 bajtů
tvrdě vyplní vato -- znakem 26 (`Ctrl+Z`). Až tento plný a zarovnaný
sektor je odeslán k zápisu na disk, čímž je zaručena úplná integrita
CP/M souborového systému.

## Optimalizace vizuální odezvy

Program běží na pomalém 16bitovém procesoru Motorola 68000 s taktem 8
MHz. Protože zpracování velkých souborů chvíli trvá, je program vybaven
vizuální indikací ("vrtulkou" používající znaky `|/-\`), která dává
uživateli najevo, že systém nezamrzl.

Aby ovšem samotné vykreslování znaků na terminál (volání grafického
výstupu je pomalé) nezdržovalo výpočetní cyklus převodu, animace se na
obrazovce pootočí vždy až po zpracování každých 1024 bajtů (celých 8
sektorů), o což se stará matematická bitová maska
`(total & 1023L) == 0L`.

# Hromadná záloha disku z CP/M-68K

## Nástroje SERDISK a serdisk-prijem.py

Zatímco nástroj `68KSER` je ideální pro rychlý přenos jednotlivých
souborů během vývoje, při potřebě zálohovat celý obsah CP/M disku do
moderního PC by bylo ruční přenášení každého souboru zdlouhavé. K tomuto
účelu vznikl plně automatizovaný dávkový systém, který se skládá z
odesílacího C programu `SERDISK.C` pro CP/M-68K a přijímacího Python
skriptu `serdisk-prijem.py` pro PC.

Tento systém prochází adresář zvoleného disku, identifikuje všechny
platné soubory, zakóduje je do formátu Base64 společně s DJB2 hashem a
jako jeden nepřetržitý stream je odešle přes sériovou linku. Python
skript tento proud dat zachytává, automaticky detekuje typy souborů a
ukládá je do vybrané složky na PC.

## Skenování adresáře a filtrace CP/M extentů

Prvním úkolem programu `SERDISK.C` je zjistit, jaké soubory se na disku
nacházejí. K tomu využívá systémová volání BDOS 17 (Search First) a BDOS
18 (Search Next).

Zde jsme narazili na specifikum historického souborového systému CP/M.
Velké soubory nejsou v adresáři zapsány jako jedna položka, ale jsou
rozděleny na takzvané Extenty (logické části). Pokud by program
jednoduše vypsal všechny nalezené položky na disku, velké soubory by se
v seznamu objevily vícekrát a následně by se i vícenásobně odesílaly,
což by zálohu znehodnotilo.

**Řešení problému:** Při sestavování vyhledávacího bloku FCB program
natvrdo nastaví bajt s indexem 12 na nulu (`search_fcb[12] = 0;`). Tím
přikáže systému CP/M, aby vyhledával pouze první (nulté) extenty, tedy
samotné hlavičky souborů. Získané jméno je následně očištěno a uloženo
do pole `file_list`, které pojme až 256 unikátních názvů. Před přidáním
navíc probíhá pojistná kontrola vlastní funkcí `is_dup`, aby se do
seznamu nedostaly žádné duplikáty.

## Kritické ochrany v kódu SERDISK.C

Vzhledem k nutnosti maximálně šetřit pamětí RAM a odesílat data co
nejrychleji, neobsahuje `SERDISK.C` standardní knihovnu `<stdio.h>` a
využívá vlastní, vysoce optimalizovaný tiskový engine (`fast_putchar`).
To však přineslo několik nízkoúrovňových problémů, které kód řeší
dedikovanými ochrannými mechanismy:

1.  **Zarování paměti (Address Error):** Stejně jako u ostatních
    nástrojů, paměťové buffery `fcb_wd` a `dma_wd` jsou deklarovány jako
    typ `long` pro garanci zarovnání na sudé adresy, aby nedošlo k
    Exception `$03`.

2.  **Záchrana DMA adresy:** Tisková funkce používá pro výpis na
    sériovou linku BDOS službu 6. CP/M-68K má však tendenci po tomto
    volání resetovat systémovou DMA adresu (do které se načítají soubory
    z disku) na výchozí hodnotu `0x0080`. Aby systém nezačal sypat data
    ze čtených souborů do špatné paměti, program zavolá před každým
    načtením jednoho sektoru BDOS 26, čímž neustále vnucuje správnou
    adresu vlastního DMA bufferu.

3.  **Ochrana před chybou kompilátoru:** Výpočet DJB2 hashe pro
    32bitovou proměnnou by v Alcyon C při zápisu na jeden řádek způsobil
    zhroucení registrů. Výpočet je proto rozložen do tří primitivních,
    izolovaných matematických kroků
    (`temp_h = hash_val << 5; hash_val = temp_h + hash_val;` atd.).

4.  **Synchronizace PC (Delay loop):** Na konci každého souboru program
    odešle značku `===END_FILE:hash===` a zavře disk. Motorole 68000 by
    na 8 MHz trvalo pouhý okamžik přejít k dalšímu souboru a začít
    chrlit další data. Python skript na straně PC ale potřebuje čas na
    dekódování Base64, ověření hashe a fyzický zápis na SSD disk.
    `SERDISK.C` proto před odesláním dalšího souboru záměrně čeká v
    prázdné zpožďovací smyčce
    (`for (delay = 0; delay < 100000L; delay++) {}`).

## Zpracování dat na straně PC (serdisk-prijem.py)

Na straně moderního počítače naslouchá python skript `serdisk-prijem.py`
rychlostí 115200 baudů a využívá stavový automat (proměnná `receiving`).
Pokud na lince zachytí text `===BEGIN_FILE:SOUBOR.EXT===`, přepne se do
režimu skládání dat.

Jakmile dorazí patička s hashem, skript proud dat odřízne, ale
nezahazuje žádná data (případný začátek nového souboru zachová pro další
cyklus v bufferu `stream_buffer`). S přijatými Base64 daty následně
provede několik operací:

### Očištění a Hash kontrola

Aby se předešlo selhání dekódování kvůli případnému šumu na sériové
lince, skript nejprve data prožene regulárním výrazem
(`re.sub(rb'[^A-Za-z0-9+/=]', b'', file_data_b64)`), který smaže všechny
znaky mimo platnou Base64 abecedu. Poté rozbalí binární byty. Pro
výpočet hashe pak skript opět simuluje 128bajtový sektor CP/M -- na
konec dat přidá znaky `0x1A` tak, aby délka zarovnaného souboru byla
přesným násobkem 128. Teprve z těchto vycpaných dat počítá DJB2 hash a
porovnává jej s hashem obdrženým od 68k-MBC.

### Autodetekce typu (Heuristika)

Protože program na retro počítači posílá všechny soubory slepě, skript
na PC se musí sám rozhodnout, zda přijatý soubor zpracuje jako text,
nebo jako binární data.

-   Nejprve zkouší detekci podle přípony (např. `.c`, `.txt`, `.bas`).

-   Pokud příponu nezná, zkoumá samotný obsah (**Content Sniffing**).
    Pokud po odstranění vycpávek v souboru neobjeví žádný nulový bajt
    (`0x00`) ani žádné podivné řídicí znaky (mimo Tab, CR a LF),
    předpokládá, že se jedná o ASCII text.

### Finální uložení

Způsob zápisu na disk se řídí výsledkem detekce:

-   **Textový soubor:** CP/M odřádkování (CRLF) je převedeno na linuxové
    (LF). Soubor je useknut při prvním výskytu znaku `0x1A` (konec
    textu) a uložen v moderním UTF-8 kódování.

-   **Binární soubor:** Skript opatrně odebere vycpávku (maximálně 127
    bajtů hodnoty `0x1A` pouze z úplného konce souboru) a data surově
    zapíše na PC.

Celý proces zálohování automaticky skončí, jakmile skript zachytí
finální řetězec `===END_DISK===`.

# Reálné využití

Ověřeno, přenos funguje spolehlivě oběma směry. Přenos celé disku už
vznikl jako nadstavba pro potřeby zálohy. S jistotou mohu říci, že
binární `.68K` soubory uložené v PC fungují i na jiném CP/M-68K systému.

\
[odkazy na programy](https://drive.google.com/drive/folders/1Ks-HDH_OrU_odsmTnd0qe1jbTylFh4P-?usp=drive_link)

-   `68k-ser.py` python program pro přenos dat
-   `68KSER.C` Alcyon C program pro 68K-MBC
-   `SHASH.C` Alcyon C počítá hash
-   `spocit-hash.py` spočte hash na PC
-   `B64CODER.C` Alcyon C pro B64 kódování a dekódování
-   `serdisk-prijem.py` v PC přijme celý disk
-   `SERDISK.C` z 68k-MBC pošle celý CP/M disk

-   `*.68K` binární zkompilované programy pro CP/M-68K


