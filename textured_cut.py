import bpy
import bmesh
import os
import sys
from datetime import datetime

# Setup Logging
LOG_FILE = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else r"E:\3D Printer\GuitarBuilder", "cut_log.txt")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(formatted_message + "\n")
    except:
        pass

# Clear log on fresh run (only if called directly, but hard to know)
# We'll just append.

def create_textured_cut(part_a_name=None, part_b_name=None, solidify_offset=1.0):
    # 1. Validation and Setup
    log(f"--- Starting Cut: {part_a_name} / {part_b_name} ---")
    
    # Ensure mode is OBJECT
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

        
    cutter_plane = bpy.context.active_object
    selected_objects = bpy.context.selected_objects
    
    if not cutter_plane or cutter_plane.type != 'MESH':
        print("Error: Active object must be a mesh (the cutter plane).")
        return {'CANCELLED'}
        
    targets = [obj for obj in selected_objects if obj != cutter_plane and obj.type == 'MESH']
    
    # Check Manifold
    # Manifold check removed to prevent BMesh error
    # for t in targets: ...
    
    if not targets:
        print("Error: Select at least one target object to cut.")
        return {'CANCELLED'}

    # 2. Process Cutter (The active plane)
    # We duplicate it first so we don't destroy the user's original plane reference if they want to undo/retry easily,
    # or strictly modify the temp one.
    
    # Duplicate plane to create the actual boolean tool
    bpy.ops.object.select_all(action='DESELECT')
    cutter_plane.select_set(True)
    bpy.context.view_layer.objects.active = cutter_plane
    bpy.ops.object.duplicate()
    tool_obj = bpy.context.active_object
    tool_obj.name = "Cutter_Tool_Temp"
    
    # Apply Scale is crucial for correct displacement and boolean
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Subdivide
    # Initial subdivision in Edit Mode to provide base density
    # For large planes, Subsurf level 6 on a single quad is not enough resolution.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=15) # Increased to 15 for deeper detail
    bpy.ops.object.mode_set(mode='OBJECT')

    # Simple subdivision or Subsurf modifier applied
    mod_sub = tool_obj.modifiers.new(name="Subdivisions", type='SUBSURF')
    mod_sub.subdivision_type = 'SIMPLE'
    mod_sub.levels = 2 # Keep at 2 for stability
    mod_sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=mod_sub.name)
    
    log(f"  Cutter subdivided: {len(tool_obj.data.vertices)} vertices")
    
    # Create Texture
    tex = bpy.data.textures.new("CutTexture", 'CLOUDS')
    tex.noise_scale = 5.0 # Scaled 10x (was 0.5)
    tex.noise_depth = 3 # Increased from 2 to 3 for more complexity
    
    # Displace
    mod_disp = tool_obj.modifiers.new(name="Displacement", type='DISPLACE')
    mod_disp.texture = tex
    mod_disp.strength = 2.0 # Increased to 2.0 for even deeper texture
    # We apply it to bake the geometry
    bpy.ops.object.modifier_apply(modifier=mod_disp.name)
    
    # Extrude to create volume (Use Solidify for centered thickness)
    mod_solid = tool_obj.modifiers.new(name="SolidifyCutter", type='SOLIDIFY')
    mod_solid.thickness = 50.0 # Clean value (Guitar is ~30mm)
    mod_solid.offset = solidify_offset       # Directional (0 to +Thick) or Centered (0) based on need
    bpy.ops.object.modifier_apply(modifier=mod_solid.name)
    
    # Recalculate normals
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Triangulate Cutter to help Boolean
    mod_tri_cutter = tool_obj.modifiers.new(name="TriangulateCutter", type='TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod_tri_cutter.name)
    
    # Additional cleanup on cutter mesh
    bpy.context.view_layer.objects.active = tool_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.fill_holes(sides=0)  # Fill any holes
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Data cleanup on Targets (Crucial for Booleans)
    for target in targets:
        # ... (Existing cleanup code) ...
        bpy.context.view_layer.objects.active = target
        target.select_set(True)
        
        # Bake all existing modifiers (Mirror, Subsurf, etc.)
        # This prevents "2 copies" issues where modifiers aren't evaluated by the Boolean
        bpy.ops.object.convert(target='MESH')
        
        # Apply Scale & Rotation to target to ensure boolean solver works in correct space
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        # HEAL MESH: Merge by distance to fix micro-gaps from previous cuts
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001) # Tighter threshold for higher detail meshes
        bpy.ops.mesh.delete_loose() # Remove any loose vertices/edges
        bpy.ops.mesh.fill_holes(sides=0)  # Fill any holes that might break booleans
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Deselect after processing
        target.select_set(False)
        
        # Triangulate to ensure robust boolean (FLOAT solver likes triangles)
        mod_tri = target.modifiers.new(name="TriangulateParams", type='TRIANGULATE')
        mod_tri.keep_custom_normals = True
        mod_tri.quad_method = 'BEAUTY'
        mod_tri.ngon_method = 'BEAUTY'
        mod_tri.min_vertices = 4 
        bpy.ops.object.modifier_apply(modifier=mod_tri.name)
        
        target.select_set(False)

    # 3. Perform Cuts on Targets
    for target in targets:
        log(f"  Processing target: {target.name}")
        log(f"  Target Location: {target.location}")
        log(f"  Target Dimensions: {target.dimensions}")
        
        # Calculate bounding box in world space to see where the mesh actually is
        bbox = [target.matrix_world @ v.co for v in target.data.vertices]
        if bbox:
            min_x = min(v.x for v in bbox)
            max_x = max(v.x for v in bbox)
            min_y = min(v.y for v in bbox)
            max_y = max(v.y for v in bbox)
            min_z = min(v.z for v in bbox)
            max_z = max(v.z for v in bbox)
            log(f"  Target Bounding Box: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")
        
        log(f"  Cutter Location: {tool_obj.location}")
        
        # Helper to robustly perform boolean
        def perform_robust_boolean(target_original, tool, op_name, part_name):
            # 1. Try EXACT Solver first (High Quality)
            log(f"  Attempting {op_name} on {part_name} with EXACT...")

            # Clean duplicate loop logic - extract helper if possible, but keep simple here
            target_original.select_set(True)
            bpy.context.view_layer.objects.active = target_original
            bpy.ops.object.duplicate()
            temp_obj = bpy.context.active_object
            temp_obj.name = part_name
            
            mod = temp_obj.modifiers.new(name="CutBool", type='BOOLEAN')
            mod.object = tool
            mod.operation = op_name
            mod.solver = 'EXACT'
            mod.use_self = True  # Enable self-intersection handling
            mod.use_hole_tolerant = True  # Better handling of non-manifold geometry
            
            # Apply Cleanly
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception as e:
                log(f"  EXACT Solver Error: {e}")
            
            # Check Result
            if len(temp_obj.data.vertices) > 0:
                return temp_obj
            
            log(f"  Warning: {part_name} is empty after EXACT solver. Falling back to FAST solver...")
            
            # 2. Fallback to FAST/FLOAT Solver (High Robustness)
            # Cleanup failed attempt
            bpy.data.objects.remove(temp_obj, do_unlink=True)
            
            # Retry
            target_original.select_set(True)
            bpy.context.view_layer.objects.active = target_original
            bpy.ops.object.duplicate()
            temp_obj = bpy.context.active_object
            temp_obj.name = part_name # Reuse name
            
            mod = temp_obj.modifiers.new(name="CutBoolFast", type='BOOLEAN')
            mod.object = tool
            mod.operation = op_name
            # Blender version compatibility: User reported 'FAST' is invalid, 'FLOAT' is valid.
            mod.solver = 'FLOAT'
            mod.use_self = True
            mod.use_hole_tolerant = False  # FLOAT solver doesn't support hole_tolerant
            
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception as e:
                 log(f"  FLOAT Solver Error: {e}")

            if len(temp_obj.data.vertices) > 0:
                log(f"  Success with FLOAT solver for {part_name}.")
                return temp_obj

            log(f"  CRITICAL FAILURE: {part_name} is empty after FLOAT solver too.")
            return temp_obj # Return empty object to allow script to continue (and fail gracefully)
            
        # STRATEGY CHANGE:
        # Calculate 'Intersect' (Part B) first, as it has proven reliable (Exact Solver).
        # Then calculate 'Difference' (Part A) by subtracting Part B from the Original.
        # This guarantees A and B are perfect complements.
        
        # Part B (Bottom/Cut Piece) - INTERSECT
        part_b_obj = perform_robust_boolean(target, tool_obj, 'INTERSECT', part_b_name if part_b_name else f"{target.name}_B")
        
        # Verify Part B
        part_b_valid = False
        if len(part_b_obj.data.vertices) == 0:
            log(f"Error: Part B ({part_b_obj.name}) is empty.")
        elif part_b_obj.dimensions == target.dimensions:
             log(f"Error: Part B ({part_b_obj.name}) is Identical to Original (Full).")
        else:
            part_b_valid = True
            log(f"  Part B generated successfully.")

        # Rename Target to avoid collision
        original_target_name = target.name
        target.name = original_target_name + "_Processed"
        
        # Generate Part A (Difference)
        part_a_obj = perform_robust_boolean(target, tool_obj, 'DIFFERENCE', part_a_name if part_a_name else f"{original_target_name}_A")
        
        if len(part_a_obj.data.vertices) == 0 or part_a_obj.dimensions == target.dimensions:
            log("  Warning: Standard Difference for Part A failed (Empty or Full).")
            # If B was valid, but A failed, we are in trouble.
            # But we disabled the risky 'Dual Intersect' fallback.
            # So we just log it.
        else:
             log("  Part A generated via Difference.")

        # Triangulate and Recalculate Normals to ensure clean topology/validity for subsequent cuts
        for obj in [part_a_obj, part_b_obj]:
            if obj and len(obj.data.vertices) > 0:
                # 1. Triangulate
                mod_tri = obj.modifiers.new(name="CleanTri", type='TRIANGULATE')
                mod_tri.min_vertices = 5 
                mod_tri.keep_custom_normals = False
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod_tri.name)
                
                # 2. Recalculate Normals (Critical for chained booleans)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=0.001) # Merge vertices to fix non-manifold edges
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # 3. Set origin to geometry center so object location reflects actual mesh position
                # This is CRITICAL for subsequent cuts to work with absolute coordinates
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                log(f"  {obj.name} origin set to geometry center, new location: {obj.location}")
        
        # ... (Inside create_textured_cut) ...
        
        # Explicitly re-assign names to ensure they claim the now-free original names
        # BUT FIRST: Validate which is Top and which is Bottom!
        
        def get_center_y(obj):
            if not obj or len(obj.data.vertices) == 0: return 0
            # Local center is 0,0,0 usually? No, geometry center.
            # Using bound box
            min_y = min([v[1] for v in obj.bound_box])
            max_y = max([v[1] for v in obj.bound_box])
            return (min_y + max_y) / 2 + obj.location.y

        # DISABLED: Swap logic causes issues with vertical cuts (X-axis splits)
        # The boolean operation order (INTERSECT vs DIFFERENCE) should match the intended names
        # Only swap if both exist
        #if len(part_a_obj.data.vertices) > 0 and len(part_b_obj.data.vertices) > 0:
        #    cy_a = get_center_y(part_a_obj)
        #    cy_b = get_center_y(part_b_obj)
        #    log(f"  Center Y Check: A={cy_a:.2f}, B={cy_b:.2f}")
        #    
        #    if cy_a < cy_b:
        #        log("  DETECTED INVERSION: Part A is below Part B. Swapping to match naming convention (A=Top/High, B=Bottom/Low).")
        #        # Swap objects
        #        part_a_obj, part_b_obj = part_b_obj, part_a_obj
        
        log(f"  Part A ({part_a_name}): location={part_a_obj.location}, dims={part_a_obj.dimensions}")
        log(f"  Part B ({part_b_name}): location={part_b_obj.location}, dims={part_b_obj.dimensions}")
        
        # Now apply names
        # SAFE RENAMING STRATEGY:
        # 1. Rename current parts to random temps to free up the namespace (especially if we swapped them!)
        import random
        r_id = random.randint(1000, 9999)
        part_a_obj.name = f"Temp_Part_A_{r_id}"
        part_b_obj.name = f"Temp_Part_B_{r_id}"
        
        final_a_name = part_a_name if part_a_name else f"{target.name}_A"
        final_b_name = part_b_name if part_b_name else f"{target.name}_B"
        
        # 2. Force Delete any OTHER objects holding the desired final names (Stale objects)
        for name in [final_a_name, final_b_name]:
            existing_obj = bpy.data.objects.get(name)
            if existing_obj:
                # This should NOT be our A or B because we just renamed them to Temp_...
                log(f"  Removing stale object '{name}' to prevent naming collision.")
                bpy.data.objects.remove(existing_obj, do_unlink=True)

        # 3. Assign Final Names
        part_a_obj.name = final_a_name
        part_b_obj.name = final_b_name
        
        log(f"  Final Parts: {part_a_obj.name} (High/Diff), {part_b_obj.name} (Low/Int)")
        log(f"  Dims A: {part_a_obj.dimensions}")
        log(f"  Dims B: {part_b_obj.dimensions}")
        
        # Verify result for next steps
        if len(part_a_obj.data.vertices) == 0:
             log(f"Error: Part A ({part_a_obj.name}) resulted in empty mesh.")
        if len(part_b_obj.data.vertices) == 0:
             log(f"Error: Part B ({part_b_obj.name}) resulted in empty mesh.")
             
        # Cleanup: Delete the original target object now that we have split it
        # It was renamed to "..._Processed" earlier
        try:
            log(f"  Cleaning up processed parent: {target.name}")
            bpy.data.objects.remove(target, do_unlink=True)
        except Exception as e:
            log(f"  Warning: Could not delete processed parent: {e}")
        
    # 4. Cleanup
    bpy.data.objects.remove(tool_obj, do_unlink=True)
    
    log("Cut operation complete.")
    return {'FINISHED'}

