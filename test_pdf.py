import pprint
import io
with open('paphos.pdf', 'rb') as f:
    pdf_bytes = f.read()

from parsers.shuttle import ShuttleParser
parser = ShuttleParser()

info = {'name': 'Limassol Express', 'provider': 'shuttle'}
results = parser.extract_limassol_express_logic(pdf_bytes, 'http://test', info)
# Print just the types and descs
for r in results:
    print(f"[{r['type']}] {r['desc']}: {len(r['times'])} times")
