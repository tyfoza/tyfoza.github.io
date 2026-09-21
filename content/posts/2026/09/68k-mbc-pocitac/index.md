---
title: "Počítač 68k-MBC"
date: 2026-08-20T22:27:00+02:00
cover:
    image: "mbc.webp"
tags: ["Počítače", "Počítače.M68k"]
draft: false
math: true
---

68k-MBC of autora Just4Fun. Domácí retro jednodeskový počítač. 
Navazuje na předchozí autorovy projekty Z80-MBC2 (Zilog Z80)
a V20-MBC (NEC V20).

Počítač je postavený na Motorola 68008 (1982). Procesor původně vznikl
jako levnější varianta procesoru M68k (1979) a lišil se především
8bitovou vnější sběrnicí.
Díky tomu mohli výrobci navrhovat
levnější hardware s použitím běžných 8bitových pamětí, řadičů a periferií.
V komerční sféře tento procesor proslavil počítač Sinclair QL (1984).

Projekt 68k-MBC nabízí možnost, jak si
vyzkoušet oživení 16bitového počítače bez nutnosti shánět někdy už
nedostupné historické součástky.

{{< obr600 "mbc.webp" "" >}}

Víc na [hackaday.io](https://hackaday.io/project/177988-68k-mbc-a-3-ics-68008-homebrew-computer)

# Hardwarová architektura

Architektura základní desky v plně osazené verzi je
minimalistická. Skládá se ze tří hlavních
integrovaných obvodů a jednoho volitelného GPIO expandéru.

Srdcem počítače je 16/32bitový mikroprocesor Motorola MC68008. Uvnitř
čipu se skrývá plnohodnotná 32bitová architektura s 32bitovými datovými
i adresními registry, ovšem vnější datová sběrnice je pouze 8bitová.
Instrukce se proto musí z paměti načítat po částech, kvůli čemuž
procesor dosahuje zhruba 50--60 % výkonu své plnohodnotné varianty
MC68000.

Moderním prvkem je řídicí mikrokontrolér Microchip
PIC18F47Q10. Tento čip plní funkci I/O subsystému, zajišťuje TTL
kompatibilitu pro propojení s procesorem a obsluhuje I2C sběrnici.
Zásadním způsobem usnadňuje stavbu, protože supluje roli EPROM paměti
(obsahuje firmware) a stará se o bootování, díky čemuž stavitelé
nepotřebují klasický programátor historických pamětí.

Operační paměť systému tvoří statická RAM (SRAM), která na rozdíl od
pamětí typu DRAM nevyžaduje neustálé oživování. K dosažení maximální
kapacity 1 MB (1024 kB) se využívají dva paměťové čipy SAMSUNG
K6T4008C1B-DL70. Každý z těchto čipů disponuje kapacitou 512 kB (524 288
bajtů), rychlou přístupovou dobou 70 ns a je dodáván v nízkopříkonové
variantě v průchozím pouzdře DIP.

Na desce lze dále nalézt 16bitový I/O expander MCP23017. Tento obvod
poskytuje 16 volně programovatelných bidirekčních digitálních pinů na
konektoru J7, které lze využít k připojení tlačítek, LED diod nebo
tiskárny. Pokud není osazen, tento konektor zůstává nefunkční.

# Operační systémy a software

Při startu systému se spustí CP/M nebo Enhanced 68K Basic nebo sLoad/Autobook
pro přímé nahrání nebo spuštění bare-metal kódu. 

Mě zaujal převším OS CP/M-68K, port CP/M odladěný přímo pro architekturu Motoroly.

Pomocí multi-boot menu lze nastavit v jakém režimu se má spouštět.

Pokud potřebujem multi-boot menu vyvolat - `RESET`, stiknout a držet
`USER tlačítko`, pustit `RESET`.

```text
68k-MBC - A091020-R140221
IOS - I/O Subsystem - S310121-R231021

IOS: Full HW configuration detected
IOS: Found RTC DS3231 Module (21/09/26 10:37:02)
IOS: RTC DS3231 temperature sensor: 28C
IOS: Found GPE Option
IOS: CP/M Autoexec is OFF

IOS: Select boot mode or system parameters:
 0: No change (4)
 1: sLoad
 2: Enhanced 68K Basic
 3: Autoboot
 4: Load OS from Disk Set 0 (CP/M-68K v1.3)
 5: Change Disk Set 0 (CP/M-68K v1.3)
 6: Change serial ports speed
 7: Change CP/M Autoexec (->ON)
 8: Change RTC time/date

Enter your choice >

```

# Úložiště a periferie

Floppy disky pro systém CP/M, se uchovávají na SD kartě. Tyto disky jsou
emulovány mikrokontrolérem jako soubory s obrazem ve formátu .DSK.

Vzhledem k tomu, že systém není primárně herní konzolí a nedisponuje
vlastním grafickým čipem (na rozdíl od počítačů Amiga či Atari ST),
veškerá komunikace s uživatelem probíhá přes sériovou linku (RS232 /
USB). Jako obrazovka a klávesnice typicky slouží běžné PC s terminálovým
programem (například tio / PuTTY), nebo lze připojit dedikovaný
doplňkový hardware s VGA výstupem, jako je terminál uTerm nebo třeba PicoTerm.

# Anachronismus v době gigahertzů

Dneska i nejlevnější chytré hodinky disponují tisícinásobně
vyšším výpočetním výkonem a kapacitou paměti než sálové počítače ze
sklonku 20. století. V době vícejádrových gigahertzových procesorů,
všudypřítomné umělé inteligence a gigabytových webových aplikací působí
stavba jednodeskového počítače s procesorem Motorola 68008 na první
pohled jako podivínství.

Skeptik by se mohl oprávněně ptát: *Proč v roce 2026 věnovat hodiny
pájení, shánění součástek a ladění sériového přenosu něčemu, co neumí
zobrazit ani jednoduchou webovou stránku a čehož celý operační systém
zabírá méně místa než jedna fotka z mobilu? Je 68k-MBC jen slepou
uličkou pro hrstku pamětníků podléhajících sentimentu?*

Abychom našli poctivou odpověď, musíme se podívat na argumenty pro i
proti a prozkoumat, co tento minimalistický stroj nabízí dnešnímu
studentovi informatiky, elektronikovi nebo softwarovému nadšenci.

# Skeptik volí emulaci

Při kritickém pohledu musíme přiznat, že stavba 68k-MBC naráží na řadu
praktických i pragmatických limitů:

-   **Úplná absence moderních standardů:** Počítač nemá grafický výstup,
    zvukovou kartu, ethernetový port ani rozhraní USB. Veškerá interakce
    probíhá přes sériovou linku, což okamžitě vylučuje jakékoliv moderní
    multimediální využití.

-   **Můžeme použít softwarovou emulaci** Pokud je cílem pouhé spuštění
    historického softwaru či operačního systému CP/M-68K, běžný počítač
    zvládne běh emulátoru (jako je MAME, QEMU nebo specializované
    C-emulátory) v okně prohlížeče bez nutnosti utratit korunu za
    hardware. Emulátor navíc nabízí okamžitý přenos souborů, možnost
    uložení stavu a nesrovnatelně vyšší komfort.

-   **Nízká výpočetní rychlost:** Taktovací frekvence v řádu jednotek
    megahertzů a 8bitová vnější sběrnice znamenají, že i náročnější
    kompilace zdrojového kódu v C nebo Pascalu trvá znatelně déle než v
    moderním prostředí.

Prizmatem "spotřebitele výpočetního
výkonu"je 68k-MBC nepraktický anachronismus.

# Optimista hledá kouzlo reálného hardwaru

Skutečný význam 68k-MBC se však neukrývá v tom, **co** počítač dělá, ale
**jak** to dělá a **jakým způsobem** vznikl. Nejcennější přidanou
hodnotou projektu je samotný proces stavby a bastlení (DIY -- *Do It Yourself*).

Proces batlení, osazení desky a hlavně obří prastarý čip Motorola MC68008,
vytváří zcela osobní vztah ke stroji. Připomíná to pocity rybáře, který po dlouhém
čekání zasekne rybu, nebo RC leteckého modeláře, jehož vlastnoručně vyrobený model
se poprvé odlepí od země.

Díky stavbě pak počítač není black boxem, ale
srozumitelný systém, kde uživatel zná roli každého integrovaného
obvodu od mikrokontroléru PIC až po SRAM.

>**Pocit z oživení:** Na emulátoru vidíte jen simulaci. Na 68k-MBC
vidíte reálné elektrické signály kmitající po měděných cestách desky
plošných spojů. Každý znak na terminálu je výsledkem fyzického tok
elektrického proudu skrz skutečný křemík.

# Výuková laboratoř architektury

Pro studenta IT nebo elektroniky představuje 68k-MBC pěknou výukovou pomůcku.
Dnešní operační systémy jsou tak složité, že pod
vrstvami abstrakce znemožňují pochopit základní principy fungování
počítače. 

68k-MBC naopak nabízí přímočarý a transparentní přístup. A má slušnou komunitní
podporu.

## Široká paleta vývojových nástrojů

Otevřené dveře k historickému i modernímu programování:

1.  **Interaktivní začátky v Enhanced 68k BASICu:** Vynikající
    prostředek pro rychlé experimenty, manipulaci s pamětí (příkazy
    `PEEK` a `POKE`) a tvorbu jednoduchých algoritmů bez nutnosti
    kompilace.
    
    Narazíme na nemožnost použít LOAD/SAVE na SD kartu. Řeší to copy/paste
    textových dat do terminálu.

2.  **Klasická textová editace a překlad v CP/M-68K:** Procházet
    vývojovým cyklem přímo na cílovém stroji má své neopakovatelné
    kouzlo. Kód lze napsat v systémovém editoru **SKED** (nebo **ED**) a
    následně jej zkompilovat:

    -   **Alcyon C:** Původní profesionální kompilátor jazyka C pro
        architekturu 68000, který odhalí vícestupňový proces kompilace
        (předzpracování, překlad do asembleru, assemblování a
        linkování).

    -   **Pascal/MT+ 3.3 for CP/M-68K:** Legendární strukturovaný jazyk,
        který v 80. letech vládl akademické půdě a učil správným
        programátorským návykům.

    -   **CBASIC (C68) Basic Compiler:** Přeložený BASIC pro ty, kteří
        požadovali vyšší rychlost než u běžného interpretu.

## Emulátor `COM` a most k 8bitové historii

FV prostředí CP/M-68K je existueje emulační vrstva pro spouštění
8bitových aplikací (s příponou `.COM` určených původně pro procesory Intel 8080
či Zilog Z80). Díky tomuto emulátoru lze na 16bitové Motorole spouštět
textové adventury a historický software:

``` text
H>COM ADVENT.COM
Adventure 1.0 - (c) 1982 The Software Toolworks

Welcome to Adventure!!  Would you like instructions?
```

32bitové jádro procesoru v reálném čase emuluje 8bitový instrukční kód,
aby spustilo klasický **ZORK 1/2/3** nebo **ADVENT**.

# Zábavný projekt

Je tedy 68k-MBC pouze podivínským nesyslem? Trochu asi je, ale když už ho mám 
postavený...

Možná neulehčí každodenní práci, ale jeho hodnota spočívá v **edukaci a
retro zážitku**. Je to stroj, který vrací do informatiky
hmatatelnost a řemeslo. Pro studenta představuje nejlepší možnou
učebnici architektury počítačů, pro bastlíře je to výzva třeba napsat něco v 
asembleru a pro retro nadšence nezaměnitelná brána do zlatého
věku počítačové historie.

# 1 MB adresního prostoru

Z hlediska architektury instrukční sady je Motorola MC68008
plnohodnotným členem rodiny 68000. Uvnitř jádra pracuje s 32bitovými
datovými i adresními registry, díky čemuž z pohledu softwaru disponuje
souvislým, nesegmentovaným, říkáme plochým adresním prostorem.

Zatímco klasická Motorola 68000 vyvádí na pouzdro 24 adresních vodičů
(umožňujících adresovat 16 MB), pouzdro DIP-48 čipu MC68008 fyzicky
vyvádí 20 adresních piny ($A_{0}$ až $A_{19}$). Procesor tak dokáže
přímo adresovat paměťový rozsah o velikosti přesně 1 MB\
($2^{20\ } = 1\ 048\ 576$ bajtů), konkrétně v šestnáctkové soustavě od
`0x000000` po `0x0FFFFF`.

## Fyzická realizace RAM a Virtual I/O Engine

Na plně osazené desce 68k-MBC (Full verze) je tento 1 MB adresního
prostoru rozdělen mezi dvě fyzické statické paměti SRAM a speciální
hardwarové rozhraní emulované mikrokontrolérem:

1.  **SRAM Čip 0 (`0x000000` až `0x07FFFF` -- 512 kB):** Spodní polovina
    paměti. Na úplném začátku (`0x000000`) sídlí resetovací vektory
    procesoru (stohový ukazatel `SP` a programový čítač `PC`). Při běhu
    operačního systému CP/M-68K zde leží struktury BIOS/BDOS a systémové
    proměnné.

2.  **SRAM Čip 1 (`0x080000` až `0x0FFFFB` -- téměř 512 kB):** Horní
    polovina paměti určená pro uživatelské programy, dynamickou alokaci
    (heap) a zásobník (stack).

3.  **Virtual I/O Engine / IOS (`0x0FFFFC` až `0x0FFFFF` -- 4 bajty):**
    Samotná Motorola nemá samostatné I/O instrukce (jako `IN`/`OUT` u
    Intelu či Zilog Z80). Všechny periferie jsou mapovány přímo do
    paměti (Memory-Mapped I/O). Nejvyšší 4 bajty celého 1MB prostoru
    nesměřují do fyzické RAM, ale jsou zachytávány řídicím
    mikrokontrolérem Microchip PIC18F47Q10. Zde probíhá veškeré
    předávání opkódů a dat pro sériovou linku, SD kartu či RTC hodiny.

<table>
<colgroup>
<col style="width: 30%" />
<col style="width: 20%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Adresní rozsah (Hex)</strong></p></td>
<td><p><strong>Velikost</strong></p></td>
<td><p><strong>Využití v systému 68k-MBC</strong></p></td>
</tr>
<tr class="even">
<td><p><code>0x000000</code> – <code>0x07FFFF</code></p></td>
<td><p>512 kB</p></td>
<td><p>SRAM Čip 0<br />
Reset vektory, jádro CP/M, EhBASIC</p></td>
</tr>
<tr class="odd">
<td><p><code>0x080000</code> – <code>0x0FFFFB</code></p></td>
<td><p> 512 kB</p></td>
<td><p>SRAM Čip 1<br />
Uživatelská paměť (TPA), Heap, Stack</p></td>
</tr>
<tr class="even">
<td><p><code>0x0FFFFC</code> – <code>0x0FFFFF</code></p></td>
<td><p>4 bajty</p></td>
<td><p>IOS Virtual I/O Engine<br />
Komunikace s PIC18F47Q10</p></td>
</tr>
</tbody>
</table>


Na desce se nenachází žádná fyzická paměť ROM/EPROM. Při zapnutí
napájení mikrokontrolér PIC nepustí hlavní CPU do běhu (drží jej v
resetu/HALTu), naplní počáteční adresy v SRAM potřebnými zaváděcími
instrukcemi a teprve poté uvolní procesor k vykonávání kódu.

# Protokol `sLoad` pro vývoj bare-metal

Pro vývojáře, kteří chtějí z procesoru Motorola 68008 vyždímat maximální
výpočetní výkon nebo potřebují rychle testovat nově napsaný kód bez
zdlouhavého startu operačního systému, nabízí 68k-MBC režim `sLoad`.

## Jak sLoad funguje 

Pokud uživatel v multi-boot menu při startu desky zvolí možnost `sLoad`,
nastane následující sekvence hardwarových kroků:

1.  **Aktivace zaváděče:** Mikrokontrolér PIC (IOS) přepne sériový port
    do stavu očekávání a vypíše výzvu k příjmu dat ve standardizovaném
    textovém formátu **Motorola S-record** (soubory s příponou `.sr`
    nebo `.s68`).

2.  **Příjem a kontrola dat:** Vývojář pošle z PC přes sériovou linku
    zkompilovaný soubor. PIC čte zprávu řádek po řádku, ověřuje
    kontrolní součty (checksums) a parsuje cílové paměťové adresy.

3.  **Přímý zápis do SRAM:** Bity ze sériové linky zapisuje PIC přímo do
    paměťových čipů SAMSUNG SRAM na adresy určené v souboru S-record.

4.  **Skok na holé železo:** Jakmile dorazí ukončovací záznam (např.
    řádek `S7` či `S9`), PIC zruší signál `HALT` na procesoru MC68008 a
    nastaví jeho programový čítač přímo na startovní adresu nahrané
    aplikace.

Program zkompilovaný pro `sLoad` běží v režimu **bare-metal** -- v
paměti není žádný operační systém, který by zabíral instrukční cykly
nebo omezoval přístup k hardwaru. Celý 1 MB RAM je k dispozici pouze pro
vývojářskou aplikaci.

# Křížový překlad (Cross-Compilation) pro 68k-MBC

Protože kompilace rozsáhlého zdrojového kódu v jazyce C zabere na 8MHz
procesoru s 8bitovou sběrnicí desítky sekund až minut, moderní vývojový
cyklus spoléhá na **křížový překlad (cross-compilation)**.

## GCC a vývojové prostředí v Dockeru

Křížový překladač běží na moderním pracovním stanici (x86_64 nebo ARM),
ale generuje strojové instrukce rodiny Motorola 68000. Aby vývojáři
nemuseli složitě řešit závislosti knihoven a staré verze systémů,
využívá se dockerizovaný toolchain obsahující `m68k-elf-gcc` propojený s
c-knihovnou `Newlib`.

### Pracovní postup (Rapid Prototyping)

Proces vývoje aplikace probíhá ve třech bleskových krocích:

``` text
[ Moderní PC (VS Code / C) ] ──(GCC cross-compiler)──> [ out.sr (S-Record) ]
                                                               │
                                                 (Sériová linka / tio / minicom)
                                                               │
                                                               🞃
[ 68k-MBC / Bare-Metal ] <──(Zápis do SRAM přes PIC)─── [ Režim sLoad ]
```

1.  **Napsání kódu na PC:** Kód je napsán v pohodlném prostředí
    moderního editoru.

2.  **Překlad do S-recordu:** Příkazový skript zkompiluje C kód a pomocí
    nástroje `objcopy` přeloží výstupní binárku do formátu Motorola
    S-record (`out.sr`).

3.  **Nahrání a spuštění:** Přes sériový terminál `minicom` se soubor pošle
    do 68k-MBC spuštěného v režimu `sLoad`.
    Celý proces od úpravy řádku kódu po jeho běh na reálné Motorole je okamžitý.

Tento přístup tak dokonale spojuje komfort moderního programování s retro 
zážitkem ze spouštění kódu na skutečném historickém křemíku.

# Adresování Virtual I/O Engine (IOS)

Mikroprocesor Motorola MC68008 nemá dedikovaný instrukční prostor pro
V/V operace (jaký známé například z architektur Intel x86 nebo Zilog
Z80). Veškerá komunikace s periferiemi se proto provádí přes paměťově
mapované V/V porty (Memory-Mapped I/O). Na základní desce 68k-MBC jsou
pro tento účel vyhrazeny nejvyšší adresy z 1MB adresního prostoru, na
kterých naslouchá řídicí mikrokontrolér Microchip PIC18F47Q10 (I/O
Subsystem -- IOS).

Komunikace s jakoukoliv periferií integrovanou v mikrokontroléru (nebo
připojenou na I2C sběrnici) probíhá ve dvou krocích: nejprve se do portu
řídicího příkazu zapíše tzv. **Opcode** (operační kód požadované
periferie) a následně se z datového portu hodnota přečte nebo se do něj
zapíše.

## Přehled adres a operačních kódů (Opcodes)

Pro přístup k rozhraní IOS a integrovaným prvkům využíváme následující
adresní porty a kódy:

-   **STORE OPCODE Port (`0xFFFFD` / `$FFFFD`):** Zápisový port určený
    pro nastavení aktivního operačního kódu (příkazu) v mikrokontroléru
    PIC.

-   **EXECUTE WRITE DATA Port (`0xFFFFC` / `$FFFFC`):** Zápisový port
    pro odeslání datového bajtu svázaného s dříve uloženým Opcode.

-   **EXECUTE READ DATA Port (`0xFFFFC` / `$FFFFC`):** Čtecí port pro
    sekvenční vyčítání naměřených nebo stavových bajtů.


|                   |                |                |                                           |
|------------------|------------|-----------|-------------------------------|
| **Funkce / Port** | **Adresa Hex** | **Opcode Hex** | **Princip a režim operace**               |
| STORE OPCODE      | `0xFFFFD`      | ---            | Uložení řídicího příkazu pro IOS (`POKE`) |
| EXECUTE WRITE     | `0xFFFFC`      | ---            | Zápis datového bajtu do IOS (`POKE`)      |
| EXECUTE READ      | `0xFFFFC`      | ---            | Čtení datového bajtu z IOS (`PEEK`)       |
| USER LED          | `0xFFFFD`      | `0x00` (`$00`) | USER_LED (1 = svítí, 0 = nesvítí)         |
| USER KEY          | `0xFFFFD`      | `0x80` (`$80`) | USER_BTN (1 = stisknuto)                  |
| RTC DS3231        | `0xFFFFD`      | `0x84` (`$84`) | 7 bajtů (čas, datum, teplota)             |


# Příklady v Enhanced 68k BASICu

Minimální funkční kód pro obsluhu
jednotlivých periferií. Všechny ukázky pracují s přímým přístupem do
paměti pomocí příkazů `POKE` a `PEEK`.

## Ovládání Uživatelské LED (USER LED)

Uživatelskou LED diodu ovláháme uložením Opcode `$00` na adresu `$FFFFD`
a následným zápisem logické hodnoty `1` (rozsvícení) nebo `0` (zhasnutí)
na adresu `$FFFFC`.

pro zhasnutí zapíše `1` na `$FFFFC`

``` basic
10 REM --- Rozsviceni USER LED ---
20 POKE $FFFFD, 0 : REM Ulozeni Opcode 0 (USER LED) 
30 POKE $FFFFC, 1 : REM Rozsvitit LED
```

pro zhasnutí zapíše `0` na `$FFFFC`

``` basic
10 REM --- Zhasnutí USER LED ---
20 POKE $FFFFD, 0 : REM Obnoveni Opcode 0 
30 POKE $FFFFC, 0 : REM Zhasnout LED

```

## Čtení stavu tlačítka USER (USER KEY)

Stav tlačítka USER zjistíme uložením Opcode `$80` na adresu `$FFFFD`.
Následné přečtení adresy `$FFFFC` vrátí hodnota `1`, pokud je tlačítko
právě stisknuto, nebo `0`, pokud je uvolněno.

``` basic
10 REM --- Cteni stavu tlacitka USER ---
20 POKE $FFFFD, $80 : REM Ulozeni Opcode $80 (USER KEY) 
30 K = PEEK($FFFFC) : REM Cteni stavu
40 IF K = 1 THEN PRINT "Tlacitko je STISKNUTO" ELSE PRINT "Tlacitko je uvolneno"
50 GOTO 20

```

## Vyčítání času, data a teploty z RTC DS3231 (volitelný modul)

Při práci s modulem RTC DS3231 pošleme mikrokontroléru Opcode `$84` na
adresu `$FFFFD`. Mikrokontrolér naplní vnitřní vyrovnávací paměť a každé
následující zavolání `PEEK($FFFFC)` vrátí postupně jeden z 7 datových
bajtů v pevně daném pořadí: **sekundy, minuty, hodiny, den, měsíc, rok
(od r. 2000)** a **teplota čipu v $C$**.

Protože hodnota teploty je vracena jako 8bitové číslo se znaménkem v
kódování dvojkového doplňku, pro záporné hodnoty (kdy je hodnota bajtu
vyšší než 127) provádíme odečet $256$.

``` basic
10 REM --- Cteni casu, data a teploty z RTC DS3231 ---
20 POKE $FFFFD, $84 : REM Ulozeni Opcode $84 (DATETIME) 
30 S = PEEK($FFFFC) : M = PEEK($FFFFC) : H = PEEK($FFFFC)
40 D = PEEK($FFFFC) : N = PEEK($FFFFC) : Y = PEEK($FFFFC) 
50 T = PEEK($FFFFC) : IF T > 127 THEN T = T - 256 : REM Dvojkovy doplnek
60 PRINT "Cas:     "; H; ":"; M; ":"; S
70 PRINT "Datum:   "; D; "/"; N; "/"; Y + 2000
80 PRINT "Teplota: "; T; " C"

```

Zde je podrobná kapitola o **GPE a I2C čipu MCP23017** zpracovaná ve
formátu **Typst** se stejnou hlavičkou, ASCII schématem konektoru J7,
přehlednou tabulkou registrového mapování / opcodů a stručnými ukázkami
v Enhanced 68k BASICu.

# Volitelné rozšíření GPE (GPIO Port Expander)

Počítač 68k-MBC ve své plné konfiguraci nabízí možnost osazení
volitelného integrovaného obvodu na pozici **U9**. V oficiální
dokumentaci se toto rozšíření označuje jako **GPE Option** (*GPIO Port
Expander*). Srdcem tohoto rozšíření je 16bitový I/O expandér
**MCP23017** komunikující přes sériovou sběrnici $I^{2}C$.

Pokud čip na pozici U9 osazen není, zůstává 20pinový lištový konektor
**J7 (GPIO)** na desce nefunkční. Piny konektoru J7 totiž nevedou přímo
k procesoru Motorola MC68008, ale jsou připojeny výhradně na brány čipu
MCP23017.

## Detekce při startu (IOS Boot)

Během inicializace systému řídicí mikrokontrolér Microchip PIC18F47Q10
(I/O Subsystem -- IOS) automaticky proskenuje interní sběrnici $I^{2}C$
na adrese `0x20`. Pokud čip MCP23017 odpoví, vypíše bootloader na
terminálu zprávu:

``` text
IOS: Found GPE Option
```

Přítomnost této zprávy potvrzuje, že je obvod správně napájen, pull-up
rezistory na $I^{2}C$ sběrnici fungují a konektor J7 je připraven k
použití.

# MCP23017

Pposkytuje celkem 16 volně programovatelných digitálních
vstupně-výstupních pinů rozdělených do dvou 8bitových portů:

-   **Port A (GPA0 až GPA7):** 8 bitů přístupných samostatnými příkazy.

-   **Port B (GPB0 až GPB7):** 8 bitů přístupných samostatnými příkazy.

Každý jednotlivý pin obou portů lze nezávisle nakonfigurovat jako
**vstupní** nebo **výstupní**. Při konfiguraci pinu jako vstupu umožňuje
čip aktivovat vnitřní slabý pull-up rezistor (cca $100k\Omega$), což
eliminuje nutnost zapojovat vnější rezistory při připojování tlačítek,
spínačů nebo joysticků spínajících proti zemi (GND).

## Principy komunikace skrze Virtual I/O Engine

Procesor Motorola MC68008 neřídí čip MCP23017 přímým bitbangingem po
sběrnici $I^{2}C$ Veškerou nízkoúrovňovou komunikaci s $I^{2}C$
sběrnicí přebírá mikrokontrolér PIC (IOS). Motorola pouze posílá
vysokohmotnostní řídicí příkazy (Opcodes) na paměťové porty IOS:

-   Zápis příkazu na adresu **`0xFFFFD`** (`STRPT` -- Store Opcode)
    určuje, jakou operaci má IOS s čipem MCP23017 provést.

-   Následný zápis nebo čtení na adrese **`0xFFFFC`** (`EXWRPT` /
    `EXRDPT`) předá nebo načte datový bajt.



|                      |                |                |                                                |
|-------------|-----------|-----------|--------------------------------------|
| **Příkaz / Registr** | **Adresa Hex** | **Opcode Hex** | **Funkce a význam operace**                    |
| WRGPA                | `0xFFFFD`      | `0x03` (`$03`) | Zápis datového bajtu na Port A (GPA0--GPA7)    |
| WRGPB                | `0xFFFFD`      | `0x04` (`$04`) | Zápis datového bajtu na Port B (GPB0--GPB7)    |
| IODIRA               | `0xFFFFD`      | `0x05` (`$05`) | Směr Portu A (Bit: 1 = Input, 0 = Output)      |
| IODIRB               | `0xFFFFD`      | `0x06` (`$06`) | Směr Portu B (Bit: 1 = Input, 0 = Output)      |
| GPPUA                | `0xFFFFD`      | `0x07` (`$07`) | Aktivace Pull-Up pro Port A (Bit: 1 = Zapnuto) |
| GPPUB                | `0xFFFFD`      | `0x08` (`$08`) | Aktivace Pull-Up pro Port B (Bit: 1 = Zapnuto) |
| RDGPA                | `0xFFFFD`      | `0x81` (`$81`) | Čtení stavu Portu A (GPA0--GPA7)               |
| RDGPB                | `0xFFFFD`      | `0x82` (`$82`) | Čtení stavu Portu B (GPB0--GPB7)               |


## Pinout konektoru J7 (GPIO)

``` text
PIN #       J7 (GPIO)        PIN #
       ----------------------------------
         1        VCC    VCC          2
         3       GPB0    GPA7         4
         5       GPB1    GPA6         6
         7       GPB2    GPA5         8
         9       GPB3    GPA4        10
        11       GPB4    GPA3        12
        13       GPB5    GPA2        14
        15       GPB6    GPA1        16
        17       GPB7    GPA0        18
        19        GND    GND         20
       ---------------------------------
```

# Obsluha v Enhanced 68k BASICu

Pro správné použití jakéhokoliv pinu na konektoru J7 je nutné nejprve
provést **inicializaci**: nastavit směr pinu (registry `IODIRA` /
`IODIRB`) a v případě vstupního pinu zapnout interní pull-up rezistory
(`GPPUA` / `GPPUB`).

## Konfigurace pinů a rozsvícení LED na GPA5

Následující ukázka nastaví pin **GPA0** (Pin 18 konektoru J7) jako vstup
s Pull-Up rezistorem a pin **GPA5** (Pin 8 konektoru J7) jako výstup, na
kterém následně rozsvítí LED diodu (zapíše bit 5 neboli hodnotu `$20` =
32).

``` basic
10 REM --- Inicializace a rizeni GPIO pinů ---
20 EXWRPT = $FFFFC : STRPT =$FFFFD
30 REM GPA0 (bit 0) je Vstup (1), ostatni piny Vystup (0) -> maska $01
40 POKE STRPT, 5 : POKE EXWRPT, $01 : REM Opcode 5 = IODIRA
50 REM Zapnuti vnitrniho Pull-Up na GPA0 -> maska $01
60 POKE STRPT, 7 : POKE EXWRPT, $01 : REM Opcode 7 = GPPUA
70 REM Rozsviceni LED pripojene na GPA5 (bit 5 neboli $20 = 32)
80 POKE STRPT, 3 : POKE EXWRPT, $20 : REM Opcode 3 = WRGPA
90 PRINT "LED na pinu GPA5 rozsvicena."

```

## Tlačítko na GPA0 ovládá LED na GPA5

V této ukázce tlačítko připojené na **GPA0** spíná proti zemi (`GND`).
Při stisku tlačítka se na pinu objeví logická `0`. Kód čte stav celého
Portu A, invertuje hodnotu bitu 0 a podle stisku rozsvěcí nebo zhasíná
LED na pinu **GPA5**.

``` basic
10 REM --- GPIO Zvonek: Stisk GPA0 rozsviti LED na GPA5 ---
20 EXWRPT = $FFFFC : STRPT = $FFFFD : EXRDPT =$FFFFC
30 POKE STRPT, 5 : POKE EXWRPT, $01 : REM GPA0 = Vstup (IODIRA)
40 POKE STRPT, 7 : POKE EXWRPT, $01 : REM GPA0 = Pull-Up (GPPUA)
50 REM --- Hlavni obnovovaci smycka ---
60 POKE STRPT, $81                 : REM Opcode $81 = RDGPA (Cteni Portu A)
70 V = PEEK(EXRDPT)                : REM Cteni stavu portu
80 IF (V AND 1) = 0 THEN GOTO 110  : REM Pokud je na GPA0 hodnota 0 (stisk)
90 POKE STRPT, 3 : POKE EXWRPT, 0  : REM Zhasnout LED na GPA5
100 GOTO 60
110 POKE STRPT, 3 : POKE EXWRPT, $20: REM Rozsvitit LED na GPA5 (bit 5)
120 GOTO 60

```

## Čtení 8bitového stavu z Portu A (joystick)

Při připojení 5tlačítkového retro joysticku (4 směry + tlačítko FIRE
spínající proti `GND`) na piny **GPA0 až GPA4** stačí nastavit spodních
5 bitů Portu A jako vstupy a v cyklu vyčítat stav portu:

``` basic
10 REM --- Cteni 8-bitoveho stavu Portu A ---
20 EXWRPT = $FFFFC : STRPT = $FFFFD : EXRDPT =$FFFFC
30 POKE STRPT, 5 : POKE EXWRPT, $1F : REM Spodnich 5 bitu jako Vstup (IODIRA)
40 POKE STRPT, 7 : POKE EXWRPT, $1F : REM Zapnout Pull-Up na GPA0-GPA4 (GPPUA)
50 REM --- Smycka cteni ---
60 POKE STRPT, $81                  : REM Opcode $81 = RDGPA
70 RAW = PEEK(EXRDPT)               : REM Načtení surovych dat
80 STAV = (255 - RAW) AND $1F       : REM Invertovani (stisk = 1) a orez
90 PRINT "Stav vstupnich pinu GPA0-GPA4: "; STAV
100 FOR I = 1 TO 200 : NEXT I        : REM Cekaci prodleva
110 GOTO 60

```

# Konektor J4 (AUX)

Konektor **J4 (AUX)** představuje na desce 68k-MBC (revize A091020)
víceúčelový rozšiřující port typu 2×9 pinů. Na
tento konektor vyvedl autor systému přímý přístup k napájení, oběma
sériovým portům mikrokontroléru PIC18F47Q10 (SER1 a SER2) i ke sběrnici
$I^{2}C$.

Díky tomuto portu lze k počítači připojit druhý sériový terminál, Wi-Fi
modem (ESP8266/ESP32), sériovou tiskárnu, externí USB převodník nebo
další hardwarové periferie na sběrnici $I^{2}C$.

# Pinout J4 (AUX)

``` text
PIN #              J4 (AUX)              PIN #
       -----------------------------------------------
         1              VCC    MCU_TX2_TTL         2
         3              VCC    MCU_TX2_USB         4
         5              SDA    MCU_RX2_TTL         6
         7              SCL    VUSB2               8
         9              GND    GND                10
        11              GND    GND                12
        13    MCU_TX1_RS232    MCU_TX2_RS232      14
        15    MCU_RX1_RS232    MCU_RX2_RS232      16
        17              GND    GND                18
       -----------------------------------------------------------
```

# Funkční skupiny signálů

Piny konektoru J4 tvoří:

1.  **Sériový port 2 v TTL logice (Piny 2, 4, 6, 8):** Umožňují připojit
    sekundární sériovou linku s napěťovými úrovněmi $0V~|~5V$ (TTL).
    Ideální pro přímé připojení USB-TTL adaptérů (CP2102, FT232), Wi-Fi
    modulů ESP8266/ESP32 nebo mikrokontrolérů Arduino/Pico.

2.  **RS232 Rozhraní pro SER1 a SER2 (Piny 13, 14, 15, 16):** Tyto piny
    vedou přímo z integrovaného budiče RS232 na desce. Umožňují připojit
    klasická historická zařízením s rozhraním RS232 (například terminály
    DEC VT510/VT520, sériové tiskárny nebo externí modemy) bez nutnosti
    externího MAX232 převodníku.

3.  **Sběrnice $I^{2}C$ (Piny 5, 7):** Přímý přístup k systémové
    sběrnici $I^{2}C$ pro připojení dodatečných senzorů, OLED displejů
    nebo dalších $I^{2}C$ periferií.

