"""Inlezen van jaarrekeningen uit verschillende bronformaten.

Ondersteunde bronnen leveren allemaal dezelfde ``{code: waarde}``-dict op, die
door :func:`core.analyse.analyseer_data` verder verwerkt wordt:

- CSV        : de ``"code","waarde"``-export (zie :func:`core.analyse.parse_csv`).
- JSON       : de NBB "jsonxbrl"-structuur (AccountingData) met rubrieken.
- PDF        : de door de NBB gegenereerde PDF, waarin de rubriekcodes vermeld staan.
- XBRL       : het ruwe XBRL-neerleggingsbestand (zie opmerking hieronder).

Opmerking over XBRL: in een XBRL-*instance* staat enkel de waarde van een rubriek;
de rubriekcode zelf zit in de *Table linkbase* van de NBB-taxonomie, niet in het
bestand. Ruwe XBRL betrouwbaar naar rubriekcodes omzetten vereist dus de volledige
taxonomie. De NBB genereert voor elke XBRL-neerlegging (vanaf 4 april 2022) ook een
JSON-versie met de codes; dat is de aangewezen route (upload de JSON of gebruik het
KBO-nummer om ze automatisch op te halen).
"""

import io
import json
import re

try:
    from core.analyse import ALIASES, parse_bedrag, parse_csv
    from core.StructuurBalans import structuurBalans
    from core.StructuurResultatenRekening import structuurResultatenRekening
except ModuleNotFoundError:  # standalone vanuit map core/
    from analyse import ALIASES, parse_bedrag, parse_csv
    from StructuurBalans import structuurBalans
    from StructuurResultatenRekening import structuurResultatenRekening


class BronFout(Exception):
    """Nette, voor de gebruiker leesbare fout bij het inlezen van een bron."""


def _tekst(inhoud):
    if isinstance(inhoud, (bytes, bytearray)):
        for codec in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return inhoud.decode(codec)
            except UnicodeDecodeError:
                continue
        return inhoud.decode("utf-8", errors="replace")
    return inhoud


# --- JSON (NBB jsonxbrl / AccountingData) ---------------------------------

def _adres_str(addr):
    if not isinstance(addr, dict):
        return ""
    straat = " ".join(str(addr.get(k, "")).strip() for k in ("Street", "Number", "Box")).strip()
    stad = " ".join(str(addr.get(k) or addr.get(a, "")).strip()
                    for k, a in (("OtherPostalCode", "PostalCode"), ("OtherCity", "City"))).strip()
    land = str(addr.get("OtherCountry") or addr.get("Country") or "").strip()
    return ", ".join(deel for deel in (straat, stad, land) if deel)


def _mandaat_velden(mandaten):
    functie, start, einde = "", "", ""
    if isinstance(mandaten, list) and mandaten:
        m = mandaten[0]
        functie = str(m.get("FunctionMandate") or m.get("OtherFunctionMandate") or "").strip()
        datums = m.get("MandateDates") or {}
        start = str(datums.get("StartDate") or "").strip()
        einde = str(datums.get("EndDate") or "").strip()
    return functie, start, einde


def _bestuurders_uit_json(acc):
    admins = acc.get("Administrators") or acc.get("administrators") or {}
    if not isinstance(admins, dict):
        return []
    bestuurders = []
    for np in admins.get("NaturalPersons", []) or []:
        persoon = np.get("Person", {}) if isinstance(np, dict) else {}
        naam = " ".join(str(persoon.get(k, "")).strip() for k in ("FirstName", "LastName")).strip()
        functie, start, einde = _mandaat_velden(np.get("Mandates"))
        if not functie:
            functie = str(np.get("Profession") or "Bestuurder").strip()
        if naam:
            bestuurders.append({"naam": naam, "adres": _adres_str(persoon.get("Address")),
                                "functie": functie or "Bestuurder", "mandaat_start": start, "mandaat_einde": einde})
    for lp in admins.get("LegalPersons", []) or []:
        entity = lp.get("Entity", {}) if isinstance(lp, dict) else {}
        naam = str(entity.get("Name") or entity.get("LegalName") or entity.get("EnterpriseName") or "").strip()
        functie, start, einde = _mandaat_velden(lp.get("Mandates"))
        if naam:
            bestuurders.append({"naam": naam, "adres": _adres_str(entity.get("Address")),
                                "functie": functie or "Bestuurder (rechtspersoon)", "mandaat_start": start, "mandaat_einde": einde})
    return bestuurders


