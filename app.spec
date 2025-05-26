# -*- mode: python ; coding: utf-8 -*-
import zipfile
import os

import importlib.util
import sys
from pathlib import Path

# get name and version from package to use for build
package_path = Path("random_key").resolve()
init_file = package_path / "__init__.py"
package_name = package_path.name
spec = importlib.util.spec_from_file_location(package_name, init_file)
module = importlib.util.module_from_spec(spec)
sys.modules[package_name] = module
spec.loader.exec_module(module)


a = Analysis(
    ["random_key/app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("random_key/*", "random_key"),
        ("random_key/ui/*", "random_key/ui"),
        ("resources/palette/*", "resources/palette"),
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
    [],
    exclude_binaries=True,
    name=module.__name__,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=module.__name__,
)

# Post Build
zip_name = os.path.join("dist", f"{module.__name__}_v{module.__version__}.zip")
dist_path = os.path.join("dist", module.__name__)

print("Zipping build %s" % zip_name)
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(dist_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dist_path)
            zipf.write(full_path, arcname=os.path.join(module.__name__, rel_path))

print("Created zipped build %s" % zip_name)
