"""Ratio-evolutie over twee boekjaren met gunstig/ongunstig-oordeel (cf. DEEL2-sjabloon).

Berekent alle ratio's voor het huidige en het vorige boekjaar (uit dezelfde neerlegging,
kolom 'boekjaar' vs 'vorig boekjaar') en beoordeelt of de evolutie gunstig of ongunstig is,
volgens de regel of een hogere dan wel lagere waarde gunstig is.
"""

try:
    from core.ratios import bereken_ratios
except ModuleNotFoundError:
    from ratios import bereken_ratios

# Per ratio-id: is een hogere waarde gunstig? (None = neutraal, geen oordeel)
HOGER_IS_BETER = {
    "bruto_tw_marge": True, "tw_per_werknemer": True,
    "aandeel_personeel_btw": False, "aandeel_nietkas_tw": False, "aandeel_fkvv_btw": False,
    "aandeel_belastingen_btw": False, "aandeel_tw_wv_btw": False,
    "brutoverkoopmarge_voor_bel": True, "nettoverkoopmarge_voor_bel": True,
    "bruto_rend_ta": True, "netto_rend_ta": True,
    "netto_rend_ev_voor_bel": True, "netto_rend_ev_na_bel": True, "bruto_rend_ev_na_bel": True,
    "algemene_schuldgraad": False, "graad_fin_onafh": True, "zelffinancieringsgraad": True,
    "lt_schuldgraad": False, "lt_graad_fin_onafh": True, "netto_fin_schuldgraad": False,
    "dekking_fkvv_nettoresultaat": True, "dekking_vv_cashflow": True, "dekking_vvlt_cashflow": True,
    "current_ratio": True, "acid_test": True, "nettobedrijfskapitaal": True,
    "nbk_behoefte": None, "nettokas": True, "nettokasratio": True,
}


def _oordeel(huidig, vorig, hoger_is_beter):
    if huidig is None or vorig is None:
        return {"tekst": "—", "kleur": "neutral"}
    verschil = huidig - vorig
    if abs(verschil) < 1e-9:
        return {"tekst": "stabiel", "kleur": "neutral"}
    if hoger_is_beter is None:
        return {"tekst": "stijging" if verschil > 0 else "daling", "kleur": "neutral"}
    gunstig = (verschil > 0) == bool(hoger_is_beter)
    return {"tekst": "gunstige evolutie" if gunstig else "ongunstige evolutie",
            "kleur": "ok" if gunstig else "err"}


def bereken_evolutie(data, vorig):
    """Geef per ratiogroep de huidige/vorige waarde en het evolutie-oordeel terug."""
    if not vorig:
        return None
    huidig_res = bereken_ratios(data)
    vorig_index = {}
    for groep in bereken_ratios(vorig)["groepen"]:
        for r in groep["ratios"]:
            if r["berekenbaar"]:
                vorig_index[r["id"]] = r["waarde"]

    groepen = []
    aantal_gunstig = aantal_ongunstig = 0
    for groep in huidig_res["groepen"]:
        rijen = []
        for r in groep["ratios"]:
            hw = r["waarde"] if r["berekenbaar"] else None
            vw = vorig_index.get(r["id"])
            if hw is None and vw is None:
                continue
            hb = HOGER_IS_BETER.get(r["id"], True)
            oordeel = _oordeel(hw, vw, hb)
            if oordeel["kleur"] == "ok":
                aantal_gunstig += 1
            elif oordeel["kleur"] == "err":
                aantal_ongunstig += 1
            rijen.append({"naam": r["naam"], "eenheid": r["eenheid"],
                          "huidig": hw, "vorig": vw, "oordeel": oordeel})
        if rijen:
            groepen.append({"naam": groep["naam"], "ratios": rijen})

    return {"groepen": groepen, "aantal_gunstig": aantal_gunstig, "aantal_ongunstig": aantal_ongunstig}
