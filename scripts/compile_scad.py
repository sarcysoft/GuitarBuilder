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
    common_scad_dir = os.path.join(scad_dir, "common")
    
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
    
    # Setup OPENSCADPATH environment variable for modular includes
    env = os.environ.copy()
    include_paths = [scad_dir]
    if os.path.exists(common_scad_dir):
        include_paths.insert(0, common_scad_dir)
    env["OPENSCADPATH"] = os.pathsep.join(include_paths)
    
    success_count = 0
    fail_count = 0
    
    def run_openscad(cmd, desc):
        nonlocal success_count, fail_count
        try:
            res = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print(f"  [OK] {desc}")
                success_count += 1
                return True
            else:
                print(f"  [FAIL] {desc}:")
                if res.stderr:
                    print(res.stderr.strip())
                fail_count += 1
                return False
        except Exception as e:
            print(f"  [EXCEPTION] {desc}: {e}")
            fail_count += 1
            return False

    # 1. Compile Hardware Variants (Option A: models/scad/hardware/<variant>/)
    hw_base_dir = os.path.join(scad_dir, "hardware")
    if os.path.exists(hw_base_dir):
        hw_variants = [d for d in sorted(os.listdir(hw_base_dir)) if os.path.isdir(os.path.join(hw_base_dir, d))]
        print(f"Found {len(hw_variants)} hardware variants: {', '.join(hw_variants)}")
        
        for variant in hw_variants:
            v_dir = os.path.join(hw_base_dir, variant)
            print(f"Compiling Hardware Variant [{variant}]...")
            
            # 1. Hardware cavity cutouts (pickup cavities, bridge rout, jack rout)
            hw_cut_scad = os.path.join(v_dir, "hardware_cutout.scad")
            legacy_hw_scad = os.path.join(v_dir, "hardware.scad")
            has_explicit_cutout = os.path.exists(hw_cut_scad)

            if has_explicit_cutout:
                out_cut_stl = os.path.join(stl_dir, f"hardware_cutout_{variant}.stl")
                run_openscad(openscad_exe + ["-o", out_cut_stl, hw_cut_scad], f"hardware_cutout_{variant}.stl")
                if variant == "standard":
                    import shutil
                    shutil.copyfile(out_cut_stl, os.path.join(stl_dir, "hardware_cutout.stl"))
            elif os.path.exists(legacy_hw_scad):
                # Fallback: legacy hardware.scad used as cutout
                out_cut_stl = os.path.join(stl_dir, f"hardware_cutout_{variant}.stl")
                run_openscad(openscad_exe + ["-o", out_cut_stl, legacy_hw_scad], f"hardware_cutout_{variant}.stl")
                if variant == "standard":
                    import shutil
                    shutil.copyfile(out_cut_stl, os.path.join(stl_dir, "hardware_cutout.stl"))

            # 2. Physical hardware model for rendering (Bridge, Pickups, Jack plate, etc.)
            hw_phys_scad = os.path.join(v_dir, "hardware_physical.scad")
            if not os.path.exists(hw_phys_scad) and has_explicit_cutout and os.path.exists(legacy_hw_scad):
                hw_phys_scad = legacy_hw_scad

            if os.path.exists(hw_phys_scad):
                out_phys_stl = os.path.join(stl_dir, f"hardware_physical_{variant}.stl")
                run_openscad(openscad_exe + ["-o", out_phys_stl, hw_phys_scad], f"hardware_physical_{variant}.stl")
                import shutil
                shutil.copyfile(out_phys_stl, os.path.join(stl_dir, f"hardware_{variant}.stl"))
                if variant == "standard":
                    shutil.copyfile(out_phys_stl, os.path.join(stl_dir, "hardware.stl"))
                
            # Check for backplate files - omitting backplate.scad skips backplate completely
            backplate_scad = os.path.join(v_dir, "backplate.scad")
            if os.path.exists(backplate_scad):
                # Backplate physical cover
                out_bp = os.path.join(stl_dir, f"backplate_{variant}.stl")
                run_openscad(openscad_exe + ["-o", out_bp, backplate_scad], f"backplate_{variant}.stl")
                if variant == "standard":
                    shutil.copyfile(out_bp, os.path.join(stl_dir, "backplate.stl"))
                
                # Backplate mask (recess cut)
                mask_scad = os.path.join(v_dir, "backplate_mask.scad")
                if os.path.exists(mask_scad):
                    out_mask = os.path.join(stl_dir, f"backplate_mask_{variant}.stl")
                    run_openscad(openscad_exe + ["-o", out_mask, mask_scad], f"backplate_mask_{variant}.stl")
                    if variant == "standard":
                        shutil.copyfile(out_mask, os.path.join(stl_dir, "backplate_mask.stl"))
                        
                # Backplate fixings (screw holes)
                fix_scad = os.path.join(v_dir, "backplate_fixings.scad")
                if os.path.exists(fix_scad):
                    out_fix = os.path.join(stl_dir, f"backplate_fixings_{variant}.stl")
                    run_openscad(openscad_exe + ["-o", out_fix, fix_scad], f"backplate_fixings_{variant}.stl")
                    if variant == "standard":
                        shutil.copyfile(out_fix, os.path.join(stl_dir, "backplate_fixings.stl"))
            else:
                print(f"  [Hardware: {variant}] No backplate.scad found. Skipping backplate compilation.")

    # 2. Compile Electronics Variants (Option A: models/scad/electronics/<variant>/)
    elec_base_dir = os.path.join(scad_dir, "electronics")
    if os.path.exists(elec_base_dir):
        elec_variants = [d for d in sorted(os.listdir(elec_base_dir)) if os.path.isdir(os.path.join(elec_base_dir, d))]
        print(f"Found {len(elec_variants)} electronics variants: {', '.join(elec_variants)}")
        
        for variant in elec_variants:
            v_dir = os.path.join(elec_base_dir, variant)
            print(f"Compiling Electronics Variant [{variant}]...")
            
            # Main electronics cavity cut
            elec_scad = os.path.join(v_dir, "electronics.scad")
            if os.path.exists(elec_scad):
                out_stl = os.path.join(stl_dir, f"electronics_{variant}.stl")
                cmd = openscad_exe + ["-o", out_stl, "-D", f'layout_type="{variant}"', elec_scad]
                run_openscad(cmd, f"electronics_{variant}.stl")
                if variant == "sarcaster":
                    import shutil
                    shutil.copyfile(out_stl, os.path.join(stl_dir, "electronics.stl"))
            else:
                print(f"  Warning: No electronics.scad found in {v_dir}")
                
            # Check for electronics backplate files
            bp_scad = os.path.join(v_dir, "elec_backplate.scad")
            if os.path.exists(bp_scad):
                out_bp = os.path.join(stl_dir, f"elec_backplate_{variant}.stl")
                cmd = openscad_exe + ["-o", out_bp, "-D", f'layout_type="{variant}"', bp_scad]
                run_openscad(cmd, f"elec_backplate_{variant}.stl")
                if variant == "sarcaster":
                    shutil.copyfile(out_bp, os.path.join(stl_dir, "elec_backplate.stl"))
                    
                mask_scad = os.path.join(v_dir, "elec_backplate_mask.scad")
                if os.path.exists(mask_scad):
                    out_mask = os.path.join(stl_dir, f"elec_backplate_mask_{variant}.stl")
                    cmd = openscad_exe + ["-o", out_mask, "-D", f'layout_type="{variant}"', mask_scad]
                    run_openscad(cmd, f"elec_backplate_mask_{variant}.stl")
                    if variant == "sarcaster":
                        shutil.copyfile(out_mask, os.path.join(stl_dir, "elec_backplate_mask.stl"))
                        
                fix_scad = os.path.join(v_dir, "elec_backplate_fixings.scad")
                if os.path.exists(fix_scad):
                    out_fix = os.path.join(stl_dir, f"elec_backplate_fixings_{variant}.stl")
                    cmd = openscad_exe + ["-o", out_fix, "-D", f'layout_type="{variant}"', fix_scad]
                    run_openscad(cmd, f"elec_backplate_fixings_{variant}.stl")
                    if variant == "sarcaster":
                        shutil.copyfile(out_fix, os.path.join(stl_dir, "elec_backplate_fixings.stl"))
            else:
                print(f"  [Electronics: {variant}] No elec_backplate.scad found. Skipping electronics backplate.")

    # 3. Compile Neck Variants (models/scad/neck/<variant>/)
    neck_base_dir = os.path.join(scad_dir, "neck")
    if os.path.exists(neck_base_dir):
        neck_variants = [d for d in sorted(os.listdir(neck_base_dir)) if os.path.isdir(os.path.join(neck_base_dir, d))]
        print(f"Found {len(neck_variants)} neck variants: {', '.join(neck_variants)}")
        
        components = [
            ("all", ""),
            ("shaft", "shaft_"),
            ("fretboard", "fretboard_"),
            ("frets", "frets_"),
            ("nut", "nut_"),
            ("tuners", "tuners_"),
        ]
        
        for variant in neck_variants:
            v_dir = os.path.join(neck_base_dir, variant)
            neck_scad = os.path.join(v_dir, "neck.scad")
            if not os.path.exists(neck_scad):
                continue
                
            print(f"Compiling Neck Variant [{variant}] components...")
            for part_name, prefix in components:
                if part_name == "all":
                    out_name = f"neck_{variant}.stl"
                elif part_name == "shaft":
                    out_name = f"neck_shaft_{variant}.stl"
                else:
                    out_name = f"{part_name}_{variant}.stl"
                
                out_stl = os.path.join(stl_dir, out_name)
                cmd = openscad_exe + ["-o", out_stl, "-D", f'part="{part_name}"', neck_scad]
                run_openscad(cmd, out_name)
                
                # Default fallback aliases for strat
                if variant == "strat":
                    import shutil
                    if part_name == "all":
                        shutil.copyfile(out_stl, os.path.join(stl_dir, "neck.stl"))
                    elif part_name == "shaft":
                        shutil.copyfile(out_stl, os.path.join(stl_dir, "neck_shaft.stl"))
                    else:
                        shutil.copyfile(out_stl, os.path.join(stl_dir, f"{part_name}.stl"))
            
    print("-" * 50)
    print(f"Compilation finished. Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
