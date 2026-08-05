---
title: "Přenos souborů z 8bitového Atari do PC"
date: 2014-12-14T22:00:00.002Z
tags: ["Počítače.8bit", "Počítače"]
---

<div class="separator" style="clear: both; text-align: center;">
<object class="BLOGGER-youtube-video" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" data-thumbnail-src="https://i.ytimg.com/vi/mHnUQYS61Bw/0.jpg" height="400" width="640"><param name="movie" value="https://www.youtube.com/v/mHnUQYS61Bw?version=3&f=user_uploads&c=google-webdrive-0&app=youtube_gdata" /><param name="bgcolor" value="#FFFFFF" /><param name="allowFullScreen" value="true" /><embed width="640" height="400"  src="https://www.youtube.com/v/mHnUQYS61Bw?version=3&f=user_uploads&c=google-webdrive-0&app=youtube_gdata" type="application/x-shockwave-flash" allowfullscreen="true"></embed></object></div>
<div style="text-align: justify;">
XRZDISK <a href="http://tyf.sweb.cz/atari/xrzdisk.zip" target="_blank">komplet ke stažení</a> viz. [<a href="http://tyf.sweb.cz/atari/xrzdisk.zip" target="_blank">0</a>]<br />
Nezbytnost nezbytná. Aneb jak po pětadvaceti letech konečně zazálohovat staré programy, zdrojové kódy a texty uložené na 5.25" disketách[<a href="http://cs.wikipedia.org/wiki/Disketa" target="_blank">1</a>]. Je třeba je přenést z osmibitového Atari do PC, ať mám čím krmit emulátor. A třeba opět nahlédnout to tajů Turbo Basicu[<a href="http://en.wikipedia.org/wiki/Turbo-Basic_XL" target="_blank">2</a>], Kyan Pascalu[<a href="http://www.atarimagazines.com/v4n7/kyanpascal.html" target="_blank">3</a>], Actionu[<a href="http://en.wikipedia.org/wiki/Action!_%28programming_language%29" target="_blank">4</a>] a Atmasu[<a href="http://atariwiki.strotmann.de/wiki/Wiki.jsp?page=Atmas%20II" target="_blank">5</a>].</div>
Prográmek pro přenos se jmenuje XRZ na počest slavné románové kódové tabulky[<a href="http://cs.wikipedia.org/wiki/Maty%C3%A1%C5%A1_Sandorf" target="_blank">6</a>].<br />
<br />
<span style="font-family: 'Courier New', Courier, monospace;">XRZ 4B ATARI -&gt; PC CABLE&nbsp;</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">[ CANON 25 MALE ] &nbsp; &nbsp; &nbsp; [ CANON 9 FEMALE ] JOYPORT 0</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; &nbsp;2 .................... 6 trigger 0 &nbsp; &nbsp;$378, bit 0</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 13 .................... 1 output bit 0 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 12 .................... 2 output bit 1</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 10 .................... 3 output bit 3</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 11 .................... 4 output bit 4</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 25 .................... 8 GND &nbsp; &nbsp; &nbsp;</span><br />
<span style="font-family: Courier New, Courier, monospace;"><br /></span>
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; [ CANON 9 FEMALE ] JOYPORT 1</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 15 .................... 1 output bit 5 $379, all output bits</span><br />
<br />
Paralelní port PC, z Atari jsou použity 4 bity joy portu 0 a 1. bit joy portu 1 jako řídící. PC potvrzuje příjem na trigger 0 joyportu 0.<br />
<br />
Řízení přenosu 5. bit – každý půlbajt &lt;16 obsahuje přenesená data; půlbajt &gt; 15 je řídící příkaz.<br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 16 ... další bude vysílán vyšší půlbajt</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 17 ... další bude vysílán nižší půlbajt</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 18 ... přenos souboru dokončen</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 19 ... přenos jména souboru dokončen</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 20 ... všechno přeneseno, konec</span><br />
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; 21 ... chyba čtení, poškozený soubor</span><br />
<span style="text-align: justify;"><br /></span>
<span style="text-align: justify;">Struktura programu je hrubá přesně tak, že mohla být použita k výuce. Třeba někdy dojde k následné optimalizace jak přenosu, tak programu.</span><br />
<div style="text-align: justify;">
<span style="text-align: start;"><a href="https://docs.google.com/document/d/1akNHpPtc6BPgQyvTOy9aXhs9GDVLZnIAG9-HJtnp4yY/edit?usp=sharing" target="_blank">XRZ4BO.ENT</a>[<a href="https://docs.google.com/document/d/1akNHpPtc6BPgQyvTOy9aXhs9GDVLZnIAG9-HJtnp4yY/edit?usp=sharing" target="_blank">7</a>]&nbsp;v Turbo Basicu XL řeší p</span>řenos jednoho souboru - čte soubor po jednom bajtu</div>
<div style="text-align: justify;">
<a href="https://docs.google.com/document/d/1d9kuWZBoOMzoa5GVhRgNHyIxJVhQpLZk024bcF2fROw/edit?usp=sharing" target="_blank">XRZ4B.PAS</a>[<a href="https://docs.google.com/document/d/1d9kuWZBoOMzoa5GVhRgNHyIxJVhQpLZk024bcF2fROw/edit?usp=sharing" target="_blank">8</a>]&nbsp;pro PC v Turbo Pascalu pro příjem</div>
<div style="text-align: justify;">
<a href="https://docs.google.com/document/d/1pGDIdMGOcWCR3YJ5fj4obgwtIgTRhG8TeBv-ARlmTFw/edit?usp=sharing" target="_blank">XRZDISK2.ENT</a>[<a href="https://docs.google.com/document/d/1pGDIdMGOcWCR3YJ5fj4obgwtIgTRhG8TeBv-ARlmTFw/edit?usp=sharing" target="_blank">9a</a>] pro odesílání více souborů - používá 512B buffer pro čtení souboru<br />
<a href="https://docs.google.com/document/d/1DJf9nY86YC0o66jNfJlOHyut-0Td00lMYiPXppi6dGg/edit?usp=sharing" target="_blank">XRZDISK5.ENT</a>[<a href="https://docs.google.com/document/d/1DJf9nY86YC0o66jNfJlOHyut-0Td00lMYiPXppi6dGg/edit?usp=sharing" target="_blank">9b</a>] odešle více souborů z Atari, ptá se na vypnutí zobrazování. Poslední verze.</div>
<a href="https://docs.google.com/document/d/1PPHIY_Isy54ABElaqRPHEQm1ECUn-m_fP0m4nsSpt8Q/edit?usp=sharing" target="_blank">XRZDISK.PAS</a>[<a href="https://docs.google.com/document/d/1PPHIY_Isy54ABElaqRPHEQm1ECUn-m_fP0m4nsSpt8Q/edit?usp=sharing" target="_blank">10</a>]&nbsp;pro příjem více souborů<br />
<br />
První chybná domněnka byla, že rychlost přenosu je limitovaná více rychlostí vstupně výstupních operací disketové mechaniky Atari 1050, než rychlostí samotného Turbo Basicu. Jenom pro radost jsem odesílání souborů přepsal i v Kyan Pascalu, který je kompilovaný a řádově rychlejší než TBasic. Je vtipné, že Kyan Pascal umožňuje zápis do paměti pomocí vlastního příkazu assign - psali o tom v časopise Antic 7/1985 [<a href="http://www.atarimagazines.com/v4n7/kyanpascal.html" target="_blank">11</a>] a my to známe spíš z příloh zpravodajů vydávaných Atarikluby Praha, Hodonín, Plzeň[<a href="http://www.atari8.cz/calp/data/misc_kp/index.php?c=42" target="_blank">12</a>] o pár let později, ale česky. Dneska máme k dispozici původní manuál[<a href="http://atarionline.pl/biblioteka/materialy_ksiazkowe/Kyan_Pascal_Tutorial_Manual.pdf" target="_blank">13</a>] z roku 1985 a tam je zmínka, že assign je definován jako assign(ukazatel, integer), takže umožní PEEK/POKE jen do adresy 32767. Takže musely pomoct tři řádky assembleru a znalost rozložení paměti. Prací s ukazateli a zásobníkem vznikají obří časové režije s nimiž se kompilátor Kyan nevypořádá.<br />
<a href="https://docs.google.com/document/d/1vj6myLQH1gEN6NfHn5_Il12XTxg2c_mCBHUEjx7IQQw/edit?usp=sharing" target="_blank">XRZ4BO.PAS</a>[<a href="https://docs.google.com/document/d/1vj6myLQH1gEN6NfHn5_Il12XTxg2c_mCBHUEjx7IQQw/edit?usp=sharing" target="_blank">14</a>] odesílání jednoho souboru, čte po bajtu v Kyan Pascalu.<br />
<br />
A jak celý přenos urychlit? Turbo Basic XL má svůj kompiler a výsledný program je výrazně rychlejší a celý přenos taktéž. Program spouštěný přímo z interpretu Turbo Basicu – rychlost přenosu 40zn/sec. Kompilovaný TBasic 110zn/sec.<br />
<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center;"><tbody>
<tr><td style="text-align: center;"><a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTvF5BWvMIQcIKm3aMrk-nOYoBkTQiqmnjkuba5OiBknFcHrTmuAeZNbRPyKF3QkuC8hVKxhS1GbA15h8QYirvCHtPeK4AORnuq8hVYrLQhzPNvCz0ZYWI3UAyJrfDkELA8Q9rTLPumb_m/s1600/xrzrychlost.png" imageanchor="1" style="margin-left: auto; margin-right: auto;"><img border="0" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTvF5BWvMIQcIKm3aMrk-nOYoBkTQiqmnjkuba5OiBknFcHrTmuAeZNbRPyKF3QkuC8hVKxhS1GbA15h8QYirvCHtPeK4AORnuq8hVYrLQhzPNvCz0ZYWI3UAyJrfDkELA8Q9rTLPumb_m/s1600/xrzrychlost.png" /></a></td></tr>
<tr><td class="tr-caption" style="text-align: center;">kompilovaný Turbo Basic XL se zapnutým zobrazováním</td></tr>
</tbody></table>
<i><b>S vypnutým zobrazením dosahuje rychlost přenosu 160zn/s, heč! (POKE 559,0)</b></i><br />
<br />
<div>
<div class="separator" style="clear: both; text-align: center;">
<object class="BLOGGER-youtube-video" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" data-thumbnail-src="https://i.ytimg.com/vi/7EEK2-aEnVU/0.jpg" height="400" width="640"><param name="movie" value="https://www.youtube.com/v/7EEK2-aEnVU?version=3&f=user_uploads&c=google-webdrive-0&app=youtube_gdata" /><param name="bgcolor" value="#FFFFFF" /><param name="allowFullScreen" value="true" /><embed width="640" height="400"  src="https://www.youtube.com/v/7EEK2-aEnVU?version=3&f=user_uploads&c=google-webdrive-0&app=youtube_gdata" type="application/x-shockwave-flash" allowfullscreen="true"></embed></object></div>
<div style="text-align: center;">
Jak se kompiluje Turbo Basic</div>
<div style="text-align: center;">
<br />
<div style="text-align: justify;">
<span style="font-size: xx-small; text-align: start;">Otázka: J</span><span style="text-align: start;">ak přenesené soubory zase vložit do jednoho .ATR souborů pro použití v emulátoru? Osobně jsem tuto věc potřeboval, když jsem chtěl znovu spustit padesát vlastních levelů uložených v BoulderDashConstructionKit[</span><a href="http://atari.panprase.cz/?action=detail&amp;co=1820" style="text-align: start;" target="_blank">15</a><span style="text-align: start;">].</span></div>
<div style="text-align: justify;">
<span style="text-align: start;">Prográmek <a href="https://docs.google.com/document/d/1xXIVegPDEinUjcJCCyMbNhKabBIIvi6Yu_G-JirUBOM/edit" target="_blank">XRZGLUE.ENT</a>[<a href="https://docs.google.com/document/d/1xXIVegPDEinUjcJCCyMbNhKabBIIvi6Yu_G-JirUBOM/edit?usp=sharing" target="_blank">16</a>] tuto věc řeší. Složku na disku s přenesenými soubory nastavíme jako disk H3: v emulátoru. Do jednoty D2: připojíme zformátovaný .ATR soubor. Pokud potřebujeme na obrazu disku DOS.SYS a DUP.SYS, musíme si je tam uložit před použitím XRZGLUE.</span></div>
<div style="text-align: justify;">
<br /></div>
</div>
A na závěr můžete nostalgicky zavzpomínat: Jak zjistit velikost souboru v Turbo Basicu XL?<br />
<a href="https://docs.google.com/document/d/1R4AyvbZ6e-mtRPJDig-ypyRjZIgVnX0YEjixKk3KPYA/edit?usp=sharing" target="_blank">FSIZE.ENT</a>[<a href="https://docs.google.com/document/d/1R4AyvbZ6e-mtRPJDig-ypyRjZIgVnX0YEjixKk3KPYA/edit?usp=sharing" target="_blank">17</a>]</div>
