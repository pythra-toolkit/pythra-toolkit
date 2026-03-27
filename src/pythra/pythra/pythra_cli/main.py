#!/usr/bin/env python3
"""
pythra_cli/main.py - The official Command Line Interface for the Pythra Framework.

Usage:
    pythra create-project <name>         # Create a new, ready-to-use project.
    pythra run [--script <path>]         # Run the project with a clean-restart loop.
    pythra build [--script <path>]       # Build a standalone application folder.
    pythra package <command>             # Package management commands.
"""
from __future__ import annotations
import typer
import os
import shutil
import subprocess
import sys
import atexit
import yaml
import json
import zlib
import base64
import stat
import time
import uuid
import platform
from pathlib import Path
from typing import List, Any, Optional

# Optional readline support for interactive history (arrow keys)
try:
    import readline  # type: ignore
except ImportError:
    try:
        import pyreadline3 as readline # type: ignore
    except ImportError:
        try:
            import pyreadline as readline # type: ignore
        except ImportError:
            readline = None

def _init_cli_history(app_name: str = "pythra") -> None:
    """Initializes command-line history for interactive sessions."""
    if not readline:
        return
    try:
        # Determine platform sub-directory for Pythra platform-aware projects
        system = platform.system().lower()
        if 'win' in system:
            platform_sub = "windows"
        elif 'darwin' in system:
            platform_sub = "macos"
        else:
            platform_sub = "linux"

        # Attempt to locate a project config.yaml in cwd or parent dirs
        project_dir = None
        cfg_path = None
        p = Path.cwd()
        while True:
            candidate = p / "config.yaml"
            if candidate.exists():
                project_dir = p
                cfg_path = candidate
                break
            if p.parent == p:
                break
            p = p.parent

        # Prefer app_name from config.yaml when available
        chosen_name = app_name
        if cfg_path:
            try:
                cfg = yaml.safe_load(cfg_path.read_text(encoding='utf-8'))
                if isinstance(cfg, dict) and cfg.get('app_name'):
                    chosen_name = str(cfg.get('app_name'))
                    print(f"[CLI] Using app name from config.yaml: {chosen_name}")  
            except Exception:
                pass

        # Fallback to project folder name when present
        elif project_dir and (not chosen_name or chosen_name.strip() == ""):
            chosen_name = project_dir.name

        # Sanitize filename
        sanitized = ''.join(c if (c.isalnum() or c in ('-', '_')) else '_' for c in chosen_name).strip().lower()
        if not sanitized:
            sanitized = 'pythra'

        print(f"[CLI] Using sanitized name: {sanitized}")

        # Determine history file path: platform-specific dir > project root > home dir
        if project_dir:
            # Check if the requested platform-aware directory exists (e.g., linux/, windows/)
            platform_dir = project_dir / platform_sub
            if platform_dir.exists() and platform_dir.is_dir():
                histfile = str((platform_dir / f".{sanitized}_history").resolve())
            else:
                histfile = str((project_dir / f".{sanitized}_history").resolve())
        else:
            histfile = os.path.expanduser(f"~/.{sanitized}_history")

        try:
            # Ensure parent directory exists
            parent = os.path.dirname(histfile)
            if parent and not os.path.exists(parent):
                try:
                    os.makedirs(parent, exist_ok=True)
                except Exception:
                    pass
            
            # Touch history file if it doesn't exist
            if not os.path.exists(histfile):
                open(histfile, "a").close()
                
            try:
                readline.read_history_file(histfile)
            except Exception:
                pass
                
            readline.set_history_length(1000)
            
            # Register save on exit
            def _save_history():
                try:
                    if readline:
                        readline.write_history_file(histfile)
                except Exception:
                    pass
            
            atexit.register(_save_history)
        except Exception:
            pass
    except Exception:
        # Don't let history initialization break the CLI
        return
# --- Typer App Initialization ---
app = typer.Typer(
    name="pythra",
    help="The official CLI for the Pythra Framework.",
    add_completion=False
)

# --- Package Management Integration ---
try:
    # Try relative import first (when used as module)
    from .package_commands import package_app
except ImportError:
    try:
        # Fall back to direct import (when run as script)
        from package_commands import package_app
    except ImportError as e:
        # If both fail, package commands aren't available
        package_app = None
        PACKAGE_COMMANDS_AVAILABLE = False
        print(f"[Warning] Package management commands not available: {e}")

if package_app is not None:
    app.add_typer(package_app, name="package", help="Package management commands")
    PACKAGE_COMMANDS_AVAILABLE = True
else:
    PACKAGE_COMMANDS_AVAILABLE = False

# --- Helper Functions (Your implementation is excellent and unchanged) ---

