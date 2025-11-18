#!/usr/bin/env python3
"""
XBRL Analyzer voor Belgische jaarrekeningen
============================================

Dit script analyseert XBRL bestanden van de Nationale Bank van België (NBB)
en extraheert belangrijke informatie zoals:
- Bedrijfsgegevens (naam, ondernemingsnummer, adressen)
- Bestuurders en hun functies
- Aandeelhouders en hun deelnemingen
- Financiële cijfers

Gebruik:
    python xbrl_analyzer.py jaarrekening.xbrl

Auteur: Gegeneerd door AI Assistant
Datum: November 2025
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
import sys


def analyze_xbrl(filename):
    """
    Analyseert een XBRL bestand en extraheert belangrijke informatie.

    Args:
        filename (str): Pad naar het XBRL bestand

    Returns:
        dict: Dictionary met geëxtraheerde informatie:
            - bedrijfsgegevens: Naam, ondernemingsnummer, adressen, datums
            - bestuurders: Lijst met bestuurders en hun functies
            - aandeelhouders: Lijst met aandeelhouders en deelnemingen
            - financiele_cijfers: Financiële data uit de jaarrekening
    """

    # Parse het XBRL bestand
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception as e:
        print(f"Fout bij het inlezen van het bestand: {e}")
        return None

    # Verzamel alle contexten met hun dimensies
    contexts = {}
    for context in root.findall('.//{http://www.xbrl.org/2003/instance}context'):
        context_id = context.get('id')

        # Extract identifier (ondernemingsnummer)
        identifier = context.find('.//{http://www.xbrl.org/2003/instance}identifier')

        # Extract period informatie
        instant = context.find('.//{http://www.xbrl.org/2003/instance}instant')
        start_date = context.find('.//{http://www.xbrl.org/2003/instance}startDate')
        end_date = context.find('.//{http://www.xbrl.org/2003/instance}endDate')

        # Extract dimensions (gebruikt in NBB XBRL taxonomie)
        dimensions = {}
        members = context.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember')
        for member in members:
            dim = member.get('dimension', '').split(':')[-1]
            dimensions[dim] = member.text

        contexts[context_id] = {
            'identifier': identifier.text if identifier is not None else None,
            'instant': instant.text if instant is not None else None,
            'start_date': start_date.text if start_date is not None else None,
            'end_date': end_date.text if end_date is not None else None,
            'dimensions': dimensions
        }

    # Verzamel alle data elementen gegroepeerd per context
    context_data = defaultdict(dict)

    for elem in root:
        # Skip context, unit en schemaRef elementen
        if 'context' not in elem.tag and 'unit' not in elem.tag and 'schemaRef' not in elem.tag:
            context_ref = elem.get('contextRef', '')

            # Extract tag naam zonder namespace
            tag_name = elem.tag.split('}')[1] if '}' in elem.tag else elem.tag
            namespace = elem.tag.split('}')[0].replace('{', '').split('/')[-1] if '}' in elem.tag else ''

            full_tag = f"{namespace}:{tag_name}" if namespace else tag_name

            # Bewaar de waarde
            if elem.text:
                context_data[context_ref][full_tag] = elem.text.strip()

    # Initialiseer resultaat dictionary
    result = {
        'bedrijfsgegevens': {},
        'bestuurders': [],
        'aandeelhouders': [],
        'financiele_cijfers': {},
    }

    # === EXTRACT BEDRIJFSGEGEVENS ===
    # Zoek hoofdonderneming (psn:m1 is de onderneming zelf in NBB taxonomie)
    for ctx_id, ctx_info in contexts.items():
        dims = ctx_info['dimensions']
        data = context_data[ctx_id]

        if dims.get('psn') == 'psn:m1':
            # Ondernemingsnummer
            if 'met:str2' in data and data['met:str2'].isdigit() and len(data['met:str2']) == 10:
                result['bedrijfsgegevens']['ondernemingsnummer'] = data['met:str2']

            # Bedrijfsnaam
            elif 'met:str2' in data and not data['met:str2'].isdigit():
                if 'naam' not in result['bedrijfsgegevens']:
                    result['bedrijfsgegevens']['naam'] = data['met:str2']

            # Rechtsvorm
            if 'lgf-enum:list2' in data or 'lgf-enum:list1' in data:
                lgf = data.get('lgf-enum:list2', data.get('lgf-enum:list1', ''))
                result['bedrijfsgegevens']['rechtsvorm_code'] = lgf.replace('lgf:m', '')

        # Datums
        if 'met:dte1' in data:
            dims = ctx_info['dimensions']
            if dims.get('evt') == 'evt:m1':
                result['bedrijfsgegevens']['datum_algemene_vergadering'] = data['met:dte1']
            elif dims.get('evt') == 'evt:m2':
                result['bedrijfsgegevens']['datum_afsluiting_boekjaar'] = data['met:dte1']
            elif dims.get('mmt') == 'mmt:m1':
                if 'periode_start' not in result['bedrijfsgegevens']:
                    result['bedrijfsgegevens']['periode_start'] = data['met:dte1']
            elif dims.get('mmt') == 'mmt:m2':
                if 'periode_einde' not in result['bedrijfsgegevens']:
                    result['bedrijfsgegevens']['periode_einde'] = data['met:dte1']

    # Verzamel adres informatie voor de onderneming
    adressen = []
    for ctx_id, ctx_info in contexts.items():
        dims = ctx_info['dimensions']
        data = context_data[ctx_id]

        if dims.get('psn') == 'psn:m1' and dims.get('ctc') == 'ctc:m1':
            # Maatschappelijke zetel (ctc:m1)
            straat = data.get('met:str2', '')

            # Zoek huisnummer, postcode en land in volgende contexten
            ctx_num = int(ctx_id[1:]) if ctx_id[1:].isdigit() else 0

            adres_info = {'type': 'Maatschappelijke zetel', 'straat': straat}

            for offset in range(1, 5):
                next_ctx = f"I{ctx_num + offset}"
                if next_ctx in context_data:
                    next_data = context_data[next_ctx]
                    next_dims = contexts[next_ctx]['dimensions']

                    if next_dims.get('ctc') == 'ctc:m2' and 'met:str2' in next_data:
                        adres_info['nummer'] = next_data['met:str2']
                    elif next_dims.get('ctc') == 'ctc:m4' and 'pcd-enum:list1' in next_data:
                        adres_info['postcode'] = next_data['pcd-enum:list1'].replace('pcd:m', '')
                    elif next_dims.get('ctc') == 'ctc:m6' and 'cty-enum:list1' in next_data:
                        adres_info['land'] = next_data['cty-enum:list1'].replace('cty:m', '')

            if adres_info.get('straat'):
                adressen.append(adres_info)

    if adressen:
        result['bedrijfsgegevens']['adres'] = adressen[0]  # Neem eerste (maatschappelijke zetel)

    # === EXTRACT BESTUURDERS ===
    # Bestuurders zijn personen met psn:m12 in NBB taxonomie
    bestuurders_contexten = []
    for ctx_id, ctx_info in contexts.items():
        dims = ctx_info['dimensions']
        if dims.get('psn') == 'psn:m12':
            bestuurders_contexten.append(ctx_id)

    # Groepeer bestuurders data
    # Elke bestuurder heeft meestal meerdere contexten voor adres, functie, mandaat, etc.
    bestuurder_groups = []
    used_contexts = set()

    for ctx_id in bestuurders_contexten:
        if ctx_id in used_contexts:
            continue

        ctx_num = int(ctx_id[1:]) if ctx_id[1:].isdigit() else 0

        # Verzamel alle contexten voor deze bestuurder (meestal 10-15 opeenvolgende contexten)
        bestuurder_data = {}
        for offset in range(0, 25):
            check_ctx = f"I{ctx_num + offset}"
            if check_ctx in contexts and contexts[check_ctx]['dimensions'].get('psn') == 'psn:m12':
                used_contexts.add(check_ctx)
                data = context_data.get(check_ctx, {})
                dims = contexts[check_ctx]['dimensions']

                # Adres type
                if 'atc-enum:list1' in data:
                    bestuurder_data['adres_type'] = data['atc-enum:list1'].replace('atc:m', '')

                # Straat (ctc:m1)
                if dims.get('ctc') == 'ctc:m1' and 'met:str2' in data:
                    bestuurder_data['straat'] = data['met:str2']

                # Huisnummer (ctc:m2)
                if dims.get('ctc') == 'ctc:m2' and 'met:str2' in data:
                    bestuurder_data['nummer'] = data['met:str2']

                # Postcode (ctc:m4)
                if dims.get('ctc') == 'ctc:m4' and 'pcd-enum:list1' in data:
                    bestuurder_data['postcode'] = data['pcd-enum:list1'].replace('pcd:m', '')

                # Land (ctc:m6)
                if dims.get('ctc') == 'ctc:m6' and 'cty-enum:list1' in data:
                    bestuurder_data['land'] = data['cty-enum:list1'].replace('cty:m', '')

                # Functie
                if 'fct-enum:list1' in data:
                    fct_code = data['fct-enum:list1'].replace('fct:m', '')
                    # fct:m10 = Zaakvoerder, fct:m13 = Bestuurder, fct:m14 = Bedrijfsrevisor
                    functie_mapping = {
                        '10': 'Zaakvoerder',
                        '13': 'Bestuurder',
                        '14': 'Bedrijfsrevisor',
                        '15': 'Commissaris',
                    }
                    bestuurder_data['functie'] = functie_mapping.get(fct_code, f'Functie code {fct_code}')

                # Mandaat start
                if dims.get('dcl') == 'dcl:m15' and 'met:dte1' in data:
                    bestuurder_data['mandaat_start'] = data['met:dte1']

                # Mandaat einde
                if dims.get('dcl') == 'dcl:m16' and 'met:dte1' in data:
                    bestuurder_data['mandaat_einde'] = data['met:dte1']
            elif check_ctx in contexts and contexts[check_ctx]['dimensions'].get('psn') != 'psn:m12':
                # Gestopt met deze groep
                break

        if bestuurder_data:
            bestuurder_groups.append(bestuurder_data)

    result['bestuurders'] = bestuurder_groups

    # === EXTRACT AANDEELHOUDERS ===
    # Zoek alle ondernemingsnummers (10 cijfers beginnend met 0)
    enterprise_numbers = []
    for ctx_id, data in context_data.items():
        for key, value in data.items():
            if 'str' in key and value.isdigit() and len(value) == 10 and value.startswith('0'):
                enterprise_numbers.append((value, ctx_id))

    main_enterprise = result['bedrijfsgegevens'].get('ondernemingsnummer')
    seen_numbers = set()

    for en, ctx_id in enterprise_numbers:
        if en in seen_numbers or en == main_enterprise:
            continue

        seen_numbers.add(en)

        # Dit is waarschijnlijk een aandeelhouder of dochteronderneming
        aandeelhouder = {'ondernemingsnummer': en}

        # Zoek gerelateerde informatie in naburige contexten
        ctx_num = int(ctx_id[1:]) if ctx_id[1:].isdigit() else 0

        for offset in range(0, 20):
            check_ctx = f"I{ctx_num + offset}"
            if check_ctx in context_data:
                data = context_data[check_ctx]
                dims = contexts[check_ctx]['dimensions']

                # Rechtsvorm
                if 'lgf-enum:list1' in data or 'lgf-enum:list2' in data:
                    lgf = data.get('lgf-enum:list1', data.get('lgf-enum:list2', ''))
                    rechtsvorm_code = lgf.replace('lgf:m', '')
                    # lgf:m014 = BV, lgf:m610 = NV
                    rechtsvorm_mapping = {
                        '014': 'Besloten Vennootschap (BV)',
                        '610': 'Naamloze Vennootschap (NV)',
                    }
                    aandeelhouder['rechtsvorm'] = rechtsvorm_mapping.get(rechtsvorm_code,
                                                                         f'Rechtsvorm {rechtsvorm_code}')

                # Adres - alleen als het een adres context is
                if dims.get('ctc') == 'ctc:m1' and 'met:str2' in data:
                    aandeelhouder['straat'] = data['met:str2']
                elif dims.get('ctc') == 'ctc:m2' and 'met:str2' in data:
                    aandeelhouder['nummer'] = data['met:str2']
                elif dims.get('ctc') == 'ctc:m4' and 'pcd-enum:list1' in data:
                    aandeelhouder['postcode'] = data['pcd-enum:list1'].replace('pcd:m', '')
                elif dims.get('ctc') == 'ctc:m6' and 'cty-enum:list1' in data:
                    aandeelhouder['land'] = data['cty-enum:list1'].replace('cty:m', '')

                # Datum (meestal balansdatum)
                if 'met:dte1' in data and 'datum' not in aandeelhouder:
                    aandeelhouder['datum'] = data['met:dte1']

                # Aantal aandelen
                if 'met:int2' in data:
                    aandeelhouder['aantal_aandelen'] = int(data['met:int2'])

                # Percentage deelneming
                if 'met:pct1' in data:
                    pct = float(data['met:pct1'])
                    # Alleen opslaan als het een redelijk percentage is
                    if 0 < pct <= 1:
                        aandeelhouder['percentage'] = f"{pct * 100:.2f}%"

                # Type aandelen
                if 'met:str2' in data and 'aandelen' in data['met:str2'].lower():
                    aandeelhouder['type_aandelen'] = data['met:str2']

                # Bedragen (activa, eigen vermogen)
                if 'met:am2' in data:
                    if 'activa' not in aandeelhouder:
                        aandeelhouder['activa'] = f"€ {float(data['met:am2']):,.2f}"
                    elif 'eigen_vermogen' not in aandeelhouder:
                        aandeelhouder['eigen_vermogen'] = f"€ {float(data['met:am2']):,.2f}"

        # Alleen toevoegen als er nuttige informatie is
        if len(aandeelhouder) > 1:
            result['aandeelhouders'].append(aandeelhouder)

    # === EXTRACT FINANCIËLE CIJFERS ===
    # Verzamel alle monetaire bedragen (am1, am2)
    for ctx_id, data in context_data.items():
        dims = contexts[ctx_id]['dimensions']

        for key, value in data.items():
            if key in ['met:am1', 'met:am2']:
                try:
                    bedrag = float(value)

                    # Probeer te identificeren wat het bedrag betekent op basis van context
                    bas_code = dims.get('bas', '')

                    # NBB codes voor balans posten
                    # bas:m2 = Vaste activa
                    # bas:m22 = Vlottende activa
                    # bas:m25 = Totaal activa
                    # Etc. (zie NBB taxonomie documentatie)

                    label = f"Bedrag_{bas_code}_{key}_{ctx_id}"

                    # Alleen positieve bedragen en betekenisvolle codes
                    if bedrag != 0 and bas_code:
                        result['financiele_cijfers'][label] = f"€ {bedrag:,.2f}"
                except ValueError:
                    continue

    return result


def print_results(result):
    """
    Print de geëxtraheerde informatie in een leesbaar formaat.

    Args:
        result (dict): Dictionary met geëxtraheerde informatie
    """
    if not result:
        print("Geen data kunnen extraheren uit het XBRL bestand.")
        return

    print("\n" + "=" * 80)
    print("XBRL ANALYSE RESULTAAT")
    print("=" * 80)

    # Bedrijfsgegevens
    print("\n### BEDRIJFSGEGEVENS ###\n")
    bg = result['bedrijfsgegevens']

    if 'naam' in bg:
        print(f"Bedrijfsnaam: {bg['naam']}")
    if 'ondernemingsnummer' in bg:
        print(f"Ondernemingsnummer: {bg['ondernemingsnummer']}")
    if 'rechtsvorm_code' in bg:
        print(f"Rechtsvorm code: {bg['rechtsvorm_code']}")

    if 'adres' in bg:
        adres = bg['adres']
        print(f"\n{adres.get('type', 'Adres')}:")
        print(f"  {adres.get('straat', '')} {adres.get('nummer', '')}")
        print(f"  {adres.get('postcode', '')} {adres.get('land', '')}")

    if 'periode_start' in bg or 'periode_einde' in bg:
        print(f"\nBoekjaar:")
        if 'periode_start' in bg:
            print(f"  Van: {bg['periode_start']}")
        if 'periode_einde' in bg:
            print(f"  Tot: {bg['periode_einde']}")

    if 'datum_algemene_vergadering' in bg:
        print(f"\nDatum algemene vergadering: {bg['datum_algemene_vergadering']}")

    if 'datum_afsluiting_boekjaar' in bg:
        print(f"Datum afsluiting boekjaar: {bg['datum_afsluiting_boekjaar']}")

    # Bestuurders
    print(f"\n### BESTUURDERS ({len(result['bestuurders'])}) ###\n")

    if result['bestuurders']:
        for i, bestuurder in enumerate(result['bestuurders'], 1):
            print(f"Bestuurder {i}:")

            if 'functie' in bestuurder:
                print(f"  Functie: {bestuurder['functie']}")

            # Adres
            if 'straat' in bestuurder or 'nummer' in bestuurder:
                adres_str = f"  Adres: {bestuurder.get('straat', '')} {bestuurder.get('nummer', '')}"
                if 'postcode' in bestuurder:
                    adres_str += f", {bestuurder['postcode']}"
                if 'land' in bestuurder:
                    adres_str += f" ({bestuurder['land']})"
                print(adres_str)

            # Mandaat
            if 'mandaat_start' in bestuurder or 'mandaat_einde' in bestuurder:
                print(f"  Mandaat: {bestuurder.get('mandaat_start', '?')} tot {bestuurder.get('mandaat_einde', '?')}")

            print()
    else:
        print("Geen bestuurders gevonden in het XBRL bestand.")

    # Aandeelhouders
    print(f"\n### AANDEELHOUDERS/DEELNEMINGEN ({len(result['aandeelhouders'])}) ###\n")

    if result['aandeelhouders']:
        for i, aandeelhouder in enumerate(result['aandeelhouders'], 1):
            print(f"Aandeelhouder {i}:")
            print(f"  Ondernemingsnummer: {aandeelhouder['ondernemingsnummer']}")

            if 'rechtsvorm' in aandeelhouder:
                print(f"  Rechtsvorm: {aandeelhouder['rechtsvorm']}")

            # Adres
            if 'straat' in aandeelhouder:
                adres_str = f"  Adres: {aandeelhouder.get('straat', '')} {aandeelhouder.get('nummer', '')}"
                if 'postcode' in aandeelhouder:
                    adres_str += f", {aandeelhouder['postcode']}"
                if 'land' in aandeelhouder:
                    adres_str += f" ({aandeelhouder['land']})"
                print(adres_str)

            # Deelneming info
            if 'percentage' in aandeelhouder:
                print(f"  Deelneming: {aandeelhouder['percentage']}")
            if 'aantal_aandelen' in aandeelhouder:
                print(f"  Aantal aandelen: {aandeelhouder['aantal_aandelen']:,}")
            if 'type_aandelen' in aandeelhouder:
                print(f"  Type: {aandeelhouder['type_aandelen']}")

            # Financiële info
            if 'activa' in aandeelhouder:
                print(f"  Activa: {aandeelhouder['activa']}")
            if 'eigen_vermogen' in aandeelhouder:
                print(f"  Eigen vermogen: {aandeelhouder['eigen_vermogen']}")

            if 'datum' in aandeelhouder:
                print(f"  Peildatum: {aandeelhouder['datum']}")

            print()
    else:
        print("Geen aandeelhouders gevonden in het XBRL bestand.")

    # Financiële cijfers (toon alleen de eerste 20)
    print(f"\n### FINANCIËLE CIJFERS ###")
    print(f"(Totaal: {len(result['financiele_cijfers'])} posten)\n")

    if result['financiele_cijfers']:
        print("Eerste 20 financiële posten:")
        for i, (label, bedrag) in enumerate(list(result['financiele_cijfers'].items())[:20], 1):
            # Maak label leesbaar
            clean_label = label.replace('_', ' ').replace('bas:', 'Code ')
            print(f"  {i:2d}. {clean_label}: {bedrag}")

        if len(result['financiele_cijfers']) > 20:
            print(f"\n  ... en nog {len(result['financiele_cijfers']) - 20} andere posten")
    else:
        print("Geen financiële cijfers gevonden.")

    print("\n" + "=" * 80)


def main():
    """
    Hoofdfunctie voor het script.
    """
    if len(sys.argv) < 2:
        print("Gebruik: python xbrl_analyzer.py <xbrl_bestand>")
        print("\nVoorbeeld:")
        print("  python xbrl_analyzer.py jaarrekening.xbrl")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"Analyseren van XBRL bestand: {filename}")
    print("Dit kan even duren...")

    result = analyze_xbrl(filename)

    if result:
        print_results(result)
    else:
        print("Fout bij het analyseren van het XBRL bestand.")
        sys.exit(1)


if __name__ == "__main__":
    main()
