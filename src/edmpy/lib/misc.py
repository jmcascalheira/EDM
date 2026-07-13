from os import path
import os
from kivy.utils import platform
from kivy.core.window import Window


def locate_file(filename, cfg_path=None):
    '''
    See if the file as given can be found.
    If not, try to find it in the same folder as the CFG file.
    This can happen when a CFG and associated files are copied to a
    new folder or computer or device.
    '''
    if path.isfile(filename):
        return filename
    if cfg_path:
        p, f = path.split(filename)
        if path.isfile(path.join(cfg_path, f)):
            return path.join(cfg_path, f)
    return ''


def filename_only(filename=None):
    if filename:
        p, f = path.split(filename)
        return f
    else:
        return ''


def platform_name():
    # return "Android"
    return (['Windows', 'Linux', 'Android', 'MacOSX', 'IOS', 'Unknown'][['win', 'linux', 'android', 'macosx', 'ios', 'unknown'].index(platform)])


def android_storage_dir():
    '''A writable, user-reachable folder on Android: the app's external files
    dir (e.g. /storage/emulated/0/Android/data/<pkg>/files), which the app can
    read/write without runtime permissions and where users can drop CFG/JSON
    files via USB or a file manager. Returns '' off Android or if unresolved.'''
    if platform_name() != 'Android':
        return ''
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ext = PythonActivity.mActivity.getExternalFilesDir(None)
        if ext is not None:
            p = ext.getAbsolutePath()
            os.makedirs(p, exist_ok=True)
            return p
    except Exception:
        pass
    try:
        from android.storage import app_storage_path
        p = app_storage_path()
        os.makedirs(p, exist_ok=True)
        return p
    except Exception:
        return ''


def default_document_dir():
    '''Where file dialogs should start and where new files default to. On
    Android this is the app's external files dir; elsewhere the user's
    documents folder.'''
    if platform_name() == 'Android':
        android = android_storage_dir()
        if android:
            return android
    from platformdirs import user_documents_dir
    return user_documents_dir()


def restore_window_size_position(main_name, main_ini):
    # On Android (and iOS) the window is full-screen and managed by the OS;
    # setting Window.top/left/size is ignored at best and harmful at worst.
    if platform_name() in ('Android', 'IOS'):
        return
    Window.minimum_width = 450
    Window.minimum_height = 450
    if main_ini.get_value(main_name, "SCREENTOP"):
        temp = max(int(main_ini.get_value(main_name, "SCREENTOP")), 0)
        Window.top = temp
    if not main_ini.get_value(main_name, "SCREENLEFT") == '':
        temp = max(int(main_ini.get_value(main_name, "SCREENLEFT")), 0)
        Window.left = temp
    window_width = None
    window_height = None
    if not main_ini.get_value(main_name, "SCREENWIDTH") == '':
        window_width = max(int(main_ini.get_value(main_name, "SCREENWIDTH")), 450)
    if not main_ini.get_value(main_name, "SCREENHEIGHT") == '':
        window_height = max(int(main_ini.get_value(main_name, "SCREENHEIGHT")), 450)
    if window_width and window_height:
        Window.size = (window_width, window_height)