def load_yaml(path: Path) -> dict:
    """Safely loads a YAML file."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def set_debug_false_in_obj(obj: Any) -> None:
    """Recursively sets any 'debug' key to False in a nested object."""
    if isinstance(obj, dict):
        for key, val in list(obj.items()):
            if isinstance(key, str) and key.strip().lower() == "debug":
                obj[key] = False
            else:
                set_debug_false_in_obj(val)
    elif isinstance(obj, list):
        for item in obj:
            set_debug_false_in_obj(item)

def generate_embedded_config_module_in_dir(
    dest_dir: Path, data: Any, module_name: str = "_embedded_config.py"
) -> Path:
    """Generates a Python module containing a compressed config."""
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    # print(f"Config data: {data}")
    json_bytes = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    compressed = zlib.compress(json_bytes, level=9)
    b64 = base64.b64encode(compressed).decode("ascii")
    module_path = (dest_dir / module_name).resolve()
    module_contents = f'''"""Auto-generated embedded config module."""
import json, zlib, base64
_CONFIG_B64 = """{b64}"""
def load_embedded_config():
    try:
        raw = base64.b64decode(_CONFIG_B64.encode("ascii"))
        json_bytes = zlib.decompress(raw)
        return json.loads(json_bytes.decode("utf-8"))
    except Exception as e:
        raise RuntimeError("Failed to load embedded config") from e
CONFIG = load_embedded_config()
'''
    with module_path.open("w", encoding="utf-8") as fh:
        fh.write(module_contents)
    print(f"[+] Generated embedded config module: {module_path}")
    return module_path

def force_rmtree(path: Path, retries: int = 5, delay: float = 0.5):
    """Robustly removes a directory tree, handling potential file locks on Windows."""
    def onerror(func, p_str, exc_info):
        p = Path(p_str)
        if not os.access(p, os.W_OK):
            os.chmod(p, stat.S_IWUSR)
            func(p_str)
        else:
            raise
    for i in range(retries):
        try:
            shutil.rmtree(path, onerror=onerror)
            return
        except PermissionError:
            print(f"[!] PermissionError removing {path}, retrying {i+1}/{retries}")
            time.sleep(delay)
    try:
        tmp_name = path.parent / f"__old_{path.name}_{uuid.uuid4().hex}"
        path.rename(tmp_name)
        shutil.rmtree(tmp_name, onerror=onerror)
        print(f"[+] Renamed and removed locked folder: {tmp_name}")
    except Exception as e:
        print(f"[!] Could not remove build folder even after retries: {e}")
        raise


# --- Shared Project Identity & Platform Dir Helpers ---

def _derive_app_identity(project_name: str) -> tuple:
    """
    Derive a proper app_name and app_id from a project directory name.
    
    Examples:
        "new-app"       -> ("New App", "com.pythra.new-app")
        "my_cool_app"   -> ("My Cool App", "com.pythra.my-cool-app")
        "HelloWorld"    -> ("HelloWorld", "com.pythra.helloworld")
    
    Returns:
        (app_name, app_id)
    """
    # app_name: replace - and _ with spaces, title-case
    app_name = project_name.replace('-', ' ').replace('_', ' ').title()
    # app_id: lowercase, replace _ with -, remove invalid chars
    sanitized = project_name.lower().replace('_', '-').replace(' ', '-')
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '-')
    app_id = f"com.pythra.{sanitized}"
    return app_name, app_id


def _generate_platform_dirs(project_root: Path, app_name: str, app_id: str, source_icon_path: Path = None):
    """
    Generate platform-specific directories with actual project values.
    
    Creates:
    - windows/appIcon.ico (from source_icon_path or template)
    - macos/appIcon.icns + Info.plist (with real app_name/app_id)
    - linux/hicolor/*/apps/appIcon.png + appIcon.desktop (with real values)
    
    If source_icon_path is None, copies icon files from the project template.
    If Pillow is available and source_icon_path is provided, generates fresh icons.
    """
    template_dir = Path(__file__).parent.parent / 'project_template'
    
    # --- Determine icon source ---
    generate_from_png = False
    if source_icon_path and source_icon_path.exists():
        try:
            from PIL import Image
            generate_from_png = True
        except ImportError:
            generate_from_png = False
    
    if not source_icon_path or not source_icon_path.exists():
        # Use the default Pythra appIcon.png from assets_template
        default_icon = Path(__file__).parent.parent / 'assets_template' / 'appIcon.png'
        if default_icon.exists():
            source_icon_path = default_icon
            try:
                from PIL import Image
                generate_from_png = True
            except ImportError:
                generate_from_png = False
    
    # --- WINDOWS ---
    windows_dir = project_root / "windows"
    windows_dir.mkdir(parents=True, exist_ok=True)
    
    if generate_from_png:
        from PIL import Image
        source = Image.open(source_icon_path).convert("RGBA")
        ico_sizes = [(s, s) for s in [16, 24, 32, 48, 64, 128, 256]]
        source.save(str(windows_dir / "appIcon.ico"), format='ICO', sizes=ico_sizes)
    else:
        # Fallback: copy from template 
        template_ico = template_dir / "windows" / "appIcon.ico"
        if template_ico.exists():
            shutil.copy2(template_ico, windows_dir / "appIcon.ico")
    print(f"  ✅ windows/appIcon.ico")
    
    # --- MACOS ---
    macos_dir = project_root / "macos"
    macos_dir.mkdir(parents=True, exist_ok=True)
    
    if generate_from_png:
        import io as _io
        import struct as _struct
        from PIL import Image
        source = Image.open(source_icon_path).convert("RGBA")
        icns_types = [
            (b'icp4', 16), (b'icp5', 32), (b'icp6', 64),
            (b'ic07', 128), (b'ic08', 256), (b'ic09', 512), (b'ic10', 1024),
        ]
        body = b''
        for type_code, size in icns_types:
            resized = source.resize((size, size), Image.Resampling.LANCZOS)
            buf = _io.BytesIO()
            resized.save(buf, format='PNG')
            png_data = buf.getvalue()
            entry_size = len(png_data) + 8
            body += type_code + _struct.pack('>I', entry_size) + png_data
        total_size = len(body) + 8
        icns_data = b'icns' + _struct.pack('>I', total_size) + body
        (macos_dir / "appIcon.icns").write_bytes(icns_data)
    else:
        template_icns = template_dir / "macos" / "appIcon.icns"
        if template_icns.exists():
            shutil.copy2(template_icns, macos_dir / "appIcon.icns")
    
    # Always generate Info.plist with actual values
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleIconFile</key>
    <string>appIcon</string>
    <key>CFBundleIdentifier</key>
    <string>{app_id}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
    (macos_dir / "Info.plist").write_text(info_plist)
    print(f"  ✅ macos/appIcon.icns + Info.plist")
    
    # --- LINUX ---
    linux_dir = project_root / "linux"
    hicolor_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    
    if generate_from_png:
        from PIL import Image
        source = Image.open(source_icon_path).convert("RGBA")
        for size in hicolor_sizes:
            icon_dir = linux_dir / f"hicolor/{size}x{size}/apps"
            icon_dir.mkdir(parents=True, exist_ok=True)
            resized = source.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(str(icon_dir / "appIcon.png"), format='PNG')
    else:
        # Copy hicolor icons from template
        template_linux = template_dir / "linux" / "hicolor"
        if template_linux.exists():
            dest_hicolor = linux_dir / "hicolor"
            if dest_hicolor.exists():
                shutil.rmtree(dest_hicolor)
            shutil.copytree(template_linux, dest_hicolor)
    
    # Always generate .desktop with actual values
    # Filename follows FreeDesktop standard: {app_id}.desktop
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=A PyThra desktop application
Exec={app_id}
Icon={app_id}
Terminal=false
Categories=Utility;
StartupWMClass={app_id}
"""
    linux_dir.mkdir(parents=True, exist_ok=True)
    # Remove old appIcon.desktop if it exists
    old_desktop = linux_dir / "appIcon.desktop"
    if old_desktop.exists():
        old_desktop.unlink()
    (linux_dir / f"{app_id}.desktop").write_text(desktop_content)
    print(f"  ✅ linux/hicolor icons + {app_id}.desktop")


def _update_config_yaml(config_path: Path, app_name: str, app_id: str, overwrite: bool = False):
    """
    Update config.yaml: set app_name/app_id if defaults, add missing keys.
    """
    try:
        current = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        if not isinstance(current, dict):
            current = {}
    except Exception:
        current = {}
    
    # Set app_name and app_id if they're still defaults or missing
    # We check for a few common defaults including empty strings
    defaults_names = ['My Pythra App', 'my_pythra_app', 'my-pythra-app', '']
    defaults_ids = ['com.pythra.my-pythra-app', 'com.pythra.my_pythra_app', '']
    
    if overwrite or current.get('app_name', 'My Pythra App') in defaults_names:
        current['app_name'] = app_name
    if overwrite or 'app_id' not in current or current.get('app_id') in defaults_ids:
        current['app_id'] = app_id
    
    # Add any missing default keys
    try:
        from pythra.config import DEFAULT_CONFIG
    except ImportError:
        DEFAULT_CONFIG = {
            'app_name': 'My Pythra App',
            'app_id': 'com.pythra.my-pythra-app',
            'win_width': 1280, 'win_height': 720,
            'min_win_width': 400, 'min_win_height': 300,
            'frameless': False, 'maximixed': False, 'fixed_size': False,
            'Debug': True, 'render_dir': 'render', 'assets_dir': 'assets',
            'assets_server_port': 8008,
        }
    
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in current:
            current[key] = default_value
    
    with config_path.open("w", encoding="utf-8") as fh:
        yaml.dump(current, fh, indent=4, sort_keys=False)




@app.command()
def create_project(project_name: str = typer.Argument(..., help="The name for the new project directory.")):
    """Creates a new Pythra project with a standard directory structure."""
    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"❌ Error: Directory '{project_name}' already exists.")
        raise typer.Exit(code=1)
    print(f"✅ Creating a new Pythra project in: {project_path}")
    try:
        template_path = Path(__file__).parent.parent / 'project_template'
        if not template_path.exists():
            print(f"❌ Fatal Error: Could not find project template at '{template_path}'")
            raise typer.Exit(code=1)
        
        # Copy template but EXCLUDE platform dirs (we generate those dynamically)
        shutil.copytree(
            template_path, project_path,
            ignore=shutil.ignore_patterns('windows', 'macos', 'linux')
        )
        
        # Derive project-specific identity from directory name
        app_name, app_id = _derive_app_identity(project_name)
        
        # Generate platform dirs with actual project values
        print("\n🖼️  Generating platform icons...")
        _generate_platform_dirs(project_path, app_name, app_id)
        
        # Always ensure config.yaml is created/updated with real project name and app_id
        config_path = project_path / "config.yaml"
        _update_config_yaml(config_path, app_name, app_id, overwrite=True)
        print(f"  ✅ config.yaml (app_name: {app_name}, app_id: {app_id})")
        
        print("\n🎉 Project created successfully!")
        print("To get started:")
        print(f"  1. cd {project_name}")
        print(f"  2. pythra run")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        if project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(code=1)


@app.command(name="generate-icons")
def generate_icons(
    source_png: str = typer.Argument(..., help="Path to the source .png icon file (ideally 1024x1024)."),
    output_dir: str = typer.Option(None, "--output", "-o", help="Output directory. Defaults to project root (current directory)."),
):
    """
    Generate all platform icons from a single PNG file.
    
    Creates windows/appIcon.ico, macos/appIcon.icns, and linux/hicolor icons
    in one command. No manual icon conversion needed — just bring your PNG!
    """
    source_path = Path(source_png).resolve()
    if not source_path.exists():
        print(f"❌ Source PNG not found: {source_path}")
        raise typer.Exit(code=1)
    if not source_path.suffix.lower() == '.png':
        print(f"⚠️  Warning: File does not have .png extension: {source_path.name}")

    try:
        from PIL import Image
    except ImportError:
        print("❌ Pillow is required for icon generation. Install it with:")
        print("   pip install Pillow")
        raise typer.Exit(code=1)

    project_root = Path(output_dir).resolve() if output_dir else Path.cwd()
    
    print(f"\n🎨 Generating cross-platform icons from: {source_path}")
    print(f"   Output directory: {project_root}\n")

    source = Image.open(source_path).convert("RGBA")
    w, h = source.size
    print(f"   Source size: {w}x{h}")
    if w < 512 or h < 512:
        print(f"   ⚠️  Recommended minimum source size is 1024x1024 for best quality.")
    if w != h:
        print(f"   ⚠️  Source image is not square ({w}x{h}). Icons will be stretched.")
    print()

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    hicolor_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    # Apple ICNS type codes → pixel sizes
    icns_types = [
        (b'icp4', 16), (b'icp5', 32), (b'icp6', 64),
        (b'ic07', 128), (b'ic08', 256), (b'ic09', 512), (b'ic10', 1024),
    ]

    def resize_icon(img, size):
        return img.resize((size, size), Image.Resampling.LANCZOS)

    # --- Windows .ico ---
    windows_dir = project_root / "windows"
    windows_dir.mkdir(parents=True, exist_ok=True)
    ico_path = windows_dir / "appIcon.ico"
    source.save(str(ico_path), format='ICO', sizes=[(s, s) for s in ico_sizes])
    print(f"  ✅ Windows: {ico_path} ({len(ico_sizes)} sizes)")

    # --- macOS .icns ---
    import io as _io
    import struct as _struct

    macos_dir = project_root / "macos"
    macos_dir.mkdir(parents=True, exist_ok=True)
    icns_path = macos_dir / "appIcon.icns"
    
    body = b''
    for type_code, size in icns_types:
        resized = resize_icon(source, size)
        buf = _io.BytesIO()
        resized.save(buf, format='PNG')
        png_data = buf.getvalue()
        entry_size = len(png_data) + 8
        body += type_code + _struct.pack('>I', entry_size) + png_data
    
    total_size = len(body) + 8
    icns_data = b'icns' + _struct.pack('>I', total_size) + body
    icns_path.write_bytes(icns_data)
    print(f"  ✅ macOS:   {icns_path} ({len(icns_types)} sizes, {len(icns_data)} bytes)")

    # --- Linux hicolor PNGs ---
    linux_dir = project_root / "linux"
    for size in hicolor_sizes:
        icon_dir = linux_dir / f"hicolor/{size}x{size}/apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        resized = resize_icon(source, size)
        resized.save(str(icon_dir / "appIcon.png"), format='PNG')
    print(f"  ✅ Linux:   {linux_dir}/hicolor/*/apps/appIcon.png ({len(hicolor_sizes)} sizes)")

    # --- Linux .desktop file ---
    desktop_path = linux_dir / "appIcon.desktop"
    # Read app_name from config if available
    app_name = "My Pythra App"
    app_id_val = "com.pythra.app"
    config_path = project_root / "config.yaml"
    if config_path.exists():
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding='utf-8'))
            if isinstance(cfg, dict):
                app_name = cfg.get('app_name', app_name)
                app_id_val = cfg.get('app_id', app_id_val)
        except Exception:
            pass
    
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=A PyThra desktop application
Exec={app_id_val}
Icon=appIcon
Terminal=false
Categories=Utility;
StartupWMClass={app_id_val}
"""
    desktop_path.write_text(desktop_content)
    print(f"  ✅ Linux:   {desktop_path}")

    print(f"\n🎉 All platform icons generated successfully!")
    print(f"   Your app icon is now ready for Windows, macOS, and Linux.")


@app.command()
def upgrade(
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview what would change without modifying anything."),
    force: bool = typer.Option(False, "--force", help="Overwrite all files, even if they already exist."),
    skip_render: bool = typer.Option(False, "--skip-render", help="Don't sync render/ directory files."),
    skip_icons: bool = typer.Option(False, "--skip-icons", help="Don't copy platform icon directories."),
    skip_config: bool = typer.Option(False, "--skip-config", help="Don't update config.yaml with new fields."),
):
    """
    Upgrade an existing PyThra project to match the current template version.
    
    Syncs render engine files, adds missing platform directories (windows/,
    macos/, linux/), and adds new config.yaml fields — all without touching
    your application code (lib/) or overwriting your customizations.
    """
    project_root = Path.cwd()
    
    # Verify this is a PyThra project
    config_path = project_root / "config.yaml"
    if not config_path.exists():
        print(f"❌ Error: No config.yaml found in {project_root}")
        print(f"   Are you in a PyThra project directory?")
        raise typer.Exit(code=1)
    
    # Find the template directory inside the installed pythra package
    template_dir = Path(__file__).parent.parent / 'project_template'
    if not template_dir.exists():
        print(f"❌ Error: Project template not found at {template_dir}")
        raise typer.Exit(code=1)
    
    label = "DRY RUN: " if dry_run else ""
    print(f"\n🔄 {label}Upgrading PyThra project at: {project_root}")
    print(f"   Template source: {template_dir}\n")
    
    stats = {"added": 0, "updated": 0, "skipped": 0}
    
    # =====================================================================
    # 1. SYNC RENDER/ DIRECTORY — Framework engine files only
    # =====================================================================
    if not skip_render:
        print("📁 [1/3] Syncing render/ directory...")
        template_render = template_dir / "render"
        project_render = project_root / "render"
        
        if template_render.exists():
            # Walk the template render dir and sync files
            # We sync ALL files EXCEPT index.html (user's generated content)
            # and styles.css (dynamically generated at runtime)
            user_owned_files = {"index.html", "styles.css"}
            
            for template_file in template_render.rglob("*"):
                if template_file.is_dir():
                    continue
                    
                relative = template_file.relative_to(template_render)
                dest_file = project_render / relative
                
                # Skip user-owned files unless --force
                if relative.name in user_owned_files and not force:
                    stats["skipped"] += 1
                    continue
                
                # Check if update is needed
                needs_update = False
                if not dest_file.exists():
                    needs_update = True
                    action = "ADD"
                elif force:
                    needs_update = True
                    action = "OVERWRITE"
                else:
                    # Compare file contents to see if template is newer
                    try:
                        template_content = template_file.read_bytes()
                        dest_content = dest_file.read_bytes()
                        if template_content != dest_content:
                            needs_update = True
                            action = "UPDATE"
                        else:
                            stats["skipped"] += 1
                            continue
                    except Exception:
                        needs_update = True
                        action = "UPDATE"
                
                if needs_update:
                    print(f"   {action}: render/{relative}")
                    if not dry_run:
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(template_file, dest_file)
                    if action == "ADD":
                        stats["added"] += 1
                    else:
                        stats["updated"] += 1
        else:
            print("   ⚠️  No template render/ directory found. Skipping.")
    else:
        print("📁 [1/3] Skipping render/ sync (--skip-render)")
        
    # =====================================================================
    # 2. GENERATE PLATFORM DIRECTORIES — windows/, macos/, linux/
    # =====================================================================
    if not skip_icons:
        print("\n🖼️  [2/3] Generating platform icon directories...")
        
        # Derive identity from project directory name
        project_name = project_root.name
        app_name, app_id = _derive_app_identity(project_name)
        
        # Read existing config to respect user-set values
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding='utf-8'))
            if isinstance(cfg, dict):
                if cfg.get('app_name') and cfg['app_name'] != 'My Pythra App':
                    app_name = cfg['app_name']
                if cfg.get('app_id') and cfg['app_id'] != 'com.pythra.my-pythra-app':
                    app_id = cfg['app_id']
        except Exception:
            pass
        
        # Check if dirs already exist
        has_all = all((project_root / d).exists() for d in ["windows", "macos", "linux"])
        
        if has_all and not force:
            # Dirs exist — only regenerate text files (.desktop, Info.plist) to fix values
            print(f"   Platform dirs already exist. Regenerating metadata files...")
            print(f"   (app_name: {app_name}, app_id: {app_id})")
            if not dry_run:
                # Regenerate .desktop with actual values
                linux_dir = project_root / "linux"
                desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=A PyThra desktop application
Exec={app_id}
Icon={app_id}
Terminal=false
Categories=Utility;
StartupWMClass={app_id}
"""
                # Remove old appIcon.desktop if it exists
                old_desktop = linux_dir / "appIcon.desktop"
                if old_desktop.exists():
                    old_desktop.unlink()
                (linux_dir / f"{app_id}.desktop").write_text(desktop_content)
                
                # Regenerate Info.plist with actual values
                macos_dir = project_root / "macos"
                info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleIconFile</key>
    <string>appIcon</string>
    <key>CFBundleIdentifier</key>
    <string>{app_id}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
                (macos_dir / "Info.plist").write_text(info_plist)
            stats["updated"] += 2
        else:
            # Generate fresh platform dirs
            print(f"   Generating platform dirs (app_name: {app_name}, app_id: {app_id})")
            if not dry_run:
                _generate_platform_dirs(project_root, app_name, app_id)
            stats["added"] += 12  # approximate file count
    else:
        print("\n🖼️  [2/3] Skipping platform icons (--skip-icons)")
    
    # =====================================================================
    # 3. UPDATE CONFIG.YAML — Project-specific identity + missing keys
    # =====================================================================
    if not skip_config:
        print("\n⚙️  [3/3] Updating config.yaml...")
        
        project_name = project_root.name
        app_name, app_id = _derive_app_identity(project_name)
        
        if not dry_run:
            _update_config_yaml(config_path, app_name, app_id, overwrite=False)
        
        # Show what changed
        try:
            updated = yaml.safe_load(config_path.read_text(encoding='utf-8')) if not dry_run else {}
            print(f"   app_name: {updated.get('app_name', app_name)}")
            print(f"   app_id:   {updated.get('app_id', app_id)}")
            print(f"   ✅ config.yaml updated")
        except Exception:
            print(f"   ✅ config.yaml updated (app_name: {app_name}, app_id: {app_id})")
        stats["updated"] += 1
    else:
        print("\n⚙️  [3/3] Skipping config update (--skip-config)")
    
    # =====================================================================
    # Summary
    # =====================================================================
    print(f"\n{'─' * 50}")
    if dry_run:
        print(f"🔍 DRY RUN Summary:")
    else:
        print(f"✅ Upgrade Summary:")
    print(f"   Files added:   {stats['added']}")
    print(f"   Files updated: {stats['updated']}")
    print(f"   Files skipped: {stats['skipped']} (already up to date)")
    
    if dry_run:
        print(f"\n   Run without --dry-run to apply these changes.")
    else:
        print(f"\n🎉 Project upgraded successfully!")


