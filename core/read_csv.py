import csv
from StructuurBalans import balansNaWinstverdeling

code_to_name = {}
for item in balansNaWinstverdeling:
    code = item.get("Code")
    if code:
        code_to_name[code] = item.get("Rubriek", "")

with open("jaarrekening.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        # sla lege rijen of rijen zonder data over
        if not row or len(row) < 2:
            continue

        key, value = row[0], row[1]

        key = key.strip('"')
        value = value.strip('"')

        name = code_to_name.get(key, key)

        print(f"{key} - {name} - {value}")
