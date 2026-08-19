"""Analyse van een Belgische jaarrekening (CSV van de NBB) tegen de wettelijke structuur.

Deze module leest een CSV met ``"code","waarde"``-rijen in, koppelt de waarden aan
de wettelijke structuur (balans, resultatenrekening, metadata) en controleert of de
belangrijkste wettelijke optelsommen kloppen (o.a. of de balans in evenwicht is).
"""

import csv
import io

try:
    from core.StructuurBalans import structuurBalans
    from core.StructuurMetadata import structuurMetadata
    from core.StructuurResultatenRekening import structuurResultatenRekening
except ModuleNotFoundError:  # standalone uitvoeren vanuit de map core/
    from StructuurBalans import structuurBalans
    from StructuurMetadata import structuurMetadata
    from StructuurResultatenRekening import structuurResultatenRekening


# Codes die in de CSV van de NBB anders geschreven worden dan in onze structuur.
# De koppeling is wederzijds: we zoeken de waarde onder beide schrijfwijzen.
_ALIAS_PAREN = [
    ("7076A", "70/76A"),
    ("6066A", "60/66A"),
    ("7576B", "75/76B"),
    ("6566B", "65/66B"),
    ("677/7", "67/77"),
    ("21/28", "20/28"),   # oud model: vaste activa als 20/28 (incl. oprichtingskosten)
]
ALIASES = {}
for _a, _b in _ALIAS_PAREN:
    ALIASES.setdefault(_a, []).append(_b)
    ALIASES.setdefault(_b, []).append(_a)

# Rubrieken die als (sub)totaal vet mogen worden weergegeven.
TOTAAL_CODES = {
    "20/58", "10/49", "10/15", "21/28", "29/58", "17/49", "16", "3",
    "7076A", "6066A", "7576B", "6566B", "9901", "9903", "9904", "9905",
    "9906", "14", "677/7", "42/48",
}


def parse_bedrag(raw):
    """Zet een tekstwaarde uit de CSV om naar een float, of ``None`` als het geen bedrag is."""
    if raw is None:
        return None
    s = str(raw).strip().strip('"').strip()
    if s == "":
        return None
    negatief = False
    if s.startswith("(") and s.endswith(")"):
        negatief = True
        s = s[1:-1]
    s = s.replace(" ", "").replace("\u00a0", "")
    if "," in s and "." in s:
        # Beide scheidingstekens: het laatste is het decimaalteken.
        if s.rfind(",") > s.rfind("."):
            # Europese notatie "1.234.567,89" -> punten zijn duizendtallen
            s = s.replace(".", "").replace(",", ".")
        else:
            # Angelsaksische notatie "1,234,567.89" -> komma's zijn duizendtallen
            s = s.replace(",", "")
    elif "," in s:
        # Enkel komma -> decimaalteken (Europese notatie "1234,56")
        s = s.replace(",", ".")
    elif "." in s:
        # Enkel punt: duizendtallen wanneer alle groepen erna exact 3 cijfers tellen
        # ("9.273.680" of "6.000"), anders een decimaalteken ("1333311.09").
        stukken = s.lstrip("-").split(".")
        if len(stukken) > 1 and all(len(deel) == 3 for deel in stukken[1:]):
            s = s.replace(".", "")
    try:
        waarde = float(s)
    except ValueError:
        return None
    return -waarde if negatief else waarde


def _kandidaat_codes(code):
    """Alle schrijfwijzen waaronder we een structuurcode in de data mogen zoeken."""
    kandidaten = [code]
    schoon = (
        code.replace("(+)/(-)", "")
        .replace("(+)", "")
        .replace("(-)", "")
        .strip()
    )
    if schoon and schoon != code:
        kandidaten.append(schoon)
    for k in list(kandidaten):
        for alias in ALIASES.get(k, []):
            if alias not in kandidaten:
                kandidaten.append(alias)
    return kandidaten


def lees_waarde(data, code):
    """Zoek de numerieke waarde voor een structuurcode in de ingelezen data."""
    if not code:
        return None
    for kandidaat in _kandidaat_codes(code):
        if kandidaat in data:
            waarde = parse_bedrag(data[kandidaat])
            if waarde is not None:
                return waarde
    return None