def parse_jsonxbrl(inhoud, extra_meta=None):
    """Lees de NBB "AccountingData"-JSON in als ``{code: waarde}``-dict.

    Rubrieken met ``Period == "N"`` (of zonder periode) zijn het lopende boekjaar;
    ``NM1`` (vorig boekjaar) wordt overgeslagen.
    """
    tekst = _tekst(inhoud)
    try:
        obj = json.loads(tekst)
    except (ValueError, TypeError) as exc:
        raise BronFout("Ongeldig JSON-bestand.") from exc

    # De AccountingData kan direct of ingepakt aangeleverd worden.
    acc = obj
    if isinstance(obj, dict):
        for sleutel in ("AccountingData", "accountingData", "data"):
            if isinstance(obj.get(sleutel), dict):
                acc = obj[sleutel]
                break
    elif isinstance(obj, list) and obj:
        acc = obj[0]

    if not isinstance(acc, dict):
        raise BronFout("Onverwachte JSON-structuur voor jaarrekeningdata.")

    rubrieken = acc.get("Rubrics") or acc.get("rubrics") or []
    if not rubrieken:
        raise BronFout("Geen rubrieken (Rubrics) gevonden in het JSON-bestand.")

    data = {}
    vorig = {}
    for rubriek in rubrieken:
        if not isinstance(rubriek, dict):
            continue
        code = rubriek.get("Code", rubriek.get("code"))
        waarde = rubriek.get("Value", rubriek.get("value"))
        periode = rubriek.get("Period", rubriek.get("period"))
        if code is None or waarde is None:
            continue
        if periode in (None, "", "N"):
            data[str(code).strip()] = str(waarde).strip()
        elif periode == "NM1":
            vorig[str(code).strip()] = str(waarde).strip()
    if vorig:
        data["__vorig__"] = vorig

    # Identificatiegegevens omzetten naar dezelfde sleutels als de CSV-export.
    naam = acc.get("EnterpriseName") or acc.get("enterpriseName")
    if naam:
        data["Entity name"] = str(naam).strip()
    ref = acc.get("ReferenceNumber") or acc.get("referenceNumber")
    if ref:
        data["Reference number"] = str(ref).strip()
    lgf = acc.get("LegalForm") or acc.get("legalForm")
    if isinstance(lgf, dict):
        lgf = lgf.get("Code") or lgf.get("Description") or lgf.get("Value")
    if lgf:
        data["Legal form"] = str(lgf).strip()
    data.setdefault("Currency", "EUR")

    bestuurders = _bestuurders_uit_json(acc)
    if bestuurders:
        data["__bestuurders__"] = bestuurders

    if extra_meta:
        for sleutel, waarde in extra_meta.items():
            if waarde:
                data[sleutel] = str(waarde).strip()
    return data


# --- PDF (door de NBB gegenereerde jaarrekening) --------------------------

def _bekende_codes():
    codes = set()
    for structuur in (structuurBalans, structuurResultatenRekening):
        for item in structuur:
            code = (item.get("Code") or "").strip()
            if code and any(ch.isdigit() for ch in code):
                codes.add(code)
                for alias in ALIASES.get(code, []):  # bv. 20/28 (oud) naast 21/28
                    codes.add(alias)
    return codes


# Een bedrag in de NBB-PDF: gehele getallen met punt-duizendtallen (26.435.299),
# optioneel met komma-decimalen (26.435.298,99), een minteken of haakjes.
_BEDRAG = re.compile(
    r"^\(?-?\d{1,3}(\.\d{3})+(,\d+)?\)?$"   # 8.728.131  of  26.435.298,99
    r"|^\(?-?\d+,\d+\)?$"                    # 1234,56
    r"|^\(?-?\d{4,}\)?$"                     # 26435299 (zonder scheidingsteken)
    r"|^-?\d{1,3}\)?$"                        # 158 , 0 , -12
)


