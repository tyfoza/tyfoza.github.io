#!/usr/bin/env python3

"""
Konzolový správce statického blogu (Hugo).

Tento skript slouží jako interaktivní CLI nástroj pro kompletní správu a automatizaci
úloh spojených s chodem blogu. Přináší přehledné rozhraní.

Hlavní funkce:
* Automaticky detekuje a bezpečně upravuje `baseURL` přímo v konfiguračním
  souboru `hugo.toml` při striktním zachování jeho formátování.
* Zajišťuje generování čistých buildů pomocí parametru `hugo --cleanDestinationDir`,
  což bezpečně promaže staré a neplatné odkazy ze složky `public/`.
* Publikování řeší GitHub Actions. Na GitHub nahrává pouze zdrojové
  soubory a nechává samotné vygenerování webu na automatizaci v cloudu.
"""

import os
import re
import subprocess
import sys

# Pokus o import interaktivního menu
try:
    from simple_term_menu import TerminalMenu
except ImportError:
    print("\033[1;31mChyba: Chybí knihovna 'simple-term-menu'.\033[0m")
    print("Pro navigaci šipkami si ji prosím nainstaluj příkazem:")
    print("\033[1;33mpython3 -m pip install simple-term-menu\033[0m")
    sys.exit(1)

DEBUG = False

# --- CESTY A KONFIGURACE ---
CONFIG_FILE = "hugo.toml"
PUBLIC_DIR = "/home/eee/muj-blog/public/"
WEB_TARGET_DIR = "/home/eee/datatyf/web"
ALLOWED_RSYNC_URL = "https://tyfoza.sytes.net/"
ALLOWED_GITHUB_URL = "https://tyfoza.github.io/"

# ANSI barevné kódování pro přehledný výstup
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
BOLD = "\033[1m"
NC = "\033[0m"  # Bez barvy

ASCII_ART = rf"""{CYAN} ▄▄▄▄▄▄▄▄▄      ▄▄                   
 ▀▀▀███▀▀▀     ██                    
    ███ ██ ██ ▀██▀ ▄███▄ ▀▀▀██  ▀▀█▄ 
    ███ ██▄██  ██  ██ ██   ▄█▀ ▄█▀██ 
    ███  ▀██▀  ██  ▀███▀ ▄██▄▄ ▀█▄██ 
          ██                         
        ▀▀▀     {NC}"""

O_PROGRAMU = rf"""
Jednoduchá SPRÁVA BLOGU
  - Spuštění testovacího HUGO serveru http://10.0.0.119:1313
  - Zveřejnění změny na
      {RED}tyfoza.sytes.net{NC} ... rsync na ~\datatyf\web pro CADDY webserver
      {RED}tyfoza.github.io{NC} ... git na hlavní adresu blogu

celá struktura pro HUGO je uložená v adresáři ~\muj-blog

{GREEN}[7] Správa příspěvků{NC}
    {YELLOW}defaultně je nastavený editor 'code', lze přepnout na 'nano'{NC}

    Umožní vložit nový přípěvek a nastavit tagy a spustí editor
    Přepnout draft ke zveřejnění
    Editovat příspěvek

Menu řeší knihovna simple_term_menu
"""


ASCII_GIT = rf"""{CYAN}       ▀▀  ██
 ▄████ ██ ▀██▀▀
 ██ ██ ██  ██
 ▀████ ██▄ ██
    ██
  ▀▀▀{NC}
"""

ASCII_RSYNC = rf"""{CYAN} 
 ████▄ ▄█▀▀▀ ██ ██ ████▄ ▄████
 ██ ▀▀ ▀███▄ ██▄██ ██ ██ ██
 ██    ▄▄▄█▀  ▀██▀ ██ ██ ▀████
               ██
             ▀▀▀
{NC}
"""

ASCII_INFO = rf""" {CYAN}            ▄▄       
 ▀▀         ██        
 ██  ████▄ ▀██▀ ▄███▄ 
 ██  ██ ██  ██  ██ ██ 
 ██▄ ██ ██  ██  ▀███▀ {NC}
"""

ASCII_END = rf"""{CYAN}                                        
 ▄▄▄▄▄▄▄   ▄▄                          ▄▄ 
 ███▀▀███▄ ██                    ▀▀    ██ 
 ███▄▄███▀ ██ ▄███▄ ▄████ ██ ██  ██    ██ 
 ███  ███▄ ██ ██ ██ ██ ██ ██ ██ ▀██    ▀▀ 
 ████████▀ ██ ▀███▀ ▀████ ▀██▀█  ██    ██ 
                       ██        ██       
                     ▀▀▀       ▀▀▀        
"""


def clear_screen():
    if DEBUG == False :
        os.system("cls" if os.name == "nt" else "clear")


