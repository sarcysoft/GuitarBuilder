import os
import sys
import random
import argparse
import math

try:
    import bpy
    inside_blender = True
except ImportError:
    inside_blender = False

# Fallback color dictionary
COLORS = {
    "red": (0.65, 0.01, 0.02, 1.0),
    "blue": (0.01, 0.2, 0.7, 1.0),
    "gold": (0.75, 0.55, 0.08, 1.0),
    "chrome": (0.85, 0.85, 0.85, 1.0),
    "silver": (0.85, 0.85, 0.85, 1.0),
    "black": (0.02, 0.02, 0.02, 1.0),
    "white": (0.95, 0.95, 0.95, 1.0),
    "green": (0.02, 0.5, 0.1, 1.0),
    "orange": (0.8, 0.3, 0.02, 1.0),
    "purple": (0.3, 0.02, 0.5, 1.0),
    "yellow": (0.9, 0.7, 0.02, 1.0)
}


def parse_color(color_str):
    """Parse color string into RGBA tuple."""
    color_str = color_str.lower().strip()
    if color_str in COLORS:
        return COLORS[color_str]
    # Check if hex format (e.g. #ff0000)
    if color_str.startswith("#"):
        hex_val = color_str.lstrip('#')
        try:
            r = int(hex_val[0:2], 16) / 255.0
            g = int(hex_val[2:4], 16) / 255.0
            b = int(hex_val[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        except Exception:
            pass
    # Default fallback to grey
    return (0.5, 0.5, 0.5, 1.0)


def purge_scene():
    """Remove default objects, cameras, and lights from the scene."""
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clean up orphaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)


def get_principled_bsdf(nodes):
    """Retrieve the Principled BSDF node from a node tree (compatible with Blender 3.x and 4.x/5.x)."""
    for n in nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


def get_or_create_satin_maple():
    """Create a satin maple wood material."""
    name = "Satin Maple"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
        
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = get_principled_bsdf(nodes)
    if principled:
        principled.inputs[0].default_value = (0.9, 0.8, 0.65, 1.0)  # Base Color
        # Roughness
        rough_input = principled.inputs.get("Roughness")
        if rough_input:
            rough_input.default_value = 0.4
    return mat


def create_glossy(name="Glossy Paint", color=(0.65, 0.01, 0.02, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = color
        p.inputs.get("Roughness").default_value = 0.08
        if "Metallic" in p.inputs:
            p.inputs["Metallic"].default_value = 0.3
        elif "Metallic Weight" in p.inputs:
            p.inputs["Metallic Weight"].default_value = 0.3
        if "Coat" in p.inputs:
            p.inputs["Coat"].default_value = 1.0
        elif "Clearcoat" in p.inputs:
            p.inputs["Clearcoat"].default_value = 1.0
        if "Coat Roughness" in p.inputs:
            p.inputs["Coat Roughness"].default_value = 0.05
        elif "Clearcoat Roughness" in p.inputs:
            p.inputs["Clearcoat Roughness"].default_value = 0.05
    return mat


def create_gold_top():
    mat = bpy.data.materials.new(name="Gold Top")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = (0.75, 0.55, 0.08, 1.0)
        p.inputs.get("Roughness").default_value = 0.15
        if "Metallic" in p.inputs:
            p.inputs["Metallic"].default_value = 0.85
        elif "Metallic Weight" in p.inputs:
            p.inputs["Metallic Weight"].default_value = 0.85
        if "Coat" in p.inputs:
            p.inputs["Coat"].default_value = 1.0
        elif "Clearcoat" in p.inputs:
            p.inputs["Clearcoat"].default_value = 1.0
    return mat


def create_polished_chrome(name="Polished Chrome", color=(0.85, 0.85, 0.85, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = color
        p.inputs.get("Roughness").default_value = 0.05
        if "Metallic" in p.inputs:
            p.inputs["Metallic"].default_value = 1.0
        elif "Metallic Weight" in p.inputs:
            p.inputs["Metallic Weight"].default_value = 1.0
    return mat


def create_transparent_glass(name="Transparent Glass", color=(1.0, 1.0, 1.0, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # EEVEE Glass settings
    try:
        mat.blend_method = 'HASHED'
    except AttributeError:
        pass
    try:
        mat.shadow_method = 'HASHED'
    except AttributeError:
        pass
    try:
        mat.use_screen_refraction = True
    except AttributeError:
        pass
    try:
        mat.refraction_depth = 0.05
    except AttributeError:
        pass
        
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = color  # Base Color
        p.inputs.get("Roughness").default_value = 0.02
        p.inputs.get("IOR").default_value = 1.45
        
        # In Blender 4.0+ EEVEE/Cycles, Transmission Weight is used
        if "Transmission" in p.inputs:
            p.inputs["Transmission"].default_value = 1.0
        elif "Transmission Weight" in p.inputs:
            p.inputs["Transmission Weight"].default_value = 1.0
            
    return mat


def create_sunburst(name="Sunburst Lacquer", center_color=(0.9, 0.7, 0.08, 1.0), mid_color=(0.65, 0.02, 0.02, 1.0), outer_color=(0.02, 0.02, 0.02, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Purge connection to base color
    p = get_principled_bsdf(nodes)
    if not p:
        return mat
        
    p.inputs.get("Roughness").default_value = 0.08
    if "Coat" in p.inputs:
        p.inputs["Coat"].default_value = 1.0
    elif "Clearcoat" in p.inputs:
        p.inputs["Clearcoat"].default_value = 1.0
        
    # Create nodes for radial gradient
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    
    mapping = nodes.new(type="ShaderNodeMapping")
    mapping.name = "Sunburst_Mapping"
    
    vec_math = nodes.new(type="ShaderNodeVectorMath")
    vec_math.operation = 'LENGTH'
    
    # Map range to scale distance
    map_range = nodes.new(type="ShaderNodeMapRange")
    map_range.name = "Sunburst_MapRange"
    map_range.inputs[1].default_value = 0.0   # From Min
    map_range.inputs[2].default_value = 18.0  # From Max (approximate guitar hip radius fallback)
    map_range.inputs[3].default_value = 0.0   # To Min
    map_range.inputs[4].default_value = 1.0   # To Max
    
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.interpolation = 'B_SPLINE'
    
    # Sunburst color steps: Center -> Mid -> Outer
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = center_color
    
    # Add Middle color
    el_mid = color_ramp.color_ramp.elements.new(position=0.45)
    el_mid.color = mid_color
    
    color_ramp.color_ramp.elements[-1].position = 0.85
    color_ramp.color_ramp.elements[-1].color = outer_color
    
    # Link up nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], vec_math.inputs[0])
    links.new(vec_math.outputs['Value'], map_range.inputs[0])
    links.new(map_range.outputs['Result'], color_ramp.inputs[0])
    links.new(color_ramp.outputs['Color'], p.inputs[0])
    
    return mat


def configure_sunburst_material(mat):
    """Automatically centers and scales the sunburst texture coordinates based on body bounding box."""
    if not mat or not mat.use_nodes:
        return
        
    mapping = mat.node_tree.nodes.get("Sunburst_Mapping")
    map_range = mat.node_tree.nodes.get("Sunburst_MapRange")
    
    if not mapping or not map_range:
        return
        
    # Find all body meshes in the scene
    body_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name.startswith("Guitar_") and obj.name != "Ground_Plane"]
    if not body_objs:
        return
        
    import mathutils
    world_coords = []
    for obj in body_objs:
        for v in obj.bound_box:
            world_coords.append(obj.matrix_world @ mathutils.Vector(v))
            
    min_x = min(w[0] for w in world_coords)
    max_x = max(w[0] for w in world_coords)
    min_y = min(w[1] for w in world_coords)
    max_y = max(w[1] for w in world_coords)
    min_z = min(w[2] for w in world_coords)
    max_z = max(w[2] for w in world_coords)
    
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0
    
    size_x = max_x - min_x
    size_y = max_y - min_y
    
    # Set Mapping Translation (moves center of gradient to center of body)
    try:
        loc_input = mapping.inputs.get('Location') or mapping.inputs[1]
        loc_input.default_value = (-center_x, -center_y, -center_z)
    except Exception as e:
        print(f"Error setting mapping Location: {e}")
        
    # Set Mapping Scale (adjusts Y scale to make the radial gradient elliptical matching body proportions)
    try:
        scale_input = mapping.inputs.get('Scale') or mapping.inputs[3]
        if size_y > 0 and size_x > 0:
            scale_input.default_value = (1.0, size_x / size_y, 1.0)
    except Exception as e:
        print(f"Error setting mapping Scale: {e}")
        
    # Set Map Range From Max (radius of the sunburst fits half the body width)
    try:
        map_range.inputs[2].default_value = size_x / 2.0
    except Exception as e:
        print(f"Error setting map range From Max: {e}")


def create_sparkle(name, main_color_rgb, sparkle_color_rgb):
    """Create a sparkling/glitter metallic shader with custom base and flake colors."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    p = get_principled_bsdf(nodes)
    if not p:
        return mat
        
    p.inputs.get("Roughness").default_value = 0.15
    if "Metallic" in p.inputs:
        p.inputs["Metallic"].default_value = 0.8
    elif "Metallic Weight" in p.inputs:
        p.inputs["Metallic Weight"].default_value = 0.8
    if "Coat" in p.inputs:
        p.inputs["Coat"].default_value = 1.0
    elif "Clearcoat" in p.inputs:
        p.inputs["Clearcoat"].default_value = 1.0
        
    # High-frequency noise for sparkles
    voronoi = nodes.new(type="ShaderNodeTexVoronoi")
    voronoi.inputs[2].default_value = 800.0  # Scale
    
    # Sharp threshold mask
    map_range = nodes.new(type="ShaderNodeMapRange")
    map_range.inputs[1].default_value = 0.00
    map_range.inputs[2].default_value = 0.05  # Select only center cores of cells
    map_range.inputs[3].default_value = 1.0
    map_range.inputs[4].default_value = 0.0
    
    # Mix node to interpolate color
    mix = nodes.new(type="ShaderNodeMix")
    mix.data_type = 'RGBA'
    mix.blend_type = 'MIX'
    try:
        mix.inputs[4].default_value = main_color_rgb[:3]
        mix.inputs[5].default_value = sparkle_color_rgb[:3]
    except Exception:
        try:
            mix.inputs[4].default_value = main_color_rgb
            mix.inputs[5].default_value = sparkle_color_rgb
        except Exception:
            pass
    
    # Bump node to perturb normals to create shimmering highlights
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs[0].default_value = 0.6  # Strength
    bump.inputs[1].default_value = 0.01 # Distance
    
    # Connections
    links.new(voronoi.outputs['Distance'], map_range.inputs[0])
    links.new(map_range.outputs['Result'], mix.inputs[0])
    links.new(mix.outputs[2], p.inputs[0])  # Connect Mix output to Base Color
    
    # Connect voronoi to bump normal
    links.new(voronoi.outputs['Distance'], bump.inputs[2])
    links.new(bump.outputs['Normal'], p.inputs['Normal'])
    
    return mat


def get_material_by_name(mat_name):
    """Retrieve or construct a material based on the parsed name."""
    mat_name = mat_name.lower().strip()
    
    if mat_name.startswith("gloss"):
        # Format: gloss or gloss:color
        parts = mat_name.split(":")
        color = (0.65, 0.01, 0.02, 1.0)  # default candy apple red
        name = "Glossy Paint"
        if len(parts) >= 2:
            color = parse_color(parts[1])
            name = f"Glossy {parts[1]}"
        return create_glossy(name, color)
    elif mat_name == "red":
        return create_glossy("Glossy Red", (0.65, 0.01, 0.02, 1.0))
    elif mat_name == "blue":
        return create_glossy("Glossy Blue", (0.01, 0.2, 0.7, 1.0))
    elif mat_name == "gold":
        return create_gold_top()
    elif mat_name.startswith("chrome") or mat_name.startswith("silver"):
        # Format: chrome or chrome:color
        parts = mat_name.split(":")
        color = (0.85, 0.85, 0.85, 1.0)  # default silver
        name = "Polished Chrome"
        if len(parts) >= 2:
            color = parse_color(parts[1])
            name = f"Chrome {parts[1]}"
        return create_polished_chrome(name, color)
    elif mat_name == "black":
        return create_glossy("Glossy Black", (0.02, 0.02, 0.02, 1.0))
    elif mat_name.startswith("glass"):
        # Format: glass or glass:color
        parts = mat_name.split(":")
        color = (1.0, 1.0, 1.0, 1.0)  # default white/clear
        name = "Transparent Glass"
        if len(parts) >= 2:
            color = parse_color(parts[1])
            name = f"Glass {parts[1]}"
        return create_transparent_glass(name, color)
    elif mat_name.startswith("sunburst"):
        # Format: sunburst or sunburst:center or sunburst:center:mid or sunburst:center:mid:outer
        parts = mat_name.split(":")
        center = (0.9, 0.7, 0.08, 1.0)
        mid = (0.65, 0.02, 0.02, 1.0)
        outer = (0.02, 0.02, 0.02, 1.0)
        name = "Sunburst Lacquer"
        
        if len(parts) >= 2:
            center = parse_color(parts[1])
            name = f"Sunburst {parts[1]}"
        if len(parts) >= 3:
            mid = parse_color(parts[2])
            name += f"-{parts[2]}"
        if len(parts) >= 4:
            outer = parse_color(parts[3])
            name += f"-{parts[3]}"
            
        return create_sunburst(name, center, mid, outer)
    elif mat_name.startswith("sparkle"):
        # Format: sparkle or sparkle:main_color:sparkle_color
        parts = mat_name.split(":")
        main_color = (0.65, 0.01, 0.02, 1.0)  # default red
        sparkle_color = (0.75, 0.55, 0.08, 1.0)  # default gold
        name = "Sparkle Red-Gold"
        
        if len(parts) >= 2:
            main_color = parse_color(parts[1])
            name = f"Sparkle {parts[1]}"
        if len(parts) >= 3:
            sparkle_color = parse_color(parts[2])
            name += f"-{parts[2]}"
            
        return create_sparkle(name, main_color, sparkle_color)
    else:
        # Fallback to default gloss (red)
        return create_glossy()


def check_and_apply_neck_material(neck_obj):
    """Checks if the neck has valid materials loaded. If not, applies Satin Maple."""
    has_valid_material = False
    for slot in neck_obj.material_slots:
        if slot.material and slot.material.name not in ["Material", "Default", ""]:
            # If the material uses nodes and has more than 2 nodes, assume it has textures/details
            if slot.material.use_nodes and len(slot.material.node_tree.nodes) > 2:
                has_valid_material = True
                break
            elif not slot.material.use_nodes:
                # If not using nodes, verify it's not default white
                if slot.material.diffuse_color[:3] != (1.0, 1.0, 1.0):
                    has_valid_material = True
                    break
                    
    if not has_valid_material:
        print("No valid material detected on imported neck. Applying Satin Maple fallback...")
        maple_mat = get_or_create_satin_maple()
        if len(neck_obj.material_slots) == 0:
            neck_obj.data.materials.append(maple_mat)
        else:
            for i in range(len(neck_obj.material_slots)):
                neck_obj.material_slots[i].material = maple_mat


def import_stl(filepath, name, material=None, scale_factor=1.0):
    """Helper to import an STL and assign a material."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return None
        
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    try:
        if hasattr(bpy.ops.wm, 'stl_import'):
            bpy.ops.wm.stl_import(filepath=filepath)
        else:
            bpy.ops.import_mesh.stl(filepath=filepath)
            
        imported_obj = bpy.context.active_object
        if imported_obj:
            imported_obj.name = name
            
            # Apply scale factor if needed (e.g. 0.1 to offset 10x export scale)
            if scale_factor != 1.0:
                imported_obj.scale = (scale_factor, scale_factor, scale_factor)
                bpy.ops.object.select_all(action='DESELECT')
                imported_obj.select_set(True)
                bpy.context.view_layer.objects.active = imported_obj
                bpy.ops.object.transform_apply(scale=True)
                
            if material:
                if len(imported_obj.material_slots) == 0:
                    imported_obj.data.materials.append(material)
                else:
                    imported_obj.material_slots[0].material = material
            return imported_obj
    except Exception as e:
        print(f"Error importing STL {filepath}: {e}")
    return None


def import_obj(filepath, name, rotation_x=0, rotation_y=0, rotation_z=0, offset_x=0, offset_y=0, offset_z=0):
    """Helper to import an OBJ and apply transforms."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return None
        
    bpy.ops.object.select_all(action='DESELECT')
    
    try:
        if hasattr(bpy.ops.wm, 'obj_import'):
            bpy.ops.wm.obj_import(filepath=filepath)
        else:
            bpy.ops.export_scene.obj(filepath=filepath)
            
        imported_obj = bpy.context.active_object
        if imported_obj:
            imported_obj.name = name
            
            imported_obj.rotation_mode = 'XYZ'
            if rotation_x != 0:
                imported_obj.rotation_euler[0] += math.radians(rotation_x)
            if rotation_y != 0:
                imported_obj.rotation_euler[1] += math.radians(rotation_y)
            if rotation_z != 0:
                imported_obj.rotation_euler[2] += math.radians(rotation_z)
                
            imported_obj.location.x += offset_x
            imported_obj.location.y += offset_y
            imported_obj.location.z += offset_z
            
            bpy.context.view_layer.update()
            return imported_obj
    except Exception as e:
        print(f"Error importing OBJ {filepath}: {e}")
    return None


def setup_lighting(theme, target_y=36.0):
    """Build a lighting system based on a custom theme/feel.
    
    Uses a 3-point lighting rig designed to work correctly for front, back
    and angled camera views. Lights are positioned to rake across the
    guitar surface (side-lighting) so detail and depth are visible from
    all angles, including the top-down front/back views.
    """
    scene = bpy.context.scene
    
    # Purge any existing lights
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # ------------------------------------------------------------------ #
    # Key light — raking from upper-left side (Y-right, Z-up space)
    # Position is offset hard to the -X side so it strikes the guitar
    # surface at an angle in the XZ plane, creating good shadow depth.
    # ------------------------------------------------------------------ #
    key_data = bpy.data.lights.new(name="Key Light", type='AREA')
    key_obj = bpy.data.objects.new(name="Key Light", object_data=key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (-60.0, target_y - 5.0, 55.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(-40), 0)
    key_data.size = 12.0   # Smaller = harder shadows = more detail

    # ------------------------------------------------------------------ #
    # Fill light — opposite side, much weaker, softens harsh shadows
    # ------------------------------------------------------------------ #
    fill_data = bpy.data.lights.new(name="Fill Light", type='AREA')
    fill_obj = bpy.data.objects.new(name="Fill Light", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (55.0, target_y - 5.0, 35.0)
    fill_obj.rotation_euler = (math.radians(50), math.radians(45), 0)
    fill_data.size = 20.0

    # ------------------------------------------------------------------ #
    # Rim light — behind and above guitar to create edge definition and
    # separate the guitar from the background in back views
    # ------------------------------------------------------------------ #
    rim_data = bpy.data.lights.new(name="Rim Light", type='AREA')
    rim_obj = bpy.data.objects.new(name="Rim Light", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (15.0, target_y + 55.0, 30.0)
    rim_obj.rotation_euler = (math.radians(-50), math.radians(15), math.radians(175))
    rim_data.size = 15.0

    # ------------------------------------------------------------------ #
    # Top overhead soft-box — provides base illumination so the front/
    # back orthographic-style views don't go dark. Much weaker than key.
    # ------------------------------------------------------------------ #
    top_data = bpy.data.lights.new(name="Top Fill", type='AREA')
    top_obj = bpy.data.objects.new(name="Top Fill", object_data=top_data)
    bpy.context.collection.objects.link(top_obj)
    top_obj.location = (0.0, target_y, 90.0)
    top_obj.rotation_euler = (0, 0, 0)
    top_data.size = 80.0   # Very large soft-box for even overhead fill

    # ------------------------------------------------------------------ #
    # World background — subtle ambient bounce that matches theme color.
    # Keep strength low (0.15–0.3) so it doesn't wash out the scene.
    # ------------------------------------------------------------------ #
    bg_colors = {
        "dramatic": (0.04, 0.02, 0.08),
        "warm":     (0.12, 0.08, 0.04),
        "sunset":   (0.06, 0.02, 0.09),
        "studio":   (0.62, 0.62, 0.62),  # proper mid-grey studio background
    }
    bg_strength = {
        "dramatic": 0.18,
        "warm":     0.25,
        "sunset":   0.18,
        "studio":   0.60,  # studio needs bright background to feel like a studio
    }
    bg_color  = bg_colors.get(theme, (0.55, 0.55, 0.55))
    bg_str    = bg_strength.get(theme, 0.25)
    
    if scene.world:
        scene.world.use_nodes = True
        wnt = scene.world.node_tree
        bg_node = wnt.nodes.get("Background")
        if bg_node:
            bg_node.inputs[0].default_value = (*bg_color, 1.0)
            bg_node.inputs[1].default_value = bg_str

    # ------------------------------------------------------------------ #
    # Per-theme energies and colors
    # ------------------------------------------------------------------ #
    if theme == "dramatic":
        # Theatrical cyan-key / magenta-rim contrast lighting
        key_data.energy  = 12000.0
        key_data.color   = (0.15, 0.85, 1.0)   # Icy cyan

        fill_data.energy = 1500.0
        fill_data.color  = (1.0, 0.9, 1.0)     # Near-white

        rim_data.energy  = 14000.0
        rim_data.color   = (1.0, 0.05, 0.75)   # Hot magenta

        top_data.energy  = 800.0
        top_data.color   = (0.6, 0.4, 1.0)     # Subtle violet overhead

    elif theme == "warm":
        # Soft amber studio with warm overhead
        key_data.energy  = 10000.0
        key_data.color   = (1.0, 0.78, 0.45)   # Amber

        fill_data.energy = 2500.0
        fill_data.color  = (1.0, 0.88, 0.65)

        rim_data.energy  = 6000.0
        rim_data.color   = (1.0, 0.96, 0.88)   # Warm white

        top_data.energy  = 4000.0
        top_data.color   = (1.0, 0.9, 0.75)

    elif theme == "sunset":
        # Sunset orange key, violet rim
        key_data.energy  = 12000.0
        key_data.color   = (1.0, 0.45, 0.08)   # Orange sun

        fill_data.energy = 1200.0
        fill_data.color  = (0.85, 0.2, 0.45)   # Pink

        rim_data.energy  = 11000.0
        rim_data.color   = (0.25, 0.0, 0.85)   # Deep violet

        top_data.energy  = 800.0
        top_data.color   = (1.0, 0.5, 0.3)

    else:  # studio — clean neutral photography-style rig
        # Key rakes across body for shadows / material detail
        key_data.energy  = 9000.0
        key_data.color   = (1.0, 1.0, 1.0)

        # Moderate fill to keep shadow side visible without killing contrast
        fill_data.energy = 2500.0
        fill_data.color  = (0.95, 0.98, 1.0)   # Slightly cool fill

        # Rim adds edge separation, helps back view pop
        rim_data.energy  = 5000.0
        rim_data.color   = (1.0, 1.0, 1.0)

        # Top soft-box is the main diffuse fill for front/back views
        top_data.energy  = 8000.0
        top_data.color   = (1.0, 1.0, 1.0)
def create_ground_plane(target_y, theme):
    """Add a large ground plane to catch shadows and reflections."""
    # Purge any existing ground plane
    for obj in list(bpy.data.objects):
        if obj.name == "Ground_Plane":
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # Create plane mesh
    bpy.ops.mesh.primitive_plane_add(size=1000.0, location=(0.0, target_y, -30.0))
    plane_obj = bpy.context.active_object
    plane_obj.name = "Ground_Plane"
    
    # Create material for ground plane
    mat_name = f"Studio_Floor_{theme}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        p = get_principled_bsdf(nodes)
        if p:
            # Procedural concrete/brushed texture coordinate
            tex_coord = nodes.new(type="ShaderNodeTexCoord")
            
            # Procedural noise texture for concrete grain
            noise = nodes.new(type="ShaderNodeTexNoise")
            noise.inputs['Scale'].default_value = 0.8  # larger features in world space (0.8 scale matches visual resolution)
            noise.inputs['Detail'].default_value = 15.0  # high frequency detail
            noise.inputs['Roughness'].default_value = 0.7
            
            # Connect texture coordinate to noise vector
            links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
            
            # Color Ramp for high-contrast concrete speckles/patches
            color_ramp = nodes.new(type="ShaderNodeValToRGB")
            color_ramp.color_ramp.interpolation = 'LINEAR'
            
            # Base color palette for floor based on theme
            if theme == "dramatic":
                c1 = (0.008, 0.005, 0.015, 1.0)
                c2 = (0.03, 0.02, 0.045, 1.0)
            elif theme == "warm":
                c1 = (0.025, 0.018, 0.012, 1.0)
                c2 = (0.07, 0.05, 0.035, 1.0)
            elif theme == "sunset":
                c1 = (0.015, 0.005, 0.025, 1.0)
                c2 = (0.05, 0.015, 0.07, 1.0)
            else: # studio
                c1 = (0.12, 0.12, 0.12, 1.0)
                c2 = (0.32, 0.32, 0.32, 1.0)
                
            color_ramp.color_ramp.elements[0].position = 0.4
            color_ramp.color_ramp.elements[0].color = c1
            color_ramp.color_ramp.elements[1].position = 0.6
            color_ramp.color_ramp.elements[1].color = c2
            
            # Link noise factor to color ramp input
            links.new(noise.outputs['Factor'], color_ramp.inputs[0])
            # Link color ramp output to base color of Principled BSDF
            links.new(color_ramp.outputs['Color'], p.inputs[0])
                
            if "Metallic" in p.inputs:
                p.inputs["Metallic"].default_value = 0.05
            elif "Metallic Weight" in p.inputs:
                p.inputs["Metallic Weight"].default_value = 0.05
                
            # Map Range for roughness
            map_rough = nodes.new(type="ShaderNodeMapRange")
            map_rough.inputs[1].default_value = 0.0
            map_rough.inputs[2].default_value = 1.0
            map_rough.inputs[3].default_value = 0.40  # Min Roughness (glossier parts)
            map_rough.inputs[4].default_value = 0.85  # Max Roughness (matte parts)
            
            # Bump node for floor grain (very pronounced texture)
            bump = nodes.new(type="ShaderNodeBump")
            bump.inputs['Strength'].default_value = 0.45  # high strength for visible concrete texture
            bump.inputs['Distance'].default_value = 0.20
            
            # Connect roughness and bump links
            links.new(noise.outputs['Factor'], map_rough.inputs[0])
            links.new(map_rough.outputs['Result'], p.inputs['Roughness'])
            
            links.new(noise.outputs['Factor'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], p.inputs['Normal'])
                
    if len(plane_obj.material_slots) == 0:
        plane_obj.data.materials.append(mat)
    else:
        plane_obj.material_slots[0].material = mat


def setup_camera(view_angle, is_body_only):
    """Add and configure camera based on view angle and zoom level."""
    # Purge any existing camera target
    for obj in list(bpy.data.objects):
        if obj.name == "Camera_Target":
            bpy.data.objects.remove(obj, do_unlink=True)

    camera_data = bpy.data.cameras.new(name="Render Camera")
    camera_obj = bpy.data.objects.new(name="Render Camera", object_data=camera_data)
    bpy.context.collection.objects.link(camera_obj)
    
    # Make active camera
    bpy.context.scene.camera = camera_obj
    
    # Position camera based on full guitar vs body-only framing
    if is_body_only:
        target_y = 20.0
        z_dist = 90.0
        if view_angle == "front" or view_angle == "back":
            camera_obj.location = (0.0, target_y, z_dist)
            camera_obj.rotation_euler = (0, 0, math.radians(90))
        else:  # angled
            camera_obj.location = (-60.0, -10.0, 52.0)
            
            # Create target empty
            target_obj = bpy.data.objects.new("Camera_Target", None)
            bpy.context.collection.objects.link(target_obj)
            target_obj.location = (0.0, target_y, 1.0)
            
            # Add track to constraint
            constraint = camera_obj.constraints.new(type='TRACK_TO')
            constraint.target = target_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
    else:
        # Full guitar (includes long neck)
        target_y = 50.0
        z_dist = 145.0
        if view_angle == "front" or view_angle == "back":
            camera_obj.location = (0.0, target_y, z_dist)
            camera_obj.rotation_euler = (0, 0, math.radians(90))
        else:  # angled
            camera_obj.location = (-100.0, -14.0, 81.0)
            
            # Create target empty
            target_obj = bpy.data.objects.new("Camera_Target", None)
            bpy.context.collection.objects.link(target_obj)
            target_obj.location = (0.0, 38.0, 1.0)
            
            # Add track to constraint
            constraint = camera_obj.constraints.new(type='TRACK_TO')
            constraint.target = target_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
            
    bpy.context.view_layer.update()


def run_rendering():
    """Main rendering execution block inside Blender."""
    if '--' in sys.argv:
        args_start = sys.argv.index('--') + 1
        args_to_parse = sys.argv[args_start:]
    else:
        args_to_parse = []
        
    parser = argparse.ArgumentParser(description="Headless background rendering tool.")
    parser.add_argument("--config-dir", required=True, help="Path to config output directory")
    parser.add_argument("--uncut", action="store_true", help="Render the uncut full body mesh")
    parser.add_argument("--body-only", action="store_true", help="Render only the guitar body")
    parser.add_argument("--angle", default="all", choices=["front", "back", "angled", "all"], help="Camera view angle")
    parser.add_argument("--engine", default="eevee", choices=["eevee", "cycles"], help="Blender render engine")
    parser.add_argument("--material", default="gloss", help="Material preset (gloss, gloss:color, gold, chrome, chrome:color, glass, sunburst, sunburst:colors, striped, random, or custom list)")
    parser.add_argument("--lighting", default="studio", choices=["studio", "dramatic", "warm", "sunset"], help="Lighting setup preset")
    parser.add_argument("--save-blend", action="store_true", help="Optionally save the .blend scene inside the renders directory")
    
    args = parser.parse_args(args_to_parse)
    
    # Initialize Scene
    purge_scene()
    
    # Ensure Output Directory for renders exists
    renders_dir = os.path.join(args.config_dir, "renders")
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir)
        
    # Setup rendering engine parameters
    scene = bpy.context.scene
    if args.engine.lower() == "cycles":
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'  # Default to CPU for maximum headless compatibility
        scene.cycles.samples = 64     # Set small sample count for faster headless render times
    else:
        # EEVEE
        scene.render.engine = 'BLENDER_EEVEE'
        if hasattr(scene, "eevee"):
            try:
                scene.eevee.use_raytracing = True
            except AttributeError:
                pass
            try:
                scene.eevee.use_ssr = True
                scene.eevee.use_ssr_refraction = True
            except AttributeError:
                pass
            
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Disable transparent film background to show world background
    scene.render.film_transparent = False
    
    # Get models / 3rdParty root path from config folder
    # config_dir is output/<config_name>/
    # Parent of output/<config_name>/ is output/
    # Parent of output/ is root/
    output_dir = os.path.dirname(args.config_dir)
    root_dir = os.path.dirname(output_dir)
    models_dir = os.path.join(root_dir, "models")
    third_party_dir = os.path.join(root_dir, "3rdParty")
    
    # Setup Shaders
    body_mat = get_material_by_name(args.material)
    chrome_mat = create_polished_chrome()
    black_plastic_mat = create_glossy("Black Plastic", (0.02, 0.02, 0.02, 1.0))
    
    # Import Body Meshes
    body_objects = []
    
    if args.uncut:
        # Load single uncut body
        body_path = os.path.join(args.config_dir, "Guitar_Full_Body.stl")
        # Fallback to root models/guitar.obj if Full Body STL does not exist
        if not os.path.exists(body_path):
            print(f"Guitar_Full_Body.stl not found in {args.config_dir}. Falling back to default models...")
            # Detect config-specific obj
            config_name = os.path.basename(args.config_dir.strip(os.sep))
            body_path = os.path.join(models_dir, f"{config_name}.obj")
            if not os.path.exists(body_path):
                body_path = os.path.join(models_dir, "guitar.obj")
                
            # OBJ loader
            body_obj = import_obj(body_path, "Guitar_Body", rotation_x=90)
            if body_obj:
                body_obj.data.materials.append(body_mat)
                body_objects.append(body_obj)
        else:
            body_obj = import_stl(body_path, "Guitar_Body", body_mat, scale_factor=0.1)
            if body_obj:
                body_objects.append(body_obj)
    else:
        # Load sliced cut parts
        parts_list = [
            "Guitar_Bot_Left", "Guitar_Bot_Right", "Guitar_Top_Left", "Guitar_Mid_Left",
            "Guitar_Top_Right", "Guitar_Mid_Right", "Guitar_Top_Mid", "Guitar_Mid"
        ]
        
        # Check if they exist. If none are found, fallback to uncut
        any_sliced = False
        for part_name in parts_list:
            part_path = os.path.join(args.config_dir, f"{part_name}.stl")
            if os.path.exists(part_path):
                any_sliced = True
                break
                
        if not any_sliced:
            print("No sliced parts found in config output folder. Falling back to uncut body render...")
            body_path = os.path.join(args.config_dir, "Guitar_Full_Body.stl")
            if not os.path.exists(body_path):
                body_path = os.path.join(models_dir, "guitar.obj")
                body_obj = import_obj(body_path, "Guitar_Body", rotation_x=90)
            else:
                body_obj = import_stl(body_path, "Guitar_Body", body_mat, scale_factor=0.1)
            if body_obj:
                body_objects.append(body_obj)
        else:
            # Parse material scheme for sliced parts
            material_mode = args.material.lower().strip()
            
            # Setup list of shaders
            if material_mode == "striped":
                striped_mats = [
                    create_glossy(name="Gloss Red", color=(0.65, 0.01, 0.02, 1.0)),
                    create_glossy(name="Gloss Blue", color=(0.01, 0.2, 0.7, 1.0)),
                    create_gold_top(),
                    create_polished_chrome()
                ]
            elif material_mode == "random":
                rand_mats = [
                    create_glossy(name="Gloss Red", color=(0.65, 0.01, 0.02, 1.0)),
                    create_glossy(name="Gloss Blue", color=(0.01, 0.2, 0.7, 1.0)),
                    create_gold_top(),
                    create_polished_chrome(),
                    create_glossy(name="Gloss Black", color=(0.02, 0.02, 0.02, 1.0)),
                    create_transparent_glass()
                ]
            elif "," in material_mode:
                # Comma separated custom list
                custom_parts = material_mode.split(",")
                custom_mats = [get_material_by_name(m) for m in custom_parts]
            else:
                custom_mats = None
                
            # Import each part
            for idx, part_name in enumerate(parts_list):
                part_path = os.path.join(args.config_dir, f"{part_name}.stl")
                if not os.path.exists(part_path):
                    continue
                    
                # Determine part material
                part_mat = body_mat
                if material_mode == "striped":
                    part_mat = striped_mats[idx % len(striped_mats)]
                elif material_mode == "random":
                    part_mat = random.choice(rand_mats)
                elif custom_mats:
                    part_mat = custom_mats[idx % len(custom_mats)]
                    
                part_obj = import_stl(part_path, part_name, part_mat, scale_factor=0.1)
                if part_obj:
                    body_objects.append(part_obj)

    # Configure all sunburst materials to center on the body size
    for mat in bpy.data.materials:
        configure_sunburst_material(mat)

    # Import Neck and Hardware (unless body-only is requested)
    if not args.body_only:
        print("Importing references (neck and backplates) for full guitar view...")
        # Neck
        neck_path = os.path.join(third_party_dir, "NeckAmericanStandard.obj")
        neck_obj = import_obj(neck_path, "Neck", rotation_x=-90, rotation_z=90, offset_z=-0.85)
        if neck_obj:
            check_and_apply_neck_material(neck_obj)
            
        # Backplates
        backplate_path = os.path.join(models_dir, "backplate.stl")
        import_stl(backplate_path, "Hardware_backplate", black_plastic_mat)
        
        elec_backplate_path = os.path.join(models_dir, "elec_backplate.stl")
        import_stl(elec_backplate_path, "Hardware_elec_backplate", black_plastic_mat)
        
        # Optionally, move the backplates into place relative to standard layout
        # (similar to setup_scene y offsets)
        bp_obj = bpy.data.objects.get("Hardware_backplate")
        if bp_obj:
            bp_obj.rotation_euler[2] = math.radians(180)
            bp_obj.location.y = 40.0
            bp_obj.location.z = 2.0
            
        ebp_obj = bpy.data.objects.get("Hardware_elec_backplate")
        if ebp_obj:
            ebp_obj.location.z = 2.0
            
    # Setup Lighting
    target_y = 20.0 if args.body_only else 50.0
    setup_lighting(args.lighting, target_y)
    
    # Create Ground Plane
    create_ground_plane(target_y, args.lighting)
    
    # View rendering presets
    angles = ["front", "back", "angled"] if args.angle == "all" else [args.angle]
    
    for angle in angles:
        # Purge any previous camera
        for obj in list(bpy.data.objects):
            if obj.type == 'CAMERA':
                bpy.data.objects.remove(obj, do_unlink=True)
                
        # For back view, rotate the guitar 180 degrees around Y-axis
        temp_parent = None
        if angle == "back":
            # CRITICAL: update view layer so all matrix_world matrices are fully initialized/updated
            bpy.context.view_layer.update()
            guitar_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Ground_Plane"]
            if guitar_objs:
                import mathutils
                # Compute world coordinates of all bounding box corners to find actual center in X, Y, Z
                world_coords = []
                for obj in guitar_objs:
                    for v in obj.bound_box:
                        world_coords.append(obj.matrix_world @ mathutils.Vector(v))
                
                min_x = min(w[0] for w in world_coords)
                max_x = max(w[0] for w in world_coords)
                min_y = min(w[1] for w in world_coords)
                max_y = max(w[1] for w in world_coords)
                min_z = min(w[2] for w in world_coords)
                max_z = max(w[2] for w in world_coords)
                
                center_x = (min_x + max_x) / 2.0
                center_y = (min_y + max_y) / 2.0
                center_z = (min_z + max_z) / 2.0
                
                temp_parent = bpy.data.objects.new("Temp_Guitar_Parent", None)
                bpy.context.collection.objects.link(temp_parent)
                temp_parent.location = (center_x, center_y, center_z)
                
                # CRITICAL: update view layer so matrix_world is initialized before setting matrix_parent_inverse!
                bpy.context.view_layer.update()
                
                for obj in guitar_objs:
                    obj.parent = temp_parent
                    obj.matrix_parent_inverse = temp_parent.matrix_world.inverted()
                
                temp_parent.rotation_euler[1] = math.radians(180)
                bpy.context.view_layer.update()
                
        # Setup Camera
        setup_camera(angle, args.body_only)
        
        # Keep ground plane visible for all renders since camera is always at +Z looking down
        ground_plane = bpy.data.objects.get("Ground_Plane")
        if ground_plane:
            ground_plane.hide_render = False
        
        # Render
        output_filepath = os.path.join(renders_dir, f"{angle}.png")
        print(f"Rendering view '{angle}' to: {output_filepath}")
        
        scene.render.filepath = output_filepath
        bpy.ops.render.render(write_still=True)
        
        # Restore rotation and clean up temp parent
        if temp_parent:
            temp_parent.rotation_euler[1] = 0.0
            bpy.context.view_layer.update()
            
            for obj in list(bpy.data.objects):
                if obj.parent == temp_parent:
                    matrix_world = obj.matrix_world.copy()
                    obj.parent = None
                    obj.matrix_world = matrix_world
            
            bpy.data.objects.remove(temp_parent, do_unlink=True)
            bpy.context.view_layer.update()
            
    # Save the blend file if requested
    if args.save_blend:
        blend_filepath = os.path.join(renders_dir, "guitar.blend")
        print(f"Saving blend file to: {blend_filepath}")
        bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
            
    print("Headless rendering complete.")


if __name__ == "__main__":
    if inside_blender:
        run_rendering()
    else:
        print("This script must be executed internally inside Blender's python interpreter.")
        sys.exit(1)
