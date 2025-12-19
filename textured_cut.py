import bpy
import bmesh
import os
import sys

# Setup Logging
LOG_FILE = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else r"E:\3D Printer\GuitarBuilder", "cut_log.txt")

def log(message):
    print(message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(str(message) + "\n")
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
    bpy.ops.mesh.subdivide(number_cuts=10) # Reduced to 10 for performance
    bpy.ops.object.mode_set(mode='OBJECT')

    # Simple subdivision or Subsurf modifier applied
    mod_sub = tool_obj.modifiers.new(name="Subdivisions", type='SUBSURF')
    mod_sub.subdivision_type = 'SIMPLE'
    mod_sub.levels = 2 # Reduced to 2 for stability
    mod_sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=mod_sub.name)
    
    # Create Texture
    tex = bpy.data.textures.new("CutTexture", 'CLOUDS')
    tex.noise_scale = 5.0 # Scaled 10x (was 0.5)
    tex.noise_depth = 2
    
    # Displace
    mod_disp = tool_obj.modifiers.new(name="Displacement", type='DISPLACE')
    mod_disp.texture = tex
    mod_disp.strength = 0.5 # Reverted to 0.5 (Proven Stable)
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
        bpy.ops.mesh.remove_doubles(threshold=0.001) # Merge nearby vertices
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
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

        # Only swap if both exist
        if len(part_a_obj.data.vertices) > 0 and len(part_b_obj.data.vertices) > 0:
            cy_a = get_center_y(part_a_obj)
            cy_b = get_center_y(part_b_obj)
            log(f"  Center Y Check: A={cy_a:.2f}, B={cy_b:.2f}")
            
            # Logic: 
            # Part A = Difference (Remaining).
            # Part B = Intersect (Cut Piece).
            # Standard Cut 1: Cut at 20. A=Top(>20), B=Bottom(<20).
            # So we expect A_Y > B_Y.
            
            if cy_a < cy_b:
                log("  DETECTED INVERSION: Part A is below Part B. Swapping to match naming convention (A=Top/High, B=Bottom/Low).")
                # Swap objects
                part_a_obj, part_b_obj = part_b_obj, part_a_obj
        
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
    # Find the target object by name
    target = bpy.data.objects.get(target_name)
    if not target:
        print(f"Error: Object '{target_name}' not found.")
        return

    # Ensure it's a mesh
    if target.type != 'MESH':
        log(f"Error: Object '{target_name}' is not a MESH.")
        return
        
    log(f"Auto-creating cutter for target: {target.name}")
    log(f"DEBUG: Target Dimensions: {target.dimensions}")
    
    # IMPORTANT: Select the target so it's ready for the operation
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    
    # Create Plane centered at origin
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cutter = bpy.context.active_object
    cutter.name = "Auto_Cutter"
    
    # Scale 50x (Reduced from 10x to maintain texture density? No, Scaled 10x from previous 5, so 50)
    cutter.scale = (50, 50, 50)
    
    # Move to specified location
    cutter.location = location
    
    # Rotate as specified (converting degrees to radians)
    import math
    cutter.rotation_euler = (
        math.radians(rotation_deg[0]),
        math.radians(rotation_deg[1]),
        math.radians(rotation_deg[2])
    )
    
    # Update view layer to get accurate dimensions after transform
    bpy.context.view_layer.update()
    log(f"DEBUG: Cutter Dimensions: {cutter.dimensions}")
    log(f"DEBUG: Cutter Location: {cutter.location}")
    
    # Ensure correct selection for the boolean operation
    # Active: Cutter
    # Selected: Target + Cutter
    bpy.ops.object.select_all(action='DESELECT')
    cutter.select_set(True)
    target.select_set(True)
    bpy.context.view_layer.objects.active = cutter
        
    # Run the cut function
    create_textured_cut(part_a_name=part1_name, part_b_name=part2_name, solidify_offset=solidify_offset)
    
    # Cleanup the auto-generated cutter if it was created
    if 'cutter' in locals() and cutter:
        # Note: create_textured_cut already deletes 'tool_obj' (the duplicate)
        # We need to delete the 'Auto_Cutter' original plane we just made
        try:
             log(f"  Cleaning up auto-cutter: {cutter.name}")
             bpy.data.objects.remove(cutter, do_unlink=True)
        except Exception as e:
            log(f"  Warning: Could not remove auto-cutter: {e}")

# perform_cuts function removed as per user request to keep cut logic centralized in setup_scene.py
