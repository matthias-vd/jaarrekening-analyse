"""Vereenvoudigd kasstromenoverzicht (cf. DEEL1-sjabloon), berekend uit twee boekjaren.

Uit één NBB-neerlegging halen we het huidige én het vorige boekjaar (kolommen 'boekjaar'
en 'vorig boekjaar'). Daarmee reconstrueren we de hoofdlijnen van het herwerkte
kasstromenoverzicht: operationele cashflow, verandering van de nettobedrijfskapitaal-
behoefte, kasstroom uit operaties, (des)investeringen, vrije kasstroom en financiering.

Let op: dit is een BENADERING. De exacte niet-kaskosten en enkele financieringslijnen
vergen de volledige herwerking met toelichtingscodes die niet altijd beschikbaar zijn.
Een controlelijn vergelijkt de berekende kasmutatie met de werkelijke mutatie van de
liquide middelen en geldbeleggingen.
"""

try:
    from core.analyse import lees_waarde
except ModuleNotFoundError:
    from analyse import lees_waarde


def bereken_kasstroom(data, vorig):
    if not vorig:
        return None
    winst = lees_waarde(data, "9904")
    if winst is None:
        return None

    def h(code):
        w = lees_waarde(data, code)
        return w if w is not None else 0.0

    def p(code):
        w = lees_waarde(vorig, code)
        return w if w is not None else 0.0

    niet_kaskosten = h("630") + h("631/4") + h("635/8")
    fkvv = lees_waarde(data, "650")
    fkvv = fkvv if fkvv is not None else h("65")
    operationele_cf = winst + niet_kaskosten + fkvv

    # Verandering nettobedrijfskapitaalbehoefte = Δ vlottende bedrijfsactiva − Δ operationeel VVKT
    def vba(f):
        return f("3") + f("40/41") + f("490/1")

    def op_vvkt(f):
        return f("44") + f("45") + f("46") + f("47/48") + f("492/3")

    d_vba = vba(h) - vba(p)
    d_opvvkt = op_vvkt(h) - op_vvkt(p)
    d_nbkb = d_vba - d_opvvkt
    kasstroom_operaties = operationele_cf - d_nbkb

    # (Des)investeringen in (uitgebreide) vaste activa ≈ −(Δ netto vaste activa + afschrijvingen)
    def uva(f):
        return f("20") + f("21/28") + f("29")

    investeringen = -((uva(h) - uva(p)) + niet_kaskosten)
    vrije_kasstroom_ond = kasstroom_operaties + investeringen

    # Financiering met financieel vreemd vermogen ≈ Δ(voorzieningen + schulden) − FKVV
    def fin_vv(f):
        return f("16") + f("17") + f("42/48")

    fin_financieel = (fin_vv(h) - fin_vv(p)) - fkvv
    vrije_kasstroom_ev = vrije_kasstroom_ond + fin_financieel

    # Financiering met extern eigen vermogen ≈ Δ(inbreng + herwaard. + kapitaalsubsidies) − uitkering
    def extern_ev(f):
        return f("10/11") + f("12") + f("15")

    uitkering = h("694/7")
    fin_ev = (extern_ev(h) - extern_ev(p)) - uitkering
    mutatie_kas = vrije_kasstroom_ev + fin_ev

    controle = (h("50/53") + h("54/58")) - (p("50/53") + p("54/58"))

    lijnen = [
        {"label": "Winst (verlies) van het boekjaar na belastingen", "waarde": winst},
        {"label": "+ Niet-kaskosten (benadering)", "waarde": niet_kaskosten},
        {"label": "+ Financiële kaskosten van het vreemd vermogen", "waarde": fkvv},
        {"label": "= Operationele cashflow na belastingen (1)", "waarde": operationele_cf, "subtotaal": True},
        {"label": "− Verandering van de nettobedrijfskapitaalbehoefte (2)", "waarde": d_nbkb},
        {"label": "= Kasstroom uit operaties (3) = (1) − (2)", "waarde": kasstroom_operaties, "subtotaal": True},
        {"label": "(Des)investeringen in (uitgebreide) vaste activa (4)", "waarde": investeringen},
        {"label": "= Vrije kasstroom voor de onderneming (5) = (3) + (4)", "waarde": vrije_kasstroom_ond, "subtotaal": True},
        {"label": "Financiering met financieel vreemd vermogen (6)", "waarde": fin_financieel},
        {"label": "= Vrije kasstroom voor de houders van het EV (7) = (5) + (6)", "waarde": vrije_kasstroom_ev, "subtotaal": True},
        {"label": "Financiering met extern eigen vermogen (8)", "waarde": fin_ev},
        {"label": "= Mutatie van de kaspositie (9) = (7) + (8)", "waarde": mutatie_kas, "subtotaal": True},
    ]
    return {
        "lijnen": lijnen,
        "controle": controle,
        "verschil": mutatie_kas - controle,
        "reconcilieert": abs(mutatie_kas - controle) <= max(1.0, abs(controle) * 0.05),
    }
