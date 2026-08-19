import os

from flask import (
    Flask,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from jinja2 import pass_context

from core import i18n
from core.analyse import analyseer_data
from core.bronnen import BronFout, laad_bron
from core.nbb_api import haal_op_via_kbo

ONDERSTEUNDE_TYPES = (".csv", ".json", ".pdf", ".xbrl", ".xml")
TAAL_COOKIE = "fao-taal"

app = Flask(__name__)
app.secret_key = os.environ.get("FAO_SECRET_KEY", "fao-jaarrekening-analyse-dev")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


# Open Graph-locales per taal (voor social sharing / SEO).
OG_LOCALE = {"nl": "nl_BE", "fr": "fr_BE", "en": "en_GB"}
# Pagina's die geïndexeerd mogen worden, met hun meta-description-sleutel.
INDEXEERBAAR = {"index": "@meta_home", "vergelijk": "@meta_vergelijk"}


@app.before_request
def _bepaal_taal():
    """Kies de UI-taal uit ?lang=, dan de cookie, dan Accept-Language."""
    query = request.args.get("lang")
    if query and query in i18n.TALEN:
        g.lang = query
    else:
        g.lang = i18n.taal_uit_verzoek(
            request.cookies.get(TAAL_COOKIE), request.headers.get("Accept-Language")
        )


@app.after_request
def _bewaar_taal(response):
    """Bewaar een via ?lang= gekozen taal in de cookie (deelbare, crawlbare URL's)."""
    query = request.args.get("lang")
    if query and query in i18n.TALEN and request.cookies.get(TAAL_COOKIE) != query:
        response.set_cookie(TAAL_COOKIE, query, max_age=31536000, samesite="Lax")
    return response


def _seo(lang):
    """Bouw de SEO-context (canonical, hreflang-alternatieven, OG-locales)."""
    root = request.url_root.rstrip("/")
    path = request.path

    def url(code):
        return f"{root}{path}?lang={code}"

    return {
        "canonical": url(lang),
        "alternates": {code: url(code) for code in i18n.TALEN},
        "x_default": url(i18n.STANDAARD),
        "og_locale": OG_LOCALE.get(lang, "nl_BE"),
        "og_locale_alt": [v for k, v in OG_LOCALE.items() if k != lang],
        "site_root": root + "/",
        "image": f"{root}/og-image.svg",
    }


def _structured_data(lang):
    """JSON-LD (schema.org) voor de indexeerbare pagina's, of None."""
    if request.endpoint not in INDEXEERBAAR:
        return None
    root = request.url_root.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "FAO — " + i18n.tl("Financiële Analyse van de Onderneming", lang),
        "url": root + "/",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "inLanguage": list(i18n.TALEN.keys()),
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "description": i18n.t(INDEXEERBAAR[request.endpoint], lang),
        "author": {"@type": "Organization",
                   "name": "FAO — Winter van den Bulck & Matthias Van Duysen"},
    }


@app.context_processor
def _injecteer_i18n():
    lang = getattr(g, "lang", i18n.STANDAARD)
    return {
        "lang": lang,
        "talen": i18n.TALEN,
        "t": lambda sleutel, **kw: i18n.t(sleutel, lang, **kw),
        "tl": lambda tekst: i18n.tl(tekst, lang),
        "seo": _seo(lang),
        "structured_data": _structured_data(lang),
    }


def _flash(sleutel):
    """Flash een (vertaalde) melding op basis van de Nederlandse brontekst."""
    flash(i18n.tl(sleutel, getattr(g, "lang", i18n.STANDAARD)))


@app.template_filter("tl")
@pass_context
def _tl_filter(context, tekst):
    return i18n.tl(tekst, context.get("lang", i18n.STANDAARD))


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
@pass_context
def ratiowaarde(context, waarde, eenheid="", munt="EUR"):
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
        dagen = {"fr": "jours", "en": "days"}.get(context.get("lang"), "dagen")
        return f"{getal:,.0f}".replace(",", "\u00a0") + "\u00a0" + dagen
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
        _flash("Kies eerst een bestand om te analyseren.")
        return redirect(url_for("index"))
    if not bestand.filename.lower().endswith(ONDERSTEUNDE_TYPES):
        _flash("Ondersteunde bestandstypes: CSV, JSON (jsonxbrl) of PDF.")
        return redirect(url_for("index"))
    try:
        data = laad_bron(bestand.filename, bestand.stream)
        resultaat = analyseer_data(data)
    except BronFout as fout:
        _flash(str(fout))
        return redirect(url_for("index"))
    except Exception:  # noqa: BLE001 - toon een nette foutmelding i.p.v. een stacktrace
        _flash("Het bestand kon niet gelezen worden. Controleer of het een geldige jaarrekening is.")
        return redirect(url_for("index"))
    return render_template("resultaat.html", analyse=resultaat, bron=bestand.filename)


@app.route("/fetch", methods=["POST"])
def fetch():
    nummer = (request.form.get("kbo") or "").strip()
    if not nummer:
        _flash("Geef een KBO-/BTW-nummer in.")
        return redirect(url_for("index"))
    try:
        data = haal_op_via_kbo(nummer)
        resultaat = analyseer_data(data)
    except BronFout as fout:
        _flash(str(fout))
        return redirect(url_for("index"))
    except Exception:  # noqa: BLE001
        _flash("Er ging iets mis bij het automatisch ophalen van de jaarrekening.")
        return redirect(url_for("index"))
    return render_template("resultaat.html", analyse=resultaat, bron=f"KBO {nummer}")


