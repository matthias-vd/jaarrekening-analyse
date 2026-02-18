import csv
from StructuurBalans import structuurBalans
from StructuurMetadata import structuurMetadata
from StructuurSocialeBalans import structuurSocialeBalans
from StructuurResultatenRekening import structuurResultatenRekening
from StructuurToelichting import structuurToelichting

code_to_name = {}

for item in structuurBalans:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")
for item in structuurMetadata:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")
for item in structuurSocialeBalans:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")
for item in structuurResultatenRekening:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")
for item in structuurToelichting:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")



with open("soubry_jaarrekening.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        # sla lege rijen of rijen zonder data over
        if not row or len(row) < 2:
            continue

        key, value = row[0], row[1]

        key = key.strip('"')
        value = value.strip('"')

        name = code_to_name.get(key, key)

        # print met code
        #print(f"{key} - {name} - {value}")
        # print zonder code
        print(f"{name} - {value}")

