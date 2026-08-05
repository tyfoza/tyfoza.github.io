---
title: "Druhá světová válka - reenactment"
date: 2014-08-04T21:57:00.002Z
tags: ["Tak jde čas", "Počítače"]
---

<div class="separator" style="clear: both; text-align: center;">
</div>
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhfKxWeonkB39TnTSRTcHb6KSFF4iHW_Xv1fLAgBv1aG53LtsQlNNs3jTzregRxVHkX2eMCCp42A_mxwSvbcvL_6KEQL6zWVxM3e0C5kqWm4Lb5soXBHbJIzBSAqQYG8UHBzDyzYEWcQvKN/s1600/hd1.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img border="0" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhfKxWeonkB39TnTSRTcHb6KSFF4iHW_Xv1fLAgBv1aG53LtsQlNNs3jTzregRxVHkX2eMCCp42A_mxwSvbcvL_6KEQL6zWVxM3e0C5kqWm4Lb5soXBHbJIzBSAqQYG8UHBzDyzYEWcQvKN/s1600/hd1.jpg" height="480" width="640" /></a></div>
[<a href="https://plus.google.com/photos/112269704324559337988/albums/6043830226099917105" target="_blank">fotky</a>]<br />
Jak to vypadá, když Městská hlídka vyrazí na bojiště II. světové války? Místy krvavé, místy úsměvné. Pod zvoleným alteregem vstříc novým zážitkům. Každý tank musí dostat „nálepku“ výbušnou a každý účastník si musí svoji hodnost obhájit.<br />
Válčil jsem jako účetní Fantozzi na počest malebného výjevu „lovecká sezóna“, kdo neviděl neuvěří viz. [<a href="https://www.youtube.com/watch?v=kZ1slDKG4HQ" target="_blank">1</a>] – válečná zóna je až od čtvrté minuty.<br />
<br />
Velmi slušné a náročné mapy pro kooperativní multiplayer ke stažení viz.[<a href="http://www.rsredsquadron.com/download.php?list.40" target="_blank">2</a>].<br />
<br />
<i>pozn. jak hrál kooperativní multiplayer Hidden and Dangerous 2 po LAN ve Windows 7 a 8.&nbsp;</i><br />
Jedenáct let stará hra Hidden and Dangerous 2 viz.[<a href="http://bonusweb.idnes.cz/hidden-dangerous-2-ceska-verze-d25-/Recenze.aspx?c=A031029_hiddendangerous2_bw" target="_blank">2</a>] běží i v nových operačních systémech Windows 7 a Windows 8. Bohužel při pokusu o síťovou hru LAN vznikne problém, kdy je hra se serverem vytvořena, ostatní ji vidí, ale když se pokusí připojit, vypíše se hlášení „vytváří se klient...“ a dál se nic neděje.<br />
Problém je v zapnutém protokolu IPv6, hra potřebuje čtyři UDP porty. První se zpracuje pomocí IPv6 a ostatní pomocí IPv4. Reálně se tedy hra nemůže propojit. Jediné řešení je vypnout celý protokol IPv6, což je nutné skrze úpravu registrů[<a href="https://www.sevecek.com/Lists/Posts/Post.aspx?ID=125" target="_blank">4</a>], podrobný postup je popsán na stránkách Microsoft viz.[<a href="http://support.microsoft.com/kb/929852/cs" target="_blank">5</a>].<br />
V&nbsp;<span style="background-color: white; color: #4c4c4c; line-height: 18.133333206176758px;"><span style="font-family: Courier New, Courier, monospace;">HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\TCPIP6\Parameters</span><span style="font-size: 11px;">&nbsp;</span></span>vytvořte novou DWORD (32bit) hodnotu s názvem&nbsp;<span style="background-color: white; color: #4c4c4c; line-height: 18.133333206176758px;"><span style="font-family: Courier New, Courier, monospace;">DisabledComponents</span><span style="font-size: 11px;">&nbsp;</span></span>a hodnotou<span style="font-family: Courier New, Courier, monospace;"> FF</span>.<br />
<br />
<i>pozn. jak v mapě povolit veškeré vybavení</i><br />
Editujte soubor&nbsp;<span style="color: #4c4c4c; font-family: Courier New, Courier, monospace;"><span style="line-height: 18.133333206176758px;">mpmaplist.txt&nbsp;</span></span>ve složce hry. Mapa je vymezena tagy <span style="font-family: Courier New, Courier, monospace;">&lt;MAP name="... </span>a <span style="font-family: Courier New, Courier, monospace;">&lt;/MAP&gt;</span>, uvnitř mapy je seznam vybavení uzavřený mezi tagy&nbsp;<span style="font-family: Courier New, Courier, monospace;">&lt;ALLOWEDITEMS &nbsp;version="0.1"&gt;</span> a&nbsp;<span style="font-family: Courier New, Courier, monospace;">&lt;/ALLOWEDITEMS&gt;</span><span style="font-family: inherit;">. Pokud chcete mít k dispozici veškeré vybavení, vložte mezi tyto tagy&nbsp;</span>obsah souboru <a href="http://tyf.sweb.cz/hd2/id_items.txt" target="_blank">items_id.txt</a>[<a href="http://tyf.sweb.cz/hd2/id_items.txt" target="_blank">6</a>].