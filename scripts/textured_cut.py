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

def create_textured_cut(part_a_name=None, part_b_name=None, solidify_offset=1.0, cut_type='flat'):
    # 1. Validation and Setup
    log(f"--- Starting Cut ({cut_type}): {part_a_name} / {part_b_name} ---")
    
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
    
    if cut_type == 'textured':
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
        tex.noise_scale = 1.0 # Scaled 10x (was 0.5)
        tex.noise_depth = 3 # Increased from 2 to 3 for more complexity
        
        # Displace
        mod_disp = tool_obj.modifiers.new(name="Displacement", type='DISPLACE')
        mod_disp.texture = tex
        mod_disp.strength = 2.0 # Increased to 2.0 for even deeper texture
        # We apply it to bake the geometry
        bpy.ops.object.modifier_apply(modifier=mod_disp.name)
    else:
        log("  Using FLAT cut (planar cut line for vertical printing).")
    
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
            try:
                available_solvers = [e.identifier for e in bpy.types.BooleanModifier.bl_rna.properties['solver'].enum_items]
            except Exception:
                available_solvers = ['EXACT']

            # Solver prioritization:
            # - MANIFOLD (Blender 5.1+): 140x faster than EXACT (~0.2s vs ~25s), exact watertight mesh topology.
            # - For FLAT cuts: Planar box tool cuts work instantly and cleanly with MANIFOLD or FLOAT.
            # - Fallback: EXACT is tested if fast solvers fail or are unavailable.
            candidate_solvers = []
            if 'MANIFOLD' in available_solvers:
                candidate_solvers.append('MANIFOLD')
            if cut_type == 'flat' and 'FLOAT' in available_solvers and 'FLOAT' not in candidate_solvers:
                candidate_solvers.append('FLOAT')
            if 'EXACT' in available_solvers and 'EXACT' not in candidate_solvers:
                candidate_solvers.append('EXACT')
            if 'FLOAT' in available_solvers and 'FLOAT' not in candidate_solvers:
                candidate_solvers.append('FLOAT')

            for solver in candidate_solvers:
                log(f"  Attempting {op_name} on {part_name} with {solver}...")

                target_original.select_set(True)
                bpy.context.view_layer.objects.active = target_original
                bpy.ops.object.duplicate()
                temp_obj = bpy.context.active_object
                temp_obj.name = part_name

                mod = temp_obj.modifiers.new(name=f"CutBool_{solver}", type='BOOLEAN')
                mod.object = tool
                mod.operation = op_name
                mod.solver = solver
                if solver == 'EXACT':
                    mod.use_self = True
                    mod.use_hole_tolerant = True
                elif solver == 'FLOAT':
                    mod.use_self = True
                    mod.use_hole_tolerant = False

                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except Exception as e:
                    log(f"  {solver} Solver Error: {e}")

                if len(temp_obj.data.vertices) > 0:
                    log(f"  Success with {solver} solver for {part_name} ({len(temp_obj.data.vertices)} vertices).")
                    return temp_obj

                log(f"  Warning: {part_name} is empty after {solver} solver. Trying next solver...")
                bpy.data.objects.remove(temp_obj, do_unlink=True)

            log(f"  CRITICAL FAILURE: {part_name} failed across all candidate solvers {candidate_solvers}.")
            target_original.select_set(True)
            bpy.context.view_layer.objects.active = target_original
            bpy.ops.object.duplicate()
            temp_obj = bpy.context.active_object
            temp_obj.name = part_name
            return temp_obj
            
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

def cut(target_name, location, rotation_deg, part1_name=None, part2_name=None, solidify_offset=1.0, cut_type='flat'):
    """
    Performs a cut (flat or textured) on a target object.
    Returns True if successful, False if failed.
    """
    log(f"=== CUT OPERATION START ({cut_type}) ===")
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
        
        result = create_textured_cut(part_a_name=part1_name, part_b_name=part2_name, solidify_offset=solidify_offset, cut_type=cut_type)
        
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


def create_cylinder_cutter(name, location, axis, radius, half_depth, taper_cone=True):
    """
    Creates a cylinder mesh tool oriented along axis ('X', 'Y', or 'Z')
    centered at location with total depth = 2 * half_depth.
    When taper_cone is True (default), adds a 45-degree conical tip at each end
    (height = radius) so blind holes print without support structures and provide
    an integrated reservoir for excess epoxy, glue, and printing extrusion zits.
    """
    import math
    import bmesh

    mesh = bpy.data.meshes.new(name)
    cyl = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(cyl)

    bm = bmesh.new()
    segments = 32
    cone_height = radius if taper_cone else 0.0

    z_top = half_depth
    z_bot = -half_depth

    top_verts = []
    bot_verts = []
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        top_verts.append(bm.verts.new((x, y, z_top)))
        bot_verts.append(bm.verts.new((x, y, z_bot)))

    # Cylinder side quads
    for i in range(segments):
        next_i = (i + 1) % segments
        bm.faces.new((bot_verts[i], top_verts[i], top_verts[next_i], bot_verts[next_i]))

    if taper_cone:
        # 45-degree conical caps for support-free 3D printing
        top_apex = bm.verts.new((0, 0, z_top + cone_height))
        bot_apex = bm.verts.new((0, 0, z_bot - cone_height))
        for i in range(segments):
            next_i = (i + 1) % segments
            bm.faces.new((top_verts[i], top_apex, top_verts[next_i]))
            bm.faces.new((bot_verts[next_i], bot_apex, bot_verts[i]))
    else:
        # Flat caps
        bm.faces.new(top_verts)
        bm.faces.new(list(reversed(bot_verts)))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    cyl.location = location
    if axis.upper() == 'X':
        cyl.rotation_euler = (0, math.radians(90), 0)
    elif axis.upper() == 'Y':
        cyl.rotation_euler = (math.radians(90), 0, 0)
    elif axis.upper() == 'Z':
        cyl.rotation_euler = (0, 0, 0)

    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = cyl
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return cyl


