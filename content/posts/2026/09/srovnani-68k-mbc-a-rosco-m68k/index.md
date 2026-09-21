---
title: "Srovnání 68k-MBC a Rosco_m68k"
date: 2026-08-27T18:31:29+02:00
cover:
    image: "m68010.webp"
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

### Proč stavíme homebrew počítače a kouzlo Motoroly 68k

{{< obr600 "m68010.webp" "" >}}

## Návrat k hardwarovým kořenům (Bare metal)

Žijeme v éře bezprecedentní výpočetní abstrakce. Od hardwaru nás dnes
dělí mikrokód, operační systém, virtuální stroje, kontejnery a
vysokoúrovňové běhové prostředí. Ačkoliv je tento vrstvený přístup
nezbytný pro moderní vývoj softwaru, zcela izoluje vývojáře od
základních principů fungování počítače.

Stavba "homebrew" (po domácku vyráběných) počítačů je reakcí na tuto
nepřehlednost. Jde o touhu porozumět počítači do posledního bitu,
adresního pinu a hodinového taktu. Na vlastnoručně postaveném počítači
víte přesně, co se děje, když se CPU resetuje, jak paměť odpovídá na
požadavky a jak se přes I/O porty rozsvěcují LED diody. Je to absolutní
kontrola, která spojuje svět elektroniky a nízkoúrovňového programování.

## Proč právě Motorola 68000?

Zatímco 8bitovým homebrew počítačům kralují procesory Z80 a 6502,
přechod do 16/32bitové éry má jediného nekorunovaného krále: procesor
Motorola 68000 (zkráceně M68k nebo 68k). Tento čip formoval 80. a 90.
léta, kdy poháněl legendární stroje jako Commodore Amiga, Atari ST,
původní Apple Macintosh nebo konzoli Sega Mega Drive.

Mezi bastlíři a vývojáři je 68k oblíbený z několika klíčových důvodů:

-   **Elegance instrukční sady:** Na rozdíl od archaické a segmentované
    architektury x86 (Intel 8086), Motorola 68000 nabídla nádherně
    ortogonální instrukční sadu, která je pro programátora v asembleru
    radostí.

-   **32bitové srdce:** Ačkoliv má původní 68000 16bitovou datovou a
    24bitovou adresní sběrnici (fyzicky), uvnitř pracuje s 32bitovými
    daty a registry.

-   **Lineární adresní prostor:** Adresování až 16 MB paměti probíhá
    zcela plynule, bez nutnosti používat segmenty a offsety.

-   **Osm datových a osm adresních registrů (D0-D7, A0-A7):** Nabízejí
    obrovskou flexibilitu, která na svou dobu připomínala spíše sálové
    počítače.

Díky těmto vlastnostem představuje rodina 68k ideální mezistupeň pro ty,
kterým už 8bitové procesory nestačí, ale nechtějí se pouštět do zbytečně
komplikovaných moderních architektur.

# Odlišné přístupy
**68k-MBC a Rosco_m68k**

Zatímco cíl je stejný (oživit Motorolu 68000 na stole), cesty, jak toho
dosáhnout, se zásadně liší. Dva populární projekty dneška -- **68k-MBC**
a **Rosco_m68k** -- reprezentují dva zcela protichůdné inženýrské
přístupy k homebrew komunitě.

## 68k-MBC: Moderní minimalismus a chytrá emulace

Projekt 68k-MBC (Multi Board Computer), za nímž stojí vývojář známý jako
Just4Fun, představuje tzv. hybridní přístup. Cílem je minimalizovat
počet součástek, zjednodušit návrh desky plošných spojů (PCB) a umožnit
rychlé zprovoznění bez potřeby specializovaného vybavení (např.
programátoru EPROM).

**Klíčové vlastnosti:**

-   **PIC jako mozek desky:** Vedle samotného CPU M68008 (verze 68000 s
    8bitovou vnější sběrnicí) a čipu SRAM se nachází moderní
    mikrokontrolér PIC.

-   **Zavádění místo ROM:** Deska vůbec neobsahuje fyzický čip ROM. Po
    zapnutí mikrokontrolér PIC převezme kontrolu nad sběrnicí a "nasype"
    bootloader přímo do SRAM, ze které pak CPU startuje.