def parse_csv(bestand):
    """Lees een CSV (pad, bytes, tekst of file-object) in als ``{code: waarde}``-dict."""
    if hasattr(bestand, "read"):
        inhoud = bestand.read()
    elif isinstance(bestand, (bytes, bytearray)):
        inhoud = bestand
    else:
        with open(bestand, "rb") as f:
            inhoud = f.read()

    if isinstance(inhoud, (bytes, bytearray)):
        for codec in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                inhoud = inhoud.decode(codec)
                break
            except UnicodeDecodeError:
                continue
        else:
            inhoud = inhoud.decode("utf-8", errors="replace")

    data = {}
    reader = csv.reader(io.StringIO(inhoud))
    for rij in reader:
        if not rij or len(rij) < 2:
            continue
        code = str(rij[0]).strip().strip('"').strip()
        waarde = str(rij[1]).strip().strip('"').strip()
        if code == "":
            continue
        data[code] = waarde
    return data


def build_metadata(data):
    """Bouw een nette lijst met identificatiegegevens van de vennootschap."""
    items = []
    gezien = set()
    for item in structuurMetadata:
        code = item["Code"]
        label = item["Rubriek"]
        if not label or code in gezien:
            continue
        if code in data and str(data[code]).strip():
            gezien.add(code)
            waarde = str(data[code]).strip()
            if waarde.upper() == "TRUE":
                waarde = "Ja"
            elif waarde.upper() == "FALSE":
                waarde = "Nee"
            items.append({"label": label, "waarde": waarde})
    return items


def _bedrijfsnaam(data):
    return (data.get("Entity name") or "").strip() or "Onbekende vennootschap"


def _format_kbo(nummer):
    cijfers = "".join(ch for ch in str(nummer or "") if ch.isdigit())
    if len(cijfers) == 10:
        return f"{cijfers[0:4]}.{cijfers[4:7]}.{cijfers[7:10]}"
    return nummer or ""


def _fiche(data):
    """Beknopte bedrijfsfiche (identiteit) voor bovenaan het overzicht."""
    adresdelen = [
        " ".join(p for p in ((data.get("Entity address street") or "").strip(),
                             (data.get("Entity address number") or "").strip()) if p),
        " ".join(p for p in ((data.get("Entity postal code") or "").strip(),
                             (data.get("Entity city") or "").strip()) if p),
        (data.get("Entity country") or "").strip(),
    ]
    adres = ", ".join(d for d in adresdelen if d)
    werknemers = lees_waarde(data, "9087")
    return {
        "naam": _bedrijfsnaam(data),
        "kbo": _format_kbo(data.get("Entity number")),
        "rechtsvorm": (data.get("Legal form") or "").strip(),
        "adres": adres,
        "boekjaar": _boekjaar(data),
        "munt": (data.get("Currency") or "EUR").strip() or "EUR",
        "werknemers": werknemers,
    }


def _boekjaar(data):
    start = (data.get("Accounting period start date") or "").strip()
    einde = (data.get("Accounting period end date") or "").strip()
    if start and einde:
        return f"{start} — {einde}"
    return einde or start or ""


def build_statement(structuur, data):
    """Zet een structuurlijst om naar weergaverijen met de bijhorende waarden."""
    rijen = []
    for item in structuur:
        code = item["Code"]
        waarde = lees_waarde(data, code) if code else None
        is_sectie = code == ""
        rijen.append(
            {
                "code": code,
                "rubriek": item["Rubriek"],
                "niveau": item.get("Niveau", 0),
                "toelichting": item.get("Toelichting", ""),
                "waarde": waarde,
                "is_sectie": is_sectie,
                "is_totaal": code in TOTAAL_CODES,
                "is_leeg": (waarde is None) and not is_sectie,
            }
        )
    return rijen


# --- Conformiteitscontrole tegen de wettelijke structuur -------------------

_EPS = 1.0  # tolerantie in euro voor afrondingsverschillen

