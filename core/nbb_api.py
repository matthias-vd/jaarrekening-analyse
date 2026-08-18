"""Jaarrekeningen automatisch ophalen bij de NBB op basis van een KBO-/BTW-nummer.

Gebruikt de gratis webservice "Authentic Data Query" van de Balanscentrale van de
Nationale Bank van België (NBB Central Balance Sheet Office):

1. ``GET /authentic/legalEntity/{kbo}/references``  -> lijst van neerleggingen
2. ``GET /authentic/deposit/{ref}/accountingData``  (Accept: application/x.jsonxbrl)
   -> gestructureerde JSON met rubriekcodes en bedragen

De webservice is gratis, maar vereist een (gratis) registratie op
https://developer.cbso.nbb.be en een abonnementssleutel. Zet die sleutel als
omgevingsvariabele ``NBB_CBSO_SUBSCRIPTION_KEY`` (bv. via de Secrets van de omgeving).
"""

import json
import os
import re
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from core.bronnen import BronFout, parse_jsonxbrl
except ModuleNotFoundError:  # standalone vanuit map core/
    from bronnen import BronFout, parse_jsonxbrl

BASIS_URL = "https://ws.cbso.nbb.be/authentic"
SLEUTEL_ENV = "NBB_CBSO_SUBSCRIPTION_KEY"


def normaliseer_kbo(nummer):
    """Maak een KBO-/BTW-nummer schoon tot 10 cifers (bv. 'BE 0403.101.811' -> '0403101811')."""
    if not nummer:
        return None
    cijfers = re.sub(r"\D", "", str(nummer))
    if len(cijfers) == 9:
        cijfers = "0" + cijfers  # ondernemingsnummers beginnen met een 0
    if len(cijfers) != 10:
        return None
    return cijfers


def _get(url, sleutel, accept):
    req = Request(url, headers={
        "NBB-CBSO-Subscription-Key": sleutel,
        "X-Request-Id": str(uuid.uuid4()),
        "Accept": accept,
    })
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read()
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise BronFout(
                "De NBB-abonnementssleutel ontbreekt of is ongeldig. Registreer gratis op "
                "developer.cbso.nbb.be en zet de sleutel als NBB_CBSO_SUBSCRIPTION_KEY."
            ) from exc
        if exc.code == 404:
            raise BronFout("Geen (publiceerbare) jaarrekening gevonden voor dit nummer.") from exc
        raise BronFout(f"De NBB-webservice gaf een fout (HTTP {exc.code}).") from exc
    except URLError as exc:
        raise BronFout("Kon de NBB-webservice niet bereiken.") from exc


def _kies_recentste_referentie(referenties):
    """Kies de recentste neerlegging en geef (referentienummer, extra_meta) terug."""
    items = referenties
    if isinstance(referenties, dict):
        for sleutel in ("References", "references", "items", "data"):
            if isinstance(referenties.get(sleutel), list):
                items = referenties[sleutel]
                break
        else:
            items = [referenties]
    if not isinstance(items, list) or not items:
        raise BronFout("Geen jaarrekeningen gevonden voor dit KBO-/BTW-nummer.")

    def ref_nummer(item):
        for sleutel in ("ReferenceNumber", "Reference", "referenceNumber", "reference"):
            if item.get(sleutel):
                return str(item[sleutel])
        return None

    def sorteer_datum(item):
        for sleutel in ("DepositDate", "depositDate", "ExerciseEndDate",
                        "PeriodEndDate", "endDate", "EndDate", "Date"):
            if item.get(sleutel):
                return str(item[sleutel])
        return ""

    geldig = [it for it in items if isinstance(it, dict) and ref_nummer(it)]
    if not geldig:
        raise BronFout("Geen bruikbare neerleggingsreferentie gevonden.")
    beste = sorted(geldig, key=sorteer_datum, reverse=True)[0]

    extra = {}
    for bron_sleutel, doel in (("StartDate", "Accounting period start date"),
                               ("ExerciseStartDate", "Accounting period start date"),
                               ("startDate", "Accounting period start date"),
                               ("EndDate", "Accounting period end date"),
                               ("ExerciseEndDate", "Accounting period end date"),
                               ("endDate", "Accounting period end date")):
        if beste.get(bron_sleutel) and doel not in extra:
            extra[doel] = beste[bron_sleutel]
    return ref_nummer(beste), extra


def haal_op_via_kbo(nummer, sleutel=None):
    """Haal de recentste jaarrekening op en geef een ``{code: waarde}``-dict terug."""
    sleutel = sleutel or os.environ.get(SLEUTEL_ENV)
    if not sleutel:
        raise BronFout(
            "Automatisch ophalen is nog niet geconfigureerd: er is geen NBB-abonnementssleutel. "
            "Registreer gratis op developer.cbso.nbb.be en zet de sleutel als NBB_CBSO_SUBSCRIPTION_KEY."
        )

    kbo = normaliseer_kbo(nummer)
    if not kbo:
        raise BronFout("Ongeldig KBO-/BTW-nummer. Geef 10 cijfers in (bv. 0403.101.811).")

    ruwe_refs = _get(f"{BASIS_URL}/legalEntity/{kbo}/references", sleutel, "application/json")
    try:
        referenties = json.loads(ruwe_refs.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise BronFout("Onverwacht antwoord van de NBB bij het opvragen van de referenties.") from exc

    ref, extra_meta = _kies_recentste_referentie(referenties)
    ruwe_data = _get(f"{BASIS_URL}/deposit/{ref}/accountingData", sleutel, "application/x.jsonxbrl")
    return parse_jsonxbrl(ruwe_data, extra_meta=extra_meta)
