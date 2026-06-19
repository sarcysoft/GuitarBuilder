import os
import sys
import subprocess


def find_openscad():
    """Locate the OpenSCAD executable or command on the system."""
    # 1. Check for custom environment variable path
    env_path = os.environ.get("OPENSCAD_PATH")
    if env_path:
        # If it's a file path, return as a list
        if os.path.exists(env_path):
            return [env_path]
        # Or maybe it's a command like "flatpak run org.openscad.OpenSCAD"
        import shlex
        return shlex.split(env_path)

    # 2. Check if flatpak version is available
    try:
        result = subprocess.run(["flatpak", "run", "org.openscad.OpenSCAD", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        if result.returncode == 0:
            return ["flatpak", "run", "org.openscad.OpenSCAD"]
    except Exception:
        pass

    # 3. Check if 'openscad' is in the system PATH
    import shutil
    openscad_path = shutil.which("openscad")
    if openscad_path:
        return [openscad_path]

    # Check for 'where openscad' or 'which openscad' as fallbacks
    try:
        cmd = ["where", "openscad"] if sys.platform == "win32" else ["which", "openscad"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            path = result.stdout.strip().split('\n')[0]
            if path:
                return [path]
    except Exception:
        pass

    # 4. Check common Windows installation paths
    program_files = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
    ]
    for pf in program_files:
        path = os.path.join(pf, "OpenSCAD", "openscad.exe")
        if os.path.exists(path):
            return [path]

    # 5. Check C:\OpenSCAD directly
    direct_path = "C:\\OpenSCAD\\openscad.exe"
    if os.path.exists(direct_path):
        return [direct_path]

    return None


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) == "scripts":
        root_dir = os.path.dirname(script_dir)
    else:
        root_dir = script_dir
    models_dir = os.path.join(root_dir, "models")
    
    if not os.path.exists(models_dir):
        print(f"Error: models directory '{models_dir}' not found.")
        sys.exit(1)
        
    openscad_exe = find_openscad()
    if not openscad_exe:
        print("Error: Could not locate the OpenSCAD executable (openscad.exe).")
        print("Please ensure OpenSCAD is installed and added to your PATH, or set the OPENSCAD_PATH environment variable.")
        sys.exit(1)
        
    print(f"Using OpenSCAD: {' '.join(openscad_exe)}")
    
    scad_files = [f for f in os.listdir(models_dir) if f.lower().endswith(".scad")]
    
    success_count = 0
    fail_count = 0
    skipped_files = []
    
    for f in scad_files:
        # Skip utility scripts starting with '_'
        if f.startswith("_"):
            skipped_files.append(f)
            continue
            
        scad_path = os.path.join(models_dir, f)
        stl_name = f[:-5] + ".stl"
        stl_path = os.path.join(models_dir, stl_name)
        
        print(f"Compiling: {f} -> {stl_name}...")
        
        cmd = openscad_exe + ["-o", stl_path, scad_path]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"  Successfully compiled: {stl_name}")
                success_count += 1
            else:
                print(f"  Error compiling {f}:")
                print(result.stderr)
                fail_count += 1
        except Exception as e:
            print(f"  Exception occurred compiling {f}: {e}")
            fail_count += 1
            
    print("-" * 50)
    print(f"Compilation finished. Success: {success_count}, Failed: {fail_count}")
    if skipped_files:
        print(f"Skipped utility files: {', '.join(skipped_files)}")


if __name__ == "__main__":
    main()
