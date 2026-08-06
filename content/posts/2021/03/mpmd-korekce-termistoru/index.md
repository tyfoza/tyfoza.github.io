---
title: "MPMD korekce termistoru..."
date: 2021-03-21T13:31:00.001Z
url: "/posts/2021/03/mpmd-korekce-termistoru/"
summary: "Výrobce Mini Delty uvádí, že v tiskárně je termistor NTC100kΩ/B3950. Při tisku ASA, jsem potřeboval mít teplotu filamentu někdy až na 260°C. Narazil jsem na problém, že i když tiskárně nastavím teplotu 270°C, což je maximální, kterou firmware akceptuje; tak filament byl pořád málo horký. Až měření reálné teploty na kostce hotendu dalo odpověď. Tiskárna vidí teplotu s velkou chybou a při maximální teplotě (270°C) měl reálně hotend sotva 245°C. Rychlé řešení ze šuplíku – k termistoru byl v sérii připojen rezistor 82Ω. Pořád je výsledek malinko nelinérní, inu termistor, ale funguje to dostatečně. Měření Monoprice Mini Delta s běžným tiskárnovým termistorem NTC100kΩ/B3950 [ 1 ] a v sérii zapojeným rezistorem 82Ω. Takto už není problém držet se při tisku teplot, které doporučuje výrobce filamentů."
cover:
    image: "obr-01.webp"
tags: ["3D"]
aliases:
  - "/2021/03/mpmd-korekce-termistoru.html"
---

<p>Výrobce Mini Delty uvádí, že v tiskárně je&nbsp; termistor NTC100kΩ/B3950.</p><p>Při tisku ASA, jsem potřeboval mít teplotu filamentu někdy až na 260°C. Narazil jsem na problém, že i když tiskárně nastavím teplotu 270°C, což je maximální, kterou firmware akceptuje; tak filament byl pořád málo horký. Až měření reálné teploty na kostce hotendu dalo odpověď. Tiskárna vidí teplotu s velkou chybou a při maximální teplotě (270°C) měl reálně hotend sotva 245°C.</p><p>Rychlé řešení ze šuplíku – k termistoru byl v sérii připojen rezistor 82Ω. Pořád je výsledek malinko nelinérní, inu termistor, ale funguje to dostatečně.</p><br />Měření Monoprice Mini Delta s běžným tiskárnovým termistorem NTC100kΩ/B3950 [<a href="https://www.na3d.cz/p/2482/termistor-pro-3d-tiskarnu-1-m-kabel" target="_blank">1</a>] a v sérii zapojeným rezistorem 82Ω. Takto už není problém držet se při tisku teplot, které doporučuje výrobce filamentů.<div class="separator" style="clear: both; text-align: center;">{{< obr600 "obr-01.webp" "Ilustrace k článku" "277" >}}</div><p><br /></p>