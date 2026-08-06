---
title: "Externí disk s daty hlásí, že musí být naformátován"
date: 2014-12-22T16:03:00Z
url: "/posts/2014/12/externi-disk-s-daty-hlasi-ze-musi-byt-23/"
summary: "Stalo se vám někdy, že vám externí disk s vašimi daty po připojení napsal: Disk v jednotce X: musí být před použitím naformátováno. Chcete provést formátování? Tato hláška vyděsí a nepotěší. Příčin může být mnoho a předpokládejme, že vyděšený uživatel zkusil běžné pokusy jako: – připojit externí disk k jinému počítači – vyměnit kabel – vyjmout disk z externího boxu a připojit ho přímo k počítači, abychom ověřili, že není vadná elektronika externího boxu A že všechny pokusy selhaly? Co dál? Zkusme připojit disk k počítači, na kterém běží nějaké linuxová distribuce – Ubuntu, Suse, cokoli. Systém nám disk automaticky nerozpozná a nepřipojí. Zjistíme pod jakým názvem zařízení se disk do systému připojuje, pak spustíme opravu a uvidíme. Pravděpodobnost úspěchu je vysoká v případě, že disk není příliš fyzicky poškozen. Záleží na tom, jak moc disk podivně chrochtá a rachtá při pokusech o..."
cover:
    image: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhGd-eWYUxS_QinseOdKLQ5eHceUqlQ3eEQY_kLUME2-QKXi85ggRjd9WxqCzlaEdTv8GHYlvQMmyJf4brlsfHTVVTFcPD8-5u1Lxe9Wtw1MWGnshuol84eDEcRDZBkuXCv0WOWAYX4iZ9Q/s1600/format.jpg"
tags: ["Počítače"]
aliases:
  - "/2014/12/externi-disk-s-daty-hlasi-ze-musi-byt_23.html"
---

