"""
modifiers.py - Artistic 3D Mesh Modifiers for GuitarBuilder

Applies non-structural 3D modifications to the guitar body while strictly preserving:
- The central structural core beneath the neck, strings, and bridge (spine keep-out).
- The hardware cavity and backplate mountings (exclusion zone based on actual backplate + margin).
- The electronics cavity and backplate mountings.
- The shoulder cutouts and neck joint roots (maintaining full structural integrity).

Supported modifiers:
1. Sphere Chunks Cutout: Randomly allocated spheres cutting organic chunks out of the body surface or volume.
2. Angled Cylinders Cutout: Perforating tunnels through the body at various angles.
3. Edge Frame (Exoskeleton): Removes all but the edge region of post-split pieces (when viewed from above),
   leaving a strong structural frame while strictly preserving shoulder cutout integrity.
"""

import os
import sys
import math
import random

try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler, Matrix
    inside_blender = True
except ImportError:
    inside_blender = False


def log(msg):
    print(f"[MODIFIERS] {msg}")


def extract_cavity_exclusion_boxes(margin=1.2):
    """
    Extracts exact world bounding boxes for cavity backplates and cutouts in the scene,
    expanded by the specified margin.
    As requested: the electronics and hardware exclusion zones are strictly based on the
    backplate and cavity sizes (with margin) since these dictate the cavity sizes in the body.
    """
    boxes = []

    # 1. Authoritative base physical cavity & backplate zones
    # Electronics cavity + backplate: spans X=[2.0, 14.5], Y=[5.5, 24.5] (Sarcaster / Standard)
    # Hardware cavity + backplate: spans X=[-6.0, 6.0], Y=[12.0, 41.0]
    elec_box = {
        "name": "Electronics_Cavity_Backplate",
        "min_x": 2.0 - margin,
        "max_x": 14.5 + margin,
        "min_y": 5.5 - margin,
        "max_y": 24.5 + margin,
        "min_z": -1.0,
        "max_z": 6.0
    }
    hw_box = {
        "name": "Hardware_Cavity_Backplate",
        "min_x": -6.0 - margin,
        "max_x": 6.0 + margin,
        "min_y": 12.0 - margin,
        "max_y": 41.0 + margin,
        "min_z": -1.0,
        "max_z": 6.0
    }

    # 2. Inspect any actual mesh objects in the scene to expand/refine boundaries
    if inside_blender:
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            name_lower = obj.name.lower()
            if any(k in name_lower for k in ["elec_backplate", "electronics", "elec_"]):
                bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
                elec_box["min_x"] = min(elec_box["min_x"], min(v.x for v in bbox) - margin)
                elec_box["max_x"] = max(elec_box["max_x"], max(v.x for v in bbox) + margin)
                elec_box["min_y"] = min(elec_box["min_y"], min(v.y for v in bbox) - margin)
                elec_box["max_y"] = max(elec_box["max_y"], max(v.y for v in bbox) + margin)
                log(f"Refined electronics exclusion zone from '{obj.name}': X=[{elec_box['min_x']:.1f}, {elec_box['max_x']:.1f}], Y=[{elec_box['min_y']:.1f}, {elec_box['max_y']:.1f}]")
            elif any(k in name_lower for k in ["backplate", "hardware_cutout", "hardware_physical"]):
                bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
                hw_box["min_x"] = min(hw_box["min_x"], min(v.x for v in bbox) - margin)
                hw_box["max_x"] = max(hw_box["max_x"], max(v.x for v in bbox) + margin)
                hw_box["min_y"] = min(hw_box["min_y"], min(v.y for v in bbox) - margin)
                hw_box["max_y"] = max(hw_box["max_y"], max(v.y for v in bbox) + margin)
                log(f"Refined hardware exclusion zone from '{obj.name}': X=[{hw_box['min_x']:.1f}, {hw_box['max_x']:.1f}], Y=[{hw_box['min_y']:.1f}, {hw_box['max_y']:.1f}]")

    boxes.append(elec_box)
    boxes.append(hw_box)
    log(f"Protected Electronics Backplate/Cavity exclusion zone: X=[{elec_box['min_x']:.1f}, {elec_box['max_x']:.1f}], Y=[{elec_box['min_y']:.1f}, {elec_box['max_y']:.1f}] (margin {margin*10:.0f}mm)")
    log(f"Protected Hardware Backplate/Cavity exclusion zone: X=[{hw_box['min_x']:.1f}, {hw_box['max_x']:.1f}], Y=[{hw_box['min_y']:.1f}, {hw_box['max_y']:.1f}] (margin {margin*10:.0f}mm)")
    return boxes


