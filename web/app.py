from flask import Flask, request, render_template
from core.StructuurBalans import structuurBalans
from core.StructuurMetadata import structuurMetadata
from core.StructuurResultatenRekening import structuurResultatenRekening
from core.StructuurSocialeBalans import structuurSocialeBalans
from core.StructuurToelichting import structuurToelichting

from core.read_csv import read_csv
app = Flask(__name__)

DEBUG = 1

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
@app.route('/structuren', methods=['GET', 'POST'])

def selecteer_structuur():
    if request.method == 'POST':
        structuren = request.form['structuur']
        if structuren == 'Balans':
            return structuurBalans
        elif structuren == 'Metadata':
            return structuurMetadata
        elif structuren == 'SocialeBalans':
            return structuurSocialeBalans
        elif structuren == 'ResultatenRekening':
            return structuurResultatenRekening
        elif structuren == 'Toelichting':
            return structuurToelichting
        else:
            return "omhooggevallen frietketel, wat je hebt ingetypt is geen optie"
    return render_template('structuren.html')

@app.route('/balans', methods=['GET', 'POST'])

def balans():
    # METADATA
    vennootschapsnaam = ""
    boekjaareinde = ""

    # ACTIEF
    oprichtingskosten = 0.0
    fva = 0.0
    mva = 0.0
    iva = 0.0
    va = 0.0
    vordmeerdan1jaar = 0.0
    voorradenbiu = 0.0
    vorderingenmax1jaar = 0.0
    geldbeleggingen = 0.0
    liquidemiddelen = 0.0
    overlopenderekeningenactief = 0.0
    vla = 0.0
    activa = 0.0

    # PASSIEF
    inbreng = 0.0
    hwmw = 0.0
    reserves = 0.0
    overgedragenwinstverlies = 0.0
    kapsubs = 0.0
    voorschotvenverdelingna = 0.0
    ev = 0.0
    voorzieningen = 0.0
    uitgesteldebelastingen = 0.0
    schuldenopmeerdan1jaar = 0.0
    schuldenopmax1jaar = 0.0
    overlopenderekeningenpassief = 0.0
    vv = 0.0
    passiva = 0.0

    # RESULTATENREKENING – bedrijfsopbrengsten
    omzet = 0.0
    voorraadwijziging_gereed_en_biu = 0.0
    geproduceerde_vaste_activa = 0.0
    andere_bedrijfsopbrengsten = 0.0
    niet_recurrente_bedrijfsopbrengsten = 0.0
    bedrijfsopbrengsten_totaal = 0.0

    # RESULTATENREKENING – bedrijfskosten
    aankopen_hhg_grond_hulp = 0.0
    voorraadwijziging_hhg_grond_hulp = 0.0
    handelsgoederen_grond_hulpstoffen = 0.0
    diensten_en_diverse_goederen = 0.0
    bezoldigingen_sociale_lasten_pensioenen = 0.0
    afschrijvingen_iva_mva = 0.0
    wvm_voorraden_biu_hv = 0.0
    voorzieningen_risicos_kosten_result = 0.0
    andere_bedrijfskosten = 0.0
    geactiveerde_herstructureringskosten = 0.0
    niet_recurrente_bedrijfskosten = 0.0
    bedrijfskosten_totaal = 0.0

    # RESULTATENREKENING – bedrijfsresultaat
    bedrijfsresultaat = 0.0

    # RESULTATENREKENING – financiële opbrengsten
    fin_opbrengsten_vaste_activa = 0.0
    fin_opbrengsten_vlottende_activa = 0.0
    andere_financiele_opbrengsten = 0.0
    recurrente_financiele_opbrengsten = 0.0
    niet_recurrente_financiele_opbrengsten = 0.0
    financiele_opbrengsten_totaal = 0.0

    # RESULTATENREKENING – financiële kosten
    kosten_van_schulden = 0.0
    wvm_vlottende_activa_overig = 0.0
    andere_financiele_kosten = 0.0
    recurrente_financiele_kosten = 0.0
    niet_recurrente_financiele_kosten = 0.0
    financiele_kosten_totaal = 0.0

    # RESULTATENREKENING – resultaat vóór belasting
    resultaat_voor_belastingen = 0.0
    onttrekking_uitgestelde_belastingen = 0.0
    overboeking_uitgestelde_belastingen = 0.0

    # RESULTATENREKENING – belastingen
    belastingen = 0.0
    regularisering_belastingen = 0.0
    belastingen_op_resultaat = 0.0

    # RESULTATENREKENING – resultaat boekjaar
    resultaat_boekjaar = 0.0
    onttrekking_belastingvrije_reserves = 0.0
    overboeking_belastingvrije_reserves = 0.0
    te_bestemmen_winst_verlies_boekjaar = 0.0

    # RESULTAATVERWERKING – te bestemmen winst/verlies
    te_bestemmen_winst_verlies = 0.0
    overgedragen_winst_verlies_vorig_boekjaar = 0.0

    # RESULTAATVERWERKING – onttrekkingen / toevoegingen EV
    onttrekking_inbreng = 0.0
    onttrekking_reserves = 0.0
    onttrekking_eigen_vermogen = 0.0
    toevoeging_inbreng = 0.0
    toevoeging_wettelijke_reserve = 0.0
    toevoeging_overige_reserves = 0.0
    toevoeging_eigen_vermogen = 0.0

    # RESULTAATVERWERKING – saldo en uitkeringen
    over_te_dragen_winst_verlies = 0.0
    tussenkomst_vennoten_in_verlies = 0.0
    vergoeding_inbreng = 0.0
    vergoeding_bestuurders_zaakvoerders = 0.0
    vergoeding_werknemers = 0.0
    vergoeding_andere_rechthebbenden = 0.0
    uit_te_keren_winst = 0.0

    for element in read_csv(file):
        if element[0] == "Entity name":
            vennootschapsnaam = element[1]
        if element[0] == "Accounting period end date":
            boekjaareinde = element[1]

        if element[0] == "":
            va = round(float(element[1]), 2)
        # ACTIEF
        if element[0] == "21/28":
            va = round(float(element[1]), 2)
        if element[0] == "21":
            iva = round(float(element[1]), 2)
        if element[0] == "22/27":
            mva = round(float(element[1]), 2)
            print("ok")
        if element[0] == "28":
            fva = round(float(element[1]), 2)
        if element[0] == "29":
            vordmeerdan1jaar = round(float(element[1]), 2)
        if element[0] == "3":
            voorradenbiu = round(float(element[1]), 2)
        if element[0] == "40/41":
            vorderingenmax1jaar = round(float(element[1]), 2)
        if element[0] == "50/53":
            geldbeleggingen = round(float(element[1]), 2)
        if element[0] == "54/58":
            liquidemiddelen = round(float(element[1]), 2)
        if element[0] == "490/1":
            overlopenderekeningenactief = round(float(element[1]), 2)
        if element[0] == "29/58":
            vla = round(float(element[1]), 2)
        if element[0] == "20/58":
            activa = round(float(element[1]), 2)

        # PASSIEF
        if element[0] == "10/11":
            inbreng = round(float(element[1]), 2)
        if element[0] == "12":
            hwmw = round(float(element[1]), 2)
        if element[0] == "13":
            reserves = round(float(element[1]), 2)
        if element[0] == "14":
            overgedragenwinstverlies = round(float(element[1]), 2)
            if overgedragenwinstverlies < 0.00:
                overgedragenwinstverlies = f"({abs(overgedragenwinstverlies)})"
            else:
                pass
        if element[0] == "15":
            kapsubs = round(float(element[1]), 2)
        if element[0] == "19":
            voorschotvenverdelingna = round(float(element[1]), 2)
        if element[0] == "10/15":
            ev = round(float(element[1]), 2)
        if element[0] == "160/5":
            voorzieningen = round(float(element[1]), 2)
        if element[0] == "168":
            uitgesteldebelastingen = round(float(element[1]), 2)
        if element[0] == "17":
            schuldenopmeerdan1jaar = round(float(element[1]), 2)
        if element[0] == "42/48":
            schuldenopmax1jaar = round(float(element[1]), 2)
        if element[0] == "492/3":
            overlopenderekeningenpassief = round(float(element[1]), 2)
        if element[0] == "17/49":
            vv = round(float(element[1]), 2)
        if element[0] == "10/49":
            passiva = round(float(element[1]), 2)

        # RESULTATENREKENING

        # Bedrijfsopbrengsten (totaal)
        if element[0] == "70":
            omzet = round(float(element[1]), 2)
        if element[0] == "71":
            voorraadwijziging_gereed_en_biu = round(float(element[1]), 2)
        if element[0] == "72":
            geproduceerde_vaste_activa = round(float(element[1]), 2)
        if element[0] == "74":
            andere_bedrijfsopbrengsten = round(float(element[1]), 2)
        if element[0] == "76A":
            niet_recurrente_bedrijfsopbrengsten = round(float(element[1]), 2)

        # 70/76A = 70 + 71 + 72 + 74 + 76A
        if element[0] == "7076A":
            bedrijfsopbrengsten_totaal = round(float(element[1]), 2)

        # Bedrijfskosten
        if element[0] == "600/8":
            aankopen_hhg_grond_hulp = round(float(element[1]), 2)
        if element[0] == "609":
            voorraadwijziging_hhg_grond_hulp = round(float(element[1]), 2)
        if element[0] == "60":
            handelsgoederen_grond_hulpstoffen = round(float(element[1]), 2)

        if element[0] == "61":
            diensten_en_diverse_goederen = round(float(element[1]), 2)
        if element[0] == "62":
            bezoldigingen_sociale_lasten_pensioenen = round(float(element[1]), 2)
        if element[0] == "630":
            afschrijvingen_iva_mva = round(float(element[1]), 2)
        if element[0] == "631/4":
            wvm_voorraden_biu_hv = round(float(element[1]), 2)
        if element[0] == "635/8":
            voorzieningen_risicos_kosten_result = round(float(element[1]), 2)
        if element[0] == "640/8":
            andere_bedrijfskosten = round(float(element[1]), 2)
        if element[0] == "649":
            geactiveerde_herstructureringskosten = round(float(element[1]), 2)
        if element[0] == "66A":
            niet_recurrente_bedrijfskosten = round(float(element[1]), 2)

        # 60/66A = 60 + 61 + 62 + 630 + 631/4 + 635/8 + 640/8 + 649 + 66A
        if element[0] == "6066A":
            bedrijfskosten_totaal = round(float(element[1]), 2)

        # Bedrijfswinst/verlies
        # 9901 = 70/76A - 60/66A
        if element[0] == "9901":
            bedrijfsresultaat = round(float(element[1]), 2)

        # Financiële opbrengsten
        if element[0] == "750":
            fin_opbrengsten_vaste_activa = round(float(element[1]), 2)
        if element[0] == "751":
            fin_opbrengsten_vlottende_activa = round(float(element[1]), 2)
        if element[0] == "752/9":
            andere_financiele_opbrengsten = round(float(element[1]), 2)
        if element[0] == "75":
            recurrente_financiele_opbrengsten = round(float(element[1]), 2)
        if element[0] == "76B":
            niet_recurrente_financiele_opbrengsten = round(float(element[1]), 2)
        # 75/76B = 75 + 76B
        if element[0] == "7576B":
            financiele_opbrengsten_totaal = round(float(element[1]), 2)

        # Financiële kosten
        if element[0] == "650":
            kosten_van_schulden = round(float(element[1]), 2)
        if element[0] == "651":
            wvm_vlottende_activa_overig = round(float(element[1]), 2)
        if element[0] == "652/9":
            andere_financiele_kosten = round(float(element[1]), 2)
        if element[0] == "65":
            recurrente_financiele_kosten = round(float(element[1]), 2)
        if element[0] == "66B":
            niet_recurrente_financiele_kosten = round(float(element[1]), 2)
        # 65/66B = 65 + 66B
        if element[0] == "6566B":
            financiele_kosten_totaal = round(float(element[1]), 2)

        # Resultaat vóór belasting
        # 9903 = 9901 + 75/76B - 65/66B
        if element[0] == "9903":
            resultaat_voor_belastingen = round(float(element[1]), 2)

        # Uitgestelde belastingen
        if element[0] == "780":
            onttrekking_uitgestelde_belastingen = round(float(element[1]), 2)
        if element[0] == "680":
            overboeking_uitgestelde_belastingen = round(float(element[1]), 2)

        # Belastingen op resultaat
        # 67/77 = 670/3 - 77
        if element[0] == "670/3":
            belastingen = round(float(element[1]), 2)
        if element[0] == "77":
            regularisering_belastingen = round(float(element[1]), 2)
        if element[0] == "677/7":
            belastingen_op_resultaat = round(float(element[1]), 2)

        # Resultaat van het boekjaar
        # 9904 = 9903 + 780 - 680 - 67/77
        if element[0] == "9904":
            resultaat_boekjaar = round(float(element[1]), 2)
        if element[0] == "789":
            onttrekking_belastingvrije_reserves = round(float(element[1]), 2)
        if element[0] == "689":
            overboeking_belastingvrije_reserves = round(float(element[1]), 2)

        # Te bestemmen winst (verlies) van het boekjaar
        # 9905 = 9904 + 789 - 689
        if element[0] == "9905":
            te_bestemmen_winst_verlies_boekjaar = round(float(element[1]), 2)

        # RESULTAATVERWERKING

        # 9906 = 9905 + 14P
        if element[0] == "9906":
            te_bestemmen_winst_verlies = round(float(element[1]), 2)
        if element[0] == "14P":
            overgedragen_winst_verlies_vorig_boekjaar = round(float(element[1]), 2)

        # Onttrekkingen aan het eigen vermogen
        if element[0] == "791":
            onttrekking_inbreng = round(float(element[1]), 2)
        if element[0] == "792":
            onttrekking_reserves = round(float(element[1]), 2)
        # 791/2 = 791 + 792
        if element[0] == "791/2":
            onttrekking_eigen_vermogen = round(float(element[1]), 2)

        # Toevoegingen aan het eigen vermogen
        if element[0] == "691":
            toevoeging_inbreng = round(float(element[1]), 2)
        if element[0] == "6920":
            toevoeging_wettelijke_reserve = round(float(element[1]), 2)
        if element[0] == "6921":
            toevoeging_overige_reserves = round(float(element[1]), 2)
        # 691/2 = 691 + 6920 + 6921
        if element[0] == "691/2":
            toevoeging_eigen_vermogen = round(float(element[1]), 2)

        # Over te dragen winst (verlies)
        # 14 = 9906 + 791/2 - 691/2 + 794 - 694/7
        if element[0] == "14":
            over_te_dragen_winst_verlies = round(float(element[1]), 2)

        if element[0] == "794":
            tussenkomst_vennoten_in_verlies = round(float(element[1]), 2)

        # Uit te keren winst
        if element[0] == "694":
            vergoeding_inbreng = round(float(element[1]), 2)
        if element[0] == "695":
            vergoeding_bestuurders_zaakvoerders = round(float(element[1]), 2)
        if element[0] == "696":
            vergoeding_werknemers = round(float(element[1]), 2)
        if element[0] == "697":
            vergoeding_andere_rechthebbenden = round(float(element[1]), 2)
        # 694/7 = 694 + 695 + 696 + 697
        if element[0] == "694/7":
            uit_te_keren_winst = round(float(element[1]), 2)
    delta = abs(activa - passiva)

    if delta > 5:
        return render_template(
            'balans_resultatenrekening.html',

            # METADATA
            vennootschapsnaam=vennootschapsnaam,
            boekjaareinde=boekjaareinde,

            # ACTIEF
            oprichtingskosten=oprichtingskosten,
            fva=fva,
            mva=mva,
            iva=iva,
            va=va,
            vordmeerdan1jaar=vordmeerdan1jaar,
            voorradenbiu=voorradenbiu,
            vorderingenmax1jaar=vorderingenmax1jaar,
            geldbeleggingen=geldbeleggingen,
            liquidemiddelen=liquidemiddelen,
            overlopenderekeningenactief=overlopenderekeningenactief,
            vla=vla,
            activa=activa,

            # PASSIEF
            inbreng=inbreng,
            hwmw=hwmw,
            reserves=reserves,
            overgedragenwinstverlies=overgedragenwinstverlies,
            kapsubs=kapsubs,
            voorschotvenverdelingna=voorschotvenverdelingna,
            ev=ev,
            voorzieningen=voorzieningen,
            uitgesteldebelastingen=uitgesteldebelastingen,
            schuldenopmeerdan1jaar=schuldenopmeerdan1jaar,
            schuldenopmax1jaar=schuldenopmax1jaar,
            overlopenderekeningenpassief=overlopenderekeningenpassief,
            vv=vv,
            passiva=passiva,

            # RESULTATENREKENING – bedrijfsopbrengsten
            omzet=omzet,
            voorraadwijziging_gereed_en_biu=voorraadwijziging_gereed_en_biu,
            geproduceerde_vaste_activa=geproduceerde_vaste_activa,
            andere_bedrijfsopbrengsten=andere_bedrijfsopbrengsten,
            niet_recurrente_bedrijfsopbrengsten=niet_recurrente_bedrijfsopbrengsten,
            bedrijfsopbrengsten_totaal=bedrijfsopbrengsten_totaal,  # 70/76A

            # RESULTATENREKENING – bedrijfskosten
            aankopen_hhg_grond_hulp=aankopen_hhg_grond_hulp,  # 600/8
            voorraadwijziging_hhg_grond_hulp=voorraadwijziging_hhg_grond_hulp,  # 609
            handelsgoederen_grond_hulpstoffen=handelsgoederen_grond_hulpstoffen,  # 60
            diensten_en_diverse_goederen=diensten_en_diverse_goederen,  # 61
            bezoldigingen_sociale_lasten_pensioenen=bezoldigingen_sociale_lasten_pensioenen,  # 62
            afschrijvingen_iva_mva=afschrijvingen_iva_mva,  # 630
            wvm_voorraden_biu_hv=wvm_voorraden_biu_hv,  # 631/4
            voorzieningen_risicos_kosten_result=voorzieningen_risicos_kosten_result,  # 635/8
            andere_bedrijfskosten=andere_bedrijfskosten,  # 640/8
            geactiveerde_herstructureringskosten=geactiveerde_herstructureringskosten,  # 649
            niet_recurrente_bedrijfskosten=niet_recurrente_bedrijfskosten,  # 66A
            bedrijfskosten_totaal=bedrijfskosten_totaal,  # 60/66A

            # RESULTATENREKENING – bedrijfsresultaat
            bedrijfsresultaat=bedrijfsresultaat,  # 9901

            # RESULTATENREKENING – financiële opbrengsten
            fin_opbrengsten_vaste_activa=fin_opbrengsten_vaste_activa,  # 750
            fin_opbrengsten_vlottende_activa=fin_opbrengsten_vlottende_activa,  # 751
            andere_financiele_opbrengsten=andere_financiele_opbrengsten,  # 752/9
            recurrente_financiele_opbrengsten=recurrente_financiele_opbrengsten,  # 75
            niet_recurrente_financiele_opbrengsten=niet_recurrente_financiele_opbrengsten,  # 76B
            financiele_opbrengsten_totaal=financiele_opbrengsten_totaal,  # 75/76B

            # RESULTATENREKENING – financiële kosten
            kosten_van_schulden=kosten_van_schulden,  # 650
            wvm_vlottende_activa_overig=wvm_vlottende_activa_overig,  # 651
            andere_financiele_kosten=andere_financiele_kosten,  # 652/9
            recurrente_financiele_kosten=recurrente_financiele_kosten,  # 65
            niet_recurrente_financiele_kosten=niet_recurrente_financiele_kosten,  # 66B
            financiele_kosten_totaal=financiele_kosten_totaal,  # 65/66B

            # RESULTATENREKENING – resultaat vóór belasting
            resultaat_voor_belastingen=resultaat_voor_belastingen,  # 9903
            onttrekking_uitgestelde_belastingen=onttrekking_uitgestelde_belastingen,  # 780
            overboeking_uitgestelde_belastingen=overboeking_uitgestelde_belastingen,  # 680

            # RESULTATENREKENING – belastingen
            belastingen=belastingen,  # 670/3
            regularisering_belastingen=regularisering_belastingen,  # 77
            belastingen_op_resultaat=belastingen_op_resultaat,  # 677/7

            # RESULTATENREKENING – resultaat van het boekjaar
            resultaat_boekjaar=resultaat_boekjaar,  # 9904
            onttrekking_belastingvrije_reserves=onttrekking_belastingvrije_reserves,  # 789
            overboeking_belastingvrije_reserves=overboeking_belastingvrije_reserves,  # 689
            te_bestemmen_winst_verlies_boekjaar=te_bestemmen_winst_verlies_boekjaar,  # 9905

            # RESULTAATVERWERKING – te bestemmen winst/verlies
            te_bestemmen_winst_verlies=te_bestemmen_winst_verlies,  # 9906
            overgedragen_winst_verlies_vorig_boekjaar=overgedragen_winst_verlies_vorig_boekjaar,  # 14P

            # RESULTAATVERWERKING – onttrekkingen en toevoegingen EV
            onttrekking_inbreng=onttrekking_inbreng,  # 791
            onttrekking_reserves=onttrekking_reserves,  # 792
            onttrekking_eigen_vermogen=onttrekking_eigen_vermogen,  # 791/2
            toevoeging_inbreng=toevoeging_inbreng,  # 691
            toevoeging_wettelijke_reserve=toevoeging_wettelijke_reserve,  # 6920
            toevoeging_overige_reserves=toevoeging_overige_reserves,  # 6921
            toevoeging_eigen_vermogen=toevoeging_eigen_vermogen,  # 691/2

            # RESULTAATVERWERKING – saldo en uitkeringen
            over_te_dragen_winst_verlies=over_te_dragen_winst_verlies,  # 14
            tussenkomst_vennoten_in_verlies=tussenkomst_vennoten_in_verlies,  # 794
            vergoeding_inbreng=vergoeding_inbreng,  # 694
            vergoeding_bestuurders_zaakvoerders=vergoeding_bestuurders_zaakvoerders,  # 695
            vergoeding_werknemers=vergoeding_werknemers,  # 696
            vergoeding_andere_rechthebbenden=vergoeding_andere_rechthebbenden,  # 697
            uit_te_keren_winst=uit_te_keren_winst  # 694/7
        )

    else:
        return render_template(
            'balans_resultatenrekening.html',

            # METADATA
            vennootschapsnaam=vennootschapsnaam,
            boekjaareinde=boekjaareinde,

            # ACTIEF
            oprichtingskosten=oprichtingskosten,
            fva=fva,
            mva=mva,
            iva=iva,
            va=va,
            vordmeerdan1jaar=vordmeerdan1jaar,
            voorradenbiu=voorradenbiu,
            vorderingenmax1jaar=vorderingenmax1jaar,
            geldbeleggingen=geldbeleggingen,
            liquidemiddelen=liquidemiddelen,
            overlopenderekeningenactief=overlopenderekeningenactief,
            vla=vla,
            activa=activa,

            # PASSIEF
            inbreng=inbreng,
            hwmw=hwmw,
            reserves=reserves,
            overgedragenwinstverlies=overgedragenwinstverlies,
            kapsubs=kapsubs,
            voorschotvenverdelingna=voorschotvenverdelingna,
            ev=ev,
            voorzieningen=voorzieningen,
            uitgesteldebelastingen=uitgesteldebelastingen,
            schuldenopmeerdan1jaar=schuldenopmeerdan1jaar,
            schuldenopmax1jaar=schuldenopmax1jaar,
            overlopenderekeningenpassief=overlopenderekeningenpassief,
            vv=vv,
            passiva=passiva,

            # RESULTATENREKENING – bedrijfsopbrengsten
            omzet=omzet,
            voorraadwijziging_gereed_en_biu=voorraadwijziging_gereed_en_biu,
            geproduceerde_vaste_activa=geproduceerde_vaste_activa,
            andere_bedrijfsopbrengsten=andere_bedrijfsopbrengsten,
            niet_recurrente_bedrijfsopbrengsten=niet_recurrente_bedrijfsopbrengsten,
            bedrijfsopbrengsten_totaal=bedrijfsopbrengsten_totaal,  # 70/76A

            # RESULTATENREKENING – bedrijfskosten
            aankopen_hhg_grond_hulp=aankopen_hhg_grond_hulp,  # 600/8
            voorraadwijziging_hhg_grond_hulp=voorraadwijziging_hhg_grond_hulp,  # 609
            handelsgoederen_grond_hulpstoffen=handelsgoederen_grond_hulpstoffen,  # 60
            diensten_en_diverse_goederen=diensten_en_diverse_goederen,  # 61
            bezoldigingen_sociale_lasten_pensioenen=bezoldigingen_sociale_lasten_pensioenen,  # 62
            afschrijvingen_iva_mva=afschrijvingen_iva_mva,  # 630
            wvm_voorraden_biu_hv=wvm_voorraden_biu_hv,  # 631/4
            voorzieningen_risicos_kosten_result=voorzieningen_risicos_kosten_result,  # 635/8
            andere_bedrijfskosten=andere_bedrijfskosten,  # 640/8
            geactiveerde_herstructureringskosten=geactiveerde_herstructureringskosten,  # 649
            niet_recurrente_bedrijfskosten=niet_recurrente_bedrijfskosten,  # 66A
            bedrijfskosten_totaal=bedrijfskosten_totaal,  # 60/66A

            # RESULTATENREKENING – bedrijfsresultaat
            bedrijfsresultaat=bedrijfsresultaat,  # 9901

            # RESULTATENREKENING – financiële opbrengsten
            fin_opbrengsten_vaste_activa=fin_opbrengsten_vaste_activa,  # 750
            fin_opbrengsten_vlottende_activa=fin_opbrengsten_vlottende_activa,  # 751
            andere_financiele_opbrengsten=andere_financiele_opbrengsten,  # 752/9
            recurrente_financiele_opbrengsten=recurrente_financiele_opbrengsten,  # 75
            niet_recurrente_financiele_opbrengsten=niet_recurrente_financiele_opbrengsten,  # 76B
            financiele_opbrengsten_totaal=financiele_opbrengsten_totaal,  # 75/76B

            # RESULTATENREKENING – financiële kosten
            kosten_van_schulden=kosten_van_schulden,  # 650
            wvm_vlottende_activa_overig=wvm_vlottende_activa_overig,  # 651
            andere_financiele_kosten=andere_financiele_kosten,  # 652/9
            recurrente_financiele_kosten=recurrente_financiele_kosten,  # 65
            niet_recurrente_financiele_kosten=niet_recurrente_financiele_kosten,  # 66B
            financiele_kosten_totaal=financiele_kosten_totaal,  # 65/66B

            # RESULTATENREKENING – resultaat vóór belasting
            resultaat_voor_belastingen=resultaat_voor_belastingen,  # 9903
            onttrekking_uitgestelde_belastingen=onttrekking_uitgestelde_belastingen,  # 780
            overboeking_uitgestelde_belastingen=overboeking_uitgestelde_belastingen,  # 680

            # RESULTATENREKENING – belastingen
            belastingen=belastingen,  # 670/3
            regularisering_belastingen=regularisering_belastingen,  # 77
            belastingen_op_resultaat=belastingen_op_resultaat,  # 677/7

            # RESULTATENREKENING – resultaat van het boekjaar
            resultaat_boekjaar=resultaat_boekjaar,  # 9904
            onttrekking_belastingvrije_reserves=onttrekking_belastingvrije_reserves,  # 789
            overboeking_belastingvrije_reserves=overboeking_belastingvrije_reserves,  # 689
            te_bestemmen_winst_verlies_boekjaar=te_bestemmen_winst_verlies_boekjaar,  # 9905

            # RESULTAATVERWERKING – te bestemmen winst/verlies
            te_bestemmen_winst_verlies=te_bestemmen_winst_verlies,  # 9906
            overgedragen_winst_verlies_vorig_boekjaar=overgedragen_winst_verlies_vorig_boekjaar,  # 14P

            # RESULTAATVERWERKING – onttrekkingen en toevoegingen EV
            onttrekking_inbreng=onttrekking_inbreng,  # 791
            onttrekking_reserves=onttrekking_reserves,  # 792
            onttrekking_eigen_vermogen=onttrekking_eigen_vermogen,  # 791/2
            toevoeging_inbreng=toevoeging_inbreng,  # 691
            toevoeging_wettelijke_reserve=toevoeging_wettelijke_reserve,  # 6920
            toevoeging_overige_reserves=toevoeging_overige_reserves,  # 6921
            toevoeging_eigen_vermogen=toevoeging_eigen_vermogen,  # 691/2

            # RESULTAATVERWERKING – saldo en uitkeringen
            over_te_dragen_winst_verlies=over_te_dragen_winst_verlies,  # 14
            tussenkomst_vennoten_in_verlies=tussenkomst_vennoten_in_verlies,  # 794
            vergoeding_inbreng=vergoeding_inbreng,  # 694
            vergoeding_bestuurders_zaakvoerders=vergoeding_bestuurders_zaakvoerders,  # 695
            vergoeding_werknemers=vergoeding_werknemers,  # 696
            vergoeding_andere_rechthebbenden=vergoeding_andere_rechthebbenden,  # 697
            uit_te_keren_winst=uit_te_keren_winst  # 694/7
        )

    return render_template('input.html')

@app.route('/read_csv', methods=['GET', 'POST'])

def readcsv():
    return read_csv()

if __name__ == '__main__':
    app.run(debug=True)