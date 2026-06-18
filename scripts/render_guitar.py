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


def create_candy_red():
    mat = bpy.data.materials.new(name="Candy Apple Red")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = (0.65, 0.01, 0.02, 1.0)
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


def create_electric_blue():
    mat = bpy.data.materials.new(name="Electric Blue")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = (0.01, 0.2, 0.7, 1.0)
        p.inputs.get("Roughness").default_value = 0.08
        if "Metallic" in p.inputs:
            p.inputs["Metallic"].default_value = 0.4
        elif "Metallic Weight" in p.inputs:
            p.inputs["Metallic Weight"].default_value = 0.4
        if "Coat" in p.inputs:
            p.inputs["Coat"].default_value = 1.0
        elif "Clearcoat" in p.inputs:
            p.inputs["Clearcoat"].default_value = 1.0
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


def create_polished_chrome():
    mat = bpy.data.materials.new(name="Polished Chrome")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = (0.85, 0.85, 0.85, 1.0)
        p.inputs.get("Roughness").default_value = 0.05
        if "Metallic" in p.inputs:
            p.inputs["Metallic"].default_value = 1.0
        elif "Metallic Weight" in p.inputs:
            p.inputs["Metallic Weight"].default_value = 1.0
    return mat


def create_glossy_black():
    mat = bpy.data.materials.new(name="Glossy Black")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    p = get_principled_bsdf(nodes)
    if p:
        p.inputs[0].default_value = (0.02, 0.02, 0.02, 1.0)
        p.inputs.get("Roughness").default_value = 0.1
        if "Coat" in p.inputs:
            p.inputs["Coat"].default_value = 1.0
        elif "Clearcoat" in p.inputs:
            p.inputs["Clearcoat"].default_value = 1.0
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


def create_sunburst():
    mat = bpy.data.materials.new(name="Sunburst Lacquer")
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
    vec_math = nodes.new(type="ShaderNodeVectorMath")
    vec_math.operation = 'LENGTH'
    
    # Map range to scale distance
    map_range = nodes.new(type="ShaderNodeMapRange")
    map_range.inputs[1].default_value = 0.0   # From Min
    map_range.inputs[2].default_value = 18.0  # From Max (approximate guitar hip radius)
    map_range.inputs[3].default_value = 0.0   # To Min
    map_range.inputs[4].default_value = 1.0   # To Max
    
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.interpolation = 'B_SPLINE'
    
    # Sunburst color steps: Center (Yellow) -> Mid (Red) -> Outer (Black)
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (0.9, 0.7, 0.08, 1.0)  # Yellow
    
    # Add Middle Red color
    el_red = color_ramp.color_ramp.elements.new(position=0.45)
    el_red.color = (0.65, 0.02, 0.02, 1.0)                           # Red
    
    color_ramp.color_ramp.elements[-1].position = 0.85
    color_ramp.color_ramp.elements[-1].color = (0.02, 0.02, 0.02, 1.0) # Black
    
    # Link up nodes
    links.new(tex_coord.outputs['Object'], vec_math.inputs[0])
    links.new(vec_math.outputs['Value'], map_range.inputs[0])
    links.new(map_range.outputs['Result'], color_ramp.inputs[0])
    links.new(color_ramp.outputs['Color'], p.inputs[0])
    
    return mat


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
    
    if mat_name == "red":
        return create_candy_red()
    elif mat_name == "blue":
        return create_electric_blue()
    elif mat_name == "gold":
        return create_gold_top()
    elif mat_name == "chrome" or mat_name == "silver":
        return create_polished_chrome()
    elif mat_name == "black":
        return create_glossy_black()
    elif mat_name.startswith("glass"):
        # Format: glass or glass:color
        parts = mat_name.split(":")
        color = (1.0, 1.0, 1.0, 1.0)  # default white/clear
        name = "Transparent Glass"
        if len(parts) >= 2:
            color = parse_color(parts[1])
            name = f"Glass {parts[1]}"
        return create_transparent_glass(name, color)
    elif mat_name == "sunburst":
        return create_sunburst()
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
        # Fallback to candy red
        return create_candy_red()


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


