---
title: "π-tá odmocnina z π"
date: 2026-09-01T15:55:52+02:00
summary: "Je větší e na π nebo π ne e?"
cover:
    image: ""
tags: []
draft: false
math: true
---

### Matematická jednohubka k zahájení školeního roku

Hodnota $\pi$-té odmocniny z $\pi$ (kterou můžeme zapsat také jako
mocninu se zlomkem) je přibližně:

$$\sqrt[\pi]{\pi} = \pi^{\frac{1}{\pi}} \approx 1.43963$$

## Proč je tahle podivná hodnota tak zajímavá?

Abychom pochopili význam tohoto čísla, představme si, že zkoumáme funkci
$f(x) = x^{\frac{1}{x}}$. Dosazujeme do ní různá čísla a sledujeme, co
nám vychází.

{{< obr600 "f.webp" "" >}}

Tato funkce dosáhne maxima přesně v bodě, kdy se $x$ rovná
**Eulerovu číslu $e$** (což je zhruba $2.718$). Hodnota v tomto
nejvyšším bodě je:

$$e^{\frac{1}{e}} \approx 1.44466$$

Jakmile se přes tento vrchol přehoupneme k větším číslům, funkce začne
zase klesat. A protože $\pi$ (asi $3.141$) je větší než $e$, nachází se
na grafu už na klesajícím svahu.

Z toho logicky vyplývá, že vrchol v bodě $e$ musí být o kousek výš než
hodnota v bodě $\pi$:

$$e^{\frac{1}{e}} > \pi^{\frac{1}{\pi}}$$

## Matematický chyták

Díky této jednoduché nerovnosti můžeme elegantně vyřešit klasickou
otázku, kterou rádi dávají učitelé matematiky na olympiádách: **Je větší
$e^{\pi}$, nebo $\pi^{e}$?**

Vezmeme naši nerovnost, o které už s jistotou víme, že platí:

$$e^{\frac{1}{e}} > \pi^{\frac{1}{\pi}}$$

Nyní obě strany umocníme na společný násobek obou jmenovatelů, tedy na
$(e \cdot \pi)$. Zlomky v exponentech se tím vykrátí:

$$\begin{aligned}
\left( e^{\frac{1}{e}} \right)^{e \cdot \pi} & > \left( \pi^{\frac{1}{\pi}} \right)^{e \cdot \pi} \\
e^{\pi} & > \pi^{e}
\end{aligned}$$

A je to dokázáno!

Díky chování obyčejné $\pi$-té odmocniny víme, že
$e^{\pi}$ je větší číslo než $\pi^{e}$.

