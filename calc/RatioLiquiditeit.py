class RatioLiquiditeit:
    def __init__(
        self,
        beperkte_vlottende_activa,   # BVA
        vlottende_bedrijfsactiva,    # VBA (voor NBKB)
        vlottende_vreemd_vermogen_kt,  # VVKT (financieel + operationeel)
        operationeel_vvkt,           # operationeel VVKT (handelschulden, ... )
        permanente_vermogen,         # PV = EV + VVLT
        uitgebreide_vaste_activa,    # UVA (vaste + vaste bedrijfsactiva + oprichtingskosten)
        beperkte_vvkt_financieel,    # financieel VVKT (voor nettokas)
        geldbeleggingen,             # GB
        liquide_middelen,            # LM
        voorraad_begin,              # beginvoorraad goederen + BIU
        voorraad_einde,              # eindvoorraad goederen + BIU
        kostprijs_verkopen,          # kostprijs van de verkopen / recurrente bedrijfskosten
        aankopen_hg_gs_hs,           # aankopen handelsgoederen, grond- en hulpstoffen
        diensten_diverse_goederen,   # DDG
        aankopen_og_bestemd_voor_verkoop,  # aangekochte onroerende goederen voor verkoop
        vooruitbetalingen_og,        # vooruitbetalingen op onroerende goederen
        verkopen,                    # omzet
        btw_op_verkopen,             # btw op verkopen
        handelsvorderingen_1j,       # handelsvorderingen op ten hoogste 1 jaar
        gendosseerde_handelseffecten,# gendosseerde wissels
        btw_op_aankopen,             # btw op aankopen
        handelsschulden_1j           # handelsschulden op ten hoogste 1 jaar
    ):
        self.BVA = beperkte_vlottende_activa
        self.VBA = vlottende_bedrijfsactiva
        self.VVKT = vlottende_vreemd_vermogen_kt
        self.opVVKT = operationeel_vvkt
        self.PV = permanente_vermogen
        self.UVA = uitgebreide_vaste_activa
        self.finVVKT = beperkte_vvkt_financieel
        self.GB = geldbeleggingen
        self.LM = liquide_middelen
        self.VB = voorraad_begin
        self.VE = voorraad_einde
        self.KV = kostprijs_verkopen
        self.aankopen_hg_gs_hs = aankopen_hg_gs_hs
        self.DDG = diensten_diverse_goederen
        self.aankopen_og = aankopen_og_bestemd_voor_verkoop
        self.vb_og = vooruitbetalingen_og
        self.verkopen = verkopen
        self.btw_verkopen = btw_op_verkopen
        self.hv_1j = handelsvorderingen_1j
        self.gendosseerde = gendosseerde_handelseffecten
        self.btw_aankopen = btw_op_aankopen
        self.hs_1j = handelsschulden_1j

    # Kern: NBK, NBKB, nettokas en grote liquiditeitsratio's

    def brutobedrijfskapitaal(self):
        # BVA
        return self.BVA

    def nettobedrijfskapitaal(self):
        # NBK = BVA - VVKT
        return self.BVA - self.VVKT

    def nettobedrijfskapitaalbehoefte(self):
        # NBKB = VBA - operationeel VVKT
        return self.VBA - self.opVVKT

    def nettokas(self):
        # Nettokas = NBK - NBKB
        return self.nettobedrijfskapitaal() - self.nettobedrijfskapitaalbehoefte()

    def current_ratio(self):
        # Liquiditeitsratio in ruime zin = BVA / VVKT
        return self.BVA / self.VVKT

    def acid_test(self):
        # Liquiditeit in enge zin = (vorderingen <= 1j + GB + LM) / VVKT
        # Hier nemen we vorderingen <= 1j impliciet op via handelsvorderingen_1j
        teller = self.hv_1j + self.GB + self.LM
        return teller / self.VVKT

    def nettokasratio(self):
        # Nettokasratio = (LM + GB + finVVKT?) / BVA
        # In de cursus: focus op aandeel zeer liquide bestanddelen in BVA
        teller = self.LM + self.GB
        return teller / self.BVA

    # Rotaties en dagen (voorraad, klanten, leveranciers)

    def gemiddelde_voorraad(self):
        return (self.VB + self.VE) / 2

    def globale_rotatie_voorraad(self):
        # Kostprijs van de verkopen / gemiddelde voorraad
        return self.KV / self.gemiddelde_voorraad()

    def dagen_voorraad(self):
        # 365 / rotatie voorraden
        return 365 / self.globale_rotatie_voorraad()

    def rotatie_aangekochte_voorraad(self):
        # (kosten HG, GS, HS + DDG) / (aangekochte voorraad + vooruitbetalingen OG)
        teller = self.aankopen_hg_gs_hs + self.DDG
        noemer = self.aankopen_og + self.vb_og
        return teller / noemer

    def rotatie_handelsvorderingen(self):
        # (verkopen + btw op verkopen) / (handelsvorderingen <= 1j + gendosseerde HE)
        teller = self.verkopen + self.btw_verkopen
        noemer = self.hv_1j + self.gendosseerde
        return teller / noemer

    def dagen_klantenkrediet(self):
        # 365 / rotatie handelsvorderingen
        return 365 / self.rotatie_handelsvorderingen()

    def rotatie_handelsschulden(self):
        # (aankopen HG,GS,HS + DDG + btw op aankopen) / handelsschulden <= 1j
        teller = self.aankopen_hg_gs_hs + self.DDG + self.btw_aankopen
        return teller / self.hs_1j

    def dagen_leverancierskrediet(self):
        # 365 / rotatie handelsschulden
        return 365 / self.rotatie_handelsschulden()
