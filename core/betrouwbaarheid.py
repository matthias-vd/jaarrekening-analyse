"""Betrouwbaarheid van de jaarrekening: auditoroordeel, resultaatsturing-indicatoren
en de Beneish M-score.

- Auditoroordeel: leest uit de PDF-tekst van het commissarisverslag of het een oordeel
  zonder voorbehoud, met voorbehoud, afkeurend of een oordeelonthouding betreft, en of er
  een toelichtende paragraaf / continuïteitsonzekerheid (going concern) is.
- Resultaatsturing: enkele indicatoren (red flags) die kunnen wijzen op winststuring.
- Beneish M-score: academisch model dat de kans op winstmanipulatie inschat (2 boekjaren).

Alles is indicatief en vervangt geen audit of forensisch onderzoek.
"""

try:
    from core.analyse import lees_waarde
except ModuleNotFoundError:
    from analyse import lees_waarde


def auditoroordeel_uit_tekst(tekst):
    """Detecteer het commissaris-/auditoroordeel uit de (PDF-)tekst."""
    low = tekst.lower()
    heeft_verslag = ("verslag van de commissaris" in low or "commissarisverslag" in low
                     or "verslag van de bedrijfsrevisor" in low)

    oordeel, kleur = None, "neutral"
    if "afkeurend oordeel" in low:
        oordeel, kleur = "Afkeurend oordeel", "err"
    elif ("oordeelonthouding" in low or "onthoudende verklaring" in low
          or "geen oordeel tot uitdrukking" in low):
        oordeel, kleur = "Oordeelonthouding", "err"
    elif "oordeel met voorbehoud" in low or "verklaring met voorbehoud" in low:
        oordeel, kleur = "Oordeel met voorbehoud", "warn"
    elif "oordeel zonder voorbehoud" in low or "verklaring zonder voorbehoud" in low or "zonder voorbehoud" in low:
        oordeel, kleur = "Oordeel zonder voorbehoud", "ok"
    elif heeft_verslag and "getrouw beeld" in low:
        oordeel, kleur = "Oordeel zonder voorbehoud", "ok"

    if not heeft_verslag and oordeel is None:
        return None

    emphasis = ("vestigen wij de aandacht" in low or "toelichtende paragraaf" in low
                or "benadrukking van bepaalde aangelegenheden" in low)
    going_concern = (("continu" in low or "going concern" in low)
                     and ("onzekerheid van materieel belang" in low or "in het gedrang" in low
                          or "gerede twijfel" in low or "materiële onzekerheid" in low))
    return {"heeft_verslag": heeft_verslag, "oordeel": oordeel, "kleur": kleur,
            "emphasis": emphasis, "going_concern": going_concern}


def _g(data, code):
    w = lees_waarde(data, code)
    return 0.0 if w is None else w


def _resultaatsturing(data, vorig, controle):
    ind = []
    ta = lees_waarde(data, "20/58")
    res = lees_waarde(data, "9904")          # winst na belasting
    res_vb = lees_waarde(data, "9903")       # winst vóór belasting
    omzet = lees_waarde(data, "70")
    afschr = _g(data, "630")

    # 1. Klein positief resultaat (winststuring rond nul / verliesvermijding)
    if res is not None and ta and 0 < res < 0.005 * ta:
        ind.append({"tekst": "Klein positief resultaat (mogelijke winststuring rond nul)",
                    "kleur": "warn",
                    "uitleg": "Een resultaat net boven nul kan wijzen op het vermijden van een verlies."})

    # 2. Hoge accruals (balansgebaseerd) — enkel met vorig boekjaar
    if vorig and ta:
        def d(c):
            return _g(data, c) - _g(vorig, c)
        accruals = (d("29/58") - (d("54/58") + d("50/53"))) - d("42/48") - afschr
        if abs(accruals) > 0.10 * ta:
            gunst = "hoog" if accruals > 0 else "sterk negatief"
            ind.append({"tekst": f"Hoge accruals t.o.v. de activa ({gunst})",
                        "kleur": "warn",
                        "uitleg": "Grote niet-kascomponenten in het resultaat kunnen op resultaatsturing wijzen."})

    # 3. Handelsvorderingen stijgen sneller dan de omzet
    if vorig and omzet and lees_waarde(vorig, "70"):
        dso_nu = _g(data, "40/41") / omzet
        dso_vorig = _g(vorig, "40/41") / lees_waarde(vorig, "70")
        if dso_vorig and dso_nu > dso_vorig * 1.30:
            ind.append({"tekst": "Handelsvorderingen stijgen fors sneller dan de omzet",
                        "kleur": "warn",
                        "uitleg": "Kan wijzen op vervroegde of geflatteerde omzeterkenning."})

    # 4. Aanzienlijke niet-recurrente resultaten
    niet_recurrent = _g(data, "76A") + _g(data, "76B") - _g(data, "66A") - _g(data, "66B")
    if res_vb and abs(niet_recurrent) > 0.10 * abs(res_vb) and abs(niet_recurrent) > 0:
        ind.append({"tekst": "Aanzienlijke niet-recurrente resultaten",
                    "kleur": "warn",
                    "uitleg": "Eenmalige opbrengsten/kosten kunnen het recurrente beeld vertekenen."})

    # 5. Opvallend lage belastingdruk bij winst
    if res_vb and res_vb > 0:
        belasting = _g(data, "67/77")
        if belasting / res_vb < 0.02:
            ind.append({"tekst": "Opvallend lage belastingdruk bij een positief resultaat",
                        "kleur": "warn",
                        "uitleg": "Een zeer lage belastinglast bij winst verdient aandacht (kan legitiem zijn)."})

    # 6. Conformiteit / evenwicht
    if controle:
        ev = controle.get("evenwicht")
        if ev and not ev["in_evenwicht"]:
            ind.append({"tekst": "Balans is niet in evenwicht", "kleur": "err",
                        "uitleg": "Activa en passiva sluiten niet op elkaar aan."})
        if not controle.get("conform", True):
            ind.append({"tekst": "Afwijkingen in de wettelijke optelsommen", "kleur": "err",
                        "uitleg": "Eén of meer subtotalen kloppen niet — controleer de brongegevens."})

    if not ind:
        ind.append({"tekst": "Geen bijzondere indicatoren voor resultaatsturing gedetecteerd",
                    "kleur": "ok", "uitleg": ""})
    return ind