_LEGE_CEL = re.compile(r"^\.{2,}$")  # puntjeslijn = lege cel (bv. ".............")


def codes_uit_tekst(tekst):
    """Haal ``{code: waarde}`` uit platte PDF-tekst van een NBB-jaarrekening.

    Werkt voor twee lay-outs:
    - alles op één regel (``Rubriek [Toel.] Code Boekjaar Vorig``), en
    - code en bedragen elk op een aparte regel (verkort/Frans model).

    De tekst wordt tot één tokenreeks herleid; na een gekende rubriekcode wordt het
    eerste bedrag (kolom 'boekjaar') genomen. Het zoeken stopt bij een lege cel
    (puntjes) of bij de volgende gekende code, zodat geen waarde van een andere
    rubriek wordt overgenomen.
    """
    bekende = _bekende_codes()
    # '!' is een kolomscheider in zeer oude jaarrekeningen (ASCII-tabellen) -> als spatie.
    tokens = tekst.replace("\t", " ").replace("!", " ").split()
    huidig, vorig = {}, {}
    n = len(tokens)
    for i, token in enumerate(tokens):
        if token in bekende and token not in huidig and i + 1 < n:
            # Kolom 'boekjaar' staat onmiddellijk na de code; 'vorig boekjaar' erna.
            v1 = tokens[i + 1]
            if _BEDRAG.match(v1) and not _LEGE_CEL.match(v1):
                w1 = parse_bedrag(v1)
                if w1 is not None:
                    huidig[token] = str(w1)
                    if i + 2 < n:
                        v2 = tokens[i + 2]
                        if _BEDRAG.match(v2) and not _LEGE_CEL.match(v2):
                            w2 = parse_bedrag(v2)
                            if w2 is not None:
                                vorig[token] = str(w2)
    return huidig, vorig


def _codes_gericht(tekst, codes):
    """Haal specifieke codes (bv. personeelscodes uit de sociale balans) gericht op."""
    doel = set(codes)
    tokens = tekst.replace("\t", " ").replace("!", " ").split()
    out = {}
    for i, token in enumerate(tokens[:-1]):
        if token in doel and token not in out:
            volgend = tokens[i + 1]
            if _BEDRAG.match(volgend) and not _LEGE_CEL.match(volgend):
                waarde = parse_bedrag(volgend)
                if waarde is not None:
                    out[token] = str(waarde)
    return out


_DATUM_BE = re.compile(r"(\d{2})[-/](\d{2})[-/](\d{4})")
_MANDAAT = re.compile(
    r"Begin van het mandaat\s*:\s*(?P<start>\d{4}-\d{2}-\d{2})?.*?"
    r"Einde van het mandaat\s*:\s*(?P<einde>\d{4}-\d{2}-\d{2})?\s*(?P<rol>[A-Za-zé]+)?",
    re.IGNORECASE,
)


def _waarde_na_dubbelpunt(regel):
    waarde = regel.split(":", 1)[-1].strip(" .\t") if ":" in regel else ""
    return waarde if waarde and not set(waarde) <= {"."} else ""


