import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from core.analyse import analyseer

app = Flask(__name__)
app.secret_key = os.environ.get("FAO_SECRET_KEY", "fao-jaarrekening-analyse-dev")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")


def _voorbeelden():
    """Verzamel de meegeleverde voorbeeld-CSV's uit de map uploads/."""
    voorbeelden = []
    if not os.path.isdir(UPLOADS_DIR):
        return voorbeelden
    for bestand in sorted(os.listdir(UPLOADS_DIR)):
        if not bestand.lower().endswith(".csv"):
            continue
        slug = bestand[:-4]
        if slug.startswith("jaarrekening_"):
            slug = slug[len("jaarrekening_"):]
        label = slug.replace("_", " ").replace("-", " ").title()
        voorbeelden.append({"slug": slug, "label": label, "bestand": bestand})
    return voorbeelden


def _voorbeeld_pad(slug):
    """Vind veilig het pad van een voorbeeldbestand op basis van zijn slug."""
    for v in _voorbeelden():
        if v["slug"] == slug:
            return os.path.join(UPLOADS_DIR, v["bestand"])
    return None


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
    return render_template("index.html", voorbeelden=_voorbeelden())


@app.route("/analyse", methods=["POST"])
def analyse():
    bestand = request.files.get("bestand")
    if bestand is None or bestand.filename == "":
        flash("Kies eerst een CSV-bestand om te analyseren.")
        return redirect(url_for("index"))
    if not bestand.filename.lower().endswith(".csv"):
        flash("Enkel .csv-bestanden worden ondersteund.")
        return redirect(url_for("index"))
    try:
        resultaat = analyseer(bestand.stream)
    except Exception:  # noqa: BLE001 - toon een nette foutmelding i.p.v. een stacktrace
        flash("Het bestand kon niet gelezen worden. Controleer of het een geldige jaarrekening-CSV is.")
        return redirect(url_for("index"))
    return render_template("resultaat.html", analyse=resultaat, bron=bestand.filename)


@app.route("/voorbeeld/<naam>")
def voorbeeld(naam):
    pad = _voorbeeld_pad(naam)
    if pad is None:
        flash("Dat voorbeeld bestaat niet (meer).")
        return redirect(url_for("index"))
    resultaat = analyseer(pad)
    return render_template("resultaat.html", analyse=resultaat, bron=os.path.basename(pad))


@app.errorhandler(404)
def niet_gevonden(_e):
    return render_template("error.html", error="Deze pagina bestaat niet.", redir=""), 404


@app.errorhandler(413)
def te_groot(_e):
    flash("Het bestand is te groot (max. 5 MB).")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