def get_base_url():
    """Přečte hugo.toml a vrátí (active_url, commented_urls_list)"""
    active_url = "Nenalezeno"
    commented_urls = []

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line_strip = line.strip()
                # Hledáme aktivní baseURL
                if line_strip.startswith("baseURL") and "=" in line_strip:
                    match = re.search(r'baseURL\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        active_url = match.group(1)
                # Hledáme zakomentované baseURL
                elif line_strip.startswith("#") and "baseURL" in line_strip:
                    match = re.search(r'#\s*baseURL\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        commented_urls.append(match.group(1))

    return active_url, commented_urls


def toggle_base_url():
    active_url, commented_urls = get_base_url()
    if not commented_urls:
        print(f"{RED}Nenalezena žádná zakomentovaná baseURL pro přepnutí!{NC}")
        return

    target_url = commented_urls[0]
    print(f"\nPřepínám baseURL z '{active_url}' na '{target_url}'...")

    new_lines = []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip.startswith("baseURL") and "=" in line_strip:
                new_lines.append(f'#baseURL = "{active_url}"\n')
            elif (
                line_strip.startswith("#")
                and "baseURL" in line_strip
                and target_url in line_strip
            ):
                new_lines.append(f'baseURL = "{target_url}"\n')
            else:
                new_lines.append(line)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"{GREEN}✔ baseURL úspěšně změněna v {CONFIG_FILE}!{NC}")


def set_custom_base_url(new_url):
    active_url, _ = get_base_url()
    if not new_url.endswith("/"):
        new_url += "/"

    new_lines = []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip.startswith("baseURL") and "=" in line_strip:
                new_lines.append(f'#baseURL = "{active_url}"\n')
                new_lines.append(f'baseURL = "{new_url}"\n')
            else:
                new_lines.append(line)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"{GREEN}✔ Nastavena nová baseURL: {new_url}{NC}")


def o_programu():
    clear_screen()
    print (ASCII_INFO)
    print (O_PROGRAMU)

