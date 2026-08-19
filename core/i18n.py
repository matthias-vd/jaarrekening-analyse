"""Meertaligheid (NL / FR / EN) voor FAO.

Aanpak: de Nederlandse brontekst is meteen de vertaalsleutel. ``tl(tekst, taal)``
zoekt de Nederlandse string op in :data:`VERT` en geeft de Franse of Engelse
vertaling terug; ontbreekt ze, dan valt hij netjes terug op het Nederlands.
Synthetische sleutels (met een ``@``-prefix) worden gebruikt voor blokken met
HTML of tijdelijke aanduidingen ({...}), die via ``t(sleutel, taal, **kw)`` worden
opgehaald en geformatteerd.

Zo hoeft de kernlogica (analyse, ratio's, risico, ...) niet aangepast te worden:
ze blijft Nederlandse labels produceren, die op het weergavemoment vertaald worden.
"""

TALEN = {"nl": "Nederlands", "fr": "Français", "en": "English"}
STANDAARD = "nl"


def normaliseer_taal(code):
    """Geef een geldige taalcode terug (nl/fr/en), of de standaardtaal."""
    if not code:
        return STANDAARD
    code = str(code).strip().lower()[:2]
    return code if code in TALEN else STANDAARD


def taal_uit_verzoek(cookie_waarde, accept_language=None):
    """Bepaal de taal uit de cookie, met de Accept-Language-header als terugval."""
    if cookie_waarde:
        return normaliseer_taal(cookie_waarde)
    if accept_language:
        for stuk in str(accept_language).replace("-", "_").split(","):
            code = stuk.split(";")[0].strip().lower()[:2]
            if code in TALEN:
                return code
    return STANDAARD


def _kies(paar, taal):
    fr, en = paar
    if taal == "fr":
        return fr
    if taal == "en":
        return en
    return None


def tl(tekst, taal="nl"):
    """Vertaal een Nederlandse brontekst (of synthetische ``@``-sleutel) naar ``taal``.

    Gewone teksten hebben de Nederlandse brontekst als sleutel; synthetische
    sleutels (``@...``) krijgen hun Nederlandse tekst uit :data:`SYNTH_NL`.
    """
    taal = normaliseer_taal(taal)
    if tekst is None or not isinstance(tekst, str):
        return tekst
    if taal == "nl":
        return SYNTH_NL.get(tekst, tekst) if tekst.startswith("@") else tekst
    paar = VERT.get(tekst) or VERT.get(tekst.strip())
    if not paar:
        return SYNTH_NL.get(tekst, tekst)
    vert = _kies(paar, taal)
    return vert if vert else SYNTH_NL.get(tekst, tekst)


def t(sleutel, taal="nl", **kw):
    """Haal een (eventueel synthetische) sleutel op en formatteer met ``kw``."""
    s = tl(sleutel, taal)
    if kw:
        try:
            s = s.format(**kw)
        except (KeyError, IndexError, ValueError):
            pass
    return s


# Nederlandse brontekst voor synthetische (@-)sleutels: gebruikt bij taal == nl
# en als terugval. HTML/opmaak wordt hier bewust behouden.
SYNTH_NL = {
    "@meta_home": (
        "Analyseer gratis elke Belgische jaarrekening (NBB): balans en resultatenrekening volgens de "
        "wettelijke structuur, ratio's met sectorvergelijking, gezondheidsbarometer, bestuurders en "
        "meerjarenvergelijking. Upload CSV, JSON of PDF, of zoek op KBO-/BTW-nummer."
    ),
    "@meta_vergelijk": (
        "Vergelijk meerdere Belgische jaarrekeningen naast elkaar of over de jaren heen: kerncijfers, "
        "ratio's en grafieken met een gunstig/ongunstig-oordeel."
    ),
    "@meta_result": (
        "Financiële analyse van de jaarrekening: balans, resultatenrekening, ratio's, "
        "risico en betrouwbaarheid."
    ),
    "@title_default": "FAO — Financiële Analyse van de Onderneming",
    "@title_vergelijk": "Vergelijken — Financiële Analyse van de Onderneming",
    "@title_error": "Pagina niet gevonden — FAO",
    "@footer": (
        "FAO — een project van Winter van den Bulck &amp; Matthias Van Duysen · "
        "Analyse conform de wettelijke structuur van de Belgische jaarrekening."
    ),
    "@hero_h1": "Doorgrond elke <span class=\"grad\">Belgische jaarrekening</span> in seconden.",
    "@hero_lead": (
        "Upload een CSV, JSON of PDF — of vul gewoon een KBO-nummer in. Je krijgt de balans en "
        "resultatenrekening volgens de wettelijke structuur, ratio's met sectorvergelijking, "
        "een gezondheidsbarometer, bestuurders en vergelijkingen over de jaren."
    ),
    "@pill_balans": "Balans &amp; resultatenrekening",
    "@upload_small": ".csv · .json · .pdf — max. 5&nbsp;MB",
    "@nbb_note": "Gratis NBB-webservice; vereist eenmalig een sleutel (<code>NBB_CBSO_SUBSCRIPTION_KEY</code>).",
    "@feat_balans": "Balans &amp; resultatenrekening",
    "@feat_ratios": "Ratio's &amp; sectorvergelijking",
    "@feat_vergelijk": "Vergelijken &amp; trends",
    "@feat_bronnen": "CSV, JSON (jsonxbrl) en PDF (NL &amp; FR), of automatisch ophalen via het KBO-/BTW-nummer.",
    "@feat_identificatie": "Identificatie &amp; kerncijfers",
    "@codes_herkend": "{h} van {tot} codes herkend",
    "@conformiteit_count": "— {ok} controles ok, {fout} met verschil",
    "@conformiteit_uitleg": (
        "FAO controleert automatisch de belangrijkste wettelijke optelsommen van de balans "
        "en de resultatenrekening. Bekijk het tabblad <strong>Controle</strong> voor alle details."
    ),
    "@optelsom_fout": "{fout} optelsom(men) klopt niet",
    "@kasstroom_uitleg": (
        "Vereenvoudigd herwerkt kasstromenoverzicht, afgeleid uit het huidige en vorige boekjaar. "
        "<strong>Benadering</strong>: de exacte niet-kaskosten en enkele financieringslijnen vergen "
        "toelichtingsdata die niet altijd beschikbaar is."
    ),
    "@evolutie_titel": "Evolutie t.o.v. vorig boekjaar",
    "@evolutie_count": "— {g} gunstig · {o} ongunstig",
    "@ratio_titel": "Ratioanalyse &amp; sectorvergelijking",
    "@ratio_intro": (
        "De ratio's uit de cursus (toegevoegde waarde, rendabiliteit, solvabiliteit, liquiditeit), "
        "berekend uit de balans en resultatenrekening. Waarden met het label "
        "<span class=\"tag benadering\">benadering</span> gebruiken een schatting van de niet-kaskosten "
        "of de financiële kosten uit de beschikbare rubrieken."
    ),
    "@sector_summary": "<strong>Over de sectorvergelijking</strong> — is dit mogelijk?",
    "@sector_p1": (
        "Ja — de <strong>NBB Balanscentrale</strong> publiceert via NBB.Stat per "
        "<strong>NACE-BEL-sector</strong> de spreiding van deze ratio's in kwartielen (Q1/Q2/Q3). "
        "Een onderneming vergelijken met haar sector betekent kijken waar haar ratio valt "
        "t.o.v. die kwartielen."
    ),
    "@sector_p2": (
        "<strong>Beperking:</strong> de gedeponeerde jaarrekening-CSV bevat géén NACE-code, "
        "dus de sector kan niet automatisch worden afgeleid. Hieronder wordt daarom een "
        "vast referentieprofiel gebruikt:"
    ),
    "@baro_krediet_titel": "Gezondheidsbarometer &amp; kredietrichtlijn",
    "@altman_uitleg": (
        "Z'' = 3,25 + 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4 — variant voor niet-beursgenoteerde "
        "ondernemingen. Zones: &gt; 2,6 veilig · 1,1–2,6 grijs · &lt; 1,1 nood."
    ),
    "@kwadrant_uitleg": (
        "Kruising rendabiliteit × liquiditeit (cursus FAO, Tabel 16.1): gezond · tijdelijk ziek · "
        "chronisch ziek · stervend."
    ),
    "@ov82_hint": "Lineaire discriminantscore · afkapgrens ≈ {a} (hoger = gezonder)",
    "@fito_titel": "SIM05 — FiTo-score (simpel-intuïtief)",
    "@beneish_hint": "Drempel: M &gt; −1,78 wijst op verhoogde kans (benadering, 2 boekjaren).",
    "@bestuurders_titel": "Bestuurders, zaakvoerders &amp; commissarissen",
    "@vgl_intro": (
        "Upload meerdere jaarrekeningen (CSV, JSON of PDF) — meerdere boekjaren van dezelfde onderneming "
        "voor de evolutie, of verschillende ondernemingen naast elkaar. FAO zet de kerncijfers en ratio's "
        "op een rij, toont de evolutie in grafieken en beoordeelt of ze gunstig of ongunstig is."
    ),
    "@aantal_jaarrekeningen": "{n} jaarrekeningen",
    "@aantal_gunstig": "{n} gunstige evoluties",
    "@aantal_ongunstig": "{n} ongunstige evoluties",
    "@kerncijfers_eur": "Kerncijfers (in {munt})",
    "@detailvgl": "Detailvergelijking &amp; evolutie",
}


