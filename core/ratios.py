"""Ratioanalyse van een jaarrekening volgens de cursus 'Financiële Analyse van de Onderneming'.

Berekent — voor zover afleidbaar uit de balans en de resultatenrekening — de ratio's
uit de vier groepen: toegevoegde waarde, rendabiliteit, solvabiliteit en liquiditeit.
Waar een exacte berekening extra toelichtingsdata of meerdere boekjaren vereist,
wordt de ratio gemarkeerd als niet-berekenbaar met de reden, of als 'benadering'
wanneer niet-kaskosten/financiële kosten benaderd worden uit de beschikbare rubrieken.
"""

try:
    from core.analyse import lees_waarde
    from core.sectordata import positie as sector_positie
except ModuleNotFoundError:  # standalone vanuit map core/
    from analyse import lees_waarde
    from sectordata import positie as sector_positie


def _g(data, code):
    """Waarde van een code, of 0.0 als ze ontbreekt (voor optelsommen)."""
    waarde = lees_waarde(data, code)
    return 0.0 if waarde is None else waarde


def _heeft(data, code):
    return lees_waarde(data, code) is not None


def _deel(teller, noemer):
    if teller is None or not noemer:
        return None
    return teller / noemer


def _ratio(rid, naam, formule, eenheid, waarde, methode="exact"):
    return {
        "id": rid,
        "naam": naam,
        "formule": formule,
        "eenheid": eenheid,
        "waarde": waarde,
        "methode": methode,
        "berekenbaar": waarde is not None,
        "reden": None,
        "sector": sector_positie(waarde, rid),
    }


def _na(rid, naam, formule, eenheid, reden):
    return {
        "id": rid,
        "naam": naam,
        "formule": formule,
        "eenheid": eenheid,
        "waarde": None,
        "methode": "n.v.t.",
        "berekenbaar": False,
        "reden": reden,
        "sector": None,
    }