def is_in_keepout_zone(x, y, z, radius, keepout_cfg, rot_x=0.0, rot_y=0.0, z_range=None):
    """
    Checks if a sphere or angled cylinder cutter at (x, y, z) with given radius intersects
    any protected structural zone (spine, hardware cavity/backplate, electronics cavity/backplate).
    For tilted cylinders, evaluates key points across the body thickness to guarantee no penetration.
    """
    core_half_width = float(keepout_cfg.get("core_width", 11.0)) / 2.0  # default 5.5 cm
    margin = float(keepout_cfg.get("margin", 1.2))  # safety buffer in cm
    effective_core_half = core_half_width + margin

    # Sample test points along the cutter axis across body thickness
    test_points = [(x, y)]
    if z_range and (abs(rot_x) > 1e-4 or abs(rot_y) > 1e-4):
        z_min, z_max = z_range
        for sample_z in [z_min, (z_min + z_max) / 2.0, z_max]:
            dz = sample_z - z
            # Small angle / rotation projection
            px = x + dz * math.tan(rot_y)
            py = y - dz * math.tan(rot_x)
            test_points.append((px, py))

    for px, py in test_points:
        # 1. Central Core Spine Check (neck pocket, pickups, strings, bridge)
        if abs(px) - radius < effective_core_half:
            if py + radius >= 6.0 and py - radius <= 46.0:
                return True

        # 2. Dynamic Cavity Exclusion Zones (Electronics Backplate + Hardware Backplate + Cavities)
        for box in keepout_cfg.get("exclusion_boxes", []):
            if (px + radius >= box["min_x"] and px - radius <= box["max_x"] and
                py + radius >= box["min_y"] and py - radius <= box["max_y"]):
                return True

    return False


def get_body_bounds(obj):
    """Returns (min_x, max_x, min_y, max_y, min_z, max_z) of object in world space."""
    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return (
        min(v.x for v in bbox), max(v.x for v in bbox),
        min(v.y for v in bbox), max(v.y for v in bbox),
        min(v.z for v in bbox), max(v.z for v in bbox)
    )


def apply_boolean_difference(target_obj, tool_obj, name="ModBool"):
    """Applies a boolean DIFFERENCE using MANIFOLD or EXACT solver."""
    if not target_obj or not tool_obj:
        return False

    solvers = []
    if hasattr(bpy.types.BooleanModifier, "bl_rna"):
        solvers = [e.identifier for e in bpy.types.BooleanModifier.bl_rna.properties['solver'].enum_items]

    preferred = 'MANIFOLD' if 'MANIFOLD' in solvers else ('EXACT' if 'EXACT' in solvers else 'FAST')
    mod = target_obj.modifiers.new(name=name, type='BOOLEAN')
    mod.object = tool_obj
    mod.operation = 'DIFFERENCE'
    if hasattr(mod, 'solver'):
        mod.solver = preferred

    bpy.context.view_layer.objects.active = target_obj
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
        log(f"Applied boolean {name} using {preferred} solver.")
        return True
    except Exception as e:
        log(f"Failed boolean with {preferred}: {e}. Retrying with EXACT/FAST...")
        for fallback in ['EXACT', 'FAST']:
            if fallback != preferred and fallback in solvers:
                try:
                    mod.solver = fallback
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    log(f"Fallback {fallback} succeeded.")
                    return True
                except Exception:
                    pass
        return False