def _beneish(data, vorig):
    """Beneish M-score (benadering, 2 boekjaren + omzet vereist)."""
    if not vorig:
        return None
    o_t, o_v = lees_waarde(data, "70"), lees_waarde(vorig, "70")
    ta_t, ta_v = lees_waarde(data, "20/58"), lees_waarde(vorig, "20/58")
    if not (o_t and o_v and ta_t and ta_v):
        return None

    def g(d, c):
        return _g(d, c)

    def deel(a, b):
        return a / b if b else None

    try:
        dsri = deel(g(data, "40/41") / o_t, g(vorig, "40/41") / o_v)
        gm_t = (o_t - (g(data, "60") + g(data, "61"))) / o_t
        gm_v = (o_v - (g(vorig, "60") + g(vorig, "61"))) / o_v
        gmi = deel(gm_v, gm_t)
        aqi = deel(1 - (g(data, "29/58") + g(data, "22/27")) / ta_t,
                   1 - (g(vorig, "29/58") + g(vorig, "22/27")) / ta_v)
        sgi = deel(o_t, o_v)
        depi = deel(g(vorig, "630") / (g(vorig, "630") + g(vorig, "22/27")) if (g(vorig, "630") + g(vorig, "22/27")) else 0,
                    g(data, "630") / (g(data, "630") + g(data, "22/27")) if (g(data, "630") + g(data, "22/27")) else 0)
        sgai = deel((g(data, "61") + g(data, "62")) / o_t, (g(vorig, "61") + g(vorig, "62")) / o_v)
        lvgi = deel((ta_t - lees_waarde(data, "10/15")) / ta_t, (ta_v - lees_waarde(vorig, "10/15")) / ta_v)

        def d(c):
            return g(data, c) - g(vorig, c)
        tata = ((d("29/58") - (d("54/58") + d("50/53"))) - d("42/48") - g(data, "630")) / ta_t
    except (TypeError, ZeroDivisionError):
        return None
    if None in (dsri, gmi, aqi, sgi, depi, sgai, lvgi):
        return None

    m = (-4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
         + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
    if m > -1.78:
        kleur, oordeel = "err", "Verhoogde kans op winstmanipulatie"
    elif m > -2.22:
        kleur, oordeel = "warn", "Grijze zone"
    else:
        kleur, oordeel = "ok", "Lage kans op winstmanipulatie"
    return {"score": round(m, 2), "kleur": kleur, "oordeel": oordeel,
            "componenten": [
                {"naam": "DSRI · dagen debiteuren-index", "waarde": round(dsri, 3)},
                {"naam": "GMI · brutomarge-index", "waarde": round(gmi, 3)},
                {"naam": "AQI · activakwaliteit-index", "waarde": round(aqi, 3)},
                {"naam": "SGI · omzetgroei-index", "waarde": round(sgi, 3)},
                {"naam": "DEPI · afschrijvingsindex", "waarde": round(depi, 3)},
                {"naam": "SGAI · kosten/omzet-index", "waarde": round(sgai, 3)},
                {"naam": "LVGI · schuldgraad-index", "waarde": round(lvgi, 3)},
                {"naam": "TATA · totale accruals ÷ activa", "waarde": round(tata, 3)},
            ]}


def evalueer_betrouwbaarheid(data, vorig, controle, bestuurders):
    auditor = data.get("__auditor__")
    heeft_commissaris = bool(auditor and auditor.get("heeft_verslag")) or any(
        "commissaris" in (b.get("functie", "").lower()) for b in (bestuurders or []))

    indicatoren = _resultaatsturing(data, vorig, controle)
    beneish = _beneish(data, vorig)

    # Globaal oordeel
    err = any(i["kleur"] == "err" for i in indicatoren)
    warn = any(i["kleur"] == "warn" for i in indicatoren)
    if auditor and auditor.get("kleur") == "err":
        err = True
    elif auditor and (auditor.get("kleur") == "warn" or auditor.get("going_concern")):
        warn = True
    if beneish and beneish["kleur"] == "err":
        err = True
    if err:
        oordeel, kleur = "Aandachtspunten voor de betrouwbaarheid", "err"
    elif warn:
        oordeel, kleur = "Matige betrouwbaarheid — enkele aandachtspunten", "warn"
    else:
        oordeel, kleur = "Geen bijzondere betrouwbaarheidsproblemen gedetecteerd", "ok"

    return {
        "auditor": auditor,
        "heeft_commissaris": heeft_commissaris,
        "indicatoren": indicatoren,
        "beneish": beneish,
        "oordeel": oordeel,
        "kleur": kleur,
    }
