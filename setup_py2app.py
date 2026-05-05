"""
py2app build script for Hermes Translate.
Creates a standalone macOS .app bundle.

Build:
    python setup_py2app.py py2app

Clean:
    rm -rf build dist
"""

from setuptools import setup

APP = ['launcher.py']
APP_NAME = 'Hermes Translate'
DATA_FILES = []

OPTIONS = {
    'py2app': {
        'argv_emulation': False,
        # 'iconfile': 'icon.icns',  # TODO: add icon later
        'plist': {
            # Menu bar only — no dock icon, no app menu in dock
            'LSUIElement': True,
            # App identity
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleIdentifier': 'com.hermes.translate',
            'CFBundleVersion': '0.01',
            'CFBundleShortVersionString': '0.01',
            # High-res display
            'NSHighResolutionCapable': True,
            # Privacy descriptions
            'NSAppleEventsUsageDescription': (
                'Hermes Translate uses Apple Events to copy selected text for translation.'
            ),
            # Accessibility (for pynput global hotkey)
            'NSAccessibilityUsageDescription': (
                'Hermes Translate needs accessibility access to detect the global '
                'translation hotkey (Cmd+Shift+T by default).'
            ),
            # Document types (none — this is a utility)
            'CFBundleDocumentTypes': [],
        },
        'packages': [
            'rumps',
            'pynput',
            'pyperclip',
            'requests',
            'urllib3',
            'certifi',
            'charset_normalizer',
            'idna',
            'six',
        ],
        'includes': [
            'tkinter',
            'json',
            'threading',
            'subprocess',
            'time',
            'os',
            'sys',
            'pathlib',
            'platform',
        ],
        'frameworks': [
            # Tcl/Tk frameworks needed by tkinter
        ],
        'excludes': [
            'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL',
            'cv2', 'tensorflow', 'torch', 'jupyter', 'IPython',
            'pytest', 'setuptools', 'pip', 'wheel',
        ],
        'strip': True,
        'optimize': 2,
        'site_packages': True,
    }
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
    setup_requires=['py2app'],
)
