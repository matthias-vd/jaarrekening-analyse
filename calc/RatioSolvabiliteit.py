class RatioSolvabiliteit:
    def __init__(
        self,
        totaal_eigen_vermogen,       # EV
        totaal_vreemd_vermogen,      # VV
        vreemd_vermogen_lt,          # VVLT
        vreemd_vermogen_kt,          # VVKT
        totaal_vermogen,             # TV = EV + VV
        netto_financieel_vv,         # financieel VVLT + financieel VVKT - (LM + GB)
        reserves,                    # reserves
        overgedragen_resultaat,      # overgedragen winst/verlies
        cashflow_ev_na_belastingen,  # CF EV na belastingen
        schulden_meer_dan_1j,        # schulden op meer dan 1 jaar
        schulden_1j_die_binnen_1j_vervallen,  # deel >1j binnen het jaar
        resultaat_voor_nkk_en_fkvv,  # EBIT voor NKK en FKVV
        fkvv,                        # financiële kosten vreemd vermogen
        kasmiddelen,                 # LM
        geldbeleggingen              # GB
    ):
        self.EV = totaal_eigen_vermogen
        self.VV = totaal_vreemd_vermogen
        self.VVLT = vreemd_vermogen_lt
        self.VVKT = vreemd_vermogen_kt
        self.TV = totaal_vermogen
        self.netto_fin_vv = netto_financieel_vv
        self.reserves = reserves
        self.ov_res = overgedragen_resultaat
        self.CF_EV = cashflow_ev_na_belastingen
        self.schulden_meer_dan_1j = schulden_meer_dan_1j
        self.schulden_1j_binnen_1j = schulden_1j_die_binnen_1j_vervallen
        self.EBIT_voor = resultaat_voor_nkk_en_fkvv
        self.FKVV = fkvv
        self.LM = kasmiddelen
        self.GB = geldbeleggingen

    # Schuldratio's

    def algemene_schuldgraad(self):
        # VV / EV of VV / TV (afhankelijk van keuze)
        return self.VV / self.EV

    def algemene_graad_financiele_onafhankelijkheid(self):
        # EV / VV of EV / TV
        return self.EV / self.VV

    def langetermijn_schuldgraad(self):
        # VVLT / EV of VVLT / PV (hier t.o.v. PV = EV + VVLT)
        permanent_vermogen = self.EV + self.VVLT
        return self.VVLT / permanent_vermogen

    def langetermijn_graad_financiele_onafhankelijkheid(self):
        # EV / VVLT of EV / PV
        permanent_vermogen = self.EV + self.VVLT
        return self.EV / permanent_vermogen

    def netto_financiele_schuldgraad(self):
        # netto financieel VV / EV
        # netto financieel VV = financieel VVLT + financieel VVKT - (LM + GB)
        return self.netto_fin_vv / self.EV

    def zelffinancieringsgraad(self):
        # (reserves + overgedragen resultaat) / totaal vermogen
        return (self.reserves + self.ov_res) / self.TV

    # Dekkingratio's

    def dekking_fkvv_door_totaal_nettoresultaat(self):
        # (resultaat voor NKK en voor FKVV) / FKVV
        return self.EBIT_voor / self.FKVV

    def dekking_vv_door_cashflow(self):
        # CF EV na belastingen / totaal VV
        return self.CF_EV / self.VV

    def dekking_vvlt_door_cashflow(self):
        # CF EV na belastingen / VVLT
        return self.CF_EV / self.VVLT

    def dekking_schulden_meer1j_binnen_1j_door_cashflow(self):
        # CF EV na belastingen / schulden >1j die binnen het jaar vervallen
        return self.CF_EV / self.schulden_1j_binnen_1j

    def dekking_netto_financieel_vv_door_cashflow(self):
        # CF EV na belastingen / netto financieel VV
        return self.CF_EV / self.netto_fin_vv
