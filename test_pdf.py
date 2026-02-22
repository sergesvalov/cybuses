import urllib.request, pdfplumber, io
import pprint

url = 'https://limassolairportexpress.eu/wp-content/uploads/2026/01/Paphos-Itinerary-01-02-2026.pdf'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
pdf_bytes = urllib.request.urlopen(req).read()

schedule = {
    "weekday": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []},
    "weekend": {"Limassol ➝ Airport": [], "Airport ➝ Limassol": []}
}

with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue
        
        times_row = table[-1]
        if len(times_row) < 14:
            continue
        
        for day_idx in range(7):
            day_type = "weekend" if day_idx >= 5 else "weekday"
            
            limassol_col = day_idx * 2
            airport_col = limassol_col + 1
            
            if times_row[limassol_col]:
                schedule[day_type]["Limassol ➝ Airport"].extend(times_row[limassol_col].split('\n'))
            
            if times_row[airport_col]:
                schedule[day_type]["Airport ➝ Limassol"].extend(times_row[airport_col].split('\n'))

pprint.pprint(schedule)