def metadata_uit_tekst(tekst):
    """Haal identificatiegegevens uit de PDF-tekst (NL en FR), best-effort."""
    meta = {}
    for regel in tekst.splitlines():
        r = regel.strip()
        low = r.lower()
        if not meta.get("Entity name") and (low.startswith("naam") or low.startswith("dénomination")
                or low.startswith("denomination") or low.startswith("firma of naam") or low.startswith("firma")):
            waarde = _waarde_na_dubbelpunt(r)
            if waarde:
                meta["Entity name"] = waarde
        elif not meta.get("Entity number") and (low.startswith("ondernemingsnummer") or low.startswith("numéro d") or low.startswith("numero d")):
            cijfers = re.sub(r"\D", "", r)
            if len(cijfers) >= 9:
                meta["Entity number"] = cijfers
        elif not meta.get("Legal form") and (low.startswith("rechtsvorm") or low.startswith("forme jurid")):
            waarde = _waarde_na_dubbelpunt(r)
            if waarde:
                meta["Legal form"] = waarde
        # Boekjaarperiode (NL: "van 01-07-2024 tot 30-06-2025"; FR: "du 01/07/2024 au 30/06/2025")
        heeft_periode = ("boekjaar" in low and " van " in low and " tot " in low and "vorig" not in low) \
            or ("exercice" in low and " du " in low and " au " in low and "précédent" not in low and "precedent" not in low)
        if heeft_periode and "Accounting period end date" not in meta:
            be = _DATUM_BE.findall(r)
            if len(be) >= 2:
                meta["Accounting period start date"] = f"{be[0][2]}-{be[0][1]}-{be[0][0]}"
                meta["Accounting period end date"] = f"{be[1][2]}-{be[1][1]}-{be[1][0]}"

    # Zeer oude jaarrekeningen zijn in Belgische frank uitgedrukt.
    if re.search(r"\bBEF\b", tekst) or "franken" in tekst.lower():
        meta["Currency"] = "BEF"

    # Ondernemingsnummer valt vaak alleen betrouwbaar af te leiden uit de paginavoettekst;
    # neem het vaakst voorkomende nummer (het eigen nummer staat op elke pagina).
    if not meta.get("Entity number"):
        nummers = re.findall(r"\b0\d{3}\.\d{3}\.\d{3}\b|\b0\d{9}\b", tekst)
        if nummers:
            import collections
            meta["Entity number"] = collections.Counter(re.sub(r"\D", "", n) for n in nummers).most_common(1)[0][0]
    return meta


def bestuurders_uit_tekst(tekst):
    """Best-effort extractie van bestuurders/zaakvoerders/commissarissen uit de PDF-tekst.

    Neemt telkens de laatste regels vóór een 'Begin van het mandaat'-regel als het blok
    (naam + adres) van één bestuurder, zodat intro-tekst en vertegenwoordigers wegvallen.
    """
    regels = [r.strip() for r in tekst.splitlines()]
    start = None
    for i, r in enumerate(regels):
        if "LIJST VAN DE BESTUURDERS" in r.upper():
            start = i
            break
    if start is None:
        return []

    bestuurders = []
    buffer = []
    for r in regels[start + 1:]:
        m = _MANDAAT.search(r)
        if m:
            venster = [b for b in buffer[-5:]
                       if b and not re.match(r"^\d{9,}$", b)
                       and "vertegenwoordigd" not in b.lower()]
            # Verwijder resterende all-caps kopfragmenten (bv. "CORRECTIE") of een
            # meegesleepte landregel vooraan, zodat de naam bovenaan staat.
            while venster and venster[0].isupper():
                venster.pop(0)
            if venster:
                bestuurders.append({
                    "naam": venster[0],
                    "adres": ", ".join(venster[1:]) if len(venster) > 1 else "",
                    "functie": (m.group("rol") or "Bestuurder").strip(),
                    "mandaat_start": m.group("start") or "",
                    "mandaat_einde": m.group("einde") or "",
                })
            buffer = []
            continue
        if bestuurders and r.upper().startswith("VERKLARING BETREFFENDE"):
            break
        if (not r or r.upper().startswith(("N°", "PAGE"))
                or r.isdigit() or "vertegenwoordigd" in r.lower()):
            continue
        if r.isupper() and len(r.split()) >= 4:
            continue
        buffer.append(r)
    return bestuurders


