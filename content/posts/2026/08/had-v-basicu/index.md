---
title: "HAD v Enhaced 68k BASIC"
date: 2026-08-23T22:57:45+02:00
cover:
    image: ""
tags: ["Počítače", "Počítače.M68k"]
draft: false
---

Cílem bylo dosáhnout maximální plynulosti v prostředí interpretovaného
BASICu. Pomohly kruhové zásobníky, předpočítání náhodného výskytu jídla
a tabulky escape sekvencí a hlavně O(1) detekce kolizí.

------------------------------------------------------------------------

## Použitá pole

Program je rychlý, protože nevyužívá k běhu hry téměř žádné výpočty, ale
čte data z předem připravených paměťových struktur.

-   **`X(500)`, `Y(500)`** -- **Kruhový zásobník (Ring Buffer) těla
    hada.** Uchovává X a Y souřadnice. Nešoupe se s nimi! Pouze se
    posouvá virtuální ukazatel hlavy (`H`) a ocas se dopočítává.
    Velikost 500 definuje maximální možnou délku hada.

-   **`P$(45, 25)`** -- **Cache pro ANSI sekvence.** Dvourozměrné
    textové pole. V každé buňce je uložen hotový textový řetězec pro
    skok kurzoru (např. `ESC[10;20H`). Tím se zcela eliminuje pomalé
    spojování řetězců během hry.

-   **`FX(500)`, `FY(500)`** -- **Předgenerované jídelníček.** Tabulka
    náhodných pozic žrádla. Místo pomalého volání matematické funkce
    `RND()` se během hry jen sekvenčně čte další hodnota v pořadí.

-   **`Q(25)`** -- **Fronta stisků kláves (Input Queue).** Menší kruhový
    zásobník chytající rychlé stisky kláves od hráče, aby nedošlo k
    zahození příkazů (např. při rychlé kličce "nahoru a hned doprava").

-   **`B(45, 25)`** -- **Mapa kolizí (Collision Map).** Dvourozměrné
    pole fungující jako mřížka obrazovky. `1` znamená, že na dané
    souřadnici je tělo hada **nebo zeď**, `0` znamená volno. Zajišťuje
    absolutní O(1) detekci nárazu a bezpečné generování jídla bez
    složitých podmínek.

## Proměnné

### Systémové a dočasné proměnné

-   **`E$`** -- Obsahuje "Escape" sekvenci `CHR$(27) + "["`. Slouží jako
    základ pro všechny ANSI příkazy.

-   **`SY$`, `SX$`** -- Dočasné textové proměnné (String Y, String X)
    používané výhradně při startu (řádky 70, 90) k oříznutí mezer po
    funkci `STR$()`.

-   **`A$`** -- Proměnná pro zachycení stisku klávesy v obrazovce "Game
    Over" (Ano/Ne).

### Stavové proměnné hry

-   **`L`** -- Aktuální délka hada (Length). Začíná na 5.

-   **`SC`** -- Aktuální skóre (Score). Začíná na 0.

-   **`EAT`** -- Logický příznak (0 nebo 1). Určuje, zda had v daném
    kroku sežral jídlo (1) nebo ne (0). Řídí vykreslování a mazání
    ocasu.

-   **`FI`** -- (Food Index). Ukazuje, které jídlo z předgenerovaných
    polí `FX/FY` je zrovna na řadě.

### Pohyb a rychlost

-   **`DX`, `DY`** -- (Delta X, Delta Y). Směrové vektory pohybu hlavy.
    Nabývají hodnot -1, 0, nebo 1.

-   **`RX`, `RY`** -- Zpoždění určující rychlost. Protože znaky v
    terminálu jsou vyšší než širší, `RY` (vertikální zpoždění) je větší
    než `RX`, aby se had pohyboval vizuálně stejně rychle do všech
    směrů. Při jídle se tyto hodnoty snižují (hra zrychluje).

-   **`D`** -- Aktuálně aplikované zpoždění (Delay) pro daný herní
    cyklus. Kopíruje hodnotu `RX` nebo `RY` podle toho, kam had zrovna
    míří.

### Ukazatele (Pointers) a Souřadnice

-   **`QH`, `QT`** -- (Queue Head, Queue Tail). Ukazatele pro čtení (QH)
    a zápis (QT) do kruhové fronty stisků kláves `Q()`.

-   **`H`** -- (Head). Index do polí `X()` a `Y()`. Ukazuje, na jakém
    indexu (1-500) se v paměti nachází aktuální hlava hada.

-   **`JX`, `JY`** -- (Jídlo X, Jídlo Y). Aktuální souřadnice zrovna
    zobrazeného jídla na obrazovce.

