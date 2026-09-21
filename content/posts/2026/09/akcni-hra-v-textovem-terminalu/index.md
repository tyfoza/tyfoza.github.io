---
title: "Space 68K Invaders"
date: 2026-08-23T15:07:04+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k", "Počítače.hry"]
draft: false
math: true
---
**Space 68K Invaders** je můj pokus o adaptaci klasické arkádové
střílečky z roku 1978. Napsáno v Alcyon C,
kompilováno a linkováno na procesoru a pro procesor Motorola 68008.
Běží na jednodeskovém homebrew počítači 68k-MBC pod operačním systémem
CP/M-68K.

V článku řeším problematiku optimalizace hry pro textový terminál.

Přestože 16/32bitový procesor taktovaný na frekvenci 8 MHz poskytuje pro
podobný typ hry více než dostatečný výpočetní výkon, narazili jsme se
jiný problém: odezva komunikačního rozhraní.

V prostředí CP/M-68K typicky neexistuje přímý přístup do grafické paměti
(VRAM) displeje. Veškerý vizuální výstup je odesílán jako proud ASCII
znaků a escape sekvencí na připojený terminál (standardu VT100)
prostřednictvím sériové linky RS232. Tento způsob komunikace, často na
rychlosti 115 200 baudů, znamená, že prosté překreslení celé obrazovky o
velikosti 24 řádků a 80 sloupců trvá z pohledu interaktivní hry
neakceptovatelně dlouho. Tradiční přístup k programování her (vymazání
obrazovky a vykreslení nové scény) zde proto naprosto selhává a vede k
masivnímu zpoždění (lagu) a výraznému blikání (flickeringu) pohybujících
se objektů.

{{< youtube 2OJufu2bbsM >}}

# Fyzikální limity VT100 a RS232

Úzkým hrdlem při vývoji her pro terminál je sériová linka RS232. Oproti
klasickým 8bitovým počítačům s přímým přístupem do video paměti (VRAM)
musí 68k-MBC odesílat veškeré grafické změny sekvenčně. Zvolená
komunikační rychlost je 115 200 baudů. Ačkoliv se to v kontextu retro
počítačů jeví jako velmi rychlé připojení, pro interaktivní plynulé
překreslování herní scény představuje tvrdý limit.

Při standardním nastavení sériového přenosu 8N1 (1 start bit, 8 datových
bitů, 1 stop bit bez parity) trvá přenos jednoho znaku přesně 10 bitů.
Maximální teoretická propustnost sériové linky je tedy:

$$\frac{115200}{10} = 11520\text{ znaků za sekundu }$$

Pro dosažení akceptovatelné plynulosti animace odezvy ovládání bychom
měli cílit alespoň na 30 snímků za sekundu (FPS). Z toho přímo vyplývá
náš striktní "datový rozpočet" na odeslání jednoho herního snímku:

$$\frac{11520}{30} = 384\text{ bajtů na snímek }$$

## Spoustu přenosu sežerou ESCAPE sekvence

K přenosovému limitu se přidává masivní režie samotného terminálu VT100.
Zatímco v přímé paměti by změna pozice znamenala pouze zápis do jiného
bytu v RAM, u sériového terminálu je k umístění kurzoru na konkrétní
souřadnice nutné odeslat escape sekvenci ve formátu `ESC [ y ; x H`.

V jazyce C to odpovídá odeslání následujících znaků:

-   `ESC` (ASCII hodnota 27, 1 bajt)

-   `[` (1 bajt)

-   `y` (souřadnice řádku, 1 až 2 bajty)

-   `;` (1 bajt)

-   `x` (souřadnice sloupce, 1 až 2 bajty)

-   `H` (1 bajt)

Tedy pouhé **přesunutí kurzoru stojí 6 až 8 bajtů** a to jsem ještě
nevytiskli jediný znak.

## Matematika naivního přístupu

Pokud bychom hru programovali klasickým způsobem, kde se každý objekt
pohybuje a překresluje nezávisle na ostatních, museli bychom při každém
posunu roje ufonů (40 objektů) provést následující kroky:

1.  Přesunout kurzor na starou pozici ufona (průměrně 8 bajtů).

2.  Vytisknout dvě mezery pro smazání staré stopy (2 bajty).

3.  Přesunout kurzor na novou pozici ufona (průměrně 8 bajtů).

4.  Vytisknout dva znaky nového tvaru ufona (2 bajty).

Na posun a překreslení jednoho ufona bychom tedy v průměru spotřebovali
20 bajtů. Pro celý roj to znamená:

$$40\text{ ufonů } \times 20\text{ bajtů } = 800\text{ bajtů na jeden krok ufonského roje }$$

