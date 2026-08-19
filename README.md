# Jaarrekening analyse

Dit is een work-in-progress repository van een programma om de jaarrekening te analyseren. 

De jaarrekening kan op verschillende manieren worden ingelezen:
| Methode                          | Ondersteund | Opmerking |
| :------------------------------- | :---------: | :-------- |
| CSV                              |     Ja      | NBB-export met `"code","waarde"`-rijen |
| JSON (jsonxbrl)                  |     Ja      | Gestructureerde NBB-JSON met rubriekcodes |
| PDF                              | Ja (best-effort) | Door de NBB gegenereerde PDF; codes worden uit de tekst gehaald |
| XBRL                             | Via JSON/KBO | Ruwe XBRL bevat de codes niet zelf (die zitten in de taxonomie); gebruik de JSON-export of het KBO-nummer |
| Ondernemingsnummer (KBO/BTW)     |     Ja      | Automatisch ophalen via de gratis NBB-webservice (zie hieronder) |

### Automatisch ophalen via KBO-/BTW-nummer
FAO kan de recentste jaarrekening rechtstreeks ophalen bij de Balanscentrale van de NBB
(webservice "Authentic Data Query"). Dit is gratis, maar vereist eenmalig een gratis
abonnementssleutel: registreer op https://developer.cbso.nbb.be en zet de sleutel als
omgevingsvariabele `NBB_CBSO_SUBSCRIPTION_KEY` (bv. via de Secrets van de omgeving / Vercel).

### Functies
- Balans en resultatenrekening volgens de wettelijke structuur, met conformiteitscontrole.
- Ratio's (toegevoegde waarde, rendabiliteit, solvabiliteit, liquiditeit) met sectorvergelijking.
- Tab **Bestuurders** (naam, functie, adres, mandaat) uit PDF/JSON/KBO.
- Tab **Risico**: Altman Z''-score en gezondheidskwadrant (indicatief krediet-/faillissementsrisico).
- **Vergelijken**: meerdere jaarrekeningen (over de jaren of tussen ondernemingen) met grafieken en een gunstig/ongunstig-oordeel over de evolutie.

## Getting Started
### Online, gemakkelijkst, "it just works"
Er is altijd een instance beschikbaar op https://fao.vuma.be.

### Self-Hosting
Wij bieden ook de mogelijkheid aan om een self-hosted instance op te zetten, voor zij die dit echt wensen. Het is echter steeds makkelijker om gebruik te maken van de hierbovenvermelde instance.

Er wordt een easy one-line installer aangeboden, dit script maakt gebruik van Apache2, Python3 (latest release), Flask en Let's Encrypt voor een SSL-certificaat. **Dit werkt nog niet**
```bash
curl -sSL https://install-fao.vuma.be | bash
```

Het is ook mogelijk om een manuele installatie uit te voeren, dit kan door het easyInstallScript.sh bestand te downloaden. Hierna past u de permissie aan, en voert u dit bestand uit.

Zet programma als executable
```bash
chmod +x easyInstallScript.sh
```
Run programma
```bash
./easyInstallScript.sh
```

### Deployen op Vercel
De repo is klaar om als Python/Flask-app op [Vercel](https://vercel.com) te draaien:

- `api/index.py` is de Vercel-functie die de Flask-app uit `web/app.py` beschikbaar stelt.
- `vercel.json` bouwt die functie (`@vercel/python`), bundelt de templates mee (`includeFiles`) en stuurt via een route alle verzoeken ernaartoe.
- `requirements.txt` wordt automatisch gedetecteerd voor de dependencies.
- `.python-version` pint Python 3.12.

Importeer de Git-repo in Vercel en deploy. Zorg dat de **Root Directory** in de projectinstellingen de repository-root is (niet `web/`). Stel eventueel de omgevingsvariabele `FAO_SECRET_KEY` in voor een stabiele sessiesleutel. Lokaal draai je de app met `python web/app.py`.

## Support
Dit is ontworpen voor gebruik op *nix-based operating systems, zoals Linux en macOS. 
Windows wordt **niet** ondersteund.
## Licensing
Dit softwarepakket wordt gereleased onder de [GNU GPL v3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html), u bent dus vrij om te doen wat u wenst met dit programma, zolang u uw eigen wijzigen ook open source maakt.

## Credits

Dit platform werd ontworpen door
| Naam                 | Affiliatie        | E-mailadres                 |
| :------------------- | ----------------- | --------------------------- |
| Winter van den Bulck | ... | winter.vandenbulck@ugent.be |
| Matthias Van Duysen  | ... | matthias@vanduysen.be       |