-   **`NX`, `NY`** -- (New X, New Y). Vypočítané souřadnice **budoucí**
    hlavy hada v dalším kroku. Než se tam had pohne, testují se na
    kolizi.

-   **`TA`** -- (Tail). Index do polí `X()` a `Y()` ukazující na úplný
    konec hada. Počítá se dynamicky jako hlava mínus délka.

-   **`TX`, `TY`** -- (Tail X, Tail Y). Reálné souřadnice konce hada
    vytažené z paměti. Slouží k vymazání znaku z terminálu a smazání
    jedničky z kolizní matice `B()`.

-   **`K`** -- Obsahuje ASCII kód stisknuté klávesy načtené příkazem
    `GET`.

## Cykly FOR

Každý cyklus v je napsaný tak, aby nesnižoval výkon hry.

-   **`60 FOR Y ...` a `80 FOR X ...`** -- Předgenerování všech ANSI
    sekvencí (`P$`). Běží jen před startem hry. Vygenerují
    $24 \times 45 = 1080$ řetězců do paměti.

-   **`130 FOR I = 1 TO 500`** -- Plnění polí `FX` a `FY` náhodnými
    souřadnicemi. Běží jen před starem hry, pak nás nezdržuje pomalý
    `RND()`.

-   **`192 FOR I = 1 TO L`** -- Nastaví počáteční souřadnice hada (aby
    nebyl srolovaný v jednom bodě) a ihned tyto body zapíše do kolizní
    mapy `B`.

-   **`240 FOR R = 3 TO 20` a `245 FOR C = 1 TO 42`** -- Zápis zdí.
    Nevykreslují pouze znaky stěn do terminálu, ale hlavně zapisují
    jedničky do okrajů kolizní matice `B`.

-   **`290 FOR I = 1 TO L`** -- Počáteční vykreslení těla hada na
    obrazovku.

-   **`350 FOR Z = 1 TO D`** -- **Nejdůležitější cyklus hry.** Slouží
    jako časovač kroku hada (aby neletěl moc rychle), ale **zároveň**
    uvnitř bleskově saje klávesy z hardwarového bufferu a ukládá je do
    fronty `Q`.

-   **`910 FOR I = 1 TO L`** -- Bleskové čištění po smrti (O(L)). Cyklus
    nečistí celou hrací plochu (což by trvalo dlouho), ale projde pouze
    staré tělo mrtvého hada a odstraní ho z kolizní matice `B`. Proměnná
    **`IDX`** v tomto cyklu slouží k bezpečnému odpočítávání zpět v
    kruhovém zásobníku.

------------------------------------------------------------------------

## Herní logiky po řádcích

### Inicializace a plnění polí před startem hry

-   **`40-43`**: Nastavení paměti pomocí `DIM`. Vytvoření Escape znaku,
    smazání terminálu, skrytí kurzoru (`?25l`) a vypsání informačního
    textu.

-   **`60-110`**: **Předvýpočet kurzorů.** Projde celou mřížku. Funkce
    `STR$()` dělá z čísel text, ale přidává mezeru pro znaménko. Pomocí
    stringových funkcí mezeru odřízneme a hotovou ANSI sekvenci uložíme.

-   **`130-165`**: **Předvýpočet žrádla.** Uloží 500 náhodných
    souřadnic. Index jídla `FI` se nastaví na 1.

### Start Hry a Vykreslení kolizních zdí kolem

-   **`180-186`**: Nastavení startovních proměnných (rychlost, délka,
    ukazatele fronty).

-   **`200-204`**: **Chytrý spawn prvního žrádla.** Otestuje se, zda na
    předgenerované pozici `JX, JY` náhodou neleží startovní had
    (`B = 0`). Pokud ano, posune se na další předgenerované jídlo v
    pořadí.

-   **`210-295`**: Vykreslení uživatelského rozhraní, arény, zdí (včetně
    zápisu jedniček do matice `B`), prvního žrádla a počátečního hada.
    Kreslení už používá výhradně pole `P$()`.

### Hlavní herní smyčka O(1)

-   **`330`**: Korekce rychlosti. Nastaví čekací cyklus `D` na hodnotu
    `RX` nebo `RY` dle směru pohybu `DY`.

-   **`340-400`**: **Sání vstupů z klávesnice.** Smyčka `FOR Z`, která
    saje znaky (`GET K`). Přečtená hodnota se bitově upraví:
    `K = K OR 32`. Tento trik známý z assembleru převede všechna velká
    písmena na malá. Klávesa se uloží do fronty `Q`.