Těchto 800 bajtů masivně překračuje náš rozpočet 384 bajtů na snímek.
Výsledkem tohoto "naivního" přístupu je rozpad zobrazení a extrémní
latence.

Fyzikální limit ukázal, že hrubá výpočetní síla procesoru nehraje roli,
dokud nevyřešíme propustnost linky. Zjištění si tak vynutilo kompletní
opuštění standardního přístupu k renderování a urychlení pomocí technik
pracujících s řádkovými buffery.

# Delta Rendering a Line Buffering

Jak radikálně minimalizovat množství dat odesílaných na terminál. Prvním
a nejčastějším krokem v podobných situacích je **Delta rendering** s
využitím virtuální obrazovky (VRAM). V případě stroje 68k-MBC se ovšem i
tento standardní přístup ukázal jako problematický.

## Slepá ulička: Dvojitý VRAM buffer

Původní návrh herního enginu pracoval se dvěma kompletními maticemi o
velikosti 24x80 znaků (`vram` a `ovram`) umístěnými v paměti RAM. Herní
logika v každém kroku překreslila celou scénu (loď, ufony, střely i
štíty) do primárního bufferu `vram`. Následně se spustila renderovací
funkce, která vnořeným cyklem porovnávala oba buffery znak po znaku. Na
sériový port se odeslaly pouze ty znaky, které se od předchozího snímku
změnily, a nakonec se aktuální stav překopíroval do záložního bufferu
`ovram`.

Ačkoliv tento přístup dokonale vyřešil problém s propustností RS232 a
zcela eliminoval blikání obrazu (flickering), narazil na fatální limit
samotného procesoru. Zpracování a porovnání celých dvou matic
($24 \times 80 = 1920$ znaků) v každém snímku vyžadovalo obrovské
množství paměťových přístupů. Historický překladač Alcyon C navíc
generoval pro výpočet indexů u dvourozměrných polí značně neoptimální
strojový kód s množstvím interního násobení.

Procesor Motorola 68000 na frekvenci 8 MHz tak strávil statisíce
hodinových taktů pouhým prohledáváním prázdného (černého) místa na
obrazovce. Výpočetní zátěž CPU byla natolik enormní, že navzdory volné
sériové lince klesla plynulost hry na nehratelnou úroveň. Koncept
kompletní VRAM musel být opuštěn.

## Přechod na Line Buffer (Řádkový buffer)

Cílem bylo zachovat výhody Delta renderingu (eliminace blikání a
minimální přenos dat), ale zbavit procesor nutnosti iterovat přes
prázdná místa obrazovky. Řešením se stala hybridní technika využívající
jediný jednorozměrný textový řetězec: `char lbuf[81]`.

Kreslení roje ufonů -- největší zátěž celého systému -- bylo převedeno
na dynamické skládání řetězců po celých herních řádcích:

1.  **Výpočet rozsahu:** Hra nejprve v dané řadě zjistí pozici nejvíce
    levého a nejvíce pravého žijícího ufona. Tím ohraničí aktivní zónu,
    kde se dějí změny.

2.  **Gumovací blok:** Zjistí se počátek zápisu (`s_x`), který
    zohledňuje minulou i novou souřadnici celého roje. V poli `lbuf` se
    následně vyčlení potřebný blok o šířce `w`, který se kompletně
    vyplní ASCII znaky pro mezeru.

3.  **Vložení ufonů:** Herní smyčka projde žijící ufony v daném řádku a
    vloží jejich grafické reprezentace (např. `][`) do tohoto
    ohraničeného řetězce z mezer na příslušné relativní offsety.

4.  **Jediný přenos přes RS232:** Na terminál se odešle pouze jedna
    povelová VT100 sekvence pro posun kurzoru (`goto_yx`) na začátek
    bloku a ihned poté se vypíše celý sestavený řetězec `lbuf`.

### Extrémní optimalizace paměti: Pointer Copy

I když Line Buffer drasticky snížil zátěž sériové linky, samotná
příprava tohoto bufferu v paměti představovala pro 8MHz procesor
zpočátku skrytý problém. Před vykreslením aktuálního stavu roje bylo
nutné vyčleněný blok pole `lbuf` pokaždé vymazat vložením mezer.
Klasický přístup v jazyce C k tomuto úkolu využívá indexovaný cyklus
`for`:

``` c
for (i = 0; i < w; i++) lbuf[i] = ' ';
```

Přestože se tento zápis zdá na první pohled triviální, z hlediska
strojového kódu znamená pro procesor velkou zátěž. V každém z až 30
kroků musí CPU inkrementovat proměnnou `i`, porovnat ji s `w`, vypočítat
paměťovou adresu (sečíst bázi pole `lbuf` + offset `i`) a teprve poté
zapsat znak do paměti. U kompilátoru Alcyon C to generovalo pomalý a
neefektivní kód. Abychom procesoru ulevili, nahradili jsme tento přístup
přímou ukazatelovou aritmetikou (Pointer Copy). V globální paměti bylo
vytvořeno statické pole spaces předvyplněné 80 mezerami. Samotné
"gumování" bufferu nyní obstarává dedikovaná funkce, která přesouvá
bloky paměti pomocí inkrementace ukazatelů:

