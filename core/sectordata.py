"""Sectorreferentie voor de ratio-analyse.

De Nationale Bank van België (Balanscentrale) publiceert via NBB.Stat per
NACE-BEL-sector de spreiding van financiële ratio's in kwartielen (Q1/Q2/Q3).
Een gedeponeerde jaarrekening-CSV bevat echter geen NACE-code, waardoor de sector
niet automatisch afgeleid kan worden — die moet gekozen of opgezocht worden.

Onderstaande kwartielen zijn de illustratieve referentiewaarden uit de cursus
"Financiële Analyse van de Onderneming" (overzichtstabellen, sectorkwartielen 20X3).
Ze dienen als aanwijsbaar referentieprofiel; echte, actuele sectorcijfers haal je
per NACE-code op bij de NBB Balanscentrale (www.nbb.be > Balanscentrale > NBB.Stat).
"""

REFERENTIE_BRON = (
    "Illustratieve NBB-kwartielen (cursus FAO, sectorkwartielen 20X3). "
    "Actuele sectorcijfers: NBB Balanscentrale via NBB.Stat, per NACE-BEL-code."
)
REFERENTIE_PROFIEL = "Algemeen referentieprofiel (voorbeeld)"

# ratio_id -> (Q1, Q2 (mediaan), Q3, hoger_is_beter)
#   hoger_is_beter = True  -> hoger dan de sector is gunstig
#   hoger_is_beter = False -> lager dan de sector is gunstig
#   hoger_is_beter = None  -> neutraal (enkel positionering, geen oordeel)
BENCHMARKS = {
    # Toegevoegde waarde
    "bruto_tw_marge": (13.9, 23.8, 35.7, True),
    "tw_per_werknemer": (62.9, 83.1, 123.8, True),
    "aandeel_personeel_btw": (44.9, 61.9, 76.4, False),
    "aandeel_nietkas_tw": (10.0, 15.0, 23.7, False),
    "aandeel_fkvv_btw": (0.6, 2.2, 5.8, False),

    # Rendabiliteit
    "brutoverkoopmarge_voor_bel": (3.4, 7.3, 13.2, True),
    "nettoverkoopmarge_voor_bel": (0.9, 3.0, 7.6, True),
    "bruto_rend_ta": (5.4, 11.2, 17.5, True),
    "netto_rend_ta": (1.6, 4.6, 10.7, True),
    "netto_rend_ev_na_bel": (1.8, 7.8, 17.7, True),
    "bruto_rend_ev_na_bel": (10.0, 22.7, 39.5, True),

    # Solvabiliteit
    "graad_fin_onafh": (22.2, 40.8, 63.0, True),

    # Liquiditeit
    "current_ratio": (0.93, 1.36, 2.21, True),
    "acid_test": (0.63, 1.05, 1.82, True),
    "dagen_klantenkrediet": (28, 45, 60, False),
    "dagen_leverancierskrediet": (32, 50, 71, None),
}


def positie(waarde, ratio_id):
    """Bepaal waar een ratiowaarde valt t.o.v. de sectorkwartielen.

    Geeft ``None`` terug als er geen benchmark of geen waarde is.
    """
    if waarde is None or ratio_id not in BENCHMARKS:
        return None
    q1, q2, q3, hoger_is_beter = BENCHMARKS[ratio_id]

    if waarde < q1:
        band = 0
    elif waarde < q2:
        band = 1
    elif waarde < q3:
        band = 2
    else:
        band = 3

    posities = ["< Q1", "Q1–Q2", "Q2–Q3", "> Q3"]

    if hoger_is_beter is True:
        oordelen = ["zwak", "onder mediaan", "boven mediaan", "sterk"]
        kleuren = ["err", "warn", "ok", "ok"]
    elif hoger_is_beter is False:
        oordelen = ["sterk", "boven mediaan", "onder mediaan", "zwak"]
        kleuren = ["ok", "ok", "warn", "err"]
    else:
        oordelen = ["laag", "eerder laag", "eerder hoog", "hoog"]
        kleuren = ["neutral", "neutral", "neutral", "neutral"]

    return {
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "band": band,
        "positie": posities[band],
        "oordeel": oordelen[band],
        "kleur": kleuren[band],
        "hoger_is_beter": hoger_is_beter,
    }
