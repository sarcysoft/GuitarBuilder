import bpy
import os


def import_stl(stl_filename, script_dir, rotation_z=0, offset_x=0, offset_y=0, offset_z=0):
    """
    Import an STL file and apply transformations.
    
    Args:
        stl_filename: Name of the STL file to import
        script_dir: Directory where the STL file is located
        rotation_z: Rotation around Z axis in degrees (default 0)
        offset_x: X axis offset (default 0)
        offset_y: Y axis offset (default 0)
        offset_z: Z axis offset (default 0)
    
    Returns:
        The imported object if successful, None otherwise
    """
    import math
    
    stl_path = os.path.join(script_dir, stl_filename)
    
    if not os.path.exists(stl_path):
        print(f"Warning: Could not find {stl_path}")
        return None
    
    print(f"Found STL: {stl_path}")
    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')
    
    try:
        # Import STL
        if hasattr(bpy.ops.wm, 'stl_import'):
            print("Using bpy.ops.wm.stl_import...")
            bpy.ops.wm.stl_import(filepath=stl_path)
        else:
            print("Using bpy.ops.import_mesh.stl...")
            bpy.ops.import_mesh.stl(filepath=stl_path)
        
        # Get the imported object
        imported_obj = bpy.context.active_object
        if not imported_obj:
            print("Warning: Could not find imported STL object.")
            return None
        
        obj_name = f"Hardware_{stl_filename.replace('.stl', '')}"
        imported_obj.name = obj_name
        print(f"Renamed imported object to: {imported_obj.name}")
        
        # Apply transformations
        if rotation_z != 0:
            imported_obj.rotation_euler[2] = math.radians(rotation_z)
            bpy.context.view_layer.update()
        
        if offset_x != 0:
            imported_obj.location.x += offset_x
        if offset_y != 0:
            imported_obj.location.y += offset_y
        if offset_z != 0:
            imported_obj.location.z += offset_z
        bpy.context.view_layer.update()
        
        print(f"{obj_name} Location: {imported_obj.location}")
        print(f"{obj_name} Rotation: {imported_obj.rotation_euler}")
        
        return imported_obj
        
    except Exception as e:
        print(f"STL Import Failed: {e}")
        return None


def import_obj(obj_filename, script_dir, rotation_x=0, rotation_y=0, rotation_z=0, offset_x=0, offset_y=0, offset_z=0):
    """
    Import an OBJ file and apply transformations.
    
    Args:
        obj_filename: Name of the OBJ file to import
        script_dir: Directory where the OBJ file is located
        rotation_x: Rotation around X axis in degrees (default 0)
        rotation_y: Rotation around Y axis in degrees (default 0)
        rotation_z: Rotation around Z axis in degrees (default 0)
        offset_x: X axis offset (default 0)
        offset_y: Y axis offset (default 0)
        offset_z: Z axis offset (default 0)
    
    Returns:
        The imported object if successful, None otherwise
    """
    import math
    
    obj_path = os.path.join(script_dir, obj_filename)
    
    if not os.path.exists(obj_path):
        print(f"Warning: Could not find {obj_path}")
        return None
    
    print(f"Found OBJ: {obj_path}")
    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')
    
    try:
        # Import OBJ
        if hasattr(bpy.ops.wm, 'obj_import'):
            print("Using bpy.ops.wm.obj_import...")
            bpy.ops.wm.obj_import(filepath=obj_path)
        else:
            print("Using bpy.ops.import_scene.obj...")
            bpy.ops.import_scene.obj(filepath=obj_path)
        
        # Get the imported object
        imported_obj = bpy.context.active_object
        if not imported_obj:
            print("Warning: Could not find imported OBJ object.")
            return None
        
        print(f"Imported object: {imported_obj.name}")
        
        # Apply rotations
        imported_obj.rotation_mode = 'XYZ'
        if rotation_x != 0:
            imported_obj.rotation_euler[0] += math.radians(rotation_x)
        if rotation_y != 0:
            imported_obj.rotation_euler[1] += math.radians(rotation_y)
        if rotation_z != 0:
            imported_obj.rotation_euler[2] += math.radians(rotation_z)
        
        bpy.context.view_layer.update()
        
        # Apply offsets
        if offset_x != 0:
            imported_obj.location.x += offset_x
        if offset_y != 0:
            imported_obj.location.y += offset_y
        if offset_z != 0:
            imported_obj.location.z += offset_z
        bpy.context.view_layer.update()
        
        print(f"{imported_obj.name} Location: {imported_obj.location}")
        print(f"{imported_obj.name} Rotation: {imported_obj.rotation_euler}")
        
        return imported_obj
        
    except Exception as e:
        print(f"OBJ Import Failed: {e}")
