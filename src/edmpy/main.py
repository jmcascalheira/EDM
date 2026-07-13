"""Entry point for python-for-android / Buildozer.

Buildozer looks for ``main.py`` in ``source.dir`` (this folder). The desktop
build still launches via ``python -m edmpy`` (see ``__main__.py``).

This wraps the whole startup so that ANY unhandled exception (during import,
app init, or the first render loop) is written to a retrievable file and to
Android logcat, instead of the app silently closing with a black screen.
"""

import os
import sys
import traceback


def _crash_dirs():
    dirs = []
    # The app's external files dir (reachable over USB): Android/data/<pkg>/files
    try:
        from jnius import autoclass
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        ext = activity.getExternalFilesDir(None)
        if ext is not None:
            dirs.append(ext.getAbsolutePath())
    except Exception:
        pass
    dirs += ['/sdcard/Download', os.path.expanduser('~'), '.']
    return dirs


def _log_crash(text):
    banner = 'EDM CRASH:\n' + text
    try:
        sys.stderr.write(banner + '\n')
        print(banner)          # -> Android logcat under the python tag
    except Exception:
        pass
    for d in _crash_dirs():
        try:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, 'EDM_crash.log'), 'w') as f:
                f.write(text)
            return
        except Exception:
            continue


if __name__ == '__main__':
    try:
        from edm import EDMApp
        EDMApp().run()
    except Exception:
        _log_crash(traceback.format_exc())
        raise
