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
Můžeme použít skript, který pošle konkrétní příkaz[[4](https://drive.google.com/drive/folders/1iRd9q9VJYnxcu2NKaZylTxHXIhkqcBWq?usp=drive_link)] nebo `hub_dahboard.py`, což je jednoduché GUI, kterým můžeme všechno nastavit a řídit. Pro textový terminál je verze `tui_dashboard.py`, která díky knihovně `textual` vypadá totožně; jenom běží v textovém rozhraní.

{{< obr600 "gui1.webp" "ruční ovládání portů" >}}
{{< obr600 "gui2.webp" "nastavení plánovače" >}}
{{< obr600 "gui3.webp" "reset do továního nastavení smázne vše a nastaví komunikaci po USB" >}}


----------

### zde končí článek na blogu
a pokračuje dokumentace, dostupná také jako\
[PDF](https://drive.google.com/file/d/1gvB18aNZMbGMnJ-kNCbxrWGPMEXKvrJV/view?usp=drive_link)

# Referenční manuál a popis API

# Úvod do systému

ESP32-C6 USB Hub Controller je řídicí jednotka navržená pro spolehlivé
fyzické spínání až 10 hardwarových portů. Hlavním případem užití je
automatizované připojení a odpojení externích pevných disků pro bezpečné
zálohování dat. Tím je zajištěno, že záložní disky jsou fyzicky
připojeny (a pod napětím) pouze po dobu provádění zálohy, což
představuje hardwarovou ochranu proti ransomwaru a elektrickému
poškození.

Zařízení podporuje autonomní běh s využitím interního plánovače (Cron) a
volitelného hardwarového modulu reálného času (RTC DS3231).

Zařízení lze ovládat dvěma způsoby:

-   **Lokálně přes USB** (sériová linka, rychlost 115200 baudů) v režimu
    prostého textu.

-   **Vzdáleně přes WiFi** pomocí HTTP POST požadavků se silným
    obousměrným kryptografickým zabezpečením.

# Komunikační vrstva a bezpečnost

## Formát dat

Veškerá komunikace mezi řídicím serverem a Hubem probíhá výhradně ve
formátu `JSON`. Každý požadavek musí obsahovat klíč `"cmd"`, který
definuje typ příkazu. Při vzdálené šifrované komunikaci přes WiFi je
nutné do JSON požadavku vždy přidat i klíč `"t"` nesoucí aktuální UNIX
čas.

## Zabezpečení WiFi (AES-128-CBC)

Zatímco lokální USB komunikace probíhá po vyhrazeném kabelu v čistém
textu, bezdrátová síť vyžaduje robustní šifrování. Tím je zamezeno
jakémukoliv odposlechu stavu záložních disků nebo podvržení povelu k
jejich neautorizovanému připojení. Zařízení používá symetrickou šifru
AES se 128bitovým klíčem v režimu CBC (Cipher Block Chaining).

<div>

**Mechanismus šifrování a odesílání paketů:**

1.  Klientský skript (např. Python) vygeneruje náhodný 16bajtový
    inicializační vektor (IV).

2.  JSON požadavek je doplněn o výplň (Padding) na násobek 16 bajtů.

3.  Data jsou zašifrována přes AES-128-CBC pomocí sdíleného hesla.

4.  Vygenerovaný IV (16 bajtů) je vložen přímo před samotnou
    zašifrovanou zprávu.

5.  Celý tento binární blok je zakódován do formátu Base64.

6.  Výsledný Base64 řetězec je odeslán jako prostý text v těle HTTP POST
    požadavku na adresu `http://<IP_ESP32>/api`.

7.  Zařízení zprávu dešifruje, zpracuje úkol a stejným postupem
    zašifruje odpověď s využitím nově vygenerovaného IV.

</div>

### Ochrana proti Replay útokům a časová synchronizace

Zařízení obsahuje striktní ochranu proti zachycení a opětovnému odeslání
paketu útočníkem (Replay Attack). Příchozí JSON paket je po přijetí
dešifrován a zadaná hodnota časového razítka `"t"` je porovnána s
interním časem mikrokontroléru. Tento interní čas je udržován
synchronizovaný přes NTP nebo pomocí hardwarového RTC modulu.

Pokud se zaslaný čas v paketu liší od systémového času hardwaru o více
než 30 vteřin, je požadavek okamžitě zahozen. Klientovi je v takovém
případě vrácena chyba s HTTP kódem 401 Unauthorized. Tím je hardwarově
zaručeno, že i když potenciální útočník zachytí platný paket pro sepnutí
napájení k zálohovacímu disku, nebude ho moci použít v budoucnu k
připojení do offline úložiště.

# Referenční příručka API

Tato kapitola obsahuje přehled dostupných příkazů API, které obsluhuje
interní parser. Každý příkaz je odesílán jako JSON objekt obsahující typ
operace v klíči `"cmd"` a aktuální UNIX čas v klíči `"t"`.

## API: Ovládání portů a diagnostika

### get_status

Vrací aktuální stavy všech 10 portů a podrobnou diagnostiku připojeného
hardwaru. Slouží k rychlému ověření, zda jsou záložní disky připojeny a
zda nedošlo k selhání na sběrnici.

**Požadavek:**

``` json
{
  "cmd": "get_status",
  "t": 1783867330
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "uptime": 1204,
  "system_time": 1783867330,
  "rtc_connected": true,
  "expander_connected": true,
  "wifi_connected": true,
  "ports": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

### set_port

Provede okamžité fyzické připojení nebo odpojení napájení pro konkrétní
port (záložní disk).

**Požadavek:**

``` json
{
  "cmd": "set_port",
  "port": 1,
  "state": "on",
  "t": 1783867335
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "port":1,
  "state": "on"
  }
```

## API: Plánovač (Cron)

Plánovač umožňuje uložit pravidla pro automatizované spínání do
nevolatilní paměti (NVS). Zálohovací okna tak fungují autonomně. Každé
pravidlo má v paměti přidělené své unikátní ID.

### set_schedule

Vytvoří nové pravidlo.

**Požadavek:**

``` json
{
  "cmd": "set_schedule",
  "port": 1,
  "action": "on",
  "time": "02:00",
  "days": [1, 3, 5],
  "t": 1783867340
}
```

Poznámka: days je pole celých čísel reprezentující dny v týdnu (1 =
Pondělí, 7 = Neděle). Při úspěšném uložení vrátí systém přidělené id
pravidla.

### clear_schedule

Smaže uložené pravidlo na základě jeho unikátního ID.

**Požadavek:**

``` json
{
  "cmd": "clear_schedule",
  "id": 5,
  "t": 1783867345
}
```

### get_schedules

Vrátí seznam všech aktuálně aktivních pravidel uložených v paměti
zařízení. Vrací pole objektů, kde každý prvek obsahuje klíče id, port,
action, hour, minute, a pole days.

např. s pravidly
- id0 port 3 ON v 15:00, každý den
- id1 port 3 OFF ve 21:00, každý den
- id2 port 1 ON v 1:00, pouze v neděli
- id3 port 1 OFF v 9:00, pouze v neděli

**Odpověď:**

``` json
{
  "status": "ok",
  "schedules": [
    {
      "id": 0,
      "port": 3,
      "action": "on",
      "hour": 15,
      "minute": 0,
      "days": [7, 1, 2, 3, 4, 5, 6]
    },
    {
      "id": 1,
      "port": 3,
      "action": "off",
      "hour": 21,
      "minute": 0,
      "days": [7, 1, 2, 3, 4, 5, 6]
    },
    {
      "id": 2,
      "port": 1,
      "action": "off",
      "hour": 1,
      "minute": 0,
      "days": [7]
    },
    {
      "id": 3,
      "port": 1,
      "action": "off",
      "hour": 9,
      "minute": 0,
      "days": [7]
    }
  ]
}

```

## API: Správa sítě

### scan_wifi

Provede aktivní skenování dostupných bezdrátových sítí v okolí. Vzhledem
k povaze rádiového modulu tento příkaz na několik vteřin zablokuje
mikrokontrolér. Vrací pole nalezených SSID.

**Požadavek:**

``` json
{
   "cmd": "scan_wifi",
   "t": 1784064242
 }
  
```

**Odpověď:**

``` json
{
  "status": "ok",
  "networks":["SSID_WIFI_1","SSID_WIFI 2", "SSID_WIFI 3"]
}
```

### set_wifi

**Požadavek:**

``` json
{
  "cmd": "set_wifi",
  "ssid": "Zaloha_Sit",
  "pass": "tajneHeslo123",
  "aes_key": "1234567890123456",
  "enable": true,
  "t": 1783867350
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "message": "WiFi config saved"
}
```

### set_ip_config

nastavení pevné IP adresy

**Požadavek:**

``` json
{
  "cmd": "set_ip_config",
  "dhcp": false,
  "ip": "192.168.1.80",
  "gateway": "192.168.1.1",
  "subnet": "255.255.255.0",
  "dns": "8.8.8.8",
  "t": 1783867355
}
```

zpět k zapnutí automatického přidělení IP adresy

**Požadavek:**

``` json
{
  "cmd": "set_ip_config",
  "dhcp": true, "ip": "",
  "gateway": "",
  "t": 1784064734
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "message": "IP config saved"
}
```

## API: Správa času a systémové příkazy

Přesný čas je kritický pro obranu proti Replay útokům i pro správné
vyhodnocování plánovače záloh. Zařízení získává čas primárně z NTP
serverů. Pokud je na I²C sběrnici osazen volitelný hardwarový RTC modul
(DS3231) se záložní baterií, mikrokontrolér s ním automaticky komunikuje
a synchronizuje se z něj v případě výpadku sítě. Časová zóna včetně
přechodů na letní čas je pevně definována ve zdrojovém kódu (`Config.h`)
pomocí POSIX formátu (např. SEČ/SELČ).

### sync_time

Okamžitě vnutí systému zadaný absolutní UNIX čas, a to nezávisle na NTP.
Tento příkaz je vyjmut z kontroly proti Replay útokům (nevyžaduje
přesnost, sám ji nastavuje). Hodnota je rovnou zapsána i do RTC modulu,
pokud je připojen.

**Požadavek:**

``` json
{
  "cmd": "sync_time",
  "timestamp": 1783867360,
  "t": 1783867360
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "system_time": 1784065095
}
```

### factory_reset

Nouzový příkaz pro uvedení do výchozího stavu. Trvale smaže obsah
konfigurační NVS paměti (všechna cron pravidla a hesla k síti), okamžitě
odpojí rádio a hardwarově vypne všechny porty, aby se minimalizovalo
riziko nechtěného zápisu na připojené disky.

**Požadavek:**

``` json
{
  "cmd": "factory_reset",
  "t": 1784065269
}
```

**Odpověď:**

``` json
{
  "status": "ok",
  "message": "Factory reset successful."
}
```

# Řízení pomocí jazyka Python

Zařízení je navrženo pro snadnou integraci do nadřazených
automatizačních skriptů. Komunikace probíhá ve formátu JSON a lze ji
realizovat prostřednictvím standardních Python knihoven.

## Potřebné knihovny

Pro plnohodnotné řízení (zejména přes šifrovanou WiFi) je nutné mít v
Python prostředí nainstalovány následující knihovny:

-   `pyserial` Slouží k přímé komunikaci s hardwarovým USB/COM portem v
    případech, kdy je ESP32-C6 připojeno kabelem přímo k zálohovacímu
    serveru.

-   `requests` Zajišťuje odesílání HTTP POST požadavků pro komunikaci
    přes bezdrátovou síť.

-   `pycryptodome` Zastřešuje kryptografické operace (AES-128-CBC) a
    generování náhodných inicializačních vektorů (IV) nutných pro
    zabezpečení WiFi komunikace.

## Jednoduchá komunikace přes USB (Sériová linka)

V tomto režimu ESP32-C6 neprovádí žádné dešifrování dat, pouze přijme
raw JSON string a obratem pošle odpověď. Zařízení se hlásí pod výchozím
identifikátorem Espressif (VID `0x303A`, PID `0x1001`).

**Ukázkový skript:** Pošle po USB příkaz pro načtení stavu a přečte
výsledek.

``` python
import serial
import serial.tools.list_ports
import json
import time

VID = 0x303A
PID = 0x1001

# Zjištění správného COM portu podle Hardware ID
port_name = None
for p in serial.tools.list_ports.comports():
    if p.vid == VID and p.pid == PID:
        port_name = p.device
        break     

if port_name:
    print(f"ESP32-C6 nalezeno na: {port_name}")
    # Otevření spojení (baudrate 115200, timeout pro případ záseku)
    with serial.Serial(port_name, 115200, timeout=2) as ser:
        # Sestavení příkazu. V USB režimu je "t" čistě formální, ale doporučené.
        cmd = {"cmd": "get_status", "t": int(time.time())}
        
        # Odeslání stringu ukončeného znakem nového řádku
        ser.write((json.dumps(cmd) + "\n").encode('utf-8'))
        ser.flush()
        
        # Přečtení a vypsání odpovědi
        response = ser.readline().decode('utf-8').strip()
        print(f"Odpověď: {response}")
else:
    print("Zařízení nebylo detekováno.")
```

## Šifrovaná komunikace přes WiFi

Základním principem je vzít JSON text, zašifrovat ho (AES-CBC), připojit
před něj použitý IV (Inicializační vektor) a celou tuto změť bajtů
převést do tisknutelných znaků pomocí Base64 před odesláním přes HTTP
POST.

**Ukázkový skript:** Pošle po WIFI příkaz pro zapnutí prvního portu.\
IP_ADRESA a AES_KEY musí být správně.

``` python
import json
import time
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

IP_ADRESA = "192.168.1.80"
# Heslo musí být přesně 16 znaků dlouhé (128 bitů)
AES_KEY = "1234567890123456".encode('utf-8') 

def posli_sifrovane(cmd_dict):
    # Ochrana proti Replay útokům: nutnost vložit aktuální čas
    cmd_dict["t"] = int(time.time())
    plain_text = json.dumps(cmd_dict).encode('utf-8')
    
    # 1. Šifrování
    iv = get_random_bytes(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded_data = pad(plain_text, AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    
    # 2. Spojení IV + Zašifrovaná data a převod do Base64
    final_payload = base64.b64encode(iv + encrypted_bytes).decode('utf-8')
    
    # 3. Odeslání na server
    url = f"http://{IP_ADRESA}/api"
    try:
        res = requests.post(url, data=final_payload, timeout=5)
        print(f"Odesláno. HTTP Status: {res.status_code}")
        # Poznámka: res.text obsahuje Base64 odpověď, kterou je třeba zpětně dešifrovat
    except Exception as e:
        print(f"Chyba spojení: {e}")

# Příklad volání: Zapnutí portu 1
posli_sifrovane({"cmd": "set_port", "port": 1, "state": "on"})
```

# GUI rozhraní
**`hub_dashboard.py`**

Pro účely správy, nasazení a vizuální kontroly existuje plnohodnotná GUI
aplikace `hub_dashboard.py`. Je vytvořena nad standardní knihovnou
`tkinter`.

Aplikace funguje jako univerzální testovací terminál. Abstrahuje
komunikační vrstvu, takže uživatel nahoře v okně pouze překlikne "USB"
nebo "WiFi", zadá heslo a zbytek uživatelského rozhraní reaguje zcela
identicky bez ohledu na způsob přenosu.

### Možnosti a funkce dashboardu:

-   Diagnostika a monitoring (Tab 1): Vizuální mřížka 10 tlačítek pro
    okamžité zapnutí/vypnutí portů. Okno detekuje aktuální čas uvnitř
    ESP32 a barevně varuje v případě poškození sběrnice I²C (ztráta
    spojení s port expandérem MCP23017), nebo v případě desynchronizace
    času.

-   Správa plánovače (Tab 2): Umožňuje z paměti stáhnout stávající cron
    pravidla, kliknutím na položku v seznamu ji vložit zpět do
    editačního formuláře, upravit časy sepnutí a pravidlo přes API
    uložit nebo trvale odstranit.

-   Nastavení sítě (Tab 3): Konfiguruje přihlašovací údaje k WiFi, AES
    klíč a fixní IPv4 topologii. Umožňuje si z antény mikrokontroléru
    vyžádat proskenování okolních bezdrátových sítí a vložit je do
    rozbalovací nabídky.

-   Systémové akce a konzole: Ve spodní části okna se nachází barevně
    odlišený "Log", který v reálném čase zobrazuje zasílané (TX) a
    přijímané (RX) JSON pakety. Obsahuje též formulář pro odeslání
    vlastního (custom) JSON příkazu, což je ideální pro vývojáře ladící
    API příkazy.

# TUI rozhraní
**`tui_dashoard.py`**

Stejné funkce jako výše zmiňovaná GUI aplikace, ale TUI dashboard běží v
terminálu s využitím frameworku Textual. Je plně klikací, ale textový.

# Program pro ESP32-C6 v Arduino IDE

Tato kapitola popisuje strukturu zdrojových kódů a rozdělení logiky
uvnitř samotného mikrokontroléru. Projekt je psán objektově v jazyce C++
s využitím frameworku Arduino. Každá logická část je oddělena do
vlastního manažera, což usnadňuje budoucí rozšiřování a údržbu.

**aktuální verze 0.1 neobsahuje watchdog**

-   `HubController.ino`\
    Hlavní vstupní bod programu. V metodě `setup()` inicializuje veškeré
    hardwarové a softwarové moduly (I²C sběrnici pro RTC a expandér,
    plánovač a WiFi rádio). V nekonečné smyčce `loop()` pak zajišťuje
    jejich periodickou aktualizaci a udržuje běh celého systému. Zároveň
    přímo zde dochází k naslouchání na sériové lince a zachytávání JSON
    příkazů poslaných po USB kabelu.

-   `Config.h`\
    Globální konfigurační hlavičkový soubor. Zde se definují pevné
    parametry zařízení, které nelze měnit za běhu. Zejména se jedná o
    maximální počet podporovaných portů (`MAX_PORTS`) a POSIX definici
    časové zóny (včetně automatického přechodu na letní čas), podle
    které systém počítá časy pro plánovač. Dále se zde nachází makro
    `ENABLE_DEBUG`, jehož odkomentováním lze zapnout diagnostické výpisy
    na sériovou linku (např. odesílané přes `DEBUG_PRINT`).

-   `ApiParser.h` / `ApiParser.cpp`\
    Komunikační mozek aplikace. Slouží k rozbalení (deserializaci)
    přijatých JSON řetězců (již po odstranění případného WiFi
    šifrování). Analyzuje obsah podle klíče `"cmd"`, validuje parametry
    a volá výkonné funkce ostatních modulů (např. zapnutí portu, uložení
    pravidla do Cronu, smazání flash paměti). Sestavuje finální
    strukturované JSON odpovědi o úspěchu či chybě.

-   `WifiManager.h` / `WifiManager.cpp`\
    Obsluhuje bezdrátovou síť a bezpečnost na LwIP (Lightweight IP)
    síťové vrstvě. Řídí připojování k wifi (s nutnou 8 vteřinovou
    prodlevou proti zablokování routerem) a provozuje HTTP server na
    portu 80. Zajišťuje nastavení DHCP, nebo ruční zadání statické IP
    adresy, brány a DNS. Dále obsahuje kompletní kryptografický aparát
    využívající `mbedtls` knihovny (šifrování AES-128-CBC) a logiku pro
    ochranu před opakovanými (Replay) útoky kontrolou časových razítek.
    Údaje o síti si ukládá do do NVS paměti.

-   `TimeManager.h` / `TimeManager.cpp`\
    Zajišťuje absolutní přesnost času v unixovém formátu, která je
    nezbytná pro plánovač a bezpečnostní časová razítka. Inicializuje
    komunikaci s hardwarovým RTC modulem DS3231 přes sběrnici I²C. Poku
    je připojen k WIFI, tak se pravidelně dotazuje na definované NTP
    servery a pokud dojde k synchronizaci s internetem, automaticky
    provede rekalibraci času i na hardwarovém RTC modulu.

-   `CronScheduler.h` / `CronScheduler.cpp`\
    Autonomní plánovač úloh. Zpracovává pole pravidel a stará se o
    jejich persistenci do nevolatilní NVS paměti (pravidla tak přežijí i
    restart po výpadku napájení). Každé pravidlo získá své unikátní ID.
    Manažer pravidelně, každou minutu, porovnává systémový čas s maskou
    nastavených dnů a hodin. Při shodě provede zadanou akci na
    příslušném portu.

-   `HardwareManager.h` / `HardwareManager.cpp`\
    Hardwarová abstrakční vrstva řídící fyzické přepínání portů. Skrze
    sběrnici I²C komunikuje s port expandérem MCP23017. Při startu
    okamžitě vnutí portům bezpečný počáteční stav (LOW, tedy vypnuto).
    Udržuje si přehled nad aktuálním stavem jednotlivých bran (Bank A,
    Bank B) a řeší nízkoúrovňový bitový zápis registrů v expandéru.
    Obsahuje také metodu `checkConnection()` pro rychlou diagnostiku,
    zda port expandér komunikuje (odpovídá znakem ACK) na své adresní
    lince.

# Hardwarové řešení

-   Řídicí jednotka (ESP32-C6): Mikrokontrolér, který obsluhuje
    firmware, spravuje WiFi konektivitu a řídí veškeré periferie.
    Disponuje nativním USB rozhraním, které se využívá pro lokální
    komunikaci.

-   I²C port expandér (MCP23017): Pro ovládání výstupů. Umožňuje spínat
    jednotlivé kanály. Při zapnutí napájení má všechny piny ve stavu
    vysoké impedance. Nastavuje a drží zapnuté nebo vypnuté porty bez
    ohledu na stav mikrokontroléru. Firmware pouze čte a zapisuje do
    registrů MCP23017.

-   USB sériová linka je považována za důvěryhodný lokální kanál, proto
    systém při USB komunikaci nevyžaduje shodu časového razítka v paketu
    s vnitřním časem mikrokontroléru. Po USB si může server sám řídit
    připojování a odpojování portů

-   I²C hodiny reálného času (DS3231) je volitelné rozšíření. V případě,
    že tento modul není na I²C sběrnici přítomen, spoléhá systém při
    startu výhradně na připojení k WiFi síti. Po navázání bezdrátového
    spojení mikrokontrolér automaticky provede synchronizaci svého
    interního času s internetovými NTP servery. Tato synchronizace je
    kriticky důležitá, neboť bez ní by zařízení nebylo schopno zajistit
    bezpečnost proti Replay útokům (které vyžadují přesné časové
    razítko) a plánovač (Cron) by nemohl korektně vykonávat naplánované
    úlohy. V prostředí bez přístupu k WiFi a bez osazeného RTC modulu je
    tak systém po restartu bez přesné časové reference, což znemožňuje
    autonomní provoz.

-   Spínací obvody: Systém využívá tranzistorové spínání (typicky
    p-mosfety ovládané n-mosfety řízenými expandérem) pro fyzické
    připojení nebo odpojení napájení k jednotlivým USB portům.

# Odkaz na stažení

[ke stažení](https://drive.google.com/drive/folders/12ns49WnBjIt_Di5GOzrGpgCpxaej0EIu?usp=drive_link) – firmware pro mikrokontroler, řídící programy v Pythonu 
