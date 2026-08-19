"""Krediet-/faillissementsrisico van een jaarrekening.

Twee complementaire, uit de balans/RR afleidbare benaderingen:

1. **Altman Z''-score** — variant voor niet-beursgenoteerde en niet-industriële
   ondernemingen (boekwaarden):
       Z'' = 3.25 + 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4
   met veilige zone (> 2.6), grijze zone (1.1–2.6) en noodzone (< 1.1).

2. **Gezondheidskwadrant** (cursus FAO, Tabel 16.1): rendabiliteit × liquiditeit
   → gezond / tijdelijk ziek / chronisch ziek / stervend.

Beide zijn indicatief en vervangen geen volwaardige kredietbeoordeling.
"""

try:
    from core.analyse import lees_waarde
except ModuleNotFoundError:  # standalone vanuit map core/
    from analyse import lees_waarde


def _deel(teller, noemer):
    if teller is None or not noemer:
        return None
    return teller / noemer


def bereken_risico(data):
    def g(code):
        return lees_waarde(data, code)

    ta = g("20/58") if g("20/58") is not None else g("10/49")
    ev = g("10/15")
    tp = g("10/49")
    vv = (tp - ev) if (tp is not None and ev is not None) else None

    vla = g("29/58")
    vvkt = (g("42/48") or 0) + (g("492/3") or 0)
    reserves = (g("13") or 0) + (g("14") or 0)
    fkvv = g("650") if g("650") is not None else (g("65") or 0)
    res_voor_bel = g("9903")
    ebit = (res_voor_bel + fkvv) if res_voor_bel is not None else g("9901")
    res_na_bel = g("9904")

    altman = None
    if ta and ev is not None and vv is not None:
        werkkapitaal = (vla - vvkt) if vla is not None else None
        x1 = _deel(werkkapitaal, ta)
        x2 = _deel(reserves, ta)
        x3 = _deel(ebit, ta)
        x4 = _deel(ev, vv) if vv else None
        if None not in (x1, x2, x3, x4):
            score = 3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
            if score > 2.6:
                zone, kleur, uitleg = "Veilige zone", "ok", "Lage kans op financiële moeilijkheden."
            elif score >= 1.1:
                zone, kleur, uitleg = "Grijze zone", "warn", "Verhoogde waakzaamheid aangewezen."
            else:
                zone, kleur, uitleg = "Noodzone", "err", "Verhoogd risico op financiële moeilijkheden."
            altman = {
                "score": round(score, 2),
                "zone": zone,
                "kleur": kleur,
                "interpretatie": uitleg,
                "componenten": [
                    {"naam": "X1 · werkkapitaal / activa", "waarde": round(x1, 3)},
                    {"naam": "X2 · reserves + overgedragen res. / activa", "waarde": round(x2, 3)},
                    {"naam": "X3 · EBIT / activa", "waarde": round(x3, 3)},
                    {"naam": "X4 · eigen vermogen / vreemd vermogen", "waarde": round(x4, 3)},
                ],
            }

    # Gezondheidskwadrant: rendabiliteit (resultaat boekjaar) × liquiditeit (current ratio)
    kwadrant = None
    current_ratio = _deel(vla, vvkt) if vvkt else None
    rendabel = None if res_na_bel is None else (res_na_bel > 0)
    liquide = None if current_ratio is None else (current_ratio >= 1)
    if rendabel is not None and liquide is not None:
        if rendabel and liquide:
            naam, kleur, uitleg = "Gezond", "ok", "Zowel rendabel als liquide."
        elif rendabel and not liquide:
            naam, kleur, uitleg = "Tijdelijk ziek", "warn", "Rendabel maar krappe liquiditeit (bv. sterke groei/overinvestering)."
        elif not rendabel and liquide:
            naam, kleur, uitleg = "Chronisch ziek", "warn", "Liquide maar structureel rendabiliteitsprobleem."
        else:
            naam, kleur, uitleg = "Stervend", "err", "Zowel rendabiliteits- als liquiditeitsproblemen."
        kwadrant = {
            "naam": naam, "kleur": kleur, "interpretatie": uitleg,
            "rendabiliteit": "positief" if rendabel else "negatief",
            "liquiditeit": "voldoende" if liquide else "krap",
            "current_ratio": round(current_ratio, 2) if current_ratio is not None else None,
        }

    gunstig = None
    if altman is not None or kwadrant is not None:
        gunstig = (altman is None or altman["kleur"] == "ok") and (kwadrant is None or kwadrant["kleur"] == "ok")

    # --- Gezondheidsbarometer (0–100) ----------------------------------
    solvabiliteit = _deel(ev, tp)  # EV/TV
    rendabiliteit = _deel(res_na_bel, ev) if (ev and ev > 0) else None  # netto rend. EV
    barometer = None
    if solvabiliteit is not None and current_ratio is not None:
        solv_pt = max(0.0, min(40.0, solvabiliteit * 100))            # 40% EV -> 40 pt
        liq_pt = max(0.0, min(30.0, current_ratio * 15))              # current ratio 2 -> 30 pt
        if rendabiliteit is None:
            rend_pt = 0.0
        else:
            rend_pt = max(0.0, min(30.0, (rendabiliteit * 100) / 15 * 30))  # 15% rend. EV -> 30 pt
        score = round(solv_pt + liq_pt + rend_pt)
        if score >= 70:
            kleur, label = "ok", "Financieel gezond (laag risico)"
        elif score >= 45:
            kleur, label = "warn", "Aandacht (matig risico)"
        else:
            kleur, label = "err", "Verhoogd risico"
        barometer = {"score": score, "kleur": kleur, "label": label}

    # --- Signalen ------------------------------------------------------
    signalen = []
    activa = lees_waarde(data, "20/58")
    passiva = lees_waarde(data, "10/49")
    overgedragen = lees_waarde(data, "14")
    if activa is not None and passiva is not None and abs(activa - passiva) > 1:
        signalen.append({"tekst": "Balans niet in evenwicht", "kleur": "err"})
    if ev is not None and ev < 0:
        signalen.append({"tekst": "Negatief eigen vermogen", "kleur": "err"})
    if res_na_bel is not None and res_na_bel < 0:
        signalen.append({"tekst": "Verlies van het boekjaar", "kleur": "warn"})
    if overgedragen is not None and overgedragen < 0:
        signalen.append({"tekst": "Overgedragen verlies", "kleur": "warn"})
    if current_ratio is not None and current_ratio < 1:
        signalen.append({"tekst": "Zwakke liquiditeit (current ratio < 1)", "kleur": "warn"})
    if solvabiliteit is not None and solvabiliteit < 0.20:
        signalen.append({"tekst": "Lage solvabiliteit (eigen vermogen < 20%)", "kleur": "warn"})
    if not signalen:
        signalen.append({"tekst": "Geen bijzondere signalen gedetecteerd", "kleur": "ok"})

    # --- Indicatieve kredietrichtlijn ----------------------------------
    kredietlimiet = None
    if ev is not None and ev > 0 and barometer is not None:
        ruw = 0.30 * ev * (barometer["score"] / 100.0)
        kredietlimiet = max(0, round(ruw / 1000.0) * 1000)

    return {
        "altman": altman,
        "kwadrant": kwadrant,
        "gunstig": gunstig,
        "barometer": barometer,
        "signalen": signalen,
        "kredietlimiet": kredietlimiet,
    }