-   **`410-490`**: **Logika pohybu.** Vytáhne nejstarší stisk z fronty.
    Zkontroluje, zda jde o povolenou klávesu (`w, s, a, d, m`) a
    zajistí, že se had neotočí o 180 stupňů sám do sebe (např. nepovolí
    `DX = 1`, pokud je už `DX = -1`).

-   **`500-516`**: **Kruhová matematika.** Spočítá se nová pozice hlavy
    `NX, NY`. Vypočte se pozice ocasu `TA`. Pokud `TA` klesne do záporu,
    přičte se 500 (kruhový wrap-around). Zjistí se souřadnice mazaného
    ocasu `TX, TY`.

-   **`540`**: **Detekce kolizí v O(1).** Zkontroluje se pouze
    `B(NX, NY) = 1`. Pokud tam je 1 a není to právě opouštějící ocas
    (výjimka `NX <> TX`), had narazil a hra končí. Bez jakéhokoliv
    počítání ohraničení obrazovky!

-   **`550-620`**: **Krmení.** Zjistí, zda `NX, NY` je jídlo. Zvýší
    skóre, zrychlí hru (`RX/RY` mínus konstanty), vybere nové jídlo z
    `FX/FY` (a otestuje na kolizi s tělem) a nastaví `EAT=1`.

### Vykreslení a obnova dat (Delta Render)

Tato sekce minimalizuje `PRINT` operace jen na nezbytné změny.

-   **`640`**: Pokud jedl (`EAT=1`): Vykreslí jídlo "O" na nové místo,
    vykreslí novou hlavu `"#"`, přepíše skóre. Ocas zůstává na místě.
    **Zásadní detail: na konci řádku je implicitní přechod na řádek 660,
    nevyhodnocuje se 650.**

-   **`650`**: Pokud nejedl (`EAT=0`): Smaže starý ocas mezerou `" "`,
    vykreslí novou hlavu `"#"` a vymaže ocas z kolizní matice
    `B(TX,TY) = 0`.

-   **`660-690`**: Posune ukazatel hlavy `H` vpřed (s ohledem na kruh do
    500). Zapíše novou hlavu do polí `X, Y` a matice `B`. Skočí zpět na
    `330`.

### Game Over a Restart

-   **`740-830`**: Zobrazí kurzor, skóre a zachytává stisk kláves A/N.

-   **`900-940`**: **O(L) Restart.** Pouze projde tělo právě mrtvého
    hada a vymaže jeho buňky z matice kolizí `B`. Nečistí celou
    obrazovku ani matici. Následně skočí na `170` pro okamžitý reset.

------------------------------------------------------------------------

## Optimalizace díky kterým je hra hratelná

Ač je procesor M68008 skvělý, interpretovaný BASIC je vždy pomalý. Aby
se had hýbal, postupně prošel těmito fázemi vylepšení:

1.  **Odstranění spojování řetězců:**

    -   *Problém:* BASIC strašně dlouho zpracovává skládání zpráv typu
        `CHR$(27) + "[" + STR$(Y)...`

    -   *Řešení:* Vygenerování mapy řetězců `P$` nanečisto hned na
        začátku. Ve hře už děláme jen absolutně nejrychlejší
        `PRINT P$(X,Y)`.

2.  **Odstranění pomalé matematiky:**

    -   *Problém:* Volání `RND()` nutí interpreter do těžkých výpočtů s
        plovoucí desetinnou čárkou.

    -   *Řešení:* Vytvoření polí `FX` a `FY`, vylosování naslepo mimo
        hru a pouhé posouvání indexu `FI` v seznamu hotových čísel.

3.  **Odstranění posunů v paměti (Kruhový zásobník):**

    -   *Problém:* Při každém kroku hada se standardně přesouvá celé
        pole o 1 index. To znamená složitost $O(N)$ (čím delší had, tím
        víc operací a hra se trhá).

    -   *Řešení:* Zavedení kruhového zásobníku. Pole `X` a `Y` stojí na
        místě. Pohybuje se jen proměnná ukazující na hlavu `H`. Časová
        složitost pohybu je fixní O(1) bez ohledu na délku hada.

4.  **Odstranění iterativního vyhledávání kolizí:**

    -   *Problém:* Hlídání nárazu typicky prochází celého hada smyčkou
        `FOR I=1 TO L`. Opět katastrofální $O(N)$ propad výkonu ke konci
        hry.

    -   *Řešení:* Cache paměť v podobě dvourozměrného pole `B(X,Y)`. Had
        za sebou nechává "stopu" (jedničky) a ocas ji maže (nuly).
        Procesor se jen podívá na jednu souřadnici. Znovu bleskové
        O(1).

