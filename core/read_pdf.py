from pypdf import PdfReader
import re

reader = PdfReader('jaarrekening-profinance.pdf')

print(len(reader.pages))

page = reader.pages[1]

text = page.extract_text()

general_pattern = re.compile(
    r"(?P<block>(?:.*?\n)*?.*?Begin van het mandaat : \d{4}-\d{2}-\d{2}.*?\s+(?:Bestuurder|Voorzitter|Gedelegeerd bestuurder).*)",
    re.MULTILINE)

matches = general_pattern.findall(text)

for match in matches:
    first_line = match.strip().split('\n')[0].strip()
    print(first_line)
