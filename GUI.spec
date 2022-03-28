# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
    ( 'Multi-OS/Batch_GUI_03232021.ui', '.' ),
    ( 'Multi-OS/Extractor_new.py', '.' ),
    ( 'Multi-OS/parameters.xml', '.' ),
    ( 'Multi-OS/tractor-512.ico', '.' )
]

a = Analysis(['Multi-OS\\GUI.py'],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='RWExtractor,Muprhy_03272022',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='RWExtractor_Murphy_03272022')