def export_full_body_stl(guitar_body, output_dir):
    """Export the guitar body to a full body STL file in the output directory."""
    if not guitar_body:
        print("Warning: Guitar_Body not found for STL export")
        return False
        
    # Deselect all, then select only this object
    bpy.ops.object.select_all(action='DESELECT')
    guitar_body.select_set(True)
    bpy.context.view_layer.objects.active = guitar_body
    
    # Export to STL with global scale of 10.0
    stl_path = os.path.join(output_dir, "Guitar_Full_Body.stl")
    print(f"Exporting Guitar_Full_Body to STL: {stl_path}")
    try:
        if hasattr(bpy.ops.wm, 'stl_export'):
            bpy.ops.wm.stl_export(
                filepath=stl_path,
                export_selected_objects=True,
                global_scale=10.0
            )
        else:
            bpy.ops.export_mesh.stl(
                filepath=stl_path,
                use_selection=True,
                global_scale=10.0
            )
        print(f"Exported: {stl_path}")
        return True
    except Exception as export_error:
        print(f"Error exporting Guitar_Full_Body: {export_error}")
        return False


def import_and_subtract_stl(stl_filename, guitar_body, script_dir, rotation_z=0, offset_x=0, offset_y=0, offset_z=0, keep_object=False):
    """
    Import an STL file, position/rotate it, and subtract it from the guitar body using boolean operation.
    
    Args:
        stl_filename: Name of the STL file to import
        guitar_body: The guitar body object to subtract from
        script_dir: Directory where the STL file is located
        rotation_z: Rotation around Z axis in degrees (default 0)
        offset_x: X axis offset (default 0)
        offset_y: Y axis offset (default 0)
        offset_z: Z axis offset (default 0)
        keep_object: If True, keep the imported object after subtraction (default False)
    
    Returns:
        True if successful, False otherwise
    """
    # Import the STL file
    imported_obj = import_stl(stl_filename, script_dir, rotation_z, offset_x, offset_y, offset_z)
    if not imported_obj:
        return False
    
    obj_name = imported_obj.name
    
    # Boolean operation: Subtract from guitar body
    if not guitar_body:
        print("Warning: Guitar_Body not found for boolean operation")
        return False
    
    print(f"Subtracting {obj_name} from Guitar_Body...")
    
    # Make sure Guitar_Body is the active object
    bpy.ops.object.select_all(action='DESELECT')
    guitar_body.select_set(True)
    bpy.context.view_layer.objects.active = guitar_body
    
    # Add boolean modifier
    bool_mod = guitar_body.modifiers.new(name=f"{obj_name}_Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = imported_obj
    try:
        available_solvers = [e.identifier for e in bpy.types.BooleanModifier.bl_rna.properties['solver'].enum_items]
    except Exception:
        available_solvers = ['EXACT']
    if 'MANIFOLD' in available_solvers:
        bool_mod.solver = 'MANIFOLD'
    elif 'FLOAT' in available_solvers:
        bool_mod.solver = 'FLOAT'
    else:
        bool_mod.solver = 'EXACT'
    
    # Apply the modifier
    try:
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        print(f"{obj_name} subtracted successfully from Guitar_Body")
    except Exception as e:
        print(f"Error applying boolean modifier: {e}")
        return False
    
    # Delete the hardware object after boolean operation (unless keep_object is True)
    if not keep_object:
        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Deselect all and select only the hardware object
        bpy.ops.object.select_all(action='DESELECT')
        imported_obj.select_set(True)
        
        # Delete the selected object
        bpy.ops.object.delete()
        print(f"{obj_name} removed")
    else:
        print(f"{obj_name} kept in scene")
    
    return True


SEAM_PINS = [
    # (part_a, part_b, location, axis)
    # 1. Bot_Left <-> Bot_Right
    ("Guitar_Bot_Left", "Guitar_Bot_Right", (0.0, 5.0, 2.0), "X"),
    
    # 2. Bot_Left <-> Mid_Left
    ("Guitar_Bot_Left", "Guitar_Mid_Left", (-9.5, 10.0, 2.0), "Y"),
    
    # 3. Bot_Left <-> Mid
    ("Guitar_Bot_Left", "Guitar_Mid", (-2.5, 10.0, 2.0), "Y"),
    
    # 4. Bot_Right <-> Mid
    ("Guitar_Bot_Right", "Guitar_Mid", (2.5, 10.0, 2.0), "Y"),
    
    # 5. Bot_Right <-> Mid_Right
    ("Guitar_Bot_Right", "Guitar_Mid_Right", (9.5, 10.0, 2.0), "Y"),
    
    # 6. Mid_Left <-> Mid (2 pins)
    ("Guitar_Mid_Left", "Guitar_Mid", (-5.0, 15.0, 2.0), "X"),
    ("Guitar_Mid_Left", "Guitar_Mid", (-5.0, 21.0, 2.0), "X"),
    
    # 7. Mid_Right <-> Mid (2 pins)
    ("Guitar_Mid_Right", "Guitar_Mid", (5.0, 15.0, 2.0), "X"),
    ("Guitar_Mid_Right", "Guitar_Mid", (5.0, 21.0, 2.0), "X"),
    
    # 8. Mid_Left <-> Top_Left
    ("Guitar_Mid_Left", "Guitar_Top_Left", (-9.0, 26.0, 2.0), "Y"),
    
    # 9. Mid_Right <-> Top_Right
    ("Guitar_Mid_Right", "Guitar_Top_Right", (9.0, 26.0, 2.0), "Y"),
    
    # 10. Top_Left <-> Top_Mid
    ("Guitar_Top_Left", "Guitar_Top_Mid", (-5.0, 31.0, 2.0), "X"),
    
    # 11. Top_Right <-> Top_Mid
    ("Guitar_Top_Right", "Guitar_Top_Mid", (5.0, 31.0, 2.0), "X"),
    
    # 12. Mid <-> Top_Mid (2 pins)
    ("Guitar_Mid", "Guitar_Top_Mid", (-2.5, 27.5, 2.0), "Y"),
    ("Guitar_Mid", "Guitar_Top_Mid", (2.5, 27.5, 2.0), "Y"),
]


def setup_scene(no_cut = False, config_name = None, cut_type = 'flat', pin_diameter = 6.0, pin_length = 16.0, no_pins = False, hardware = None, electronics = None, neck = 'auto', custom_output_dir = None, project_dir = None, modifiers_cfg = None):
    print("Starting Scene Setup...")
    
    import sys
    this_script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    if this_script_dir not in sys.path:
        sys.path.insert(0, this_script_dir)
    
    # Initialize progress bar
    wm = bpy.context.window_manager
    wm.progress_begin(0, 100)
    progress = 0
    wm.progress_update(progress)
    
    # 1. Clear Objects (Keep Lights and Cameras)
    # 1. Clear Objects (Keep Lights and Cameras)
    # Ensure in Object Mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.object.select_all(action='DESELECT')
    
    # Aggressive Cleanup: Iterate over bpy.data.objects to catch everything
    objects_to_delete = []
    for obj in bpy.data.objects:
        # Keep Lights and Cameras
        if obj.type not in ['LIGHT', 'CAMERA']:
            objects_to_delete.append(obj)
            
    if objects_to_delete:
        print(f"Deleting {len(objects_to_delete)} objects...")
        # Reduce memory usage by removing in batches or directly
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        print("No objects to delete.")
    
    # 2. Import Files
    # Get the directory where this script is located
    # When running from Blender's Text Editor, __file__ might be the .blend file
    if bpy.data.filepath:
        # If a .blend file is open, use its directory
        script_dir = os.path.dirname(os.path.abspath(bpy.data.filepath))
    else:
        # Fallback to the script's actual location or hardcoded path
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # If __file__ is a .blend file, get its directory
            if script_dir.endswith('.blend'):
                script_dir = os.path.dirname(script_dir)
        except:
            script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    
    print(f"Script directory: {script_dir}")
    if os.path.basename(script_dir) == "scripts":
        root_dir = os.path.dirname(script_dir)
    else:
        root_dir = script_dir
    print(f"Root directory: {root_dir}")
    
    models_dir = os.path.join(root_dir, "models")
    obj_dir = os.path.join(models_dir, "obj")
    stl_dir = os.path.join(models_dir, "stl")
    third_party_dir = os.path.join(root_dir, "3rdParty")
    debug_dir = os.path.join(root_dir, "debug")
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
            
    body_model_name = None
    if project_dir and os.path.exists(os.path.join(project_dir, "project.json")):
        try:
            with open(os.path.join(project_dir, "project.json"), "r", encoding="utf-8") as f:
                pj = json.load(f)
                body_model_name = pj.get("body_model")
        except Exception:
            pass

    cand_filenames = []
    if body_model_name:
        cand_filenames.append(f"{body_model_name}.obj")
    if config_name and config_name != "default":
        cand_filenames.append(f"{config_name}.obj")
    cand_filenames.extend(["sarcaster.obj", "les_paul.obj", "flying_v.obj", "guitar.obj"])

    guitar_path = None
    guitar_obj_filename = cand_filenames[0]
    for cfn in cand_filenames:
        cp = os.path.join(obj_dir, cfn)
        if os.path.exists(cp):
            guitar_path = cp
            guitar_obj_filename = cfn
            break
    if not guitar_path:
        guitar_path = os.path.join(obj_dir, guitar_obj_filename)

    neck_obj_filename = "NeckAmericanStandard.obj"
    
    guitar_path = os.path.join(obj_dir, guitar_obj_filename)
    neck_path = os.path.join(third_party_dir, neck_obj_filename)
    
    # Import Guitar OBJ
    if os.path.exists(guitar_path):
        print(f"Found Guitar OBJ: {guitar_path}")
        # Deselect everything first
        bpy.ops.object.select_all(action='DESELECT')
        
        try:
            if hasattr(bpy.ops.wm, 'obj_import'):
                print("Using bpy.ops.wm.obj_import...")
                bpy.ops.wm.obj_import(filepath=guitar_path)
            else:
                print("Using bpy.ops.import_scene.obj...")
                bpy.ops.import_scene.obj(filepath=guitar_path)
                
            # Rename the imported object
            guitar = bpy.context.active_object
            if guitar:
                guitar.name = "Guitar_Body"
                print(f"Renamed imported object to: {guitar.name}")
                print(f"Guitar Dimensions (Before Rot): {guitar.dimensions}")
                print(f"Guitar Location (Before): {guitar.location}")
                
                 # Rotate Guitar to lie flat (Z-up thickness)
                import math
                # User reported -90 was "Wrong Way". Trying +90 (Flip over).
                guitar.rotation_euler[0] = math.radians(90)
                bpy.context.view_layer.update()
                bpy.ops.object.transform_apply(rotation=True)
                
                # Normalize Position: Set Min Y to 0 (Align with cuts)
                # Calculate Bounding Box in World Space
                min_y = min([v[1] for v in guitar.bound_box])
                # We can't trust bound_box directly if origin is weird, but scaling is applied.
                # Simplest: Origin to Geometry, then move.
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                # Now move to Y = Dimensions.Y / 2 (Since origin is center)
                guitar.location.y = guitar.dimensions.y / 2
                bpy.context.view_layer.update()
                bpy.ops.object.transform_apply(location=True)
                
                print(f"Guitar Dimensions (After Rot): {guitar.dimensions}")
                print(f"Guitar Location (After): {guitar.location}")
                print(f"Guitar Scale: {guitar.scale}")
                
            else:
                print("Warning: Could not find imported guitar object to rename.")
                
        except Exception as e:
            print(f"Guitar OBJ Import Failed: {e}")
            # Fallback attempt
            try:
                bpy.ops.import_scene.obj(filepath=guitar_path)
                guitar = bpy.context.active_object
                if guitar: 
                    guitar.name = "Guitar_Body"
                
                # Rotate Guitar to lie flat (Z-up thickness)
                # Current: Thin Y (standing). Target: Thin Z.
                import math
                guitar.rotation_euler[0] = math.radians(-90)
                bpy.ops.object.transform_apply(rotation=True)
                
                print(f"Renamed imported object to: {guitar.name}")

            except:
                pass
    else:
        print(f"Error: Could not find {guitar_path}")

    progress = 25
    wm.progress_update(progress)

    # Import and subtract hardware STL from guitar body
    guitar_body = bpy.data.objects.get("Guitar_Body")

    # Resolve hardware and electronics variants
    import json
    cfg_hardware = "standard"
    cfg_electronics = None
    if config_name:
        cfg_file = os.path.join(root_dir, "config", f"{config_name}.json")
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r") as f:
                    cdata = json.load(f)
                    cfg_hardware = cdata.get("hardware", cfg_hardware)
                    cfg_electronics = cdata.get("electronics", cfg_electronics)
            except Exception as e:
                print(f"Warning: Failed to read config JSON for variant defaults: {e}")

    hardware = hardware or cfg_hardware or "standard"
    if not electronics:
        electronics = cfg_electronics
        if not electronics and config_name:
            c_name = config_name.lower().strip()
            if "flying_v" in c_name or "sarcy_v" in c_name:
                electronics = "flying_v"
            elif "les_paul" in c_name or "sg" in c_name or "single_cut" in c_name:
                electronics = "les_paul"
            else:
                electronics = "sarcaster"
        elif not electronics:
            electronics = "sarcaster"

    print(f"Active Hardware Variant: {hardware}")
    print(f"Active Electronics Variant: {electronics}")

    # 1. Hardware cavity cutout subtraction
    hw_stl = None
    for cand in [f"hardware_cutout_{hardware}.stl", "hardware_cutout.stl", f"hardware_{hardware}.stl", "hardware.stl"]:
        if os.path.exists(os.path.join(stl_dir, cand)):
            hw_stl = cand
            break
    if hw_stl:
        import_and_subtract_stl(hw_stl, guitar_body, stl_dir, rotation_z=180, offset_y=40, offset_z=2)

    # Check for backplate on this hardware variant (omitting backplate skips it completely)
    bp_stl = f"backplate_{hardware}.stl"
    has_backplate = os.path.exists(os.path.join(stl_dir, bp_stl))
    if not has_backplate and hardware == "standard" and os.path.exists(os.path.join(stl_dir, "backplate.stl")):
        bp_stl = "backplate.stl"
        has_backplate = True

    if has_backplate:
        print(f"Applying backplate for hardware variant '{hardware}'...")
        mask_stl = f"backplate_mask_{hardware}.stl"
        if not os.path.exists(os.path.join(stl_dir, mask_stl)):
            mask_stl = "backplate_mask.stl"
        fix_stl = f"backplate_fixings_{hardware}.stl"
        if not os.path.exists(os.path.join(stl_dir, fix_stl)):
            fix_stl = "backplate_fixings.stl"

        import_and_subtract_stl(mask_stl, guitar_body, stl_dir, rotation_z=180, offset_y=40, offset_z=2)
        import_and_subtract_stl(fix_stl, guitar_body, stl_dir, rotation_z=180, offset_y=40, offset_z=2)
        import_stl(bp_stl, stl_dir, rotation_z=180, offset_y=40, offset_z=2)
    else:
        print(f"Hardware variant '{hardware}' has no backplate. Skipping backplate.")

    # 2. Electronics subtraction
    elec_stl = f"electronics_{electronics}.stl"
    if not os.path.exists(os.path.join(stl_dir, elec_stl)):
        elec_stl = "electronics.stl"
    import_and_subtract_stl(elec_stl, guitar_body, stl_dir, offset_x=0, offset_y=0, offset_z=2)

    # Check for electronics backplate (omitting skips it completely)
    ebp_stl = f"elec_backplate_{electronics}.stl"
    has_elec_backplate = os.path.exists(os.path.join(stl_dir, ebp_stl))
    if not has_elec_backplate and electronics == "sarcaster" and os.path.exists(os.path.join(stl_dir, "elec_backplate.stl")):
        ebp_stl = "elec_backplate.stl"
        has_elec_backplate = True

    if has_elec_backplate:
        print(f"Applying electronics backplate for variant '{electronics}'...")
        emask_stl = f"elec_backplate_mask_{electronics}.stl"
        if not os.path.exists(os.path.join(stl_dir, emask_stl)):
            emask_stl = "elec_backplate_mask.stl"
        efix_stl = f"elec_backplate_fixings_{electronics}.stl"
        if not os.path.exists(os.path.join(stl_dir, efix_stl)):
            efix_stl = "elec_backplate_fixings.stl"

        import_and_subtract_stl(emask_stl, guitar_body, stl_dir, offset_x=0, offset_y=0, offset_z=2)
        import_and_subtract_stl(efix_stl, guitar_body, stl_dir, offset_x=0, offset_y=0, offset_z=2)
        import_stl(ebp_stl, stl_dir, offset_y=0, offset_z=2)
    else:
        print(f"Electronics variant '{electronics}' has no backplate. Skipping backplate.")

    progress = 45
    wm.progress_update(progress)

    # Import Neck (OpenSCAD STL if available, else fallback to 3rdParty OBJ)
    neck_type = neck
    if not neck_type or neck_type == "auto":
        c_name = config_name.lower().strip() if config_name else ""
        if any(k in c_name for k in ["les_paul", "sg", "flying_v", "sarcy_v", "single_cut"]):
            neck_type = "les_paul"
        else:
            neck_type = "strat"

    neck_stl = os.path.join(models_dir, "stl", f"neck_{neck_type}.stl")
    if os.path.exists(neck_stl):
        try:
            print(f"Importing OpenSCAD display neck: {neck_stl}...")
            if hasattr(bpy.ops.wm, 'stl_import'):
                bpy.ops.wm.stl_import(filepath=neck_stl)
            else:
                bpy.ops.import_mesh.stl(filepath=neck_stl)
            neck_obj = bpy.context.active_object
            if neck_obj:
                neck_obj.name = f"Neck_{neck_type}"
        except Exception as e:
            print(f"Warning: Failed to import OpenSCAD neck: {e}")
    else:
        try:
            neck_imported = import_obj(neck_obj_filename, third_party_dir, rotation_x=-90, rotation_z=90, offset_z=-0.85)
            if not neck_imported:
                print(f"Warning: Optional display neck '{neck_obj_filename}' not loaded from 3rdParty.")
        except Exception as e:
            print(f"Warning: Failed to import optional neck: {e}")

    # Resolve output directory
    if custom_output_dir:
        output_dir = os.path.abspath(custom_output_dir)
    elif config_name and config_name != "default":
        output_dir = os.path.join(root_dir, "output", config_name)
    else:
        output_dir = os.path.join(root_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    guitar_body = bpy.data.objects.get("Guitar_Body")

    # Resolve modifiers configuration if project_dir or custom_output_dir is provided
    if modifiers_cfg is None:
        p_dir = project_dir
        if not p_dir and custom_output_dir:
            parent = os.path.dirname(os.path.abspath(custom_output_dir))
            if os.path.exists(os.path.join(parent, "project.json")):
                p_dir = parent
        if p_dir:
            p_json = os.path.join(p_dir, "project.json")
            if os.path.exists(p_json):
                try:
                    with open(p_json, "r", encoding="utf-8") as f:
                        p_data = json.load(f)
                        modifiers_cfg = p_data.get("modifiers", {})
                except Exception as e:
                    print(f"Warning: Could not read modifiers from {p_json}: {e}")

    # Determine if any modifier is enabled
    is_mod_enabled = bool(modifiers_cfg and (
        modifiers_cfg.get("enabled", False) or
        modifiers_cfg.get("spheres", {}).get("enabled", False) or
        modifiers_cfg.get("cylinders", {}).get("enabled", False) or
        modifiers_cfg.get("edge_frame", {}).get("enabled", False)
    ))

    # Apply Pre-Slice Modifiers (Sphere chunks & Cylinder perforations)
    if is_mod_enabled:
        try:
            import modifiers
            # Extract dynamic cavity exclusion zones from backplates in the scene
            cavity_margin = float(modifiers_cfg.get("keepout", {}).get("margin", 1.2))
            cavity_boxes = modifiers.extract_cavity_exclusion_boxes(margin=cavity_margin)
            if "keepout" not in modifiers_cfg:
                modifiers_cfg["keepout"] = {}
            modifiers_cfg["keepout"]["exclusion_boxes"] = cavity_boxes
            print(f"Applying pre-slice 3D modifiers (Spheres / Cylinders) with {len(cavity_boxes)} backplate exclusion zones...")
            modifiers.apply_pre_slice_modifiers(guitar_body, modifiers_cfg)
        except Exception as e:
            print(f"Warning: Failed to apply pre-slice modifiers: {e}")
            import traceback
            traceback.print_exc()

    if no_cut:
        print("no_cut is True. Exporting Guitar_Full_Body to STL...")
        export_full_body_stl(guitar_body, output_dir)
            
        # Save Debug State
        debug_path = os.path.join(debug_dir, "debug_guitar_result.blend")
        print(f"Saving debug result to: {debug_path}")
        try:
            bpy.ops.wm.save_as_mainfile(filepath=debug_path)
        except Exception as save_error:
            print(f"Error saving debug blend file: {save_error}")
            
        return

    # Always export full body STL for uncut renders even if cutting is performed
    print("Exporting Guitar_Full_Body to STL (uncut backup)...")
    export_full_body_stl(guitar_body, output_dir)

    # 3. Perform Cuts
    # Ensure the script directory is in sys.path to import textured_cut
    # Helper to clear log
    from datetime import datetime
    LOG_FILE = os.path.join(debug_dir, "cut_log.txt")
    try:
        with open(LOG_FILE, "w") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"=== NEW RUN: {timestamp} ===\n")
            f.write(f"Script: setup_scene.py\n")
            f.write(f"Working Directory: {script_dir}\n")
            f.write("=" * 50 + "\n\n")
    except:
        pass

    import sys
    import importlib.util
    
    # Remove any .blend file paths from sys.path that might interfere
    sys.path = [p for p in sys.path if not p.endswith('.blend')]
    
    # Make sure script_dir is first in the path for priority
    if script_dir in sys.path:
        sys.path.remove(script_dir)
    sys.path.insert(0, script_dir)
    print(f"Added to sys.path (priority): {script_dir}")
    
    # Remove cached import if it exists (from failed previous attempts)
    if 'textured_cut' in sys.modules:
        del sys.modules['textured_cut']
    
    print(f"Attempting to import textured_cut from: {script_dir}")
    
    try:
        # Use importlib to manually load the module from the file path
        textured_cut_path = os.path.join(script_dir, "textured_cut.py")
        print(f"Loading module from: {textured_cut_path}")
        print(f"File exists: {os.path.exists(textured_cut_path)}")
        
        spec = importlib.util.spec_from_file_location("textured_cut", textured_cut_path)
        textured_cut = importlib.util.module_from_spec(spec)
        sys.modules['textured_cut'] = textured_cut
        spec.loader.exec_module(textured_cut)
        
        print("Successfully imported textured_cut!")
        
        print(f"Starting Cut Operations ({cut_type})...")
        # Execute the cuts as requested - stop if any cut fails
        # Note: part1_name = DIFFERENCE (what remains), part2_name = INTERSECT (what's cut off)
        
        if not textured_cut.cut("Guitar_Body", location=(0, 10.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top", part2_name="Guitar_Bottom", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 1 failed. Stopping.")
            return

        # Swap: Left/Right were backwards
        if not textured_cut.cut("Guitar_Bottom", location=(0, 10.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Bot_Left", part2_name="Guitar_Bot_Right", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 2 failed. Stopping.")
            return
        
        # Vertical cut at X=-5
        if not textured_cut.cut("Guitar_Top", location=(-5.0, 20.0, 0), rotation_deg=(0, -90, 0), part1_name="Guitar_Middle_Right", part2_name="Guitar_Left", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 3 failed. Stopping.")
            return
            
        # Vertical cut at X=5 - Swap: Middle/Right were backwards
        if not textured_cut.cut("Guitar_Middle_Right", location=(5.0, 20.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Middle", part2_name="Guitar_Right", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 4 failed. Stopping.")
            return

        if not textured_cut.cut("Guitar_Left", location=(-10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Left", part2_name="Guitar_Mid_Left", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 5 failed. Stopping.")
            return
        
        # Swap: Top_Right/Mid_Right were backwards - swap again to fix
        if not textured_cut.cut("Guitar_Right", location=(10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Right", part2_name="Guitar_Mid_Right", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 6 failed. Stopping.")
            return

        # Cut 7: Swap: Top_Mid/Mid were backwards - swap again to fix
        if not textured_cut.cut("Guitar_Middle", location=(0, 27.5, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Mid", part2_name="Guitar_Mid", solidify_offset=1.0, cut_type=cut_type):
            print("ERROR: Cut 7 failed. Stopping.")
            return
        
        print("All cuts completed successfully!")

        # Apply Post-Slice Modifiers (Edge Frame / Exoskeleton)
        if is_mod_enabled and modifiers_cfg.get("edge_frame", {}).get("enabled", False):
            try:
                import modifiers
                all_parts = [
                    "Guitar_Bot_Left", "Guitar_Bot_Right",
                    "Guitar_Mid_Left", "Guitar_Mid_Right",
                    "Guitar_Top_Left", "Guitar_Top_Right",
                    "Guitar_Mid", "Guitar_Top_Mid"
                ]
                print("Applying post-slice 3D modifiers (Edge Frame)...")
                modifiers.apply_post_slice_modifiers(all_parts, modifiers_cfg)
            except Exception as e:
                print(f"Warning: Failed to apply post-slice modifiers: {e}")
                import traceback
                traceback.print_exc()

        # Apply locator pin holes to mating faces for vertical print assembly
        if cut_type == "flat" and not no_pins:
            print(f"Applying locator pin holes ({pin_diameter}mm diam x {pin_length}mm length)...")
            from collections import defaultdict
            part_pins_map = defaultdict(list)
            for part_a, part_b, loc, axis in SEAM_PINS:
                part_pins_map[part_a].append((loc, axis))
                part_pins_map[part_b].append((loc, axis))
            textured_cut.subtract_pin_holes_from_parts(
                part_pins_map,
                pin_diameter=pin_diameter,
                pin_length=pin_length,
                clearance=0.4
            )
            
            # Export printable locator pin STL
            textured_cut.export_locator_pin_stl(
                output_dir,
                pin_diameter=pin_diameter,
                pin_length=pin_length
            )
        
        # Export all resultant parts to separate STL files
        print("Exporting parts to STL files...")
        if custom_output_dir:
            output_dir = os.path.abspath(custom_output_dir)
        elif config_name and config_name != "default":
            output_dir = os.path.join(root_dir, "output", config_name)
        else:
            output_dir = os.path.join(root_dir, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        # List of all final part names
        final_parts = [
            "Guitar_Bot_Left",
            "Guitar_Bot_Right",
            "Guitar_Top_Left",
            "Guitar_Mid_Left",
            "Guitar_Top_Right",
            "Guitar_Mid_Right",
            "Guitar_Top_Mid",
            "Guitar_Mid"
        ]
        
        exported_count = 0
        for part_name in final_parts:
            obj = bpy.data.objects.get(part_name)
            if obj:
                # Deselect all, then select only this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                # Export to STL with global scale of 10.0
                stl_path = os.path.join(output_dir, f"{part_name}.stl")
                
                # Try Blender 5.0+ operator first, fallback to older versions
                try:
                    if hasattr(bpy.ops.wm, 'stl_export'):
                        # Blender 5.0+ uses wm.stl_export
                        bpy.ops.wm.stl_export(
                            filepath=stl_path,
                            export_selected_objects=True,
                            global_scale=10.0
                        )
                    else:
                        # Older Blender versions use export_mesh.stl
                        bpy.ops.export_mesh.stl(
                            filepath=stl_path,
                            use_selection=True,
                            global_scale=10.0
                        )
                    print(f"Exported: {stl_path}")
                    exported_count += 1
                except Exception as export_error:
                    print(f"Error exporting {part_name}: {export_error}")
            else:
                print(f"Warning: Part '{part_name}' not found for export")
        
        print(f"Successfully exported {exported_count} parts to {output_dir}")

        # Copy matching physical backplate STLs to output_dir if present
        import shutil
        if has_backplate:
            src_bp = os.path.join(stl_dir, bp_stl)
            if os.path.exists(src_bp):
                dst_bp = os.path.join(output_dir, "Backplate.stl")
                shutil.copyfile(src_bp, dst_bp)
                print(f"Exported Backplate.stl ({bp_stl}) to {output_dir}")
        if has_elec_backplate:
            src_ebp = os.path.join(stl_dir, ebp_stl)
            if os.path.exists(src_ebp):
                dst_ebp = os.path.join(output_dir, "Elec_Backplate.stl")
                shutil.copyfile(src_ebp, dst_ebp)
                print(f"Exported Elec_Backplate.stl ({ebp_stl}) to {output_dir}")
        
        # Save Debug State
        debug_path = os.path.join(debug_dir, "debug_guitar_result.blend")
        
        print(f"Saving debug result to: {debug_path}")
        bpy.ops.wm.save_as_mainfile(filepath=debug_path)
        
    except ImportError as e:
        print(f"Error: Could not import textured_cut.py: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"An error occurred during cutting: {e}")
        import traceback
        traceback.print_exc()

    print("Scene setup and processing complete.")

if __name__ == "__main__":
    import sys
    
    no_cut_val = False
    config_name_val = None
    cut_type_val = "flat"
    pin_diameter_val = 6.0
    pin_length_val = 16.0
    no_pins_val = False
    hardware_val = None
    electronics_val = None
    neck_val = "auto"
    custom_output_dir_val = None
    project_dir_val = None
    modifiers_cfg_val = None
    
    args = []
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
    else:
        args = sys.argv[1:]
        
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["--no-cut", "--no_cut", "no_cut"]:
            no_cut_val = True
            i += 1
        elif arg.startswith("--output-dir=") or arg.startswith("--output_dir="):
            custom_output_dir_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--output-dir", "--output_dir"] and i + 1 < len(args):
            custom_output_dir_val = args[i + 1]
            i += 2
        elif arg.startswith("--config="):
            config_name_val = arg.split("=", 1)[1]
            i += 1
        elif arg == "--config" and i + 1 < len(args):
            config_name_val = args[i + 1]
            i += 2
        elif arg.startswith("--cut-type="):
            cut_type_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--cut-type", "--cut_type"] and i + 1 < len(args):
            cut_type_val = args[i + 1]
            i += 2
        elif arg in ["--textured", "--textured-cut", "--textured_cut"]:
            cut_type_val = "textured"
            i += 1
        elif arg in ["--flat", "--flat-cut", "--flat_cut"]:
            cut_type_val = "flat"
            i += 1
        elif arg.startswith("--pin-diameter="):
            pin_diameter_val = float(arg.split("=", 1)[1])
            i += 1
        elif arg in ["--pin-diameter", "--pin_diameter"] and i + 1 < len(args):
            pin_diameter_val = float(args[i + 1])
            i += 2
        elif arg.startswith("--pin-length="):
            pin_length_val = float(arg.split("=", 1)[1])
            i += 1
        elif arg in ["--pin-length", "--pin_length"] and i + 1 < len(args):
            pin_length_val = float(args[i + 1])
            i += 2
        elif arg in ["--no-pins", "--no_pins"]:
            no_pins_val = True
            i += 1
        elif arg.startswith("--hardware="):
            hardware_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--hardware", "--hardware_variant", "--hw"] and i + 1 < len(args):
            hardware_val = args[i + 1]
            i += 2
        elif arg.startswith("--electronics="):
            electronics_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--electronics", "--electronics_variant", "--elec"] and i + 1 < len(args):
            electronics_val = args[i + 1]
            i += 2
        elif arg.startswith("--neck="):
            neck_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--neck", "--neck_style"] and i + 1 < len(args):
            neck_val = args[i + 1]
            i += 2
        elif arg.startswith("--project-dir=") or arg.startswith("--project="):
            project_dir_val = arg.split("=", 1)[1]
            i += 1
        elif arg in ["--project-dir", "--project"] and i + 1 < len(args):
            project_dir_val = args[i + 1]
            i += 2
        elif arg.startswith("--modifiers-json="):
            try:
                import json
                modifiers_cfg_val = json.loads(arg.split("=", 1)[1])
            except Exception:
                pass
            i += 1
        elif arg == "--modifiers-json" and i + 1 < len(args):
            try:
                import json
                modifiers_cfg_val = json.loads(args[i + 1])
            except Exception:
                pass
            i += 2
        else:
            i += 1
                
    setup_scene(no_cut_val, config_name_val, cut_type_val, pin_diameter_val, pin_length_val, no_pins_val, hardware_val, electronics_val, neck_val, custom_output_dir_val, project_dir=project_dir_val, modifiers_cfg=modifiers_cfg_val)
