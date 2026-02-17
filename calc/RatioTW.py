class RatioTW:
    def __init__(
        self,
        personeelskosten,                             # Personeelskosten
        brutotoegevoegdewaarde,                      # Bruto toegevoegde waarde
        recurrentenkkvanbedrijfsaardexclvoorzieningenpensioenensubsidies,  # Recurrente NKK bedrijfsaard excl. voorzieningen pensioenen en subsidies
        fkvvexclsubs,                                # Financiële kosten vreemd vermogen excl. subsidies
        belastingen,                                 # Belastingen
        toegevoegdewinstverlies,                     # Toegevoegde winst/verlies
        gemiddeldpersoneelsbestand,                  # Gemiddeld personeelsbestand
        waardevandeproductie,                        # Waarde van de productie
        vastebedrijfsactiva,                         # Vaste bedrijfsactiva
        bezoldigingensocialelastenpensioenen,        # Bezoldiging en sociale lasten pensioenen
        aantalgepresteerdeuren,                      # Aantal gepresteerde uren
        aanschaffingenmva,                           # Aanschaffingen materiële vaste activa
        overheidssubsidies                           # Overheidssubsidies
    ):
        self.personeelskosten = personeelskosten
        self.brutotoegevoegdewaarde = brutotoegevoegdewaarde
        self.recurrentenkkvanbedrijfsaardexclvoorzieningenpensioenensubsidies = recurrentenkkvanbedrijfsaardexclvoorzieningenpensioenensubsidies
        self.fkvvexclsubs = fkvvexclsubs
        self.belastingen = belastingen
        self.toegevoegdewinstverlies = toegevoegdewinstverlies
        self.gemiddeldpersoneelsbestand = gemiddeldpersoneelsbestand
        self.waardevandeproductie = waardevandeproductie
        self.vastebedrijfsactiva = vastebedrijfsactiva
        self.bezoldigingensocialelastenpensioenen = bezoldigingensocialelastenpensioenen
        self.aantalgepresteerdeuren = aantalgepresteerdeuren
        self.aanschaffingenmva = aanschaffingenmva
        self.overheidssubsidies = overheidssubsidies

    # Aandelen in bruto toegevoegde waarde
    def aandeelpersoneelinbtw(self):
        # Aandeel van het personeel in de bruto toegevoegde waarde
        return self.personeelskosten / self.brutotoegevoegdewaarde

    def aandeelrecurrentenkkvbedrijfsaardinbtw(self):
        # Aandeel van de recurrente niet-kaskosten van bedrijfsaard excl. voorzieningen voor pensioenen en subsidies in de bruto toegevoegde waarde
        return self.recurrentenkkvanbedrijfsaardexclvoorzieningenpensioenensubsidies / self.brutotoegevoegdewaarde

    def aandeelfkvvinbtw(self):
        # Aandeel van de financiële kosten van het vreemd vermogen excl. subsidies in de bruto toegevoegde waarde
        return self.fkvvexclsubs / self.brutotoegevoegdewaarde

    def aandeelbelinbtw(self):
        # Aandeel van de belastingen in de bruto toegevoegde waarde
        return self.belastingen / self.brutotoegevoegdewaarde

    def aandeeltoegevoegdewinstverliesinbtw(self):
        # Aandeel van de toegevoegde winst of verlies in de bruto toegevoegde waarde
        return self.toegevoegdewinstverlies / self.brutotoegevoegdewaarde

    # Per werknemer
    def btwperwerknemer(self):
        # Bruto toegevoegde waarde per werknemer
        return self.brutotoegevoegdewaarde / self.gemiddeldpersoneelsbestand

    def vbapwn(self):
        # Vaste bedrijfsactiva per werknemer
        return self.vastebedrijfsactiva / self.gemiddeldpersoneelsbestand

    def pkpwnpj(self):
        # Personeelskosten per werknemer per jaar
        return self.bezoldigingensocialelastenpensioenen / self.gemiddeldpersoneelsbestand

    # Productiviteit en marges
    def btwmarge(self):
        # Bruto toegevoegdewaardemarge
        return self.brutotoegevoegdewaarde / self.waardevandeproductie

    def rotatievastebainwvproductie(self):
        # Rotatie van de vaste bedrijfsactiva in de waarde van de productie
        return self.waardevandeproductie / self.vastebedrijfsactiva

    # Uur‑ratio's
    def pkpwnpu(self):
        # Personeelskosten per werknemer per uur
        return self.bezoldigingensocialelastenpensioenen / self.aantalgepresteerdeuren

    def aupwnpj(self):
        # Aantal uren per werknemer per jaar
        return self.aantalgepresteerdeuren / self.gemiddeldpersoneelsbestand

    # Investerings‑ en subsidieratio's
    def investeringsgraad(self):
        # Investeringsgraad
        return self.aanschaffingenmva / self.brutotoegevoegdewaarde

    def overheidssubsidieringsgraad(self):
        # Overheidssubsidiëringsgraad
        return self.overheidssubsidies / self.brutotoegevoegdewaarde