# Elke controle: (naam, totaalcode, [(code, teken, verplicht), ...])
_BALANS_CONTROLES = [
    ("Totaal activa = oprichtingskosten + vaste activa + vlottende activa", "20/58",
     [("20", 1, False), ("21/28", 1, True), ("29/58", 1, True)]),
    ("Vaste activa = IVA + MVA + FVA", "21/28",
     [("21", 1, False), ("22/27", 1, False), ("28", 1, False)]),
    ("Vlottende activa = vord. >1j + voorraden + vord. \u22641j + geldbeleggingen + liquide middelen + overlopende rek.", "29/58",
     [("29", 1, False), ("3", 1, False), ("40/41", 1, False), ("50/53", 1, False),
      ("54/58", 1, False), ("490/1", 1, False)]),
    ("Totaal passiva = eigen vermogen + voorzieningen + schulden", "10/49",
     [("10/15", 1, True), ("16", 1, False), ("17/49", 1, True)]),
    ("Eigen vermogen = inbreng + herwaarderingsmw + reserves + overgedragen res. + kapitaalsubsidies + voorschot", "10/15",
     [("10/11", 1, False), ("12", 1, False), ("13", 1, False), ("14", 1, False),
      ("15", 1, False), ("19", 1, False)]),
    ("Schulden = schulden >1j + schulden \u22641j + overlopende rekeningen", "17/49",
     [("17", 1, False), ("42/48", 1, False), ("492/3", 1, False)]),
]

_RR_CONTROLES = [
    ("Bedrijfswinst (verlies) = bedrijfsopbrengsten \u2212 bedrijfskosten", "9901",
     [("7076A", 1, True), ("6066A", -1, True)]),
    ("Winst (verlies) vóór belasting = bedrijfsresultaat + financiële opbrengsten \u2212 financiële kosten", "9903",
     [("9901", 1, True), ("7576B", 1, True), ("6566B", -1, True)]),
    ("Winst (verlies) van het boekjaar = resultaat vóór belasting \u2212 belastingen", "9904",
     [("9903", 1, True), ("780", 1, False), ("680", -1, False), ("677/7", -1, True)]),
    ("Te bestemmen resultaat = resultaat boekjaar +/\u2212 belastingvrije reserves", "9905",
     [("9904", 1, True), ("789", 1, False), ("689", -1, False)]),
]


def _voer_controle_uit(naam, totaalcode, componenten, data):
    totaal = lees_waarde(data, totaalcode)
    if totaal is None:
        return None  # niets om tegen te controleren
    berekend = 0.0
    aanwezig = 0
    for code, teken, verplicht in componenten:
        waarde = lees_waarde(data, code)
        if waarde is None:
            if verplicht:
                return {"naam": naam, "status": "overgeslagen", "totaalcode": totaalcode,
                        "verwacht": totaal, "berekend": None, "verschil": None}
            waarde = 0.0
        else:
            aanwezig += 1
        berekend += teken * waarde
    # Geen enkele component aanwezig (bv. verkort model): niet te controleren.
    if aanwezig == 0:
        return {"naam": naam, "status": "overgeslagen", "totaalcode": totaalcode,
                "verwacht": totaal, "berekend": None, "verschil": None}
    verschil = totaal - berekend
    status = "ok" if abs(verschil) <= _EPS else "fout"
    return {"naam": naam, "status": status, "totaalcode": totaalcode,
            "verwacht": totaal, "berekend": berekend, "verschil": verschil}


def controleer_conformiteit(data):
    """Controleer de belangrijkste wettelijke optelsommen en het evenwicht van de balans."""
    balans_checks = []
    for naam, code, comps in _BALANS_CONTROLES:
        res = _voer_controle_uit(naam, code, comps, data)
        if res is not None:
            balans_checks.append(res)

    rr_checks = []
    for naam, code, comps in _RR_CONTROLES:
        res = _voer_controle_uit(naam, code, comps, data)
        if res is not None:
            rr_checks.append(res)

    activa = lees_waarde(data, "20/58")
    passiva = lees_waarde(data, "10/49")
    evenwicht = None
    if activa is not None and passiva is not None:
        verschil = activa - passiva
        evenwicht = {
            "activa": activa,
            "passiva": passiva,
            "verschil": verschil,
            "in_evenwicht": abs(verschil) <= _EPS,
        }

    alle = balans_checks + rr_checks
    aantal_fout = sum(1 for c in alle if c["status"] == "fout")
    aantal_ok = sum(1 for c in alle if c["status"] == "ok")
    conform = aantal_fout == 0 and (evenwicht is None or evenwicht["in_evenwicht"])

    return {
        "evenwicht": evenwicht,
        "balans_checks": balans_checks,
        "rr_checks": rr_checks,
        "aantal_ok": aantal_ok,
        "aantal_fout": aantal_fout,
        "conform": conform,
    }