``` c
copy_spaces(dest, len)
char *dest;
int len;
{
    char *s = spaces;
    while(len--) *dest++ = *s++;
    *dest = '\0';
}
```

Tento zápis C kompilátorům velmi vyhovuje. Procesor Motorola 68000 je
hardwarově navržen pro bleskovou manipulaci s adresami. Výraz
`*dest++ = *s++` se na úrovni assembleru přeloží do několika málo
instrukcí s využitím interního post-inkrementu adresových registrů
(typicky instrukce `move.b (a0)+, (a1)+`). Díky tomu se čištění bufferu
odehrává plynule a bez jakéhokoliv počítání paměťových offsetů.

### Hratelný výsledek

Kombinace Line Bufferu a optimalizovaného přístupu k paměti je pro CP/M
ideální z několika důvodů:

-   **Deltu řeší textový přepis:** Mezery nakopírované do řetězce `lbuf`
    na pozicích, kde ufon stál v předchozím snímku, automaticky
    "vygumují" starou stopu. Vykreslení a smazání proběhne v jediném
    okamžiku. Obraz absolutně nebliká.

-   **Minimalizace režie RS232:** K překreslení deseti ufonů letících v
    jedné řadě již není potřeba deseti samostatných escape sekvencí
    (které by zabraly cca 80 bajtů). Systém použije jen jedinou navigaci
    kurzoru na začátek řetězce, což srazilo datovou zátěž linky takřka
    na třetinu.

-   **Menší zátěž procesoru:** Tím, že pracujeme pouze s absolutním
    ohraničením aktuálně žijících ufonů a obyčejným jednorozměrným polem
    přes rychlé ukazatele, klesla zátěž CPU na absolutní minimum.

# Ochrana proti extrémního zrychlení na konci

Specifickým neduhem historických arkádových her, proslaveným právě
původními Space Invaders, je nechtěné zrychlování hry v závislosti na
úbytku nepřátel na obrazovce.

S tím, jak hráč postupně ničí ufony, zkracuje se délka řetězce
odesílaného přes sériovou linku v rámci Line Bufferu. Pokud je zničen
celý sloupec ufonů (nebo ufon na samém kraji), program díky proměnným
`min_c` a `max_c` dokonce fyzicky zúží aktivní vykreslovací zónu.
Jakmile na obrazovce zůstane například pouze jediný ufon, procesor
M68000 a sériový port sestaví a přenesou pouze minimální zlomek dat
oproti startu úrovně. Vzhledem k tomu, že herní engine nepoužívá fixní
časování ukotvené na reálný čas (např. pomocí hardwarových přerušení od
časovače), ale běží v neomezené iterativní smyčce, zkrácení doby
renderování znamená, že celý cyklus proběhne řádově rychleji. Zbývající
ufoni se tak začnou pohybovat nehratelně rychle a poslední nepřítel se
stane prakticky netrefitelným.

## Lineární a pak nelineární kompenzace

Na konci každé herní smyčky se přidá "pálení" procesorových cyklů pomocí
prázdné smyčky `(while (delay--) { })`. Hodnota zpoždění se dynamicky
vypočítává na základě aktuální hodnoty proměnné `alive` (počet žijících
ufonů). Základní složka zpoždění roste lineárně s počtem zničených
nepřátel. Za každého chybějícího ufona se k celkovému zpoždění přidá
drobná penalizace: `extra = (40 - alive) * 10L;`\
Tento lineární růst se však ukázal jako nedostatečný v momentech, kdy
stav nepřátel klesne na kritické minimum. V tento okamžik klesne režie
RS232 linky natolik strmě, že lineární vzorec rychlost procesoru
neudrží.

Proto byla do kódu přidána skoková (nelineární) zátěž: Při poklesu na 5
a méně ufonů se k brzdě fixně přičte zdržení o hodnotě 150L. Při poklesu
na 2 a méně ufonů se přidá dalších 300L. Tento nelineární nárůst
čekacích cyklů uměle simuluje časovou ztrátu, jakou by jinak
představovalo vykreslování kompletního roje a průchod dlouhého řetězce
RS232 linkou. Výsledkem je rozumně plynulá a predikovatelná rychlost
invaze od prvního kobercového bombardování až po dramatický souboj s
posledním přeživším nepřítelem.

# Detekce kolizí a sestřelování střel