def generate_spheres_cutter(target_obj, sphere_cfg, keepout_cfg):
    """
    Creates a single joined mesh of spheres to cut chunks out of the body surface / volume.
    """
    count = int(sphere_cfg.get("count", 35))
    min_r = float(sphere_cfg.get("min_radius", 1.2))
    max_r = float(sphere_cfg.get("max_radius", 2.6))
    placement = sphere_cfg.get("placement", "surface")
    seed = int(sphere_cfg.get("seed", 42))

    rng = random.Random(seed)
    min_x, max_x, min_y, max_y, min_z, max_z = get_body_bounds(target_obj)
    rim_margin = float(keepout_cfg.get("rim_margin", 0.8))

    created_spheres = []
    placed_spheres = []
    attempts = 0
    max_attempts = count * 25

    log(f"Generating {count} sphere cutters (radius {min_r:.1f}-{max_r:.1f}cm, placement '{placement}', seed {seed})...")

    while len(created_spheres) < count and attempts < max_attempts:
        attempts += 1
        r = rng.uniform(min_r, max_r)
        x = rng.uniform(min_x + rim_margin + r * 0.4, max_x - rim_margin - r * 0.4)
        y = rng.uniform(min_y + rim_margin + r * 0.4, max_y - rim_margin - r * 0.4)

        if is_in_keepout_zone(x, y, 0, r, keepout_cfg):
            continue

        # Prevent deep self-intersection between spheres to maintain 2-manifold mesh topology & structural webs
        if any(math.hypot(x - p[0], y - p[1]) < (r + p[3]) * 0.9 for p in placed_spheres):
            continue

        if placement == "surface":
            if rng.random() > 0.5:
                z = max_z - rng.uniform(0.15 * r, 0.45 * r)
            else:
                z = min_z + rng.uniform(0.15 * r, 0.45 * r)
        elif placement == "through":
            z = (min_z + max_z) / 2.0 + rng.uniform(-0.2, 0.2)
        else:  # mixed
            pick = rng.random()
            if pick < 0.4:
                z = max_z - rng.uniform(0.15 * r, 0.45 * r)
            elif pick < 0.8:
                z = min_z + rng.uniform(0.15 * r, 0.45 * r)
            else:
                z = (min_z + max_z) / 2.0

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16,
            ring_count=12,
            radius=r,
            location=(x, y, z)
        )
        s_obj = bpy.context.active_object
        created_spheres.append(s_obj)
        placed_spheres.append((x, y, z, r))

    if not created_spheres:
        log("No valid sphere positions found outside keepout zones.")
        return None

    log(f"Created {len(created_spheres)} valid spheres in {attempts} attempts. Joining into cutter tool...")

    bpy.ops.object.select_all(action='DESELECT')
    for s in created_spheres:
        s.select_set(True)
    bpy.context.view_layer.objects.active = created_spheres[0]
    bpy.ops.object.join()
    combined_cutter = bpy.context.active_object
    combined_cutter.name = "Modifier_Spheres_Cutter"
    return combined_cutter


def generate_cylinders_cutter(target_obj, cyl_cfg, keepout_cfg):
    """
    Creates a single joined mesh of angled cylinders to cut perforations/tunnels through the body.
    Cylinder radius is randomly chosen between configurable min_radius and max_radius.
    """
    count = int(cyl_cfg.get("count", 25))
    min_radius = float(cyl_cfg.get("min_radius", cyl_cfg.get("radius", 0.4)))
    max_radius = float(cyl_cfg.get("max_radius", cyl_cfg.get("radius", 0.8)))
    if min_radius > max_radius:
        min_radius, max_radius = max_radius, min_radius
    max_angle_deg = float(cyl_cfg.get("max_angle", 25.0))
    style = cyl_cfg.get("style", "random")
    seed = int(cyl_cfg.get("seed", 42))

    rng = random.Random(seed)
    min_x, max_x, min_y, max_y, min_z, max_z = get_body_bounds(target_obj)
    body_thickness = max_z - min_z
    depth = body_thickness * 3.5
    rim_margin = float(keepout_cfg.get("rim_margin", 0.8))

    created_cyls = []
    placed_cyls = []
    attempts = 0
    max_attempts = count * 35

    log(f"Generating {count} cylinder cutters (radius {min_radius:.2f}-{max_radius:.2f}cm, max tilt {max_angle_deg}deg, style '{style}', seed {seed})...")

    while len(created_cyls) < count and attempts < max_attempts:
        attempts += 1
        radius = rng.uniform(min_radius, max_radius)
        x = rng.uniform(min_x + rim_margin + radius, max_x - rim_margin - radius)
        y = rng.uniform(min_y + rim_margin + radius, max_y - rim_margin - radius)
        z = (min_z + max_z) / 2.0

        if style == "vertical":
            rot_x = 0.0
            rot_y = 0.0
        elif style == "fan":
            tilt_dir = 1.0 if x > 0 else -1.0
            rot_y = math.radians(tilt_dir * rng.uniform(5.0, max_angle_deg))
            rot_x = math.radians(rng.uniform(-max_angle_deg * 0.5, max_angle_deg * 0.5))
        else:  # random 3D angles
            tilt = math.radians(rng.uniform(0.0, max_angle_deg))
            azimuth = rng.uniform(0.0, 2 * math.pi)
            rot_x = tilt * math.cos(azimuth)
            rot_y = tilt * math.sin(azimuth)

        # Test keepout zone considering cylinder tilt across thickness
        if is_in_keepout_zone(x, y, z, radius, keepout_cfg, rot_x=rot_x, rot_y=rot_y, z_range=(min_z, max_z)):
            continue

        # Prevent overlapping tunnels to ensure structural walls between holes
        if any(math.hypot(x - p[0], y - p[1]) < (radius + p[2]) * 1.3 for p in placed_cyls):
            continue

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=radius,
            depth=depth,
            location=(x, y, z),
            rotation=(rot_x, rot_y, 0)
        )
        c_obj = bpy.context.active_object
        created_cyls.append(c_obj)
        placed_cyls.append((x, y, radius))

    if not created_cyls:
        log("No valid cylinder positions found outside keepout zones.")
        return None

    log(f"Created {len(created_cyls)} valid cylinders in {attempts} attempts. Joining into cutter tool...")

    bpy.ops.object.select_all(action='DESELECT')
    for c in created_cyls:
        c.select_set(True)
    bpy.context.view_layer.objects.active = created_cyls[0]
    bpy.ops.object.join()
    combined_cutter = bpy.context.active_object
    combined_cutter.name = "Modifier_Cylinders_Cutter"
    return combined_cutter