5.  **Chytré generování jídla bez "problikávání":**

    -   *Problém:* Žrádlo se často vykreslilo přímo pod jedoucího hada a
        ocas ho po chvíli smazal.

    -   *Řešení:* Využití hotové matice `B()`. Před zobrazením jídla se
        zkontroluje, zda pole není obsazené tělem, případně se přeskočí
        na další.

6.  **Buffer pro ovládací klávesy:**

    -   *Problém:* Rychlé pohyby prstů na klávesnici (WASD klička v
        jedné vteřině) BASIC ztrácel kvůli zdržovacímu cyklu.

    -   *Řešení:* Vlastní vyrovnávací paměť `Q()`, která vysává sériový
        port neustále i během pauzy, a herní logika pak stisky postupně
        odbavuje.

7.  **Zahození manipulace s řetězci pro ovládaní:**

    -   *Problém:* Původní `GET A$` a `ASC(A$)` nutilo BASIC ve smyčce
        neustále tvořit a mazat stringy v paměti.

    -   *Řešení:* Přechod na `GET K` (načítá přímo číselnou ASCII
        hodnotu) a využití rychlého bitového převodu `OR 32` zrychlily
        výrazně vstup.

8.  **Zdi zabudované v kolizní mapě:**

    -   *Problém:* Složená matematická podmínka
        `IF NX < 2 OR NX > 41 OR NY < 3 OR NY > 20` drtila každý snímek
        hry neskutečnou režií.

    -   *Řešení:* Do mapy kolizí `B()` jsme nahráli neviditelné zdi
        podél okrajů arény. Kolizní kontrola nyní řeší náraz do sebe i
        do zdi v jediném testu matice.

9.  **Minimum větvení při kreslení:**

    -   *Problém:* BASIC zbytečně vyhodnocoval další `IF` podmínky poté,
        co zjistil, že had jedl.

    -   *Řešení:* Použitím `IF EAT=1 THEN ...` na řádku 640 se vykoná
        vykreslení a díky absenci `GOTO` program plynule přejde na další
        příkazy.

10. **Zahození REM:**

    -   *Problém:* Interpretovaný jazyk ztrácel jednotky milisekund
        čtením komentářů, pokud byly umístěny uvnitř hlavní herní
        smyčky.

    -   *Řešení:* Neúprosné promazání všech textů a zbytečných mezer v
        herním enginu (`330-690`). Komentáře mohou být jen u
        inicializace.


### CTRL+V vložit do Enhanced BASIC 68K spuštěného v terminálu

