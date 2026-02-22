from bs4 import BeautifulSoup

html = """
<h3>Paphos - Larnaca, Ayia Napa & Paralimni</h3>
06:00, 08:30, 10:00*
<h3>Larnaca - Paphos</h3>
09:12, 10:45**, 12:00
"""
soup = BeautifulSoup(html, 'html.parser')

target = 'larnaca'
current_dir = None

print("START PARSING")
for tag in soup.find_all(['h3', 'p', 'text']):
    txt = tag.get_text(' ', strip=True).lower()
    norm_txt = txt.replace('–', '-').replace('—', '-')
    print(f"Checking tag text: '{norm_txt}'")
    
    is_from_paphos = (
        "from paphos" in norm_txt or "from pafos" in norm_txt or 
        f"paphos - {target}" in norm_txt or f"pafos - {target}" in norm_txt or
        f"paphos-{target}" in norm_txt or
        (target == "larnaca" and "paphos - larnaca" in norm_txt)
    )
    is_to_paphos = (
        f"from {target}" in norm_txt or 
        f"{target} - paphos" in norm_txt or f"{target} - pafos" in norm_txt or
        f"{target}-paphos" in norm_txt or
        (target == "larnaca" and "larnaca - paphos" in norm_txt)
    )
    
    print(f"  -> is_from_paphos: {is_from_paphos}, is_to_paphos: {is_to_paphos}")
    
    if is_from_paphos and not is_to_paphos:
        current_dir = 'from_paphos'
        print(f"  -> SWITCHED DIR TO: {current_dir}")
        continue
    if is_to_paphos and not is_from_paphos:
        current_dir = 'to_paphos'
        print(f"  -> SWITCHED DIR TO: {current_dir}")
        continue
    if current_dir:
        print(f"  -> WOULD EXTRACT TIMES FOR: {current_dir}")

print("DONE")
