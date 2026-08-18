"""Vercel-functie-entrypoint voor de FAO jaarrekening-analyse.

Vercel draait Python-apps als serverless functions in de map ``api/``.
Deze functie stelt de WSGI-callable ``app`` beschikbaar; de eigenlijke
applicatie staat in ``web/app.py``. Alle verzoeken worden via de route in
``vercel.json`` naar deze functie doorgestuurd.
"""

import os
import sys

# De repo-root op het importpad zetten zodat de pakketten ``web`` en ``core``
# vindbaar zijn, ongeacht de werkmap waarin Vercel de functie uitvoert.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from web.app import app  # noqa: E402  (import na sys.path-aanpassing)

# Vercel gebruikt de WSGI-callable ``app``.
__all__ = ["app"]