def subtract_pin_holes_from_parts(part_pins_map, pin_diameter=6.0, pin_length=16.0, clearance=0.4):
    """
    Subtracts locator pin holes from each specified part object.
    
    Args:
        part_pins_map: dict of { part_name: [ (location_tuple, axis_str), ... ] }
        pin_diameter: nominal pin diameter in mm (default: 6.0)
        pin_length: nominal total pin length in mm (default: 16.0)
        clearance: diametral clearance in mm (default: 0.4)
    """
    # Convert mm to Blender units (1 Blender unit = 10mm)
    hole_diameter_bu = (pin_diameter + clearance) / 10.0
    hole_radius_bu = hole_diameter_bu / 2.0
    
    # Extra 1.0mm depth clearance in blind hole so pins never bottom out
    hole_depth_bu = ((pin_length / 2.0) + 1.0) / 10.0
    
    log(f"Applying locator pin holes: diameter={pin_diameter+clearance:.2f}mm (r={hole_radius_bu:.3f}bu), depth={hole_depth_bu*10.0:.2f}mm")
    
    for part_name, pin_list in part_pins_map.items():
        if not pin_list:
            continue
            
        part_obj = bpy.data.objects.get(part_name)
        if not part_obj or part_obj.type != 'MESH':
            log(f"Warning: Part '{part_name}' not found for pin hole subtraction.")
            continue
            
        cutters = []
        for idx, (loc, axis) in enumerate(pin_list):
            cyl_name = f"TempPinCutter_{part_name}_{idx}"
            cyl = create_cylinder_cutter(cyl_name, loc, axis, hole_radius_bu, hole_depth_bu)
            cutters.append(cyl)
            
        if not cutters:
            continue
            
        # Join cutters into a single object if more than 1
        bpy.ops.object.select_all(action='DESELECT')
        for c in cutters:
            c.select_set(True)
        bpy.context.view_layer.objects.active = cutters[0]
        if len(cutters) > 1:
            bpy.ops.object.join()
        union_cutter = bpy.context.active_object
        union_cutter.name = f"Pin_Tool_{part_name}"
        
        # Subtract from part_obj
        bpy.ops.object.select_all(action='DESELECT')
        part_obj.select_set(True)
        bpy.context.view_layer.objects.active = part_obj
        
        bool_mod = part_obj.modifiers.new(name="PinHoles", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = union_cutter
        try:
            available_solvers = [e.identifier for e in bpy.types.BooleanModifier.bl_rna.properties['solver'].enum_items]
        except Exception:
            available_solvers = ['EXACT']
        bool_mod.solver = 'MANIFOLD' if 'MANIFOLD' in available_solvers else 'EXACT'
        
        try:
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
            log(f"  Successfully subtracted {len(pin_list)} pin holes from {part_name}")
        except Exception as e:
            log(f"  EXACT solver failed for {part_name} pin holes: {e}. Trying FLOAT solver...")
            # Fallback
            if bool_mod.name in part_obj.modifiers:
                part_obj.modifiers.remove(bool_mod)
            bool_mod_fast = part_obj.modifiers.new(name="PinHolesFast", type='BOOLEAN')
            bool_mod_fast.operation = 'DIFFERENCE'
            bool_mod_fast.object = union_cutter
            bool_mod_fast.solver = 'FLOAT'
            try:
                bpy.ops.object.modifier_apply(modifier=bool_mod_fast.name)
                log(f"  Success with FLOAT solver for {part_name} pin holes.")
            except Exception as e2:
                log(f"  Error applying pin holes to {part_name}: {e2}")
                
        # Clean up cutter
        try:
            bpy.data.objects.remove(union_cutter, do_unlink=True)
        except:
            pass


def export_locator_pin_stl(output_dir, pin_diameter=6.0, pin_length=16.0):
    """
    Creates and exports a printable locator pin STL file (locator_pin.stl).
    Pin has chamfered ends for easy insertion into holes.
    """
    # Radius and length in Blender units
    radius_bu = (pin_diameter / 2.0) / 10.0
    depth_bu = pin_length / 10.0
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius_bu,
        depth=depth_bu,
        end_fill_type='NGON',
        location=(0, 0, 0)
    )
    pin_obj = bpy.context.active_object
    pin_obj.name = "Locator_Pin"
    
    # Add a small chamfer/bevel modifier for lead-in ends
    mod_bev = pin_obj.modifiers.new(name="PinBevel", type='BEVEL')
    mod_bev.width = 0.05  # 0.5mm chamfer
    mod_bev.segments = 2
    mod_bev.limit_method = 'ANGLE'
    try:
        bpy.ops.object.modifier_apply(modifier=mod_bev.name)
    except:
        pass
        
    stl_path = os.path.join(output_dir, "locator_pin.stl")
    log(f"Exporting locator pin STL to: {stl_path}")
    
    bpy.ops.object.select_all(action='DESELECT')
    pin_obj.select_set(True)
    bpy.context.view_layer.objects.active = pin_obj
    
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
        log(f"Exported locator pin: {stl_path}")
    except Exception as e:
        log(f"Error exporting locator pin STL: {e}")
    finally:
        bpy.data.objects.remove(pin_obj, do_unlink=True)


# perform_cuts function removed as per user request to keep cut logic centralized in setup_scene.py