def bereken_ratios(data):
    """Bouw de vier ratiogroepen op basis van de ingelezen jaarrekeningdata."""

    # --- Afgeleide grootheden -------------------------------------------
    TV = lees_waarde(data, "20/58")          # totaal activa
    TP = lees_waarde(data, "10/49")          # totaal passiva (= TV)
    EV = lees_waarde(data, "10/15")          # eigen vermogen
    tv = TV if TV is not None else TP
    vv = (tv - EV) if (tv is not None and EV is not None) else None  # vreemd vermogen

    VVLT = _g(data, "16") + _g(data, "17")   # voorzieningen + schulden > 1 jaar
    VVKT = _g(data, "42/48") + _g(data, "492/3")  # schulden <= 1 jaar + overl. rek.
    PV = (EV + VVLT) if EV is not None else None  # permanent vermogen

    reserves = _g(data, "13")
    overgedragen = _g(data, "14")

    afschrijvingen = _g(data, "630")
    wv_voorraden = _g(data, "631/4")
    voorzieningen_rr = _g(data, "635/8")
    niet_kaskosten = afschrijvingen + wv_voorraden + voorzieningen_rr  # benadering

    res_voor_bel = lees_waarde(data, "9903")
    res_na_bel = lees_waarde(data, "9904")

    # Financiële kosten van het vreemd vermogen (kosten van schulden 650, anders 65)
    if _heeft(data, "650"):
        fkvv = _g(data, "650")
    else:
        fkvv = _g(data, "65")

    cashflow = (res_na_bel + niet_kaskosten) if res_na_bel is not None else None
    ebit = (res_voor_bel + fkvv) if res_voor_bel is not None else None

    omzet = lees_waarde(data, "70")
    bedrijfsopbr = lees_waarde(data, "7076A")
    if _heeft(data, "60/61"):
        interm_verbruik = _g(data, "60/61")
    else:
        interm_verbruik = _g(data, "60") + _g(data, "61")
    bruto_tw = (bedrijfsopbr - interm_verbruik) if bedrijfsopbr is not None else None
    personeel = _g(data, "62")
    belastingen = _g(data, "67/77")
    werknemers = lees_waarde(data, "9087")   # gemiddeld personeelsbestand (VTE)

    VA = lees_waarde(data, "29/58")          # vlottende activa
    vord_kt = _g(data, "40/41")
    geldbel = _g(data, "50/53")
    lm = _g(data, "54/58")
    fin_schulden_kt = _g(data, "43")
    fin_schulden_lt = _g(data, "170/4") if _heeft(data, "170/4") else _g(data, "17")
    netto_fin_vv = (fin_schulden_lt + fin_schulden_kt) - (geldbel + lm)

    nbk = (VA - VVKT) if VA is not None else None
    vlottende_bedrijfsactiva = (VA - geldbel - lm) if VA is not None else None
    operationeel_vvkt = VVKT - fin_schulden_kt
    nbk_behoefte = (vlottende_bedrijfsactiva - operationeel_vvkt) if vlottende_bedrijfsactiva is not None else None
    nettokas = (geldbel + lm) - fin_schulden_kt

    rotatie_reden = "Vereist toelichtingsdata (BTW, aankopen, begin-/eindwaarden) en/of twee boekjaren."

    # --- Toegevoegde waarde ---------------------------------------------
    tw = []
    if bruto_tw is not None and bedrijfsopbr:
        tw.append(_ratio("bruto_tw_marge", "Bruto toegevoegde waardemarge",
                         "bruto TW / bedrijfsopbrengsten", "%",
                         _deel(bruto_tw, bedrijfsopbr) * 100 if bedrijfsopbr else None))
    else:
        tw.append(_na("bruto_tw_marge", "Bruto toegevoegde waardemarge",
                      "bruto TW / bedrijfsopbrengsten", "%",
                      "Bedrijfsopbrengsten (70/76A) niet aanwezig in de CSV."))

    if bruto_tw is not None and werknemers:
        tw.append(_ratio("tw_per_werknemer", "Bruto toegevoegde waarde per werknemer",
                         "bruto TW / gemiddeld personeelsbestand (9087)", "000 EUR",
                         _deel(bruto_tw / 1000.0, werknemers)))
    else:
        tw.append(_na("tw_per_werknemer", "Bruto toegevoegde waarde per werknemer",
                      "bruto TW / gemiddeld personeelsbestand (9087)", "000 EUR",
                      "Bruto TW of personeelsbestand (9087) niet beschikbaar."))

    if bruto_tw:
        tw.append(_ratio("aandeel_personeel_btw", "Aandeel van het personeel in de BTW",
                         "bezoldigingen (62) / bruto TW", "%", _deel(personeel, bruto_tw) * 100))
        tw.append(_ratio("aandeel_nietkas_tw", "Aandeel recurrente niet-kaskosten in de TW",
                         "afschrijvingen + waardeverm. + voorz. (630+631/4+635/8) / bruto TW", "%",
                         _deel(niet_kaskosten, bruto_tw) * 100, methode="benadering"))
        tw.append(_ratio("aandeel_fkvv_btw", "Aandeel van de FKVV in de BTW",
                         "financiële kosten VV / bruto TW", "%",
                         _deel(fkvv, bruto_tw) * 100, methode="benadering"))
        tw.append(_ratio("aandeel_belastingen_btw", "Aandeel van de belastingen in de BTW",
                         "belastingen (67/77) / bruto TW", "%", _deel(belastingen, bruto_tw) * 100))
        toegevoegde_wv = bruto_tw - personeel - niet_kaskosten - fkvv - belastingen
        tw.append(_ratio("aandeel_tw_wv_btw", "Aandeel van de toegevoegde winst/verlies in de BTW",
                         "(bruto TW − personeel − niet-kaskosten − FKVV − belastingen) / bruto TW", "%",
                         _deel(toegevoegde_wv, bruto_tw) * 100, methode="benadering"))
    else:
        for rid, naam in [("aandeel_personeel_btw", "Aandeel van het personeel in de BTW"),
                          ("aandeel_nietkas_tw", "Aandeel recurrente niet-kaskosten in de TW"),
                          ("aandeel_fkvv_btw", "Aandeel van de FKVV in de BTW"),
                          ("aandeel_belastingen_btw", "Aandeel van de belastingen in de BTW"),
                          ("aandeel_tw_wv_btw", "Aandeel van de toegevoegde winst/verlies in de BTW")]:
            tw.append(_na(rid, naam, "aandeel in bruto TW", "%",
                          "Bruto TW niet berekenbaar (bedrijfsopbrengsten/inkopen ontbreken)."))

    # --- Rendabiliteit --------------------------------------------------
    rend = []
    if omzet:
        rend.append(_ratio("brutoverkoopmarge_voor_bel", "Brutoverkoopmarge vóór belastingen",
                           "(resultaat vóór bel. + FKVV + niet-kaskosten) / omzet", "%",
                           _deel((res_voor_bel or 0) + fkvv + niet_kaskosten, omzet) * 100,
                           methode="benadering"))
        rend.append(_ratio("nettoverkoopmarge_voor_bel", "Nettoverkoopmarge vóór belastingen",
                           "(resultaat vóór bel. + FKVV) / omzet", "%",
                           _deel((res_voor_bel or 0) + fkvv, omzet) * 100, methode="benadering"))
    else:
        rend.append(_na("brutoverkoopmarge_voor_bel", "Brutoverkoopmarge vóór belastingen",
                        "(resultaat vóór bel. + FKVV + niet-kaskosten) / omzet", "%",
                        "Omzet (70) niet afzonderlijk gerapporteerd in de CSV."))
        rend.append(_na("nettoverkoopmarge_voor_bel", "Nettoverkoopmarge vóór belastingen",
                        "(resultaat vóór bel. + FKVV) / omzet", "%",
                        "Omzet (70) niet afzonderlijk gerapporteerd in de CSV."))

    if tv:
        rend.append(_ratio("bruto_rend_ta", "Brutorendabiliteit van het totaal van de activa",
                           "(resultaat vóór bel. + FKVV + niet-kaskosten) / totaal activa", "%",
                           _deel((res_voor_bel or 0) + fkvv + niet_kaskosten, tv) * 100, methode="benadering"))
        rend.append(_ratio("netto_rend_ta", "Nettorendabiliteit van het totaal van de activa",
                           "(resultaat vóór bel. + FKVV) / totaal activa", "%",
                           _deel((res_voor_bel or 0) + fkvv, tv) * 100, methode="benadering"))
    if EV:
        rend.append(_ratio("netto_rend_ev_voor_bel", "Nettorendabiliteit van het EV vóór belastingen",
                           "resultaat vóór bel. (9903) / eigen vermogen", "%",
                           _deel(res_voor_bel, EV) * 100))
        rend.append(_ratio("netto_rend_ev_na_bel", "Nettorendabiliteit van het EV na belastingen",
                           "resultaat na bel. (9904) / eigen vermogen", "%",
                           _deel(res_na_bel, EV) * 100))
        rend.append(_ratio("bruto_rend_ev_na_bel", "Brutorendabiliteit van het EV na belastingen",
                           "(resultaat na bel. + niet-kaskosten) / eigen vermogen", "%",
                           _deel((res_na_bel or 0) + niet_kaskosten, EV) * 100, methode="benadering"))
    else:
        rend.append(_na("netto_rend_ev_na_bel", "Nettorendabiliteit van het EV na belastingen",
                        "resultaat na bel. / eigen vermogen", "%", "Eigen vermogen (10/15) ontbreekt of is nul."))

    # --- Solvabiliteit --------------------------------------------------
    solv = []
    if tv:
        solv.append(_ratio("algemene_schuldgraad", "Algemene schuldgraad",
                           "vreemd vermogen / totaal vermogen", "%", _deel(vv, tv) * 100))
        solv.append(_ratio("graad_fin_onafh", "Algemene graad van financiële onafhankelijkheid",
                           "eigen vermogen / totaal vermogen", "%", _deel(EV, tv) * 100))
        solv.append(_ratio("zelffinancieringsgraad", "Zelffinancieringsgraad",
                           "(reserves + overgedragen resultaat) / totaal vermogen", "%",
                           _deel(reserves + overgedragen, tv) * 100))
    if PV:
        solv.append(_ratio("lt_schuldgraad", "Langetermijnschuldgraad",
                           "VV op lange termijn / permanent vermogen", "%", _deel(VVLT, PV) * 100))
        solv.append(_ratio("lt_graad_fin_onafh", "Langetermijngraad van financiële onafhankelijkheid",
                           "eigen vermogen / permanent vermogen", "%", _deel(EV, PV) * 100))
    if EV:
        solv.append(_ratio("netto_fin_schuldgraad", "Netto financiële schuldgraad",
                           "netto financieel VV / eigen vermogen", "x",
                           _deel(netto_fin_vv, EV), methode="benadering"))
    if fkvv:
        solv.append(_ratio("dekking_fkvv_nettoresultaat", "Dekking van de FKVV door het nettoresultaat",
                           "EBIT (resultaat vóór bel. + FKVV) / FKVV", "x",
                           _deel(ebit, fkvv), methode="benadering"))
    if vv:
        solv.append(_ratio("dekking_vv_cashflow", "Dekking van het totaal VV door de cashflow",
                           "cashflow van het EV na bel. / totaal VV", "%",
                           _deel(cashflow, vv) * 100, methode="benadering"))
    if VVLT:
        solv.append(_ratio("dekking_vvlt_cashflow", "Dekking van het VVLT door de cashflow",
                           "cashflow van het EV na bel. / VV op lange termijn", "%",
                           _deel(cashflow, VVLT) * 100, methode="benadering"))

    # --- Liquiditeit ----------------------------------------------------
    liq = []
    if VVKT:
        liq.append(_ratio("current_ratio", "Liquiditeitsratio in ruime zin (current ratio)",
                          "vlottende activa (29/58) / VV op korte termijn", "x", _deel(VA, VVKT)))
        liq.append(_ratio("acid_test", "Liquiditeitsratio in enge zin (acid test)",
                          "(vord. ≤1j + geldbeleggingen + liquide middelen) / VVKT", "x",
                          _deel(vord_kt + geldbel + lm, VVKT)))
    liq.append(_ratio("nettobedrijfskapitaal", "Nettobedrijfskapitaal",
                      "vlottende activa − VV op korte termijn", "EUR", nbk))
    liq.append(_ratio("nbk_behoefte", "Nettobedrijfskapitaalbehoefte",
                      "vlottende bedrijfsactiva − operationeel VVKT", "EUR", nbk_behoefte, methode="benadering"))
    liq.append(_ratio("nettokas", "Nettokas",
                      "(geldbeleggingen + liquide middelen) − financieel VVKT", "EUR", nettokas, methode="benadering"))
    if VA:
        liq.append(_ratio("nettokasratio", "Nettokasratio",
                          "nettokas / (beperkte) vlottende activa", "%",
                          _deel(nettokas, VA) * 100, methode="benadering"))
    liq.append(_na("rotatie_voorraden", "Rotatie van de voorraden en BIU", "kostprijs verkopen / gem. voorraad", "x", rotatie_reden))
    liq.append(_na("rotatie_handelsvorderingen", "Rotatie van de handelsvorderingen", "(verkopen + btw) / handelsvorderingen", "x", rotatie_reden))
    liq.append(_na("rotatie_handelsschulden", "Rotatie van de handelsschulden", "(inkopen + btw) / handelsschulden", "x", rotatie_reden))
    liq.append(_na("dagen_klantenkrediet", "Dagen klantenkrediet", "365 / rotatie handelsvorderingen", "dagen", rotatie_reden))
    liq.append(_na("dagen_leverancierskrediet", "Dagen leverancierskrediet", "365 / rotatie handelsschulden", "dagen", rotatie_reden))

    groepen = [
        {"naam": "Toegevoegde waarde", "ratios": tw},
        {"naam": "Rendabiliteit", "ratios": rend},
        {"naam": "Solvabiliteit", "ratios": solv},
        {"naam": "Liquiditeit", "ratios": liq},
    ]

    berekend = sum(1 for g in groepen for r in g["ratios"] if r["berekenbaar"])
    totaal = sum(len(g["ratios"]) for g in groepen)
    met_sector = sum(1 for g in groepen for r in g["ratios"] if r.get("sector"))

    return {
        "groepen": groepen,
        "aantal_berekend": berekend,
        "aantal_totaal": totaal,
        "aantal_met_sector": met_sector,
        "werknemers": werknemers,
    }


if __name__ == "__main__":
    import os
    try:
        from core.analyse import parse_csv
    except ModuleNotFoundError:
        from analyse import parse_csv

    map_uploads = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    for naam in sorted(os.listdir(map_uploads)):
        if not naam.endswith(".csv"):
            continue
        data = parse_csv(os.path.join(map_uploads, naam))
        res = bereken_ratios(data)
        print(f"\n=== {naam} (werknemers={res['werknemers']}) "
              f"berekend {res['aantal_berekend']}/{res['aantal_totaal']}, "
              f"met sector {res['aantal_met_sector']} ===")
        for groep in res["groepen"]:
            for r in groep["ratios"]:
                if r["berekenbaar"]:
                    s = r["sector"]
                    pos = f"  [sector {s['positie']}: {s['oordeel']}]" if s else ""
                    print(f"  {groep['naam'][:4]:4s} {r['naam'][:48]:48s} "
                          f"{r['waarde']:>12.2f} {r['eenheid']:<7}{pos}")