def main():
    while True:
        clear_screen()
        print(ASCII_ART)

        active_url, commented_urls = get_base_url()
        print(f"  Aktuální baseURL: {GREEN}{BOLD}{active_url}{NC}")
        if commented_urls:
            print(f"  Zakomentovaná baseURL: {YELLOW}{commented_urls[0]}{NC}")
        print()

        options = [
            "[1] Build s drafty (není potřeba)",
            "[2] Build finální BEZ konceptů ",
            "[3] Spustit vývojový server v síti",
            "[4] Zveřejnění lokálně na tyfoza.sytes.net",
            "[5] Změnit / Přepnout baseURL v hugo.toml",
            "[6] Git commit na tyfoza.github.io",
            "[7] Správa příspěvků (Nové, Drafty, Editace)",
            "[9] O programu",
            "[0] Ukončit skript"
        ]

        menu = TerminalMenu(
            options,
            title="[ SPRÁVA BLOGU ] - Šipky a Enter nebo číslo pro výběr:",
            clear_screen=False
        )
        choice_idx = menu.show()

        if choice_idx == 0:  # [1]
            print(f"\n{CYAN}Spouštím testovací build s koncepty (-D)...{NC}")
            subprocess.run(["hugo", "--cleanDestinationDir", "-D"])
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 1:  # [2]
            print(f"\n{CYAN}Spouštím ostrý build BEZ konceptů...{NC}")
            subprocess.run(["hugo", "--cleanDestinationDir"])
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 2:  # [3]
            print(f"\n{CYAN}Spouštím vývojový server...{NC}")
            print(f"{YELLOW}Pro ukončení stiskněte CTRL+C{NC}\n")
            cmd = [
                "hugo",
                "server",
                "-D",
                "--bind",
                "0.0.0.0",
                "--baseURL",
                "http://10.0.0.119:1313",
            ]
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Server byl ukončen.{NC}")
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 3:  # [4]
            if active_url != ALLOWED_RSYNC_URL:
                print(f"\n{RED}CHYBA: Není nastavena správná baseURL pro rsync!{NC}")
                print(f"Aktuální baseURL: {BOLD}{active_url}{NC}")
                print(f"Požadovaná baseURL: {BOLD}{ALLOWED_RSYNC_URL}{NC}")
                print(f"{YELLOW}Nejprve změňte baseURL pomocí volby [5].{NC}")
            else:
                clear_screen()
                print(ASCII_RSYNC)
                confirm = input("\nChcete provést rsync na tyfoza.sytes.net? [a/n]: ").strip().lower()

                if confirm == "a":
                    print(f"\n{CYAN}Spouštím ostrý build BEZ konceptů...{NC}")
                    subprocess.run(["hugo", "--cleanDestinationDir"])
                    print(f"\n{CYAN}Spouštím rsync synchronizaci...{NC}")
                    cmd = [
                        "rsync",
                        "-a",
                        "-c",
                        "-h",
                        "--info=progress2",
                        "--delete",
                        "--no-o",
                        "--no-g",
                        '--exclude=~tyf',
                        PUBLIC_DIR,
                        WEB_TARGET_DIR,
                    ]
                    subprocess.run(cmd)
                else:
                    print(f"\n{YELLOW}Akce byla stornována. Žádné změny nebyly odeslány.{NC}")
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 4:  # [5]
            sub_options = []
            if commented_urls:
                sub_options.append(f"[1] Přepnout na zakomentovanou ({commented_urls[0]})")
            else:
                sub_options.append("[1] Přepnout na zakomentovanou (Není k dispozici)")
            sub_options.append("[2] Zadat vlastní baseURL")
            sub_options.append("[0] Zpět do hlavního menu")

            sub_menu = TerminalMenu(
                sub_options,
                title="[ ZMĚNA BASEURL - Vyberte akci ]:",
                clear_screen=False
            )
            sub_idx = sub_menu.show()

            if sub_idx == 0:
                if commented_urls:
                    toggle_base_url()
                else:
                    print(f"{RED}Nenalezena žádná zakomentovaná URL pro přepnutí.{NC}")
            elif sub_idx == 1:
                custom_url = input("\nZadejte novou baseURL (např. https://mujblog.cz/): ").strip()
                if custom_url:
                    set_custom_base_url(custom_url)
                else:
                    print(f"{RED}URL nebyla zadána.{NC}")
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 5:  # [6]
            if active_url != ALLOWED_GITHUB_URL:
                print(f"\n{RED}CHYBA: Není nastavena správná baseURL pro GitHub!{NC}")
                print(f"Aktuální baseURL: {BOLD}{active_url}{NC}")
                print(f"Požadovaná baseURL: {BOLD}{ALLOWED_GITHUB_URL}{NC}")
                print(f"{YELLOW}Nejprve změňte baseURL pomocí volby [5].{NC}")
            else:
                clear_screen()
                print(ASCII_GIT)
                print(f"{CYAN}=== ZVEŘEJNĚNÍ NA GITHUB ==={NC}\n")
                commit_msg = input("Zadejte popis změny (commit message):\n> ").strip()
                if not commit_msg:
                    commit_msg = "Aktualizace blogu"

                print(f"\nPřipraveno k vykonání:")
                print(f"  Zpráva commitu: {BOLD}{commit_msg}{NC}")
                print(f"  Postup: {YELLOW}git add . -> git commit -> git push{NC}")

                confirm = input("\nChcete provést celý proces zveřejnění? [a/n]: ").strip().lower()

                if confirm == "a":
                    print(f"\n{CYAN}Spouštím ostrý build BEZ konceptů...{NC}")
                    subprocess.run(["hugo", "--cleanDestinationDir"])

                    print(f"\n{YELLOW}[1/3] Spouštím git add...{NC}")
                    res_add = subprocess.run(["git", "add", "."])

                    if res_add.returncode == 0:
                        print(f"{YELLOW}[2/3] Spouštím git commit...{NC}")
                        res_commit = subprocess.run(["git", "commit", "-m", commit_msg])

                        if res_commit.returncode == 0:
                            print(f"{YELLOW}[3/3] Spouštím git push...{NC}")
                            res_push = subprocess.run(["git", "push"])

                            if res_push.returncode == 0:
                                print(f"\n{GREEN}✔ Zveřejnění na GitHub proběhlo úspěšně!{NC}")
                            else:
                                print(f"\n{RED}✘ Chyba při git push!{NC}")
                        else:
                            print(f"\n{RED}✘ Chyba při git commit!{NC}")
                    else:
                        print(f"\n{RED}✘ Chyba při git add!{NC}")
                else:
                    print(f"\n{YELLOW}Akce byla stornována. Nic nebylo přidáno ani odesláno na GitHub.{NC}")

            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 6:  # [7]
            print(f"\n{CYAN}Spouštím správce příspěvků...{NC}")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            prispevky_script = os.path.join(script_dir, "blog_prispevky.py")
            subprocess.run([sys.executable, prispevky_script])

        elif choice_idx == 7:  # [9]
            o_programu()
            input("\nStiskni Enter pro pokračování...")

        elif choice_idx == 8 or choice_idx is None:  # [0] nebo ESC
            clear_screen()
            print(ASCII_END)
            #print(f"\n{CYAN}Bloguj!{NC}")
            sys.exit(0)


if __name__ == "__main__":
    main()


