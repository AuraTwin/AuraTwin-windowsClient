# -*- mode: python ; coding: utf-8 -*-
# macOS build spec — produces AuraTwin.app bundle
# Run with: pyinstaller AuraTwin_macOS.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.'), ('AuraTwin_Logo.png', '.')],
    hiddenimports=['PyQt5.sip'],
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
    [],
    exclude_binaries=True,
    name='AuraTwin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX disabled — unreliable on macOS
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # required for proper macOS event handling
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='AuraTwin_Logo.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AuraTwin',
)

app = BUNDLE(
    coll,
    name='AuraTwin.app',
    icon='AuraTwin_Logo.png',
    bundle_identifier='com.auratwin.client',
    info_plist={
        # Camera permission — required by macOS, app will crash without this
        'NSCameraUsageDescription': 'AuraTwin needs camera access to capture frames for emotion analysis.',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleName': 'AuraTwin',
        'CFBundleDisplayName': 'AuraTwin',
        # Allow both light and dark mode
        'NSRequiresAquaSystemAppearance': False,
    },
)
