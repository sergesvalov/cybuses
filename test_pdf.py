import aiohttp
import asyncio
import pdfplumber
import io

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

async def fetch_and_print():
    url = "https://limassolairportexpress.eu/wp-content/uploads/2025/11/Paphos-Itinerary-01-12-2025.pdf"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, ssl=False, timeout=30) as r:
            pdf_bytes = await r.read()

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- PAGE {i} ---")
            text = page.extract_text()
            print(text[:1000])

            print(f"--- PAGE {i} extracted words ---")
            words = page.extract_words()
            # print first 50 words to see bounding boxes
            for w in words[:20]:
                print(w['text'], w['x0'])

if __name__ == "__main__":
    asyncio.run(fetch_and_print())