@app.command(name="install-linux")
def install_linux(
    executable: str = typer.Option(None, "--exec", "-e", help="Path to the built executable. If omitted, uses the project's lib/main.py."),
):
    """
    Install .desktop file and hicolor icons to Linux system directories.
    
    Copies the .desktop file to ~/.local/share/applications/ and hicolor
    icons to ~/.local/share/icons/hicolor/ so your app icon shows up in
    the application launcher and taskbar.
    """
    if not sys.platform.startswith('linux'):
        print("⚠️  This command is only relevant on Linux.")
        raise typer.Exit(code=1)
    
    project_root = Path.cwd()
    config_path = project_root / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ Error: No config.yaml found in {project_root}")
        raise typer.Exit(code=1)
    
    # Read app identity from config
    app_name, app_id = _derive_app_identity(project_root.name)
    try:
        cfg = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        if isinstance(cfg, dict):
            if cfg.get('app_name') and cfg['app_name'] != 'My Pythra App':
                app_name = cfg['app_name']
            if cfg.get('app_id') and cfg['app_id'] != 'com.pythra.my-pythra-app':
                app_id = cfg['app_id']
    except Exception:
        pass
    
    linux_dir = project_root / "linux"
    
    # Find the .desktop file
    desktop_file = linux_dir / f"{app_id}.desktop"
    if not desktop_file.exists():
        # Try legacy name
        desktop_file = linux_dir / "appIcon.desktop"
    if not desktop_file.exists():
        print(f"❌ No .desktop file found in {linux_dir}/")
        print(f"   Run `pythra upgrade` first to generate platform files.")
        raise typer.Exit(code=1)
    
    # Resolve the executable path
    if executable:
        exec_path = Path(executable).resolve()
    else:
        # Default: python3 + lib/main.py
        script_path = (project_root / "lib" / "main.py").resolve()
        exec_path = script_path
    
    print(f"\n🐧 Installing Linux desktop integration for: {app_name}")
    print(f"   app_id: {app_id}")
    print(f"   exec:   {exec_path}\n")
    
    # --- 1. Install .desktop file ---
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    # Read and modify the .desktop content to set the actual Exec path
    desktop_content = desktop_file.read_text(encoding='utf-8')
    
    # Replace Exec line with actual executable
    lines = desktop_content.strip().split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('Exec='):
            if str(exec_path).endswith('.py'):
                new_lines.append(f'Exec=python3 {exec_path}')
            else:
                new_lines.append(f'Exec={exec_path}')
        else:
            new_lines.append(line)
    
    installed_desktop = apps_dir / f"{app_id}.desktop"
    installed_desktop.write_text('\n'.join(new_lines) + '\n')
    print(f"  ✅ {installed_desktop}")
    
    # --- 2. Install hicolor icons ---
    hicolor_src = linux_dir / "hicolor"
    if hicolor_src.exists():
        icons_base = Path.home() / ".local" / "share" / "icons" / "hicolor"
        
        for size_dir in hicolor_src.iterdir():
            if not size_dir.is_dir():
                continue
            for apps_subdir in size_dir.iterdir():
                if not apps_subdir.is_dir():
                    continue
                for icon_file in apps_subdir.iterdir():
                    if icon_file.is_file():
                        dest_dir = icons_base / size_dir.name / apps_subdir.name
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        # Rename icon to app_id for FreeDesktop lookup
                        dest_file = dest_dir / f"{app_id}.png"
                        shutil.copy2(icon_file, dest_file)
        
        print(f"  ✅ Icons installed to {icons_base}/*/apps/{app_id}.png")
    else:
        print(f"  ⚠️  No hicolor icons found in {linux_dir}/hicolor/")
    
    # --- 3. Update icon cache ---
    try:
        subprocess.run(
            ["gtk-update-icon-cache", str(Path.home() / ".local" / "share" / "icons" / "hicolor")],
            capture_output=True, timeout=10
        )
        print(f"  ✅ Icon cache updated")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print(f"\n🎉 Linux desktop integration installed!")
    print(f"   Your app should now appear in the application launcher.")




