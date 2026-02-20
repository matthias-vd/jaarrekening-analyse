from flask import Flask, request, render_template
from core.StructuurBalans import structuurBalans
from core.StructuurMetadata import structuurMetadata
from core.StructuurResultatenRekening import structuurResultatenRekening
from core.StructuurSocialeBalans import structuurSocialeBalans
from core.StructuurToelichting import structuurToelichting
app = Flask(__name__)
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


if __name__ == '__main__':
    app.run()