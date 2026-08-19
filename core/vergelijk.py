"""Vergelijking van meerdere jaarrekeningen (over de jaren heen of tussen ondernemingen).

Neemt een lijst van (data-dict) in, berekent per dataset een set kerncijfers en
ratio's, en bouwt een vergelijkingsstructuur met:
- een kolom per jaarrekening (gesorteerd op boekjaareinde),
- per metriek de reeks waarden en een evolutie-oordeel (gunstig/ongunstig),
- kant-en-klare data voor grafieken.
"""

try:
    from core.analyse import lees_waarde, _bedrijfsnaam, _boekjaar
    from core.ratios import bereken_ratios
except ModuleNotFoundError:  # standalone
    from analyse import lees_waarde, _bedrijfsnaam, _boekjaar
    from ratios import bereken_ratios


# Metrieken: uit een rubriekcode (code) of uit een berekende ratio (ratio).
_METRIEKEN = [
    {"naam": "Balanstotaal", "code": "20/58", "eenheid": "EUR", "hoger_is_beter": True},
    {"naam": "Eigen vermogen", "code": "10/15", "eenheid": "EUR", "hoger_is_beter": True},
    {"naam": "Resultaat van het boekjaar", "code": "9904", "eenheid": "EUR", "hoger_is_beter": True},
    {"naam": "Omzet", "code": "70", "eenheid": "EUR", "hoger_is_beter": True},
    {"naam": "Current ratio", "ratio": "current_ratio", "eenheid": "x", "hoger_is_beter": True},
    {"naam": "Solvabiliteit (EV/TV)", "ratio": "graad_fin_onafh", "eenheid": "%", "hoger_is_beter": True},
    {"naam": "Nettorendabiliteit EV na bel.", "ratio": "netto_rend_ev_na_bel", "eenheid": "%", "hoger_is_beter": True},
]

_EUR_METRIEKEN = {"Balanstotaal", "Eigen vermogen", "Resultaat van het boekjaar", "Omzet"}


def _ratio_waarden(data):
    waarden = {}
    for groep in bereken_ratios(data)["groepen"]:
        for r in groep["ratios"]:
            if r["berekenbaar"]:
                waarden[r["id"]] = r["waarde"]
    return waarden


def _jaar(boekjaar):
    # boekjaar is bv. "2024-07-01 — 2025-06-30"; neem het eindjaar.
    cijfers = [deel for deel in boekjaar.replace("—", " ").split() if len(deel) >= 4 and deel[:4].isdigit()]
    return cijfers[-1][:4] if cijfers else ""


def _evolutie(waarden, hoger_is_beter):
    geldig = [w for w in waarden if w is not None]
    if len(geldig) < 2:
        return None
    eerste, laatste = geldig[0], geldig[-1]
    verschil = laatste - eerste
    pct = (verschil / abs(eerste) * 100) if eerste else None
    if abs(verschil) < 1e-9:
        return {"richting": "stabiel", "pct": 0.0, "gunstig": None, "kleur": "neutral"}
    stijging = verschil > 0
    gunstig = stijging if hoger_is_beter else (not stijging)
    return {
        "richting": "stijging" if stijging else "daling",
        "pct": round(pct, 1) if pct is not None else None,
        "gunstig": gunstig,
        "kleur": "ok" if gunstig else "err",
    }


def bouw_vergelijking(datasets):
    """``datasets``: lijst van ``{code: waarde}``-dicts. Geeft de vergelijkingsstructuur terug."""
    kolommen = []
    for data in datasets:
        naam = _bedrijfsnaam(data)
        boekjaar = _boekjaar(data)
        jaar = _jaar(boekjaar)
        kolommen.append({
            "naam": naam,
            "boekjaar": boekjaar,
            "jaar": jaar,
            "label": f"{naam} ({jaar})" if jaar else naam,
            "data": data,
            "ratios": _ratio_waarden(data),
        })

    # Sorteer op eindjaar wanneer beschikbaar (chronologisch), anders behoud volgorde.
    if all(k["jaar"] for k in kolommen):
        kolommen.sort(key=lambda k: k["jaar"])

    metrieken = []
    for spec in _METRIEKEN:
        waarden = []
        for kol in kolommen:
            if "code" in spec:
                waarden.append(lees_waarde(kol["data"], spec["code"]))
            else:
                waarden.append(kol["ratios"].get(spec["ratio"]))
        if all(w is None for w in waarden):
            continue
        metrieken.append({
            "naam": spec["naam"],
            "eenheid": spec["eenheid"],
            "is_eur": spec["naam"] in _EUR_METRIEKEN,
            "waarden": waarden,
            "evolutie": _evolutie(waarden, spec["hoger_is_beter"]),
        })

    labels = [k["label"] for k in kolommen]
    grafiek_eur = {"labels": labels, "reeksen": [
        {"naam": m["naam"], "waarden": [None if w is None else round(w, 2) for w in m["waarden"]]}
        for m in metrieken if m["is_eur"]
    ]}
    grafiek_ratio = {"labels": labels, "reeksen": [
        {"naam": f"{m['naam']} ({m['eenheid']})",
         "waarden": [None if w is None else round(w, 3) for w in m["waarden"]]}
        for m in metrieken if not m["is_eur"]
    ]}

    aantal_gunstig = sum(1 for m in metrieken if m["evolutie"] and m["evolutie"]["gunstig"])
    aantal_ongunstig = sum(1 for m in metrieken if m["evolutie"] and m["evolutie"]["gunstig"] is False)

    return {
        "kolommen": [{k2: v for k2, v in kol.items() if k2 not in ("data", "ratios")} for kol in kolommen],
        "metrieken": metrieken,
        "grafiek_eur": grafiek_eur,
        "grafiek_ratio": grafiek_ratio,
        "aantal": len(kolommen),
        "aantal_gunstig": aantal_gunstig,
        "aantal_ongunstig": aantal_ongunstig,
        "meerdere_bedrijven": len({k["naam"] for k in kolommen}) > 1,
    }
