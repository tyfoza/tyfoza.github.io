---
title: "Automatické titulky a překlad"
date: 2026-10-16T00:19:03+02:00
summary: "K mému oblíbenému seriálu z roku 1983 jsem nedohledal anglické titulky. Vytvoříme je automaticky ze zvukové stopy; a když už budeme mít anglické titulky, tak je strojově přeložíme do češtiny."
cover:
    image: "Hardcastle_and_McCormick.webp"
tags: ["Počítače"]
draft: false
---

### Přepis a strojový překlad titulků k filmu nebo seriálu

#### Motivace
K mému oblíbenému seriálu z roku 1983 jsem nedohledal anglické titulky. Vytvoříme je automaticky ze zvukové stopy; a když už budeme mít anglické titulky, tak je strojově přeložíme do češtiny.

#### Výsledek
Tři série seriálu [Hardcaste and McCormick](https://www.csfd.cz/film/123702-hardcastle-a-mccormick/prehled/) mají v součtu 54 hodin videa. Celý postup přepisu a překladu běžel asi trojnásobek tohoto času. Vše lokálně bez závislosti na cloudu a to mám jen starou NVIDIA Quadro RTX 4000. Oba použité AI modely se bez problému vejdou do 8GB.

#### Python skripty ke stažení
[stáhnout](https://drive.google.com/drive/folders/1RE9ijzIvJKWEN6I34Lx8kmmEgDO2fyLg?usp=sharing) z Google Disku

#### Slepá ulička
Zkusil jsem vygenerovat čtený překlad do audio stopy, ale výsledek byl tristní. Ne, že by to nefungovalo, ale titulky jsou jednoznačně lepší.

### 1. extrakce zvukové stopy z filmu
Ze všech filmů v aktuální složce uloží zvuk, výstup pojmenuje stejně jako film, liší se pouze přípona

```bash
film2wav.sh
```
### 2. převod angličtiny na text
Pokud by existovaly titulky `.srt` v angličtině, tento krok přeskočíme a ušetříme nemalé množství času, protože přesný přepis textu ze zvuku trvá asi 2,5 násobek délky audia.

Přepíše všechny `.wav` soubory v aktuální složce do podoby filmových titulků `.srt`
nahrát `.wav` soubory a spustit:
```bash
python3 wav_srt.py
```

### 3. překlad do češtiny
Samotný překlad běží svižně. Přeloží všechny `.srt` titulky v aktuální složce do češtiny a uloží je jako `_cs.srt`

**CUDA nebo CPU ?**\
v programu `srt_preloz.py` je na výběr, jestli má překlad běžet akcelerovaně
```python
NVIDIA_CUDA = True  #False pro CPU        
```
pak stačí spustit a všechny anglické  titulky se přeloží do češtiny

```bash
python3 srt_preloz.py
```

Víc netřeba. 
- umíme vycucnout anglický zvuk z filmu, uložit ho jako `.wav`
- přepsat do textu a uložit jako titulky `.srt`
- přeložit anglické `.srt` titulky do češtiny

## Instalace potřebných knihoven
*vytvořit prostředí:*\
python3 -m venv whisper_env

*aktivovat prostředí:*\
source whisper_env/bin/activate

**vybrat verzi knihovny**\
*verze pro NVIDIA CUDA:*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

*verze pro CPU (univezální):*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

*verze pro AMD karty, ale pouze Linux/WSL:*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1
```
*verze pro macOS zapne hw akceleraci Apple Metal (MPS):*
```bash
pip install torch torchvision torchaudio
````

**dále potřebujeme knihovny**
```bash
pip install -U openai-whisper pysrt "transformers==4.49.0" sentencepiece accelerate
```


# Jak fedruje `wav_srt.py`

Tento program slouží k plně automatickému přepisu zvukových stop (`.wav`) do anglických titulků (`.srt`) s integrovaným systémem pro čištění chyb a opravu časování. Řeší typické neduhy AI přepisu, jako jsou "visící" titulky během dlouhých pasáží ticha nebo generování nesmyslných textů (halucinací).

---

## Použitý AI model a jeho nastavení

Program využívá k přepisu mluveného slova model **Whisper od OpenAI**.

*   **Verze modelu:** `large` (největší a nejpřesnější dostupná verze, která minimalizuje chyby v porozumění).
*   **Akcelerace:** Model je natvrdo nastaven k běhu na grafické kartě (`device="cuda"`), což zajišťuje několikanásobně rychlejší zpracování než přes procesor.

### Konfigurace při samotném přepisu (funkce `transcribe`)
Aby model nevynechával věty v rozhovorech a zároveň si nevymýšlel texty v hudebních pasážích, je volán s těmito specifickými parametry:
*   `language="en"`: Vynucuje rozpoznávání angličtiny (zabraňuje tomu, aby model začal náhodně překládat nebo detekovat jiný jazyk ze šumu).
*   `condition_on_previous_text=False`: Zabraňuje modelu, aby se zacyklil. Pokud by tato hodnota byla `True`, model by se mohl „zaseknout“ na jedné frázi a opakovat ji stále dokola.
*   `no_speech_threshold=0.6`: Zpřísňuje toleranci pro ticho. Pokud má zvukový úsek nižší pravděpodobnost mluveného slova než 60 %, model jej ignoruje jako šum nebo hudbu.
*   `verbose=True`: Zajišťuje, že program v terminálu průběžně vypisuje zachycené titulky v reálném čase.

---

## Jak program funguje (Krok za krokem)

1.  **Načtení modelu:** Skript nejprve načte model Whisper do VRAM grafické karty.
2.  **Hledání souborů:** Prohledá aktuální složku a najde všechny soubory s koncovkou `.wav`. Automaticky přitom ignoruje soubory končící na `_cz_dabing.wav` (aby nepřepisoval již hotový vygenerovaný český dabing).
3.  **Přepis zvuku:** Pokud k `.wav` souboru ještě neexistuje `.srt` soubor, spustí se AI přepis a výsledek se uloží do aktuální složky.
4.  **Čištění a oprava časů:** Jakmile je soubor `.srt` vytvořen (nebo pokud již existoval), program jej načte pomocí knihovny `pysrt` a spustí sérii oprav (viz níže).

---

## Mechanismus čištění a oprav (Post-processing)

Samotný výstup z Whisperu není pro přímé sledování ideální, proto skript provádí tři zásadní úpravy hotového textu:

### 1. Odstranění "halucinací" (Funkce `is_hallucination`)
Whisper se učil na televizních datech a v místech, kde je naprosté ticho nebo hraje pouze hudba, má tendenci vkládat vodoznaky nebo popisy hudby. Skript tyto řádky natvrdo maže:
*   Maže texty obsahující hudební značky a tagy: `"¶"`, `"sólová kytara"`, `"solo guitar"`, `"bf-watch"`, atd.
*   Maže specifické 20–30vteřinové výkřiky do ticha na konci dílů (pokud titulek trvá déle než 20 sekund a obsahuje pouze `"thank you."`, `"i'm sorry."` nebo `"uh-huh."`).

### 2. Zkrácení zacyklených slov (Funkce `clean_repeated_words`)
Pokud postava křičí nebo koktá, AI občas vygeneruje nekonečnou smyčku (např. *„No, no, no, no, no, no...“*). Skript obsahuje regulární výraz, který podobná slova zkrátí maximálně na tři opakování (*„No, no, no.“*).

### 3. Dynamická oprava časování (Funkce `fix_srt_timings`)
Toto je nejdůležitější opravný mechanismus skriptu. Řeší problém, kdy Whisper u slova, které následuje po dlouhé hudební scéně, nastaví začátek titulku na začátek hudby (titulek pak visí na obrazovce třeba 20 vteřin dříve, než postava vůbec promluví). 

**Logika opravy:**
*   Skript vezme délku textu (počet znaků) a spočítá, jak dlouho by měl titulek přirozeně svítit na obrazovce (minimálně 1,6 s, maximálně 4,8 s).
    *   *Vzorec:* `1100 ms + (počet znaků * 55 ms)`
*   Pokud titulek trvá na obrazovce déle než stanovený limit `MAX_ALLOWED_DURATION_MS` (5,5 vteřiny) a zároveň je jeho trvání výrazně delší než spočítaná doba čtení, skript zasáhne.
*   **Posun začátku:** Protože Whisper určuje *konec* mluvení vždy naprosto přesně, skript ponechá koncový čas na místě a posune *začátek* titulku dopředu tak, aby odpovídal přirozené době čtení (čímž odstraní hluché místo před promluvou).

Nakonec skript titulky přečísluje a soubor `.srt` uloží zpět na disk. V terminálu pak vypíše souhrn – kolik dlouhých titulků zkrátil a kolik vymýšlených halucinací smazal.


# Jak fedruje `srt_preloz.py`

Tento program slouží k plně offline automatickému překladu anglických filmových a seriálových titulků (`.srt`) do češtiny. Využívá k tomu dedikovanou umělou inteligenci navrženou speciálně pro vysoce kvalitní vícejazyčné překlady.

## Použitý AI model a jeho parametry

Program ke své práci využívá open-source model **NLLB-200 (No Language Left Behind)** od společnosti Meta (Facebook).

*   **Verze modelu:** `facebook/nllb-200-distilled-1.3B` (Jedná se o odlehčenou „distilled“ verzi s 1,3 miliardami parametrů, která nabízí ideální poměr mezi špičkovou kvalitou překladu a paměťovou náročností, takže se bez problémů vejde např. do 8GB VRAM grafické karty).
*   **Vstupní a výstupní jazyk:** Tokenizér je nastaven na čtení angličtiny (`src_lang="eng_Latn"`) a model je při generování natvrdo nucen zahajovat větu tokenem pro češtinu (`forced_bos_token_id=ces_token_id`), což zajišťuje konzistentní český výstup.

### Konfigurace a kvalita generování
Kvalitu a rychlost překladu řídí ve skriptu tyto klíčové parametry:

*   **`BATCH_SIZE = 16`:** Zapíná tzv. dávkové zpracování. Model nepřekládá věty jednu po druhé, ale vezme jich 16 najednou, zpracuje je paralelně a vrátí je zpět. To extrémně urychluje práci na grafických kartách (využívá se jejich masivní paralelní výkon).
*   **`num_beams=4` (Beam Search):** Klíčový parametr pro kvalitu překladu. Místo toho, aby model překládal slovo od slova tak, jak ho napadne první možnost (Greedy Search), zvažuje souběžně 4 různé „větve“ překladu a na konci vybere tu, která dává z hlediska celkového českého slovosledu největší smysl. Zabraňuje to krkolomným strojovým překladům.
*   **`max_length=256`:** Omezuje maximální délku přeložené repliky (v tokenech), čímž zamezuje tomu, aby se model u nějaké věty „zasekl“ a začal generovat nekonečný text.

## Hardwarové nastavení (GPU vs. CPU)

Skript obsahuje manuální přepínač pro volbu výpočetní jednotky:
`NVIDIA_CUDA = True` (nebo `False`)

*   **Při zapnutí na True (pro grafické karty NVIDIA):**
    Model se přesune do VRAM karty (`.to("cuda")`). Zásadní je parametr `torch_dtype=torch.float16` (poloviční přesnost) – díky němu model zabere zhruba jen poloviční velikost paměti (cca 2,7 GB) a moderní Tensor jádra na NVIDIA kartách (jako je Quadro RTX) jej dokáží počítat několikanásobně rychleji bez viditelné ztráty kvality.
*   **Při přepnutí na False (pro procesory):**
    Model běží ve standardní přesnosti `torch.float32` a přesouvá se do RAM a procesoru (`.to("cpu")`). Tato cesta je výrazně pomalejší, ale funguje na jakémkoliv hardwaru bez ohledu na grafickou kartu. 

## Jak probíhá překlad (Krok za krokem)

1.  **Vyhledání souborů:** Skript si najde všechny `.srt` soubory ve složce. Pokud už u některého existuje český protějšek s koncovkou `_cs.srt`, rovnou jej přeskočí, aby nepřekládal totéž dvakrát.
2.  **Filtrace a spojování vět:** Otevře anglický soubor pomocí knihovny `pysrt`. Projde všechny titulky a:
    *   Ignoruje prázdné titulky a titulky s halucinacemi/značkami hudby (obsahující `¶` nebo `©`).
    *   Zásadní oprava: Funkce `.replace("\n", " ")` u platných titulků smaže odřádkování. Pokud Whisper rozdělil jednu anglickou větu do dvou řádků v jednom titulku, model ji díky tomuto spojení dostane celou, pochopí kontext a nepřeloží ji jako dvě nedávající smysl oddělené části.
3.  **Dávkový překlad:** Spojené texty se rozřežou po 16 (`BATCH_SIZE`) a odesílají se na grafickou kartu.
4.  **Rekonstrukce a výpis:** Hotové překlady se vkládají přesně na ta stejná místa, odkud byl vzat anglický originál. Tím zůstanou zachovány původní zlomky sekund v časování. Program zároveň do terminálu krásně pod sebe vypisuje časové okno, anglický originál a hotový český překlad.
5.  **Uložení:** Výsledek je uložen s koncovkou `_cs.srt` v kódování UTF-8, aby se korektně zobrazovala česká diakritika.
