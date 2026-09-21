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

DEBUG = False

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

ASCII_ART = rf"""{CYAN}
 ▄▄▄▄▄▄▄                                 ▄▄    ▄▄
█████▀▀▀                                 ██    ██
 ▀████▄  ████▄ ████▄  ▀▀█▄ ██ ██  ▀▀█▄   ████▄ ██ ▄███▄ ▄████ ██ ██
   ▀████ ██ ██ ██ ▀▀ ▄█▀██ ██▄██ ▄█▀██   ██ ██ ██ ██ ██ ██ ██ ██ ██
███████▀ ████▀ ██    ▀█▄██  ▀█▀  ▀█▄██   ████▀ ██ ▀███▀ ▀████ ▀██▀█
         ██                                                ██
         ▀▀                                              ▀▀▀
{NC}"""

ASCII_NOVY = rf"""{CYAN}
████▄ ▄███▄ ██ ██ ██ ██ 
██ ██ ██ ██ ██▄██ ██▄██ 
██ ██ ▀███▀  ▀█▀   ▀██▀ 
                    ██  
                  ▀▀▀   {NC}
"""

def clear_screen():
    if DEBUG == False :
        os.system('cls' if os.name == 'nt' else 'clear')

def remove_accents(input_str):
    """Odstraní diakritiku pro potřeby správného abecedního řazení."""
    return unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')

def sanitize_title(title):
    """Odstraní diakritiku, převede na malá písmena a nahradí mezery pomlčkami pro URL."""
    slug = remove_accents(title).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

def safe_input(prompt=""):
    """Bezpečné načtení vstupu, které odolá poškozeným znakům v bufferu terminálu."""
    while True:
        try:
            return input(prompt)
        except UnicodeDecodeError:
            pass
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Přerušeno uživatelem.{NC}")
            sys.exit(0)

def get_yes_no(prompt, default_yes=False):
    """Pomocná funkce pro blbuvzdorné a bezpečné [a/n] potvrzování."""
    hint = "[A/n]" if default_yes else "[a/N]"
    while True:
        ans = safe_input(f"{prompt} {hint}: ").strip().lower()
        if not ans:
            return default_yes
        if ans in ['a', 'ano', 'y', 'yes']:
            return True
        if ans in ['n', 'ne', 'no']:
            return False
        print(f"{RED}Neplatný vstup. Zadej 'a' pro ano, nebo 'n' pro ne.{NC}")