<div class="separator" style="clear: both; text-align: justify;">
Stalo se vám někdy, že vám externí disk s vašimi daty po připojení napsal: Disk v jednotce X: musí být před použitím naformátováno. Chcete provést formátování?</div>
<div class="separator" style="clear: both; text-align: center;">
{{< obr600 "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhGd-eWYUxS_QinseOdKLQ5eHceUqlQ3eEQY_kLUME2-QKXi85ggRjd9WxqCzlaEdTv8GHYlvQMmyJf4brlsfHTVVTFcPD8-5u1Lxe9Wtw1MWGnshuol84eDEcRDZBkuXCv0WOWAYX4iZ9Q/s1600/format.jpg" "Ilustrace k článku" >}}</div>
<div class="" style="clear: both; text-align: justify;">
Tato hláška vyděsí a nepotěší. Příčin může být mnoho a předpokládejme, že vyděšený uživatel zkusil běžné pokusy jako:</div>
<div class="" style="clear: both; text-align: justify;">
– připojit externí disk k jinému počítači</div>
<div class="" style="clear: both; text-align: justify;">
– vyměnit kabel</div>
<div class="" style="clear: both; text-align: justify;">
– vyjmout disk z externího boxu a připojit ho přímo k počítači, abychom ověřili, že není vadná elektronika externího boxu</div>
<div class="" style="clear: both; text-align: justify;">
A že všechny pokusy selhaly? Co dál? Zkusme připojit disk k počítači, na kterém běží nějaké linuxová distribuce – Ubuntu, Suse, cokoli.</div>
<div class="" style="clear: both; text-align: justify;">
Systém nám disk automaticky nerozpozná a nepřipojí.</div>
<div class="" style="clear: both; text-align: justify;">
Zjistíme pod jakým názvem zařízení se disk do systému připojuje, pak spustíme opravu a uvidíme. Pravděpodobnost úspěchu je vysoká v případě, že disk není příliš fyzicky poškozen. Záleží na tom, jak moc disk podivně chrochtá a rachtá při pokusech o přístup.</div>
<div style="text-align: justify;">
<u><b>1. odpojíme disk</b></u></div>
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>zjistíme jaké disky v linuxovém systému máme<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">cat /proc/partitions</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>vypíše něco jako:<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>&nbsp; <span style="font-family: Courier New, Courier, monospace;">&nbsp;major minor &nbsp;#blocks &nbsp;name</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp;8 &nbsp; &nbsp;0 &nbsp; &nbsp;8388608 &nbsp;sda</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp;8 &nbsp; &nbsp;1 &nbsp; &nbsp;1211392 &nbsp;sda1</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; &nbsp;8 &nbsp; &nbsp;2 &nbsp; &nbsp;7176192 &nbsp;sda2</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 11 &nbsp; &nbsp;0 &nbsp; &nbsp;1048575 &nbsp;sr0</span><br />
<u><b>2. připojíme disk</b></u><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>znovu vypíšeme seznam připojených zařízení<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">cat /proc/partitions</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>připojený disk přibude jako další v seznamu<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; major minor #blocks &nbsp; name</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 8 &nbsp; &nbsp; 0 &nbsp; 8388608 &nbsp; sda</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 8 &nbsp; &nbsp; 1 &nbsp; 1211392 &nbsp; sda1</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 8 &nbsp; &nbsp; 2 &nbsp; 7176192 &nbsp; sda2</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp;11 &nbsp; &nbsp; 0 &nbsp; 1048575 &nbsp; sr0</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 8 &nbsp; &nbsp;16 &nbsp; 488386584 sdb </span><b><i><span style="font-family: inherit;">&lt;-- náš připojený disk</span></i></b><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; &nbsp; 8 &nbsp; &nbsp;17 &nbsp; 488384001 sdb1</span><i><b><span style="font-family: inherit;"> &lt;-- vadná partition k opravě</span></b></i><br />
<u><b>3. pokus o přimountování disku</b></u><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>vytvořme si v aktuální složce/adresáři novou složku pro připojení disku - např. <span style="font-family: Courier New, Courier, monospace;">mujdisk</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo mount /dev/sdb1 mujdisk</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>disk se nepřipojí a systém nahlásí:<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>mount: /dev/sdb1: superblok nelze přečíst</i><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>mount: /dev/sdb1: can't read superblock</i><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>můžeme se pokusit připojit přímo zvolený souborový systém, jestli víme, jaký byl a pro další obnovu je to nezbytné. Ve windows to bude obvykle <span style="font-family: Courier New, Courier, monospace;">vfat</span> nebo <span style="font-family: Courier New, Courier, monospace;">ntfs</span>. Nevíme to, zkusíme<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo mount -t ntfs /dev/sdb1 mujdisk</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>NTFS signature is missing.&nbsp;</i><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>Failed to mount '/dev/sdb1': Nepřípustný argument&nbsp;</i><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>The device '/dev/sdb1' doesn't seem to have a valid NTFS...</i><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>tak <span style="font-family: Courier New, Courier, monospace;">ntfs</span> to není<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo mount -t vfat /dev/sdb1 mujdisk</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><i>mount: /dev/sdb1: superblok nelze přečíst</i><br />
<u><b>4. zkoumání disku a oprava</b></u><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>pro zjištění, co vlastně s diskem je použije fsck, více v manuálových stránkách<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo fsck.msdos /dev/sdb1</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>pro vlastní opravdu, automatickou se zápisem změn na disk<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo fsck.msdos /dev/sdb1 -a -w</span><br />
<u><b>5. hotovo</b></u><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>jestli pokus o připojení proběhne korektně<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; sudo mount /dev/sdb1 mujdisk</span><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>máme z části vyhráno. A je možné, že se disk bude dát připojit i do Windows.<br />
<u><b>6. kopírujme data dokud to jde</b></u><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>to že se na disk dá dostat neznamená, že se to ještě někdy jindy podaří. Vykopírujme pro jistotu data ještě v linuxu.<br />
<b><u>7. jak ve Windows kopírovat data z disku, který možná chybuj</u>e</b><br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span>ve Win není dobrý nápad kopírovat data z disku, který může být vadný třeba v Total Commanderu nebo v Průzkumníkovi. Lepší je použít příkazový řádek a postupně kopírovat pomocí<br />
<span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: 'Courier New', Courier, monospace;">&nbsp;</span><span style="font-family: Courier New, Courier, monospace;">&nbsp; xcopy zdroj cíl /E /C</span><br />
<br />
<i>Jiné možnosti?</i><br />
V linuxu se dá snadno pořídit otisk celé partition do souboru a pak přes loopback připojit, případně měnit velikost disku a jiná kouzla, která google bez problémů doporučí.<br />
<br />
Někdy je potřeba disk rozebrat a pomoct mu ručně, viz. [<a href="/posts/2013/09/vadny-pevny-disk/" target="_blank">1</a>]