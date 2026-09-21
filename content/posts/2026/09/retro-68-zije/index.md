---
title: "Retro 68 žije"
date: 2026-09-05T17:08:08+02:00
summary: "Často se čelím otázce: “A k čemu to je dobré?” Proč trávíš čas programováním pro čtyřicet let starý procesor, když tu máme cloud, umělou inteligenci a nekonečný výpočetní výkon?"
cover:
    image: "68008.webp"
tags: ["Počítače", "Počítače.M68k"]
draft: false
---
# aneb nejen o potřebě včelaření

## Píšu bezúčelný kód
Často se čelím otázce: “A k čemu to je dobré?” Proč trávíš čas programováním pro čtyřicet let starý procesor, když tu máme cloud, umělou inteligenci a nekonečný výpočetní výkon? Není to jen ztráta času? Nebo snad je to jen nějaké nostalgické volání?

Krátká odpověď zní: Ne, není.

Dlouhá odpověď je o něco složitější. Je pravda, že vývoj herního enginu
v prehistorickém C kompilátoru (Alcyon C) pro procesor Motorola 68008 na
8 MHz neřeší světový mír, nesníží inflaci ani neurychlí zelenou tranzici.
Dělám to jako volnočasovou aktivitu. Někdo včelaří, někdo
rybaří, já zkoumám architekturu M68K a `CP/M 1.3` z roku 1983.

Ale pokud se ptáte na smysl a užitek, rád bych vám nabídl jinou
perspektivu, než je nostalgie.

{{< obr600 "68008.webp" "" >}}


## Proč nevolím osmibity

Kolegové z našeho ATARI klubu (8bitového) se ptají -- a proč M68K? Proč nepíšeš
něco nového pro MOS6502? Nebo jiný osmibit?

Programování je jako modelaření. Psát pro osmibity je stavění lodí v
láhvi. Je to cool, chce to specifické dovednosti a výsledky jsou zase
spefické -- jsou za sklem. Nepoplavou, nepoletí; ať se držím přirovnání
k modelaření. Jediná výhoda je, že loď v láhvi se nezapáší -- což je
jediná výhoda kódění pro osmibity.

Na 68k-MBC mám přímo z procesoru M68K výhled na kompatní blok téměř 1MB
paměti. Nabízí úplně jiné možnosti a protože mě hlubce zasáhl realtime
operační systému NuttX pro mikrontroléry, tak programátorské návyky jsou
podobné.

## CP/M je pro osmibity

Alespoň nějaká výzva. Operační systém CP/M na 68K je plně portován a
běží. Proč ho nevyužít.

## Software jako tělocvična

Když jdete do posilovny zvedat činky, nikdo se vás neptá, **k čemu je
dobré** přesouvat kus železa nahoru a dolů. Je to trénink. Stejným
způsobem je Motorola 68000 tréninkem.

Dnes jsme zvyklí na nekonečné zdroje. Když se náš program zpomalí,
prostě přidáme další gigabajt RAM nebo sáhneme po silnějším hardware
nebo škálujeme výkon v cloudu. Výsledkem je často líný, nabobtnalý
software.

Práce s Motorolou 68000 mě vrací k absolutním fyzikálním a logickým
kořenům výpočetní techniky. Tady si nemohu dovolit abstrakci. Pokud v
herní smyčce **Space Invaders** provedu hardwarové dělení, které trvá
140 hodinových taktů, hra se začne zasekávat. Když pro vykreslení pozice
kurzoru použiju dělení a modulo deset, procesor se udusí. Musím
přemýšlet. Musím nahradit matematiku pamět a stavět si překladové
tabulky (LUT), využívat řádkové buffery pro minimalizaci zátěže sériové
linky a maskovat 32bitové operace (protože 16bitový `int` zkrátka
nestačí).

Tohle není nostalgie. To je fundamentální inženýrství obnažené na kost.
Učí mě to vážit si každého hodinového taktu a každého bajtu.

## Pochopení toho, na čem stojíme

Motorola 68000 je fascinující kus hardwaru. Není to jen zastaralý čip;
je to křižovatka, na které se rodily koncepty moderních počítačů. Když
pro něj dnes píšu kód, nečtu si o historii v učebnici -- já se jí
fyzicky dotýkám. Zkoumám asymetrii mezi výkonem CPU vs. uzké hrdlo linky
RS232 na VT100 terminál.

Především je to nekonečně zábavné.

{{< obr600 "68010.webp" "" >}}

## Učím se, tedy jsem

Nakonec, proč děláme věci ze studijních důvodů? Protože radost z
objevování nepotřebuje okamžitý komerční byznys plán. Programování
historického hardwaru učí pokoře. Zjišťujete, že inženýři v 80. letech
řešili neuvěřitelně těžké problémy s elegancí a vynalézavostí.

Takže, k čemu to je? Je to nástroj k broušení mysli. A ten, kdo dokáže
optimalizovat kód tak, aby plynule běžel na procesoru z roku 1983 na
frekvenci 8 MHz, bude psát mnohem lepší, rychlejší a čistší kód i zítra,
pro nejnovější architekturu v moderním cloudu.

Na 68k-MBC s procesorem Motorola 68008 prozkoumám zákoutí `CP/M` a v dáli čeká spousta výzev na Rosco_m68k s CPU 68010 na 10MHz.

\
\
Retro není mrtvé.
