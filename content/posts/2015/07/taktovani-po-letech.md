---
title: "Taktování po letech..."
date: 2015-07-31T17:28:00.004Z
url: "/posts/2015/07/taktovani-po-letech/"
summary: "Pamatujete ty časy, kdy jsme nové AMD Athlony a Durony taktovali tak, že se grafitem (t.j. jedničkou tužkou) propojovaly jednotlivé piny násobičů přímo na procesorech[ 1 ]. To bylo na přelomu milénia, po radostných oslavách, že jsme přežili Y2K[ 2 ]. Od té doby jsem se o taktování procesoru nepokoušel a vlastně to ani nebylo potřeba. Loni vydal Intel ke 25 výročí značky Pentium procesor s krásným a snadno zapamatovatelným názvem G3258 a pozor! s otevřeným násobičem. Tedy přímo výzva pro taktování. V základu běží G3258 na taktu 3,2GHz při napětí 1.04V. S originálním chladičem se nechá bez problémů taktovat na 4,3GHz při napětí 1.25V. Jedna věc je si o tom číst[ 3 ]. A druhá věc je vyzkoušet to. Pro srovnání výkonu byl použit jednoduchý program Prime Benchmark[ 4 ], který minutu počítá a pak vyzvrací číslo, čím větší, tím je procesor rychlejší. Zvýšení výkonu o 34% je zajímavé. Uvidíme,..."
cover:
    image: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiPokilTA3i-BCj2fQ5MblRuUMpPWk8SzP1wrCROPlLAvqzCLwnWiRGr8buWDJd7TLWXd9vlRsubajp94nnCwl62fkQVYvqaUdn8NFjZxKAOX0_PoSXr1wHFjcq-dNf4e6yB_w9idBap8qi/s640/taktovani+G3258.png"
tags: ["Počítače"]
aliases:
  - "/2015/07/taktovani-po-letech.html"
---

<div class="separator" style="clear: both; text-align: center;">
</div>
<div class="separator" style="clear: both; text-align: center;">
{{< obr600 "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiPokilTA3i-BCj2fQ5MblRuUMpPWk8SzP1wrCROPlLAvqzCLwnWiRGr8buWDJd7TLWXd9vlRsubajp94nnCwl62fkQVYvqaUdn8NFjZxKAOX0_PoSXr1wHFjcq-dNf4e6yB_w9idBap8qi/s1600/taktovani+G3258.png" "Ilustrace k článku" "640" >}}</div>
<div style="text-align: justify;">
Pamatujete ty časy, kdy jsme nové AMD Athlony a Durony taktovali tak, že se grafitem (t.j. jedničkou tužkou) propojovaly jednotlivé piny násobičů přímo na procesorech[<a href="http://pctuning.tyden.cz/navody/upravy-pretaktovani/3705-athlon_xp-kompletni_navod_na_zmenu_nasobicu" target="_blank">1</a>]. To bylo na přelomu milénia, po radostných oslavách, že jsme přežili Y2K[<a href="https://cs.wikipedia.org/wiki/Probl%C3%A9m_roku_2000" target="_blank">2</a>]. Od té doby jsem se o taktování procesoru nepokoušel a vlastně to ani nebylo potřeba.&nbsp;</div>
<div style="text-align: justify;">
Loni vydal Intel ke 25 výročí značky Pentium procesor s krásným a snadno zapamatovatelným názvem G3258 a pozor! s otevřeným násobičem. Tedy přímo výzva pro taktování.</div>
<div style="text-align: justify;">
V základu běží G3258 na taktu 3,2GHz při napětí 1.04V. S originálním chladičem se nechá bez problémů taktovat na 4,3GHz při napětí 1.25V. Jedna věc je si o tom číst[<a href="http://pctuning.tyden.cz/hardware/procesory-pameti/30874?start=13" target="_blank">3</a>]. A druhá věc je vyzkoušet to. Pro srovnání výkonu byl použit jednoduchý program Prime Benchmark[<a href="https://www.google.cz/webhp?sourceid=chrome-instant&amp;ion=1&amp;espv=2&amp;ie=UTF-8#q=prime+benchmark" target="_blank">4</a>], který minutu počítá a pak vyzvrací číslo, čím větší, tím je procesor rychlejší. Zvýšení výkonu o 34% je zajímavé. Uvidíme, zda se projeví na životnosti samotného procesoru.</div>
<div style="text-align: justify;">
Je pravda, že samotný výkon není žádné terno, ale je příjemné z placičky za dva tisíce dostat výkon procesu 2× dražšího. Ano, jistě, hnidopich by se hned ozval, jaký že je to G3258 procesor, když nemá podporu instrukcí AES a AVX, ale já bych si tím nenechal zkazit hezký den. Střižna uloží výsledné video o třetinu rychleji, OCRko přečte text o třetinu rychleji; ještě že hodin reálného času se takové taktování nedotkne. Komu by se líbilo mít z oblíbené Helenky trash metál, že.<br />
Zdůrazňuji, že přetaktovaný procesor bez problémů funguje s původním malinkých chladičem, který k němu přibalil výrobce. Nutnost pořízení nějakého obřího chladiče s heatpipe by smazala ekonomickou výhodnost přetaktovaného řešení.<br />
<br />
<i>přidáno 10.8.2015:</i><br />
<i>Srovnání přetaktovaného Intel G3258@4,2GHz a Intel Core i3-4160@3,6GHz se zapnutým Hyper-threadingem[<a href="https://cs.wikipedia.org/wiki/Hyper-threading" target="_blank">5</a>]. Zdůrazňuji, že Core i3 je o 75% dražší, čili je to procesor lepší třídy. Testovalo se na identickém hardware, to je jasná věc.</i><br />
<div class="separator" style="clear: both; text-align: center;">
{{< obr600 "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjypOUFc9pGJU4pJzleoZpfOKBTJhzIqWndJKF8Q-9Dva9XqptcKXxIxoetvdiMh4SrZga4AvZykm_RpR_CT8HulIRNELevLgzVt_Oj5sZ9OdogZ7WucQr2IrGI8qWyTW5U_UxbWkqf9snQ/s1600/testik.png" "Ilustrace k článku" "640" >}}</div>
<i>Hodně záleží na využití počítače, dražší procesor bude ve vícevláknových úlohách jednoznačně lepší. Ale vzhledem k tomu, že nejčastěji na mém počítači běží virtualbox kvůli testem skriptů, někdy úmorné SQL dotazy v Access 97 spuštěném ve virtuálních WinXP. Výpočty neprovádím. Pokud se něco počítá, tak obrázky, skeny, OCRka nebo videoformáty. Volím tedy variantu levnější. Vlastně jenom proto, abych v reálu ověřil, kolik naběhá takový přetaktovaný procesor dní, týdnů, měsíců či let...</i></div>
