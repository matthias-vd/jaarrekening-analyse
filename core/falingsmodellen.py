"""Faalvoorspellingsmodellen uit de cursus: OV82, OJD91 en SIM05 (FiTo).

Bronnen/definities:
- OV82 (Ooghe-Verbaere 1982): lineair discriminantmodel. Het algemene model (1–3 jaar
  vóór faling) met de niet-gestandaardiseerde coëfficiënten en de ratio-formules (in
  NBB-codes) zoals gepubliceerd in Ooghe e.a. (EFMA 2006, appendix). Hogere score =
  gunstigere financiële toestand. Referentie-afkapgrens ~0,19 (validatiesteekproef).
- OJD91 (Ooghe-Joos-De Vos 1991): logistisch model. De coëfficiënten zijn NIET publiek
  (exclusieve licentie Graydon NV), dus de score kan hier niet betrouwbaar berekend
  worden — we tonen wél de gebruikte variabelen.
- SIM05 / FiTo-score (simpel-intuïtief model): coëfficiëntvrij. Elke ratio krijgt een
  teken (+ gunstig / − ongunstig), wordt logit-herschaald naar [0,1] en het gemiddelde
  is de score (0–1). Hoger = gezonder.

Alle uitkomsten zijn indicatief en vervangen geen kredietbeoordeling.
"""

import math

try:
    from core.analyse import lees_waarde
except ModuleNotFoundError:  # standalone
    from analyse import lees_waarde


def _g(data, code):
    waarde = lees_waarde(data, code)
    return 0.0 if waarde is None else waarde


def _deel(teller, noemer):
    if noemer is None or abs(noemer) < 1e-9:
        return None
    return teller / noemer


def _logit(ratio):
    """Logit-herschaling L = 1/(1+e^-R), met begrenzing tot [-10, 10]."""
    r = max(-10.0, min(10.0, ratio))
    return 1.0 / (1.0 + math.exp(-r))


def _logit_met_regel(teller, noemer, teken=1):
    """Logit van een getekende ratio; bij noemer <= 0 bepaalt de teller de waarde."""
    if noemer is None or noemer <= 0:
        if teller is None or teller == 0:
            return 0.5
        return 1.0 if (teller > 0) == (teken > 0) else 0.0
    return _logit(teken * (teller / noemer))


# --- OV82 -----------------------------------------------------------------

def _ov82(data):
    tp = lees_waarde(data, "10/49")
    if not tp:
        return None
    va_vlot = lees_waarde(data, "29/58")
    vord_1j = _g(data, "29")
    restricted = (va_vlot - vord_1j) if va_vlot is not None else None
    voorraad_werk = _g(data, "3") + _g(data, "40/41") + _g(data, "490/1")

    x1 = _deel(_g(data, "13") + _g(data, "14"), tp) or 0.0
    x2 = _deel(_g(data, "9072") + _g(data, "9076"), _g(data, "42/48") + _g(data, "492/3"))
    x2 = x2 if x2 is not None else 0.0
    x3 = _deel(_g(data, "54/58"), restricted) if restricted else 0.0
    x3 = x3 if x3 is not None else 0.0
    x4 = _deel(_g(data, "3"), voorraad_werk) if voorraad_werk else 0.0
    x4 = x4 if x4 is not None else 0.0
    x5 = _deel(_g(data, "430/8"), _g(data, "42/48") + _g(data, "492/3"))
    x5 = x5 if x5 is not None else 0.0

    score = 0.2324 + 4.3178 * x1 - 11.6782 * x2 + 3.1676 * x3 - 1.6200 * x4 - 0.8353 * x5
    afkap = 0.1904
    if score >= afkap:
        kleur, oordeel = "ok", "Lopend profiel (lager risico)"
    else:
        kleur, oordeel = "err", "Falingsprofiel (verhoogd risico)"
    return {
        "score": round(score, 3),
        "afkapgrens": afkap,
        "kleur": kleur,
        "oordeel": oordeel,
        "componenten": [
            {"naam": "X1 · ingehouden winst/reserves ÷ totaal passiva", "waarde": round(x1, 3)},
            {"naam": "X2 · vervallen belastingen/RSZ ÷ schulden ≤1j", "waarde": round(x2, 3)},
            {"naam": "X3 · liquide middelen ÷ beperkte vlottende activa", "waarde": round(x3, 3)},
            {"naam": "X4 · voorraden ÷ vlottende bedrijfsactiva", "waarde": round(x4, 3)},
            {"naam": "X5 · fin. schulden ≤1j (kredietinst.) ÷ schulden ≤1j", "waarde": round(x5, 3)},
        ],
    }


