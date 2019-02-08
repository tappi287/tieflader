# -*- mode: python -*-

block_cipher = None

tief_files = [('locale/de/LC_MESSAGES/*.mo', 'locale/de/LC_MESSAGES'),
              ('locale/en/LC_MESSAGES/*.mo', 'locale/en/LC_MESSAGES'),
              ('ui/gui_resource*', 'ui'),
              ('ui/tieflader*', 'ui'),
              ('license.txt', '.'),]

tief_hidden_imports = ["PySide2.QtXml"]
# tief_binaries = [('/usr/local/lib/libtiff.dylib', '.')]
tief_binaries = [('/System/Library/Frameworks/Tk.framework/Tk', 'tk'),
		         ('/System/Library/Frameworks/Tcl.framework/Tcl', 'tcl')]

a = Analysis(['tieflader.py'],
             pathex=['/Users/stefan/PycharmProjects/tieflader'],
             binaries=tief_binaries,
             datas=tief_files,
             hiddenimports=tief_hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Tieflader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='Tieflader.app',
             icon='ui/AppIcon.icns',
             bundle_identifier=None)
