class RatioRendabiliteit:
    def __init__(
        self,
        omzet,                      # verkopen
        brutoverkoopresultaat,      # REBITDA (bruto recurrent bedrijfsresultaat)
        nettoverkoopresultaat,      # REBIT
        totaal_activa_begin,
        totaal_activa_einde,
        bedrijfsactiva_begin,
        bedrijfsactiva_einde,
        bedrijfsresultaat_bruto,    # resultaat voor NKK en FKVV (op TA)
        bedrijfsresultaat_netto,    # resultaat na NKK, voor FKVV (op TA)
        recurrent_bedrijfsresultaat, # REBIT op bedrijfsactiva
        nettorecurrent_bedrijfsresultaat, # netto REBIT op bedrijfsactiva
        winst_na_belastingen,       # winst verlies bj na belastingen
        winst_voor_belastingen,     # winst verlies bj voor belastingen
        eigen_vermogen_begin,
        eigen_vermogen_einde,
        fkvv,                       # financiële kosten vreemd vermogen
        prijs_per_eenheid,          # P
        variabele_kost_per_eenheid, # V
        totale_vaste_kosten,        # F
        verkochte_eenheden          # Q
    ):
        self.omzet = omzet
        self.brutoverkoopresultaat = brutoverkoopresultaat
        self.nettoverkoopresultaat = nettoverkoopresultaat
        self.TA_begin = totaal_activa_begin
        self.TA_einde = totaal_activa_einde
        self.BA_begin = bedrijfsactiva_begin
        self.BA_einde = bedrijfsactiva_einde
        self.R_bruto_TA = bedrijfsresultaat_bruto
        self.R_netto_TA = bedrijfsresultaat_netto
        self.REBIT_BA = recurrent_bedrijfsresultaat
        self.NREBIT_BA = nettorecurrent_bedrijfsresultaat
        self.winst_na_bel = winst_na_belastingen
        self.winst_vr_bel = winst_voor_belastingen
        self.EV_begin = eigen_vermogen_begin
        self.EV_einde = eigen_vermogen_einde
        self.FKVV = fkvv
        self.P = prijs_per_eenheid
        self.V = variabele_kost_per_eenheid
        self.F = totale_vaste_kosten
        self.Q = verkochte_eenheden

    # Hulpmaten

    def gemiddeld_totaal_actief(self):
        return (self.TA_begin + self.TA_einde) / 2

    def gemiddeld_bedrijfsactief(self):
        return (self.BA_begin + self.BA_einde) / 2

    def gemiddeld_eigen_vermogen(self):
        return (self.EV_begin + self.EV_einde) / 2

    # Rendabiliteit verkopen

    def brutoverkoopmarge(self):
        # REBITDA / omzet
        return self.brutoverkoopresultaat / self.omzet

    def nettoverkoopmarge(self):
        # REBIT / omzet
        return self.nettoverkoopresultaat / self.omzet

    # Rendabiliteit activa

    def brutorendabiliteit_totaal_actief(self):
        # resultaat voor NKK en FKVV / gemiddeld totaal actief
        return self.R_bruto_TA / self.gemiddeld_totaal_actief()

    def nettorendabiliteit_totaal_actief(self):
        # resultaat na NKK, voor FKVV / gemiddeld totaal actief
        return self.R_netto_TA / self.gemiddeld_totaal_actief()

    def brutorendabiliteit_bedrijfsactiva(self):
        # REBIT / gemiddeld bedrijfsactief
        return self.REBIT_BA / self.gemiddeld_bedrijfsactief()

    def nettorendabiliteit_bedrijfsactiva(self):
        # netto REBIT / gemiddeld bedrijfsactief
        return self.NREBIT_BA / self.gemiddeld_bedrijfsactief()

    # Rendabiliteit eigen vermogen

    def brutorendabiliteit_eigen_vermogen_na_bel(self):
        # cashflow EV na belastingen / gemiddeld EV
        # hier benaderd door winst na belastingen + afschrijvingen (CF moet extern worden meegegeven indien exact)
        return self.winst_na_bel / self.gemiddeld_eigen_vermogen()

    def nettorendabiliteit_eigen_vermogen_voor_bel(self):
        # winst of verlies voor belastingen / gemiddeld EV
        return self.winst_vr_bel / self.gemiddeld_eigen_vermogen()

    def nettorendabiliteit_eigen_vermogen_na_bel(self):
        # winst of verlies na belastingen / gemiddeld EV
        return self.winst_na_bel / self.gemiddeld_eigen_vermogen()

    # Evenwichtspunt en operationele hefboom

    def contributiemarge_per_eenheid(self):
        # P - V
        return self.P - self.V

    def evenwichtshoeveelheid(self):
        # QN = F / (P - V)
        return self.F / self.contributiemarge_per_eenheid()

    def evenwichtsverkoop_bedrag(self):
        # F / ( (P - V) / P ) = F * P / (P - V)
        return self.F * self.P / self.contributiemarge_per_eenheid()

    def relatieve_contributiemarge(self):
        # (P - V) / P
        return self.contributiemarge_per_eenheid() / self.P

    def veiligheidsmarge(self):
        # (werkelijke omzet - evenwichtsomzet) / werkelijke omzet
        evenwichtsomzet = self.evenwichtsverkoop_bedrag()
        return (self.omzet - evenwichtsomzet) / self.omzet

    def graad_operationele_hefboom(self):
        # (P*Q - V*Q - F) / (P*Q - V*Q)
        # = REBIT / (verkopen - variabele kosten)
        verkoop = self.P * self.Q
        variabele_kosten = self.V * self.Q
        rebit = verkoop - variabele_kosten - self.F
        contributie = verkoop - variabele_kosten
        return rebit / contributie

    # Financiële hefboom

    def financiele_hefboommultiplicator(self):
        # (winst of verlies bj voor belastingen / gemiddeld EV) /
        # (nettorendabiliteit totaal actief voor bel.)  => factor1 * factor2
        # Hier eenvoudiger: (TA / EV) * (EBIT - FKVV)/EBIT
        gemiddeld_EV = self.gemiddeld_eigen_vermogen()
        gemiddeld_TA = self.gemiddeld_totaal_actief()
        factor2 = gemiddeld_TA / gemiddeld_EV
        EBIT = self.R_netto_TA + self.FKVV  # benadering
        factor1 = (EBIT - self.FKVV) / EBIT
        return factor1 * factor2

    def graad_financiele_hefboom(self):
        # EBIT / (EBIT - FKVV)
        EBIT = self.R_netto_TA + self.FKVV  # benadering
        return EBIT / (EBIT - self.FKVV)

    def graad_totale_hefboom(self):
        # graad operationele hefboom x graad financiële hefboom
        return self.graad_operationele_hefboom() * self.graad_financiele_hefboom()
