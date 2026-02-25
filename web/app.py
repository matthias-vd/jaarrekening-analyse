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
    oprichtingskosten = 0.0
    mva = 0.0
    fva = 0.0
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

    for element in read_csv():
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

    #va = fva + iva + mva
    #vla = vordmeerdan1jaar + voorradenbiu + vorderingenmax1jaar + geldbeleggingen + liquidemiddelen + overlopenderekeningenactief
    #activa = va + vla

    #ev = inbreng + hwmw + reserves + overgedragenwinstverlies + kapsubs + voorschotvenverdelingna
    #vv = voorzieningen + uitgesteldebelastingen + schuldenopmeerdan1jaar + schuldenopmax1jaar + overlopenderekeningenpassief
    #passiva = ev + vv

    delta = abs(activa - passiva)

    if delta > 5:
        return render_template('balans-niet-in-evenwicht.html',
                           # METADATA
                           vennootschapsnaam=vennootschapsnaam,boekjaareinde=boekjaareinde,

                           # ACTIEF
                           oprichtingskosten=oprichtingskosten, fva=fva,mva=mva, iva=iva, va=va,
                           vordmeerdan1jaar=vordmeerdan1jaar, voorradenbiu=voorradenbiu,
                           vorderingenmax1jaar=vorderingenmax1jaar, geldbeleggingen=geldbeleggingen,
                           liquidemiddelen=liquidemiddelen, overlopenderekeningenactief=overlopenderekeningenactief,
                           vla=vla, activa=activa,

                           # PASSIEF
                           inbreng=inbreng,hwmw=hwmw,reserves=reserves,overgedragenwinstverlies=overgedragenwinstverlies,
                           kapsubs=kapsubs,voorschotvenverdelingna=voorschotvenverdelingna,ev=ev,voorzieningen=voorzieningen,
                           uitgesteldebelastingen=uitgesteldebelastingen,schuldenopmeerdan1jaar=schuldenopmeerdan1jaar,
                           schuldenopmax1jaar=schuldenopmax1jaar,overlopenderekeningenpassief=overlopenderekeningenpassief,
                           vv=vv,passiva=passiva)
    else:
        return render_template('balans.html',
                           # METADATA
                           vennootschapsnaam=vennootschapsnaam,boekjaareinde=boekjaareinde,

                           # ACTIEF
                           oprichtingskosten=oprichtingskosten, fva=fva, mva=mva, iva=iva, va=va,
                           vordmeerdan1jaar=vordmeerdan1jaar, voorradenbiu=voorradenbiu,
                           vorderingenmax1jaar=vorderingenmax1jaar, geldbeleggingen=geldbeleggingen,
                           liquidemiddelen=liquidemiddelen, overlopenderekeningenactief=overlopenderekeningenactief,
                           vla=vla, activa=activa,

                           # PASSIEF
                           inbreng=inbreng,hwmw=hwmw,reserves=reserves,overgedragenwinstverlies=overgedragenwinstverlies,
                           kapsubs=kapsubs,voorschotvenverdelingna=voorschotvenverdelingna,ev=ev,voorzieningen=voorzieningen,
                           uitgesteldebelastingen=uitgesteldebelastingen,schuldenopmeerdan1jaar=schuldenopmeerdan1jaar,
                           schuldenopmax1jaar=schuldenopmax1jaar,overlopenderekeningenpassief=overlopenderekeningenpassief,
                           vv=vv,passiva=passiva)


    return render_template('input.html')

@app.route('/read_csv', methods=['GET', 'POST'])

def readcsv():
    return read_csv()

if __name__ == '__main__':
    app.run(debug=True)