"""Vercel-entrypoint voor de FAO jaarrekening-analyse.

Vercel zoekt op de repo-root naar een Flask-instantie ``app`` in een van de
ondersteunde entrypoints (app.py / main.py / wsgi.py / index.py) en routeert
alle verzoeken daarnaartoe. De eigenlijke applicatie staat in ``web/app.py``;
hier her-exporteren we ze zodat de bestaande projectstructuur behouden blijft.

Lokaal blijft ``python web/app.py`` gewoon werken.
"""

import os
import sys

# Zorg dat de repo-root op het importpad staat, ongeacht de werkmap waarin
# Vercel de functie uitvoert, zodat de pakketten ``web`` en ``core`` vindbaar zijn.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from web.app import app  # noqa: E402  (import moet na de sys.path-aanpassing)

# Vercel gebruikt de WSGI-callable ``app``.
__all__ = ["app"]

if __name__ == "__main__":
    app.run(debug=True)