def apply_pre_slice_modifiers(guitar_body, modifiers_cfg):
    """
    Applies sphere chunks and cylinder perforation modifiers to the guitar body
    prior to physical part slicing.
    """
    if not modifiers_cfg:
        return

    # Check if either master or individual mode is enabled
    spheres_enabled = modifiers_cfg.get("spheres", {}).get("enabled", False)
    cyls_enabled = modifiers_cfg.get("cylinders", {}).get("enabled", False)
    if not (modifiers_cfg.get("enabled", False) or spheres_enabled or cyls_enabled):
        return

    keepout_cfg = modifiers_cfg.get("keepout", {})

    # Extract dynamic cavity exclusion zones from backplates if not already populated
    if "exclusion_boxes" not in keepout_cfg or not keepout_cfg["exclusion_boxes"]:
        cavity_margin = float(keepout_cfg.get("margin", 1.2))
        keepout_cfg["exclusion_boxes"] = extract_cavity_exclusion_boxes(margin=cavity_margin)

    # 1. Sphere Chunks Modifier
    if spheres_enabled:
        log("Applying Sphere Chunks Modifier...")
        cutter = generate_spheres_cutter(guitar_body, modifiers_cfg.get("spheres", {}), keepout_cfg)
        if cutter:
            apply_boolean_difference(guitar_body, cutter, name="Mod_Spheres_Diff")
            bpy.data.objects.remove(cutter, do_unlink=True)

    # 2. Angled Cylinders Modifier
    if cyls_enabled:
        log("Applying Angled Cylinders Modifier...")
        cutter = generate_cylinders_cutter(guitar_body, modifiers_cfg.get("cylinders", {}), keepout_cfg)
        if cutter:
            apply_boolean_difference(guitar_body, cutter, name="Mod_Cylinders_Diff")
            bpy.data.objects.remove(cutter, do_unlink=True)


