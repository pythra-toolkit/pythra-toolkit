import sys
import os
from pathlib import Path
sys.path.insert(0, '/home/red-x/Documents/pythra-toolkit/src/pythra')
from pythra.package_manager import PackageManager

pm = PackageManager(Path('/home/red-x/Documents/pythra-toolkit'))
all_pkgs = pm.discover_all_packages()
print("Discovered packages:")
for name in all_pkgs:
    print(f" - {name}")

print("\nDependency Graph Order:")
import pprint
try:
    loaded, warnings = pm.resolve_and_load_packages(['pythra_video_player'])
    print("Loaded packages:")
    for k in loaded.keys(): print(f" - {k}")
    print("Warnings:", warnings)
except Exception as e:
    print("Error:", e)
