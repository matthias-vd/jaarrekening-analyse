# Jaarrekening analyse

Dit is een work-in-progress repository van een programma om de jaarrekening te analyseren. 

De jaarrekening kan op verschillende manieren worden ingelezen:
| Methode                                      | Ondersteund |
| :------------------------------------------- | ----------- |
| PDF                                          |     TBD     |
| XBRL                                         |   Nog niet  |
| CSV                                          |   Nog niet  |
| Ondernemingsnummer                           |   Nog niet  |

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
- `vercel.json` bouwt die functie (`@vercel/python`), bundelt de templates en voorbeeld-CSV's mee (`includeFiles`) en stuurt via een route alle verzoeken ernaartoe.
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