def setup_lighting(theme):
    """Build a lighting system based on a custom theme/feel."""
    # Create key light
    key_data = bpy.data.lights.new(name="Key Light", type='AREA')
    key_obj = bpy.data.objects.new(name="Key Light", object_data=key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (-30.0, -10.0, 50.0)
    key_obj.rotation_euler = (math.radians(35), math.radians(-30), 0)
    key_data.size = 15.0
    
    # Create fill light
    fill_data = bpy.data.lights.new(name="Fill Light", type='AREA')
    fill_obj = bpy.data.objects.new(name="Fill Light", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (30.0, -10.0, 40.0)
    fill_obj.rotation_euler = (math.radians(35), math.radians(30), 0)
    fill_data.size = 20.0
    
    # Create rim/back light
    rim_data = bpy.data.lights.new(name="Rim Light", type='AREA')
    rim_obj = bpy.data.objects.new(name="Rim Light", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (0.0, 70.0, 20.0)
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(180))
    rim_data.size = 10.0
    
    # Apply colors and power based on theme
    if theme == "dramatic":
        # Theatrical cyan/magenta contrast
        key_data.energy = 800.0
        key_data.color = (0.0, 0.8, 1.0)      # Cyan
        
        fill_data.energy = 150.0
        fill_data.color = (1.0, 1.0, 1.0)
        
        rim_data.energy = 1000.0
        rim_data.color = (1.0, 0.0, 0.8)      # Magenta
        
    elif theme == "warm":
        # Soft cozy golden lighting
        key_data.energy = 600.0
        key_data.color = (1.0, 0.75, 0.45)    # Amber/warm key
        
        fill_data.energy = 200.0
        fill_data.color = (1.0, 0.85, 0.6)     # Light orange/yellow fill
        
        rim_data.energy = 400.0
        rim_data.color = (1.0, 0.95, 0.85)    # Warm white
        
    elif theme == "sunset":
        # Sunset orange and deep violet
        key_data.energy = 700.0
        key_data.color = (1.0, 0.5, 0.1)      # Sun orange
        
        fill_data.energy = 150.0
        fill_data.color = (0.8, 0.2, 0.4)      # Soft magenta/pink
        
        rim_data.energy = 900.0
        rim_data.color = (0.3, 0.0, 0.8)      # Deep violet
        
    else:  # studio
        # Clean neutral lighting
        key_data.energy = 500.0
        key_data.color = (1.0, 1.0, 1.0)
        
        fill_data.energy = 150.0
        fill_data.color = (1.0, 1.0, 1.0)
        
        rim_data.energy = 400.0
        rim_data.color = (1.0, 1.0, 1.0)


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
        if view_angle == "front":
            camera_obj.location = (0.0, target_y, z_dist)
            camera_obj.rotation_euler = (0, 0, math.radians(90))
        elif view_angle == "back":
            camera_obj.location = (0.0, target_y, -z_dist)
            camera_obj.rotation_euler = (math.radians(180), 0, math.radians(-90))
        else:  # angled
            camera_obj.location = (-56.0, -8.0, 48.0)
            
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
        if view_angle == "front":
            camera_obj.location = (0.0, target_y, z_dist)
            camera_obj.rotation_euler = (0, 0, math.radians(90))
        elif view_angle == "back":
            camera_obj.location = (0.0, target_y, -z_dist)
            camera_obj.rotation_euler = (math.radians(180), 0, math.radians(-90))
        else:  # angled
            camera_obj.location = (-75.0, -2.0, 65.0)
            
            # Create target empty
            target_obj = bpy.data.objects.new("Camera_Target", None)
            bpy.context.collection.objects.link(target_obj)
            target_obj.location = (0.0, target_y, 1.0)
            
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
    parser.add_argument("--material", default="red", help="Material preset (red, blue, gold, chrome, black, glass, sunburst, striped, random, or custom list)")
    parser.add_argument("--lighting", default="studio", choices=["studio", "dramatic", "warm", "sunset"], help="Lighting setup preset")
    
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
            
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Set transparent film background (for clean composites)
    scene.render.film_transparent = True
    
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
    black_plastic_mat = create_glossy_black()
    
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
                    create_candy_red(),
                    create_electric_blue(),
                    create_gold_top(),
                    create_polished_chrome()
                ]
            elif material_mode == "random":
                rand_mats = [
                    create_candy_red(),
                    create_electric_blue(),
                    create_gold_top(),
                    create_polished_chrome(),
                    create_glossy_black(),
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
    setup_lighting(args.lighting)
    
    # View rendering presets
    angles = ["front", "back", "angled"] if args.angle == "all" else [args.angle]
    
    for angle in angles:
        # Purge any previous camera
        for obj in list(bpy.data.objects):
            if obj.type == 'CAMERA':
                bpy.data.objects.remove(obj, do_unlink=True)
                
        # Setup Camera
        setup_camera(angle, args.body_only)
        
        # Render
        output_filepath = os.path.join(renders_dir, f"{angle}.png")
        print(f"Rendering view '{angle}' to: {output_filepath}")
        
        scene.render.filepath = output_filepath
        bpy.ops.render.render(write_still=True)
        
    print("Headless rendering complete.")


if __name__ == "__main__":
    if inside_blender:
        run_rendering()
    else:
        print("This script must be executed internally inside Blender's python interpreter.")
        sys.exit(1)
