## Hexo helper

### development

#### Environment

- python 3.10.5

#### Install packages

run

```
pip install -r requirements.txt
```

#### update i18n locale file

**Configure environment variable**
>This is optional, but recommended.

```
pygettext_path=
```
The value is the path of `pygettext.py`, which is a script to generate `.po`, the locale file for i18n.

Its path most likely looks like this: `{python of your path}\3.10.5\Tools\i18n\pygettext.py`

**1.run script `scripts/compile_translations.py`**

>If environment variable is not configured, it is required to input manually while running script.

>To automatically translate by google, set `auto_translate = true` in `script_config.ini`

.po file will be generated.

**2.run script `scripts/compile_translations.py`**

.mo file will be generated.

You are supposed to see locale file in `locale` directory.

#### Package into .exe

By using Pyinstaller.

**1.install pyinstaller**
```
pip install pyinstaller
```

**2.generate .spec file**
```
pyinstaller --onefile --name "HexoHelper" src/hexo_helper/main.py
```

**3.configure .spec file**

Modify like this:
```
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src\\hexo_helper\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'), # Add data list to exe file
        ('locale', 'locale'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HexoHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/favicon.ico' # Specify an icon for app
)

```

**4.generate .exe package**
```
pyinstaller HexoHelper.spec --clean
```

> For windows user, icon may not immediately update because of file explorer cache.

run this in Administrator Command Prompt may help.
```
taskkill /f /im explorer.exe
del %localappdata%\Microsoft\Windows\Explorer\iconcache*
start explorer.exe
```