-   **Emulace periferií:** PIC zároveň emuluje sériovou linku, I/O
    operace a diskové úložiště (SD kartu).

-   **Výhody:** Extrémní jednoduchost stavby (jen 3 integrované obvody),
    nízká cena, okamžitá funkčnost z výroby (stačí nahrát firmware do
    PIC přes běžné USB rozhraní).
    
{{< obr600 "mbc.webp" "68k-MBC" >}}

## Rosco_m68k: Čistokrevné retro a hardwarová rozšiřitelnost

Na opačné straně spektra stojí projekt Rosco_m68k, jehož hlavním autorem
je Ross Bamford. Tento projekt se drží klasických zásad návrhu počítačů
z 80. let. Nespokojí se s tím, že CPU běží -- chce, aby k němu byly
připojeny autentické obvody té doby.

**Klíčové vlastnosti:**

-   **Diskrétní glue-logika a ROM:** Počítač startuje kód z fyzických
    EPROM/EEPROM čipů a adresní dekódování obstarávají obvody rodiny
    74LS (nebo programovatelná logika GAL/ATF).

-   **Opravdové periferie:** Pro sériovou komunikaci (UART) se používají
    klasické čipy jako MC68681, případně modernější ale stále klasické
    UARTy.

-   **Rozšiřující sběrnice:** Srdcem Rosco_m68k je masivní
    rozšiřitelnost. Obsahuje sloty, do kterých se dají zapojit grafické
    karty (často využívající čipy z MSX), zvukové karty (Yamaha YM2149)
    nebo řadiče IDE.

-   **Výhody:** Nabízí plný zážitek z návrhu hardwaru. Vývojář si osahá
    dekódování adres, časování sběrnice a hardwarová přerušení bez
    jakýchkoliv "švindlů" pomocí mikrokontrolérů.

{{< obr600 "rosco.webp" "Rosco_m68k, bus board, RAM expansion board" >}}

# Který vybrat?

Výběr mezi 68k-MBC a Rosco_m68k se odvíjí od toho, jaký cíl při stavbě
homebrew počítače sledujete.

> Pokud vás láká samotný **mikroprocesor Motorola 68000 z pohledu
softwaru**, chcete se naučit jeho krásný asembler, spouštět CP/M-68K,
psát vlastní malý OS, ale nezajímá vás tolik pájení a složitosti
adresního dekódování, pak je **68k-MBC** jasnou volbou. Představuje
nejrychlejší cestu, jak mít "bare metal" 68k na stole funkční během
jednoho večera.\
\
Je to hotové řešení, všechny dostupné programy jsou odladěné a použitelné.
Tedy nejen pro bare-metal programování. BASIC, CP/M-68K, PASCAL, ASSEMBLER, C

> Na druhou stranu, pokud je pro vás cesta samotným cílem a chcete
**pochopit, jak byly stavěny počítače v éře Amigy**, pak neexistuje
lepší volba než **Rosco_m68k**. Tento systém vás donutí pochopit, co to
znamená "Bus Error", jak se implementují hardwarová přerušení s čipem
UART a poskytne vám modulární platformu, kterou můžete rozšiřovat po
celé roky (například o vlastní videokartu).\
\
Většina hardwarových rozšíření nebo portů operačních systémů je pouze
v režimu testování. Dokonale odladěný je snad jen toolchain
pro bare-metal programování.

# Detailní zaměření: 68k-MBC

Abychom plně pochopili genialitu, ale i kompromisy projektu 68k-MBC,
musíme se podívat na jeho architekturu zblízka. Srdcem tohoto počítače
není klasická Motorola 68000, ale její varianta **M68008**. Tento čip je
softwarově 100% kompatibilní se svým větším bratrem, ale hardwarově
disponuje pouze 8bitovou externí datovou sběrnicí. To drasticky snižuje
počet spojů na desce a umožňuje spárovat procesor s jediným paměťovým
čipem SRAM.

Druhým pilířem systému je mikrokontrolér z rodiny PIC (typicky
PIC18F47Q10). Tento moderní obvod slouží jako "strážce" celého systému.
Zajišťuje generování hodinového signálu, obstarává sériovou komunikaci
(UART), simuluje diskový řadič pomocí modulu pro SD karty a hlavně při
startu počítače zastupuje paměť ROM.

