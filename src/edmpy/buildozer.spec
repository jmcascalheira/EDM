[app]

# (str) Title of your application
title = EDMpy

# (str) Package name
package.name = edmpy

# (str) Package domain (needed for android/ios packaging)
package.domain = com.oldstoneage

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,cfg,txt

# (list) Source files to exclude
source.exclude_exts = spec

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, build, .buildozer

# (str) Application versioning — read from the VERSION string in edm.py so the
# APK version stays in sync with the desktop app.
version.regex = VERSION = ['"](.*)['"]
version.filename = %(source.dir)s/edm.py

# (list) Application requirements
# pyenchant is intentionally omitted (unused native dep). pyjnius is needed for
# the Android Bluetooth backend. All others are pure-Python and pip-installable.
# Kivy 2.3.1 (not the desktop's 2.1.0) — 2.1.0 fails to build under modern p4a
# because it imports the removed `cgi` module. The desktop keeps kivy 2.1.0.
requirements = python3,kivy==2.3.1,tinydb,angles,requests,platformdirs,appdata,pyserial,pyjnius,android

# (str) Supported orientation (one of landscape, portrait, portrait-reverse or all)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions
android.permissions = INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION, WAKE_LOCK

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (bool) keep screen on while the app is in the foreground (needs WAKE_LOCK)
android.wakelock = True

# (list) The Android archs to build for.
# arm64-v8a only during bring-up to halve build time; add armeabi-v7a for release.
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (bool) accept the Android SDK license so unattended CI builds don't hang.
android.accept_sdk_license = True

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
