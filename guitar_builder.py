import os
import sys
import subprocess
import json
import argparse

# Detect if we are running inside Blender's python interpreter
try:
    import bpy
    inside_blender = True
except ImportError:
    inside_blender = False


def find_blender():
    """Locate the Blender executable on Windows, macOS, and Linux."""
    # 1. Check if an environment variable BLENDER_PATH is set
    env_path = os.environ.get("BLENDER_PATH")
    if env_path:
        if os.path.exists(env_path) and os.path.isfile(env_path):
            return env_path
        else:
            print(f"Error: BLENDER_PATH environment variable is set to '{env_path}', but the file does not exist.")
            sys.exit(1)

    # 2. Check if 'blender' is in the system PATH
    try:
        cmd = ["where", "blender"] if os.name == "nt" else ["which", "blender"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # Strip trailing newline if any
            path = result.stdout.strip().split('\n')[0].strip()
            if os.path.exists(path) and os.path.isfile(path):
                return path
    except Exception:
        pass
    
    # 3. Check platform-specific standard installation directories
    if os.name == "nt":
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        bf = os.path.join(pf, "Blender Foundation")
        if os.path.exists(bf):
            subdirs = [os.path.join(bf, d) for d in os.listdir(bf) if d.startswith("Blender")]
            subdirs.sort(reverse=True)
            for sd in subdirs:
                exe = os.path.join(sd, "blender.exe")
                if os.path.exists(exe):
                    return exe
    elif sys.platform == "darwin":
        mac_path = "/Applications/Blender.app/Contents/MacOS/blender"
        if os.path.exists(mac_path):
            return mac_path
    else:
        linux_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender"
        ]
        for path in linux_paths:
            if os.path.exists(path):
                return path
                
    # If not found, print a helpful, descriptive error message and exit.
    print("=" * 80)
    print("Error: Blender executable (blender.exe / blender) could not be located.")
    print("The script requires a standard command-line executable of Blender to run.")
    print("=" * 80)
    print("How to fix this:")
    print("1. Set the BLENDER_PATH environment variable to point to your blender.exe / blender path.")
    print("   Example (PowerShell):")
    print("     $env:BLENDER_PATH=\"C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe\"")
    print("   Example (CMD):")
    print("     set BLENDER_PATH=C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe")
    print("   Example (Linux/macOS):")
    print("     export BLENDER_PATH=/usr/bin/blender")
    print()
    print("2. Or add the directory containing the Blender executable to your system's PATH.")
    print()
    # Check if they have the Microsoft Store version's alias in PATH
    try:
        store_check = subprocess.run(["where", "blender-launcher"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if store_check.returncode == 0:
            print("Note: It appears you have the Microsoft Store version of Blender installed.")
            print("      Due to sandboxing restrictions, Microsoft Store applications cannot easily be run")
            print("      in background/headless mode via automation scripts.")
            print("      We highly recommend downloading and installing the standard release version")
            print("      (or the portable .zip version) of Blender from: https://www.blender.org/download/")
            print("      Once installed/extracted, configure the BLENDER_PATH environment variable as shown above.")
            print("=" * 80)
            sys.exit(1)
    except Exception:
        pass
        
    print("We recommend installing a standard release version of Blender from https://www.blender.org/")
    print("=" * 80)
    sys.exit(1)


def get_modifier_inputs(geom_modifier):
    """Retrieve the mapping of friendly display names to socket identifiers in the Geometry Nodes modifier."""
    node_group = geom_modifier.node_group
    mapping = {}
    
    # In Blender 4.0+, the inputs/outputs collection is in interface.items_tree
    if hasattr(node_group, 'interface') and hasattr(node_group.interface, 'items_tree'):
        for item in node_group.interface.items_tree:
            # Check if it's an input socket with a valid identifier
            if getattr(item, 'in_out', None) == 'INPUT' and hasattr(item, 'identifier'):
                mapping[item.name] = {
                    'identifier': item.identifier,
                    'type': getattr(item, 'socket_type', 'none')
                }
    return mapping


def resolve_config_path(filepath, script_dir):
    """Ensure the config file is placed in or read from the 'config' directory by default if a relative name is given, and create parent folders if missing."""
    if not os.path.isabs(filepath):
        norm_path = os.path.normpath(filepath)
        parts = norm_path.split(os.sep)
        if parts[0] != 'config':
            filepath = os.path.join('config', filepath)
        filepath = os.path.join(script_dir, filepath)
        
    parent_dir = os.path.dirname(filepath)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        
    return filepath


def export_config(geom_modifier, filepath):
    """Read Geometry Nodes modifier values and write them to a JSON configuration file."""
    mapping = get_modifier_inputs(geom_modifier)
    config = {}
    
    for name, info in mapping.items():
        ident = info['identifier']
        val = geom_modifier.get(ident)
        
        # Handle vector/color array types to make them JSON serializable
        if hasattr(val, "to_list"):
            val = val.to_list()
        elif hasattr(val, "to_tuple"):
            val = val.to_tuple()
            
        config[name] = val
        
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Successfully exported configuration to: {filepath}")


def import_config(geom_modifier, filepath):
    """Read a JSON configuration file and apply the values to the Geometry Nodes modifier."""
    if not os.path.exists(filepath):
        print(f"Error: Configuration file '{filepath}' not found.")
        sys.exit(1)
        
    with open(filepath, 'r') as f:
        config = json.load(f)
        
    mapping = get_modifier_inputs(geom_modifier)
    updated_count = 0
    
    for name, val in config.items():
        if name in mapping:
            ident = mapping[name]['identifier']
            geom_modifier[ident] = val
            print(f"  Applied: '{name}' -> {val}")
            updated_count += 1
        else:
            print(f"  Warning: Parameter '{name}' in JSON is not a valid parameter in Geometry Nodes.")
            
    print(f"Successfully updated {updated_count} parameters.")


def generate_obj(guitar_body, script_dir, filename="guitar.obj"):
    """Deselect all objects, select the Guitar Body, and export it as an OBJ mesh."""
    # Ensure we are in Object Mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # Deselect all first
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select Guitar Body and make it active
    guitar_body.select_set(True)
    bpy.context.view_layer.objects.active = guitar_body
    
    # Ensure the models output folder exists
    models_dir = os.path.join(script_dir, "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        
    obj_path = os.path.join(models_dir, filename)
    print(f"Exporting Guitar Body mesh to: {obj_path}")
    
    # Export with modifiers applied
    try:
        if hasattr(bpy.ops.wm, 'obj_export'):
            bpy.ops.wm.obj_export(
                filepath=obj_path,
                export_selected_objects=True,
                export_materials=True
            )
        else:
            bpy.ops.export_scene.obj(
                filepath=obj_path,
                use_selection=True,
                use_materials=True
            )
        print("Export completed successfully.")
    except Exception as e:
        print(f"Error exporting OBJ: {e}")
        sys.exit(1)


def parse_wrapper_args(argv):
    """Custom command-line argument parser for wrapper shell execution mode."""
    # Pre-parse pass to find --cli-config
    cli_config_path = None
    i = 0
    while i < len(argv):
        if argv[i] == "--cli-config" and i + 1 < len(argv):
            cli_config_path = argv[i + 1]
            break
        i += 1

    # Default variables
    no_cut = False
    config = None
    export_config = None
    export_config_flag = False
    import_config = None
    generate = False
    
    # Render arguments
    render = False
    body_only = False
    exploded_body = False
    uncut = False
    save_blend = False
    angle = "all"
    engine = "eevee"
    material = "gloss"
    material_back = "gloss:black"
    lighting = "studio"
    pitch = None
    guitar_rot = None
    animate = False
    no_render_anim = False
    preview = False
    dynamic_zoom = False
    seed = None

    # Load settings from cli-config if provided
    if cli_config_path and os.path.exists(cli_config_path):
        try:
            with open(cli_config_path, "r") as f:
                config_data = json.load(f)
            
            # Map key-values to variables
            no_cut = config_data.get("no_cut", no_cut)
            config = config_data.get("config", config)
            render = config_data.get("render", render)
            body_only = config_data.get("body_only", body_only)
            exploded_body = config_data.get("exploded_body", exploded_body)
            uncut = config_data.get("uncut", uncut)
            save_blend = config_data.get("save_blend", save_blend)
            angle = config_data.get("angle", angle)
            engine = config_data.get("engine", engine)
            material = config_data.get("material", material)
            material_back = config_data.get("material_back", material_back)
            lighting = config_data.get("lighting", lighting)
            pitch = config_data.get("pitch", pitch)
            guitar_rot = config_data.get("guitar_rot", guitar_rot)
            animate = config_data.get("animate", animate)
            no_render_anim = config_data.get("no_render_anim", no_render_anim)
            preview = config_data.get("preview", preview)
            dynamic_zoom = config_data.get("dynamic_zoom", dynamic_zoom)
            
            # Read seed if present and not commented out
            if "seed" in config_data:
                seed = config_data["seed"]
        except Exception as e:
            print(f"Warning: Failed to load CLI config from '{cli_config_path}': {e}")
            
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ["--no-cut", "--no_cut", "no_cut"]:
            no_cut = True
            i += 1
        elif arg == "--render":
            render = True
            i += 1
        elif arg in ["--body-only", "--body_only", "body_only"]:
            body_only = True
            i += 1
        elif arg in ["--exploded-body", "--exploded_body", "exploded_body", "--explode-body", "--explode_body", "explode_body"]:
            exploded_body = True
            i += 1
        elif arg == "--uncut":
            uncut = True
            i += 1
        elif arg == "--angle":
            if i + 1 < len(argv):
                angle = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--engine":
            if i + 1 < len(argv):
                engine = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--material":
            if i + 1 < len(argv):
                material = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ["--material-back", "--material_back"]:
            if i + 1 < len(argv):
                material_back = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--lighting":
            if i + 1 < len(argv):
                lighting = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--pitch":
            if i + 1 < len(argv):
                pitch = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ["--guitar-rot", "--guitar_rot"]:
            if i + 1 < len(argv):
                guitar_rot = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--animate":
            animate = True
            i += 1
        elif arg in ["--no-render-anim", "--no_render_anim"]:
            no_render_anim = True
            i += 1
        elif arg in ["--preview", "-p"]:
            preview = True
            i += 1
        elif arg in ["--dynamic-zoom", "--dynamic_zoom"]:
            dynamic_zoom = True
            i += 1
        elif arg in ["--save-blend", "--save_blend"]:
            save_blend = True
            i += 1
        elif arg == "--seed":
            if i + 1 < len(argv):
                try:
                    seed = int(argv[i + 1])
                except ValueError:
                    seed = None
                i += 2
            else:
                i += 1
        elif arg == "--cli-config":
            # Already handled in pre-parse, just skip
            i += 2
        elif arg in ["--export-config", "--export_config"]:
            export_config_flag = True
            if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                export_config = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ["--import-config", "--import_config"]:
            if i + 1 < len(argv):
                import_config = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--config":
            if i + 1 < len(argv):
                config = argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--generate":
            generate = True
            i += 1
        elif arg.startswith("-"):
            # Skip/ignore other unsupported flags
            i += 1
        else:
            # Positional argument: set config if not already set
            if not config:
                config = arg
            i += 1
            
    return no_cut, config, export_config_flag, export_config, import_config, generate, render, body_only, exploded_body, uncut, angle, engine, material, material_back, lighting, save_blend, pitch, guitar_rot, animate, no_render_anim, preview, dynamic_zoom, seed


def run_wrapper_mode():
    # =========================================================================
    # WRAPPER MODE (System Shell)
    # =========================================================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_exe = find_blender()
    
    guitar_blend = os.path.join(script_dir, "scripts", "guitar.blend")
    if not os.path.exists(guitar_blend):
        print(f"Error: {guitar_blend} not found in the workspace.")
        sys.exit(1)
        
    # Parse command line args
    (no_cut, config, export_config_flag, wrapper_export_config, wrapper_import_config, generate,
     render, body_only, exploded_body, uncut, angle, engine, material, material_back, lighting, save_blend, pitch, guitar_rot, animate, no_render_anim, preview, dynamic_zoom, seed) = parse_wrapper_args(sys.argv[1:])
    
    # Case 0: Rendering Mode (Runs background render script on previously generated STL/OBJ files)
    if render or animate or no_render_anim:
        print("Launching background rendering pipeline...")
        if config and config != "default":
            config_dir = os.path.join(script_dir, "output", config)
        else:
            config_dir = os.path.join(script_dir, "output")
            
        # Seed generation for random material strings if not provided
        if "random" in material.lower() and material.lower().strip() != "random":
            if seed is None:
                import random
                seed = random.randint(1, 1000000)
                print(f"Generated random seed for materials: {seed}")
                
        # Always save last_config.json
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        last_config_path = os.path.join(config_dir, "last_config.json")
        config_dict = {
            "no_cut": no_cut,
            "config": config,
            "render": render,
            "body_only": body_only,
            "exploded_body": exploded_body,
            "uncut": uncut,
            "save_blend": save_blend,
            "angle": angle,
            "engine": engine,
            "material": material,
            "material_back": material_back,
            "lighting": lighting,
            "pitch": pitch,
            "guitar_rot": guitar_rot,
            "animate": animate,
            "no_render_anim": no_render_anim,
            "preview": preview,
            "dynamic_zoom": dynamic_zoom
        }
        if "random" in material.lower():
            if seed is not None:
                config_dict["//seed"] = seed
        else:
            if seed is not None:
                config_dict["seed"] = seed
                
        try:
            with open(last_config_path, "w") as f:
                json.dump(config_dict, f, indent=4)
            print(f"Saved CLI config preset to: {last_config_path}")
        except Exception as e:
            print(f"Warning: Failed to save last_config.json: {e}")
            
        render_args = ["--config-dir", config_dir]
        if uncut:
            render_args.append("--uncut")
        if body_only:
            render_args.append("--body-only")
        if exploded_body:
            render_args.append("--exploded-body")
        if save_blend:
            render_args.append("--save-blend")
        if pitch is not None:
            render_args += ["--pitch", str(pitch)]
        if guitar_rot is not None:
            render_args += ["--guitar-rot", str(guitar_rot)]
        if animate:
            render_args.append("--animate")
        if no_render_anim:
            render_args.append("--no-render-anim")
        if preview:
            render_args.append("--preview")
        if dynamic_zoom:
            render_args.append("--dynamic-zoom")
        if seed is not None:
            render_args += ["--seed", str(seed)]
        render_args += ["--angle", angle]
        render_args += ["--engine", engine]
        render_args += ["--material", material]
        render_args += ["--material-back", material_back]
        render_args += ["--lighting", lighting]
        
        cmd = [
            blender_exe,
            "--background",
            "--python",
            os.path.join(script_dir, "scripts", "render_guitar.py"),
            "--"
        ] + render_args
        
        import re
        import time
        
        # Launch subprocess with stdout/stderr piped
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        total_frames = 870  # default fallback
        start_time = None
        first_frame_num = 1
        
        # Regex patterns
        total_frames_pattern = re.compile(r"\[ANIMATION_TOTAL_FRAMES\]\s+(\d+)")
        frame_saved_pattern = re.compile(r"Saved:\s+'.*?frame_(\d+)\.png'")
        
        def format_duration(seconds):
            if seconds < 60:
                return f"{int(seconds)}s"
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if minutes < 60:
                return f"{minutes}m {secs}s"
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m {secs}s"
            
        for line in process.stdout:
            line_str = line.strip()
            
            # Check for total frames hook
            tf_match = total_frames_pattern.search(line_str)
            if tf_match:
                total_frames = int(tf_match.group(1))
                continue  # suppress the hook printout
                
            # Check for saved frame line
            fs_match = frame_saved_pattern.search(line_str)
            if fs_match:
                current_frame = int(fs_match.group(1))
                if start_time is None:
                    start_time = time.time()
                    first_frame_num = current_frame
                    print(f"Rendering: Frame {current_frame}/{total_frames} ({current_frame/total_frames*100:.1f}%) | ETA: Calculating...", flush=True)
                else:
                    elapsed = time.time() - start_time
                    rendered_count = max(1, current_frame - first_frame_num)
                    time_per_frame = elapsed / rendered_count
                    remaining_frames = total_frames - current_frame
                    eta_seconds = remaining_frames * time_per_frame
                    eta_str = format_duration(eta_seconds)
                    percent = (current_frame / total_frames) * 100
                    print(f"Rendering: Frame {current_frame}/{total_frames} ({percent:.1f}%) | Time per frame: {time_per_frame:.2f}s | ETA: {eta_str}", flush=True)
            else:
                # Print other lines as normal
                print(line_str, flush=True)
                
        process.wait()
        sys.exit(process.returncode)
    
    # Case 1: Config Export Mode
    if export_config_flag:
        print("Exporting guitar model configuration...")
        cmd_args = []
        if config:
            cmd_args += ["--config", config]
        if wrapper_export_config:
            cmd_args += ["--export-config", wrapper_export_config]
        else:
            cmd_args += ["--export-config"]
            
        cmd = [
            blender_exe,
            "--background",
            guitar_blend,
            "--python",
            os.path.abspath(__file__),
            "--"
        ] + cmd_args
        
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
        
    # Case 2: Config Import Mode
    if wrapper_import_config:
        print(f"Importing configuration: {wrapper_import_config}...")
        cmd_args = ["--import-config", wrapper_import_config]
        if config:
            cmd_args += ["--config", config]
        if generate:
            cmd_args += ["--generate"]
            
        cmd = [
            blender_exe,
            "--background",
            guitar_blend,
            "--python",
            os.path.abspath(__file__),
            "--"
        ] + cmd_args
        
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
        
    # Case 3: Build Mode (Stage 1 Configurator -> Stage 2 Scene Setup)
    setup_scene_path = os.path.join(script_dir, "scripts", "setup_scene.py")
    if not os.path.exists(setup_scene_path):
        print(f"Error: setup_scene.py not found at {setup_scene_path}")
        sys.exit(1)
        
    if config:
        print(f"Generating guitar model for config: {config}...")
        # Run Stage 1 (Configurator inside Blender)
        cmd1 = [
            blender_exe,
            "--background",
            guitar_blend,
            "--python",
            os.path.abspath(__file__),
            "--",
            "--config", config,
            "--generate"
        ]
        print(f"-> Launching Stage 1 Configurator...")
        res1 = subprocess.run(cmd1)
        if res1.returncode != 0:
            print(f"Error: Configurator stage failed with return code {res1.returncode}")
            sys.exit(res1.returncode)
            
        # Run Stage 2 (Scene Setup inside Blender)
        setup_args = ["--config", config]
        if no_cut:
            setup_args.append("--no-cut")
            
        cmd2 = [
            blender_exe,
            "--background",
            "--python",
            setup_scene_path,
            "--"
        ] + setup_args
        
        print(f"-> Launching Stage 2 Scene Setup...")
        res2 = subprocess.run(cmd2)
        sys.exit(res2.returncode)
        
    else:
        # No config profile specified: run Stage 2 directly with optional --no-cut
        setup_args = []
        if no_cut:
            setup_args.append("--no-cut")
            
        cmd2 = [
            blender_exe,
            "--background",
            "--python",
            setup_scene_path,
            "--"
        ] + setup_args
        
        print(f"-> Launching Stage 2 Scene Setup (no configuration profile)...")
        res2 = subprocess.run(cmd2)
        sys.exit(res2.returncode)


def run_internal_mode():
    # =========================================================================
    # BLENDER INTERNAL MODE (Running inside Blender)
    # =========================================================================
    # Retrieve arguments passed after '--'
    if '--' in sys.argv:
        args_start = sys.argv.index('--') + 1
        args_to_parse = sys.argv[args_start:]
    else:
        args_to_parse = []
        
    parser = argparse.ArgumentParser(description="Configure and generate Guitar Model from command line.")
    parser.add_argument("--export-config", nargs='?', const='__default__', help="Export current model parameters to a JSON file")
    parser.add_argument("--import-config", help="Import model parameters from a JSON file and save to guitar.blend")
    parser.add_argument("--config", help="Name of configuration profile to import and generate (e.g. 'sarcaster')")
    parser.add_argument("--generate", action="store_true", help="Generate and export models/guitar.obj")
    
    args = parser.parse_args(args_to_parse)
    
    if not (args.export_config or args.import_config or args.config or args.generate):
        parser.print_help()
        sys.exit(0)
        
    # Get Guitar Body mesh
    guitar_body = bpy.data.objects.get("Guitar Body")
    if not guitar_body:
        print("Error: 'Guitar Body' object not found in guitar.blend.")
        sys.exit(1)
        
    # Get Geometry Nodes modifier
    geom_modifier = None
    for mod in guitar_body.modifiers:
        if mod.type == 'NODES':
            geom_modifier = mod
            break
            
    if not geom_modifier:
        print("Error: Geometry Nodes modifier not found on 'Guitar Body' object.")
        sys.exit(1)
        
    script_dir = os.path.dirname(os.path.abspath(bpy.data.filepath)) if bpy.data.filepath else os.getcwd()
    if os.path.basename(script_dir) == "scripts":
        script_dir = os.path.dirname(script_dir)
    
    # Handle the --config helper
    config_name = args.config
    import_path = args.import_config
    export_path = args.export_config
    obj_filename = "guitar.obj"
    
    if config_name:
        if config_name != "default":
            # If no import/export path is explicitly specified, default import path to <config_name>.json
            if not import_path and not export_path:
                import_path = f"{config_name}.json"
            obj_filename = f"{config_name}.obj"
        else:
            obj_filename = "guitar.obj"
            
    if export_path == '__default__':
        if config_name and config_name != "default":
            export_path = f"{config_name}.json"
        else:
            export_path = "guitar_config.json"
            
    if import_path:
        resolved_path = resolve_config_path(import_path, script_dir)
        print(f"Importing parameters from: {resolved_path}...")
        import_config(geom_modifier, resolved_path)
        print("Saving updated parameters to guitar.blend...")
        bpy.ops.wm.save_mainfile()
        
    if export_path:
        resolved_path = resolve_config_path(export_path, script_dir)
        print(f"Exporting parameters to: {resolved_path}...")
        export_config(geom_modifier, resolved_path)
        
    if args.generate:
        print(f"Generating mesh as '{obj_filename}'...")
        generate_obj(guitar_body, script_dir, obj_filename)
        
    print("Execution complete.")


def main():
    if not inside_blender:
        run_wrapper_mode()
    else:
        run_internal_mode()


if __name__ == "__main__":
    main()