V arkádových střílečkách patří detekce kolizí (vyhodnocování průniku
hitboxů) k výpočetně nejexponovanějším částem kódu. V prostředí s
omezeným výkonem CPU, jakým je Motorola 68000 při vykreslování na pomalý
terminál, máme kolize pečlivě optimalizované a rozdělené do tří
odlišných přístupů podle toho, s jakým objektem se střela potká.

## Kolize s rojem ufonů: Algoritmus Bounding Box

První verze enginu testovala kolize tak, že při každém posunu střely
procházela celou stavovou matici ufonů a\[4\]\[10\] pomocí dvou
vnořených for cyklů. Pro každý průběh se musela spočítat absolutní
pozice ufona z tabulky a porovnat se souřadnicemi střely. Při hře, která
běží přes 30 snímků za sekundu a má na obrazovce až 4 střely současně,
to pro procesor znamenalo provádět nespočet zbytečných iterací a výpočtů
i v případě, že všechny střely letěly prázdným prostorem. Pro extrémní
odlehčení CPU byla proto do enginu implementována technika Bounding Box
(ohraničující obdélník). Vzhledem k tomu, že známe přesnou kotevní
souřadnici celého roje (ax, ay), jeho výšku (4 řádky) a maximální šířku
(30 znaků), nemusíme donekonečna iterovat matici a testovat jednotlivé
ufony. Místo toho se provede jediná rychlá matematická kontrola: nachází
se střela hráče vůbec uvnitř velkého ohraničujícího obdélníku patřícího
roji?

``` c
if (by >= ay && by < ay + 4) {
    if (bx >= ax && bx < ax + 30) {
        /* Střela je uvnitř! Nyní lokalizujeme cíl. */
```

Pokud střela letí mimo roj, procesor ufony v daném cyklu zcela ignoruje,
čímž ušetří drtivou většinu strojového času. Pokud střela do obdélníku
fyzicky vletí, program přejde k okamžité matematické lokalizaci cíle bez
cyklů:Vypočítá se relativní pozice střely vůči levému hornímu rohu roje:
`rel_x = bx - ax` a `rel_y = by - ay`. Z X-ové souřadnice se určí index
zasaženého sloupce. Abychom se vyhnuli systémově velmi drahému dělení
(případně instrukci modulo `%`), využívá C kód jednoduchou odčítací
smyčku (protože ufoni mají fixní rozestup 3 znaky).

Následně se program jednoduše a cíleně podívá do matice na index
`a[rel_y][sloupec]`. Pokud zde ufon žije, je označen za zničeného a na
jeho zrekonstruované absolutní souřadnice `(ax + c3[sloupec])` je
okamžitě odeslána VT100 animace exploze.

Tento geometrický a matematický průnik srazil časovou složitost kolizí
na naprosté minimum a odstranil z herní smyčky největší zátěž pro ALU
jednotku procesoru.

## Kolize se štíty

Přístup s časovou složitostí $O(1)$

Naprosto odlišný přístup vyžadují
klasické ochranné štíty (bunkry). Protože jsou štíty statické a
nepohybují se, byla by iterace přes jejich jednotlivé bloky zbytečným
plýtváním výkonu. Místo toho využívá hra dostupnou paměť 68k-MBC a drží
si přesnou ASCII mapu dvou řádků štítů (na souřadnicích Y=20 a Y=21) ve
dvoudimenzionálním poli `char shld[2][81]`  .

Když hráčova nebo nepřátelská střela dosáhne výšky 20 nebo 21, hra
nepočítá žádné složité průniky. Pouze se přímo podívá do pole na index
odpovídající X-ové souřadnici střely. Pokud se na daném místě nachází
jakýkoliv znak (maso štítu, typicky `#` nebo `/`), střela je zničena a
do pole je na její místo zapsána mezera. Na terminál se následně odešle
povel k vymazání tohoto jediného znaku. Tento přístup funguje v
konstantním čase $O(1)$ a pro procesor nepředstavuje prakticky žádnou
zátěž.

## Sestřelování nepřátelských bomb

Specifickým oživením hratelnosti je možnost sestřelit nepřátelskou bombu
ve vzduchu. Ufoni mohou díky dynamické kadenci shodit až 3 bomby
současně `(abx[0..2], aby[0..2])`. Systém v každém cyklu kontroluje, zda
nedošlo k protnutí hráčovy letící střely s některou z padajících bomb.

Prostorová tolerance bomby je mírně rozšířena. Aby se
vykompenzoval pohyb o celé diskrétní znaky na terminálu, hra vyhodnocuje
zásah i v případě, že se střely minou o pouhý jeden znak v jakékoliv
ose. V případě intercepce se obě střely vzájemně vyruší a hráči je
připsán drobný bodový bonus za defenzivní zásah.