# --- SIM05 / FiTo ---------------------------------------------------------

def _fito(data):
    tp = lees_waarde(data, "10/49")
    ev = lees_waarde(data, "10/15")
    if not tp or ev is None:
        return None

    # Cashflow (benadering) en vreemd vermogen
    niet_kas = _g(data, "630") + _g(data, "631/4") + _g(data, "635/8")
    res_na_bel = lees_waarde(data, "9904")
    cashflow = (res_na_bel + niet_kas) if res_na_bel is not None else None
    vv = _g(data, "16") + _g(data, "17/49")

    va_vlot = lees_waarde(data, "29/58")
    vord_1j = _g(data, "29")
    beperkte_vla = (va_vlot - vord_1j) if va_vlot is not None else None
    fin_kt = _g(data, "43")
    nettokas_teller = _g(data, "50/53") + _g(data, "54/58") - fin_kt

    ratios = [
        ("Graad van zelffinanciering", _g(data, "13") + _g(data, "14"), tp, 1),
        ("Graad van financiële onafhankelijkheid", ev, tp, 1),
        ("KT financiële schuldgraad", _g(data, "430/8") or fin_kt, _g(data, "42/48"), -1),
        ("Dekking VV door de cashflow", cashflow if cashflow is not None else 0.0, vv, 1),
        ("Nettokasratio", nettokas_teller, beperkte_vla, 1),
    ]
    componenten, som = [], 0.0
    for naam, teller, noemer, teken in ratios:
        l = _logit_met_regel(teller, noemer, teken)
        som += l
        componenten.append({"naam": naam, "logit": round(l, 3)})
    score = som / len(ratios)
    if score >= 0.60:
        kleur, oordeel = "ok", "Gezond profiel"
    elif score >= 0.40:
        kleur, oordeel = "warn", "Aandacht"
    else:
        kleur, oordeel = "err", "Verhoogd risico"
    return {"score": round(score, 3), "kleur": kleur, "oordeel": oordeel, "componenten": componenten}


# --- OJD91 (variabelen, geen score) ---------------------------------------

_OJD91_VARIABELEN = [
    "Richting van het financieel hefboomeffect (netto rendabiliteit activa vóór bel. − gem. interestvoet)",
    "Ingehouden winst/reserves ÷ (totaal passiva − overlopende rekeningen)",
    "Liquide middelen + geldbeleggingen ÷ totaal activa",
    "Vervallen belastingen en RSZ-schulden (indicator > 0)",
    "Nettobedrijfskapitaalbehoefte-componenten ÷ totaal activa",
    "Netto rendabiliteit van de bedrijfsactiva vóór belasting",
    "Financiële schulden ≤1 jaar ÷ schulden ≤1 jaar",
    "Gewaarborgde schulden ÷ totaal schulden",
]


def _ojd91():
    return {
        "beschikbaar": False,
        "reden": ("De coëfficiënten van OJD91 zijn niet publiek beschikbaar "
                  "(exclusieve licentie Graydon NV), waardoor de score niet betrouwbaar "
                  "berekend kan worden. De gebruikte variabelen worden hieronder wel getoond."),
        "variabelen": _OJD91_VARIABELEN,
    }


def bereken_falingsmodellen(data):
    return {"ov82": _ov82(data), "fito": _fito(data), "ojd91": _ojd91()}