@app.command()
def run(script: str = typer.Option("lib/main.py", "--script", "-s", help="Script to run relative to the project root.")):
    """Runs the application with a clean-restart-on-keypress loop."""
    # This command is perfect as-is.
    project_root = Path.cwd()
    script_path = (project_root / script).resolve()
    if not script_path.exists():
        print(f"❌ Error: Script not found at '{script_path}'")
        raise typer.Exit(code=1)
    process = None
    try:
        while True:
            print(f"\n🚀 Launching: python {script}")
            
            # Inject project_root into PYTHONPATH so local imports work seamlessly
            env = os.environ.copy()
            current_pythonpath = env.get("PYTHONPATH", "")
            if current_pythonpath:
                env["PYTHONPATH"] = f"{project_root}{os.pathsep}{current_pythonpath}"
            else:
                env["PYTHONPATH"] = str(project_root)
                
            process = subprocess.Popen([sys.executable, "-u", str(script_path)], env=env)
            cmd = input("🔥 Clean Restart active. Press [r] + Enter to restart, [q] + Enter to quit: ").strip().lower()
            if cmd and readline:
                try:
                    readline.add_history(cmd)
                except Exception:
                    pass
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=2)
                except subprocess.TimeoutExpired: process.kill()
            if cmd == 'q':
                print("👋 Exiting...")
                break
            elif cmd != 'r':
                print("❓ Unknown command. Exiting.")
                break
            print("🔄 Restarting application...")
            time.sleep(0.5)
    finally:
        if process and process.poll() is None:
            process.kill()


