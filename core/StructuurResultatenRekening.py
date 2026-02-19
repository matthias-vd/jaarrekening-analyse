structuurResultatenRekening = [
    # Root
    {"Code": "", "Rubriek": "RESULTATENREKENING", "Parent_Code": None, "Niveau": 0, "Toelichting": "", "Waarde": None},

    # Bedrijfsopbrengsten
    {"Code": "", "Rubriek": "Bedrijfsopbrengsten", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "7076A", "Rubriek": "Bedrijfsopbrengsten (totaal)", "Parent_Code": "Bedrijfsopbrengsten", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "70", "Rubriek": "Omzet", "Parent_Code": "7076A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},
    {"Code": "71", "Rubriek": "Voorraad goederen in bewerking en gereed product en bestellingen in uitvoering (toename (+)/afname (-))", "Parent_Code": "7076A", "Niveau": 3, "Toelichting": "", "Waarde": None},
    {"Code": "72", "Rubriek": "Geproduceerde vaste activa", "Parent_Code": "7076A", "Niveau": 3, "Toelichting": "", "Waarde": None},
    {"Code": "74", "Rubriek": "Andere bedrijfsopbrengsten", "Parent_Code": "7076A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},
    {"Code": "76A", "Rubriek": "Niet-recurrente bedrijfsopbrengsten", "Parent_Code": "7076A", "Niveau": 3, "Toelichting": "6.12", "Waarde": None},

    # Bedrijfskosten
    {"Code": "", "Rubriek": "Bedrijfskosten", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "6066A", "Rubriek": "Bedrijfskosten (totaal)", "Parent_Code": "Bedrijfskosten", "Niveau": 2, "Toelichting": "", "Waarde": None},

    {"Code": "60", "Rubriek": "Handelsgoederen, grond- en hulpstoffen", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "", "Waarde": None},
    {"Code": "600/8", "Rubriek": "Aankopen", "Parent_Code": "60", "Niveau": 4, "Toelichting": "", "Waarde": None},
    {"Code": "609", "Rubriek": "Voorraad (afname (+)/toename (-))", "Parent_Code": "60", "Niveau": 4, "Toelichting": "", "Waarde": None},

    {"Code": "61", "Rubriek": "Diensten en diverse goederen", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "", "Waarde": None},

    {"Code": "62", "Rubriek": "Bezoldigingen, sociale lasten en pensioenen", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},

    {"Code": "630", "Rubriek": "Afschrijvingen en waardeverminderingen op oprichtingskosten, immateriële en materiële vaste activa", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "", "Waarde": None},

    {"Code": "631/4", "Rubriek": "Waardeverminderingen op voorraden, bestellingen in uitvoering en handelsvorderingen (toevoegingen (+)/terugnemingen (-))", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},

    {"Code": "635/8", "Rubriek": "Voorzieningen voor risico's en kosten (toevoegingen (+)/bestedingen en terugnemingen (-))", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},

    {"Code": "640/8", "Rubriek": "Andere bedrijfskosten", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "6.10", "Waarde": None},
    {"Code": "649", "Rubriek": "Als herstructureringskosten geactiveerde bedrijfskosten", "Parent_Code": "640/8", "Niveau": 4, "Toelichting": "", "Waarde": None},

    {"Code": "66A", "Rubriek": "Niet-recurrente bedrijfskosten", "Parent_Code": "6066A", "Niveau": 3, "Toelichting": "6.12", "Waarde": None},

    {"Code": "9901", "Rubriek": "Bedrijfswinst (Bedrijfsverlies (-))", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},

    # Financiële opbrengsten
    {"Code": "", "Rubriek": "Financiële opbrengsten", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "7576B", "Rubriek": "Financiële opbrengsten (totaal)", "Parent_Code": "Financiële opbrengsten", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "75", "Rubriek": "Recurrente financiële opbrengsten", "Parent_Code": "7576B", "Niveau": 3, "Toelichting": "", "Waarde": None},
    {"Code": "750", "Rubriek": "Opbrengsten uit financiële vaste activa", "Parent_Code": "75", "Niveau": 4, "Toelichting": "", "Waarde": None},
    {"Code": "751", "Rubriek": "Opbrengsten uit vlottende activa", "Parent_Code": "75", "Niveau": 4, "Toelichting": "", "Waarde": None},
    {"Code": "752/9", "Rubriek": "Andere financiële opbrengsten", "Parent_Code": "75", "Niveau": 4, "Toelichting": "6.11", "Waarde": None},
    {"Code": "76B", "Rubriek": "Niet-recurrente financiële opbrengsten", "Parent_Code": "7576B", "Niveau": 3, "Toelichting": "6.12", "Waarde": None},

    # Financiële kosten
    {"Code": "", "Rubriek": "Financiële kosten", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "6566B", "Rubriek": "Financiële kosten (totaal)", "Parent_Code": "Financiële kosten", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "65", "Rubriek": "Recurrente financiële kosten", "Parent_Code": "6566B", "Niveau": 3, "Toelichting": "6.11", "Waarde": None},
    {"Code": "650", "Rubriek": "Kosten van schulden", "Parent_Code": "65", "Niveau": 4, "Toelichting": "", "Waarde": None},
    {"Code": "651", "Rubriek": "Waardeverminderingen op vlottende activa andere dan voorraden, bestellingen in uitvoering en handelsvorderingen (toevoegingen (+)/terugnemingen (-))", "Parent_Code": "65", "Niveau": 4, "Toelichting": "", "Waarde": None},
    {"Code": "652/9", "Rubriek": "Andere financiële kosten", "Parent_Code": "65", "Niveau": 4, "Toelichting": "6.11", "Waarde": None},
    {"Code": "66B", "Rubriek": "Niet-recurrente financiële kosten", "Parent_Code": "6566B", "Niveau": 3, "Toelichting": "6.12", "Waarde": None},

    # Resultaat vóór en na belasting
    {"Code": "9903", "Rubriek": "Winst (Verlies) van het boekjaar vóór belasting", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "780", "Rubriek": "Onttrekking aan de uitgestelde belastingen", "Parent_Code": "9903", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "680", "Rubriek": "Overboeking naar de uitgestelde belastingen", "Parent_Code": "9903", "Niveau": 2, "Toelichting": "", "Waarde": None},

    {"Code": "677/7", "Rubriek": "Belastingen op het resultaat", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "6.13", "Waarde": None},
    {"Code": "670/3", "Rubriek": "Belastingen", "Parent_Code": "677/7", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "77", "Rubriek": "Regularisering van belastingen en terugneming van voorzieningen voor belastingen", "Parent_Code": "677/7", "Niveau": 2, "Toelichting": "", "Waarde": None},

    {"Code": "9904", "Rubriek": "Winst (Verlies) van het boekjaar", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "789", "Rubriek": "Onttrekking aan de belastingvrije reserves", "Parent_Code": "9904", "Niveau": 2, "Toelichting": "", "Waarde": None},
    {"Code": "689", "Rubriek": "Overboeking naar de belastingvrije reserves", "Parent_Code": "9904", "Niveau": 2, "Toelichting": "", "Waarde": None},

    {"Code": "9905", "Rubriek": "Te bestemmen winst (verlies) van het boekjaar", "Parent_Code": "RESULTATENREKENING", "Niveau": 1, "Toelichting": "", "Waarde": None},

    # RESULTAATVERWERKING

    # Root
    {"Code": "", "Rubriek": "RESULTAATVERWERKING", "Parent_Code": None, "Niveau": 0, "Toelichting": "", "Waarde": None},

    {"Code": "9906", "Rubriek": "Te bestemmen winst (verlies)", "Parent_Code": "RESULTAATVERWERKING", "Niveau": 1,
     "Toelichting": "", "Waarde": None},
    {"Code": "9905", "Rubriek": "Te bestemmen winst (verlies) van het boekjaar", "Parent_Code": "9906", "Niveau": 2,
     "Toelichting": "", "Waarde": None},
    {"Code": "14P", "Rubriek": "Overgedragen winst (verlies) van het vorige boekjaar", "Parent_Code": "9906",
     "Niveau": 2, "Toelichting": "", "Waarde": None},

    {"Code": "791/2", "Rubriek": "Onttrekking aan het eigen vermogen", "Parent_Code": "RESULTAATVERWERKING",
     "Niveau": 1, "Toelichting": "", "Waarde": None},
    {"Code": "791", "Rubriek": "Onttrekking aan de inbreng", "Parent_Code": "791/2", "Niveau": 2, "Toelichting": "",
     "Waarde": None},
    {"Code": "792", "Rubriek": "Onttrekking aan de reserves", "Parent_Code": "791/2", "Niveau": 2, "Toelichting": "",
     "Waarde": None},

    {"Code": "691/2", "Rubriek": "Toevoeging aan het eigen vermogen", "Parent_Code": "RESULTAATVERWERKING", "Niveau": 1,
     "Toelichting": "", "Waarde": None},
    {"Code": "691", "Rubriek": "Toevoeging aan de inbreng", "Parent_Code": "691/2", "Niveau": 2, "Toelichting": "",
     "Waarde": None},
    {"Code": "6920", "Rubriek": "Toevoeging aan de wettelijke reserve", "Parent_Code": "691/2", "Niveau": 2,
     "Toelichting": "", "Waarde": None},
    {"Code": "6921", "Rubriek": "Toevoeging aan de overige reserves", "Parent_Code": "691/2", "Niveau": 2,
     "Toelichting": "", "Waarde": None},

    {"Code": "14", "Rubriek": "Over te dragen winst (verlies)", "Parent_Code": "RESULTAATVERWERKING", "Niveau": 1,
     "Toelichting": "", "Waarde": None},

    {"Code": "794", "Rubriek": "Tussenkomst van de vennoten in het verlies", "Parent_Code": "RESULTAATVERWERKING",
     "Niveau": 1, "Toelichting": "", "Waarde": None},

    {"Code": "694/7", "Rubriek": "Uit te keren winst", "Parent_Code": "RESULTAATVERWERKING", "Niveau": 1,
     "Toelichting": "", "Waarde": None},
    {"Code": "694", "Rubriek": "Vergoeding van de inbreng", "Parent_Code": "694/7", "Niveau": 2, "Toelichting": "",
     "Waarde": None},
    {"Code": "695", "Rubriek": "Vergoeding – bestuurders of zaakvoerders", "Parent_Code": "694/7", "Niveau": 2,
     "Toelichting": "", "Waarde": None},
    {"Code": "696", "Rubriek": "Vergoeding – werknemers", "Parent_Code": "694/7", "Niveau": 2, "Toelichting": "",
     "Waarde": None},
    {"Code": "697", "Rubriek": "Vergoeding – andere rechthebbenden", "Parent_Code": "694/7", "Niveau": 2,
     "Toelichting": "", "Waarde": None},
]