def cut(target_name, location, rotation_deg, part1_name=None, part2_name=None, solidify_offset=1.0):
    """
    Performs a textured cut on a target object.
    Returns True if successful, False if failed.
    """
    log(f"=== CUT OPERATION START ===")
    log(f"Target: {target_name} -> Part1: {part1_name}, Part2: {part2_name}")
    
    # Validate target object
    target = bpy.data.objects.get(target_name)
    if not target:
        log(f"ERROR: Object '{target_name}' not found.")
        return False

    if target.type != 'MESH':
        log(f"ERROR: Object '{target_name}' is not a MESH.")
        return False
    
    if len(target.data.vertices) == 0:
        log(f"ERROR: Target '{target_name}' is empty (0 vertices).")
        return False
        
    log(f"Target dimensions: {target.dimensions}")
    
    # Create cutter plane
    try:
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        cutter = bpy.context.active_object
        cutter.name = "Auto_Cutter"
        
        # Scale and position
        cutter.scale = (50, 50, 50)
        cutter.location = location
        
        import math
        cutter.rotation_euler = (
            math.radians(rotation_deg[0]),
            math.radians(rotation_deg[1]),
            math.radians(rotation_deg[2])
        )
        
        bpy.context.view_layer.update()
        log(f"Cutter location: {cutter.location}")
        
    except Exception as e:
        log(f"ERROR: Failed to create cutter: {e}")
        return False
    
    # Perform the cut operation
    try:
        bpy.ops.object.select_all(action='DESELECT')
        cutter.select_set(True)
        target.select_set(True)
        bpy.context.view_layer.objects.active = cutter
        
        result = create_textured_cut(part_a_name=part1_name, part_b_name=part2_name, solidify_offset=solidify_offset)
        
        # Cleanup the auto-cutter
        try:
            bpy.data.objects.remove(cutter, do_unlink=True)
        except:
            pass
        
        # Cleanup any leftover cutter debris
        cleanup_debris()
        
        # Verify the cut produced valid results
        part1 = bpy.data.objects.get(part1_name)
        part2 = bpy.data.objects.get(part2_name)
        
        if not part1 or len(part1.data.vertices) == 0:
            log(f"ERROR: Part1 '{part1_name}' is empty or missing!")
            log("=== CUT OPERATION FAILED ===")
            return False
            
        if not part2 or len(part2.data.vertices) == 0:
            log(f"ERROR: Part2 '{part2_name}' is empty or missing!")
            log("=== CUT OPERATION FAILED ===")
            return False
        
        log(f"SUCCESS: Created {part1_name} ({len(part1.data.vertices)} verts) and {part2_name} ({len(part2.data.vertices)} verts)")
        log("=== CUT OPERATION SUCCESS ===")
        return True
        
    except Exception as e:
        log(f"ERROR: Cut operation failed with exception: {e}")
        import traceback
        log(traceback.format_exc())
        
        # Cleanup on failure
        try:
            if cutter:
                bpy.data.objects.remove(cutter, do_unlink=True)
        except:
            pass
        cleanup_debris()
        
        log("=== CUT OPERATION FAILED ===")
        return False


def cleanup_debris():
    """Remove temporary cutter objects and duplicate artifacts"""
    debris_count = 0
    for obj in list(bpy.data.objects):
        # Delete cutters
        if obj.name.startswith("Cutter_Tool") or obj.name.startswith("Auto_Cutter"):
            bpy.data.objects.remove(obj, do_unlink=True)
            debris_count += 1
            continue
            
        # Delete processed parents
        if obj.name.endswith("_Processed"):
            bpy.data.objects.remove(obj, do_unlink=True)
            debris_count += 1
            continue
            
        # Delete duplicates (.001, .002, etc)
        if ".00" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
            debris_count += 1
    
    if debris_count > 0:
        log(f"Cleaned up {debris_count} debris objects")


# perform_cuts function removed as per user request to keep cut logic centralized in setup_scene.py
