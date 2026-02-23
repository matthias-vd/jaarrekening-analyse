from flask import Flask, request, render_template
from core.StructuurBalans import structuurBalans
from core.StructuurMetadata import structuurMetadata
from core.StructuurResultatenRekening import structuurResultatenRekening
from core.StructuurSocialeBalans import structuurSocialeBalans
from core.StructuurToelichting import structuurToelichting
app = Flask(__name__)

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
    if request.method == 'POST':
        # ---------- ACTIVA ----------
        # OPRICHTINGSKOSTEN
        oprichtingskosten = float(request.form['oprichtingskosten'])

        # VASTE ACTIVA
        fva = float(request.form['fva'])
        mva = float(request.form['mva'])
        iva = float(request.form['iva'])

        va = float(fva + iva + mva)


        # VLOTTENDE ACTIVA
        vordmeerdan1jaar = float(request.form['vordmeerdan1jaar'])
        voorradenbiu = float(request.form['voorradenbiu'])
        vorderingenmax1jaar = float(request.form['vorderingenmax1jaar'])
        geldbeleggingen = float(request.form['geldbeleggingen'])
        liquidemiddelen = float(request.form['liquidemiddelen'])
        overlopenderekeningenactief = float(request.form['overlopenderekeningenactief'])

        vla = vordmeerdan1jaar + voorradenbiu + vorderingenmax1jaar + geldbeleggingen + liquidemiddelen + overlopenderekeningenactief

        # TOTAAL ACTIVA
        activa = va + vla




        # ---------- PASSIVA ----------

        # EIGEN VERMOGEN
        inbreng = float(request.form['inbreng'])
        hwmw = float(request.form['hwmw'])
        reserves = float(request.form['reserves'])
        overgedragenwinstverlies = float(request.form['overgedragenwinstverlies'])
        kapsubs = float(request.form['kapsubs'])
        voorschotvenverdelingna = float(request.form['voorschotvenverdelingna'])

        ev = inbreng + hwmw + reserves + overgedragenwinstverlies + kapsubs + voorschotvenverdelingna

        # VREEMD VERMOGEN
        voorzieningen = float(request.form['voorzieningen'])
        uitgesteldebelastingen = float(request.form['uitgesteldebelastingen'])
        schuldenopmeerdan1jaar = float(request.form['schuldenopmeerdan1jaar'])
        schuldenopmax1jaar = float(request.form['schuldenopmax1jaar'])
        overlopenderekeningenpassief = float(request.form['overlopenderekeningenpassief'])

        vv = voorzieningen + uitgesteldebelastingen + schuldenopmeerdan1jaar + schuldenopmax1jaar + overlopenderekeningenpassief

        # TOTAAL PASSIVA
        passiva = ev + vv

        if activa != passiva:
            return render_template('balans-niet-in-evenwicht.html', oprichtingskosten=oprichtingskosten, fva=fva,
                               # ACTIEF
                               mva=mva, iva=iva, va=va,
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
            return render_template('balans.html', oprichtingskosten=oprichtingskosten, fva=fva,
                               # ACTIEF
                               mva=mva, iva=iva, va=va,
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

if __name__ == '__main__':
    app.run(debug=True)