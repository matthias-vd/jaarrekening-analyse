"""Landherkenning (naam -> ISO-landcode -> vlagemoji) en verrijking van bestuurders.

Wordt gebruikt om in de bestuurderstab een vlaggetje van het land van herkomst te
tonen en om niet langer actieve mandaten te markeren.
"""

from datetime import date

# Landnaam (NL/FR/EN, kleine letters) -> ISO 3166-1 alpha-2
_NAAR_ISO = {
    "belgië": "BE", "belgie": "BE", "belgique": "BE", "belgium": "BE",
    "nederland": "NL", "pays-bas": "NL", "netherlands": "NL",
    "frankrijk": "FR", "france": "FR",
    "duitsland": "DE", "allemagne": "DE", "germany": "DE", "deutschland": "DE",
    "luxemburg": "LU", "luxembourg": "LU",
    "verenigd koninkrijk": "GB", "royaume-uni": "GB", "united kingdom": "GB",
    "groot-brittannië": "GB", "great britain": "GB",
    "ierland": "IE", "ireland": "IE", "irlande": "IE",
    "spanje": "ES", "espagne": "ES", "spain": "ES", "españa": "ES",
    "italië": "IT", "italie": "IT", "italy": "IT", "italia": "IT",
    "portugal": "PT",
    "zwitserland": "CH", "suisse": "CH", "switzerland": "CH",
    "oostenrijk": "AT", "autriche": "AT", "austria": "AT",
    "denemarken": "DK", "danemark": "DK", "denmark": "DK",
    "zweden": "SE", "suède": "SE", "sweden": "SE",
    "noorwegen": "NO", "norvège": "NO", "norway": "NO",
    "finland": "FI", "finlande": "FI",
    "polen": "PL", "pologne": "PL", "poland": "PL",
    "thailand": "TH", "thaïlande": "TH", "thailande": "TH",
    "verenigde staten": "US", "états-unis": "US", "etats-unis": "US",
    "united states": "US", "usa": "US", "verenigde staten van amerika": "US",
    "canada": "CA",
    "china": "CN", "chine": "CN",
    "japan": "JP", "japon": "JP",
    "verenigde arabische emiraten": "AE", "united arab emirates": "AE",
    "hong kong": "HK",
    "turkije": "TR", "turquie": "TR", "turkey": "TR",
    "rusland": "RU", "russie": "RU", "russia": "RU",
    "india": "IN", "inde": "IN",
    "brazilië": "BR", "brésil": "BR", "brazil": "BR",
    "australië": "AU", "australie": "AU", "australia": "AU",
    "zuid-afrika": "ZA", "afrique du sud": "ZA", "south africa": "ZA",
    "china (volksrepubliek)": "CN",
}


def iso_naar_vlag(iso):
    """Zet een ISO-2-landcode om naar een vlagemoji (regionale indicatoren)."""
    if not iso or len(iso) != 2:
        return ""
    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in iso.upper())


def land_en_vlag(adres, land=None):
    """Bepaal (landnaam, vlagemoji) uit een expliciet land of het einde van een adres."""
    kandidaat = (land or "").strip()
    if not kandidaat and adres:
        kandidaat = adres.split(",")[-1].strip()
    iso = _NAAR_ISO.get(kandidaat.lower()) if kandidaat else None
    return kandidaat, iso_naar_vlag(iso) if iso else ""


def _is_actief(mandaat_einde):
    einde = (mandaat_einde or "").strip()
    if not einde:
        return True
    try:
        jaar, maand, dag = (int(x) for x in einde.split("-")[:3])
        return date(jaar, maand, dag) >= date.today()
    except (ValueError, TypeError):
        return True


def verrijk_bestuurders(bestuurders):
    """Voeg landnaam, vlag en actief-status toe aan elke bestuurder."""
    verrijkt = []
    for b in bestuurders or []:
        land, vlag = land_en_vlag(b.get("adres", ""), b.get("land"))
        item = dict(b)
        item["land"] = land
        item["vlag"] = vlag
        item["actief"] = _is_actief(b.get("mandaat_einde"))
        verrijkt.append(item)
    return verrijkt