Tento silně asymetrický design s sebou přináší specifické klady i
zápory.

## Výhody 68k-MBC

-   **Extrémní jednoduchost stavby:** Deska obvykle obsahuje jen tři
    hlavní integrované obvody (CPU, SRAM, PIC) a pár diskrétních
    součástek. Není zde žádná "hustá" změť logických obvodů řady 74xx
    pro dekódování adres.

-   **Absence programátoru EPROM:** Bastlíři často narážejí na to, že
    pro retro počítače potřebují staré UV mazatelné paměti EPROM a k nim
    příslušný programátor. U 68k-MBC tento problém zcela odpadá.
    Firmware leží v mikrokontroléru PIC, který ho při každém zapnutí
    bleskově nakopíruje (DMA stylem) do paměti SRAM a teprve poté uvolní
    CPU z resetu.

-   **Nízká cena a kompaktnost:** Díky malému počtu součástek je počítač
    levný a vejde se na PCB o velikosti zhruba balíčku karet.

-   **Okamžitá užitná hodnota ("Out of the box"):** Po složení a nahrání
    firmware máte okamžitě přístupný zavaděč a systém CP/M-68K bootující
    z SD karty. Pro softwarově orientovaného nadšence je to splněný sen
    -- může rovnou začít psát v asembleru nebo kompilovat C kód.

## Nevýhody 68k-MBC

-   **Ztráta autentického hardwarového zážitku:** Pro hardwarové puristy
    je tento přístup tak trochu "podváděním". Tím, že PIC emuluje
    podstatnou část systému, přichází stavitel o radost z navrhování
    skutečné počítačové architektury z 80. let.

-   **Omezená rozšiřitelnost:** Mikrokontrolér řídí prakticky vše. Pokud
    byste chtěli k 68k-MBC připojit tradiční grafický čip, zvukovou
    kartu nebo vlastní hardwarové periferie, narazíte na zásadní
    omezení. Neexistuje zde žádná volně přístupná, plnohodnotná
    rozšiřující sběrnice jako u projektu Rosco_m68k.

-   **Rychlostní limity (Úzké hrdlo):** Procesor M68008 s 8bitovou
    sběrnicí potřebuje ke načtení jedné 32bitové instrukce čtyři
    přístupy do paměti, což jej přirozeně zpomaluje oproti plnohodnotné
    16bitové Motorole 68000. Komunikace s periferiemi (například I/O
    požadavky), kterou obsluhuje PIC, může rovněž trpět latencí
    způsobenou softwarovou emulací v mikrokontroléru.

# Závěr

Výběr mezi 68k-MBC a Rosco_m68k se odvíjí od toho, jaký cíl při stavbě
homebrew počítače sledujete.

Pokud vás láká samotný **mikroprocesor Motorola 68000 z pohledu
softwaru**, chcete se naučit jeho krásný asembler, spouštět CP/M-68K,
psát vlastní malý OS, ale nezajímá vás tolik pájení a složitosti
adresního dekódování, pak je **68k-MBC** jasnou volbou. Představuje
nejrychlejší cestu, jak mít "bare metal" 68k na stole funkční během
jednoho večera.

Na druhou stranu, pokud je pro vás cesta samotným cílem a chcete
**pochopit, jak byly stavěny počítače v éře Amigy**, pak neexistuje
lepší volba než **Rosco_m68k**. Tento systém vás donutí pochopit, co to
znamená "Bus Error", jak se implementují hardwarová přerušení s čipem
UART a poskytne vám modulární platformu, kterou můžete rozšiřovat po
celé roky (například o vlastní videokartu).

# Softwarová výbava a operační systémy

## 68k-MBC: Znovuzrození CP/M-68K

Zatímco 8bitový svět zná klasické CP/M jako své boty, jeho 16/32bitový
nástupce pro architekturu Motorola 68000 je poněkud exotičtější a v
komerční sféře byl rychle zastíněn DOSem. Na počítači 68k-MBC je však
spuštění operačního systému **CP/M-68K** (často ve verzi 1.3) naprosto
přímočaré a představuje primární způsob, jak tento počítač využívat.

