# -*- mode: python -*-

block_cipher = None


a = Analysis(['vm_gui.py'],
             pathex=['D:\\Development\\Code\\Python\\vm_manage_version2'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='vm_gui',
          debug=False,
          strip=False,
          upx=True,
          console=False )
