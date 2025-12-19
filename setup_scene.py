import bpy
import os



def setup_scene():
    print("Starting Scene Setup...")
    
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
    # Hardcoded path to ensure it matches the user's workspace
    script_dir = r"E:\3D Printer\GuitarBuilder"
            
    guitar_obj_filename = "guitar.obj"
    neck_obj_filename = "NeckAmericanStandard.obj"
    
    guitar_path = os.path.join(script_dir, guitar_obj_filename)
    neck_path = os.path.join(script_dir, neck_obj_filename)
    
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

    # Import Neck OBJ
    if os.path.exists(neck_path):
        print(f"Found Neck OBJ: {neck_path}")
        # Deselect everything first so we know what gets selected is the new import
        bpy.ops.object.select_all(action='DESELECT')
        
        try:
            if hasattr(bpy.ops.wm, 'obj_import'):
                print("Using bpy.ops.wm.obj_import...")
                bpy.ops.wm.obj_import(filepath=neck_path)
            else:
                print("Using bpy.ops.import_scene.obj...")
                bpy.ops.import_scene.obj(filepath=neck_path)
                
            # Rotate Neck
            # The import usually selects the new objects.
            # We specifically want 'NeckAmericanStandard' (or the active object if it's the only one).
            
            # Simple assumption: The active object is the neck we just imported
            neck = bpy.context.active_object
            
            # Verify name just in case, or fallback to searching
            if neck is None or "Neck" not in neck.name:
                # Try to find by exact name
                neck = bpy.data.objects.get("NeckAmericanStandard")
            
            if neck:
                print(f"Rotating {neck.name}...")
                import math
                neck.rotation_mode = 'XYZ'
                # 90 degrees around X, then 90 around Z (cumulative)
                # Note: Euler rotation applied in XYZ order means X first, then Y, then Z.
                # So setting both at once works for "X then Z".
                neck.rotation_euler[0] += math.radians(-90)
                neck.rotation_euler[2] += math.radians(90)
            else:
                print("Warning: Could not find imported neck object to rotate.")
                
        except Exception as e:
            print(f"OBJ Import Failed: {e}")
            # Fallback attempt
            try: 
                 bpy.ops.import_scene.obj(filepath=neck_path)
            except:
                pass
    else:
        print(f"Error: Could not find {neck_path}")

    # 3. Perform Cuts
    # Ensure the script directory is in sys.path to import textured_cut
    # Helper to clear log
    LOG_FILE = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else r"E:\3D Printer\GuitarBuilder", "cut_log.txt")
    try:
        with open(LOG_FILE, "w") as f:
            f.write("--- New Run ---\n")
    except:
        pass

    import sys
    if script_dir not in sys.path:
        sys.path.append(script_dir)
        
    try:
        import textured_cut
        import importlib
        importlib.reload(textured_cut) # Ensure we use the latest version if modified
        
        print("Starting Cut Operations...")
        # Execute the cuts as requested
        textured_cut.cut("Guitar_Body", location=(0, 10.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top", part2_name="Guitar_Bottom", solidify_offset=1.0)

        textured_cut.cut("Guitar_Bottom", location=(0, 10.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Bot_Right", part2_name="Guitar_Bot_Left", solidify_offset=1.0)
        
        # Rotated -90 Y (270) to Flip normal so Intersect captures the Left side instead of Full
        textured_cut.cut("Guitar_Top", location=(-5.0, 20.0, 0), rotation_deg=(0, -90, 0), part1_name="Guitar_Middle_Right", part2_name="Guitar_Left", solidify_offset=1.0)
        # Note: Guitar_Middle_Right is the big piece, which is split into Middle and Right.
        # Rot 90 (X>5) keeps Right (Part B). Diff (Part A) matches Middle.
        # So Part1(A)=Middle, Part2(B)=Right.
        textured_cut.cut("Guitar_Middle_Right", location=(5.0, 20.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Right", part2_name="Guitar_Middle", solidify_offset=1.0)

        textured_cut.cut("Guitar_Left", location=(-10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Left", part2_name="Guitar_Mid_Left", solidify_offset=1.0)
        textured_cut.cut("Guitar_Right", location=(10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Right", part2_name="Guitar_Mid_Right", solidify_offset=1.0)

        # Cut 7: Split Guitar_Middle (Center Strip). Rot -90 (Keeps Top / Y > Cut).
        # So Part2(B)=Top. Part1(A)=Bottom.
        textured_cut.cut("Guitar_Middle", location=(0, 27.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Mid", part2_name="Guitar_Mid", solidify_offset=1.0)

        # Final Cleanup Sweep
        print("Running Final Debris Cleanup...")
        for obj in bpy.data.objects:
             # Delete Cutters
             if obj.name.startswith("Cutter_Tool") or obj.name.startswith("Auto_Cutter"):
                 print(f"  Removing debris: {obj.name}")
                 bpy.data.objects.remove(obj, do_unlink=True)
                 continue
                 
             # Delete Processed parents
             if obj.name.endswith("_Processed"):
                 print(f"  Removing intermediate: {obj.name}")
                 bpy.data.objects.remove(obj, do_unlink=True)
                 continue
                 
             # Delete duplicates (.00X)
             if is_debris(obj.name):
                  print(f"  Removing duplicate/artifact: {obj.name}")
                  bpy.data.objects.remove(obj, do_unlink=True)
        
        # Save Debug State
        debug_path = r"E:\3D Printer\GuitarBuilder\debug_guitar_result.blend"
        if bpy.data.filepath:
             debug_path = os.path.join(os.path.dirname(bpy.data.filepath), "debug_guitar_result.blend")
        
        print(f"Saving debug result to: {debug_path}")
        bpy.ops.wm.save_as_mainfile(filepath=debug_path)
        
    except ImportError:
        print("Error: Could not import textured_cut.py. Make sure it is in the same directory.")
    except Exception as e:
        print(f"An error occurred during cutting: {e}")

    print("Scene setup and processing complete.")

def is_debris(name):
    # Helper to identify unwanted suffixes
    if ".00" in name:
        # Check if it's a version of a known valid part?
        # Setup list of expected final names
        valid_names = [
            "Guitar_Bot_Left", "Guitar_Bot_Right",
            "Guitar_Top_Left", "Guitar_Top_Right", "Guitar_Top_Mid",
            "Guitar_Mid_Left", "Guitar_Mid_Right", "Guitar_Mid",
            # Neck?
            "NeckAmericanStandard"
        ]
        base_name = name.split(".00")[0]
        # If the base name is valid, then this .001 is a duplicate we don't want.
        # Unless the valid name IS the one with .001 (unlikely).
        return True
    return False

if __name__ == "__main__":
    setup_scene()
