import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from core.analyse import analyseer_data
from core.bronnen import BronFout, laad_bron
from core.nbb_api import haal_op_via_kbo

ONDERSTEUNDE_TYPES = (".csv", ".json", ".pdf", ".xbrl", ".xml")

app = Flask(__name__)
app.secret_key = os.environ.get("FAO_SECRET_KEY", "fao-jaarrekening-analyse-dev")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


@app.template_filter("bedrag")
def bedrag(waarde):
    """Formatteer een bedrag in Belgische notatie (1.234.567,89), negatief tussen haakjes."""
    if waarde is None or waarde == "":
        return ""
    try:
        getal = float(waarde)
    except (TypeError, ValueError):
        return str(waarde)
    negatief = getal < 0
    tekst = f"{abs(getal):,.2f}".replace(",", "\u00a0").replace(".", ",")
    return f"({tekst})" if negatief else tekst


@app.template_filter("ratiowaarde")
def ratiowaarde(waarde, eenheid="", munt="EUR"):
    """Formatteer een ratiowaarde volgens haar eenheid."""
    if waarde is None:
        return "—"
    try:
        getal = float(waarde)
    except (TypeError, ValueError):
        return str(waarde)
    if eenheid == "%":
        return f"{getal:,.1f}".replace(",", "\u00a0") + "\u00a0%"
    if eenheid == "x":
        return f"{getal:,.2f}".replace(",", "\u00a0") + "\u00a0×"
    if eenheid == "dagen":
        return f"{getal:,.0f}".replace(",", "\u00a0") + "\u00a0dagen"
    if eenheid == "000 EUR":
        return f"{getal:,.1f}".replace(",", "\u00a0") + "\u00a0k" + munt
    if eenheid == "EUR":
        return bedrag(getal) + "\u00a0" + munt
    return f"{getal:,.2f}".replace(",", "\u00a0")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    bestand = request.files.get("bestand")
    if bestand is None or bestand.filename == "":
        flash("Kies eerst een bestand om te analyseren.")
        return redirect(url_for("index"))
    if not bestand.filename.lower().endswith(ONDERSTEUNDE_TYPES):
        flash("Ondersteunde bestandstypes: CSV, JSON (jsonxbrl) of PDF.")
        return redirect(url_for("index"))
    try:
        data = laad_bron(bestand.filename, bestand.stream)
        resultaat = analyseer_data(data)
    except BronFout as fout:
        flash(str(fout))
        return redirect(url_for("index"))
    except Exception:  # noqa: BLE001 - toon een nette foutmelding i.p.v. een stacktrace
        flash("Het bestand kon niet gelezen worden. Controleer of het een geldige jaarrekening is.")
        return redirect(url_for("index"))
    return render_template("resultaat.html", analyse=resultaat, bron=bestand.filename)


@app.route("/fetch", methods=["POST"])
def fetch():
    nummer = (request.form.get("kbo") or "").strip()
    if not nummer:
        flash("Geef een KBO-/BTW-nummer in.")
        return redirect(url_for("index"))
    try:
        data = haal_op_via_kbo(nummer)
        resultaat = analyseer_data(data)
    except BronFout as fout:
        flash(str(fout))
        return redirect(url_for("index"))
    except Exception:  # noqa: BLE001
        flash("Er ging iets mis bij het automatisch ophalen van de jaarrekening.")
        return redirect(url_for("index"))
    return render_template("resultaat.html", analyse=resultaat, bron=f"KBO {nummer}")


@app.route("/vergelijk", methods=["GET", "POST"])
def vergelijk():
    if request.method == "GET":
        return render_template("vergelijk.html")
    bestanden = [f for f in request.files.getlist("bestanden") if f and f.filename]
    if len(bestanden) < 2:
        flash("Kies minstens twee jaarrekeningen om te vergelijken.")
        return redirect(url_for("vergelijk"))
    datasets, fouten = [], []
    for f in bestanden:
        if not f.filename.lower().endswith(ONDERSTEUNDE_TYPES):
            fouten.append(f"{f.filename}: niet-ondersteund bestandstype")
            continue
        try:
            datasets.append(laad_bron(f.filename, f.stream))
        except BronFout as fout:
            fouten.append(f"{f.filename}: {fout}")
        except Exception:  # noqa: BLE001
            fouten.append(f"{f.filename}: kon niet gelezen worden")
    if len(datasets) < 2:
        melding = "Kon niet minstens twee geldige jaarrekeningen inlezen."
        if fouten:
            melding += " " + " · ".join(fouten)
        flash(melding)
        return redirect(url_for("vergelijk"))
    from core.vergelijk import bouw_vergelijking
    vergelijking = bouw_vergelijking(datasets)
    return render_template("vergelijk.html", vergelijking=vergelijking, fouten=fouten)


@app.errorhandler(404)
def niet_gevonden(_e):
    return render_template("error.html", error="Deze pagina bestaat niet.", redir=""), 404


@app.errorhandler(413)
def te_groot(_e):
    flash("Het bestand is te groot (max. 5 MB).")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