def keep_largest_component(obj):
    """
    Cleans up any detached loose floating artifacts directly in-place in obj.data,
    guaranteeing obj remains a single connected manifold mesh without creating
    or deleting Blender objects.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    visited = set()
    islands = []
    for v in bm.verts:
        if v not in visited:
            island = []
            queue = [v]
            visited.add(v)
            while queue:
                curr = queue.pop()
                island.append(curr)
                for edge in curr.link_edges:
                    other = edge.other_vert(curr)
                    if other not in visited:
                        visited.add(other)
                        queue.append(other)
            islands.append(island)

    if len(islands) > 1:
        islands.sort(key=len, reverse=True)
        verts_to_delete = []
        for small_island in islands[1:]:
            verts_to_delete.extend(small_island)
        bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
        bm.to_mesh(obj.data)
        obj.data.update()
        log(f"Cleaned up {len(islands)-1} detached loose islands ({len(verts_to_delete)} vertices) from {obj.name}.")
    bm.free()


def create_organic_profile_cutter(obj, wall_thickness=1.2, is_shoulder_piece=False, style="through", floor_thickness=0.4):
    """
    Creates an organic extruded prism cutter following the exact 2D perimeter of the piece,
    enforcing true 2D Euclidean clearance against the boundary to ensure structural integrity
    at cutaway dips, neck joint cantilevers, and thin horn areas.
    """
    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    min_x, max_x = min(v.x for v in bbox), max(v.x for v in bbox)
    min_y, max_y = min(v.y for v in bbox), max(v.y for v in bbox)
    min_z, max_z = min(v.z for v in bbox), max(v.z for v in bbox)
    dx = max_x - min_x
    dy = max_y - min_y
    cz = (min_z + max_z) / 2.0

    if dx <= wall_thickness * 2.2 or dy <= wall_thickness * 2.2:
        return None

    # Sample 2D perimeter at Z=cz
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    local_zno = (obj.matrix_world.inverted().to_3x3() @ Vector((0, 0, 1.0))).normalized()
    res = bmesh.ops.bisect_plane(
        bm,
        geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=obj.matrix_world.inverted() @ Vector((0, 0, cz)),
        plane_no=local_zno
    )
    cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    boundary_pts = []
    for e in cut_edges:
        for v in e.verts:
            p = obj.matrix_world @ v.co
            boundary_pts.append((p.x, p.y))
    bm.free()

    if not boundary_pts:
        return None

    # Margins: shoulder cutaway dips require >= 1.8cm clearance for structural integrity
    if is_shoulder_piece:
        dip_margin = max(wall_thickness, 1.8)
        outer_margin = wall_thickness
        min_cut_y = min_y + wall_thickness
        max_cut_y = min(max_y - 2.0, 38.0)  # Keep upper horn tip 100% solid
    else:
        dip_margin = wall_thickness
        outer_margin = wall_thickness
        min_cut_y = min_y + wall_thickness
        max_cut_y = max_y - wall_thickness

    if max_cut_y <= min_cut_y:
        return None

    import numpy as np
    y_samples = np.linspace(min_cut_y, max_cut_y, 50)
    left_pts = []
    right_pts = []

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    for y_val in y_samples:
        local_pt = obj.matrix_world.inverted() @ Vector((0, y_val, 0))
        local_no = (obj.matrix_world.inverted().to_3x3() @ Vector((0, 1.0, 0))).normalized()
        res = bmesh.ops.bisect_plane(
            bm,
            geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=local_pt,
            plane_no=local_no
        )
        c_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
        if not c_edges:
            continue
        xs = [(obj.matrix_world @ v.co).x for e in c_edges for v in e.verts]
        if not xs:
            continue
        x_min, x_max = min(xs), max(xs)
        xl = x_min + outer_margin
        xr = x_max - outer_margin
        xc = (x_min + x_max) / 2.0

        for bx, by in boundary_pts:
            dy_pt = abs(y_val - by)
            if obj.name == "Guitar_Top_Left":
                # Inner dip is on right (bx > xc, towards center)
                if bx > xc and dy_pt < dip_margin:
                    needed_dx = math.sqrt(dip_margin**2 - dy_pt**2)
                    limit_x = bx - needed_dx
                    if limit_x < xr:
                        xr = limit_x
                # Outer contour is on left (bx < xc)
                elif bx < xc and dy_pt < outer_margin:
                    needed_dx = math.sqrt(outer_margin**2 - dy_pt**2)
                    limit_x = bx + needed_dx
                    if limit_x > xl:
                        xl = limit_x
            elif obj.name == "Guitar_Top_Right":
                # Inner dip is on left (bx < xc, towards center)
                if bx < xc and dy_pt < dip_margin:
                    needed_dx = math.sqrt(dip_margin**2 - dy_pt**2)
                    limit_x = bx + needed_dx
                    if limit_x > xl:
                        xl = limit_x
                # Outer contour is on right (bx > xc)
                elif bx > xc and dy_pt < outer_margin:
                    needed_dx = math.sqrt(outer_margin**2 - dy_pt**2)
                    limit_x = bx - needed_dx
                    if limit_x < xr:
                        xr = limit_x
            else:
                if bx > xc and dy_pt < outer_margin:
                    needed_dx = math.sqrt(outer_margin**2 - dy_pt**2)
                    limit_x = bx - needed_dx
                    if limit_x < xr:
                        xr = limit_x
                elif bx < xc and dy_pt < outer_margin:
                    needed_dx = math.sqrt(outer_margin**2 - dy_pt**2)
                    limit_x = bx + needed_dx
                    if limit_x > xl:
                        xl = limit_x

        if xr - xl > 0.4:
            left_pts.append((xl, y_val))
            right_pts.append((xr, y_val))
    bm.free()

    if len(left_pts) < 3:
        return None

    poly_pts = left_pts + right_pts[::-1]
    bm2 = bmesh.new()
    z_bottom = (min_z + floor_thickness) if style == "pocket" else (min_z - 1.0)
    z_top = max_z + 1.0

    poly_verts = [bm2.verts.new((x, y, z_bottom)) for x, y in poly_pts]
    face = bm2.faces.new(poly_verts)
    bm2.faces.ensure_lookup_table()
    if face.normal.z < 0:
        face.normal_flip()

    extrude_res = bmesh.ops.extrude_face_region(bm2, geom=[face])
    for v in extrude_res['geom']:
        if isinstance(v, bmesh.types.BMVert):
            v.co.z = z_top
    bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces[:])

    cutter_mesh = bpy.data.meshes.new(f"{obj.name}_FrameCutterMesh")
    bm2.to_mesh(cutter_mesh)
    cutter = bpy.data.objects.new(f"{obj.name}_FrameCutter", cutter_mesh)
    bpy.context.collection.objects.link(cutter)
    bm2.free()
    return cutter


def apply_post_slice_modifiers(part_names, modifiers_cfg):
    """
    Applies post-split edge frame / exoskeleton modifier to outer guitar pieces,
    removing interior volume to leave a cut-out shape with a strong structural frame.
    
    Strictly preserves:
    - Central structural spine (Guitar_Mid, Guitar_Top_Mid) 100% solid.
    - Combined electronics region + backplate: completely protected so cavity walls,
      potentiometers, switches, and backplate screw mounting rim remain 100% solid.
    - Shoulder cutouts (Guitar_Top_Left & Guitar_Top_Right): framed with reinforced cutouts
      in the upper bout while maintaining full structural integrity around the cutaways,
      neck joint roots, and locator pin mating faces.
    """
    if not modifiers_cfg:
        return

    frame_cfg = modifiers_cfg.get("edge_frame", {})
    if not (modifiers_cfg.get("enabled", False) or frame_cfg.get("enabled", False)):
        return
    if not frame_cfg.get("enabled", False):
        return

    wall_thickness = float(frame_cfg.get("wall_thickness", 1.2))  # cm
    style = frame_cfg.get("style", "through")  # "through" or "pocket"
    floor_thickness = float(frame_cfg.get("floor_thickness", 0.4))  # cm
    apply_to = frame_cfg.get("apply_to", "outer_wings")

    # Central structural spine pieces MUST ALWAYS remain 100% solid
    protected_core_parts = {"Guitar_Mid", "Guitar_Top_Mid"}

    target_parts = []
    for pname in part_names:
        if pname in protected_core_parts:
            log(f"Preserving piece '{pname}' (100% solid structural core).")
            continue
        obj = bpy.data.objects.get(pname)
        if obj and obj.type == 'MESH':
            target_parts.append(obj)

    keepout_cfg = modifiers_cfg.get("keepout", {})
    exclusion_boxes = keepout_cfg.get("exclusion_boxes", [])
    if not exclusion_boxes:
        cavity_margin = float(keepout_cfg.get("margin", 1.2))
        exclusion_boxes = extract_cavity_exclusion_boxes(margin=cavity_margin)

    log(f"Applying Edge Frame Modifier to {len(target_parts)} post-split pieces (wall {wall_thickness*10:.0f}mm, style '{style}')...")

    for obj in target_parts:
        try:
            bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
            min_x = min(v.x for v in bbox)
            max_x = max(v.x for v in bbox)
            min_y = min(v.y for v in bbox)
            max_y = max(v.y for v in bbox)
            min_z = min(v.z for v in bbox)
            max_z = max(v.z for v in bbox)

            dx = max_x - min_x
            dy = max_y - min_y
            dz = max_z - min_z
            cx = (min_x + max_x) / 2.0
            cy = (min_y + max_y) / 2.0
            cz = (min_z + max_z) / 2.0

            # Only frame pieces that are wide and tall enough to support an inner window
            if dx <= wall_thickness * 2.2 or dy <= wall_thickness * 2.2:
                log(f"Skipping piece '{obj.name}': dimensions ({dx:.1f}x{dy:.1f}cm) too small for frame.")
                continue

            is_shoulder_piece = obj.name in ["Guitar_Top_Left", "Guitar_Top_Right"]
            if is_shoulder_piece:
                cutter = create_organic_profile_cutter(
                    obj,
                    wall_thickness=wall_thickness,
                    is_shoulder_piece=True,
                    style=style,
                    floor_thickness=floor_thickness
                )
                if not cutter:
                    log(f"Preserving piece '{obj.name}' (profile cutter could not find safe volume).")
                    continue
            else:
                # Duplicate object to create an inset frame cutter following the piece's organic silhouette
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.duplicate()
                cutter = bpy.context.active_object
                cutter.name = f"{obj.name}_FrameCutter"

                sx = max(0.1, (dx - 2.0 * wall_thickness) / dx)
                sy = max(0.1, (dy - 2.0 * wall_thickness) / dy)

                for v in cutter.data.vertices:
                    world_co = cutter.matrix_world @ v.co
                    rel_x = world_co.x - cx
                    rel_y = world_co.y - cy
                    new_x = cx + rel_x * sx
                    new_y = cy + rel_y * sy

                    if style == "pocket":
                        new_z = (min_z + floor_thickness) + (world_co.z - min_z) * 1.5
                    else:
                        new_z = cz + (world_co.z - cz) * 1.6
                    v.co = cutter.matrix_world.inverted() @ Vector((new_x, new_y, new_z))
                cutter.data.update()

            # CRITICAL: Respect combined electronics cavity + backplate exclusion zone!
            # If cutter overlaps the electronics exclusion zone, subtract it from the cutter!
            c_bbox = [cutter.matrix_world @ Vector(v) for v in cutter.bound_box]
            c_min_x, c_max_x = min(v.x for v in c_bbox), max(v.x for v in c_bbox)
            c_min_y, c_max_y = min(v.y for v in c_bbox), max(v.y for v in c_bbox)

            for ex in exclusion_boxes:
                if (c_min_x <= ex["max_x"] and c_max_x >= ex["min_x"] and
                    c_min_y <= ex["max_y"] and c_max_y >= ex["min_y"]):
                    log(f"Exoskeleton cutter for '{obj.name}' overlaps '{ex['name']}'. Subtracting exclusion zone to preserve cavity & backplate...")
                    ex_cx = (ex["min_x"] + ex["max_x"]) / 2.0
                    ex_cy = (ex["min_y"] + ex["max_y"]) / 2.0
                    ex_cz = cz
                    ex_dx = ex["max_x"] - ex["min_x"]
                    ex_dy = ex["max_y"] - ex["min_y"]
                    ex_dz = dz * 2.0
                    bpy.ops.mesh.primitive_cube_add(
                        size=1.0,
                        location=(ex_cx, ex_cy, ex_cz),
                        scale=(ex_dx, ex_dy, ex_dz)
                    )
                    ex_tool = bpy.context.active_object
                    apply_boolean_difference(cutter, ex_tool, name=f"Protect_{obj.name}")
                    bpy.data.objects.remove(ex_tool, do_unlink=True)

            # Check if cutter still has usable volume
            c_bbox2 = [cutter.matrix_world @ Vector(v) for v in cutter.bound_box]
            rem_dx = max(v.x for v in c_bbox2) - min(v.x for v in c_bbox2)
            rem_dy = max(v.y for v in c_bbox2) - min(v.y for v in c_bbox2)
            if rem_dx < wall_thickness * 1.5 or rem_dy < wall_thickness * 1.5 or len(cutter.data.vertices) < 8:
                log(f"Preserving piece '{obj.name}' 100% solid to protect the combined electronics region & backplate mounting integrity.")
                bpy.data.objects.remove(cutter, do_unlink=True)
                continue

            # Apply boolean subtraction to piece
            success = apply_boolean_difference(obj, cutter, name=f"Frame_{obj.name}")
            bpy.data.objects.remove(cutter, do_unlink=True)

            if success:
                keep_largest_component(obj)
                log(f"Successfully framed piece '{obj.name}'.")

        except Exception as e:
            log(f"Error applying edge frame to '{obj.name}': {e}")
