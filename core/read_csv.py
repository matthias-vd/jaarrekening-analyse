import csv
import os

bestand = "jaarrekening_profinance.csv"

if __name__ == '__main__':
    from StructuurBalans import structuurBalans
    from StructuurMetadata import structuurMetadata
    from StructuurSocialeBalans import structuurSocialeBalans
    from StructuurResultatenRekening import structuurResultatenRekening
    from StructuurToelichting import structuurToelichting
else:
    from core.StructuurBalans import structuurBalans
    from core.StructuurMetadata import structuurMetadata
    from core.StructuurResultatenRekening import structuurResultatenRekening
    from core.StructuurSocialeBalans import structuurSocialeBalans
    from core.StructuurToelichting import structuurToelichting


def read_csv():
    def flatten(nested):
        flat = []
        for item in nested:
            if isinstance(item, list):
                flat.extend(flatten(item))
            else:
                flat.append(item)
        return flat

    flattened = flatten([structuurBalans, structuurMetadata, structuurSocialeBalans, structuurResultatenRekening, structuurToelichting])

    code_to_name = {}

    for item in flattened:
        code = item.get("Code")
        if code:
            code_to_name[code] = item.get("Rubriek", "")

    uitgelezenData = []
    if __name__ == "__main__":
        file = bestand
    else:
        cur_path = os.path.dirname(__file__)
        target = fr'../uploads/{bestand}'
        file = os.path.normpath(os.path.join(cur_path, target))

    with open(file, newline="", encoding="utf-8") as f:
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
            #print(f"{name} - {value}")

            elementUitgelezen = [key,value]

            uitgelezenData.append(elementUitgelezen)

    return uitgelezenData