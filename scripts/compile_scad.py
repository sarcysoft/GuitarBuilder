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
    scad_dir = os.path.join(root_dir, "models", "scad")
    stl_dir = os.path.join(root_dir, "models", "stl")
    
    if not os.path.exists(scad_dir):
        print(f"Error: OpenSCAD directory '{scad_dir}' not found.")
        sys.exit(1)
        
    if not os.path.exists(stl_dir):
        os.makedirs(stl_dir)
        
    openscad_exe = find_openscad()
    if not openscad_exe:
        print("Error: Could not locate the OpenSCAD executable (openscad.exe).")
        print("Please ensure OpenSCAD is installed and added to your PATH, or set the OPENSCAD_PATH environment variable.")
        sys.exit(1)
        
    print(f"Using OpenSCAD: {' '.join(openscad_exe)}")
    
    scad_files = [f for f in os.listdir(scad_dir) if f.lower().endswith(".scad")]
    
    success_count = 0
    fail_count = 0
    skipped_files = []
    
    for f in scad_files:
        # Skip utility scripts starting with '_'
        if f.startswith("_"):
            skipped_files.append(f)
            continue
            
        base_name = f[:-5]
        scad_path = os.path.join(scad_dir, f)
        
        is_electronics = base_name in ["electronics", "elec_backplate", "elec_backplate_mask", "elec_backplate_fixings"]
        
        if is_electronics:
            layouts = ["sarcaster", "flying_v", "les_paul"]
            for layout in layouts:
                stl_name = f"{base_name}_{layout}.stl"
                stl_path = os.path.join(stl_dir, stl_name)
                print(f"Compiling variant [{layout}]: {f} -> {stl_name}...")
                
                cmd = openscad_exe + ["-o", stl_path, "-D", f'layout_type="{layout}"', scad_path]
                try:
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        print(f"  Successfully compiled: {stl_name}")
                        success_count += 1
                    else:
                        print(f"  Error compiling variant {layout} of {f}:")
                        print(result.stderr)
                        fail_count += 1
                except Exception as e:
                    print(f"  Exception occurred compiling variant {layout} of {f}: {e}")
                    fail_count += 1
            
            # Also compile default fallback version without suffix
            stl_name = base_name + ".stl"
            stl_path = os.path.join(stl_dir, stl_name)
            print(f"Compiling default: {f} -> {stl_name}...")
            cmd = openscad_exe + ["-o", stl_path, scad_path]
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print(f"  Successfully compiled: {stl_name}")
                    success_count += 1
                else:
                    print(f"  Error compiling default {f}:")
                    print(result.stderr)
                    fail_count += 1
            except Exception as e:
                print(f"  Exception occurred compiling default {f}: {e}")
                fail_count += 1
        else:
            # Standard single compilation
            stl_name = base_name + ".stl"
            stl_path = os.path.join(stl_dir, stl_name)
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