@app.command()
def doctor():
    """Check PyThra installation and dependencies"""
    try:
        import sys
        from pathlib import Path
        
        print("🔍 PyThra Installation Check")
        print("=" * 40)
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 8):
            print(f"✅ Python {python_version} (supported)")
        else:
            print(f"❌ Python {python_version} (requires 3.8+)")
        
        # Check required dependencies
        required_packages = [
            ('PySide6', 'PySide6'),
            ('typer', 'typer'),
            ('PyYAML', 'yaml'),
        ]
        
        optional_packages = [
            ('rich', 'rich'),
            ('semver', 'semver'),
            ('requests', 'requests'),
        ]
        
        print(f"\n📦 Required Dependencies:")
        for display_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"✅ {display_name}")
            except ImportError:
                print(f"❌ {display_name} (missing)")
        
        print(f"\n📦 Optional Dependencies:")
        for display_name, import_name in optional_packages:
            try:
                __import__(import_name)
                print(f"✅ {display_name}")
            except ImportError:
                print(f"⚠️ {display_name} (recommended)")
        
        # Check package management system
        print(f"\n📦 Package Management:")
        if PACKAGE_COMMANDS_AVAILABLE:
            print(f"✅ Package management commands available")
            print(f"   Try: pythra package list")
        else:
            print(f"⚠️ Package management commands not available")
            print(f"   Install with: pip install semver requests rich")
        
        # Check project structure if in a project
        if Path('config.yaml').exists():
            print(f"\n📁 Project Structure:")
            expected_dirs = ['lib', 'assets', 'plugins']
            for dir_name in expected_dirs:
                if Path(dir_name).exists():
                    print(f"✅ {dir_name}/")
                else:
                    print(f"⚠️ {dir_name}/ (recommended)")
            
            if Path('lib/main.py').exists():
                print(f"✅ lib/main.py")
            else:
                print(f"❌ lib/main.py (missing)")
        else:
            print(f"\n📁 No PyThra project detected in current directory")
        
        print(f"\n🎯 Installation Summary:")
        print(f"PyThra framework appears to be properly installed!")
        
    except Exception as e:
        print(f"Error checking installation: {e}")


