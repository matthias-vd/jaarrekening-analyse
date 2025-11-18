# Jaarrekening analyse

Dit is een work-in-progress repository van een programma om de jaarrekening te analyseren. 

De jaarrekening kan op verschillende manieren worden ingelezen:
| Methode                                      | Ondersteund |
| :------------------------------------------- | ----------- |
| PDF                                          |     N/A     |
| XBRL                                         |   Nog niet  |
| CSV                                          |   Nog niet  |
| Ondernemingsnummer                           |   Nog niet  |

## Getting Started
### Online, gemakkelijkst, "it just works"
Er is altijd een instance beschikbaar op https://fao.vuma.be.

### Self-Hosting
Wij bieden ook de mogelijkheid aan om een self-hosted instance op te zetten, voor zij die dit echt wensen. Het is echter steeds makkelijker om gebruik te maken van de hierbovenvermelde instance.

Er wordt een easy one-line installer aangeboden, dit script maakt gebruik van Apache2, Python3 (latest release), Flask en Let's Encrypt voor een SSL-certificaat.
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
## Licensing
Dit softwarepakket wordt gereleased onder de [GNU GPL v3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html), u bent dus vrij om te doen wat u wenst met dit programma, zolang u uw eigen wijzigen ook open source maakt.

## Credits

Dit platform werd ontworpen door
| Naam                 | Affiliatie        | E-mailadres                 |
| :------------------- | ----------------- | --------------------------- |
| Winter van den Bulck | Universiteit Gent | winter.vandenbulck@ugent.be |
| Matthias Van Duysen  | Universiteit Gent | matthias@vanduysen.be       |