``` BASIC
10 REM ==========================================
20 REM Hra HAD - pro Enhanced BASIC 68k
30 REM ==========================================
40 CLEAR: DIM X(500), Y(500), P$(45, 25), FX(500), FY(500), Q(25), B(45, 25)
41 E$ = CHR$(27) + "["
42 PRINT E$;"2J";E$;"?25l";
43 PRINT E$;"2J";E$;"1;1H";"Nacitam hru..."
59 REM --- PREDVYPOCET ESCAPE SEKVENCI ---
60 FOR Y = 1 TO 24
65 PRINT E$;"1;20H";"Generuji mapu: "; Y; "/ 24 "
70 SY$ = STR$(Y): IF LEFT$(SY$,1) = " " THEN SY$ = MID$(SY$,2)
80 FOR X = 1 TO 45
90 SX$ = STR$(X): IF LEFT$(SX$,1) = " " THEN SX$ = MID$(SX$,2)
100 P$(X, Y) = E$ + SY$ + ";" + SX$ + "H"
110 NEXT X: NEXT Y
120 REM --- PREDGENEROVANI POZIC ZRADLA ---
130 FOR I = 1 TO 500
135 PRINT E$;"1;20H";"Generuji zradlo: "; I; "/ 500"
140 FX(I) = INT(RND(0) * 38) + 2
150 FY(I) = INT(RND(0) * 16) + 4
160 NEXT I
165 FI = 1
170 PRINT E$;"2J";E$;"?25l";
180 L = 5: SC = 0: DX = 1: DY = 0
185 RX = 10: RY = 20: QH = 1: QT = 1
186 REM --- KJRUHOVY BUFFER INICIALIZACE ---
190 H = L
192 FOR I = 1 TO L: X(I) = 20 - L + I: Y(I) = 10: B(X(I), Y(I)) = 1: NEXT I
200 JX = FX(FI): JY = FY(FI): IF B(JX, JY) = 0 THEN GOTO 210
202 FI = FI + 1: IF FI > 500 THEN FI = 1
204 GOTO 200
210 REM --- VYKRESLENI RAMECKU ---
220 PRINT P$(1,1);"--- HAD --- Skore: 0    | WASD = Pohyb | M = Konec"
230 PRINT P$(1,2);"+----------------------------------------+"
240 FOR R = 3 TO 20: B(1,R)=1: B(42,R)=1: PRINT P$(1,R);"|";P$(42,R);"|": NEXT R
245 FOR C = 1 TO 42: B(C,2)=1: B(C,21)=1: NEXT C
250 PRINT P$(1,R);"|";P$(42,R);"|"
270 PRINT P$(1,21);"+----------------------------------------+"
280 PRINT P$(JX, JY);"O";
290 FOR I = 1 TO L: PRINT P$(X(I), Y(I));"#";: NEXT I
295 PRINT P$(1,22)
300 REM ==========================================
310 REM HLAVNI SMYCKA HRY
320 REM ==========================================
330 D = RX: IF DY <> 0 THEN D = RY
340 REM --- UPLNE VYSATI HARDWAROVEHO BUFFERU ---
350 FOR Z = 1 TO D
360 GET K: IF K = 0 THEN GOTO 400
370 K = K OR 32 : REM Trik: Bitovy OR prevede velka pismena na mala!
380 Q(QT) = K: QT = QT + 1: IF QT > 20 THEN QT = 1
390 GOTO 360
400 NEXT Z
410 REM --- ZPRACOVANI FRONTY STISKU ---
420 IF QH = QT THEN GOTO 500
430 K = Q(QH): QH = QH + 1: IF QH > 20 THEN QH = 1
440 IF K = 109 OR K = 77 THEN GOTO 750
450 IF (K = 119 OR K = 87) AND DY = 0 THEN DX = 0: DY = -1: GOTO 500
460 IF (K = 115 OR K = 83) AND DY = 0 THEN DX = 0: DY = 1: GOTO 500
470 IF (K = 97 OR K = 65) AND DX = 0 THEN DX = -1: DY = 0: GOTO 500
480 IF (K = 100 OR K = 68) AND DX = 0 THEN DX = 1: DY = 0: GOTO 500
490 GOTO 420
500 REM --- VYPOCET NOVE POZICE A CHVOSTU ---
510 NX = X(H) + DX: NY = Y(H) + DY
515 TA = H - L + 1: IF TA <= 0 THEN TA = TA + 500
516 TX = X(TA): TY = Y(TA)
520 REM --- KONTROLA ZDI A SEBE SAMA ---
540 IF B(NX, NY) = 1 AND (NX <> TX OR NY <> TY) THEN GOTO 750
550 REM --- SEBRANI ZRADLA ---
560 EAT = 0
570 IF NX <> JX OR NY <> JY THEN GOTO 630
580 SC = SC + 1: L = L + 1
590 IF RX > 10 THEN RX = RX - 4: RY = RY - 6
600 FI = FI + 1: IF FI > 500 THEN FI = 1
610 JX = FX(FI): JY = FY(FI): IF B(JX, JY) = 1 THEN GOTO 600
620 EAT = 1
630 REM --- O(1) VYKRESLENI S CR LF RESETEM ---
640 IF EAT = 1 THEN PRINT P$(JX, JY);"O"; P$(NX, NY);"#"; P$(20, 1);SC; P$(1,22)
650 IF EAT = 0 THEN PRINT P$(TX, TY);" "; P$(NX, NY);"#"; P$(1,22): B(TX, TY) = 0
660 REM --- AKTUALIZACE HLAVY ---
670 H = H + 1: IF H > 500 THEN H = 1
680 X(H) = NX: Y(H) = NY: B(NX, NY) = 1
690 GOTO 330
740 REM ==========================================
750 REM KONEC HRY
760 REM ==========================================
770 PRINT E$;"?25h";P$(1,23);
780 PRINT "GAME OVER! Skore: "; SC
790 PRINT "Nova hra? A/N":
800 GET A$: IF A$ = "" THEN GOTO 800
810 IF (A$ = "n") OR (A$ = "N") THEN PRINT "Ukonceno": END
820 IF (A$ = "a") OR (A$ = "A") THEN GOTO 900
830 GOTO 800
900 REM ======== POKRACOVAT? (CISTENI HADA KOLIZI) ========
910 FOR I = 1 TO L
915 IDX = H - I + 1: IF IDX <= 0 THEN IDX = IDX + 500
920 B(X(IDX), Y(IDX)) = 0
930 NEXT I
940 GOTO 170

```