def parse_pdf(fileobj):
    """Lees een NBB-jaarrekening-PDF in als ``{code: waarde}``-dict (best-effort)."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise BronFout("PDF-ondersteuning vereist het pakket 'pypdf'.") from exc

    if hasattr(fileobj, "read"):
        bron = io.BytesIO(fileobj.read())
    else:
        bron = fileobj
    try:
        reader = PdfReader(bron)
        paginas = [(pagina.extract_text() or "") for pagina in reader.pages]
    except Exception as exc:  # noqa: BLE001
        raise BronFout("De PDF kon niet gelezen worden.") from exc

    tekst = "\n".join(paginas)
    # Beperk de code-extractie tot de eigenlijke overzichtspagina's (balans/RR),
    # zodat rubriekcodes niet per ongeluk matchen met paginanummers of toelichtingen.
    ankers = ("20/58", "10/49", "9901", "9903", "9904", "9905",
              "BALANS", "BILAN", "ACTIVA", "ACTIF", "PASSIVA", "PASSIF",
              "RESULTATENREKENING", "COMPTE DE R", "COMPTES DE R")
    overzicht = [p for p in paginas if any(a in p or a in p.upper() for a in ankers)]
    data, vorig = codes_uit_tekst("\n".join(overzicht) if overzicht else tekst)

    # Personeelscijfers staan op de sociale balans (buiten de overzichtspagina's en
    # niet in de balans/RR-structuur); gericht ophalen uit de volledige tekst.
    personeel = _codes_gericht(tekst, ("9087", "9086", "1003", "1013", "1023"))
    for code, waarde in personeel.items():
        data.setdefault(code, waarde)
    if "9087" not in data and "1003" in data:
        data["9087"] = data["1003"]  # gemiddeld personeelsbestand benaderen via totaal VTE
    if vorig:
        data["__vorig__"] = vorig  # 'vorig boekjaar'-kolom voor evolutie en kasstromen
    if not data.get("20/58") and not data.get("10/49"):
        raise BronFout(
            "Geen herkenbare balanscodes in de PDF gevonden. Gebruik bij voorkeur de "
            "JSON-export of het KBO-nummer; niet elke PDF-lay-out kan automatisch gelezen worden."
        )
    for sleutel, waarde in metadata_uit_tekst(tekst).items():
        data.setdefault(sleutel, waarde)
    data.setdefault("Currency", "EUR")
    bestuurders = bestuurders_uit_tekst(tekst)
    if bestuurders:
        data["__bestuurders__"] = bestuurders
    return data


# --- XBRL (ruw neerleggingsbestand) ---------------------------------------

def parse_xbrl(inhoud):
    """Lees een ruwe XBRL in via het ondernemingsnummer in de entity-identifier.

    In een XBRL-*instance* staan de bedragen onder interne datapunt-members (dim:bas),
    niet onder de rubriekcodes zelf — die koppeling zit in de NBB-taxonomie. We lezen
    daarom het ondernemingsnummer uit het bestand en halen (als de gratis NBB-sleutel
    is ingesteld) automatisch de JSON-versie van dezelfde neerlegging op, die de
    rubriekcodes wél bevat.
    """
    import os

    tekst = _tekst(inhoud)
    match = re.search(r"<identifier[^>]*>\s*([0-9]{9,10})\s*</identifier>", tekst)
    kbo = match.group(1) if match else None
    if kbo and len(kbo) == 9:
        kbo = "0" + kbo

    if kbo and os.environ.get("NBB_CBSO_SUBSCRIPTION_KEY"):
        from core.nbb_api import haal_op_via_kbo  # lazy import (vermijdt circulaire import)
        return haal_op_via_kbo(kbo)

    kbo_txt = f" {kbo[0:4]}.{kbo[4:7]}.{kbo[7:10]}" if kbo and len(kbo) == 10 else ""
    raise BronFout(
        "Een ruw XBRL-bestand bevat de rubriekcodes niet zelf; die zitten in de NBB-taxonomie. "
        f"Dit bestand hoort bij ondernemingsnummer{kbo_txt or ' (onbekend)'}. "
        "Stel de gratis sleutel NBB_CBSO_SUBSCRIPTION_KEY in om de jaarrekening automatisch op te "
        "halen, of upload de JSON-export van dezelfde neerlegging."
    )


# --- Dispatch op basis van bestandsnaam -----------------------------------

def laad_bron(bestandsnaam, fileobj):
    """Kies op basis van de extensie de juiste parser en geef een ``{code: waarde}``-dict terug."""
    naam = (bestandsnaam or "").lower()
    if naam.endswith(".csv"):
        return parse_csv(fileobj)
    if naam.endswith(".json"):
        return parse_jsonxbrl(fileobj.read() if hasattr(fileobj, "read") else fileobj)
    if naam.endswith(".pdf"):
        return parse_pdf(fileobj)
    if naam.endswith(".xbrl") or naam.endswith(".xml"):
        return parse_xbrl(fileobj.read() if hasattr(fileobj, "read") else fileobj)
    raise BronFout("Niet-ondersteund bestandstype. Gebruik .csv, .json of .pdf.")
