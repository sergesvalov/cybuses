import urllib.request
import io
import pdfplumber

url = "https://limassolairportexpress.eu/wp-content/uploads/2025/11/Paphos-Itinerary-01-12-2025.pdf"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        pdf_bytes = response.read()

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words()
            words.sort(key=lambda w: (w['top'], w['x0']))
            lines = []
            for w in words:
                if lines and abs(lines[-1]['top'] - w['top']) <= 5:
                    lines[-1]['text'] += " " + w['text']
                else:
                    lines.append({'top': w['top'], 'text': w['text']})
            print(f"--- PAGE {i} ---")
            for line in lines[:20]:  # print first 20 lines
                print(line['text'])
except Exception as e:
    print(e)