def _herkende_codes():
    codes = set()
    for structuur in (structuurBalans, structuurResultatenRekening, structuurMetadata):
        for item in structuur:
            for kandidaat in _kandidaat_codes(item["Code"]):
                if kandidaat:
                    codes.add(kandidaat)
    return codes


def kerncijfers(data):
    """Enkele kerncijfers die rechtstreeks uit de balanstotalen af te leiden zijn."""
    cijfers = []
    vla = lees_waarde(data, "29/58")
    schulden_kt = lees_waarde(data, "42/48")
    ev = lees_waarde(data, "10/15")
    tv = lees_waarde(data, "10/49")

    if vla is not None and schulden_kt:
        cijfers.append({
            "label": "Liquiditeit in ruime zin",
            "waarde": round(vla / schulden_kt, 2),
            "eenheid": "x",
            "toelichting": "Vlottende activa (29/58) / schulden \u22641 jaar (42/48)",
        })
    if ev is not None and tv:
        cijfers.append({
            "label": "Solvabiliteit (eigen vermogen)",
            "waarde": round(100 * ev / tv, 1),
            "eenheid": "%",
            "toelichting": "Eigen vermogen (10/15) / totaal vermogen (10/49)",
        })
    if vla is not None and schulden_kt is not None:
        cijfers.append({
            "label": "Nettobedrijfskapitaal",
            "waarde": round(vla - schulden_kt, 2),
            "eenheid": "\u20ac",
            "toelichting": "Vlottende activa (29/58) \u2212 schulden \u22641 jaar (42/48)",
        })
    return cijfers


def analyseer(bestand):
    """Volledige analyse van één jaarrekening-CSV (pad, bytes of file-object)."""
    return analyseer_data(parse_csv(bestand))


def analyseer_data(data):
    """Volledige analyse op basis van een reeds ingelezen ``{code: waarde}``-dict.

    Zo kan dezelfde analyse gevoed worden vanuit CSV, JSON (jsonxbrl), PDF of
    de NBB-webservice.
    """
    from core.ratios import bereken_ratios  # lokale import om circulaire import te vermijden
    from core.risico import bereken_risico
    from core.falingsmodellen import bereken_falingsmodellen as _falingsmodellen
    from core.landen import verrijk_bestuurders
    from core.sectordata import REFERENTIE_BRON, REFERENTIE_PROFIEL

    herkende = _herkende_codes()
    # Gereserveerde sleutels (bv. __bestuurders__) tellen niet mee als rubriekcodes.
    codes_in_data = {c for c in data.keys() if not c.startswith("__")}
    aantal_herkend = len(codes_in_data & herkende)

    return {
        "bedrijfsnaam": _bedrijfsnaam(data),
        "boekjaar": _boekjaar(data),
        "munt": (data.get("Currency") or "EUR").strip() or "EUR",
        "metadata": build_metadata(data),
        "balans": build_statement(structuurBalans, data),
        "resultatenrekening": build_statement(structuurResultatenRekening, data),
        "controle": controleer_conformiteit(data),
        "kerncijfers": kerncijfers(data),
        "ratios": bereken_ratios(data),
        "risico": bereken_risico(data),
        "falingsmodellen": _falingsmodellen(data),
        "bestuurders": verrijk_bestuurders(data.get("__bestuurders__", [])),
        "fiche": _fiche(data),
        "sector_bron": REFERENTIE_BRON,
        "sector_profiel": REFERENTIE_PROFIEL,
        "aantal_codes": len(codes_in_data),
        "aantal_herkend": aantal_herkend,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Gebruik: python -m core.analyse <pad-naar-jaarrekening.csv>")
        raise SystemExit(1)
    resultaat = analyseer(sys.argv[1])
    controle = resultaat["controle"]
    ev = controle["evenwicht"]
    status = "in evenwicht" if ev and ev["in_evenwicht"] else "NIET in evenwicht"
    print(f"{resultaat['bedrijfsnaam']:30s} "
          f"{status:20s} ok={controle['aantal_ok']} fout={controle['aantal_fout']}")