# nl -> (fr, en)
VERT = {
    # ============================ Algemeen / UI ============================
    "Financiële Analyse van de Onderneming": ("Analyse financière de l'entreprise", "Financial Analysis of the Company"),
    "Indicatieve tool, gebruik op eigen risico": ("Outil indicatif, utilisation à vos risques", "Indicative tool, use at your own risk"),
    "Start": ("Accueil", "Home"),
    "Uploaden": ("Importer", "Upload"),
    "Vergelijken": ("Comparer", "Compare"),
    "Thema": ("Thème", "Theme"),
    "Kies een thema": ("Choisir un thème", "Choose a theme"),
    "Taal": ("Langue", "Language"),
    "Licht": ("Clair", "Light"),
    "Donker": ("Sombre", "Dark"),
    "Oceaan": ("Océan", "Ocean"),
    "Bos": ("Forêt", "Forest"),
    "Zonsondergang": ("Coucher de soleil", "Sunset"),
    "Koninklijk": ("Royal", "Royal"),
    "Analyse": ("Analyse", "Analysis"),
    "@meta_home": (
        "Analysez gratuitement tout compte annuel belge (BNB) : bilan et compte de résultats selon la "
        "structure légale, ratios avec comparaison sectorielle, baromètre de santé, administrateurs et "
        "comparaison pluriannuelle. Importez CSV, JSON ou PDF, ou recherchez par numéro BCE/TVA.",
        "Freely analyse any Belgian annual account (NBB): balance sheet and income statement in the legal "
        "structure, ratios with sector comparison, health barometer, directors and multi-year comparison. "
        "Upload CSV, JSON or PDF, or search by CBE/VAT number.",
    ),
    "@meta_vergelijk": (
        "Comparez plusieurs comptes annuels belges côte à côte ou dans le temps : chiffres clés, ratios "
        "et graphiques avec un verdict favorable/défavorable.",
        "Compare multiple Belgian annual accounts side by side or over time: key figures, ratios and "
        "charts with a favourable/unfavourable verdict.",
    ),
    "@meta_result": (
        "Analyse financière des comptes annuels : bilan, compte de résultats, ratios, risque et fiabilité.",
        "Financial analysis of the annual accounts: balance sheet, income statement, ratios, risk and reliability.",
    ),
    "@title_default": ("FAO — Analyse financière de l'entreprise", "FAO — Financial Analysis of the Company"),
    "@title_vergelijk": ("Comparer — Analyse financière de l'entreprise", "Compare — Financial Analysis of the Company"),
    "@title_error": ("Page introuvable — FAO", "Page not found — FAO"),
    "@footer": (
        "FAO — un projet de Winter van den Bulck &amp; Matthias Van Duysen · "
        "Analyse conforme à la structure légale des comptes annuels belges.",
        "FAO — a project by Winter van den Bulck &amp; Matthias Van Duysen · "
        "Analysis in line with the legal structure of Belgian annual accounts.",
    ),

    # ============================ Homepage ============================
    "NBB-jaarrekeningen, meteen leesbaar": ("Comptes annuels BNB, immédiatement lisibles", "NBB annual accounts, instantly readable"),
    "@hero_h1": (
        "Décryptez chaque <span class=\"grad\">compte annuel belge</span> en quelques secondes.",
        "Understand every <span class=\"grad\">Belgian annual account</span> in seconds.",
    ),
    "@hero_lead": (
        "Importez un CSV, un JSON ou un PDF — ou saisissez simplement un numéro BCE. Vous obtenez le bilan et "
        "le compte de résultats selon la structure légale, des ratios avec comparaison sectorielle, "
        "un baromètre de santé, les administrateurs et des comparaisons dans le temps.",
        "Upload a CSV, JSON or PDF — or just enter a CBE number. You get the balance sheet and "
        "income statement in the legal structure, ratios with sector comparison, "
        "a health barometer, directors and multi-year comparisons.",
    ),
    "@pill_balans": ("Bilan &amp; compte de résultats", "Balance sheet &amp; income statement"),
    "Ratio's + sector": ("Ratios + secteur", "Ratios + sector"),
    "Upload een jaarrekening": ("Importer un compte annuel", "Upload an annual account"),
    "Zoek op KBO-nummer": ("Rechercher par numéro BCE", "Search by CBE number"),
    "Vergelijk bedrijven": ("Comparer des entreprises", "Compare companies"),
    "CSV, JSON (jsonxbrl) of PDF van de NBB.": ("CSV, JSON (jsonxbrl) ou PDF de la BNB.", "CSV, JSON (jsonxbrl) or PDF from the NBB."),
    "Sleep hierheen of klik om te kiezen": ("Glissez ici ou cliquez pour choisir", "Drag here or click to choose"),
    "@upload_small": (".csv · .json · .pdf — max. 5&nbsp;Mo", ".csv · .json · .pdf — max. 5&nbsp;MB"),
    "Analyseer": ("Analyser", "Analyse"),
    "Of via KBO-/BTW-nummer": ("Ou via un numéro BCE/TVA", "Or via CBE/VAT number"),
    "Recentste neerlegging rechtstreeks van de NBB Balanscentrale.": (
        "Dépôt le plus récent directement de la Centrale des bilans de la BNB.",
        "Most recent filing directly from the NBB Central Balance Sheet Office.",
    ),
    "bv. 0403.101.811": ("p. ex. 0403.101.811", "e.g. 0403.101.811"),
    "Ophalen": ("Récupérer", "Fetch"),
    "@nbb_note": (
        "Service web gratuit de la BNB ; nécessite une clé unique (<code>NBB_CBSO_SUBSCRIPTION_KEY</code>).",
        "Free NBB web service; requires a one-time key (<code>NBB_CBSO_SUBSCRIPTION_KEY</code>).",
    ),
    "Alles-in-één": ("Tout-en-un", "All-in-one"),
    "Wat je met de tool kan doen": ("Ce que l'outil vous permet de faire", "What you can do with the tool"),
    "Van ruwe neerlegging tot een volledig financieel beeld — automatisch en volgens de wettelijke structuur.": (
        "Du dépôt brut à une image financière complète — automatiquement et selon la structure légale.",
        "From raw filing to a complete financial picture — automatically and in the legal structure.",
    ),
    "@feat_balans": ("Bilan &amp; compte de résultats", "Balance sheet &amp; income statement"),
    "Automatisch opgemaakt volgens de wettelijke NBB-structuur, met codes, toelichtingen en nette bedragen.": (
        "Établi automatiquement selon la structure légale de la BNB, avec codes, annexes et montants soignés.",
        "Automatically prepared in the legal NBB structure, with codes, notes and neatly formatted amounts.",
    ),
    "Conformiteitscontrole": ("Contrôle de conformité", "Compliance check"),
    "Controleert het balansevenwicht en de belangrijkste wettelijke optelsommen, en flagt afwijkingen.": (
        "Vérifie l'équilibre du bilan et les principaux totaux légaux, et signale les écarts.",
        "Checks the balance-sheet equilibrium and the main statutory subtotals, and flags discrepancies.",
    ),
    "@feat_ratios": ("Ratios &amp; comparaison sectorielle", "Ratios &amp; sector comparison"),
    "Toegevoegde waarde, rendabiliteit, solvabiliteit en liquiditeit, afgezet tegen NBB-sectorkwartielen.": (
        "Valeur ajoutée, rentabilité, solvabilité et liquidité, comparées aux quartiles sectoriels de la BNB.",
        "Value added, profitability, solvency and liquidity, benchmarked against NBB sector quartiles.",
    ),
    "Gezondheidsbarometer": ("Baromètre de santé", "Health barometer"),
    "Score /100, Altman Z''-score en gezondheidskwadrant, met signalen en een indicatieve kredietrichtlijn.": (
        "Score /100, score Altman Z'' et quadrant de santé, avec signaux et une ligne de crédit indicative.",
        "Score /100, Altman Z'' score and health quadrant, with signals and an indicative credit guideline.",
    ),
    "Bestuurders": ("Administrateurs", "Directors"),
    "Namen, functies, adres en mandaat — mét landvlag en inactieve mandaten duidelijk gemarkeerd.": (
        "Noms, fonctions, adresse et mandat — avec drapeau du pays et mandats inactifs clairement signalés.",
        "Names, functions, address and mandate — with country flag and inactive mandates clearly marked.",
    ),
    "@feat_vergelijk": ("Comparaison &amp; tendances", "Comparison &amp; trends"),
    "Meerdere boekjaren of ondernemingen naast elkaar, met grafieken en een gunstig/ongunstig-oordeel.": (
        "Plusieurs exercices ou entreprises côte à côte, avec graphiques et un verdict favorable/défavorable.",
        "Multiple financial years or companies side by side, with charts and a favourable/unfavourable verdict.",
    ),
    "Meerdere bronnen": ("Sources multiples", "Multiple sources"),
    "@feat_bronnen": (
        "CSV, JSON (jsonxbrl) et PDF (NL &amp; FR), ou récupération automatique via le numéro BCE/TVA.",
        "CSV, JSON (jsonxbrl) and PDF (NL &amp; FR), or automatic retrieval via the CBE/VAT number.",
    ),
    "@feat_identificatie": ("Identification &amp; chiffres clés", "Identification &amp; key figures"),
    "Bedrijfsfiche met KBO-nummer, rechtsvorm, boekjaar en personeel, plus de kerncijfers in één oogopslag.": (
        "Fiche d'entreprise avec numéro BCE, forme juridique, exercice et personnel, plus les chiffres clés en un coup d'œil.",
        "Company profile with CBE number, legal form, financial year and staff, plus key figures at a glance.",
    ),
    "Signalen": ("Signaux", "Signals"),
    "Duidelijke waarschuwingen zoals verlies, negatief eigen vermogen of zwakke liquiditeit.": (
        "Avertissements clairs comme une perte, des capitaux propres négatifs ou une liquidité faible.",
        "Clear warnings such as loss, negative equity or weak liquidity.",
    ),
    "Zo werkt het": ("Comment ça marche", "How it works"),
    "In drie stappen naar inzicht": ("En trois étapes vers l'analyse", "Three steps to insight"),
    "Kies je bron": ("Choisissez votre source", "Choose your source"),
    "Upload een CSV/JSON/PDF of vul een KBO-nummer in.": (
        "Importez un CSV/JSON/PDF ou saisissez un numéro BCE.",
        "Upload a CSV/JSON/PDF or enter a CBE number.",
    ),
    "FAO analyseert": ("FAO analyse", "FAO analyses"),
    "De jaarrekening wordt opgemaakt, gecontroleerd en doorgerekend.": (
        "Le compte annuel est établi, contrôlé et calculé.",
        "The annual account is prepared, checked and computed.",
    ),
    "Bekijk het inzicht": ("Consultez l'analyse", "View the insights"),
    "Balans, ratio's, risico, bestuurders en vergelijkingen — meteen.": (
        "Bilan, ratios, risque, administrateurs et comparaisons — immédiatement.",
        "Balance sheet, ratios, risk, directors and comparisons — instantly.",
    ),
    "NBB-export": ("Export BNB", "NBB export"),
    "automatisch ophalen": ("récupération automatique", "automatic retrieval"),
    "Klaar om een jaarrekening te doorgronden?": ("Prêt à décrypter un compte annuel ?", "Ready to dive into an annual account?"),
    "Sleep je bestand hierboven, of vergelijk meteen meerdere boekjaren en bedrijven.": (
        "Glissez votre fichier ci-dessus, ou comparez directement plusieurs exercices et entreprises.",
        "Drop your file above, or compare several financial years and companies right away.",
    ),
    "Start een analyse": ("Démarrer une analyse", "Start an analysis"),
    "Naar vergelijken": ("Vers la comparaison", "Go to compare"),
    "Gekozen": ("Choisi", "Selected"),

    # ============================ Resultaat: tabs & kop ============================
    "Overzicht": ("Aperçu", "Overview"),
    "Balans": ("Bilan", "Balance sheet"),
    "Resultatenrekening": ("Compte de résultats", "Income statement"),
    "Kasstromen": ("Flux de trésorerie", "Cash flows"),
    "Ratio's": ("Ratios", "Ratios"),
    "Risico": ("Risque", "Risk"),
    "Betrouwbaarheid": ("Fiabilité", "Reliability"),
    "Controle": ("Contrôle", "Checks"),
    "Boekjaar": ("Exercice", "Financial year"),
    "munt": ("devise", "currency"),
    "@codes_herkend": ("{h} sur {tot} codes reconnus", "{h} of {tot} codes recognised"),
    "Conform de wettelijke structuur": ("Conforme à la structure légale", "Compliant with the legal structure"),
    "Aandachtspunten gevonden": ("Points d'attention détectés", "Issues found"),
    "Nieuwe analyse": ("Nouvelle analyse", "New analysis"),

    # ============================ Resultaat: overzicht ============================
    "De balans is in evenwicht": ("Le bilan est équilibré", "The balance sheet is balanced"),
    "De balans is niet in evenwicht": ("Le bilan n'est pas équilibré", "The balance sheet is not balanced"),
    "Totaal activa": ("Total de l'actif", "Total assets"),
    "Totaal passiva": ("Total du passif", "Total liabilities"),
    "verschil": ("écart", "difference"),
    "Bedrijfsfiche": ("Fiche d'entreprise", "Company profile"),
    "Onderneming": ("Entreprise", "Company"),
    "KBO-nummer": ("Numéro BCE", "CBE number"),
    "Rechtsvorm": ("Forme juridique", "Legal form"),
    "Adres": ("Adresse", "Address"),
    "Personeel (VTE)": ("Personnel (ETP)", "Staff (FTE)"),
    "Munt": ("Devise", "Currency"),
    "Indicatieve kredietrichtlijn": ("Ligne de crédit indicative", "Indicative credit guideline"),
    "Ruwe indicatie op basis van eigen vermogen en score — geen advies.": (
        "Estimation approximative basée sur les capitaux propres et le score — sans conseil.",
        "Rough indication based on equity and score — not advice.",
    ),
    "Onvoldoende gegevens voor een gezondheidsscore.": (
        "Données insuffisantes pour un score de santé.",
        "Insufficient data for a health score.",
    ),
    "Kerncijfers": ("Chiffres clés", "Key figures"),
    "Identificatiegegevens": ("Données d'identification", "Identification details"),
    "Conformiteit": ("Conformité", "Compliance"),
    "@conformiteit_count": ("— {ok} contrôles ok, {fout} avec écart", "— {ok} checks ok, {fout} with difference"),
    "@conformiteit_uitleg": (
        "FAO contrôle automatiquement les principaux totaux légaux du bilan et du compte de résultats. "
        "Consultez l'onglet <strong>Contrôle</strong> pour tous les détails.",
        "FAO automatically checks the main statutory subtotals of the balance sheet and income statement. "
        "See the <strong>Checks</strong> tab for all details.",
    ),
    "Alle controleerbare optelsommen kloppen": ("Tous les totaux vérifiables sont corrects", "All verifiable subtotals are correct"),
    "@optelsom_fout": ("{fout} total(aux) incorrect(s)", "{fout} subtotal(s) incorrect"),

    # ============================ Resultaat: balans / RR ============================
    "Balans na winstverdeling": ("Bilan après répartition", "Balance sheet after appropriation"),
    "Alles inklappen": ("Tout réduire", "Collapse all"),
    "Alles uitklappen": ("Tout développer", "Expand all"),
    "Verberg lege rubrieken": ("Masquer les rubriques vides", "Hide empty items"),

    # ============================ Resultaat: kasstromen ============================
    "Kasstromenoverzicht": ("Tableau des flux de trésorerie", "Cash flow statement"),
    "@kasstroom_uitleg": (
        "Tableau des flux de trésorerie retraité simplifié, dérivé de l'exercice courant et précédent. "
        "<strong>Approximation</strong> : les charges non décaissées exactes et certaines lignes de financement "
        "requièrent des données de l'annexe pas toujours disponibles.",
        "Simplified reworked cash flow statement, derived from the current and previous financial year. "
        "<strong>Approximation</strong>: the exact non-cash costs and some financing lines require "
        "disclosure data that is not always available.",
    ),
    "Sluit aan op de werkelijke kasmutatie": ("Concorde avec la variation réelle de trésorerie", "Reconciles with the actual cash movement"),
    "Benadering — sluit niet exact aan": ("Approximation — ne concorde pas exactement", "Approximation — does not reconcile exactly"),
    "Werkelijke mutatie liquide middelen + geldbeleggingen:": (
        "Variation réelle des valeurs disponibles + placements de trésorerie :",
        "Actual change in cash + short-term investments:",
    ),
    "verschil met berekening:": ("écart avec le calcul :", "difference vs calculation:"),

    # ============================ Resultaat: ratio's ============================
    "@evolutie_titel": ("Évolution par rapport à l'exercice précédent", "Trend versus previous financial year"),
    "@evolutie_count": ("— {g} favorable(s) · {o} défavorable(s)", "— {g} favourable · {o} unfavourable"),
    "Ratio": ("Ratio", "Ratio"),
    "Huidig": ("Actuel", "Current"),
    "Vorig": ("Précédent", "Previous"),
    "Evolutie": ("Évolution", "Trend"),
    "@ratio_titel": ("Analyse des ratios &amp; comparaison sectorielle", "Ratio analysis &amp; sector comparison"),
    "@ratio_intro": (
        "Les ratios du cours (valeur ajoutée, rentabilité, solvabilité, liquidité), calculés à partir du bilan "
        "et du compte de résultats. Les valeurs portant le label <span class=\"tag benadering\">approximation</span> "
        "utilisent une estimation des charges non décaissées ou des charges financières à partir des rubriques disponibles.",
        "The ratios from the course (value added, profitability, solvency, liquidity), computed from the balance "
        "sheet and income statement. Values with the <span class=\"tag benadering\">approximation</span> label "
        "use an estimate of non-cash costs or financial charges from the available items.",
    ),
    "@sector_summary": (
        "<strong>À propos de la comparaison sectorielle</strong> — est-ce possible ?",
        "<strong>About the sector comparison</strong> — is this possible?",
    ),
    "@sector_p1": (
        "Oui — la <strong>Centrale des bilans de la BNB</strong> publie via NBB.Stat, par "
        "<strong>secteur NACE-BEL</strong>, la répartition de ces ratios en quartiles (Q1/Q2/Q3). "
        "Comparer une entreprise à son secteur revient à voir où se situe son ratio par rapport à ces quartiles.",
        "Yes — the <strong>NBB Central Balance Sheet Office</strong> publishes via NBB.Stat, per "
        "<strong>NACE-BEL sector</strong>, the distribution of these ratios in quartiles (Q1/Q2/Q3). "
        "Comparing a company with its sector means seeing where its ratio falls relative to those quartiles.",
    ),
    "@sector_p2": (
        "<strong>Limite :</strong> le CSV déposé des comptes annuels ne contient pas de code NACE, de sorte que "
        "le secteur ne peut pas être déduit automatiquement. Un profil de référence fixe est donc utilisé ci-dessous :",
        "<strong>Limitation:</strong> the filed annual-account CSV contains no NACE code, so the sector cannot be "
        "derived automatically. A fixed reference profile is therefore used below:",
    ),
    "Profiel:": ("Profil :", "Profile:"),
    "Bron:": ("Source :", "Source:"),
    "sterk": ("fort", "strong"),
    "rond mediaan": ("autour de la médiane", "around median"),
    "zwak": ("faible", "weak"),
    "neutraal / geen benchmark": ("neutre / pas de référence", "neutral / no benchmark"),
    "Waarde": ("Valeur", "Value"),
    "Sector Q1 · Q2 · Q3": ("Secteur Q1 · Q2 · Q3", "Sector Q1 · Q2 · Q3"),
    "Positie": ("Position", "Position"),
    "benadering": ("approximation", "approximation"),
    "geen benchmark": ("pas de référence", "no benchmark"),

    # ============================ Resultaat: risico ============================
    "@baro_krediet_titel": ("Baromètre de santé &amp; ligne de crédit", "Health barometer &amp; credit guideline"),
    "Ruwe indicatie op basis van eigen vermogen en gezondheidsscore — geen kredietadvies.": (
        "Estimation approximative basée sur les capitaux propres et le score de santé — pas un conseil en crédit.",
        "Rough indication based on equity and health score — not credit advice.",
    ),
    "Globaal beeld: eerder gunstig": ("Image globale : plutôt favorable", "Overall picture: rather favourable"),
    "Globaal beeld: aandachtspunten qua financieel risico": (
        "Image globale : points d'attention quant au risque financier",
        "Overall picture: financial-risk concerns",
    ),
    "Indicatieve inschatting op basis van balans en resultatenrekening — geen volwaardige kredietbeoordeling.": (
        "Estimation indicative basée sur le bilan et le compte de résultats — pas une évaluation de crédit complète.",
        "Indicative estimate based on balance sheet and income statement — not a full credit assessment.",
    ),
    "@altman_uitleg": (
        "Z'' = 3,25 + 6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4 — variante pour les entreprises non cotées. "
        "Zones : &gt; 2,6 sûr · 1,1–2,6 gris · &lt; 1,1 détresse.",
        "Z'' = 3.25 + 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4 — variant for non-listed companies. "
        "Zones: &gt; 2.6 safe · 1.1–2.6 grey · &lt; 1.1 distress.",
    ),
    "Onvoldoende gegevens om de Altman Z''-score te berekenen.": (
        "Données insuffisantes pour calculer le score Altman Z''.",
        "Insufficient data to compute the Altman Z'' score.",
    ),
    "Gezondheidskwadrant": ("Quadrant de santé", "Health quadrant"),
    "@kwadrant_uitleg": (
        "Croisement rentabilité × liquidité (cours FAO, Tableau 16.1) : sain · temporairement malade · "
        "chroniquement malade · mourant.",
        "Profitability × liquidity crossing (FAO course, Table 16.1): healthy · temporarily ill · "
        "chronically ill · dying.",
    ),
    "Onvoldoende gegevens voor het gezondheidskwadrant.": (
        "Données insuffisantes pour le quadrant de santé.",
        "Insufficient data for the health quadrant.",
    ),
    "Onvoldoende gegevens om het financieel risico in te schatten.": (
        "Données insuffisantes pour estimer le risque financier.",
        "Insufficient data to assess financial risk.",
    ),
    "Faalvoorspellingsmodellen": ("Modèles de prédiction de défaillance", "Failure prediction models"),
    "Academische modellen uit de cursus. Indicatief — geen kredietbeoordeling.": (
        "Modèles académiques du cours. Indicatif — pas une évaluation de crédit.",
        "Academic models from the course. Indicative — not a credit assessment.",
    ),
    "@ov82_hint": (
        "Score discriminant linéaire · seuil ≈ {a} (plus élevé = plus sain)",
        "Linear discriminant score · cut-off ≈ {a} (higher = healthier)",
    ),
    "@fito_titel": ("SIM05 — score FiTo (simple-intuitif)", "SIM05 — FiTo score (simple-intuitive)"),
    "Gemiddelde van 5 logit-herschaalde ratio's (0–1, hoger = gezonder)": (
        "Moyenne de 5 ratios rééchelonnés par logit (0–1, plus élevé = plus sain)",
        "Average of 5 logit-rescaled ratios (0–1, higher = healthier)",
    ),
    "Onvoldoende gegevens.": ("Données insuffisantes.", "Insufficient data."),

    # ============================ Resultaat: betrouwbaarheid ============================
    "Indicatieve beoordeling — geen audit of forensisch onderzoek.": (
        "Évaluation indicative — pas un audit ni une enquête forensique.",
        "Indicative assessment — not an audit or forensic investigation.",
    ),
    "Commissaris / auditoroordeel": ("Commissaire / opinion d'audit", "Statutory auditor / audit opinion"),
    "Automatisch gelezen uit het commissarisverslag in de PDF.": (
        "Lu automatiquement dans le rapport du commissaire du PDF.",
        "Automatically read from the auditor's report in the PDF.",
    ),
    "Toelichtende paragraaf (aandacht gevestigd)": ("Paragraphe d'observation (attention attirée)", "Emphasis of matter paragraph"),
    "Onzekerheid over de continuïteit (going concern)": ("Incertitude sur la continuité (going concern)", "Going-concern uncertainty"),
    "Geen bijzondere paragrafen gedetecteerd": ("Aucun paragraphe particulier détecté", "No special paragraphs detected"),
    "Er is een commissaris, maar het verslag kon niet automatisch uit deze bron gelezen worden.": (
        "Un commissaire existe, mais le rapport n'a pas pu être lu automatiquement à partir de cette source.",
        "There is an auditor, but the report could not be read automatically from this source.",
    ),
    "Geen commissarisverslag gevonden. Dit is normaal voor kleine vennootschappen zonder wettelijke controleplicht, of wanneer de bron (CSV/JSON/XBRL) de tekst niet bevat.": (
        "Aucun rapport de commissaire trouvé. C'est normal pour les petites sociétés sans obligation légale de contrôle, "
        "ou lorsque la source (CSV/JSON/XBRL) ne contient pas le texte.",
        "No auditor's report found. This is normal for small companies without a statutory audit obligation, "
        "or when the source (CSV/JSON/XBRL) does not contain the text.",
    ),
    "— winstmanipulatie": ("— manipulation des résultats", "— earnings manipulation"),
    "@beneish_hint": (
        "Seuil : M &gt; −1,78 indique une probabilité accrue (approximation, 2 exercices).",
        "Threshold: M &gt; −1.78 indicates elevated likelihood (approximation, 2 financial years).",
    ),
    "Niet berekenbaar (vereist twee boekjaren en de omzet).": (
        "Non calculable (nécessite deux exercices et le chiffre d'affaires).",
        "Not computable (requires two financial years and turnover).",
    ),
    "Indicatoren voor resultaatsturing": ("Indicateurs de gestion du résultat", "Earnings-management indicators"),
    "aandacht": ("attention", "caution"),
    "let op": ("attention", "warning"),

    # ============================ Resultaat: bestuurders ============================
    "@bestuurders_titel": ("Administrateurs, gérants &amp; commissaires", "Directors, managers &amp; auditors"),
    "Naam": ("Nom", "Name"),
    "Functie": ("Fonction", "Function"),
    "Mandaat": ("Mandat", "Mandate"),
    "niet meer actief": ("plus actif", "no longer active"),
    "Geen bestuurdersgegevens beschikbaar voor deze bron. Bestuurders worden gehaald uit een PDF, JSON (jsonxbrl) of via het KBO-nummer; een CSV met enkel rubriekcodes bevat ze niet.": (
        "Aucune donnée d'administrateurs disponible pour cette source. Les administrateurs proviennent d'un PDF, "
        "d'un JSON (jsonxbrl) ou du numéro BCE ; un CSV avec seulement des codes de rubriques n'en contient pas.",
        "No director data available for this source. Directors are taken from a PDF, JSON (jsonxbrl) or via the "
        "CBE number; a CSV with only item codes does not contain them.",
    ),

    # ============================ Resultaat: controle ============================
    "Niet te controleren — niet alle rubrieken zijn aanwezig in de CSV.": (
        "Non vérifiable — toutes les rubriques ne sont pas présentes dans le CSV.",
        "Cannot be checked — not all items are present in the CSV.",
    ),
    "Aangegeven": ("Déclaré", "Reported"),
    "berekend": ("calculé", "computed"),
    "Klopt": ("Correct", "Correct"),
    "Overgeslagen": ("Ignoré", "Skipped"),

    # ============================ Vergelijken ============================
    "Jaarrekeningen vergelijken": ("Comparer des comptes annuels", "Compare annual accounts"),
    "@vgl_intro": (
        "Importez plusieurs comptes annuels (CSV, JSON ou PDF) — plusieurs exercices de la même entreprise pour "
        "l'évolution, ou différentes entreprises côte à côte. FAO aligne les chiffres clés et les ratios, montre "
        "l'évolution en graphiques et juge si elle est favorable ou défavorable.",
        "Upload several annual accounts (CSV, JSON or PDF) — several financial years of the same company for the "
        "trend, or different companies side by side. FAO lines up the key figures and ratios, shows the trend in "
        "charts and judges whether it is favourable or unfavourable.",
    ),
    "Kies minstens twee bestanden": ("Choisissez au moins deux fichiers", "Choose at least two files"),
    "Tip: selecteer in één keer meerdere bestanden (Ctrl/Cmd + klik). Types: .csv · .json · .pdf": (
        "Astuce : sélectionnez plusieurs fichiers à la fois (Ctrl/Cmd + clic). Types : .csv · .json · .pdf",
        "Tip: select several files at once (Ctrl/Cmd + click). Types: .csv · .json · .pdf",
    ),
    "Vergelijk": ("Comparer", "Compare"),
    "Enkele bestanden werden overgeslagen:": ("Certains fichiers ont été ignorés :", "Some files were skipped:"),
    "@aantal_jaarrekeningen": ("{n} comptes annuels", "{n} annual accounts"),
    "@aantal_gunstig": ("{n} évolutions favorables", "{n} favourable trends"),
    "@aantal_ongunstig": ("{n} évolutions défavorables", "{n} unfavourable trends"),
    "Meerdere ondernemingen": ("Plusieurs entreprises", "Multiple companies"),
    "Één onderneming over de tijd": ("Une entreprise dans le temps", "One company over time"),
    "@kerncijfers_eur": ("Chiffres clés (en {munt})", "Key figures (in {munt})"),
    "@detailvgl": ("Comparaison détaillée &amp; évolution", "Detailed comparison &amp; trend"),
    "Metriek": ("Métrique", "Metric"),
    "gunstig": ("favorable", "favourable"),
    "ongunstig": ("défavorable", "unfavourable"),

    # ============================ Foutpagina ============================
    "Er ging iets mis": ("Une erreur est survenue", "Something went wrong"),
    "De pagina die je zoekt bestaat niet.": ("La page que vous cherchez n'existe pas.", "The page you are looking for does not exist."),
    "Terug naar start": ("Retour à l'accueil", "Back to home"),

    # ============================ Flash / fouten (app + core) ============================
    "Deze pagina bestaat niet.": ("Cette page n'existe pas.", "This page does not exist."),
    "Het bestand is te groot (max. 5 MB).": ("Le fichier est trop volumineux (max. 5 Mo).", "The file is too large (max. 5 MB)."),
    "Kies eerst een bestand om te analyseren.": ("Choisissez d'abord un fichier à analyser.", "First choose a file to analyse."),
    "Ondersteunde bestandstypes: CSV, JSON (jsonxbrl) of PDF.": (
        "Types de fichiers pris en charge : CSV, JSON (jsonxbrl) ou PDF.",
        "Supported file types: CSV, JSON (jsonxbrl) or PDF.",
    ),
    "Het bestand kon niet gelezen worden. Controleer of het een geldige jaarrekening is.": (
        "Le fichier n'a pas pu être lu. Vérifiez qu'il s'agit d'un compte annuel valide.",
        "The file could not be read. Check that it is a valid annual account.",
    ),
    "Geef een KBO-/BTW-nummer in.": ("Saisissez un numéro BCE/TVA.", "Enter a CBE/VAT number."),
    "Er ging iets mis bij het automatisch ophalen van de jaarrekening.": (
        "Une erreur est survenue lors de la récupération automatique du compte annuel.",
        "Something went wrong while automatically retrieving the annual account.",
    ),
    "Kies minstens twee jaarrekeningen om te vergelijken.": (
        "Choisissez au moins deux comptes annuels à comparer.",
        "Choose at least two annual accounts to compare.",
    ),
    "Kon niet minstens twee geldige jaarrekeningen inlezen.": (
        "Impossible de lire au moins deux comptes annuels valides.",
        "Could not read at least two valid annual accounts.",
    ),
    "niet-ondersteund bestandstype": ("type de fichier non pris en charge", "unsupported file type"),
    "kon niet gelezen worden": ("n'a pas pu être lu", "could not be read"),
    # BronFout (bronnen.py / nbb_api.py)
    "Ongeldig JSON-bestand.": ("Fichier JSON invalide.", "Invalid JSON file."),
    "Onverwachte JSON-structuur voor jaarrekeningdata.": (
        "Structure JSON inattendue pour les données des comptes annuels.",
        "Unexpected JSON structure for annual-account data.",
    ),
    "Geen rubrieken (Rubrics) gevonden in het JSON-bestand.": (
        "Aucune rubrique (Rubrics) trouvée dans le fichier JSON.",
        "No rubrics found in the JSON file.",
    ),
    "PDF-ondersteuning vereist het pakket 'pypdf'.": (
        "Le support PDF nécessite le paquet « pypdf ».",
        "PDF support requires the 'pypdf' package.",
    ),
    "De PDF kon niet gelezen worden.": ("Le PDF n'a pas pu être lu.", "The PDF could not be read."),
    "Geen herkenbare balanscodes in de PDF gevonden. Gebruik bij voorkeur de JSON-export of het KBO-nummer; niet elke PDF-lay-out kan automatisch gelezen worden.": (
        "Aucun code de bilan reconnaissable trouvé dans le PDF. Utilisez de préférence l'export JSON ou le numéro BCE ; "
        "toutes les mises en page PDF ne peuvent pas être lues automatiquement.",
        "No recognisable balance-sheet codes found in the PDF. Prefer the JSON export or the CBE number; "
        "not every PDF layout can be read automatically.",
    ),
    "Niet-ondersteund bestandstype. Gebruik .csv, .json of .pdf.": (
        "Type de fichier non pris en charge. Utilisez .csv, .json ou .pdf.",
        "Unsupported file type. Use .csv, .json or .pdf.",
    ),
    "De NBB-abonnementssleutel ontbreekt of is ongeldig. Registreer gratis op developer.cbso.nbb.be en zet de sleutel als NBB_CBSO_SUBSCRIPTION_KEY.": (
        "La clé d'abonnement BNB est absente ou invalide. Inscrivez-vous gratuitement sur developer.cbso.nbb.be "
        "et définissez la clé comme NBB_CBSO_SUBSCRIPTION_KEY.",
        "The NBB subscription key is missing or invalid. Register for free at developer.cbso.nbb.be "
        "and set the key as NBB_CBSO_SUBSCRIPTION_KEY.",
    ),
    "Geen (publiceerbare) jaarrekening gevonden voor dit nummer.": (
        "Aucun compte annuel (publiable) trouvé pour ce numéro.",
        "No (publishable) annual accounts found for this number.",
    ),
    "Kon de NBB-webservice niet bereiken.": ("Impossible de joindre le service web de la BNB.", "Could not reach the NBB web service."),
    "Geen jaarrekeningen gevonden voor dit KBO-/BTW-nummer.": (
        "Aucun compte annuel trouvé pour ce numéro BCE/TVA.",
        "No annual accounts found for this CBE/VAT number.",
    ),
    "Geen bruikbare neerleggingsreferentie gevonden.": (
        "Aucune référence de dépôt utilisable trouvée.",
        "No usable filing reference found.",
    ),
    "Onverwacht antwoord van de NBB bij het opvragen van de referenties.": (
        "Réponse inattendue de la BNB lors de la demande des références.",
        "Unexpected response from the NBB when requesting references.",
    ),
    "Automatisch ophalen is nog niet geconfigureerd: er is geen NBB-abonnementssleutel. Registreer gratis op developer.cbso.nbb.be en zet de sleutel als NBB_CBSO_SUBSCRIPTION_KEY.": (
        "La récupération automatique n'est pas encore configurée : aucune clé d'abonnement BNB. Inscrivez-vous "
        "gratuitement sur developer.cbso.nbb.be et définissez la clé comme NBB_CBSO_SUBSCRIPTION_KEY.",
        "Automatic retrieval is not yet configured: no NBB subscription key. Register for free at "
        "developer.cbso.nbb.be and set the key as NBB_CBSO_SUBSCRIPTION_KEY.",
    ),
    "Ongeldig KBO-/BTW-nummer. Geef 10 cijfers in (bv. 0403.101.811).": (
        "Numéro BCE/TVA invalide. Saisissez 10 chiffres (p. ex. 0403.101.811).",
        "Invalid CBE/VAT number. Enter 10 digits (e.g. 0403.101.811).",
    ),

    # ============================ Waarden / rollen ============================
    "Ja": ("Oui", "Yes"),
    "Nee": ("Non", "No"),
    "Onbekende vennootschap": ("Société inconnue", "Unknown company"),
    "Bestuurder": ("Administrateur", "Director"),
    "Bestuurder (rechtspersoon)": ("Administrateur (personne morale)", "Director (legal entity)"),

    # ============================ Metadata-labels ============================
    "IDENTIFICATIEGEGEVENS": ("DONNÉES D'IDENTIFICATION", "IDENTIFICATION DETAILS"),
    "Referentienummer": ("Numéro de référence", "Reference number"),
    "KBO-/BTW-nummer": ("Numéro BCE/TVA", "CBE/VAT number"),
    "BOEKJAAR": ("EXERCICE", "FINANCIAL YEAR"),
    "Boekjaar - Begin": ("Exercice - Début", "Financial year - Start"),
    "Boekjaar - Einde": ("Exercice - Fin", "Financial year - End"),
    "Vennootschapsnaam": ("Dénomination de la société", "Company name"),
    "Straatnaam": ("Rue", "Street"),
    "Huisnummer": ("Numéro", "Number"),
    "Postcode": ("Code postal", "Postal code"),
    "Stad": ("Ville", "City"),
    "Land": ("Pays", "Country"),
    "Datum Algemene Vergadering": ("Date de l'assemblée générale", "General meeting date"),
    "Liquidatie?": ("Liquidation ?", "Liquidation?"),
    "Correctie?": ("Correction ?", "Correction?"),
    "Vennootschapsvorm": ("Forme juridique", "Legal form"),

    # ============================ Kerncijfers (analyse.py) ============================
    "Liquiditeit in ruime zin": ("Liquidité au sens large", "Liquidity in the broad sense"),
    "Solvabiliteit (eigen vermogen)": ("Solvabilité (capitaux propres)", "Solvency (equity)"),
    "Nettobedrijfskapitaal": ("Fonds de roulement net", "Net working capital"),
    "Vlottende activa (29/58) / schulden \u22641 jaar (42/48)": (
        "Actifs circulants (29/58) / dettes \u22641 an (42/48)",
        "Current assets (29/58) / debt \u22641 year (42/48)",
    ),
    "Eigen vermogen (10/15) / totaal vermogen (10/49)": (
        "Capitaux propres (10/15) / total du passif (10/49)",
        "Equity (10/15) / total capital (10/49)",
    ),
    "Vlottende activa (29/58) \u2212 schulden \u22641 jaar (42/48)": (
        "Actifs circulants (29/58) \u2212 dettes \u22641 an (42/48)",
        "Current assets (29/58) \u2212 debt \u22641 year (42/48)",
    ),

    # ============================ Conformiteitscontroles (analyse.py) ============================
    "Totaal activa = oprichtingskosten + vaste activa + vlottende activa": (
        "Total de l'actif = frais d'établissement + actifs immobilisés + actifs circulants",
        "Total assets = formation expenses + fixed assets + current assets",
    ),
    "Vaste activa = IVA + MVA + FVA": (
        "Actifs immobilisés = immob. incorporelles + corporelles + financières",
        "Fixed assets = intangible + tangible + financial fixed assets",
    ),
    "Vlottende activa = vord. >1j + voorraden + vord. \u22641j + geldbeleggingen + liquide middelen + overlopende rek.": (
        "Actifs circulants = créances >1 an + stocks + créances \u22641 an + placements de trésorerie + valeurs disponibles + comptes de régularisation",
        "Current assets = receivables >1yr + inventories + receivables \u22641yr + short-term investments + cash + accruals",
    ),
    "Totaal passiva = eigen vermogen + voorzieningen + schulden": (
        "Total du passif = capitaux propres + provisions + dettes",
        "Total liabilities = equity + provisions + debt",
    ),
    "Eigen vermogen = inbreng + herwaarderingsmw + reserves + overgedragen res. + kapitaalsubsidies + voorschot": (
        "Capitaux propres = apport + plus-values de réévaluation + réserves + résultat reporté + subsides en capital + avance",
        "Equity = contribution + revaluation surpluses + reserves + retained result + capital subsidies + advance",
    ),
    "Schulden = schulden >1j + schulden \u22641j + overlopende rekeningen": (
        "Dettes = dettes >1 an + dettes \u22641 an + comptes de régularisation",
        "Debt = debt >1yr + debt \u22641yr + accruals",
    ),
    "Bedrijfswinst (verlies) = bedrijfsopbrengsten \u2212 bedrijfskosten": (
        "Bénéfice (perte) d'exploitation = produits d'exploitation \u2212 charges d'exploitation",
        "Operating profit (loss) = operating income \u2212 operating charges",
    ),
    "Winst (verlies) vóór belasting = bedrijfsresultaat + financiële opbrengsten \u2212 financiële kosten": (
        "Bénéfice (perte) avant impôts = résultat d'exploitation + produits financiers \u2212 charges financières",
        "Profit (loss) before tax = operating result + financial income \u2212 financial charges",
    ),
    "Winst (verlies) van het boekjaar = resultaat vóór belasting \u2212 belastingen": (
        "Bénéfice (perte) de l'exercice = résultat avant impôts \u2212 impôts",
        "Profit (loss) for the year = result before tax \u2212 taxes",
    ),
    "Te bestemmen resultaat = resultaat boekjaar +/\u2212 belastingvrije reserves": (
        "Résultat à affecter = résultat de l'exercice +/\u2212 réserves immunisées",
        "Result to be appropriated = result for the year +/\u2212 tax-free reserves",
    ),

    # ============================ Sector (sectordata.py) ============================
    "Algemeen referentieprofiel (illustratief)": (
        "Profil de référence général (illustratif)",
        "General reference profile (illustrative)",
    ),
    "Illustratieve NBB-kwartielen (cursus FAO, sectorkwartielen 20X3). Actuele sectorcijfers: NBB Balanscentrale via NBB.Stat, per NACE-BEL-code.": (
        "Quartiles BNB illustratifs (cours FAO, quartiles sectoriels 20X3). Chiffres sectoriels actuels : "
        "Centrale des bilans BNB via NBB.Stat, par code NACE-BEL.",
        "Illustrative NBB quartiles (FAO course, sector quartiles 20X3). Current sector figures: "
        "NBB Central Balance Sheet Office via NBB.Stat, per NACE-BEL code.",
    ),
    "onder mediaan": ("sous la médiane", "below median"),
    "boven mediaan": ("au-dessus de la médiane", "above median"),
    "laag": ("bas", "low"),
    "eerder laag": ("plutôt bas", "rather low"),
    "eerder hoog": ("plutôt élevé", "rather high"),
    "hoog": ("élevé", "high"),

    # ============================ Ratiogroepen & -namen (ratios.py) ============================
    "Toegevoegde waarde": ("Valeur ajoutée", "Value added"),
    "Rendabiliteit": ("Rentabilité", "Profitability"),
    "Solvabiliteit": ("Solvabilité", "Solvency"),
    "Liquiditeit": ("Liquidité", "Liquidity"),
    "Bruto toegevoegde waardemarge": ("Marge brute sur valeur ajoutée", "Gross value-added margin"),
    "Bruto toegevoegde waarde per werknemer": ("Valeur ajoutée brute par travailleur", "Gross value added per employee"),
    "Aandeel van het personeel in de BTW": ("Part du personnel dans la VAB", "Share of personnel in gross value added"),
    "Aandeel recurrente niet-kaskosten in de TW": ("Part des charges récurrentes non décaissées dans la VA", "Share of recurring non-cash costs in value added"),
    "Aandeel van de FKVV in de BTW": ("Part des charges financières des dettes dans la VAB", "Share of financial debt costs in gross value added"),
    "Aandeel van de belastingen in de BTW": ("Part des impôts dans la VAB", "Share of taxes in gross value added"),
    "Aandeel van de toegevoegde winst/verlies in de BTW": ("Part du bénéfice/perte ajouté(e) dans la VAB", "Share of added profit/loss in gross value added"),
    "Brutoverkoopmarge vóór belastingen": ("Marge brute sur ventes avant impôts", "Gross sales margin before taxes"),
    "Nettoverkoopmarge vóór belastingen": ("Marge nette sur ventes avant impôts", "Net sales margin before taxes"),
    "Brutorendabiliteit van het totaal van de activa": ("Rentabilité brute de l'actif total", "Gross return on total assets"),
    "Nettorendabiliteit van het totaal van de activa": ("Rentabilité nette de l'actif total", "Net return on total assets"),
    "Nettorendabiliteit van het EV vóór belastingen": ("Rentabilité nette des capitaux propres avant impôts", "Net return on equity before taxes"),
    "Nettorendabiliteit van het EV na belastingen": ("Rentabilité nette des capitaux propres après impôts", "Net return on equity after taxes"),
    "Brutorendabiliteit van het EV na belastingen": ("Rentabilité brute des capitaux propres après impôts", "Gross return on equity after taxes"),
    "Algemene schuldgraad": ("Taux d'endettement général", "General debt ratio"),
    "Algemene graad van financiële onafhankelijkheid": ("Degré général d'indépendance financière", "General degree of financial independence"),
    "Zelffinancieringsgraad": ("Taux d'autofinancement", "Self-financing ratio"),
    "Langetermijnschuldgraad": ("Taux d'endettement à long terme", "Long-term debt ratio"),
    "Langetermijngraad van financiële onafhankelijkheid": ("Degré d'indépendance financière à long terme", "Long-term degree of financial independence"),
    "Netto financiële schuldgraad": ("Taux d'endettement financier net", "Net financial debt ratio"),
    "Dekking van de FKVV door het nettoresultaat": ("Couverture des charges financières des dettes par le résultat net", "Coverage of financial debt costs by net result"),
    "Dekking van het totaal VV door de cashflow": ("Couverture du total des dettes par le cash-flow", "Coverage of total debt by cash flow"),
    "Dekking van het VVLT door de cashflow": ("Couverture des dettes à long terme par le cash-flow", "Coverage of long-term debt by cash flow"),
    "Liquiditeitsratio in ruime zin (current ratio)": ("Ratio de liquidité au sens large (current ratio)", "Liquidity ratio in the broad sense (current ratio)"),
    "Liquiditeitsratio in enge zin (acid test)": ("Ratio de liquidité au sens strict (acid test)", "Liquidity ratio in the narrow sense (acid test)"),
    "Nettobedrijfskapitaalbehoefte": ("Besoin en fonds de roulement net", "Net working capital requirement"),
    "Nettokas": ("Trésorerie nette", "Net cash"),
    "Nettokasratio": ("Ratio de trésorerie nette", "Net cash ratio"),
    "Rotatie van de voorraden en BIU": ("Rotation des stocks et commandes en cours", "Inventory and WIP turnover"),
    "Rotatie van de handelsvorderingen": ("Rotation des créances commerciales", "Trade receivables turnover"),
    "Rotatie van de handelsschulden": ("Rotation des dettes commerciales", "Trade payables turnover"),
    "Dagen klantenkrediet": ("Jours de crédit clients", "Days of customer credit"),
    "Dagen leverancierskrediet": ("Jours de crédit fournisseurs", "Days of supplier credit"),

    # Ratio-formules
    "bruto TW / bedrijfsopbrengsten": ("VAB / produits d'exploitation", "gross VA / operating income"),
    "bruto TW / gemiddeld personeelsbestand (9087)": ("VAB / effectif moyen du personnel (9087)", "gross VA / average workforce (9087)"),
    "bezoldigingen (62) / bruto TW": ("rémunérations (62) / VAB", "remuneration (62) / gross VA"),
    "afschrijvingen + waardeverm. + voorz. (630+631/4+635/8) / bruto TW": (
        "amortissements + réductions de valeur + provisions (630+631/4+635/8) / VAB",
        "depreciation + write-downs + provisions (630+631/4+635/8) / gross VA",
    ),
    "financiële kosten VV / bruto TW": ("charges financières des dettes / VAB", "financial debt costs / gross VA"),
    "belastingen (67/77) / bruto TW": ("impôts (67/77) / VAB", "taxes (67/77) / gross VA"),
    "(bruto TW \u2212 personeel \u2212 niet-kaskosten \u2212 FKVV \u2212 belastingen) / bruto TW": (
        "(VAB \u2212 personnel \u2212 charges non décaissées \u2212 charges fin. dettes \u2212 impôts) / VAB",
        "(gross VA \u2212 personnel \u2212 non-cash costs \u2212 financial debt costs \u2212 taxes) / gross VA",
    ),
    "aandeel in bruto TW": ("part dans la VAB", "share of gross VA"),
    "(resultaat vóór bel. + FKVV + niet-kaskosten) / omzet": (
        "(résultat avant impôts + charges fin. dettes + charges non décaissées) / chiffre d'affaires",
        "(result before tax + financial debt costs + non-cash costs) / turnover",
    ),
    "(resultaat vóór bel. + FKVV) / omzet": (
        "(résultat avant impôts + charges fin. dettes) / chiffre d'affaires",
        "(result before tax + financial debt costs) / turnover",
    ),
    "(resultaat vóór bel. + FKVV + niet-kaskosten) / totaal activa": (
        "(résultat avant impôts + charges fin. dettes + charges non décaissées) / total de l'actif",
        "(result before tax + financial debt costs + non-cash costs) / total assets",
    ),
    "(resultaat vóór bel. + FKVV) / totaal activa": (
        "(résultat avant impôts + charges fin. dettes) / total de l'actif",
        "(result before tax + financial debt costs) / total assets",
    ),
    "resultaat vóór bel. (9903) / eigen vermogen": (
        "résultat avant impôts (9903) / capitaux propres",
        "result before tax (9903) / equity",
    ),
    "resultaat na bel. (9904) / eigen vermogen": (
        "résultat après impôts (9904) / capitaux propres",
        "result after tax (9904) / equity",
    ),
    "(resultaat na bel. + niet-kaskosten) / eigen vermogen": (
        "(résultat après impôts + charges non décaissées) / capitaux propres",
        "(result after tax + non-cash costs) / equity",
    ),
    "resultaat na bel. / eigen vermogen": (
        "résultat après impôts / capitaux propres",
        "result after tax / equity",
    ),
    "vreemd vermogen / totaal vermogen": ("capitaux de tiers / total du passif", "debt / total capital"),
    "eigen vermogen / totaal vermogen": ("capitaux propres / total du passif", "equity / total capital"),
    "(reserves + overgedragen resultaat) / totaal vermogen": (
        "(réserves + résultat reporté) / total du passif",
        "(reserves + retained result) / total capital",
    ),
    "VV op lange termijn / permanent vermogen": ("dettes à long terme / capitaux permanents", "long-term debt / permanent capital"),
    "eigen vermogen / permanent vermogen": ("capitaux propres / capitaux permanents", "equity / permanent capital"),
    "netto financieel VV / eigen vermogen": ("dettes financières nettes / capitaux propres", "net financial debt / equity"),
    "EBIT (resultaat vóór bel. + FKVV) / FKVV": (
        "EBIT (résultat avant impôts + charges fin. dettes) / charges fin. dettes",
        "EBIT (result before tax + financial debt costs) / financial debt costs",
    ),
    "cashflow van het EV na bel. / totaal VV": (
        "cash-flow des capitaux propres après impôts / total des dettes",
        "cash flow of equity after tax / total debt",
    ),
    "cashflow van het EV na bel. / VV op lange termijn": (
        "cash-flow des capitaux propres après impôts / dettes à long terme",
        "cash flow of equity after tax / long-term debt",
    ),
    "vlottende activa (29/58) / VV op korte termijn": (
        "actifs circulants (29/58) / dettes à court terme",
        "current assets (29/58) / short-term debt",
    ),
    "(vord. \u22641j + geldbeleggingen + liquide middelen) / VVKT": (
        "(créances \u22641 an + placements de trésorerie + valeurs disponibles) / dettes à court terme",
        "(receivables \u22641yr + short-term investments + cash) / short-term debt",
    ),
    "vlottende activa \u2212 VV op korte termijn": (
        "actifs circulants \u2212 dettes à court terme",
        "current assets \u2212 short-term debt",
    ),
    "vlottende bedrijfsactiva \u2212 operationeel VVKT": (
        "actifs circulants d'exploitation \u2212 dettes d'exploitation à court terme",
        "operating current assets \u2212 operating short-term debt",
    ),
    "(geldbeleggingen + liquide middelen) \u2212 financieel VVKT": (
        "(placements de trésorerie + valeurs disponibles) \u2212 dettes financières à court terme",
        "(short-term investments + cash) \u2212 short-term financial debt",
    ),
    "nettokas / (beperkte) vlottende activa": (
        "trésorerie nette / actifs circulants (restreints)",
        "net cash / (restricted) current assets",
    ),
    "kostprijs verkopen / gem. voorraad": ("coût des ventes / stock moyen", "cost of sales / average inventory"),
    "(verkopen + btw) / handelsvorderingen": ("(ventes + TVA) / créances commerciales", "(sales + VAT) / trade receivables"),
    "(inkopen + btw) / handelsschulden": ("(achats + TVA) / dettes commerciales", "(purchases + VAT) / trade payables"),
    "365 / rotatie handelsvorderingen": ("365 / rotation des créances commerciales", "365 / trade receivables turnover"),
    "365 / rotatie handelsschulden": ("365 / rotation des dettes commerciales", "365 / trade payables turnover"),

    # Ratio-redenen
    "Bedrijfsopbrengsten (70/76A) niet aanwezig in de CSV.": (
        "Produits d'exploitation (70/76A) absents du CSV.",
        "Operating income (70/76A) not present in the CSV.",
    ),
    "Bruto TW of personeelsbestand (9087) niet beschikbaar.": (
        "VAB ou effectif du personnel (9087) non disponible.",
        "Gross VA or workforce (9087) not available.",
    ),
    "Bruto TW niet berekenbaar (bedrijfsopbrengsten/inkopen ontbreken).": (
        "VAB non calculable (produits d'exploitation/achats manquants).",
        "Gross VA not computable (operating income/purchases missing).",
    ),
    "Omzet (70) niet afzonderlijk gerapporteerd in de CSV.": (
        "Chiffre d'affaires (70) non rapporté séparément dans le CSV.",
        "Turnover (70) not reported separately in the CSV.",
    ),
    "Eigen vermogen (10/15) ontbreekt of is nul.": (
        "Capitaux propres (10/15) manquants ou nuls.",
        "Equity (10/15) missing or zero.",
    ),
    "Vereist toelichtingsdata (BTW, aankopen, begin-/eindwaarden) en/of twee boekjaren.": (
        "Nécessite des données de l'annexe (TVA, achats, valeurs de début/fin) et/ou deux exercices.",
        "Requires disclosure data (VAT, purchases, opening/closing values) and/or two financial years.",
    ),

    # ============================ Risico (risico.py) ============================
    "Veilige zone": ("Zone de sécurité", "Safe zone"),
    "Grijze zone": ("Zone grise", "Grey zone"),
    "Noodzone": ("Zone de détresse", "Distress zone"),
    "Lage kans op financiële moeilijkheden.": ("Faible probabilité de difficultés financières.", "Low probability of financial difficulties."),
    "Verhoogde waakzaamheid aangewezen.": ("Vigilance accrue recommandée.", "Increased vigilance advised."),
    "Verhoogd risico op financiële moeilijkheden.": ("Risque accru de difficultés financières.", "Increased risk of financial difficulties."),
    "X1 · werkkapitaal / activa": ("X1 · fonds de roulement / actif", "X1 · working capital / assets"),
    "X2 · reserves + overgedragen res. / activa": ("X2 · réserves + résultat reporté / actif", "X2 · reserves + retained result / assets"),
    "X3 · EBIT / activa": ("X3 · EBIT / actif", "X3 · EBIT / assets"),
    "X4 · eigen vermogen / vreemd vermogen": ("X4 · capitaux propres / dettes", "X4 · equity / debt"),
    "Gezond": ("Sain", "Healthy"),
    "Tijdelijk ziek": ("Temporairement malade", "Temporarily ill"),
    "Chronisch ziek": ("Chroniquement malade", "Chronically ill"),
    "Stervend": ("Mourant", "Dying"),
    "Zowel rendabel als liquide.": ("À la fois rentable et liquide.", "Both profitable and liquid."),
    "Rendabel maar krappe liquiditeit (bv. sterke groei/overinvestering).": (
        "Rentable mais liquidité tendue (p. ex. forte croissance/surinvestissement).",
        "Profitable but tight liquidity (e.g. strong growth/overinvestment).",
    ),
    "Liquide maar structureel rendabiliteitsprobleem.": (
        "Liquide mais problème structurel de rentabilité.",
        "Liquid but structural profitability problem.",
    ),
    "Zowel rendabiliteits- als liquiditeitsproblemen.": (
        "Problèmes de rentabilité et de liquidité.",
        "Both profitability and liquidity problems.",
    ),
    "positief": ("positif", "positive"),
    "negatief": ("négatif", "negative"),
    "voldoende": ("suffisante", "sufficient"),
    "krap": ("tendue", "tight"),
    "Financieel gezond (laag risico)": ("Financièrement sain (risque faible)", "Financially healthy (low risk)"),
    "Aandacht (matig risico)": ("Attention (risque modéré)", "Caution (moderate risk)"),
    "Verhoogd risico": ("Risque accru", "Elevated risk"),
    "Balans niet in evenwicht": ("Bilan non équilibré", "Balance sheet not balanced"),
    "Negatief eigen vermogen": ("Capitaux propres négatifs", "Negative equity"),
    "Verlies van het boekjaar": ("Perte de l'exercice", "Loss for the year"),
    "Overgedragen verlies": ("Perte reportée", "Loss carried forward"),
    "Zwakke liquiditeit (current ratio < 1)": ("Liquidité faible (current ratio < 1)", "Weak liquidity (current ratio < 1)"),
    "Lage solvabiliteit (eigen vermogen < 20%)": ("Solvabilité faible (capitaux propres < 20 %)", "Low solvency (equity < 20%)"),
    "Geen bijzondere signalen gedetecteerd": ("Aucun signal particulier détecté", "No particular signals detected"),

    # ============================ Falingsmodellen (falingsmodellen.py) ============================
    "Lopend profiel (lager risico)": ("Profil sain (risque plus faible)", "Going-concern profile (lower risk)"),
    "Falingsprofiel (verhoogd risico)": ("Profil de défaillance (risque accru)", "Failure profile (elevated risk)"),
    "X1 · ingehouden winst/reserves ÷ totaal passiva": ("X1 · bénéfices/réserves retenus ÷ total du passif", "X1 · retained earnings/reserves ÷ total liabilities"),
    "X2 · vervallen belastingen/RSZ ÷ schulden ≤1j": ("X2 · impôts/ONSS échus ÷ dettes ≤1 an", "X2 · overdue taxes/social security ÷ debt ≤1yr"),
    "X3 · liquide middelen ÷ beperkte vlottende activa": ("X3 · valeurs disponibles ÷ actifs circulants restreints", "X3 · cash ÷ restricted current assets"),
    "X4 · voorraden ÷ vlottende bedrijfsactiva": ("X4 · stocks ÷ actifs circulants d'exploitation", "X4 · inventories ÷ operating current assets"),
    "X5 · fin. schulden ≤1j (kredietinst.) ÷ schulden ≤1j": ("X5 · dettes fin. ≤1 an (étab. de crédit) ÷ dettes ≤1 an", "X5 · financial debt ≤1yr (credit inst.) ÷ debt ≤1yr"),
    "Gezond profiel": ("Profil sain", "Healthy profile"),
    "Aandacht": ("Attention", "Caution"),
    "Graad van zelffinanciering": ("Taux d'autofinancement", "Self-financing ratio"),
    "Graad van financiële onafhankelijkheid": ("Degré d'indépendance financière", "Degree of financial independence"),
    "KT financiële schuldgraad": ("Taux d'endettement financier à CT", "Short-term financial debt ratio"),
    "Dekking VV door de cashflow": ("Couverture des dettes par le cash-flow", "Debt coverage by cash flow"),
    "De coëfficiënten van OJD91 zijn niet publiek beschikbaar (exclusieve licentie Graydon NV), waardoor de score niet betrouwbaar berekend kan worden. De gebruikte variabelen worden hieronder wel getoond.": (
        "Les coefficients d'OJD91 ne sont pas publics (licence exclusive Graydon NV), de sorte que le score ne peut pas "
        "être calculé de façon fiable. Les variables utilisées sont toutefois présentées ci-dessous.",
        "The OJD91 coefficients are not publicly available (exclusive licence Graydon NV), so the score cannot be "
        "reliably computed. The variables used are shown below.",
    ),
    "Richting van het financieel hefboomeffect (netto rendabiliteit activa vóór bel. \u2212 gem. interestvoet)": (
        "Sens de l'effet de levier financier (rentabilité nette de l'actif avant impôts \u2212 taux d'intérêt moyen)",
        "Direction of the financial leverage effect (net return on assets before tax \u2212 average interest rate)",
    ),
    "Ingehouden winst/reserves ÷ (totaal passiva \u2212 overlopende rekeningen)": (
        "Bénéfices/réserves retenus ÷ (total du passif \u2212 comptes de régularisation)",
        "Retained earnings/reserves ÷ (total liabilities \u2212 accruals)",
    ),
    "Liquide middelen + geldbeleggingen ÷ totaal activa": (
        "Valeurs disponibles + placements de trésorerie ÷ total de l'actif",
        "Cash + short-term investments ÷ total assets",
    ),
    "Vervallen belastingen en RSZ-schulden (indicator > 0)": (
        "Impôts et dettes ONSS échus (indicateur > 0)",
        "Overdue taxes and social security debts (indicator > 0)",
    ),
    "Nettobedrijfskapitaalbehoefte-componenten ÷ totaal activa": (
        "Composantes du besoin en fonds de roulement net ÷ total de l'actif",
        "Net working capital requirement components ÷ total assets",
    ),
    "Netto rendabiliteit van de bedrijfsactiva vóór belasting": (
        "Rentabilité nette des actifs d'exploitation avant impôts",
        "Net return on operating assets before tax",
    ),
    "Financiële schulden ≤1 jaar ÷ schulden ≤1 jaar": (
        "Dettes financières ≤1 an ÷ dettes ≤1 an",
        "Financial debt ≤1yr ÷ debt ≤1yr",
    ),
    "Gewaarborgde schulden ÷ totaal schulden": ("Dettes garanties ÷ total des dettes", "Secured debt ÷ total debt"),

    # ============================ Betrouwbaarheid (betrouwbaarheid.py) ============================
    "Afkeurend oordeel": ("Opinion défavorable", "Adverse opinion"),
    "Oordeelonthouding": ("Déclaration d'abstention", "Disclaimer of opinion"),
    "Oordeel met voorbehoud": ("Opinion avec réserve", "Qualified opinion"),
    "Oordeel zonder voorbehoud": ("Opinion sans réserve", "Unqualified opinion"),
    "Klein positief resultaat (mogelijke winststuring rond nul)": (
        "Petit résultat positif (possible gestion du résultat autour de zéro)",
        "Small positive result (possible earnings management around zero)",
    ),
    "Een resultaat net boven nul kan wijzen op het vermijden van een verlies.": (
        "Un résultat juste au-dessus de zéro peut indiquer l'évitement d'une perte.",
        "A result just above zero may indicate loss avoidance.",
    ),
    "Hoge accruals t.o.v. de activa (hoog)": (
        "Accruals élevés par rapport à l'actif (élevés)",
        "High accruals relative to assets (high)",
    ),
    "Hoge accruals t.o.v. de activa (sterk negatief)": (
        "Accruals élevés par rapport à l'actif (fortement négatifs)",
        "High accruals relative to assets (strongly negative)",
    ),
    "Grote niet-kascomponenten in het resultaat kunnen op resultaatsturing wijzen.": (
        "D'importantes composantes non décaissées du résultat peuvent indiquer une gestion du résultat.",
        "Large non-cash components in the result may indicate earnings management.",
    ),
    "Handelsvorderingen stijgen fors sneller dan de omzet": (
        "Les créances commerciales augmentent nettement plus vite que le chiffre d'affaires",
        "Trade receivables grow much faster than turnover",
    ),
    "Kan wijzen op vervroegde of geflatteerde omzeterkenning.": (
        "Peut indiquer une reconnaissance de revenus anticipée ou embellie.",
        "May indicate premature or inflated revenue recognition.",
    ),
    "Aanzienlijke niet-recurrente resultaten": ("Résultats non récurrents importants", "Significant non-recurring results"),
    "Eenmalige opbrengsten/kosten kunnen het recurrente beeld vertekenen.": (
        "Des produits/charges exceptionnels peuvent fausser l'image récurrente.",
        "One-off income/expenses may distort the recurring picture.",
    ),
    "Opvallend lage belastingdruk bij een positief resultaat": (
        "Charge d'impôt étonnamment faible malgré un résultat positif",
        "Strikingly low tax burden despite a positive result",
    ),
    "Een zeer lage belastinglast bij winst verdient aandacht (kan legitiem zijn).": (
        "Une charge d'impôt très faible en cas de bénéfice mérite attention (peut être légitime).",
        "A very low tax charge on profit warrants attention (may be legitimate).",
    ),
    "Balans is niet in evenwicht": ("Le bilan n'est pas équilibré", "The balance sheet is not balanced"),
    "Activa en passiva sluiten niet op elkaar aan.": ("L'actif et le passif ne concordent pas.", "Assets and liabilities do not match."),
    "Afwijkingen in de wettelijke optelsommen": ("Écarts dans les totaux légaux", "Discrepancies in the statutory subtotals"),
    "Eén of meer subtotalen kloppen niet — controleer de brongegevens.": (
        "Un ou plusieurs sous-totaux sont incorrects — vérifiez les données source.",
        "One or more subtotals are incorrect — check the source data.",
    ),
    "Geen bijzondere indicatoren voor resultaatsturing gedetecteerd": (
        "Aucun indicateur particulier de gestion du résultat détecté",
        "No particular earnings-management indicators detected",
    ),
    "Verhoogde kans op winstmanipulatie": ("Probabilité accrue de manipulation des résultats", "Elevated likelihood of earnings manipulation"),
    "Lage kans op winstmanipulatie": ("Faible probabilité de manipulation des résultats", "Low likelihood of earnings manipulation"),
    "DSRI · dagen debiteuren-index": ("DSRI · indice des jours clients", "DSRI · days sales in receivables index"),
    "GMI · brutomarge-index": ("GMI · indice de marge brute", "GMI · gross margin index"),
    "AQI · activakwaliteit-index": ("AQI · indice de qualité de l'actif", "AQI · asset quality index"),
    "SGI · omzetgroei-index": ("SGI · indice de croissance du CA", "SGI · sales growth index"),
    "DEPI · afschrijvingsindex": ("DEPI · indice d'amortissement", "DEPI · depreciation index"),
    "SGAI · kosten/omzet-index": ("SGAI · indice charges/CA", "SGAI · SG&A expenses index"),
    "LVGI · schuldgraad-index": ("LVGI · indice d'endettement", "LVGI · leverage index"),
    "TATA · totale accruals ÷ activa": ("TATA · accruals totaux ÷ actif", "TATA · total accruals ÷ assets"),
    "Aandachtspunten voor de betrouwbaarheid": ("Points d'attention pour la fiabilité", "Concerns regarding reliability"),
    "Matige betrouwbaarheid — enkele aandachtspunten": ("Fiabilité moyenne — quelques points d'attention", "Moderate reliability — some concerns"),
    "Geen bijzondere betrouwbaarheidsproblemen gedetecteerd": ("Aucun problème particulier de fiabilité détecté", "No particular reliability issues detected"),

    # ============================ Evolutie (evolutie.py) ============================
    "stabiel": ("stable", "stable"),
    "stijging": ("hausse", "increase"),
    "daling": ("baisse", "decrease"),
    "gunstige evolutie": ("évolution favorable", "favourable trend"),
    "ongunstige evolutie": ("évolution défavorable", "unfavourable trend"),

    # ============================ Vergelijken (vergelijk.py) ============================
    "Balanstotaal": ("Total du bilan", "Balance sheet total"),
    "Resultaat van het boekjaar": ("Résultat de l'exercice", "Result for the year"),
    "Solvabiliteit (EV/TV)": ("Solvabilité (CP/total)", "Solvency (equity/total)"),
    "Nettorendabiliteit EV na bel.": ("Rentabilité nette CP après impôts", "Net return on equity after tax"),

    # ============================ Kasstroom-lijnen (kasstroom.py) ============================
    "Winst (verlies) van het boekjaar na belastingen": (
        "Bénéfice (perte) de l'exercice après impôts",
        "Profit (loss) for the year after taxes",
    ),
    "+ Niet-kaskosten (benadering)": ("+ Charges non décaissées (approximation)", "+ Non-cash costs (approximation)"),
    "+ Financiële kaskosten van het vreemd vermogen": ("+ Charges financières décaissées des dettes", "+ Cash financial costs of debt"),
    "= Operationele cashflow na belastingen (1)": ("= Cash-flow opérationnel après impôts (1)", "= Operating cash flow after taxes (1)"),
    "\u2212 Verandering van de nettobedrijfskapitaalbehoefte (2)": (
        "\u2212 Variation du besoin en fonds de roulement net (2)",
        "\u2212 Change in net working capital requirement (2)",
    ),
    "= Kasstroom uit operaties (3) = (1) \u2212 (2)": (
        "= Flux de trésorerie des opérations (3) = (1) \u2212 (2)",
        "= Cash flow from operations (3) = (1) \u2212 (2)",
    ),
    "(Des)investeringen in (uitgebreide) vaste activa (4)": (
        "(Dés)investissements en actifs immobilisés (élargis) (4)",
        "(Dis)investments in (extended) fixed assets (4)",
    ),
    "= Vrije kasstroom voor de onderneming (5) = (3) + (4)": (
        "= Flux de trésorerie disponible pour l'entreprise (5) = (3) + (4)",
        "= Free cash flow to the firm (5) = (3) + (4)",
    ),
    "Financiering met financieel vreemd vermogen (6)": ("Financement par dettes financières (6)", "Financing with financial debt (6)"),
    "= Vrije kasstroom voor de houders van het EV (7) = (5) + (6)": (
        "= Flux de trésorerie disponible pour les actionnaires (7) = (5) + (6)",
        "= Free cash flow to equity holders (7) = (5) + (6)",
    ),
    "Financiering met extern eigen vermogen (8)": ("Financement par capitaux propres externes (8)", "Financing with external equity (8)"),
    "= Mutatie van de kaspositie (9) = (7) + (8)": (
        "= Variation de la trésorerie (9) = (7) + (8)",
        "= Change in cash position (9) = (7) + (8)",
    ),

    # ============================ Rubrieken: balans ============================
    "BALANS NA WINSTVERDELING": ("BILAN APRÈS RÉPARTITION", "BALANCE SHEET AFTER APPROPRIATION"),
    "ACTIVA": ("ACTIF", "ASSETS"),
    "PASSIVA": ("PASSIF", "EQUITY AND LIABILITIES"),
    "Oprichtingskosten": ("Frais d'établissement", "Formation expenses"),
    "Vaste activa": ("Actifs immobilisés", "Fixed assets"),
    "Immateriële vaste activa": ("Immobilisations incorporelles", "Intangible fixed assets"),
    "Materiële vaste activa": ("Immobilisations corporelles", "Tangible fixed assets"),
    "Terreinen en gebouwen": ("Terrains et constructions", "Land and buildings"),
    "Installaties, machines en uitrusting": ("Installations, machines et outillage", "Plant, machinery and equipment"),
    "Meubilair en rollend materieel": ("Mobilier et matériel roulant", "Furniture and vehicles"),
    "Leasing en soortgelijke rechten": ("Location-financement et droits similaires", "Leasing and similar rights"),
    "Overige materiële vaste activa": ("Autres immobilisations corporelles", "Other tangible fixed assets"),
    "Activa in aanbouw en vooruitbetalingen": ("Immobilisations en cours et acomptes versés", "Assets under construction and advance payments"),
    "Financiële vaste activa": ("Immobilisations financières", "Financial fixed assets"),
    "Verbonden ondernemingen": ("Entreprises liées", "Affiliated enterprises"),
    "Deelnemingen": ("Participations", "Participating interests"),
    "Vorderingen": ("Créances", "Amounts receivable"),
    "Ondernemingen met deelnemingsverhouding": ("Entreprises avec lien de participation", "Enterprises linked by participating interests"),
    "Andere financiële vaste activa": ("Autres immobilisations financières", "Other financial fixed assets"),
    "Aandelen": ("Actions et parts", "Shares"),
    "Vorderingen en borgtochten in contanten": ("Créances et cautionnements en numéraire", "Amounts receivable and cash guarantees"),
    "Vlottende activa": ("Actifs circulants", "Current assets"),
    "Vorderingen op meer dan één jaar": ("Créances à plus d'un an", "Amounts receivable after more than one year"),
    "Handelsvorderingen": ("Créances commerciales", "Trade receivables"),
    "Overige vorderingen": ("Autres créances", "Other amounts receivable"),
    "Voorraden en bestellingen in uitvoering": ("Stocks et commandes en cours d'exécution", "Inventories and contracts in progress"),
    "Voorraden": ("Stocks", "Inventories"),
    "Grond- en hulpstoffen": ("Approvisionnements", "Raw materials and consumables"),
    "Goederen in bewerking": ("En-cours de fabrication", "Work in progress"),
    "Gereed product": ("Produits finis", "Finished goods"),
    "Handelsgoederen": ("Marchandises", "Goods purchased for resale"),
    "Onroerende goederen bestemd voor verkoop": ("Immeubles destinés à la vente", "Immovable property intended for sale"),
    "Vooruitbetalingen": ("Acomptes versés", "Advance payments"),
    "Bestellingen in uitvoering": ("Commandes en cours d'exécution", "Contracts in progress"),
    "Vorderingen op ten hoogste één jaar": ("Créances à un an au plus", "Amounts receivable within one year"),
    "Geldbeleggingen": ("Placements de trésorerie", "Short-term investments"),
    "Eigen aandelen": ("Actions propres", "Own shares"),
    "Overige beleggingen": ("Autres placements", "Other investments"),
    "Liquide middelen": ("Valeurs disponibles", "Cash at bank and in hand"),
    "Overlopende rekeningen": ("Comptes de régularisation", "Accruals and deferred income"),
    "Totaal van de activa": ("Total de l'actif", "Total assets"),
    "Eigen vermogen": ("Capitaux propres", "Equity"),
    "Inbreng": ("Apport", "Contribution"),
    "Kapitaal": ("Capital", "Capital"),
    "Geplaatst kapitaal": ("Capital souscrit", "Issued capital"),
    "Niet-opgevraagd kapitaal": ("Capital non appelé", "Uncalled capital"),
    "Buiten kapitaal": ("Hors capital", "Outside capital"),
    "Uitgiftepremies": ("Primes d'émission", "Share premium account"),
    "Andere": ("Autres", "Other"),
    "Herwaarderingsmeerwaarden": ("Plus-values de réévaluation", "Revaluation surpluses"),
    "Reserves": ("Réserves", "Reserves"),
    "Onbeschikbare reserves": ("Réserves indisponibles", "Unavailable reserves"),
    "Wettelijke reserve": ("Réserve légale", "Legal reserve"),
    "Statutair onbeschikbare reserves": ("Réserves statutairement indisponibles", "Statutorily unavailable reserves"),
    "Inkoop eigen aandelen": ("Acquisition d'actions propres", "Acquisition of own shares"),
    "Financiële steunverlening": ("Soutien financier", "Financial support"),
    "Overige": ("Autres", "Other"),
    "Belastingvrije reserves": ("Réserves immunisées", "Tax-free reserves"),
    "Beschikbare reserves": ("Réserves disponibles", "Available reserves"),
    "Overgedragen winst (verlies)": ("Bénéfice (perte) reporté(e)", "Accumulated profits (losses)"),
    "Kapitaalsubsidies": ("Subsides en capital", "Capital subsidies"),
    "Voorschot aan vennoten op netto-actief": ("Avance aux associés sur répartition de l'actif net", "Advance to shareholders on net assets"),
    "Voorzieningen en uitgestelde belastingen": ("Provisions et impôts différés", "Provisions and deferred taxes"),
    "Voorzieningen voor risico's en kosten": ("Provisions pour risques et charges", "Provisions for liabilities and charges"),
    "Pensioenen en soortgelijke verplichtingen": ("Pensions et obligations similaires", "Pensions and similar obligations"),
    "Belastingen": ("Impôts", "Taxation"),
    "Grote herstellings- en onderhoudswerken": ("Grosses réparations et gros entretien", "Major repairs and maintenance"),
    "Milieuverplichtingen": ("Obligations environnementales", "Environmental obligations"),
    "Overige risico's en kosten": ("Autres risques et charges", "Other liabilities and charges"),
    "Uitgestelde belastingen": ("Impôts différés", "Deferred taxes"),
    "Schulden": ("Dettes", "Amounts payable"),
    "Schulden op meer dan één jaar": ("Dettes à plus d'un an", "Amounts payable after more than one year"),
    "Financiële schulden": ("Dettes financières", "Financial debts"),
    "Achtergestelde leningen": ("Emprunts subordonnés", "Subordinated loans"),
    "Niet-achtergestelde obligatieleningen": ("Emprunts obligataires non subordonnés", "Unsubordinated debentures"),
    "Leasingschulden en soortgelijke schulden": ("Dettes de location-financement et assimilées", "Leasing and similar obligations"),
    "Kredietinstellingen": ("Établissements de crédit", "Credit institutions"),
    "Overige leningen": ("Autres emprunts", "Other loans"),
    "Handelsschulden": ("Dettes commerciales", "Trade debts"),
    "Leveranciers": ("Fournisseurs", "Suppliers"),
    "Te betalen wissels": ("Effets à payer", "Bills of exchange payable"),
    "Vooruitbetalingen op bestellingen": ("Acomptes reçus sur commandes", "Advances received on contracts"),
    "Overige schulden": ("Autres dettes", "Other amounts payable"),
    "Schulden op ten hoogste één jaar": ("Dettes à un an au plus", "Amounts payable within one year"),
    "Schulden > 1 jaar binnen jaar vervallen": ("Dettes à plus d'un an échéant dans l'année", "Current portion of amounts payable after more than one year"),
    "Schulden m.b.t. belastingen, bezoldigingen en sociale lasten": ("Dettes fiscales, salariales et sociales", "Taxes, remuneration and social security"),
    "Bezoldigingen en sociale lasten": ("Rémunérations et charges sociales", "Remuneration and social security"),
    "Totaal van de passiva": ("Total du passif", "Total equity and liabilities"),

    # ============================ Rubrieken: resultatenrekening ============================
    "RESULTATENREKENING": ("COMPTE DE RÉSULTATS", "INCOME STATEMENT"),
    "Bedrijfsopbrengsten": ("Produits d'exploitation", "Operating income"),
    "Bedrijfsopbrengsten (totaal)": ("Produits d'exploitation (total)", "Operating income (total)"),
    "Omzet": ("Chiffre d'affaires", "Turnover"),
    "Voorraad goederen in bewerking en gereed product en bestellingen in uitvoering (toename (+)/afname (-))": (
        "En-cours de fabrication, produits finis et commandes en cours d'exécution (augmentation (+)/réduction (-))",
        "Work in progress, finished goods and contracts in progress (increase (+)/decrease (-))",
    ),
    "Geproduceerde vaste activa": ("Production immobilisée", "Own construction capitalised"),
    "Andere bedrijfsopbrengsten": ("Autres produits d'exploitation", "Other operating income"),
    "Niet-recurrente bedrijfsopbrengsten": ("Produits d'exploitation non récurrents", "Non-recurring operating income"),
    "Bedrijfskosten": ("Charges d'exploitation", "Operating charges"),
    "Bedrijfskosten (totaal)": ("Charges d'exploitation (total)", "Operating charges (total)"),
    "Handelsgoederen, grond- en hulpstoffen": ("Marchandises, approvisionnements", "Raw materials, consumables and goods for resale"),
    "Aankopen": ("Achats", "Purchases"),
    "Voorraad (afname (+)/toename (-))": ("Stocks (réduction (+)/augmentation (-))", "Inventories (decrease (+)/increase (-))"),
    "Diensten en diverse goederen": ("Services et biens divers", "Services and other goods"),
    "Bezoldigingen, sociale lasten en pensioenen": ("Rémunérations, charges sociales et pensions", "Remuneration, social security costs and pensions"),
    "Afschrijvingen en waardeverminderingen op oprichtingskosten, immateriële en materiële vaste activa": (
        "Amortissements et réductions de valeur sur frais d'établissement, immobilisations incorporelles et corporelles",
        "Depreciation and write-downs on formation expenses, intangible and tangible fixed assets",
    ),
    "Waardeverminderingen op voorraden, bestellingen in uitvoering en handelsvorderingen (toevoegingen (+)/terugnemingen (-))": (
        "Réductions de valeur sur stocks, commandes en cours et créances commerciales (dotations (+)/reprises (-))",
        "Write-downs on inventories, contracts in progress and trade receivables (additions (+)/reversals (-))",
    ),
    "Voorzieningen voor risico's en kosten (toevoegingen (+)/bestedingen en terugnemingen (-))": (
        "Provisions pour risques et charges (dotations (+)/utilisations et reprises (-))",
        "Provisions for liabilities and charges (additions (+)/uses and reversals (-))",
    ),
    "Andere bedrijfskosten": ("Autres charges d'exploitation", "Other operating charges"),
    "Als herstructureringskosten geactiveerde bedrijfskosten": (
        "Charges d'exploitation portées à l'actif au titre de frais de restructuration",
        "Operating charges capitalised as restructuring costs",
    ),
    "Niet-recurrente bedrijfskosten": ("Charges d'exploitation non récurrentes", "Non-recurring operating charges"),
    "Bedrijfswinst (Bedrijfsverlies (-))": ("Bénéfice (Perte) d'exploitation (-)", "Operating profit (loss) (-)"),
    "Financiële opbrengsten": ("Produits financiers", "Financial income"),
    "Financiële opbrengsten (totaal)": ("Produits financiers (total)", "Financial income (total)"),
    "Recurrente financiële opbrengsten": ("Produits financiers récurrents", "Recurring financial income"),
    "Opbrengsten uit financiële vaste activa": ("Produits des immobilisations financières", "Income from financial fixed assets"),
    "Opbrengsten uit vlottende activa": ("Produits des actifs circulants", "Income from current assets"),
    "Andere financiële opbrengsten": ("Autres produits financiers", "Other financial income"),
    "Niet-recurrente financiële opbrengsten": ("Produits financiers non récurrents", "Non-recurring financial income"),
    "Financiële kosten": ("Charges financières", "Financial charges"),
    "Financiële kosten (totaal)": ("Charges financières (total)", "Financial charges (total)"),
    "Recurrente financiële kosten": ("Charges financières récurrentes", "Recurring financial charges"),
    "Kosten van schulden": ("Charges des dettes", "Debt charges"),
    "Waardeverminderingen op vlottende activa andere dan voorraden, bestellingen in uitvoering en handelsvorderingen (toevoegingen (+)/terugnemingen (-))": (
        "Réductions de valeur sur actifs circulants autres que stocks, commandes en cours et créances commerciales (dotations (+)/reprises (-))",
        "Write-downs on current assets other than inventories, contracts in progress and trade receivables (additions (+)/reversals (-))",
    ),
    "Andere financiële kosten": ("Autres charges financières", "Other financial charges"),
    "Niet-recurrente financiële kosten": ("Charges financières non récurrentes", "Non-recurring financial charges"),
    "Winst (Verlies) van het boekjaar vóór belasting": ("Bénéfice (Perte) de l'exercice avant impôts", "Profit (loss) for the period before taxes"),
    "Onttrekking aan de uitgestelde belastingen": ("Prélèvement sur les impôts différés", "Transfer from deferred taxes"),
    "Overboeking naar de uitgestelde belastingen": ("Transfert aux impôts différés", "Transfer to deferred taxes"),
    "Belastingen op het resultaat": ("Impôts sur le résultat", "Income taxes"),
    "Regularisering van belastingen en terugneming van voorzieningen voor belastingen": (
        "Régularisation d'impôts et reprises de provisions fiscales",
        "Adjustment of income taxes and write-back of tax provisions",
    ),
    "Winst (Verlies) van het boekjaar": ("Bénéfice (Perte) de l'exercice", "Profit (loss) for the period"),
    "Onttrekking aan de belastingvrije reserves": ("Prélèvement sur les réserves immunisées", "Transfer from tax-free reserves"),
    "Overboeking naar de belastingvrije reserves": ("Transfert aux réserves immunisées", "Transfer to tax-free reserves"),
    "Te bestemmen winst (verlies) van het boekjaar": ("Bénéfice (perte) à affecter de l'exercice", "Profit (loss) for the period available for appropriation"),
    "RESULTAATVERWERKING": ("AFFECTATIONS ET PRÉLÈVEMENTS", "APPROPRIATION ACCOUNT"),
    "Te bestemmen winst (verlies)": ("Bénéfice (perte) à affecter", "Profit (loss) to be appropriated"),
    "Overgedragen winst (verlies) van het vorige boekjaar": ("Bénéfice (perte) reporté(e) de l'exercice précédent", "Profit (loss) brought forward from previous period"),
    "Onttrekking aan het eigen vermogen": ("Prélèvements sur les capitaux propres", "Withdrawals from equity"),
    "Onttrekking aan de inbreng": ("Prélèvement sur l'apport", "Withdrawal from contribution"),
    "Onttrekking aan de reserves": ("Prélèvement sur les réserves", "Withdrawal from reserves"),
    "Toevoeging aan het eigen vermogen": ("Affectation aux capitaux propres", "Appropriation to equity"),
    "Toevoeging aan de inbreng": ("Affectation à l'apport", "Appropriation to contribution"),
    "Toevoeging aan de wettelijke reserve": ("Affectation à la réserve légale", "Appropriation to the legal reserve"),
    "Toevoeging aan de overige reserves": ("Affectation aux autres réserves", "Appropriation to other reserves"),
    "Over te dragen winst (verlies)": ("Bénéfice (perte) à reporter", "Profit (loss) to be carried forward"),
    "Tussenkomst van de vennoten in het verlies": ("Intervention des associés dans la perte", "Shareholders' contribution to the loss"),
    "Uit te keren winst": ("Bénéfice à distribuer", "Profit to be distributed"),
    "Vergoeding van de inbreng": ("Rémunération de l'apport", "Remuneration of the contribution"),
    "Vergoeding – bestuurders of zaakvoerders": ("Rémunération – administrateurs ou gérants", "Remuneration – directors or managers"),
    "Vergoeding – werknemers": ("Rémunération – travailleurs", "Remuneration – employees"),
    "Vergoeding – andere rechthebbenden": ("Rémunération – autres ayants droit", "Remuneration – other beneficiaries"),
}
