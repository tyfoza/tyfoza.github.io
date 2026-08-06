---
---

<style>
/* 1. Výchozí stav: na mobilu schováme citát i naši novou mezeru */
.moudro-dne-wrapper,
.mezera-pro-clanek {
    display: none;
}

/* 2. Na PC box ukážeme a chytře oddělíme od toku stránky */
@media (min-width: 768px) {
    .moudro-dne-wrapper {
        display: block;
        position: relative; /* Slouží jako kotva pro absolutní pozici */
        height: 0;          /* Kontejner nezabere ŽÁDNÉ místo, vymaže "ducha" původního boxu */
        overflow: visible;
    }

    .moudro-dne {
        position: absolute; /* Vytrhne citát z toku textu, už nikdy nebude odtlačovat články */
        right: -180px;      /* PÁČKA 1: Posun doprava k nápisu Archiv (lze ladit) */
        top: -70px;         /* PÁČKA 2: Posun nahoru/dolů k horní liště (lze ladit) */
        width: 250px;
    }

    .moudro-dne-text {
        font-size: 1rem;
        line-height: 1.4;
        text-align: justify;
        color: var(--secondary);
        opacity: 0.65;
    }

    .mezera-pro-clanek {
        display: block;
        height: 40px;       /* PÁČKA 3: Tímto číslem přesně určíš mezeru JEN nad prvním článkem */
    }
}
</style>

<!-- Hlavní obal, který nevyhrazuje žádné místo v textu -->
<div class="moudro-dne-wrapper">
    <div class="moudro-dne">
        <div class="moudro-dne-text">
            <div id="dailyVersesWrapper"></div>
            <script async="async" defer="defer" src="https://dailyverses.net/get/verse.js?language=cep"></script>
        </div>
    </div>
</div>

<!-- Zde si přesně definujeme mezeru před prvním článkem -->
<div class="mezera-pro-clanek"></div>