Celé kouzlo spočívá v tom, že mikrokontrolér PIC, který obstarává
systémové I/O operace, zprostředkovává přístup k SD kartě ve formě
virtuálních pevných disků. CP/M-68K z nich po startu bez problémů
nabootuje a rázem promění "holou desku" ve funkční vývojovou stanici.

**Co tento systém vývojáři nabízí?**

-   **Nativní vývoj na platformě:** Díky dostupnosti legendárního
    kompilátoru **Alcyon C** (zahrnující sadu nástrojů jako `CP68`,
    `C068`, `C168`, `AS68`, `LO68`) a interpretu **Enhanced 68k BASIC**
    není nutné spoléhat výhradně na křížovou kompilaci (cross-compiling)
    na moderním PC. Programy lze psát a kompilovat přímo na cílovém
    retro hardwaru.

-   **Terminálové aplikace a hry:** Protože veškerý grafický a textový
    výstup probíhá přes sériovou linku, otevírá se prostor pro tvorbu
    aplikací využívajících standardní ANSI/VT100 escape sekvence.

## Rosco_m68k: Od bare-metal vývoje po EmuTOS

Filozofie systému Rosco_m68k směřuje jinam. Z výroby (resp. po sestavení
desky) se stroj chová primárně jako **bare-metal** (čistě hardwarová)
platforma. V ROM je uložen zavaděč a jednoduchý monitor, který vývojáři
umožňuje posílat přeložený kód ve formátu S-Record (SREC) přes sériovou
linku přímo do systémové RAM a následně jej spustit.

Tento přístup je absolutně ideální pro psaní hardwarově orientovaného
softwaru. Běžně je do desky Rosco osazován vylepšený procesor **Motorola
MC68010**, který přináší výhodu v podobě registru VBR (Vector Base
Register). Ten umožňuje přesouvat tabulku vektorů přerušení kamkoliv do
paměti (nikoliv jen na adresu nula jako u 68000), což je pro vývoj
operačních systémů stěžejní. Ve spojení s kapacitou paměti 1MB na desce
a možností rozšiřujících modulů, tvoří systém dokonalé pískoviště pro
psaní nízkoúrovňových diagnostik paměti v C/Assembly či vlastních
ovladačů.

Pokud však na Rosco_m68k toužíte po plnohodnotném operačním systému,
architektura umožňuje spustit hned několik řešení:

-   **EmuTOS:** Jde o pravděpodobně nejpopulárnější volbu pro otevřené
    systémy na bázi 68k. Jedná se o open-source implementaci operačního
    systému známého z počítačů Atari ST. Ať už přes sériový terminál
    nebo s patřičnou rozšiřující grafickou kartou, Rosco tím získá
    robustní OS s vynikající podporou souborového systému FAT.

-   **CP/M-68K:** Stejně jako na 68k-MBC, i zde je možné spustit CP/M.
    Rozdíl je v tom, že pro Rosco je nutné napsat (či zkompilovat)
    reálný BIOS (CBIOS) obsluhující fyzické čipy na desce -- tedy
    hardwarový UART (např. MC68681) a řadiče pevných disků na
    rozšiřující sběrnici, nikoliv jen posílat instrukce podpůrnému
    mikrokontroléru.

-   **uClinux:** Přestože klasické linuxové jádro vyžaduje jednotku pro
    správu paměti (MMU), kterou standardní řada 68000/68010 nedisponuje,
    varianta uClinux navržená právě pro "MMU-less" architektury je na
    Rosco teoreticky (a komunitně i prakticky) proveditelná, vyžaduje
    pouze dostatečnou kapacitu RAM a podporu pro úložný prostor.

# Proč píšeme bare-metal programy
**Hledání limitů**

Pokud už máme funkční hardware a možnost nahrát do něj operační systém,
nabízí se logická otázka: Proč se mnozí vývojáři vrací k programování
typu "bare-metal", tedy k psaní kódu běžícího přímo na hardwaru bez
jakékoliv vrstvy operačního systému?

Odpověď leží v touze po absolutní kontrole a v inženýrské výzvě, kterou
představuje hledání skutečných limitů dané architektury. Bez operačního
systému neexistuje žádné plánování procesů, žádné skryté kontextové
přepínání a žádná ochrana paměti. Celých 100 % strojového času patří
vašemu kódu.