## Pasti kompilátoru Alcyon C

Zanořování podmínekPři implementaci výše zmíněných kolizních detekcí
(zejména u protínání střel) jsme narazili na kritický historický bug
překladače Alcyon C. Běžný C kód pro detekci průniku obdélníků vypadá
následovně:

``` c
if (by != -1 && aby != -1 && bx >= abx - 1 && bx <= abx + 1 && ...) {
    /* Zásah */
  }
```

Pokud je však takto složitá a dlouhá logická konstrukce předložena
překladači Alcyon C, jeho interní generátor kódu v kombinaci se
zkráceným vyhodnocováním (short-circuit evaluation) zkolabuje. Fáze
assembleru (AS68) vygeneruje dvě stejná skoková návěští a proces
překladu spadne s chybou label redefined. Z tohoto důvodu je kompletní
detekce kolizí v enginu Space 68K Invaders napsána stylem hlubokého
zanořování do izolovaných if bloků:

``` c
if (bx >= abx[b] - 1) {
    if (bx <= abx[b] + 1) {
        if (by >= aby[b] - 1) {
            /* Zásah vyhodnocen bezpečně pro Alcyon C */
        }
    }
}
```

Tento zápis, připomínající "pyramidu smrti", je v prostředí CP/M-68K
nutným zlem. Překladač díky němu rozloží testování na elementární skoky,
nevytvoří duplicitní návěští a vygeneruje čistý a velmi rychlý strojový
kód pro procesor M68000.

# Ochranné štíty a logika kobercového bombardování

Ochranné štíty (bunkry) tvoří základní defenzivní prvek původní arkády.
Hráči poskytují dočasný bezpečný úkryt před nepřátelskou palbou, avšak s
každým zásahem postupně degradují. Do enginu Space 68K Invaders byla
tato mechanika nejen přidána, ale byla rozšířena o dynamickou agresivitu
nepřátel, která na stav štítů přímo reaguje.

## Životnost štítů

Vizuální a kolizní model štítů je uložen v paměti jako textové pole o
dvou řádcích. Čtveřice štítů se skládá ze znaků `/`, `\` a `#`. Každý
štít má šířku 6 znaků a výšku 2 znaky, což pro jeden štít představuje 12
štítových bloků. Celkové "zdraví" defenzivní linie `s_hlth` je na
začátku úrovně nastaveno na absolutní hodnotu 48 (4 štíty × 12 bloků).
Toto zdraví se snižuje třemi způsoby:

-   **Zásah hráčovou střelou:** Hráč si může vlastní neopatrností
    prostřílet do štítu díru zespodu.

-   **Zásah nepřátelskou bombou:** Ufoní střela odmaže vrchní vrstvy
    štítu.

-   **Zničení rojem:** Pokud roj ufonů klesne až na úroveň `Y=20` nebo
    `Y=21`, štíty jsou automaticky a nevratně vymazány, a hodnota
    `s_hlth` okamžitě padá na `0`.

## Strategie ufonů

Algoritmus ufonů průběžně sleduje globální stav hráčova krytí (s_hlth) a
podle něj mění svou agresivitu. Tato logika je rozdělena do dvou fází

### Fáze 1: Destrukce krytí  (Kobercové bombardování)

Dokud je celkové zdraví štítů větší než 12 (tedy zbývá více než čtvrtina
původní hmoty bunkrů), ufoni "vědí", že hráč je v relativním bezpečí.
Proto aktivují režim kobercového bombardování. Kapacita střel
(`max_b = 3`): Roj má povoleno shodit až tři nezávislé bomby současně.
Kadence (`f_rate = 5`): Časovač přebíjení je zkrácen na pouhých 5 cyklů
herní smyčky. Výsledkem je brutální příval nepřátelské palby, který se
na hráče sype napříč celou obrazovkou. Cílem invaze v této fázi není
primárně trefit hráče (což je přes štíty obtížné), ale co nejrychleji
zničit jeho ochrannou bariéru. Hráč je pod silným tlakem hned od začátku
levelu.

### Fáze 2: Odstřelování (Otevřený střet)

