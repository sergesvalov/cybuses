import asyncio
import aiohttp
from parsers.intercity import IntercityParser
from config import ROUTES

class DebugParser(IntercityParser):
    async def parse(self, session, info):
        results = []
        soup = await self.get_soup(session, info['url'])
        if not soup: return []
        
        footnotes_map = self.extract_footnotes(soup)
        city1 = info.get('city1', 'paphos')
        city2 = info.get('city2', '')
        blocks = { "dir1": {"daily": [], "weekday": [], "weekend": []}, "dir2": {"daily": [], "weekday": [], "weekend": []} }
        current_dir = None
        current_type = "daily"
        
        tags = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p', 'td', 'span', 'li', 'div'])
        print(f"Total tags: {len(tags)}")
        for tag in tags:
            if tag.name == 'div' and tag.find(['div', 'p', 'table', 'ul', 'h2', 'h3']):
                continue

            txt = tag.get_text(" ", strip=True).lower()
            norm_txt = txt.replace("–", "-").replace("—", "-")
            
            def check_match(source, dest, text):
                s_opts = ["paphos", "pafos"] if source == "paphos" else [source]
                d_opts = ["paphos", "pafos"] if dest == "paphos" else [dest]
                for s in s_opts:
                    if f"from {s}" in text: return True
                    for d in d_opts:
                        if f"{s} - {d}" in text or f"{s}-{d}" in text: return True
                return False

            is_dir1 = check_match(city1, city2, norm_txt)
            is_dir2 = check_match(city2, city1, norm_txt)

            if is_dir1 and not is_dir2 and len(txt) < 100:
                print(f"Found DIR1: {txt}")
                current_dir = "dir1"
                current_type = "daily"
                continue
            if is_dir2 and not is_dir1 and len(txt) < 100:
                print(f"Found DIR2: {txt}")
                current_dir = "dir2"
                current_type = "daily"
                continue
            
            if len(norm_txt) < 100:
                if "monday" in norm_txt and "sunday" in norm_txt:
                    current_type = "daily"
                elif "monday" in norm_txt and "friday" in norm_txt:
                    current_type = "weekday"
                    print(f"Found WEEKDAY: {txt}")
                elif "saturday" in norm_txt or "sunday" in norm_txt or "public holiday" in norm_txt:
                    current_type = "weekend"
                    print(f"Found WEEKEND: {txt}")
                elif "daily" in norm_txt:
                    current_type = "daily"
                    print(f"Found DAILY: {txt}")
            
            if current_dir:
                raw = self.extract_times(tag.get_text(" ", strip=True))
                if len(raw) >= 1:
                    print(f"Extracted {len(raw)} times for {current_dir} {current_type}")
                    blocks[current_dir][current_type].append(raw)
        return blocks

async def main():
    parser = DebugParser()
    info = ROUTES['nicosia']
    async with aiohttp.ClientSession() as session:
        res = await parser.parse(session, info)
        if isinstance(res, list):
            print("Returned LIST. soup was probably None.", res)
        else:
            print("Final Blocks:", {k: {t: len(v) for t, v in res[k].items()} for k in res})

if __name__ == "__main__":
    asyncio.run(main())
