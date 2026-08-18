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


_TOELICHTING = re.compile(r"^\d+(\.\d+)+$")            # bv. 6.3, 6.5.1 (verwijzing)
_BEDRAG = re.compile(r"^\(?-?\d{1,3}(\.\d{3})+(,\d+)?\)?$|^\(?-?\d+,\d+\)?$|^\(?-?\d{4,}\)?$|^0$")


def codes_uit_tekst(tekst):
    """Haal ``{code: waarde}`` uit platte PDF-tekst van een NBB-jaarrekening.

    Heuristiek: op elke regel wordt na een gekende rubriekcode het eerste bedrag
    (kolom 'boekjaar') als waarde genomen. Best-effort — de PDF-lay-out varieert.
    """
    bekende = _bekende_codes()
    data = {}
    for regel in tekst.splitlines():
        tokens = regel.replace("\t", " ").split()
        for i, token in enumerate(tokens):
            if token in bekende and token not in data:
                for volgend in tokens[i + 1:]:
                    if _TOELICHTING.match(volgend):
                        continue
                    if _BEDRAG.match(volgend):
                        waarde = parse_bedrag(volgend)
                        if waarde is not None:
                            data[token] = str(waarde)
                        break
    return data


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
