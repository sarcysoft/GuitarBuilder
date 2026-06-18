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
    """Locate the Blender executable on Windows."""
    # 1. Check if 'blender' is in the system PATH
    try:
        result = subprocess.run(["where", "blender"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return "blender"
    except Exception:
        pass
    
    # 2. Check the standard installation directories in Program Files
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    bf = os.path.join(pf, "Blender Foundation")
    if os.path.exists(bf):
        subdirs = [os.path.join(bf, d) for d in os.listdir(bf) if d.startswith("Blender")]
        # Sort subdirs to get the highest version first (e.g. Blender 5.1 over 4.2)
        subdirs.sort(reverse=True)
        for sd in subdirs:
            exe = os.path.join(sd, "blender.exe")
            if os.path.exists(exe):
                return exe
                
    # 3. Fallback to 'blender'
    return "blender"


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


def generate_obj(guitar_body, script_dir):
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
        
    obj_path = os.path.join(models_dir, "guitar.obj")
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


if not inside_blender:
    # =========================================================================
    # WRAPPER MODE (System Shell)
    # =========================================================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_exe = find_blender()
    
    guitar_blend = os.path.join(script_dir, "guitar.blend")
    if not os.path.exists(guitar_blend):
        print(f"Error: {guitar_blend} not found in the workspace.")
        sys.exit(1)
        
    # Re-run this script inside Blender
    cmd = [
        blender_exe,
        "--background",
        guitar_blend,
        "--python",
        os.path.abspath(__file__),
        "--"
    ] + sys.argv[1:]
    
    print(f"Launching Blender in background mode...")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

else:
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
    parser.add_argument("--export-config", help="Export current model parameters to a JSON file")
    parser.add_argument("--import-config", help="Import model parameters from a JSON file and save to guitar.blend")
    parser.add_argument("--generate", action="store_true", help="Generate and export models/guitar.obj")
    
    args = parser.parse_args(args_to_parse)
    
    if not (args.export_config or args.import_config or args.generate):
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
    
    if args.import_config:
        print(f"Importing parameters from: {args.import_config}...")
        import_config(geom_modifier, args.import_config)
        print("Saving updated parameters to guitar.blend...")
        bpy.ops.wm.save_mainfile()
        
    if args.export_config:
        print(f"Exporting parameters...")
        export_config(geom_modifier, args.export_config)
        
    if args.generate:
        print("Generating mesh...")
        generate_obj(guitar_body, script_dir)
        
    print("Execution complete.")
