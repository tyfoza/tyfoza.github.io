#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime
import unicodedata
import re

# Pokus o import interaktivního menu
try:
    from simple_term_menu import TerminalMenu
except ImportError:
    print("\033[1;31mChyba: Chybí knihovna 'simple-term-menu'.\033[0m")
    print("Pro navigaci šipkami si ji prosím nainstaluj příkazem:")
    print("\033[1;33mpython3 -m pip install simple-term-menu\033[0m")
    sys.exit(1)

# --- KONFIGURACE ---
CONTENT_DIR = "content/posts"
CURRENT_EDITOR = "code"

# ANSI barvy
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
BOLD = "\033[1m"
NC = "\033[0m"

ASCII_ART = rf"""{YELLOW}
    ____  __               ____  __      __   _ __       
   / __ )/ /___  ____ _   / __ \/ /___  / /__(_) /___  __
  / __  / / __ \/ __ `/  / /_/ / / __ \/ //_/ / // _ \/ /
 / /_/ / / /_/ / /_/ /  / _, _/ / /_/ / ,< / / //  __/_/ 
/_____/_/\____/\__, /  /_/ |_/_/\____/_/|_/_/_/ \___(_)  
              /____/                                     
{NC}"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_title(title):
    """Odstraní diakritiku, převede na malá písmena a nahradí mezery pomlčkami."""
    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('utf-8')
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

def add_new_post(editor):
    clear_screen()
    print(f"{CYAN}--- NOVÝ PŘÍSPĚVEK ---{NC}\n")
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    
    print(f"Aktuální datum zjištěno na: {BOLD}{year}/{month}{NC}")
    confirm_date = input("Chceš použít tento rok a měsíc? [a/n]: ").strip().lower()
    
    if confirm_date != 'a':
        year = input("Zadej rok (např. 2026): ").strip()
        month = input("Zadej měsíc (např. 08): ").strip()
        if len(month) == 1:
            month = f"0{month}"

    title = input(f"\nZadej název příspěvku česky (např. Výlet na Čachtice):\n> ")
    if not title:
        print(f"{RED}Název nesmí být prázdný. Zrušeno.{NC}")
        return

    slug = sanitize_title(title)
    post_path = f"posts/{year}/{month}/{slug}/index.md"
    
    print(f"\n{YELLOW}Připraven vykonat příkaz:{NC}")
    print(f"hugo new {post_path}")
    
    execute = input("\nVytvořit tento příspěvek? [a/n]: ").strip().lower()
    if execute == 'a':
        res = subprocess.run(["hugo", "new", post_path])
        if res.returncode == 0:
            print(f"\n{GREEN}✔ Příspěvek '{title}' byl úspěšně vytvořen!{NC}")
            open_editor = input(f"Otevřít příspěvek v editoru {BOLD}{editor}{NC}? [a/n]: ").strip().lower()
            if open_editor == 'a':
                full_path = os.path.join("content", post_path)
                subprocess.run([editor, full_path])
        else:
            print(f"\n{RED}✘ Vyskytla se chyba při vytváření příspěvku.{NC}")
    else:
        print(f"\n{YELLOW}Akce byla zrušena.{NC}")

def get_all_posts():
    """Projde složku obsahu a vrátí datovou strukturu o všech index.md."""
    posts = []
    if not os.path.exists(CONTENT_DIR):
        return posts
        
    for root, dirs, files in os.walk(CONTENT_DIR):
        if "index.md" in files:
            path = os.path.join(root, "index.md")
            
            # Zjištění draftu
            is_draft = False
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "draft: true" in content or "draft: true" in content.lower():
                    is_draft = True
            
            rel_path = path.replace(CONTENT_DIR + "/", "").replace("\\", "/").replace("/index.md", "")
            parts = rel_path.split("/")
            
            if len(parts) >= 3:
                year, month, slug = parts[0], parts[1], parts[-1]
            else:
                year = parts[0] if len(parts) > 0 else "Neznámý"
                month = parts[1] if len(parts) > 1 else "Neznámý"
                slug = parts[-1] if len(parts) > 0 else "Neznámý"

            posts.append({
                'path': path,
                'is_draft': is_draft,
                'year': year,
                'month': month,
                'slug': slug,
                'display': rel_path
            })
    return posts

def manage_drafts():
    all_posts = get_all_posts()
    drafts = [p for p in all_posts if p['is_draft']]
    
    if not drafts:
        clear_screen()
        print(f"\n{GREEN}Žádné rozepsané koncepty nenalezeny! Vše je publikováno.{NC}\n")
        return
        
    options = [f"{d['year']}/{d['month']} - {d['slug']}" for d in drafts]
    options.append("[Zpět]")
    
    menu = TerminalMenu(options, title="[Vyber šipkami draft k publikování a stiskni Enter]")
    idx = menu.show()
    
    if idx is None or idx == len(drafts):
        return
        
    selected = drafts[idx]['path']
    clear_screen()
    print(f"Vybrán: {selected}")
    confirm = input("Opravdu změnit na publikovaný (draft: false)? [a/n]: ").strip().lower()
    if confirm == 'a':
        with open(selected, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'draft:\s*true', 'draft: false', content, flags=re.IGNORECASE)
        
        with open(selected, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{GREEN}✔ Příspěvek byl publikován!{NC}")
    else:
        print(f"{YELLOW}Zrušeno.{NC}")

def manage_all_posts(editor):
    """Hierarchická navigace adresářem s automatickým rozbalením nejnovějšího roku a měsíce."""
    posts = get_all_posts()
    if not posts:
        clear_screen()
        print(f"{RED}Nenalezeny žádné příspěvky!{NC}")
        return

    years = sorted(list(set(p['year'] for p in posts)), reverse=True)
    if not years:
        return

    # Příznak pro první otevření - přeskočí ruční výběr a rozbalí nejnovější rok/měsíc
    first_run = True

    while True:
        clear_screen()
        if first_run:
            selected_year = years[0]
        else:
            year_menu = TerminalMenu(years + ["[Zpět do hlavního menu]"], title="[1/3] Vyber ROK úprav (šipky nahoru/dolů):")
            y_idx = year_menu.show()
            
            if y_idx is None or y_idx == len(years):
                break  # Vracíme se do hlavního menu
            selected_year = years[y_idx]

        while True:
            clear_screen()
            months = sorted(list(set(p['month'] for p in posts if p['year'] == selected_year)), reverse=True)
            
            if first_run:
                selected_month = months[0] if months else None
                first_run = False  # První běh dokončen, další navigace již bude manuální
            else:
                month_menu = TerminalMenu(months + ["[Zpět na výběr roku]"], title=f"[2/3] Vyber MĚSÍC v roce {selected_year}:")
                m_idx = month_menu.show()
                
                if m_idx is None or m_idx == len(months):
                    break  # Vracíme se k výběru roku
                selected_month = months[m_idx]

            if not selected_month:
                break

            while True:
                clear_screen()
                filtered = [p for p in posts if p['year'] == selected_year and p['month'] == selected_month]
                filtered.sort(key=lambda x: x['path'], reverse=True)

                options = []
                for p in filtered:
                    status = "[DRAFT]" if p['is_draft'] else "[ONLINE]"
                    options.append(f"{status} {p['slug']}")

                post_menu = TerminalMenu(
                    options + ["[Zpět na výběr měsíce]"], 
                    title=f"[3/3] Články pro {selected_year}/{selected_month} (Stiskni Enter pro spuštění v {editor}, '/' pro hledání):"
                )
                p_idx = post_menu.show()

                if p_idx is None or p_idx == len(filtered):
                    break  # Vracíme se k výběru měsíce

                selected_post = filtered[p_idx]['path']
                clear_screen()
                print(f"\n{CYAN}Otevírám {selected_post} v editoru {editor}...{NC}")
                subprocess.run([editor, selected_post])
                
                # Znovu načteme příspěvky pro případ, že došlo k úpravám
                posts = get_all_posts()

def main():
    global CURRENT_EDITOR
    while True:
        clear_screen()
        print(ASCII_ART)
        
        options = [
            "[1] Nový příspěvek",
            "[2] Seznam draft příspěvků (publikace)",
            "[3] Správa příspěvků (Adresářová navigace: Rok -> Měsíc -> Článek)",
            f"[9] Přepnout editor (Nyní aktivní: {CURRENT_EDITOR})",
            "[0] Zpět do hlavního menu (blog.py)"
        ]
        
        menu = TerminalMenu(options, title="[ REDAKČNÍ SYSTÉM ] - Vyber šipkami a potvrď Enterem:", clear_screen=False)
        choice_idx = menu.show()

        if choice_idx == 0:
            add_new_post(CURRENT_EDITOR)
            input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 1:
            manage_drafts()
            input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 2:
            manage_all_posts(CURRENT_EDITOR)
        elif choice_idx == 3:
            CURRENT_EDITOR = "nano" if CURRENT_EDITOR == "code" else "code"
            print(f"\n{YELLOW}Editor úspěšně změněn na: {CURRENT_EDITOR}{NC}")
            input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 4 or choice_idx is None:
            print(f"\n{CYAN}Návrat do hlavního menu...{NC}")
            break

if __name__ == "__main__":
    if not os.path.exists("content"):
        print(f"{RED}Chyba: Složka 'content' nenalezena. Spouštíš skript ze složky blogu?{NC}")
        sys.exit(1)
    main()


