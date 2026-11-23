---
title: "Atari hry - dokumentace"
date: 2026-11-21T17:16:11+01:00
cover:
    image: ""
tags: ["Počítače", "Počítače.emulátory", "Počítače.hry"]
draft: false
---
### Jak funguje
**[atarihry.sytes.net](https://atarihry.sytes.net)**

# Technická dokumentace `hry.html` – WebAssembly spouštěč pro Atari 130XE PAL

Je mně jasné, že když na tomto projektíku budu chtít za půl roku něco opravit, bude se každý kousek dokumentace hodit. 

> **Zdrojový soubor:** `hry.html` (samostatný jednosouborový frontend pro vlastní WebAssembly build emulátoru `atari800` v5.2.0 / SDL2)

## Obsah dokumentace

1. [Úvod a motivace: Proč to děláme](#1-úvod-a-motivace-proč-to-děláme)
2. [Spouštění emulátoru, URL API, MEMFS a správa obrazu](#2-spouštění-emulátoru-url-api-memfs-a-správa-obrazu)
3. [Desktopové ovládání – klávesnicové matice, konfigurátor joysticků, kolize a `localStorage`](#3-desktopové-ovládání--klávesnicové-matice-konfigurátor-joysticků-kolize-a-localstorage)
4. [Sjednocená vrstva syntetických vstupů (`dispatchSynthKey`, SDL2 `SDL_TEXTINPUT`) a Gamepad API](#4-sjednocená-vrstva-syntetických-vstupů-dispatchsynthkey-sdl2-sdl_textinput-a-gamepad-api)
5. [Mobilní rozhraní, Fullscreen (včetně iOS Safari fallbacku) a dotyková klávesnice Atari](#5-mobilní-rozhraní-fullscreen-včetně-ios-safari-fallbacku-a-dotyková-klávesnice-atari)
6. [Dotykový D-pad, tlačítko FIRE a nízké latence)](#6-dotykový-d-pad-tlačítko-fire-a-nízké-latence)
7. [Vývojářský referenční přehled (konstanty, klíče, stavové třídy, bezpečnostní pojistky)](#7-vývojářský-referenční-přehled)

---

## 1. Úvod a motivace: Proč to děláme

Cílem `hry.html` je umožnit okamžité, autentické a bezproblémové hraní klasických 8bitových her pro **Atari 130XE PAL ($128\text{ KB}$ RAM)** přímo v běžném webovém prohlížeči – jedním kliknutím na odkaz, bez instalace jakýchkoli doplňků a bez ohledu na to, zda návštěvník sedí u stolního PC, pracuje na notebooku bez pravého `Ctrl`, drží v ruce mobil (Android / iOS), nebo si připojil Bluetooth gamepad.

Zatímco zkompilování samotného emulátoru do WebAssembly řeší emulaci hardwaru (CPU 6502, čipy ANTIC, GTIA, POKEY, PIA), **skutečná použitelnost a herní zážitek stojí a padá s obslužnou vrstvou v prohlížeči**. Soubor `hry.html` je výsledkem postupného ladění reálných problémů z praxe – od přesnosti emulace přes omezení fyzických klávesnic až po milisekundovou latenci na dotykových displejích.

### 1.1 Proč nestačila hotová webová řešení

Cesta k vlastnímu řešení v `hry.html` vychází z empirického ověření dostupných alternativ a jejich konkrétních limitů:

| Přístup | Hlavní omezení zjištěná v praxi |
| ----- | ----- |
| **EmulatorJS / veřejné CDN** | Chybějící jádro `atari800` na veřejném CDN, závislost na externích službách a nutnost řešit bezpečnostní hlavičky `COOP` / `COEP` pro vícevláknový `SharedArrayBuffer`. |
| **jsA8E (JavaScriptový port A8E)** | Nepřesné rastrové časování čipů ANTIC/GTIA na úrovni barevných taktů – složitější DLI efekty, scrolly a vlastní diskové loadery (např. české magazíny typu FLOP a demoscéna) se vizuálně rozpadaly. |
| **MAME / MESS WASM (AtariOnline)** | Velký přenosový objem (cca $21\text{ MB}$), starší ovladač Atari s nepřesným časováním SIO/DLI, modifikovaná ROM a uživatelsky nepraktické přepínání režimů klávesnice. |
| **Vlastní `atari800.wasm` + `hry.html`** | Originální C jádro **Atari800 5.2.0** přeložené přes Emscripten do jednovláknového WebAssembly bez OpenGL a bez `R:` zařízení (`atari800.js` cca $185\text{ KB}$, `atari800.wasm` cca $1{,}8\text{ MB}$; s gzip cca $608\text{ KB}$, s Brotli předkompresí pod $500\text{ KB}$). Přesná PAL emulace, nulová závislost na cizích CDN a žádný požadavek na `SharedArrayBuffer`. |

Klíčový vedlejší přínos tohoto přístupu je **architektura čistě na straně klienta**: webový server (např. Caddy běžící na úsporném ARM serveru typu Odroid M2) pouze servíruje předkomprimované statické soubory (`.wasm.br`, `.atr.br`, `.car.br`). Po stažení běží celá emulace v prohlížeči hráče a zatížení serveru zůstává prakticky nulové.

### 1.2 Sjednocená cílová platforma: Atari 130XE PAL

Aby nebylo nutné u každé hry řešit, zda vyžaduje $64\text{ KB}$ nebo rozšířených $128\text{ KB}$ paměti, konfiguruje `hry.html` jádro vždy jednotně jako **Atari 130XE PAL ($128\text{ KB}$ RAM)** s originálními obrazy `ATARIXL.ROM` a `ATARIBAS.ROM`:

* **Plná zpětná kompatibilita:** Hry určené pro Atari 800XL běží na 130XE bez úprav a současně fungují i moderní tituly či velké produkce vyžadující rozšířenou paměť (včetně cartridge ve formátu `.car`, např. *Prince of Persia*).
* **Podporovaná média:** Automatické načítání disketových obrazů a spustitelných souborů (`.atr`, `.xfd`, `.xex`, `.dcm`, `.atx`) i cartridge (`.car`) do mechanik `D1:` a `D2:`.
* **Flexibilita bez přepisování kódu:** Vše podstatné (cesty k diskům, titulek, zapnutí `BASIC`, vypnutí `SIO` patche pro nestandardní loadery i režim vložení `embed`) se předává přes parametry URL.

### 1.3 Čtyři hlavní problémy, které `hry.html` řeší

Samotný `atari800.wasm` očekává klasické desktopové prostředí SDL2 s fyzickou klávesnicí. Aby z něj vznikla plnohodnotná multiplatformní herní aplikace, řeší `hry.html` čtyři zásadní oblasti:

1. **Hardwarová a prohlížečová omezení na desktopu:** Klávesnicové matice (*key ghosting / 2KRO*), absence `Pravého Ctrl` na noteboocích, kolize mezi dvěma joysticky, potřeba psát písmena `WASD` v textových hrách a kolize funkčních kláves `F1`–`F6` se zkratkami prohlížeče.
2. **Hraní na mobilech a tabletech bez kompromisů:** Přeskládání stránky pro dotykové displeje, nativní i CSS pseudo-fullscreen (pro iOS Safari), automatické přepínání rozložení na šířku a na výšku, okamžité prohazování stran ovladače i vestavěná dotyková klávesnice Atari.
3. **Nízká latence a spolehlivá registrace dotyku při $50\text{ Hz}$ PAL:** Přímé nativní Touch Events bez syntetizačního zpoždění, okamžitá odezva $0\text{ ms}$ při stisku i změně směru, kešování geometrie D-padu, pulzní garance pro rychlá ťuknutí a asynchronní volitelná haptika.
4. **Univerzální vstupní architektura a vkládání (`embed`):** Jednotný překlad všech zdrojů vstupu (dotyk, dotyková klávesnice, konzolová tlačítka, až 2 USB/Bluetooth gamepady přes Gamepad API) na standardní syntetické události DOM + minimalistické `embed=1` / `embed=2` režimy pro `<iframe>`.

### 1.4 Vysokoúrovňové schéma toku dat v `hry.html`

```text
+-------------------------------------------------------------------------+
|                           VSTUPY UŽIVATELE                              |
|  [Fyzická klávesnice]  [USB/BT Gamepad API]  [Touch D-pad/FIRE + Kláv.] |
+-----------+---------------------+------------------------+--------------+
            |                     |                        |
            | (nativní DOM)       | (rAF polling)          | (Touch/Pointer)
            v                     v                        v
            |         +---------------------------------------------+
            |         |  Sjednocená vrstva: dispatchSynthKey()      |
            |         |  (activeRunCfg -> SDL_TO_DOM -> keydown /   |
            |         |   keypress[charCode] / keyup na #canvas)    |
            |         +----------------------+----------------------+
            |                                |
            +---------------+----------------+
                            v
+-------------------------------------------------------------------------+
|                   <canvas id="canvas"> (672 x 480)                      |
|               Emscripten SDL2 + atari800.wasm (130XE PAL)               |
|    [MEMFS: /ATARIXL.ROM, /ATARIBAS.ROM, /atari800.cfg, /hra.atr|.car]   |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                    VÝSTUP A RESPONZIVNÍ VRSTVA                          |
|  fitCanvas() + ResizeObserver + MutationObserver -> vždy přesný 4:3     |
|  [Desktop: 30-100 % + panel] [Mobil: Fullscreen L/P] [Embed: 1 / 2]     |
+-------------------------------------------------------------------------+
```

---

## 2. Spouštění emulátoru, URL API, MEMFS a správa obrazu

Tato část popisuje životní cyklus stránky od přečtení adresy URL přes stažení binárních dat do paměťového souborového systému Emscriptenu a nastartování jádra `atari800.wasm` až po přesné udržování poměru stran $4:3$ ve všech režimech zobrazení.

### 2.1 URL API a rekonstrukce odkazů

Soubor `hry.html` je bezstavový parametrizovaný spouštěč – konkrétní hru i startovací volby hardwaru přijímá z `window.location.search` prostřednictvím `URLSearchParams`:

| Parametr | Výchozí hodnota | Chování a význam v `hry.html` |
| ----- | ----- | ----- |
| `d1` | `""` *(prázdný)* | Primární obraz pro mechaniku `D1:` (`.atr`, `.xfd`, `.xex`, `.dcm`, `.atx`) nebo cartridge (`.car`). Pokud není zadán, Atari 130XE startuje bez média (do Self-Testu nebo BASICu). |
| `d2` | `""` *(prázdný)* | Volitelný druhý obraz připojený automaticky do mechaniky `D2:` (dvoudiskové hry). |
| `title` | název z `d1` bez přípony | Uživatelský titulek zobrazovaný v `<title>`, ve stavové liště `#status-info` i ve spouštěcím boxu `#start-title`. Při absenci `d1` i `title` se použije `"Atari 130XE"`. |
| `basic` | `"0"` *(vypnuto)* | `basic=1` zapíná interní Atari BASIC (`DISABLE_BASIC=0`, přepínač `-basic`). Ve výchozím stavu je BASIC vypnutý (`DISABLE_BASIC=1`, `-nobasic`), což odpovídá držení `OPTION` při zapnutí a vyžaduje to naprostá většina her. |
| `sio` | `"1"` *(zapnuto)* | `sio=0` vypíná zrychlený SIO patch (`ENABLE_SIO_PATCH=0`). Nutné pro hry a dema s vlastním nestandardním diskovým loaderem nebo hudbou/animací při nahrávání. |
| `embed` | `""` *(plné UI)* | `embed=1` nebo `embed=true` zapne vložený režim (`html.mode-embed`); `embed=2` zapne minimální režim bez spodní nápovědy (`html.mode-embed-min`). |

#### Rozlišení cartridge vs. disketa (`isCartFile`)

Funkce `isCartFile(path)` testuje příponu regulárním výrazem `/\.car$/i`. Pokud `d1` končí na `.car`, projeví se to na třech místech:

1. **V uživatelském rozhraní (`updateUI`):** Stavová lišta a úvodní karta zobrazí prefix `CART:` místo `D1:` a tlačítko při načítání hlásí `"Nahrávám ROM a cartridge..."`.
2. **Při sestavení argumentů `callMain(args)`:** Cartridge musí být emulátoru `atari800` předána explicitním přepínačem `["-cart", fsPath1]`, zatímco disketové a spustitelné formáty (`.atr`, `.xex`, `.xfd`…) se předávají přímo jako poziční argument.

#### Přepínače SIO a BASIC za běhu (`buildQuery`)

Protože parametry `ENABLE_SIO_PATCH` a `DISABLE_BASIC` čte jádro `atari800` při startu, jsou odkazy `#sio-toggle-link` a `#basic-toggle-link` v horní liště řešeny jako čistá navigace na aktualizovanou URL. Funkce `buildQuery(overrides)` sestaví nový query string tak, že zachová `d1`, `d2`, `title` i `embed` a zapisuje pouze volby lišící se od výchozího stavu (`basic=1`, `sio=0`), takže výsledné URL zůstává krátké a čisté.

### 2.2 Načítání souborů a virtuální souborový systém (MEMFS)

WebAssembly jádro běží v prohlížečovém sandboxu a nemá přímý přístup na disk serveru ani klienta. Emscripten proto vytváří v operační paměti prohlížeče virtuální souborový systém **MEMFS**, přístupný z JavaScriptu pod `window.Module.FS`.

#### Bezpečné kódování cest (`encodePath`)

Názvy souborů v katalogu her běžně obsahují mezery, závorky, apostrofy či ampersandy (např. `Boulder Dash I (1984).atr`, `Clowns & Balloons (1982).atr`, `Montezuma's revenge (1984).atr`). Funkce `encodePath(path)` proto rozdělí cestu podle `/` a každou část zakóduje samostatně přes `encodeURIComponent`, čímž zachová oddělovače adresářů a zabrání selhání HTTP `fetch()`.

#### Stažení do paměti (`fetchToFS`) a součinnost s Brotli/gzip

```text
Prohlížeč (fetch s cache: "no-store")
   |  Accept-Encoding: gzip, deflate, br
   v
Webový server (např. Caddy s precompressed br gzip)
   |  najde soubor .atr.br / .car.br / .wasm.br
   |  odešle menší binární payload + Content-Encoding: br
   v
HTTP vrstva prohlížeče (transparentně rozbalí data)
   |  res.arrayBuffer() -> originální nekomprimované bajty
   v
window.Module.FS.writeFile("/nazev.atr", new Uint8Array(buf))
```

* Příznak `{ cache: "no-store" }` zaručuje, že při výměně či opravě souboru na serveru dostane uživatel okamžitě novou verzi bez nutnosti mazat mezipaměť.
* Předkomprese na serveru (`.br`, `.gz`) je pro `hry.html` zcela transparentní – `fetchToFS()` vždy zapíše do MEMFS přesnou nekomprimovanou bitovou kopii ROM nebo diskety.

#### Automatické dohledávání médií a ochrana cesty (`fetchDiskAuto`)

Aby URL odkazy mohly být co nejkratší (`hry.html?d1=boulder.atr`), ale zároveň podporovaly podsložky (`hry.html?d1=atr/archiv/hra.atr`), postupuje `fetchDiskAuto(diskParam)` ve třech krocích:

1. **Sanitizace a ochrana proti *path traversal*:** Odstraní úvodní lomítka (`replace(/^\/+/, "")`) a striktně odmítne jakoukoli cestu obsahující segment `..`.
2. **Kandidátní cesty:**
   * Obsahuje-li parametr lomítko (`clean.includes("/")`), zkusí přesně zadanou relativní cestu `[clean]`.
   * Jde-li o prostý název souboru bez lomítka, zkusí nejprve `atr/${clean}` a při neúspěchu (např. HTTP 404) jako záložní variantu `./${clean}` vedle `hry.html`.
3. **Zápis do kořene MEMFS:** První úspěšně stažený obraz se zapíše jako `/${baseName(clean)}` (tedy vždy plochou cestou do kořene virtuálního FS), aby jádro `atari800` nemuselo zakládat vnořené podadresáře v MEMFS.

### 2.3 Životní cyklus startu WebAssembly (`window.Module` a `callMain`)

Skript `atari800.js` (vygenerovaný Emscriptenem) je záměrně vložen až jako poslední prvek před `</body>`, tedy po definici globálního objektu `window.Module`:

```javascript
window.Module = {
    canvas: canvasEl,
    print: (text) => console.log("[atari800]", text),
    printErr: (text) => console.warn("[atari800]", text),
    onRuntimeInitialized: function () {
        startBtn.disabled = false;
        startBtn.textContent = d1 ? "Spustit hru" : "Spustit Atari 130XE";
        fitCanvas();
    }
};
```

#### Proč emulátor nestartuje automaticky, ale až po kliknutí na `#start-btn`

Jádro `atari800.wasm` bylo zkompilováno s přepínačem `-sINVOKE_RUN=0`, takže po načtení binárky nevolá funkci `main()` samo, ale pouze oznámí připravenost přes `onRuntimeInitialized`. Důvody jsou tři:

1. **Odemknutí zvuku (Web Audio Autoplay Policy):** Moderní prohlížeče blokují spuštění `AudioContext` (tedy zvuk čipu POKEY), dokud neproběhne přímá uživatelská interakce (*user gesture*). Kliknutí na tlačítko **Spustit hru** zvuk spolehlivě odblokuje.
2. **Příprava souborů a konfigurace:** Teprve v obsluze kliknutí se do MEMFS zapíšou `ATARIXL.ROM`, `ATARIBAS.ROM`, případné `d1`/`d2` a dynamicky vygenerovaný `/atari800.cfg`.
3. **Možnost nastavit joysticky před startem:** Uživatel může ještě před spuštěním přepnout profil joysticku v pravém panelu a vygenerovaný `/atari800.cfg` už obsahuje jeho zvolené klávesy bez nutnosti následného restartu.

#### Vygenerovaný `/atari800.cfg` a význam jednotlivých direktiv

Při spuštění `hry.html` sestaví a zapíše do `/atari800.cfg` čistý textový konfigurační soubor s unixovými konci řádků (`\n`):

| Skupina direktiv | Hodnoty | Technický důvod |
| ----- | ----- | ----- |
| **Hardware** | `MACHINE_TYPE=Atari XL/XE`, `RAM_SIZE=128`, `DEFAULT_TV_MODE=PAL` | Sjednocená konfigurace **Atari 130XE PAL** s $128\text{ KB}$ RAM a $50\text{ Hz}$ časováním. |
| **Video & roztažení** | `VIDEOMODE_WINDOWED=1`, `VIDEOMODE_WINDOW_WIDTH=672`, `VIDEOMODE_WINDOW_HEIGHT=480`, `VIDEOMODE_HORIZONTAL_AREA=TV`, `VIDEOMODE_VERTICAL_AREA=TV`, `VIDEOMODE_STRETCH=FULL`, `VIDEOMODE_FIT=BOTH`, `VIDEOMODE_KEEP_ASPECT=NONE` | Přinutí softwarový SDL2 renderer `atari800` vyplnit $100\%$ pixelové plochy framebufferu $672 \times 480$ bez vlastních vnitřních černých okrajů. Výsledný autentický poměr stran $4:3$ pak řídí výhradně `fitCanvas()` v CSS/JS. |
| **BASIC a SIO** | `DISABLE_BASIC=0\|1`, `ENABLE_SIO_PATCH=0\|1` | Řídí boot do BASICu a zrychlení disketové jednotky. (`ENABLE_SIO_PATCH` se nastavuje výhradně zde – CLI přepínač `-siopatch` v této verzi `atari800` neexistuje.) |
| **Klávesové joysticky** | `SDL_JOY_0_ENABLED=1`, `SDL_JOY_0_{UP,DOWN,LEFT,RIGHT,TRIGGER}`, `SDL_JOY_1_ENABLED=0\|1`, `SDL_JOY_1_*` | Mapování z aktuálního `joyCfg` v klasických číselných kódech SDL 1.2 (např. `273`–`276`, `305`), které `atari800` se SDL2 interně překládá na `SDLK_*`. |

#### Sekvence po zápisu konfigurace (`callMain` a zmrazení konfigurace)

Po zapsání ROM, `/atari800.cfg` a obrazů médií provede handler tlačítka `#start-btn` tyto kroky:

1. Sestaví pole argumentů `args` (včetně `-xe`, `-pal`, `-kbdjoy0`, podmíněného `-kbdjoy1` / `-no-kbdjoy1`, `-windowed -win-width 672 -win-height 480`, `d1` s `-cart` pro `.car` a případného `d2`).
2. **Vytvoří neměnný snapshot běžící instance:**
   * `activeRunCfg = JSON.parse(JSON.stringify(joyCfg))` – všechny syntetické vstupy (dotykový ovladač i Gamepad API) čtou klávesové kódy právě z `activeRunCfg`, nikoli ze živého `joyCfg`. Pokud si tedy hráč uprostřed hry v panelu změní mapování kláves, ale hru ještě nerestartoval, dotyk i gamepad dál posílají klávesy, na kterých běží aktuální instance `atari800`, a nepřestanou fungovat.
   * `startedKbdSnapshot = kbdSnapshot(joyCfg)` – textový otisk klávesových joysticků, oproti kterému UI detekuje změnu (*dirty state*) a zobrazí tlačítko **Použít a restartovat hru** (`#btn-apply-restart`).
3. Skryje `#start-box`, nastaví `isRunning = true`, aktualizuje UI a smyčku gamepadu, předá fokus na `#canvas` a zavolá `window.Module.callMain(args)`.
4. Po $100\text{ ms}$ vyvolá `fitCanvas()`, aby srovnal plátno po dokončení inicializace SDL2 okna.
5. Celý blok je obalen v `try / catch`: při jakékoli síťové nebo souborové chybě (chybějící ROM, 404 u diskety) vypíše důvod do `#status-info` i `#start-info` a odemkne tlačítko s popiskem `"Zkusit znovu"`.

### 2.4 Správa obrazu ($4:3$), plynulé škálování a ochrana proti SDL2

Zobrazení emulovaného obrazu bez deformací a ořezů napříč monitory, okny libovolných proporcí i mobily na šířku a výšku je řízeno centrální funkcí `fitCanvas()` a plynulým vyhlazováním (`image-rendering: auto`).

#### Proč `image-rendering: auto` místo `pixelated`

Framebuffer má fixní rozlišení $672 \times 480$ (tedy $2\times$ nativní $336 \times 240$), ale cílová velikost `<canvas>` v prohlížeči bývá téměř vždy neceločíselným násobkem (např. při přizpůsobení oknu nebo posuvníku $30\text{--}100\%$). Režim `pixelated` při neceločíselném zvětšení způsobuje nerovnoměrnou tloušťku svislých a vodorovných čar (zvláště patrnou u $8 \times 8$ znaků v textech a menu). Volba `image-rendering: auto` zajišťuje rovnoměrné, čitelné zobrazení při jakékoli velikosti okna.

#### Uživatelské měřítko na desktopu (`screenScale`)

Na desktopu (mimo Fullscreen a mimo `embed`) si uživatel může obraz kdykoli za běhu zmenšit v rozsahu $30\%$ až $100\%$ bez restartu emulátoru:

* **Posuvník `#size-slider`:** krok $5\%$, zaokrouhlování v `setScreenScale()` výrazem $\text{round}(v / 5) \cdot 5$ a oříznutí do intervalu $[30, 100]$.
* **Tlačítka `−` a `+`:** skok po $\pm 10\%$, po kliknutí vrátí fokus zpět na `#canvas`.
* **Tlačítko hodnoty (`100 %`):** jedním kliknutím vrací velikost na $100\%$.
* **Perzistence:** Hodnota se ukládá do `localStorage` pod klíčem `"atari800_scale"`.
* **Izolace kláves:** Kontejner `#size-switch` zachytává `keydown` přes `e.stopPropagation()`, aby šipky při posouvání jezdce neovládaly současně Atari.

#### Výpočet rozměrů v `fitCanvas()` – tři geometrické větve

Při každém přepočtu `fitCanvas()` nejprve invaliduje kešovanou pozici dotykového D-padu (`dpadCachedRect = null`), synchronizuje CSS stavové třídy kontejneru `#stage` (`syncStageFullscreenClasses()`) a poté zvolí jednu ze tří větví výpočtu pro konstantu $\text{ASPECT} = \frac{4}{3}$:

1. **Fullscreen na výšku s dotykovým ovladačem (`fs && isPortrait && touchActive`):**
   * Z celkové výšky `#stage` odečte skutečnou výšku horní lišty (`fsTopbarEl.offsetHeight || 44`) a vyhradí spodní zónu pro D-pad a `FIRE` o velikosti $\max(185,\; \lfloor 0{,}34 \cdot H_{\text{stage}} \rfloor)\text{ px}$.
   * Do zbývající plochy maximalizuje obdélník o poměru $4:3$, takže hra nahoře a ovladač pod ní nikdy nekolidují.
2. **Mobilní rozložení mimo Fullscreen (`!isEmbed && !fs && mobileMq.matches`):**
   * Obraz roztáhne na celou dostupnou šířku displeje, ale výšku zastropuje na $72\%$ výšky viewportu ($\max(180,\; \lfloor 0{,}72 \cdot H_{\text{window}} \rfloor)$), aby pod plátnem zůstalo bez rolování viditelné velké tlačítko **Celá obrazovka**.
3. **Desktop, Fullscreen na šířku, Fullscreen bez dotyku a Embed (výchozí větev):**
   * Spočítá maximální obdélník $4:3$, který se vejde do vnitřního prostoru `#stage` po odečtení CSS paddingu (`padX`, `padY`).
   * Použije efektivní měřítko `effectiveScale = (isEmbed || fs) ? 100 : screenScale` (ve Fullscreenu a `embed` režimu vždy plných $100\%$, nikdy ne méně než $160 \times 120\text{ px}$).

#### Obrana proti přepisování rozměrů z Emscripten SDL2 (`!important` + `MutationObserver`)

Knihovna SDL2 v Emscriptenu si při volání `SDL_CreateWindow` a při změnách stavu okna sama zapisuje inline styly `width` a `height` přímo na element `<canvas>`, čímž by rozbila responzivní layout. `hry.html` tomuto chování čelí kombinací čtyř mechanismů:

1. **Zápis s prioritou `!important`:** `canvasEl.style.setProperty("width", wPx, "important")` (a totéž pro `height`), přičemž zápis proběhne jen tehdy, pokud se vypočtená hodnota skutečně liší.
2. **Sledování atributů plátna (`MutationObserver`):** Hlídá změny `["style", "width", "height"]` přímo na `#canvas` a při jakémkoli zásahu SDL2 okamžitě zavolá `fitCanvas()`.
3. **Ochrana proti nekonečné rekurzi (`isFitting`):** Příznak `isFitting` v bloku `try / finally` brání tomu, aby zápis stylu uvnitř `fitCanvas()` znovu spustil rekurzivní přepočet přes `MutationObserver`.
4. **Sledování velikosti a orientace kontejneru:**
   * `ResizeObserver` na `#stage` reaguje okamžitě jak na změnu velikosti okna, tak na otevření či skrytí pravého panelu `#joy-panel` na desktopu.
   * Doplňkové listenery `window.resize`, `window.orientationchange` (se zpožděním $120\text{ ms}$ kvůli doběhu systémové animace otočení displeje) a `mobileMq.addEventListener("change", fitCanvas)` pokrývají přechody mezi mobilním a desktopovým breakpointem.

### 2.5 Režimy vložení (`embed=1` a `embed=2`)

Pro integraci her do blogových článků, katalogů či dokumentace přes `<iframe>` nabízí `hry.html` dvě úrovně minimalizace, aktivované přidáním tříd `mode-embed` a `mode-embed-min` přímo na `document.documentElement` ještě před prvním vykreslením stránky:

| Vlastnost | Plný režim *(bez `embed`)* | `embed=1` *(nebo `embed=true`)* | `embed=2` *(minimální)* |
| ----- | ----- | ----- | ----- |
| **Horní lišta `.bar` a pravý panel `#joy-panel`** | Zobrazeno | Skryto (`display: none !important`) | Skryto |
| **Mobilní tlačítka, Fullscreen lišta, D-pad, klávesnice** | Dle zařízení a režimu | Skryto a blokováno i v JS | Skryto a blokováno i v JS |
| **Spodní nápověda `.help`** | Plná velikost ($13\text{ px}$) | Kompaktní ($12\text{ px}$), bez horního rámečku | Skryta (`display: none`) |
| **Odsazení `#stage` a stín `#canvas`** | `8px 16px` + `box-shadow` | `4px`, bez stínu | `0`, bez stínu |
| **Měřítko plátna** | `screenScale` ($30\text{--}100\%$, z `localStorage`) | Vždy $100\%$ plochy `<iframe>` | Vždy $100\%$ plochy `<iframe>` |

Pro bezproblémové ovládání klávesnicí uvnitř vloženého `<iframe>` má plátno atribut `tabindex="0"`, zakázané kontextové menu (`oncontextmenu="event.preventDefault()"`) a handler `mousedown`, který okamžitě zruší případné odchytávání klávesy a předá prvku `#canvas` fokus.

---

## 3. Desktopové ovládání – klávesnicové matice, konfigurátor joysticků, kolize a `localStorage`

Na první pohled se může zdát, že emulovat 8bitový joystick na desktopové klávesnici znamená jen přiřadit pět libovolných kláves. V praxi ale narážíte na fyzickou topologii membránových klávesnic, absenci pravých modifikátorů na noteboocích, hry vyžadující dva hráče a tituly, které kromě joysticku vyžadují i běžné psaní na klávesnici Atari.

### 3.1 Fyzika klávesnicových matic (*key ghosting / 2KRO*) a volba výchozích kláves

Běžné kancelářské a notebookové klávesnice nepoužívají pro každou klávesu samostatnou diodu (*N-Key Rollover*), ale sdílenou matici řádků a sloupců (často s limitem *2KRO*, tedy garancí jen pro 2 současně stisknuté klávesy mimo modifikátory). V akčních hrách na Atari (typicky šikmý skok + střelba nebo kop v *International Karate*, *Bruce Lee*, *Dropzone*) ale hráč běžně drží **tři klávesy současně**: dva kolmé směry + `FIRE`.

* **Proč ne `W + A + Q` nebo `Šipky + Pravý Shift`:** Tři sousední písmena v jednom rohu matice téměř vždy způsobí zablokování třetí klávesy (*jamming*). Stejně tak u řady membránových klávesnic sdílí `Pravý Shift` linku se šipkou doprava.
* **Proč modifikátory `Ctrl` a `Shift`:** Řadiče klávesnic vedou modifikátory (`Control`, `Shift`, `Alt`) po vyhrazených linkách mimo hlavní matici písmen, takže téměř vždy umožňují spolehlivý trojhmat.
* **Výchozí konfigurace (`DEFAULT_JOY_CFG`):**
  * **Joystick 1:** Šipky (`273`, `274`, `276`, `275`) + **Pravý Ctrl** (`305`).
  * **Joystick 2 (zapnutý ve výchozím stavu):** `W`/`S`/`A`/`D` (`119`, `115`, `97`, `100`) + **Levý Shift** (`304`).

### 3.2 Předvolby (`J1_PRESETS`, `J2_PRESETS`) a přizpůsobení notebookům

Protože moderní kompaktní notebooky často vůbec nemají klávesu `Pravý Ctrl`, nabízí pravý boční panel `#joy-panel` rychlý výběr osvědčených profilů:

| Joystick | Klíč předvolby | Popisek v UI | Mapování (Nahoru / Dolů / Doleva / Doprava / Střelba) |
| ----- | ----- | ----- | ----- |
| **Joystick 1** | `arrows_rctrl` *(výchozí)* | Šipky + Pravý Ctrl | `273` / `274` / `276` / `275` / `305` |
| **Joystick 1** | `arrows_dot` | Šipky + tečka `.` (notebook) | `273` / `274` / `276` / `275` / `46` |
| **Joystick 1** | `arrows_space` | Šipky + Mezerník | `273` / `274` / `276` / `275` / `32` |
| **Joystick 1** | `wasd_lshift` | WASD + Levý Shift | `119` / `115` / `97` / `100` / `304` |
| **Joystick 2** | `wasd_lshift` *(výchozí)* | WASD + Levý Shift | `119` / `115` / `97` / `100` / `304` |
| **Joystick 2** | `ijkl_space` | IJKL + Mezerník | `105` / `107` / `106` / `108` / `32` |
| **Joystick 2** | `numpad` | Numpad 8/5/4/6 + 0 | `264` / `261` / `260` / `262` / `256` |

#### Chytré předcházení kolizi a uvolnění klávesnice Atari

* **Automatické vypnutí J2 při volbě WASD pro J1:** Pokud si hráč u Joysticku 1 vybere profil `wasd_lshift` a Joystick 2 je v tu chvíli zapnutý se stejným profilem `wasd_lshift`, skript automaticky nastaví `joyCfg.j2Enabled = false`, aby nevznikla okamžitá kolize všech pěti kláves.
* **Vypínač Joysticku 2 (`#j2-enabled`):** Jakmile se Joystick 2 vypne, předá se jádru přepínač `-no-kbdjoy1` a `SDL_JOY_1_ENABLED=0`. Klávesy `W`, `A`, `S`, `D` se okamžitě uvolní pro běžnou klávesnici Atari (potřebné např. v BASICu, textových hrách nebo při zadávání jména do tabulky rekordů). UI navíc zobrazí vysvětlující poznámku `#j2-off-note`.
* **Rozpoznávání vlastního profilu (`matchPreset`):** Funkce porovnává všech pět kódů oproti předvolbám; pokud se uživatel odchýlí byť v jediné klávese, rozbalovací seznam automaticky přepne na `"custom"` (*Vlastní nastavení*).

### 3.3 Datový model, perzistence a sanitizace (`localStorage`)

Veškeré nastavení ovládání se ukládá v jediném JSON objektu pod klíčem `JOY_STORAGE_KEY = "atari800_joy_cfg_v1"`:

```javascript
const DEFAULT_JOY_CFG = {
    j1: { up: 273, down: 274, left: 276, right: 275, fire: 305 },
    j2Enabled: true,
    j2: { up: 119, down: 115, left: 97, right: 100, fire: 304 },
    gamepadEnabled: false,
    touchMode: "auto",          // "auto" | "always" | "off"
    touchLayout: "dpad_right",  // "dpad_right" | "dpad_left"
    touchDpadStyle: "digital8", // "digital8" | "digital4"
    touchHaptics: false
};
```

Funkce `loadJoyConfig()` je napsána defenzivně, aby aplikace nikdy nespadla ani při poškozeném záznamu, změně schématu po aktualizaci nebo v režimu anonymního okna bez povoleného `localStorage`:

* Celé čtení i zápis jsou obalené v `try / catch`.
* Každá páčka prochází funkcí `sanitizeStick(obj, fallback)`, která u všech pěti směrů kontroluje `Number.isInteger(v) && v > 0`.
* Všechny výčtové položky (`touchMode`, `touchLayout`, `touchDpadStyle`) se ověřují proti povoleným seznamům a booleany (`j2Enabled`, `gamepadEnabled`, `touchHaptics`) pomocí `typeof ... === "boolean"`.
* Samostatný klíč `PANEL_STORAGE_KEY = "atari800_joy_panel_open"` pamatuje stav pravého panelu na desktopu (`"1"` / `"0"`). Pokud uživatel dosud panel nepřepínal, otevírá se automaticky na širších obrazovkách (`window.innerWidth >= 960`).

### 3.4 Převod DOM událostí na SDL 1.2 kódy (`eventToSdlCode`)

Přestože je `atari800.wasm` zkompilováno proti **SDL2**, soubor `/atari800.cfg` z důvodu zpětné kompatibility očekává u voleb `SDL_JOY_*` klasické číselné kódy **SDL 1.2** (uvnitř `src/sdl/input.c` má jádro vlastní `switch`, např. `case 273: return SDLK_UP;`).

Funkce `eventToSdlCode(e)` proto převádí reálný stisk klávesy z prohlížeče ve třech krocích:

1. **Přesný fyzický kód (`CODE_TO_SDL[e.code]`):** Zpracuje šipky (`273`–`276`), levé a pravé modifikátory (`ShiftRight` = `303`, `ShiftLeft` = `304`, `ControlRight` = `305`, `ControlLeft` = `306`, `AltRight` = `307`, `AltLeft` = `308`), speciální klávesy (`Space` = `32`, `Enter` = `13`…), interpunkci (`Period` = `46`, `Comma` = `44`…) a kompletní numerický blok (`Numpad0` = `256` až `NumpadEqual` = `272`).
2. **Číslice horní řady (`/^Digit[0-9]$/`):** Vrací ASCII kód `48 + n` – díky použití `e.code` místo `e.key` funguje spolehlivě i na české klávesnici (kde horní řada generuje `ě`, `š`, `č`, `ř`, `ž`…).
3. **Písmena (`/^Key[A-Z]$/`):** Pokud `e.key` obsahuje jedno ASCII písmeno (`^[a-zA-Z]$`), vezme jeho malé ASCII (`toLowerCase().charCodeAt(0)`), takže na české klávesnici QWERTZ přiřadí `Z` skutečně klávese `Z` a `Y` klávese `Y`. Pokud by uživatel měl zapnutou jinou abecedu, bezpečně spadne na fyzický kód z `e.code`.

### 3.5 Interaktivní přemapování (*key capture*), detekce kolizí a restart

Kliknutím na kterékoli z deseti tlačítek `.key-btn` v panelu se aktivuje režim zachytávání (`capturingTarget = { joy, dir, btn }`):

* Tlačítko dostane třídu `.listening` a popisek `"Stiskněte klávesu..."`.
* Globální listener `window.addEventListener("keydown", ..., true)` registrovaný v **capture fázi** (předběhne všechny ostatní posluchače včetně Emscriptenu) kontroluje `if (!capturingTarget || !e.isTrusted) return;` – příznak `e.isTrusted` zaručuje, že proces učení klávesy nemůže omylem zachytit syntetickou událost z gamepadu nebo dotyku.
* Ihned volá `e.preventDefault()` a `e.stopImmediatePropagation()`, takže zachycený stisk nepronikne do běžící hry.
* **Bezpečnostní pravidla při učení:**
  * `Escape` zruší zachytávání bez změny (`cancelCapture()`).
  * Funkční klávesy `F1`–`F12` jsou zamítnuty s upozorněním v `#joy-warning`, protože jsou vyhrazeny pro ovládání emulátoru `atari800`.
  * Klávesy mimo podporovanou sadu (`sdlCode === null`, např. `Meta` / `CapsLock`) se rovněž odmítnou s vysvětlením.

#### Průběžná detekce kolizí (`renderJoyUI`)

Při každé změně konfigurace provádí `renderJoyUI()` tři kontroly a případné varování vypíše do žlutého bloku `#joy-warning`:

1. **Vnitřní kolize Joy 1:** `new Set(j1Vals).size < j1Vals.length` (dvě akce na jedné klávese).
2. **Vnitřní kolize Joy 2:** totéž pro Joy 2 (jen pokud je `joyCfg.j2Enabled === true`).
3. **Křížová kolize Joy 1 $\cap$ Joy 2:** filtruje společné kódy mezi oběma joysticky a vypíše jejich čitelné názvy přes `sdlCodeToLabel()`.

#### Živé změny vs. změny vyžadující restart (`dirty` stav)

Protože `atari800` načítá klávesnicové mapování joysticků pouze při startu z `/atari800.cfg`, rozlišuje `hry.html` dva druhy nastavení:

* **Okamžité bez restartu:** Režim dotyku, rozložení `L/P`, styl D-padu (`8`/`4`), vibrace, zapnutí/vypnutí Gamepad API a velikost plátna.
* **Vyžadující restart emulátoru:** Změna kláves Joy 1, kláves Joy 2 nebo stavu `j2Enabled`. Funkce `kbdSnapshot(cfg)` vytváří jejich JSON otisk; jakmile `isRunning && kbdSnapshot(joyCfg) !== startedKbdSnapshot`, zobrazí se tlačítko **Použít a restartovat hru** (`#btn-apply-restart`), které uloží `joyCfg` do `localStorage` a obnoví stránku (`window.location.reload()`).

### 3.6 Ochrana zkratek prohlížeče a izolace UI ovládacích prvků

Aby hraní na desktopu nerušily výchozí akce prohlížeče a naopak aby klikání v panelu neovládalo hru na pozadí, existují tři jasně oddělené pojistky:

1. **Blokování systémových kláves během hry:** Množina `blokovaneKlavesy` obsahuje `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight` a `" "` (Mezerník). Na `window` v bubble fázi volá `e.preventDefault()`, pokud je událost fyzická (`e.isTrusted`), neběží zachytávání klávesy a cílovým prvkem **není** formulářový či interaktivní prvek (`INPUT`, `SELECT`, `TEXTAREA`, `BUTTON`, `A`). Díky tomu:
   * `F1` otevře menu `atari800` místo nápovědy prohlížeče,
   * `F5` provede Warm Reset Atari (a `Shift+F5` Cold Reset) místo reloadu stránky,
   * šipky a mezerník neposouvají okno prohlížeče.
2. **Izolace panelu a posuvníku:** `joyPanelEl` i `sizeSwitchEl` zastavují šíření události `keydown` (`e.stopPropagation()`), takže navigace v `<select>` nebo posouvání `#size-slider` klávesnicí neovlivňuje běžící hru.
3. **Automatický návrat fokusu a čistý `blur()`:** Každé tlačítko či rozbalovací seznam v horní liště i v panelu po aktivaci volá `.blur()` a u vybraných akcí vrací fokus zpět na `#canvas`, aby následný stisk `Mezerníku` nespustil znovu naposledy kliknuté tlačítko.

---

## 4. Sjednocená vrstva syntetických vstupů (`dispatchSynthKey`, SDL2 `SDL_TEXTINPUT`) a Gamepad API

Namísto zásahů do C zdrojových kódů `atari800` a exportování vlastních vstupních funkcí z WebAssembly zvolilo `hry.html` elegantní a zcela bezúdržbovou architekturu: **všechny neklávesnicové zdroje vstupu (dotykový D-pad, tlačítko `FIRE`, konzolová tlačítka, dotyková klávesnice Atari i USB/Bluetooth gamepady) se překládají na jednotné syntetické `KeyboardEvent` události doručované přímo na `<canvas>`**.

### 4.1 Překladová tabulka `SDL_TO_DOM`, `FKEY_TO_DOM` a `sdlCodeToDom`

Každý podporovaný SDL 1.2 kód se v `SDL_TO_DOM` (resp. přes pomocnou funkci `sdlCodeToDom(code)`) mapuje na čtyřčlenný DOM deskriptor:

```javascript
// Příklad záznamů v SDL_TO_DOM:
273: { key: "ArrowUp", code: "ArrowUp",      keyCode: 38, location: 0 },
305: { key: "Control", code: "ControlRight", keyCode: 17, location: 2 },
256: { key: "0",       code: "Numpad0",      keyCode: 96, location: 3 },
```

Význam jednotlivých polí pro Emscripten SDL2 vrstvu:

* `key` a `code`: Moderní identifikátory klávesy (pro `SDL_Scancode` a `SDL_Keycode`).
* `keyCode`: Starší numerický kód klávesy, ze kterého Emscripten v řadě cest stále odvozuje mapování.
* `location`: Kritický atribut pro rozlišení fyzicky odlišných kláves se stejným `keyCode` (`0` = standardní blok, `1` = levý modifikátor, `2` = pravý modifikátor, `3` = numerická klávesnice). Bez `location: 2` by např. `ControlRight` (`305`) nebyl rozeznán od `ControlLeft` (`306`).

Pro běžná písmena (`97`–`122`, tj. `a`–`z`) a číslice (`48`–`57`, tj. `0`–`9`) není nutné vypisovat tabulku ručně – `sdlCodeToDom()` je syntetizuje dynamicky (`KeyA`–`KeyZ`, `Digit0`–`Digit9`). Konzolové klávesy `F1`–`F6` a `Space` jsou uloženy odděleně v konstantě `FKEY_TO_DOM`.

### 4.2 Anatomie `makeSynthKeyEvent()` a `dispatchSynthKey()`

Vytvoření syntetické události v prohlížeči naráží na dvě zákeřné pasti, které `hry.html` explicitně ošetřuje:

#### Past 1: Read-only nulové `keyCode`, `which` a `charCode` u syntetických `KeyboardEvent`

Moderní prohlížeče (Chromium, WebKit, Gecko) podle specifikace UI Events ignorují vlastnosti `keyCode`, `which` a `charCode` předané v konstruktoru `new KeyboardEvent(...)` a nechávají je nastavené na `0`. Emscripten SDL2 na nich ale dodnes závisí. Funkce `makeSynthKeyEvent()` proto ihned po vytvoření události provádí přepis pomocí `Object.defineProperty`:

```javascript
if (ev.keyCode !== codeVal) {
    Object.defineProperty(ev, "keyCode", { get: () => codeVal });
}
if (ev.which !== codeVal) {
    Object.defineProperty(ev, "which", { get: () => codeVal });
}
if (type === "keypress" && ev.charCode !== charCode) {
    Object.defineProperty(ev, "charCode", { get: () => charCode });
}
```

#### Past 2: Chybějící textový vstup v SDL2 bez události `keypress` (`emitText`)

Jádro `atari800` se SDL2 rozlišuje dva typy vstupu:

* **Stisk fyzické klávesy (`SDL_KEYDOWN` / `SDL_KEYUP`):** Používá se pro emulaci joysticku, funkčních kláves (`F1`–`F6`), klávesy `ESC`, `ENTER`, `BACKSPACE` i kombinací s `CTRL`. Generuje se z DOM událostí `keydown` a `keyup`.
* **Znakový vstup (`SDL_TEXTINPUT`):** Vyžadují ho textové dotazy ve hrách (`Y`/`N`), zadávání jmen, Atari BASIC i samotná emulace některých znaků na klávesnici Atari. Emscripten SDL2 generuje `SDL_TEXTINPUT` až na základě DOM události **`keypress`** s nastaveným Unicode kódem `charCode` ($\ge 32$).

Proto má funkce `dispatchSynthKey(desc, isDown, mods = null, emitText = false)` čtvrtý parametr `emitText`:

```javascript
function dispatchSynthKey(desc, isDown, mods = null, emitText = false) {
    if (!desc || !isRunning) return;
    canvasEl.dispatchEvent(makeSynthKeyEvent(isDown ? "keydown" : "keyup", desc, mods, 0));

    if (isDown && emitText && !(mods && mods.ctrl) && desc.key && desc.key.length === 1) {
        const cp = desc.key.charCodeAt(0);
        if (cp >= 32) {
            canvasEl.dispatchEvent(makeSynthKeyEvent("keypress", desc, mods, cp));
        }
    }
}
```

* D-pad, `FIRE`, Gamepad API a funkční klávesy `F1`–`F6` volají `dispatchSynthKey` s `emitText = false` (nevytvářejí zbytečné textové události).
* Dotyková klávesnice Atari a tlačítko `Mezerník` volají `emitText = true`, takže při stisku tisknutelného znaku (bez `CTRL`) odešlou ihned po `keydown` také syntetický `keypress` s přesným `charCode`.

### 4.3 Podpora USB a Bluetooth ovladačů (Gamepad API)

Vestavěný překladač **Gamepad API** funguje shodně na stolních počítačích (Windows, Linux, macOS) i na mobilech s připojeným Bluetooth ovladačem (Xbox, PlayStation, 8BitDo, generické USB retro joysticky) a podporuje **až dva hráče současně**.

#### Aktivace a šetrnost k baterii i CPU

* Ve výchozím stavu je překlad vypnutý (`joyCfg.gamepadEnabled = false`). Dokud jej uživatel nezapne a není připojen alespoň jeden ovladač (`connectedGamepads.length > 0`), **neběží žádná `requestAnimationFrame` smyčka**.
* Připojení a odpojení ovladače zachycují události `gamepadconnected` a `gamepaddisconnected` volající `ensureGamepadLoop()`. Prohlížeče z bezpečnostních důvodů (ochrana proti fingerprintingu) odhalí připojený gamepad až po prvním stisku libovolného tlačítka na ovladači – na tuto skutečnost upozorňuje i stavový text v `#gp-status`.

#### Mapování os a tlačítek (`readGamepadDirections`)

| Funkce na Atari | Zdroj na 1. gamepadu (`pads[0]`) | Zdroj na 2. gamepadu (`pads[1]`, je-li J2 zapnut) |
| ----- | ----- | ----- |
| **Nahoru** | `buttons[12]` (D-pad ↑) nebo `axes[1] < -0.40` nebo alt HAT `axes[7] < -0.5` | stejně $\rightarrow$ `activeRunCfg.j2.up` |
| **Dolů** | `buttons[13]` (D-pad ↓) nebo `axes[1] > +0.40` nebo alt HAT `axes[7] > +0.5` | stejně $\rightarrow$ `activeRunCfg.j2.down` |
| **Doleva** | `buttons[14]` (D-pad ←) nebo `axes[0] < -0.40` nebo alt HAT `axes[6] < -0.5` | stejně $\rightarrow$ `activeRunCfg.j2.left` |
| **Doprava** | `buttons[15]` (D-pad →) nebo `axes[0] > +0.40` nebo alt HAT `axes[6] > +0.5` | stejně $\rightarrow$ `activeRunCfg.j2.right` |
| **Střelba (`FIRE`)** | libovolné z `buttons[0, 1, 2, 3, 5]` (A / B / X / Y / R1) | stejně $\rightarrow$ `activeRunCfg.j2.fire` |
| **START (`F4`)** | `buttons[9]` (Start / Options) | — |
| **SELECT (`F3`)** | `buttons[8]` (Select / Back / Share) | — |
| **OPTION (`F2`)** | `buttons[4]` (L1 / LB) | — |

Technické detaily implementace:

* **Analogová mrtvá zóna:** Konstanta `GP_DEADZONE = 0.40` spolehlivě odfiltruje samovolné ujíždění (*stick drift*) u opotřebovaných analogových páček.
* **Podpora nestandardních retro USB ovladačů:** Pokud ovladač nemá standardní mapování (`gp.mapping !== "standard"`), čte funkce navíc alternativní HAT osy `axes[6]` a `axes[7]` s prahem $\pm 0{,}5$.
* **Univerzální čtení tlačítek (`btnPressed`):** Kontroluje `b.pressed || b.value > 0.5`, takže funguje stejně dobře pro digitální mikrospínače i analogové spouště.
* **Hranová detekce (`gpPressedMap`):** Mapa uchovává aktuálně stisknuté virtuální klávesy (`g0_up`, `g0_fire`, `g0_start`…). Funkce `setGamepadVirtualKey()` posílá `keydown` výhradně na náběžné hraně (`!wasPressed && pressed`) a `keyup` výhradně na sestupné hraně (`wasPressed && !pressed`), čímž zabraňuje zahlcení fronty SDL událostí opakováním na každém snímku $60\text{ Hz}$ / $120\text{ Hz}$ displeje.
* **Prevence zaseknutých kláves (`releaseAllGamepadKeys`):** Jakmile dojde k odpojení ovladače, vypnutí přepínače, ztrátě fokusu okna (`window.blur`), skrytí záložky (`document.visibilitychange` $\rightarrow$ `document.hidden`) nebo zahájení učení klávesy (`capturingTarget`), smyčka okamžitě odešle `keyup` za všechny aktuálně držené směry i tlačítka. Totéž udělá selektivně pro `g1_*`, pokud uživatel za běhu odpojí druhý gamepad.
* **Čitelné jméno ovladače (`shortGamepadName`):** Odstraní technické přípony typu `(Standard Gamepad Vendor: 045e Product: 02ea)` regulárním výrazem `/\s*\([^)]*Vendor:[^)]*\)/gi` a zkrátí název na max. 34 znaků pro přehledné zobrazení v panelu i spodní liště.

---

## 5. Mobilní rozhraní, Fullscreen (včetně iOS Safari fallbacku) a dotyková klávesnice Atari

Mobilní zařízení přinášejí zcela odlišná omezení než desktop: malou úhlopříčku, dynamickou adresní lištu prohlížeče, výřezy v displeji (*notch / Dynamic Island*), absenci fyzické klávesnice a u iOS Safari i neexistenci nativního Fullscreen API pro běžné HTML prvky. `hry.html` proto implementuje samostatnou mobilní vrstvu, která bez jediné externí knihovny mění stránku v plnohodnotnou kapesní konzoli.

### 5.1 Detekce mobilního prostředí a přeskupení stránky mimo Fullscreen

Stránka používá dva nezávislé mediální dotazy:

* `mobileMq = window.matchMedia("(max-width: 820px), (max-height: 520px) and (pointer: coarse)")` – detekuje telefony na výšku i na šířku (včetně širokoúhlých telefonů, jejichž šířka na šířku přesahuje $820\text{ px}$, ale výška je pod $520\text{ px}$ a vstupem je prst).
* `coarseMq = window.matchMedia("(pointer: coarse)")` – společně s `navigator.maxTouchPoints > 0 || ("ontouchstart" in window)` tvoří funkci `isTouchDevice()`, která rozhoduje v režimu `touchMode === "auto"`.

Na mobilu mimo Fullscreen provede CSS přes `display: contents` na `.workspace` a vlastnost `order` kompletní přeskupení priorit odshora dolů (a povolí plynulé vertikální rolování `overflow-y: auto`):

1. **`order: 1` – `#stage` (obraz Atari):** Plná šířka displeje, černé pozadí bez paddingu, výška zastropovaná v `fitCanvas()` na $72\%$ viewportu.
2. **`order: 2` – `#mobile-fs-wrap`:** Výrazné černé tlačítko **⛶ Celá obrazovka (Fullscreen)** s minimální výškou $54\text{ px}$ pro okamžitý přechod do herního režimu jedním palcem.
3. **`order: 3` – `.help` s `.mobile-console-bar`:** Řada dotykových konzolových tlačítek (`START`, `SELECT`, `OPTION`, `Reset`, `␣ Mezerník`, `⌨ Klávesnice`, `Menu F1`) nad textovou nápovědou.
4. **`order: 4` – `#joy-panel`:** Panel nastavení ovládání je na mobilu rozbalený natrvalo pod hrou v plné šířce (skryjí se desktopové prvky `#size-switch`, `#btn-fullscreen`, `#btn-toggle-panel`, `#btn-close-panel`).
5. **`order: 5` – `.bar`:** Stavová lišta, tlačítko zpět na katalog a přepínače `SIO` / `BASIC` na samém konci stránky, kde nepřekážejí při hraní.

### 5.2 Nativní Fullscreen API + CSS pseudo-fullscreen pro iOS Safari

Přechod na celou obrazovku řídí funkce `enterFullscreenMode()` a `exitFullscreenMode()`:

```text
enterFullscreenMode()
  ├── cancelCapture() + zavře dotykovou klávesnici
  ├── Existuje stageEl.requestFullscreen / webkitRequestFullscreen?
  │     ├── ANO -> pokus o await req.call(stageEl)
  │     │     ├── úspěch -> po 80 ms fitCanvas(), fokus na #canvas
  │     │     └── výjimka (např. blokováno iOS) -> fallback níže
  │     └── NE  -> fallback níže
  └── CSS pseudo-fullscreen:
        document.documentElement.classList.add("is-pseudo-fs")
        (#stage: position: fixed; inset: 0; width: 100vw; height: 100dvh; z-index: 9999)
        -> po 50 ms fitCanvas(), fokus na #canvas
```

Klíčové detaily Fullscreen manažeru:

* **Podpora dynamického viewportu (`100dvh`) a bezpečných zón:** V `<meta name="viewport">` je nastaveno `viewport-fit=cover` a všechny okrajové ovládací prvky ve Fullscreenu využívají `max(..., env(safe-area-inset-top|right|bottom|left))`, takže tlačítka ani D-pad nikdy nezapadnou pod kameru, výřez ani domovskou lištu iOS/Androidu.
* **Jednotná detekce stavu:** `isFullscreenActive()` vrací `true` jak při nativním `document.fullscreenElement` / `webkitFullscreenElement`, tak při třídě `html.is-pseudo-fs`.
* **Čistý odchod z Fullscreenu:** Tlačítko `✕ Ukončit`, systémové gesto Zpět, nebo klávesa `Escape` (u pseudo-fullscreenu zachytávaná samostatně v `keydown` handleru) vyvolá `exitFullscreenMode()` a událost `fullscreenchange` vždy zavře dotykovou klávesnici a uvolní všechny držené dotyky (`releaseAllTouchKeys()`).

### 5.3 Čtyři adaptivní rozložení Fullscreenu (`syncStageFullscreenClasses`)

Funkce `syncStageFullscreenClasses()` při každé změně orientace či nastavení synchronizuje pět stavových tříd na prvku `#stage`: `fs-landscape`, `fs-portrait`, `touch-active`, `touch-dpad-right`, `touch-dpad-left`. Tím vznikají čtyři přesně vyladěné vizuální režimy:

| Režim (`#stage` třídy) | Typické zařízení | Rozložení obrazu a ovládacích prvků |
| ----- | ----- | ----- |
| **Na šířku bez dotyku** (`.fs-landscape`) | Desktop PC / notebook | Černé pozadí, obraz $4:3$ na $100\%$ výšky, nahoře vpravo jen plovoucí tlačítko `✕ Ukončit`. |
| **Na šířku s dotykem** (`.fs-landscape.touch-active`) | Mobil / tablet na šířku | Obraz $4:3$ vycentrovaný na plnou výšku. Na moderních $19:9$–$20:9$ telefonech vznikají po stranách černé okraje, do kterých přirozeně zapadnou **D-pad** a **FIRE** (dolní rohy, pozice podle `.touch-dpad-right` / `.touch-dpad-left`). Vlevo nahoře je nenápadná 2sloupcová mřížka konzolových tlačítek (`grid-template-columns: repeat(2, minmax(42px, 48px))`) s velmi nízkou opacitou (`rgba(255,255,255,0.08)`), aby při hraní neodváděla pozornost; vpravo nahoře malé `✕ Ukončit`. |
| **Na výšku bez dotyku** (`.fs-portrait`) | Monitor na výšku / tablet bez dotyku | Vycentrovaný obraz $4:3$ a horní tlačítko `✕ Ukončit`. |
| **Na výšku s dotykem** (`.fs-portrait.touch-active`) | Mobil na výšku (*handheld* styl) | `#stage` se přepne na svislý sloupec (`flex-direction: column`). Úplně nahoře pevná lišta `#fs-topbar` (`#0a0a0a`) se všemi konzolovými tlačítky a přepínači, hned pod ní obraz $4:3$ a celý zbývající prostor pod obrazem (`flex: 1 1 auto`) zabírá `#touch-pad-layer` s většími ovladači (D-pad `clamp(156px, 45vw, 206px)`, FIRE `clamp(98px, 28vw, 134px)`). Strany se prohazují jedním CSS pravidlem (`flex-direction: row-reverse` vs. `row`). |

#### Okamžité přepínače dostupné přímo ve Fullscreenu

Aniž by hráč musel opouštět Fullscreen nebo restartovat hru, má v horní liště k dispozici:

* **Konzolové klávesy Atari:** `START` (`F4`), `SEL` (`F3`), `OPT` (`F2`), `RST` (`F5`) a `␣ MEZERNÍK` (`Space`, ve 2sloupcové mřížce na šířku roztažený přes oba sloupce přes `.fs-space-btn`).
* **`⇄ L/P` (`#btn-swap-touch`):** Okamžitě prohodí ovladač a `FIRE` mezi konfigurací *joystick/klávesnice* (`dpad_right`: směry vpravo, `FIRE` vlevo) a *gamepad* (`dpad_left`: směry vlevo, `FIRE` vpravo).
* **`⌨ KLÁV` (`#btn-toggle-kbd`):** Zobrazí nebo skryje vestavěnou dotykovou klávesnici Atari.
* **`⊞ 8 SMĚR` / `✚ 4 SMĚR` (`#btn-dpad-style`):** Okamžitě přepne mezi 8tlačítkovým D-padem s rohovými diagonálami a 4tlačítkovým křížem s multitouch kombinací.
* **`〰 VIB: ZAP` / `〰 VIB: VYP` (`#btn-toggle-haptics`):** Okamžitě zapíná nebo vypíná asynchronní haptickou odezvu.

### 5.4 Dotyková klávesnice Atari (`#touch-kbd-overlay`)

Protože HTML `<canvas>` není textový vstup, mobilní prohlížeč u něj nikdy nevysune systémovou klávesnici – a i kdyby ano, zakryla by podstatnou část hry a neposkytovala by klávesy jako `CTRL`, `ESC`, `F1` či `HELP (F6)`. `hry.html` proto staví vlastní kompaktní klávesnici přímo nad spodní částí obrazovky.

#### Rozložení (`VK_ROWS`) a adaptace na nízké displeje

* **Hlavička:** Popisek `Klávesnice Atari` a rychlá tlačítka `Menu F1` (`F1`), `HELP` (`F6`) a `✕ Zavřít`.
* **5 řad kláves** generovaných dynamicky přes `DocumentFragment` v `buildVirtualKeyboard()`:
  1. `1`–`0` + `⌫` (`Backspace`, SDL `8`)
  2. `Q`–`P`
  3. `A`–`L` + `↵` (`Enter`, SDL `13`, modře zvýrazněný `.vk-enter`)
  4. `SHIFT` (modifikátor) + `Z`–`M` + `,` + `.`
  5. `ESC` (SDL `27`) + `CTRL` (modifikátor) + `MEZERNÍK` (SDL `32`, široký `.vk-space`) + `-` + `=` + `/`
* **Kompaktní režim na šířku (`@media (max-height: 430px)`):** Výška kláves se automaticky sníží ze $36\text{ px}$ na $30\text{ px}$ a mezery ze $4\text{ px}$ na $3\text{ px}$, aby zůstala dobře viditelná horní polovina obrazovky Atari.
* **Vzájemné vyloučení s D-padem:** Třída `#stage.kbd-open` zobrazí `#touch-kbd-overlay` a zároveň skryje `#touch-pad-layer` (`display: none !important`). Funkce `setTouchKbdOpen()` při otevření i zavření uvolní veškeré držené dotykové klávesy (`releaseAllTouchKeys()`).

#### Jednorázové (*one-shot / sticky*) modifikátory `SHIFT` a `CTRL`

Na dotykovém displeji je nepohodlné držet `SHIFT` jedním prstem a druhým hledat znak. Klávesy `SHIFT` a `CTRL` proto fungují jako přepínací jednorázové modifikátory (`vkMods = { shift: false, ctrl: false }`):

1. Klepnutím se modifikátor zapne a vizuálně rozsvítí (`.mod-active`).
2. Při stisku následující klávesy v `bindVirtualKeyButton()`:
   * Je-li aktivní `shift`, převede se písmeno na velké (`toUpperCase()`), nebo se číslice/symbol přemapuje podle `SHIFT_CHAR_MAP` (`1` $\rightarrow$ `!`, `2` $\rightarrow$ `@`, …, `/` $\rightarrow$ `?`).
   * Odešlou se syntetické `keydown` aktivních modifikátorů (`SDL_TO_DOM[304]` pro `ShiftLeft`, `SDL_TO_DOM[306]` pro `ControlLeft`).
   * Odešle se samotná klávesa s `emitText = true` (takže projde jak `keydown`, tak `keypress` s příslušným velkým/posunutým `charCode`).
   * Modifikátory se ihned automaticky vypnou (`resetVkMods()`), aby další znak už byl malý.
3. Při uvolnění prstu je zaručena **minimální doba stisku $90\text{ ms}$** ($\approx 4{,}5$ PAL snímku), po které `finishRelease()` uvolní nejprve samotnou klávesu a poté oba použité modifikátory v opačném pořadí (`CTRL`, pak `SHIFT`).

Stejný mechanismus minimální délky stisku $90\text{ ms}$, `setPointerCapture` a registrace nouzového uvolnění do množiny `activeButtonReleases` používají i všechna konzolová tlačítka (`[data-fkey]`: `START`, `SELECT`, `OPTION`, `RST`, `Mezerník`, `Menu F1`, `HELP`), takže ani velmi rychlé ťuknutí prstem na `START` nebo `Mezerník` nikdy nezůstane bez odezvy.

---

## 6. Dotykový D-pad, tlačítko FIRE a nízké latence

Ovládání akčních 8bitových her na dotykovém displeji je nejnáročnější částí celého `hry.html`. Klasické hry pro Atari (např. *River Raid*, *Dropzone*, *Boulder Dash*, *Montezuma's Revenge*, *Zybex*) byly navrženy pro čistě digitální mikrospínačový joystick **Atari CX40** s okamžitou reakcí v rytmu televizního snímku.

### 6.1 Fyzika časování emulátoru PAL ($50\text{ Hz}$)

Atari 130XE PAL generuje přesně $50$ snímků za sekundu, takže perioda jednoho snímku činí:

$$T_{\text{PAL}} = \frac{1}{50\text{ Hz}} = 20\text{ ms}$$

Jádro `atari800` v každém snímku vypumpuje frontu SDL2 událostí a teprve poté vyčte výsledný stav klávesových joysticků (pole `SDL_GetKeyboardState`). Z toho vyplývají dva zásadní důsledky pro návrh dotykového ovladače:

1. **Nebezpečí „neviditelného ťuknutí“:** Pokud hráč provede velmi krátké klepnutí prstem na `FIRE` nebo směr (např. $15\text{--}25\text{ ms}$) a události `keydown` i `keyup` dorazí mezi dvěma odečty emulátoru, výsledný stav ve chvíli čtení je opět `0` – emulátor stisk vůbec nezaregistruje.
2. **Citlivost na každou prodlevu na náběžné hraně:** Jakákoli umělá prodleva při *začátku* stisku (mrtvá zóna virtuální páčky, syntetizační zpoždění prohlížeče, blokující vibrace, překreslování DOM před odesláním události) posouvá reakci o jeden až dva celé PAL snímky ($+20$ až $+40\text{ ms}$), což hráč okamžitě vnímá jako „gumové“ ovládání.

### 6.2 Proč digitální SVG D-pad místo analogové virtuální páčky

Virtuální analogový „thumbstick“, který vyžaduje položit palec doprostřed a teprve pak jej táhnout za hranici mrtvé zóny, je pro 8bitové hry zásadně nevhodný – přidává mechanický čas tahu prstu a při rychlých změnách směru snadno mine diagonálu nebo naopak nechtěně sepne sousední osu.

`hry.html` proto používá **vektorový digitální D-pad** (`#touch-dpad-svg`, `viewBox="0 0 100 100"`) s nulovou středovou mrtvou zónou: každá část plochy okamžitě odpovídá přesnému směru bez nutnosti prstem kamkoli táhnout.

### 6.3 Geometrie vyhodnocení dotyků (`hitTestDpad`)

Pro každý dotyk o souřadnicích $(x, y)$ spočítá funkce normalizované souřadnice uvnitř čtverce D-padu:

$$n_x = \frac{x - \text{rect.left}}{\max(1, \text{rect.width})}, \qquad n_y = \frac{y - \text{rect.top}}{\max(1, \text{rect.height})}$$

$$d_x = n_x - 0{,}5, \qquad d_y = n_y - 0{,}5$$

#### Režim 1: `digital8` (8 tlačítek – výchozí)

Plocha D-padu je rozdělena na 4 rohové zóny pro přesné diagonály a 4 hlavní směrové sektory bez středové mrtvé zóny:

```text
  0.0       0.30              0.70       1.0
0.0 +---------+-----------------+---------+
    |   UL    |                 |   UR    |
    | (↑ + ←) |       UP        | (↑ + →) |
0.30+---------+   \         /   +---------+
    |               \     /               |
    |     LEFT        \ /      RIGHT      |
    |                 / \                 |
    |               /     \               |
0.70+---------+   /         \   +---------+
    |   DL    |      DOWN       |   DR    |
    | (↓ + ←) |                 | (↓ + →) |
1.0 +---------+-----------------+---------+
```

* Pokud bod spadá do rohu ($n_x < 0{,}30$ nebo $n_x > 0{,}70$ současně s $n_y < 0{,}30$ nebo $n_y > 0{,}70$), okamžitě se aktivuje příslušný **šikmý směr** (`ul`, `ur`, `dl`, `dr`).
* Všude jinde rozhoduje čisté porovnání $|d_x| \ge |d_y|$: pokud převažuje vodorovná odchylka, je aktivní `left` ($d_x < 0$) nebo `right` ($d_x \ge 0$); jinak `up` ($d_y < 0$) nebo `down` ($d_y \ge 0$). Neexistuje žádná mrtvá zóna uprostřed.

#### Režim 2: `digital4` (4 tlačítka – kříž + multitouch)

* CSS třída `#touch-dpad.dpad-mode-4 .dpad-diag { display: none; }` skryje 4 rohové prvky SVG, takže zůstane čistý kříž.
* Při **počátečním položení prstu** (`isInitialDown === true`) do prázdného rohu (hranice $0{,}295$ / $0{,}705$) vrací `hitTestDpad()` hodnotu `null` – zabrání tak nechtěnému sepnutí směru při opření dlaně vedle kříže.
* Při **tažení již položeného prstu** (`isInitialDown === false`) rohy neblokují, takže sklouznutí prstu přes okraj kříže nezpůsobí výpadek pohybu.
* Šikmých směrů lze v tomto režimu docílit přirozeným **současným stiskem dvou sousedních ramen kříže** (multitouch).

### 6.4 Multitouch a řešení protichůdných směrů (*SOCD – Last Input Priority*)

Mapa `dpadPointers` sleduje nezávisle všechny prsty položené na D-pad (klíč `"t:" + t.identifier` pro Touch Events, `"p:" + e.pointerId` pro Pointer Events). Pro každý prst ukládá dvojici `{ dirs, ts }`, kde `ts = performance.now()` je časové razítko poslední změny směru daného prstu.

Funkce `recomputeDpadFromPointers()` skládá výsledný stav všech aktivních prstů takto:

1. Pro každý ze 4 směrů najde nejnovější časové razítko napříč všemi prsty (`upTs`, `downTs`, `leftTs`, `rightTs`).
2. **Kolmé směry se čistě kombinují:** Drží-li jeden prst `up` a druhý `right`, oba jsou aktivní současně (výsledek = šikmo vpravo nahoru).
3. **Protilehlé směry řeší pravidlo *Last Input Priority (LIP)*:**

```javascript
const dirs = {
    up:    upTs >= 0 && upTs >= downTs,
    down:  downTs >= 0 && downTs > upTs,
    left:  leftTs >= 0 && leftTs >= rightTs,
    right: rightTs >= 0 && rightTs > leftTs
};
```

Pokud hráč rychle přebíhá zleva doprava tak, že položí prst na `right` o pár milisekund dříve, než stihne zvednout prst z `left`, nedojde k zablokování pohybu ani k neutrálu – vyhrává novější stisk (`rightTs > leftTs`), a jakmile původní prst zvedne, plynule pokračuje doprava. Stejně funguje i zpětný návrat po zvednutí novějšího prstu.

### 6.5 Sedm pilířů inženýrství nízké latence v `hry.html`

Aby ovládání na mobilu působilo co nejblíže fyzickému joysticku, spojuje `hry.html` sedm cílených optimalizací:

#### 1. Přímé nativní Touch Events na mobilu + Pointer Events pro myš

Na dotykových displejích obsluhují `#touch-dpad` i `#touch-fire` přímo nativní události **`touchstart`**, **`touchmove`**, **`touchend`** a **`touchcancel`** s parametrem `{ passive: false }` a okamžitým `e.preventDefault()`:

* Obcházejí tak syntetizační vrstvu Pointer Events a eliminují zpoždění vyhodnocování systémových gest (double-tap zoom, scrolling, výběr textu, dlouhý stisk).
* Pro možnost testovat a používat dotykový ovladač i na desktopu myší nebo stylusem (v režimu `touchMode = "always"`) zůstávají registrovány i `pointerdown` / `pointermove` / `pointerup` / `pointercancel` / `lostpointercapture`, ale každý z těchto handlerů začíná strážní podmínkou:
  ```javascript
  if (e.pointerType === "touch") return;
  ```
  Tím je zaručeno, že na mobilu nikdy nedojde ke zdvojení událostí.

#### 2. Input-first pořadí operací (emulátor má absolutní přednost před UI)

V `applyDpadDirections()` i `pressFire()` je striktně dodrženo třífázové pořadí:

1. **Okamžité odeslání syntetických kláves do emulátoru** (`setTouchVirtualKey(...)` $\rightarrow$ `dispatchSynthKey(...)`).
2. **Aktualizace vizuálního stavu** (`updateDpadVisuals()` / `.classList.add("pressed")`).
3. **Volitelná asynchronní haptika** (`hapticPulse(...)`).

Emulátor tak dostane změnu směru nebo výstřel ještě před tím, než prohlížeč začne počítat překreslení zvýrazněného SVG tlačítka.

#### 3. Kešování geometrie D-padu bez vynuceného reflow (`dpadCachedRect`)

Volání `element.getBoundingClientRect()` uvnitř vysokofrekvenční události `touchmove` (až $120\text{--}240\text{ Hz}$ na moderních telefonech) může vyvolávat *forced synchronous layout*. `hry.html` proto měří rozměry D-padu pouze při položení prstu (`refreshDpadRect()` v `touchstart`) a během tažení čte kešovaný obdélník `dpadCachedRect`. Keš se automaticky invaliduje při jakékoli změně velikosti nebo orientace (`fitCanvas()`) a při uvolnění všech dotyků (`releaseAllTouchKeys()`).

#### 4. Eliminace CSS zpoždění a prohlížečových artefaktů

Herní prvky (`#touch-pad-layer`, `#touch-dpad`, `#touch-fire`) záměrně nepoužívají žádné `transition` animace – vizuální odezva je okamžitá v rámci jednoho snímku. Současně mají natvrdo potlačené veškeré rušivé interakce prohlížeče:

* `touch-action: none` (vypíná scroll i pinch-zoom přímo v kompozitoru),
* `user-select: none` a `-webkit-user-select: none`,
* `-webkit-touch-callout: none` (blokuje kontextovou bublinu na iOS při dlouhém držení `FIRE`),
* `-webkit-tap-highlight-color: transparent`,
* `touchPadLayerEl.addEventListener("contextmenu", (e) => e.preventDefault())`.

#### 5. Asymetrická pulzní garance ($0\text{ ms}$ náběh a změna směru, $\ge 2$ PAL snímky při uvolnění)

```text
Stisk / změna směru:  [prst položen] ── 0 ms ──> keydown v emulátoru (okamžitě!)
                                                 + ruší jakýkoli běžící releaseTimer

Rychlé ťuknutí (< 45 ms u D-padu / < 50 ms u FIRE):
                      [prst zvednut v t = 18 ms]
                         ├── vizuál tlačítka zhasne OKAMŽITĚ (t = 18 ms)
                         └── logický keyup se pozdrží o (45 - 18) = 27 ms
                             -> v t = 45 ms (> 2 PAL snímky) odešle keyup
                             -> emulátor zaručeně zachytí impuls!

Dlouhé držení (>= 45 ms / 50 ms) nebo touchcancel / blur:
                      [prst zvednut] ── 0 ms ──> vizuál i keyup OKAMŽITĚ
```

* Konstanty jsou dimenzovány těsně nad dva PAL snímky ($2 \times 20\text{ ms} = 40\text{ ms}$): **`TOUCH_DPAD_MIN_MS = 45`**, **`TOUCH_FIRE_MIN_MS = 50`**.
* **Zásadní detail:** U D-padu se pulzní garance uplatňuje **výhradně při přechodu ze směru do neutrálu (`0000`)**. Přechod z jednoho směru přímo na jiný (`nextKey !== "0000"`) ruší případný `dpadReleaseTimer` a aplikuje nový směr s latencí **$0\text{ ms}$**.

#### 6. Multitouch odolnost tlačítka `FIRE` (`firePointers`)

Stav tlačítka `FIRE` se neřídí jediným booleanem, ale množinou `firePointers = new Set()`. Každý dotyk má vlastní ID (`"t:" + id` / `"p:" + id`):

* `keydown` se vyšle jen při přechodu z $0 \rightarrow 1$ prst (`wasEmpty`),
* zvednutí jednoho ze dvou prstů na tlačítku nepřeruší střelbu (`if (firePointers.size > 0) return`),
* rychlé opětovné klepnutí během doby doběhu `fireReleaseTimer` časovač zruší bez zbytečného výpadku.

#### 7. Volitelná asynchronní haptika (`hapticPulse`)

Na některých Android zařízeních volání `navigator.vibrate()` krátce blokuje hlavní JS vlákno (IPC volání do systémového vibrátoru). Proto:

1. Ve výchozím stavu jsou vibrace **vypnuté** (`joyCfg.touchHaptics = false`), aby měl hráč zaručenu maximální rychlost reakce.
2. Po zapnutí se každá vibrace odkládá přes `setTimeout(() => { try { navigator.vibrate(ms); } catch (_) {} }, 0)`, takže nikdy nezdrží odeslání vstupu do WebAssembly.
3. Délka impulzu je jemně odstupňována podle významu akce: $8\text{ ms}$ pro změnu směru na D-padu a klávesy, $10\text{ ms}$ pro přepínače rozložení/režimu a $12\text{ ms}$ pro stisk `FIRE` (a zpětnou vazbu při zapnutí vibrací).

---

## 7. Vývojářský referenční přehled

### 7.1 Přehled časovacích a prahových konstant

| Konstanta / hodnota | Hodnota | Účel |
| ----- | ----- | ----- |
| `ASPECT` | $4 / 3$ | Fixní poměr stran obrazovky Atari 130XE PAL (`672 x 480` framebuffer). |
| `MIN_SCALE` / `MAX_SCALE` | $30\%$ / $100\%$ | Rozsah uživatelského škálování na desktopu (krok posuvníku $5\%$, krok tlačítek $\pm 10\%$). |
| `TOUCH_DPAD_MIN_MS` | $45\text{ ms}$ | Minimální délka impulzu D-padu při uvolnění do neutrálu ($\ge 2{,}25$ PAL snímku). Změna směru = $0\text{ ms}$. |
| `TOUCH_FIRE_MIN_MS` | $50\text{ ms}$ | Minimální délka impulzu tlačítka `FIRE` při rychlém klepnutí ($2{,}5$ PAL snímku). |
| Minimální stisk `[data-fkey]` a `VK` | $90\text{ ms}$ | Spolehlivá registrace `START`, `SELECT`, `OPTION`, `RST`, `Mezerníku` a kláves dotykové klávesnice. |
| `GP_DEADZONE` | $0{,}40$ | Mrtvá zóna hlavní analogové páčky Gamepad API (alternativní HAT osy používají práh $0{,}50$). |
| Rohové zóny `digital8` / `digital4` | $0{,}30$ / $0{,}295$ | Normalizovaná šířka a výška rohových zón D-padu. |
| Zpoždění `fitCanvas()` | $50 / 60 / 80 / 100 / 120\text{ ms}$ | Doběh animací pseudo-fullscreenu, nativního fullscreenu, inicializace SDL2 a otočení displeje (`orientationchange`). |

### 7.2 Klíče v `localStorage`

| Klíč | Typ / formát | Výchozí stav | Co ukládá |
| ----- | ----- | ----- | ----- |
| `atari800_joy_cfg_v1` | JSON objekt | `DEFAULT_JOY_CFG` | Mapování `j1`, `j2`, `j2Enabled`, `gamepadEnabled`, `touchMode`, `touchLayout`, `touchDpadStyle`, `touchHaptics`. |
| `atari800_joy_panel_open` | `"1"` \| `"0"` | `"1"` pro šířku $\ge 960\text{ px}$ | Zda je pravý konfigurační panel na desktopu otevřený. |
| `atari800_scale` | celé číslo (`"30"`–`"100"`) | `"100"` | Zvolené měřítko obrazovky Atari na desktopu (ignorováno v `embed` režimu). |

### 7.3 Přehled CSS stavových tříd

| Element | Třída | Význam |
| ----- | ----- | ----- |
| `<html>` | `mode-embed`, `mode-embed-min` | Vložený režim `embed=1` (bez ovládacího UI) a minimální `embed=2` (bez nápovědy a paddingu). |
| `<html>` | `is-pseudo-fs` | Aktivní CSS pseudo-fullscreen fallback (např. iOS Safari). |
| `#stage` | `fs-landscape`, `fs-portrait` | Aktivní Fullscreen v orientaci na šířku nebo na výšku. |
| `#stage` | `touch-active` | Ve Fullscreenu jsou zobrazeny dotykové ovladače a konzolová tlačítka. |
| `#stage` | `touch-dpad-right`, `touch-dpad-left` | Stranové rozložení D-padu a `FIRE` (joystick vs. gamepad). |
| `#stage` | `kbd-open` | Otevřená dotyková klávesnice Atari (automaticky skrývá `#touch-pad-layer`). |
| `#touch-dpad` | `dpad-mode-4` | Skryje 4 rohové diagonální prvky `.dpad-diag` pro 4tlačítkový kříž. |
| `.dpad-pad`, `#touch-fire`, `.vk-key`, `.fs-mini-btn` | `active`, `pressed`, `mod-active` | Okamžité vizuální zvýraznění stisknutého směru, tlačítka nebo aktivního sticky modifikátoru. |
| `#joy-panel`, `.joy-card`, `.key-btn` | `hidden`, `disabled`, `listening` | Skrytí panelu na desktopu, zašednutí vypnuté karty (Gamepad / Joy 2) a aktivní zachytávání klávesy. |

### 7.4 Bezpečnostní pojistky proti zaseknutým klávesám

Všechny stavy syntetických vstupů jsou centralizovaně čištěny funkcemi `releaseAllTouchKeys()` (maže časovače, mapy pointerů, `touchPressedMap` i všechny registrované `activeButtonReleases`) a `releaseAllGamepadKeys()` (uvolňuje `gpPressedMap`). Spouštějí se automaticky při každé potenciálně rizikové události:

* ztráta fokusu okna (`window.addEventListener("blur", ...)`),
* přepnutí na jinou kartu prohlížeče nebo minimalizace (`document.visibilitychange` při `document.hidden === true`),
* opuštění Fullscreenu (`exitFullscreenMode`, `fullscreenchange`, `webkitfullscreenchange`),
* otevření či zavření dotykové klávesnice (`setTouchKbdOpen`),
* přepnutí stran ovladače (`#btn-swap-touch`) nebo stylu D-padu (`#btn-dpad-style`, `#touch-dpad-style`),
* přerušení dotyku systémem (`touchcancel`, `pointercancel`, `lostpointercapture`),
* odpojení gamepadu, vypnutí Gamepad API nebo zahájení učení klávesy (`capturingTarget`).