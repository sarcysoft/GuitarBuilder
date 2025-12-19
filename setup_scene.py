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
            script_dir = r"E:\3D Printer\GuitarBuilder"
    
    print(f"Script directory: {script_dir}")
            
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
    from datetime import datetime
    LOG_FILE = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else r"E:\3D Printer\GuitarBuilder", "cut_log.txt")
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
        
        print("Starting Cut Operations...")
        # Execute the cuts as requested - stop if any cut fails
        # Note: part1_name = DIFFERENCE (what remains), part2_name = INTERSECT (what's cut off)
        
        if not textured_cut.cut("Guitar_Body", location=(0, 10.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top", part2_name="Guitar_Bottom", solidify_offset=1.0):
            print("ERROR: Cut 1 failed. Stopping.")
            return

        # Swap: Left/Right were backwards
        if not textured_cut.cut("Guitar_Bottom", location=(0, 10.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Bot_Left", part2_name="Guitar_Bot_Right", solidify_offset=1.0):
            print("ERROR: Cut 2 failed. Stopping.")
            return
        
        # Vertical cut at X=-5
        if not textured_cut.cut("Guitar_Top", location=(-5.0, 20.0, 0), rotation_deg=(0, -90, 0), part1_name="Guitar_Middle_Right", part2_name="Guitar_Left", solidify_offset=1.0):
            print("ERROR: Cut 3 failed. Stopping.")
            return
            
        # Vertical cut at X=5 - Swap: Middle/Right were backwards
        if not textured_cut.cut("Guitar_Middle_Right", location=(5.0, 20.0, 0), rotation_deg=(0, 90, 0), part1_name="Guitar_Middle", part2_name="Guitar_Right", solidify_offset=1.0):
            print("ERROR: Cut 4 failed. Stopping.")
            return

        if not textured_cut.cut("Guitar_Left", location=(-10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Left", part2_name="Guitar_Mid_Left", solidify_offset=1.0):
            print("ERROR: Cut 5 failed. Stopping.")
            return
        
        # Swap: Top_Right/Mid_Right were backwards - swap again to fix
        if not textured_cut.cut("Guitar_Right", location=(10.0, 26.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Right", part2_name="Guitar_Mid_Right", solidify_offset=1.0):
            print("ERROR: Cut 6 failed. Stopping.")
            return

        # Cut 7: Swap: Top_Mid/Mid were backwards - swap again to fix
        if not textured_cut.cut("Guitar_Middle", location=(0, 27.0, 0), rotation_deg=(90, 0, 0), part1_name="Guitar_Top_Mid", part2_name="Guitar_Mid", solidify_offset=1.0):
            print("ERROR: Cut 7 failed. Stopping.")
            return
        
        print("All cuts completed successfully!")
        
        # Export all resultant parts to separate STL files
        print("Exporting parts to STL files...")
        models_dir = os.path.join(script_dir, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            print(f"Created models directory: {models_dir}")
        
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
                stl_path = os.path.join(models_dir, f"{part_name}.stl")
                
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
        
        print(f"Successfully exported {exported_count} parts to {models_dir}")
        
        # Save Debug State
        debug_path = r"E:\3D Printer\GuitarBuilder\debug_guitar_result.blend"
        if bpy.data.filepath:
             debug_path = os.path.join(os.path.dirname(bpy.data.filepath), "debug_guitar_result.blend")
        
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
    setup_scene()
