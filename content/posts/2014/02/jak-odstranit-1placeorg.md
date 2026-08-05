---
title: "Jak odstranit 1place.org"
date: 2014-02-21T10:19:00.003Z
url: "/posts/2014/02/jak-odstranit-1placeorg/"
tags: ["Počítače"]
aliases:
  - "/2014/02/jak-odstranit-1placeorg.html"
---

Otravný program, který instaluje službu proxy serveru, přes něj přidává reklamy a otevírá vyskakovací okna. Ke dni 21.2.2014 není detekován žádným adware/spyware/care/combofix programem ani antiviry jako norton, avast, comodo, mcafee, eset (víc jsem jich nezkoušel). On to vlastně není ani virus nebo malware. Tento typ programu bude spíše nějaký harassware.<br />
<i><br /></i>
<i>Projevy</i><br />
- při hledání v googlu zobrazuje nejprve odkazy na 1place.org<br />
- přidává reklamy tam, kde nemají být<br />
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;na hlavní stránce www.google.com nebo pod články cs.wikipedia.org<br />
- reklamní proužek se sdělením „You need to update your version of media player“<br />
- těsně po zapnutí počítače hlásí prohlížeč, že nemůže najít proxy server<br />
<i><br /></i>
<i>Kterak se této havěti snadno zbaviti</i><br />
<i>1) Jaký port používá nechtěná proxy?</i><br />
Ovládácí panel - &nbsp;Síť a Internet - Možnosti Internetu - Připojení - dole Nastavení místní sítě. Tam bude nastavený proxy server např.&nbsp;<span style="font-family: 'Courier New', Courier, monospace;">127.0.0.1</span>&nbsp;port&nbsp;<span style="font-family: 'Courier New', Courier, monospace;">9980</span>. Port se může lišit.<br />
<i>2) Jaký program běží na tomto portu?&nbsp;</i><br />
Najít jeho název, umístění a smazat.<br />
Příkazový řádek Win+R Spustit&nbsp;<span style="font-family: 'Courier New', Courier, monospace;">cmd</span><br />
<span style="font-family: Courier New, Courier, monospace;">netstat -ao | find "9980"</span><br />
v posledním sloupci zobrazí&nbsp;<span style="font-family: 'Courier New', Courier, monospace;">PID p</span>rocesu, který proces to je najdeme pomocí:<br />
<span style="font-family: Courier New, Courier, monospace;">tasklist | find "PID"</span><br />
vrací název spuštěného program např. <span style="font-family: Courier New, Courier, monospace;">PDesktop.exe</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">taskmgr</span><br />
ve správci úloh v kartě Procesy nebo Služby najdeme <span style="font-family: Courier New, Courier, monospace;">Pdesktop.exe</span> stačí kliknout pravým myšítkem - Otevřít umístění souboru a máme ho!<br />
Další volbu pak - Ukončit strom procesu.<br />
Odinstalovat tento „program“ v Ovládacích panelech - Odinstalovat program.<br />
Ručně odstranit neexistující službu pomocí&nbsp;<span style="font-family: 'Courier New', Courier, monospace;">regedit&nbsp;</span>v seznamu služeb:<br />
<span style="font-family: Courier New, Courier, monospace;">HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Services</span><br />
Zbývá zrušit použití proxy serveru pro připojení Ovládácí panel - &nbsp;Síť a Internet - Možnosti Internetu - Připojení - dole Nastavení místní sítě.<br />
<br />
<i>Jako při každém zásahu do systému platí – dvakrát měř a jednou řež!</i>