@app.route("/vergelijk", methods=["GET", "POST"])
def vergelijk():
    if request.method == "GET":
        return render_template("vergelijk.html")
    lang = getattr(g, "lang", i18n.STANDAARD)
    bestanden = [f for f in request.files.getlist("bestanden") if f and f.filename]
    if len(bestanden) < 2:
        _flash("Kies minstens twee jaarrekeningen om te vergelijken.")
        return redirect(url_for("vergelijk"))
    datasets, fouten = [], []
    for f in bestanden:
        if not f.filename.lower().endswith(ONDERSTEUNDE_TYPES):
            fouten.append(f"{f.filename}: " + i18n.tl("niet-ondersteund bestandstype", lang))
            continue
        try:
            datasets.append(laad_bron(f.filename, f.stream))
        except BronFout as fout:
            fouten.append(f"{f.filename}: {i18n.tl(str(fout), lang)}")
        except Exception:  # noqa: BLE001
            fouten.append(f"{f.filename}: " + i18n.tl("kon niet gelezen worden", lang))
    if len(datasets) < 2:
        melding = i18n.tl("Kon niet minstens twee geldige jaarrekeningen inlezen.", lang)
        if fouten:
            melding += " " + " · ".join(fouten)
        flash(melding)
        return redirect(url_for("vergelijk"))
    from core.vergelijk import bouw_vergelijking
    vergelijking = bouw_vergelijking(datasets)
    _vertaal_grafiek(vergelijking.get("grafiek_eur"), lang)
    _vertaal_grafiek(vergelijking.get("grafiek_ratio"), lang)
    return render_template("vergelijk.html", vergelijking=vergelijking, fouten=fouten)


def _vertaal_grafiek(grafiek, lang):
    """Vertaal de reeksnamen (metrieken) van een grafiekstructuur, incl. '(eenheid)'."""
    if not grafiek:
        return
    for reeks in grafiek.get("reeksen", []):
        naam = reeks.get("naam", "")
        vert = i18n.tl(naam, lang)
        if vert == naam and " (" in naam:
            basis, _, rest = naam.partition(" (")
            vert = i18n.tl(basis, lang) + " (" + rest
        reeks["naam"] = vert


_FAVICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
    "<rect width='64' height='64' rx='14' fill='#2CCCC4'/>"
    "<text x='32' y='43' font-family='Arial,Helvetica,sans-serif' font-size='23' "
    "font-weight='bold' fill='#ffffff' text-anchor='middle'>FAO</text></svg>"
)

_OG_IMAGE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630' viewBox='0 0 1200 630'>"
    "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
    "<stop offset='0' stop-color='#0c7d77'/><stop offset='1' stop-color='#0a5f5b'/>"
    "</linearGradient></defs><rect width='1200' height='630' fill='url(#g)'/>"
    "<rect x='72' y='72' width='96' height='96' rx='22' fill='#2CCCC4'/>"
    "<text x='120' y='138' font-family='Arial,Helvetica,sans-serif' font-size='44' "
    "font-weight='bold' fill='#ffffff' text-anchor='middle'>FAO</text>"
    "<text x='72' y='330' font-family='Arial,Helvetica,sans-serif' font-size='72' "
    "font-weight='bold' fill='#ffffff'>Financiële Analyse</text>"
    "<text x='72' y='412' font-family='Arial,Helvetica,sans-serif' font-size='72' "
    "font-weight='bold' fill='#dffdfa'>van de Onderneming</text>"
    "<text x='72' y='500' font-family='Arial,Helvetica,sans-serif' font-size='34' "
    "fill='#b6e8e4'>Balans · resultatenrekening · ratio's · risico — NL / FR / EN</text></svg>"
)


@app.route("/favicon.svg")
def favicon():
    return Response(_FAVICON_SVG, mimetype="image/svg+xml")


@app.route("/og-image.svg")
def og_image():
    return Response(_OG_IMAGE_SVG, mimetype="image/svg+xml")


@app.route("/robots.txt")
def robots():
    root = request.url_root.rstrip("/")
    regels = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /analyse",
        "Disallow: /fetch",
        f"Sitemap: {root}/sitemap.xml",
        "",
    ]
    return Response("\n".join(regels), mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    root = request.url_root.rstrip("/")
    paden = ["/", "/vergelijk"]
    regels = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" "
        "xmlns:xhtml=\"http://www.w3.org/1999/xhtml\">",
    ]
    for pad in paden:
        loc = f"{root}{pad}?lang={i18n.STANDAARD}"
        regels.append("  <url>")
        regels.append(f"    <loc>{loc}</loc>")
        for code in i18n.TALEN:
            regels.append(
                f"    <xhtml:link rel=\"alternate\" hreflang=\"{code}\" "
                f"href=\"{root}{pad}?lang={code}\"/>"
            )
        regels.append(
            f"    <xhtml:link rel=\"alternate\" hreflang=\"x-default\" "
            f"href=\"{root}{pad}?lang={i18n.STANDAARD}\"/>"
        )
        regels.append("  </url>")
    regels.append("</urlset>")
    return Response("\n".join(regels), mimetype="application/xml")


@app.errorhandler(404)
def niet_gevonden(_e):
    melding = i18n.tl("Deze pagina bestaat niet.", getattr(g, "lang", i18n.STANDAARD))
    return render_template("error.html", error=melding, redir=""), 404


@app.errorhandler(413)
def te_groot(_e):
    _flash("Het bestand is te groot (max. 5 MB).")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
