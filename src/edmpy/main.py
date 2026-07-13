"""Entry point for python-for-android / Buildozer.

Buildozer looks for ``main.py`` in ``source.dir`` (this folder). The desktop
build still launches via ``python -m edmpy`` (see ``__main__.py``); this file
only exists so the Android/p4a packaging has a top-level entry point. The flat
``from edm import ...`` works because ``source.dir`` is this ``edmpy`` folder,
matching the app's existing flat-import style (``from geo import ...`` etc.).
"""

from edm import EDMApp

if __name__ == '__main__':
    EDMApp().run()