@app.command()
def build(
    script: str = typer.Option("lib/main.py", "--script", "-s", help="Script to compile, relative to project root."),
    include_dir: Optional[List[str]] = typer.Option(None, "--include-dir", "-d", help="Directory to include (e.g., assets). Can be repeated."),
    include_file: Optional[List[str]] = typer.Option(None, "--include-file", "-f", help="File to include."),
    output_root: str = typer.Option("build", help="Top-level build folder."),
    icon: str = typer.Option(None, "--icon", "-i", help="Path to an icon file (.ico for Windows, .icns for macOS). Auto-detected from windows/ or macos/ dirs if omitted."),
    onefile: bool = typer.Option(False, "--onefile", help="Create a single-file executable instead of a folder."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print actions but don't execute Nuitka."),
    keep_embedded: bool = typer.Option(False, "--keep-embedded", help="Do not delete the generated _embedded_config.py after build.")
):
    """Builds a standalone executable using Nuitka, embedding a release-mode config."""
    project_root = Path.cwd()
    config_path = project_root / "config.yaml"

    if not config_path.exists():
        print(f"❌ Error: `config.yaml` not found in project root: {project_root}")
        raise typer.Exit(code=1)

    print("--- Starting Pythra Build Process ---")
    
    # Set default include directories, and add optional dirs if they exist.
    default_includes = ["assets", "render"]
    for optional_dir in ["plugins", "windows", "macos", "linux"]:
        if (project_root / optional_dir).is_dir():
            default_includes.append(optional_dir)
    include_dir = include_dir or default_includes
    include_file = include_file or []

    original_config = load_yaml(config_path)
    build_config = yaml.safe_load(yaml.safe_dump(original_config))
    set_debug_false_in_obj(build_config)

    app_name = str(build_config.get("app_name", "PythraApp")).strip()
    version = str(build_config.get("version", "1.0.0"))

    # The final output directory is the main target.
    final_build_dir = (project_root / output_root / app_name).resolve()
    if final_build_dir.exists():
        print(f"[+] Removing existing build folder: {final_build_dir}")
        force_rmtree(final_build_dir)
    final_build_dir.mkdir(parents=True, exist_ok=True)
    print(f"[+] Created clean build folder: {final_build_dir}")

    script_src = (project_root / script).resolve()
    if not script_src.exists():
        raise FileNotFoundError(f"Script to compile not found: {script_src}")

    embedded_module_path = generate_embedded_config_module_in_dir(dest_dir=final_build_dir, data=build_config)

    try:
        import pythra
        pythra_package_path = Path(pythra.__file__).parent
    except ImportError:
        print("❌ Fatal Error: Could not find 'pythra' package. Is it installed with 'pip install -e .'?")
        raise typer.Exit(code=1)

    # Nuitka data arguments (source=destination)
    dir_args = [f"--include-data-dir={project_root/d}={d}" for d in include_dir if (project_root/d).exists()]
    file_args = [f"--include-data-file={project_root/f}={f}" for f in include_file if (project_root/f).exists()]
    
    nuitka_cmd = [
        sys.executable, "-m", "nuitka", str(script_src),
        "--standalone",
        f"--output-filename={app_name}",
        "--enable-plugin=pyside6",
        f"--output-dir={str(final_build_dir)}",
        f"--file-version={version}",
        "--windows-console-mode=disable",
        f"--include-package=pythra",
        "--nofollow-import-to=pythra.tests",
        "--include-module=_embedded_config",
        *dir_args,
        *file_args,
    ]

    if onefile:
        nuitka_cmd.append("--onefile")

    try:
        system = platform.system().lower()
    except Exception:
        system = ''

    # --- Platform-aware icon handling ---
    # Auto-detect platform icon if --icon is not specified
    if not icon:
        if 'windows' in system:
            auto_icon = project_root / 'windows' / 'appIcon.ico'
            if auto_icon.exists():
                icon = str(auto_icon)
        elif 'darwin' in system:
            auto_icon = project_root / 'macos' / 'appIcon.icns'
            if auto_icon.exists():
                icon = str(auto_icon)

    if icon:
        icon_path = (project_root / icon).resolve() if not Path(icon).is_absolute() else Path(icon).resolve()
        if icon_path.exists():
            if 'darwin' in system and icon_path.suffix == '.icns':
                # macOS: create an .app bundle with the icon
                nuitka_cmd.extend([
                    '--macos-create-app-bundle',
                    f'--macos-app-icon={str(icon_path)}'
                ])
                print(f"[+] macOS: Using app bundle icon: {icon_path}")
            else:
                # Windows (and fallback): use --windows-icon-from-ico
                nuitka_cmd.append(f"--windows-icon-from-ico={str(icon_path)}")
                print(f"[+] Windows: Using icon: {icon_path}")
        else:
            print(f"⚠️ Warning: Icon file not found at '{icon_path}'. Skipping icon.")

    print("\n" + "="*72)
    print(f"App: {app_name} v{version}")
    print(f"Build will be located in: {final_build_dir}")
    print(f"PyThra package location: {pythra_package_path}")
    print("Nuitka command to be executed:")
    print(" ".join(nuitka_cmd))
    print("="*72 + "\n")

    if dry_run:
        print("DRY RUN: Skipping Nuitka execution.")
        if not keep_embedded:
            embedded_module_path.unlink(missing_ok=True)
        return

    # PYTHONPATH needs to include:
    # 1. The folder with the generated _embedded_config module
    # 2. The parent directory of the pythra package (for editable installs)
    env = os.environ.copy()
    pythra_parent = str(pythra_package_path.parent)
    pythonpath_parts = [
        str(final_build_dir),
        pythra_parent,
        env.get("PYTHONPATH", "")
    ]
    env["PYTHONPATH"] = os.pathsep.join(p for p in pythonpath_parts if p)

    # Compiler environment tweaks:
    # - For MSVC we set CL=/Zm300 to increase preprocessor memory and avoid
    #   "fatal error C1060: compiler is out of heap space" when building large apps.
    # - For non-Windows platforms there is no direct CL equivalent; set a
    #   conservative CFLAGS fallback so build tools have some optimization flags.
       
    

    if 'windows' in system:
        # Only override CL if not already set (allow users to predefine it)
        if not env.get('CL'):
            env['CL'] = '/Zm300'
        print(f"[+] Set environment: CL={env.get('CL')}")
    else:
        # Best-effort fallback for non-MSVC toolchains. This is not an exact
        # equivalent to /Zm300 but helps ensure the compiler has reasonable flags.
        existing_cflags = env.get('CFLAGS', '').strip()
        fallback_flags = '-O2'
        env['CFLAGS'] = (existing_cflags + ' ' + fallback_flags).strip() if existing_cflags else fallback_flags
        print(f"[+] Non-Windows detected ({system}); set CFLAGS='{env['CFLAGS']}' as a fallback for the build.")

    try:
        subprocess.run(nuitka_cmd, check=True, env=env)
        print("\n✅ Build completed successfully!")
        print(f"   Application folder located at: {final_build_dir}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ Nuitka build failed. Please check the output above for errors.")
        print("   Make sure Nuitka and a C/C++ compiler are installed and configured correctly.")
        raise typer.Exit(code=1)
    finally:
        if not keep_embedded:
            embedded_module_path.unlink(missing_ok=True)
            print(f"[+] Removed temporary embedded module.")

# Always initialize history when the CLI module is loaded
_init_cli_history()

if __name__ == "__main__":
    app()