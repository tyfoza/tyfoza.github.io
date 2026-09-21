---
title: "USB Hub Controller"
date: 2026-08-18T23:49:17+02:00
cover:
    image: ""
tags: ["Bastlení"]
draft: true
---

## Programově ovládáných deset USB portů.

*Typické využití* – máme server a chceme udělat denní zálohu, každou zálohu na jiný disk tak, aby byl připojený vždy pouze jeden z nich. Tento přístup poslouží třeba jako ochrana proti kybernetickému útoku (rasomware). Můžeme připojit nebo odpojit libovolný port. Lze komunikovat po USB nebo šifrovaně po wifi. Podporuje autonomní režim s plánovačem, kdy se porty připojují a odpojují podle týdenního plánu.

Doporučuji přečíst [dokumentaci](https://drive.google.com/file/d/1gvB18aNZMbGMnJ-kNCbxrWGPMEXKvrJV/view?usp=drive_link) celého ovládání, kde je vše potřebné. Článek tady na blogu se věnuje tvorbě funkčního prototypu.

Celé řešení [ke stažení](https://drive.google.com/drive/folders/12ns49WnBjIt_Di5GOzrGpgCpxaej0EIu?usp=drive_link) – firmware pro mikrokontroler, řídící programy v Pythonu 

## Zadání a prvotní zámysl
Máme deset ručně spínaných portů USB 3 hubu. Chceme nahradit mechanická tlačítka elektronickým spínáním. To znamená nějaké spínací prvky a mikrokontrolér, který to bude řídit. Existují spínané HUBy s jiným počtem portů (8–16). 

Určitě bude potřeba robuství spínání, tedy pokud má server mít disk připojený desítky hodin, nechceme jen držet sepnutý pin MCU, což by v případě pádu programu v mikrokontroleru nebo nahrání nového firmware znamenalo možné selhání. 

Spínací prvek musí dostat infomace o tom, co sepnout; na dotaz podat informaci o tom, co je připojeno. Také bude potřeba nějaký scheduler, týdenní plánovač – což znamená, že mikrokontroler musí znát přesný čas.

## Spínací portů
Víme, že tlačítko propojí napájení konkrétního portu s 5V napájením,  potřebujeme spínání v kladné větvi napájení (high-side).

{{< obr400 "spinani.webp" "P-MOSFET musí snést stálou zátěž nejméně 900mA" >}}

### Spínací prvek 
První, co mě napadlo bylo řešení pomocí logických hradel, kdy každý port bude mít svůj RS latch a bude jako paměťová buňka. Adresace pomocí dekodéru/demultiplexeru. Nebo posuvný registr, který by řídil spínání. Tuto úvahu jsem opustil a našel hotové řešení.

### MCP23017 I²C expander
MCP23017 [datasheet](https://cz.mouser.com/datasheet/3/282/1/MCP23017-Data-Sheet-DS20001952.pdf), dostupný i jako hotový modul [[1](https://www.laskakit.cz/laskakit-mcp23017-i2c-16-bit-i-o-expander/)].  Tento čip řeší celý problém spínání instantním způsobem.

Při zapnutí napájení má nastavené piny jako vstupní a jsou ve stavu vysoké impedance, tedy odpojené, takže se žádný z USB portů sám nepřipojí. Navážeme komunikaci, přečteme stav registru, upravíme bitovou operací, zapíšeme do registru.

**Registry**
- `IODIRA (0x00)` a `IODIRB (0x01)` určují směr komunikace, používáme je pouze jako výstupní (zapíšeme nuly).
- `OLATA(0x14)` a `OLATAB (0x15)` na nastavení, který pin má být sepnut.
- `GPIOA (0x12)` a `GPIOB (0x13)` jsou datové registry, kde přečteme stav jakou logickou úroveň máme na kterém pinu

### Logika řízení
Celé to musí být především univezální a přehledné. Pošleme příkaz v textovém formátu JSON, který se dobře parsuje. Program příkaz zpracuje a podle něj se zachová. Připojí USB port zvoleného čísla, vrátí aktuální stav připojených portů, přidá nebo upraví pravidlo scheduleru.

Vybral jsem mikrokontrolér Seeed Studio XIAO ESP32C3 [[2](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)], má USB-C a wifi s externí anténou. 
   
### Přesný čas
Plánovač i šifrovaná komunikace vyžaduje, aby mikrokontrolér znal přesný čas. Dá se to vyřešit připojením do wifi a synchronizaci času z NTP serverů. 

Zároveň necháváme možnost, že pokud je na I²C sběrnici osazen hardwarový RTC modul (DS3231) se záložní baterií, mikrokontrolér s ním automaticky komunikuje a synchronizuje se z něj.  Časová zóna včetně přechodů na letní čas je pevně definována ve zdrojovém kódu (`Config.h`) pomocí POSIX formátu, tedy problém letního času vyřešen. 

## Komunikace s mikrokontrolerem 
Veškerá komunikace mezi řídicím serverem a Hubem probíhá výhradně ve formátu JSON. Každý
požadavek musí obsahovat klíč "cmd", který definuje typ příkazu. Při vzdálené šifrované
komunikaci přes WiFi je nutné do `JSON` požadavku vždy přidat i klíč `"t"` nesoucí aktuální UNIX čas.

Zabezpečení WiFi (AES-128-CBC)
Vyřešit zabezpečení komunikce po wifi bylo nejobtížnější část celé řešení.
 
Zatímco lokální USB komunikace probíhá po vyhrazeném kabelu v čistém textu, bezdrátová síť
vyžaduje robustní šifrování. Tím je zamezeno jakémukoliv odposlechu stavu záložních disků nebo podvržení povelu k jejich neautorizovanému připojení. Zařízení používá symetrickou šifru AES se 128bitovým klíčem v režimu CBC (Cipher Block Chaining).

### Mechanismus šifrování a odesílání paketů:
1. Klientský skript (např. Python) vygeneruje náhodný 16bajtový inicializační vektor `IV`.
2. JSON požadavek je doplněn o výplň (Padding) na násobek 16 bajtů.
3. Data jsou zašifrována přes `AES-128-CBC` pomocí sdíleného hesla.
4. Vygenerovaný `IV` (16 bajtů) je vložen přímo před samotnou zašifrovanou zprávu.
5. Celý tento binární blok je zakódován do formátu `Base64`.
6. Výsledný Base64 řetězec je odeslán jako prostý text v těle `HTTP POST` požadavku na
adresu `http://<IP_ESP32>/api`.
7. Zařízení zprávu dešifruje, zpracuje úkol a stejným postupem zašifruje odpověď s využitím
nově vygenerovaného `IV`.

### Ochrana proti Replay útokům a časová synchronizace
Obsahuje striktní ochranu proti zachycení a opětovnému odeslání paketu útočníkem
(Replay Attack). Příchozí JSON paket je po přijetí dešifrován a zadaná hodnota časového razítka `"t"` je porovnána s interním časem mikrokontroléru. Tento interní čas je udržován
synchronizovaný přes NTP nebo pomocí hardwarového RTC modulu.

Pokud se zaslaný čas v paketu liší od systémového času hardwaru o více než 30 vteřin, je
požadavek okamžitě zahozen. Klientovi je v takovém případě vrácena chyba s `HTTP kódem 401
Unauthorized`. Tím je hardwarově zaručeno, že i když potenciální útočník zachytí platný paket pro sepnutí napájení k zálohovacímu disku, nebude ho moci použít v budoucnu k připojení USB portu.

###  Struktura firmware
Program[[3](https://drive.google.com/drive/folders/1mDqF-dsXtVTMLXUQNC1ASDGscrrDJMwJ?usp=drive_link)] pro XIAO ESP32-C3 je napsaný v Arduino IDE, což považuju za dostupnější než ESP-IDF.

#### `HubController.ino`
Hlavní vstupní bod programu. V metodě `setup()` inicializuje veškeré hardwarové a softwarové moduly (I2C sběrnici pro RTC a expandér, plánovač a WiFi rádio). V nekonečné smyčce `loop()` pak zajišťuje jejich periodickou aktualizaci a udržuje běh celého systému. Zároveň přímo zde dochází k naslouchání na sériové lince a zachytávání JSON příkazů poslaných po USB kabelu.

 
#### `Config.h`
Globální konfigurační hlavičkový soubor. Zde se definují pevné parametry zařízení, které nelze měnit za běhu. Zejména se jedná o maximální počet podporovaných portů (`MAX_PORTS`) a
`POSIX` definici časové zóny (včetně automatického přechodu na letní čas), podle které systém počítá časy pro plánovač. Dále se zde nachází makro `ENABLE_DEBUG`, jehož odkomentováním lze zapnout diagnostické výpisy na sériovou linku (např. odesílané přes `DEBUG_PRINT`).

#### `ApiParser.h / ApiParser.cpp`
Komunikační mozek aplikace. Slouží k rozbalení (deserializaci) přijatých JSON řetězců (již po odstranění případného WiFi šifrování). Analyzuje obsah podle klíče "cmd", validuje parametry a volá výkonné funkce ostatních modulů (např. zapnutí portu, uložení pravidla do Cronu, smazání flash paměti). Sestavuje finální strukturované JSON odpovědi o úspěchu či chybě.

#### `WifiManager.h / WifiManager.cpp`
Obsluhuje bezdrátovou síť a bezpečnost na LwIP (Lightweight IP) síťové vrstvě. Řídí připojování k wifi (s nutnou 8 vteřinovou prodlevou proti zablokování routerem) a provozuje HTTP server na portu 80. Zajišťuje nastavení DHCP, nebo ruční zadání statické IP adresy, brány a DNS. Dále obsahuje kompletní kryptografický aparát využívající mbedtls knihovny (šifrování AES-128-CBC) a logiku pro ochranu před opakovanými (Replay) útoky kontrolou časových razítek. Údaje o síti si ukládá do do NVS paměti.

#### `TimeManager.h / TimeManager.cpp`
Zajišťuje absolutní přesnost času v unixovém formátu, která je nezbytná pro plánovač a
bezpečnostní časová razítka. Inicializuje komunikaci s hardwarovým RTC modulem DS3231
přes sběrnici I2C. Poku je připojen k WIFI, tak se pravidelně dotazuje na definované NTP servery a pokud dojde k synchronizaci s internetem, automaticky provede rekalibraci času i na hardwarovém RTC modulu.

#### `CronScheduler.h / CronScheduler.cpp`
Autonomní plánovač úloh. Zpracovává pole pravidel a stará se o jejich persistenci do nevolatilní NVS paměti (pravidla tak přežijí i restart po výpadku napájení). Každé pravidlo získá své unikátní ID. Manažer pravidelně, každou minutu, porovnává systémový čas s maskou nastavených dnů a hodin. Při shodě provede zadanou akci na příslušném portu.

#### `HardwareManager.h / HardwareManager.cpp`
Hardwarová abstrakční vrstva řídící fyzické přepínání portů. Skrze sběrnici I2C komunikuje s port expandérem MCP23017. Při startu okamžitě vnutí portům bezpečný počáteční stav (LOW, tedy vypnuto). Udržuje si přehled nad aktuálním stavem jednotlivých bran (Bank A, Bank B) a řeší nízkoúrovňový bitový zápis registrů v expandéru. Obsahuje také metodu `checkConnection()` pro rychlou diagnostiku, zda port expandér komunikuje (odpovídá znakem ACK) na své adresní lince.

## Řízení pomocí Python skriptů
Můžeme použít skript, který pošle konkrétní příkaz[[4](https://drive.google.com/drive/folders/1iRd9q9VJYnxcu2NKaZylTxHXIhkqcBWq?usp=drive_link)] nebo `hub_dahboard.py`, což je jednoduché GUI, kterým můžeme všechno nastavit a řídit

{{< obr600 "gui1.webp" "ruční ovládání portů" >}}
{{< obr600 "gui2.webp" "nastavení plánovače" >}}
{{< obr600 "gui3.webp" "reset do továního nastavení smázne vše a nastaví komunikaci po USB" >}}