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
    from core.analyse import parse_bedrag, parse_csv
    from core.StructuurBalans import structuurBalans
    from core.StructuurResultatenRekening import structuurResultatenRekening
except ModuleNotFoundError:  # standalone vanuit map core/
    from analyse import parse_bedrag, parse_csv
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
    return codes


# Een bedrag in de NBB-PDF: gehele getallen met punt-duizendtallen (26.435.299),
# optioneel met komma-decimalen (26.435.298,99), een minteken of haakjes.
_BEDRAG = re.compile(
    r"^\(?-?\d{1,3}(\.\d{3})+(,\d+)?\)?$"   # 8.728.131  of  26.435.298,99
    r"|^\(?-?\d+,\d+\)?$"                    # 1234,56
    r"|^\(?-?\d{4,}\)?$"                     # 26435299 (zonder scheidingsteken)
    r"|^-?\d{1,3}\)?$"                        # 158 , 0 , -12
)


def codes_uit_tekst(tekst):
    """Haal ``{code: waarde}`` uit platte PDF-tekst van een NBB-jaarrekening.

    Lay-out per regel: ``Rubriek [Toel.] Code Boekjaar [Vorig boekjaar]``. Na een
    gekende rubriekcode wordt het eerste bedrag (kolom 'boekjaar') genomen. Best-effort.
    """
    bekende = _bekende_codes()
    data = {}
    for regel in tekst.splitlines():
        tokens = regel.replace("\t", " ").split()
        for i, token in enumerate(tokens):
            if token in bekende and token not in data:
                for volgend in tokens[i + 1:]:
                    if volgend in bekende:
                        break  # volgende rubriek: deze had geen bedrag op de regel
                    if _BEDRAG.match(volgend):
                        waarde = parse_bedrag(volgend)
                        if waarde is not None:
                            data[token] = str(waarde)
                        break
    return data


_DATUM_BE = re.compile(r"(\d{2})[-/](\d{2})[-/](\d{4})")
_MANDAAT = re.compile(
    r"Begin van het mandaat\s*:\s*(?P<start>\d{4}-\d{2}-\d{2})?.*?"
    r"Einde van het mandaat\s*:\s*(?P<einde>\d{4}-\d{2}-\d{2})?\s*(?P<rol>[A-Za-zé]+)?",
    re.IGNORECASE,
)


def metadata_uit_tekst(tekst):
    """Haal identificatiegegevens uit de PDF-tekst (naam, nummer, rechtsvorm, boekjaar)."""
    meta = {}
    for regel in tekst.splitlines():
        r = regel.strip()
        low = r.lower()
        if not meta.get("Entity name") and low.startswith("naam"):
            waarde = r.split(":", 1)[-1].strip()
            if waarde:
                meta["Entity name"] = waarde
        elif not meta.get("Entity number") and low.startswith("ondernemingsnummer"):
            cijfers = re.sub(r"\D", "", r)
            if len(cijfers) >= 9:
                meta["Entity number"] = cijfers
        elif not meta.get("Legal form") and low.startswith("rechtsvorm"):
            waarde = r.split(":", 1)[-1].strip()
            if waarde:
                meta["Legal form"] = waarde
        # Boekjaarperiode: "... boekjaar dat de periode dekt van 01-07-2024 tot 30-06-2025"
        if ("boekjaar" in low and " van " in low and " tot " in low
                and "vorig" not in low and "Accounting period end date" not in meta):
            be = _DATUM_BE.findall(r)
            if len(be) >= 2:
                meta["Accounting period start date"] = f"{be[0][2]}-{be[0][1]}-{be[0][0]}"
                meta["Accounting period end date"] = f"{be[1][2]}-{be[1][1]}-{be[1][0]}"
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
        tekst = "\n".join((pagina.extract_text() or "") for pagina in reader.pages)
    except Exception as exc:  # noqa: BLE001
        raise BronFout("De PDF kon niet gelezen worden.") from exc

    data = codes_uit_tekst(tekst)
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
    """Ruwe XBRL wordt niet rechtstreeks ondersteund (codes zitten in de taxonomie)."""
    raise BronFout(
        "Ruwe XBRL-bestanden bevatten de rubriekcodes niet zelf (die zitten in de NBB-taxonomie). "
        "Gebruik de JSON-export van dezelfde neerlegging, of vul het KBO-/BTW-nummer in om de "
        "jaarrekening automatisch op te halen."
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
