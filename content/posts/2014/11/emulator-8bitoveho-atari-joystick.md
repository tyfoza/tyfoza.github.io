---
title: "Emulátor 8bitového Atari, joystick a 64bitový Windows"
date: 2014-11-27T00:20:00.004Z
url: "/posts/2014/11/emulator-8bitoveho-atari-joystick/"
tags: ["Počítače", "Počítače.8bit"]
aliases:
  - "/2014/11/emulator-8bitoveho-atari-joystick.html"
---

Dvě otázky: <i>Lze k moderním 64bitovým Windows připojit Atari joystick z roku 1985? Bude fungovat i v emulátoru?</i>&nbsp;Prosté dvě odpovědi: <i>Ano. Ano.</i><div>
<br /></div>
<div>
Stačí nainstalovat ovladač pro připojení joysticku do paralelního portu LPT: <a href="http://sourceforge.net/projects/ps2padd/files/ppjoysetup-0-8-4-6.exe/download" target="_blank">ppjoysetup-0-8-4-6</a>[<a href="http://sourceforge.net/projects/ps2padd/files/ppjoysetup-0-8-4-6.exe/download" target="_blank">1</a>][<a href="http://uloz.to/xJ3hKSdf/ppjoysetup-0-8-4-6-rar" target="_blank">2</a>]<div>
<div style="text-align: justify;">
V konfiguraci PPJoy přidáme nový joystick - virtuální pro testování nebo paralelní a pro naše zapojení vyhovuje LPT JoyStick. Existuje i obrázkový návod[<a href="http://uloz.to/x48dDv4/ppjoy-turorial-zip" target="_blank">3</a>].</div>
<div>
<br /></div>
<div>
Připojení digitálního joysticku[<a href="http://cs.wikipedia.org/wiki/Joystick" target="_blank">4</a>] Atari s konektorem Canon 9 pin podle atari800emu-doc-LPTJoy nebo nápovědy Atari800win Plus:</div>
<div>
<div>
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;LPTjoy interface (designed by Petr Sumbera)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp; &nbsp;[ CANON 25 MALE ] &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; [ CANON 9 M ]</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;"><br /></span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(acknowledge) &nbsp;10 ........................... 4 &nbsp;(right)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(busy) &nbsp; &nbsp; &nbsp; &nbsp; 11 ........................... 3 &nbsp;(left)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(out of paper) 12 ........................... 2 &nbsp;(down)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(select) &nbsp; &nbsp; &nbsp; 13 ........................... 1 &nbsp;(up)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;"><br /></span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(error) &nbsp; &nbsp; &nbsp; &nbsp;15 ........................... 6 &nbsp;(button)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;"><br /></span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(strobe) &nbsp; &nbsp; &nbsp; &nbsp;1 ........................... 7 &nbsp;(Ucc)</span></div>
<div>
<span style="font-family: Courier New, Courier, monospace;">(ground) &nbsp; &nbsp; &nbsp; 25 ........................... 8 &nbsp;(ground)</span></div>
</div>
<div>
podle zapojení Atari joysticku není pin 7 zapojen[<a href="http://old.pinouts.ru/Inputs/JoystickAtari2600_pinout.shtml" target="_blank">5</a>] už od dob Atari 2600. Nezáleží na tom, zda máte paralelní port na základní desce nebo připojený před USB třeba k notebooku.</div>
</div>
<div>
<br /></div>
<div>
Atari800emu[<a href="http://atari800.sourceforge.net/" target="_blank">6</a>] detekuje LPTjoy automaticky a dá se použít ihned - nejlepší pro fullscreen použití.</div>
<div>
V emulátoru Atari800win Plus[<a href="http://www.a800win.atari-area.prv.pl/" target="_blank">7</a>] je třeba přiřadit číslo joysticku a jeho typ: Input - Joystick na LPT1: LPT Joystick</div>
<div>
<br /></div>
<div>
Dopřejte svým dětem hratelnosti osmibitových her dříve, než je pohltí moderní digitální peklo.</div>
</div>