def extract_existing_tags():
    """Projít celý blog a vrátit unikátní abecedně seřazený seznam všech tagů."""
    tags = set()
    if not os.path.exists(CONTENT_DIR):
        return []
        
    for root, dirs, files in os.walk(CONTENT_DIR):
        if "index.md" in files:
            with open(os.path.join(root, "index.md"), 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Zkusíme najít zápis typu `tags: ["tag1", "tag2"]`
                match_inline = re.search(r'^tags:\s*\[(.*?)\]', content, re.MULTILINE)
                if match_inline:
                    inner_text = match_inline.group(1)
                    # Rozsekáme podle uvozovek
                    found = re.findall(r'["\']([^"\']+)["\']', inner_text)
                    for t in found:
                        tags.add(t.strip())
                else:
                    # Případně odchytíme YAML seznam odrážek (volitelně)
                    match_multiline = re.search(r'^tags:\s*\n((?:\s+-\s+.*\n?)+)', content, re.MULTILINE)
                    if match_multiline:
                        inner_lines = match_multiline.group(1)
                        for line in inner_lines.split('\n'):
                            t = re.sub(r'^\s*-\s*', '', line).strip()
                            t = re.sub(r'^["\']|["\']$', '', t)
                            if t:
                                tags.add(t)

    # Vrátí seřazené pole (řadíme bez diakritiky přes NFKD, aby 'č' bylo za 'c')
    return sorted(list(tags), key=lambda x: remove_accents(x).lower())

def update_frontmatter(full_path, original_title, selected_tags):
    """Opraví název a aplikuje vybrané tagy do hlavičky nového index.md."""
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        escaped_title = original_title.replace('"', '\\"')
        
        # 1. Oprava Title
        def repl_title(match):
            sep = match.group(1)
            return f'title{sep} "{escaped_title}"'
        content = re.sub(r'^title\s*([:=])\s*.*$', repl_title, content, flags=re.MULTILINE)

        # 2. Úprava Tagů
        tags_str = "[" + ", ".join([f'"{t}"' for t in selected_tags]) + "]"
        
        # Pokud šablona vygenerovala "tags: cokoliv", nahradíme to naším stringem
        if re.search(r'^tags\s*[:=]', content, flags=re.MULTILINE):
            content = re.sub(r'^tags\s*[:=].*$', f'tags: {tags_str}', content, flags=re.MULTILINE)
        else:
            # Pokud tagy z nějakého důvodu chybí úplně, vložíme je hned pod název článku
            def insert_tags(m):
                return m.group(1) + f'\ntags: {tags_str}'
            content = re.sub(r'^(title\s*[:=]\s*.*)$', insert_tags, content, flags=re.MULTILINE)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

def add_new_post(editor):
    clear_screen()
    print(ASCII_NOVY)
    print(f"{CYAN}--- NOVÝ PŘÍSPĚVEK ---{NC}\n")
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    
    print(f"Aktuální datum zjištěno na: {BOLD}{year}/{month}{NC}")
    
    if not get_yes_no("Chceš použít tento rok a měsíc?", default_yes=True):
        year = safe_input("Zadej rok (např. 2026): ").strip()
        month = safe_input("Zadej měsíc (např. 08): ").strip()
        if len(month) == 1:
            month = f"0{month}"

    while True:
        title = safe_input(f"\nZadej název příspěvku česky (např. Výlet na Čachtice):\n> ").strip()
        if title:
            break
        print(f"{RED}Název nesmí být prázdný. Zkus to znovu.{NC}")

    slug = sanitize_title(title)
    post_path = f"posts/{year}/{month}/{slug}/index.md"
    
    # --- Interaktivní výběr TAGŮ ---
    print(f"\n{CYAN}[Načítám existující tagy z blogu...]{NC}")
    existing_tags = extract_existing_tags()
    
    options = ["[+] Přidat úplně nový tag..."] + existing_tags
    menu = TerminalMenu(
        options,
        title="Vyber tagy (Mezerník = označit/odznačit, Enter = potvrdit výběr, '/' = hledat):",
        multi_select=True,
        show_multi_select_hint=True,
        clear_screen=False
    )
    
    print(f"\n{YELLOW}Otevírám nabídku tagů...{NC}")
    selected_idx = menu.show()
    
    final_tags = []
    if selected_idx is not None:
        for idx in selected_idx:
            if idx == 0:
                # Uživatel zaklikl volbu "Nový tag"
                new_t = safe_input(f"\n{YELLOW}Zadej nové tagy (pokud je jich víc, odděl je čárkou):{NC}\n> ")
                if new_t.strip():
                    # Umožní zadat více tagů naráz ("výlet, hory, slovensko")
                    for t in new_t.split(","):
                        cleaned = t.strip()
                        if cleaned:
                            final_tags.append(cleaned)
            else:
                final_tags.append(options[idx])
                
    # Unikátní tagy (kdyby se duplikovaly z nového i existujícího výběru)
    final_tags = list(dict.fromkeys(final_tags))
    
    print(f"\n{YELLOW}Připraven vykonat příkaz:{NC}")
    print(f"hugo new {post_path}")
    print(f"Název v článku bude: {BOLD}{title}{NC}")
    print(f"Cesta/URL bude:      {BOLD}{post_path}{NC}")
    print(f"Vybrané tagy:        {BOLD}{', '.join(final_tags) if final_tags else '(žádné)'}{NC}")
    
    if get_yes_no("\nVytvořit tento příspěvek?", default_yes=True):
        res = subprocess.run(["hugo", "new", post_path])
        if res.returncode == 0:
            full_path = os.path.join("content", post_path)
            
            # Automatická oprava názvu a vložení TAGŮ do hlavičky
            update_frontmatter(full_path, title, final_tags)
            
            print(f"\n{GREEN}✔ Příspěvek '{title}' byl úspěšně vytvořen!{NC}")
            if get_yes_no(f"Otevřít příspěvek v editoru {BOLD}{editor}{NC}?", default_yes=True):
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
    
    if get_yes_no("Opravdu změnit na publikovaný (draft: false)?", default_yes=True):
        with open(selected, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'draft:\s*true', 'draft: false', content, flags=re.IGNORECASE)
        
        with open(selected, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{GREEN}✔ Příspěvek byl publikován!{NC}")
    else:
        print(f"{YELLOW}Zrušeno.{NC}")

def manage_all_posts(editor):
    posts = get_all_posts()
    if not posts:
        clear_screen()
        print(f"{RED}Nenalezeny žádné příspěvky!{NC}")
        return

    years = sorted(list(set(p['year'] for p in posts)), reverse=True)
    if not years:
        return

    first_run = True

    while True:
        clear_screen()
        if first_run:
            selected_year = years[0]
        else:
            year_menu = TerminalMenu(years + ["[Zpět do hlavního menu]"], title="[1/3] Vyber ROK úprav (šipky nahoru/dolů):")
            y_idx = year_menu.show()
            
            if y_idx is None or y_idx == len(years):
                break
            selected_year = years[y_idx]

        while True:
            clear_screen()
            months = sorted(list(set(p['month'] for p in posts if p['year'] == selected_year)), reverse=True)
            
            if first_run:
                selected_month = months[0] if months else None
                first_run = False
            else:
                month_menu = TerminalMenu(months + ["[Zpět na výběr roku]"], title=f"[2/3] Vyber MĚSÍC v roce {selected_year}:")
                m_idx = month_menu.show()
                
                if m_idx is None or m_idx == len(months):
                    break
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
                    break

                selected_post = filtered[p_idx]['path']
                clear_screen()
                print(f"\n{CYAN}Otevírám {selected_post} v editoru {editor}...{NC}")
                subprocess.run([editor, selected_post])
                
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
        
        menu = TerminalMenu(options, title="[ Trapný REDAKČNÍ SYSTÉM ] - Šipky a Enter nebo číslo:", clear_screen=False)
        choice_idx = menu.show()

        if choice_idx == 0:
            add_new_post(CURRENT_EDITOR)
            safe_input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 1:
            manage_drafts()
            safe_input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 2:
            manage_all_posts(CURRENT_EDITOR)
        elif choice_idx == 3:
            CURRENT_EDITOR = "nano" if CURRENT_EDITOR == "code" else "code"
            print(f"\n{YELLOW}Editor úspěšně změněn na: {CURRENT_EDITOR}{NC}")
            safe_input("\nStiskni Enter pro pokračování...")
        elif choice_idx == 4 or choice_idx is None:
            print(f"\n{CYAN}Návrat do hlavního menu...{NC}")
            break

if __name__ == "__main__":
    if not os.path.exists("content"):
        print(f"{RED}Chyba: Složka 'content' nenalezena. Spouštíš skript ze složky blogu?{NC}")
        sys.exit(1)
    main()