Jakmile zdraví štítů klesne na hodnotu 12 nebo nižší (štíty jsou "téměř
rozbité" nebo zcela smazané klesajícím rojem), ufoni radikálně změní
strategii. Kapacita střel (`max_b = 1`): Povolena je pouze jedna letící
bomba na obrazovce. Kadence (`f_rate = 35`): Časovač přebíjení se
prodlouží na pomalých 35 cyklů Roj se zklidní. Ufoni vyhodnotí, že hráč
již ztratil své krytí a je zasažitelný. Kobercové bombardování v takové
chvíli ustane z důvodu vyvážení hratelnosti -- pokud by na nechráněného
hráče pršely tři bomby každých 5 cyklů, hra by se stala nehratelnou a
frustrující. Návrat k ojedinělé, ale neustálé palbě nutí hráče kličkovat
mezi zbytky štítů a pečlivě mířit, čímž vzniká klasické, napínavé finále
každé vlny.

## Výpočetní nenáročnost rozšířené strategie

Přidání tří nezávislých střel si vyžádalo konverzi původních
jednoduchých proměnných na pole (`abx[3], aby[3]`). Z hlediska
historického procesoru Motorola 68000 na frekvenci 8 MHz je však přidání
krátkého cyklu `for (b = 0; b < 3; b++)` naprosto marginální zátěží.

Jediný dopad má tato mechanika na datový tok RS232, neboť systém musí v
jednom snímku smazat a překreslit až tři bomby namísto jedné (tj.
odeslat zhruba 30 bajtů navíc). Vzhledem k obrovské úspoře, které bylo
dosaženo dříve implementovaným Line Bufferem pro roj ufonů, se však
tento drobný nárůst bez problémů vejde do vymezeného komunikačního
rozpočtu a hra neztrácí na své plynulosti.

# Přenosová náročnost v praxi

Na začátku jsme si stanovili přísný fyzikální limit: pro dosažení
plynulého překreslování rychlostí 30 snímků za sekundu (FPS) po sériové
lince s rychlostí 115 200 baudů nesmí herní smyčka odeslat na terminál
více než 384 bajtů na jeden snímek. Naivní přístup, který by přesouval
každého ze 40 ufonů samostatnou VT100 sekvencí, vyžadoval zhruba 800
bajtů jen pro samotný roj, což je nehratelné. Díky implementaci techniky
Line Bufferu můžeme nyní exaktně spočítat skutečnou zátěž naší
optimalizované herní smyčky v jejím výpočetně nejnáročnějším okamžiku --
tedy na samém začátku hry, kdy žije všech 40 ufonů a na obrazovce
probíhá masivní kobercové bombardování.

## Analýza typického snímku (Horizontální pohyb)

Nejnáročnějším běžným stavem hry je horizontální posun celého roje a let
střel (úplně nejčastějším snímkem je pak pouze pohyb lodi a střel, který
je datově zanedbatelný).

Podívejme se na datovou náročnost toho, co se musí vykreslit v jednom
průchodu herní smyčkou:

-   **Roj ufonů** (Line Buffer): Namísto 40 individuálních přesunů
    kurzoru se roj překresluje po 4 řádcích. Pro každý řádek se odešle
    jedna navigační sekvence goto_yx (průměrně 8 bajtů). Za ní následuje
    celý řetězec `lbuf`. Jeho maximální šířka při plném stavu roje je
    $9 \times 3 + 3 = 30$ znaků.

$$4\text{ řádky } \times \left( 8\text{ bajtů navigace } + 30\text{ bajtů textu} \right) = 152\text{ bajtů }$$

-   **Hráčova raketka:** Při pohybu hráče se musí smazat stará pozice
    (navigace + 2 mezery) a vykreslit nová (navigace + znaky `MM`).

$$(8 + 2) + (8 + 2) = 20\text{ bajtů }$$

-   **Střela z raketky:** Smazání staré stopy (navigace + 1 mezera) a
    vykreslení nové (navigace + znak \|).

$$(8 + 1) + (8 + 1) = 18\text{ bajtů }$$

** Nepřátelské bomby (až 3 současně):** Během kobercového bombardování
padají až 3 střely. Každá vyžaduje smazání staré stopy a vykreslení
nového znaku "`v`".

$$3 \times \left( (8 + 1) + (8 + 1) \right) = 54\text{ bajtů }$$

Celková zátěž standardního snímku:
$$152 + 20 + 18 + 54 = 244\text{ bajtů }$$

Naše optimalizace srazila objem přenášených dat ze zhruba 800 bajtů
(naivní přístup) na slušných 244 bajtů. Jsme tedy hluboko pod stanoveným
limitem 384 bajtů. S tímto datovým objemem linka při 115 200 baudech
teoreticky zvládne přenést až 47 snímků za sekundu, což poskytuje
dostatečnou rezervu pro plynulé hraní.

## Vertikální skok roje ufonů je největší zátěž přenosu

Dochází k němu pouze ve zlomku vteřiny, kdy roj narazí na okraj
obrazovky a posouvá se o řádek níž. V tomto kroku Line Buffer nevkládá
"gumovací" mezery do vykreslovaného řetězce, ale pro zachování čistého
obrazu musí explicitně smazat 4 staré řádky a následně vykreslit 4 nové.
Během posunu dolů se také použije úspornější vzorec a vyrovnávací paměť
(Line buffer) se alokuje na šířku 29 znaků.

Smazání 4 starých řádků (navigace + 29 mezer):
$$4 \times (8 + 29) = 148\text{ bajtů }$$

Vykreslení 4 nových řádků (navigace + 29 znaků):
$$4 \times (8 + 29) = 148\text{ bajtů }$$

Hráč, jeho střela a 3 bomby: $$20 + 18 + 54 = 92\text{ bajtů }$$

Celková zátěž skoku dolů: $$148 + 148 + 92 = 388\text{ bajtů }$$

Tento nejhorší možný scénář, který nastává jen jednou za několik desítek
cyklů, generuje 388 bajtů. Překračuje tedy velmi těsně náš teoretický
limit 384 bajtů. V praxi to znamená, že tento jeden specifický snímek se
na terminál vykreslí za cca 33,6 milisekund (ekvivalent cca 29,7 FPS).
Pro lidské oko je tento mikroskopický propad naprosto nepostřehnutelný.
Z těchto úvah je zřejmé, že kombinace lineárních bufferů a přímé obsluhy
terminálu skrze assemblerový modul KEY.S dosáhla absolutního maxima
toho, co fyzikální vrstva sériového spojení CP/M-68K dovoluje.

# Generování pseudonáhodných čísel

Pro nepředvídatelné chování, konkrétně pro výběr ufona, který shodí
bombu při kobercovém bombardování, potřebuje herní engine rychlý zdroj
náhodných čísel. Standardní knihovní funkce `rand()` z prostředí CP/M by
do zkompilovaného kódu mohla zanést zbytečnou zátěž nebo další
závislosti. Proto byla přímo do enginu implementována vlastní odlehčená
verze LCG.

## Lineární kongruentní generátor (LCG)
[LCG na wiki](https://cs.wikipedia.org/wiki/Line%C3%A1rn%C3%AD_kongruentn%C3%AD_gener%C3%A1tor)

Tento algoritmus je jedním z nejstarších a výpočetně nejméně náročných
způsobů generování pseudonáhodných čísel. Funguje na principu neustálého
násobení předchozí hodnoty (seedu) velkým číslem a přičítání konstanty.
V našem zdrojovém kódu je implementován prostřednictvím funkce
`fast_rand()`:

``` c
long r_seed = 54321L;
fast_rand() {
    r_seed = (r_seed * 1103515245L + 12345L);
    return (int)((r_seed >> 16) & 0x7FFF);
}

```

Výpočet provede aritmetickou operaci a její výsledek následně bitově
posune o 16 pozic doprava (`>> 16`), protože vyšší bity u LCG generátorů
vykazují mnohem lepší statistické vlastnosti náhodnosti než bity nižší.
Nakonec je výsledná hodnota oříznuta logickým součinem (`& 0x7FFF`) na
kladné 15bitové číslo.

## 16bitový typ `int` v Alcyon C

Při implementaci generátoru jsem narazil na jeden z nejzrádnějších
problémů spojených s historickým kompilátorem Alcyon C. Během
počátečního testování kobercového bombardování střílel neustále pouze
jeden a ten samý ufon -- vždy ten, který se nacházel v nejlevějším
žijícím sloupci.

Příčinou byla původní deklarace proměnné `seed` jako standardního typu
`unsigned int`. Ačkoliv je procesor Motorola 68000 interně vybaven
32bitovými registry, kompilátor Alcyon C (jakožto historický K&R C
překladač) striktně mapuje datový typ `int` jako 16bitovou hodnotu
(rozsah -32 768 až 32 767).

Když pak původní kód provedl bitový posun o 16 pozic doprava
(`seed >> 16`), všech 16 datových bitů proměnné beze zbytku "přepadlo"
mimo paměťové místo. Funkce tak v každém herním cyklu vracela nulu.
Herní smyčka si následně z této nuly udělala zbytek po dělení aktuálním
počtem sloupců a logicky vždy vybrala sloupec s indexem 0.

## Řešení pomocí 32bitového typu `long`

Aby bitový posun `>> 16` správně fungoval a na své místo "natáhl"
horních 16 bitů z vypočítané hodnoty, musela být proměnná pro udržování
stavu (`r_seed`) explicitně deklarována jako 32bitový typ `long`.

Ze stejného důvodu musely být příponou `L` označeny i velké násobící
konstanty uvnitř samotné matematické rovnice (např. `1103515245L`), aby
překladač nepřevedl mezivýpočet zpět na 16 bitů. Teprve s tímto
vynucením 32bitové aritmetiky začal překladač generovat správné dlouhé
strojové instrukce pro Motorolu 68000, bitový posun odřízl pouze spodní
šum a ufoni mohli spustit skutečně náhodné kobercové bombardování napříč
celou šířkou herní obrazovky.

# Nízkoúrovňové vstupy a výstupy: Modul KEY.S

Aby mohla dynamická akční hra fungovat na operačním systému CP/M-68K,
bylo nutné vyřešit dva zásadní problémy s komunikací se sériovým
terminálem: neblokující čtení klávesnice a maximálně ořezaný výpis
znaků.

Standardní funkce jazyka C poskytované historickou knihovnou překladače
Alcyon C byly pro vývoj her naprosto nevhodné. Funkce jako `getchar()`
nebo `scanf()` zastaví běh celého programu a čekají, dokud uživatel
nestiskne klávesu a nepotvrdí ji klávesou Enter (blokující vstup). Pokud
by hra čekala na vstup, roj ufonů by se zastavil. Funkce `putchar()`
nebo `printf()` zase procházejí složitými interními buffery a
formátovacími rutinami, což přidává zbytečnou režii ke každému
odeslanému znaku na pomalou linku RS232.

Máme vytvořený modul `KEY.S`. Po překladu (AS68) vznikne objektový
soubor `KEY.O`, který slinkujeme s hlavním program `CLINK SPACEINV KEY`
Po slinkování máme k dispozici dvě globální funkce: `_getch_noblock` a
`_fast_putchar`.

Modul obchází standardní C knihovny a komunikuje přímo s jádrem CP/M-68K
(BDOS) pomocí systémového přerušení `trap #2`.

### KEY.S

``` asm
.text
        .globl  _getch_noblock
        .globl  _fast_putchar

_getch_noblock:
        move.w  #11,d0
        trap    #2
        tst.w   d0
        beq.s   L_empty

        move.w  #6,d0
        move.l  #255,d1
        trap    #2
        andi.l  #255,d0
        rts

L_empty:
        moveq   #0,d0
        rts

_fast_putchar:
        link    a6,#0
        move.w  #6,d0
        move.w  8(a6),d1
        andi.l  #255,d1
        trap    #2
        unlk    a6
        rts

        .end    
```

## Neblokující čtení klávesnice: `getch_noblock`

Základ pro jakoukoli hru. Umožňuje programu "podívat se" na klávesnici,
přečíst případný stisk, ale pokud uživatel nic nemačká, okamžitě vrátit
řízení zpět hře bez jakéhokoliv zdržení.

Funkce nejprve nastaví registr `d0` na hodnotu 11 (`move.w #11,d0`). V
systému CP/M to odpovídá volání funkce **Console Status**. Následuje
volání systému instrukcí `trap #2`. Systém vrátí výsledek zpět do
registru `d0`. Pokud je hodnota nula (`beq.s L_empty`), znamená to, že
ve vstupním bufferu není žádný znak, a funkce okamžitě vrací do C kódu
hodnotu 0 (`moveq #0,d0` a `rts`).

Pokud je na klávesnici detekován stisk, funkce pokračuje voláním BDOS
služby 6 (**Direct Console I/O**) nastavením `move.w #6,d0`. Aby
operační systém věděl, že chceme znak přečíst (a nikoliv vypsat), je do
registru `d1` vložena speciální hodnota 255 (`move.l #255,d1`). Po
dalším volání `trap #2` je přečtený znak maskován na 8 bitů instrukcí
`andi.l #255,d0` a předán zpět do herní smyčky jako platný ASCII kód.

## Extrémně rychlý výpis: `fast_putchar`

Pro vykreslování hry a odesílání předpřipraveného Line Bufferu se
používá druhá funkce v assembleru, která provádí přímý zápis na sériový
port terminálu s absolutně minimální procesorovou režií.

Na rozdíl od standardní K&R C funkce využívá `_fast_putchar` základní C
volací konvenci (C Calling Convention) a přímo si vyzvedává znak
(argument) ze zásobníku procesoru. Pomocí instrukce `link a6,#0` si
funkce vytvoří stack frame a následně přečte parametr přesně z adresy
`8(a6)` do registru `d1` (`move.w 8(a6),d1`).

Samotný výpis je opět realizován skrze CP/M službu 6 (**Direct Console
I/O**) naplněním registru `d0` a systémovým voláním `trap #2`. Následně
funkce obnoví zásobník instrukcí `unlk a6` a vrátí řízení do programu
(`rts`).

Díky tomuto přímému assemblerovému modulu `KEY.S` může herní engine v
jazyce C operovat v reálném čase, asynchronně zpracovávat vstupy hráče
(např. pohyb lodi a střelbu) a "krmit" buffer terminálu VT100 daty
nejvyšší možnou rychlostí, kterou je operační systém a hardware 68k-MBC
schopen zvládnout.

### komentovaný výpis programu
[SPACEINV.C](https://drive.google.com/drive/folders/1IVfAavBhIgBhavIPGhk5WQOr0lfNuhtq?usp=sharing)
