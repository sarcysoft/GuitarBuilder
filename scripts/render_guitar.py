import os
import sys
import random
import colorsys
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


def generate_distinct_colors(fixed_colors, count, seed=None):
    """Generate a list of distinct, aesthetic RGBA colors, excluding any too close to fixed_colors."""
    # Seed the local random generator if a seed is provided
    local_random = random.Random(seed) if seed is not None else random
    
    # A curated list of 24 distinct, vibrant, and premium colors (RGBA)
    base_palette = [
        (0.85, 0.05, 0.05, 1.0),  # Candy Red
        (0.05, 0.25, 0.85, 1.0),  # Royal Blue
        (0.80, 0.60, 0.05, 1.0),  # Gold
        (0.05, 0.65, 0.15, 1.0),  # Emerald Green
        (0.90, 0.35, 0.02, 1.0),  # Sunset Orange
        (0.40, 0.05, 0.60, 1.0),  # Velvet Purple
        (0.95, 0.80, 0.02, 1.0),  # Canary Yellow
        (0.05, 0.75, 0.75, 1.0),  # Turquoise/Teal
        (0.90, 0.10, 0.60, 1.0),  # Hot Pink
        (0.10, 0.80, 0.50, 1.0),  # Mint Green
        (0.55, 0.30, 0.05, 1.0),  # Copper / Bronze
        (0.30, 0.50, 0.90, 1.0),  # Sky Blue
        (0.50, 0.05, 0.20, 1.0),  # Maroon
        (0.10, 0.10, 0.40, 1.0),  # Navy Blue
        (0.45, 0.60, 0.05, 1.0),  # Olive Green
        (0.90, 0.60, 0.60, 1.0),  # Coral
        (0.30, 0.80, 0.20, 1.0),  # Lime Green
        (0.50, 0.20, 0.80, 1.0),  # Lavender
        (0.85, 0.85, 0.85, 1.0),  # Silver / Platinum
        (0.95, 0.95, 0.95, 1.0),  # Arctic White
        (0.02, 0.02, 0.02, 1.0),  # Jet Black
        (0.35, 0.35, 0.35, 1.0),  # Slate Grey
        (0.60, 0.40, 0.80, 1.0),  # Plum
        (0.90, 0.45, 0.10, 1.0),  # Apricot
    ]
    
    # Filter out colors close to any fixed colors
    filtered_palette = []
    for c in base_palette:
        too_close = False
        for fc in fixed_colors:
            # Euclidean distance in RGB
            dist = math.sqrt(sum((a - b)**2 for a, b in zip(c[:3], fc[:3])))
            if dist < 0.25:
                too_close = True
                break
        if not too_close:
            filtered_palette.append(c)
            
    # Shuffle using our seeded/unseeded local random generator
    local_random.shuffle(filtered_palette)
    
    # If we need more colors than available, dynamically generate distinct HSV colors
    while len(filtered_palette) < count:
        h = local_random.random()
        s = 0.7 + 0.3 * local_random.random()
        v = 0.6 + 0.4 * local_random.random()
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        c = (r, g, b, 1.0)
        # Verify it's not close to fixed colors or already selected colors
        too_close = False
        for fc in fixed_colors + filtered_palette:
            dist = math.sqrt(sum((a - b)**2 for a, b in zip(c[:3], fc[:3])))
            if dist < 0.25:
                too_close = True
                break
        if not too_close:
            filtered_palette.append(c)
            
    return filtered_palette[:count]


def get_concrete_material_string(template, part_index, colors_list, num_rand_per_part):
    """Replace 'random' color placeholders in the material template with hex colors from colors_list."""
    parts = template.split(":")
    concrete_parts = [parts[0]]
    color_cursor = part_index * num_rand_per_part
    
    for p in parts[1:]:
        if p.lower().strip() == "random":
            c = colors_list[color_cursor]
            color_cursor += 1
            hex_str = f"#{int(c[0]*255):02x}{int(c[1]*255):02x}{int(c[2]*255):02x}"
            concrete_parts.append(hex_str)
        else:
            concrete_parts.append(p)
            
    return ":".join(concrete_parts)


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
    links = mat.node_tree.links
    
    principled = get_principled_bsdf(nodes)
    if not principled:
        return mat
        
    # Set roughness and reflection settings
    rough_input = principled.inputs.get("Roughness")
    if rough_input:
        rough_input.default_value = 0.35
        
    # Nodes for wood grain texture
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    mapping = nodes.new(type="ShaderNodeMapping")
    
    # Scale coordinates to stretch noise into long grain lines (maple grain)
    mapping.inputs['Scale'].default_value = (12.0, 0.4, 12.0)
    
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 6.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.5
    
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.interpolation = 'LINEAR'
    
    # Light maple base and darker grain streak colors
    color_ramp.color_ramp.elements[0].position = 0.25
    color_ramp.color_ramp.elements[0].color = (0.86, 0.76, 0.58, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.75
    color_ramp.color_ramp.elements[1].color = (0.75, 0.61, 0.43, 1.0)
    
    # Subtle bump mapping for grain texture
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.015
    bump.inputs['Distance'].default_value = 0.05
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Factor'], color_ramp.inputs['Factor'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    
    links.new(noise.outputs['Factor'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
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


def create_random_material(name="Random Material"):
    """Generate a highly diverse, vibrant, and premium random material (glossy, sparkle, chrome, or glass)."""
    # Material types:
    # - "glossy" (Glossy paint)
    # - "sparkle" (Glitter paint)
    # - "chrome" (Polished metal tint)
    # - "glass" (Tinted transparent glass)
    mat_type = random.choice(["glossy", "sparkle", "chrome", "glass"])
    
    # Use HSL/HSV color space for vibrant and diverse colors
    h = random.random()
    s = random.uniform(0.55, 0.95)
    v = random.uniform(0.5, 0.95)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    color = (r, g, b, 1.0)
    
    if mat_type == "glossy":
        return create_glossy(name=name, color=color)
    elif mat_type == "sparkle":
        h_flake = (h + random.uniform(0.1, 0.5)) % 1.0
        s_flake = random.uniform(0.6, 1.0)
        v_flake = random.uniform(0.7, 1.0)
        r2, g2, b2 = colorsys.hsv_to_rgb(h_flake, s_flake, v_flake)
        return create_sparkle(name=name, main_color_rgb=color, sparkle_color_rgb=(r2, g2, b2, 1.0))
    elif mat_type == "chrome":
        return create_polished_chrome(name=name, color=color)
    elif mat_type == "glass":
        glass_r, glass_g, glass_b = colorsys.hsv_to_rgb(h, random.uniform(0.2, 0.5), random.uniform(0.8, 1.0))
        return create_transparent_glass(name=name, color=(glass_r, glass_g, glass_b, 1.0))
        
    return create_glossy(name=name, color=color)


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
    
    size_x = max_x - min_x
    size_y = max_y - min_y
    
    center_x = (min_x + max_x) / 2.0
    center_y = min_y + size_y * 0.38
    
    scale_y = size_x / size_y if (size_y > 0 and size_x > 0) else 1.0
    
    # Set Mapping Scale (adjusts Y scale to make the radial gradient elliptical matching body proportions, and projects 2D along Z)
    try:
        scale_input = mapping.inputs.get('Scale') or mapping.inputs[3]
        scale_input.default_value = (1.0, scale_y, 0.0)
    except Exception as e:
        print(f"Error setting mapping Scale: {e}")
        
    # Set Mapping Translation (moves center of gradient to center of body - requires scaling the Location coordinates for POINT mapping)
    try:
        loc_input = mapping.inputs.get('Location') or mapping.inputs[1]
        loc_input.default_value = (-center_x, -center_y * scale_y, 0.0)
    except Exception as e:
        print(f"Error setting mapping Location: {e}")
        
    # Set Map Range From Max (radius of the sunburst fits half the body width)
    try:
        map_range.inputs[2].default_value = size_y * 0.55
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
        
    # Standard settings
    p.inputs.get("Roughness").default_value = 0.25  # default base roughness
    if "Metallic" in p.inputs:
        p.inputs["Metallic"].default_value = 0.0   # base is non-metallic paint
    elif "Metallic Weight" in p.inputs:
        p.inputs["Metallic Weight"].default_value = 0.0
        
    # Setup Clearcoat (Coat) layer properly for Blender 5.x/4.x/3.x
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = 1.0
    elif "Coat" in p.inputs:
        p.inputs["Coat"].default_value = 1.0
    elif "Clearcoat" in p.inputs:
        p.inputs["Clearcoat"].default_value = 1.0
        
    if "Coat Roughness" in p.inputs:
        p.inputs["Coat Roughness"].default_value = 0.02
        
    # Texture coordinate node
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    
    # Voronoi cells for sparkles - scale of 3.5 gives distinct larger flakes
    voronoi = nodes.new(type="ShaderNodeTexVoronoi")
    voronoi.inputs['Scale'].default_value = 3.5
    
    # Separate color to extract a random value per Voronoi cell for variation
    sep_color = nodes.new(type="ShaderNodeSeparateColor")
    
    # Map random cell value to threshold range (size variation: 0.12 to 0.26)
    map_thresh = nodes.new(type="ShaderNodeMapRange")
    map_thresh.inputs[1].default_value = 0.0
    map_thresh.inputs[2].default_value = 1.0
    map_thresh.inputs[3].default_value = 0.12  # min flake size
    map_thresh.inputs[4].default_value = 0.26  # max flake size
    
    # Flake Mask (Binary check: Distance < threshold)
    mask_math = nodes.new(type="ShaderNodeMath")
    mask_math.operation = 'LESS_THAN'
    
    # Mix node for Base Color (Mix between paint color A and flake color B)
    mix = nodes.new(type="ShaderNodeMix")
    mix.data_type = 'RGBA'
    mix.blend_type = 'MIX'
    
    # Find RGBA type sockets
    color_a_socket = None
    color_b_socket = None
    for inp in mix.inputs:
        if inp.type == 'RGBA':
            if color_a_socket is None:
                color_a_socket = inp
            else:
                color_b_socket = inp
                break
                
    if color_a_socket and color_b_socket:
        color_a_socket.default_value = main_color_rgb
        color_b_socket.default_value = sparkle_color_rgb
    
    # Map range to mix Roughness (0.25 for paint, 0.01 for shiny metallic flakes)
    map_rough = nodes.new(type="ShaderNodeMapRange")
    map_rough.inputs[1].default_value = 0.0
    map_rough.inputs[2].default_value = 1.0
    map_rough.inputs[3].default_value = 0.25  # paint roughness
    map_rough.inputs[4].default_value = 0.01  # flake roughness
    
    # Map range to mix Metallic (0.0 for paint, 1.0 for flakes)
    map_metal = nodes.new(type="ShaderNodeMapRange")
    map_metal.inputs[1].default_value = 0.0
    map_metal.inputs[2].default_value = 1.0
    map_metal.inputs[3].default_value = 0.0   # paint metallic
    map_metal.inputs[4].default_value = 1.0   # flake metallic
    
    # Geometry input node for clean normals
    geom_node = nodes.new(type="ShaderNodeNewGeometry")
    
    # Bump node to perturb normals on the flakes for glinting
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs['Strength'].default_value = 1.2  # High strength for maximum angle variance
    bump.inputs['Distance'].default_value = 0.02
    
    # Mix normal node to combine clean normal and bump normal based on binary mask
    mix_normal = nodes.new(type="ShaderNodeMix")
    mix_normal.data_type = 'VECTOR'
    mix_normal.blend_type = 'MIX'
    
    # Connections
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Color'], sep_color.inputs['Color'])
    
    # Connect Red channel of cell color to threshold mapping
    links.new(sep_color.outputs['Red'], map_thresh.inputs[0])
    
    # Connect distance and threshold to the binary mask node
    links.new(voronoi.outputs['Distance'], mask_math.inputs[0])
    links.new(map_thresh.outputs['Result'], mask_math.inputs[1])
    
    # Connect mask directly as factor for all attributes
    links.new(mask_math.outputs['Value'], mix.inputs[0])
    
    # Connect mask to Roughness map
    links.new(mask_math.outputs['Value'], map_rough.inputs[0])
    links.new(map_rough.outputs['Result'], p.inputs['Roughness'])
    
    # Connect mask to Metallic map
    links.new(mask_math.outputs['Value'], map_metal.inputs[0])
    if "Metallic" in p.inputs:
        links.new(map_metal.outputs['Result'], p.inputs['Metallic'])
    elif "Metallic Weight" in p.inputs:
        links.new(map_metal.outputs['Result'], p.inputs['Metallic Weight'])
        
    # Connect Base Color mix
    rgba_output = None
    for out in mix.outputs:
        if out.type == 'RGBA':
            rgba_output = out
            break
    if rgba_output:
        links.new(rgba_output, p.inputs[0])
        
    # Connect Bump height and normal input
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    
    # Mix normals: Clean normal (A) and Bumped normal (B) using binary mask
    a_vector = [i for i in mix_normal.inputs if i.name == 'A' and i.type == 'VECTOR'][0]
    b_vector = [i for i in mix_normal.inputs if i.name == 'B' and i.type == 'VECTOR'][0]
    factor_float = [i for i in mix_normal.inputs if i.name == 'Factor' and i.type == 'VALUE'][0]
    result_vector = [o for o in mix_normal.outputs if o.name == 'Result' and o.type == 'VECTOR'][0]
    
    links.new(geom_node.outputs['Normal'], a_vector)
    links.new(bump.outputs['Normal'], b_vector)
    links.new(mask_math.outputs['Value'], factor_float)
    
    # Connect base normal
    links.new(result_vector, p.inputs['Normal'])
    
    # Connect clean normal to Clearcoat Normal to keep outer surface perfectly smooth/glossy
    if "Coat Normal" in p.inputs:
        links.new(geom_node.outputs['Normal'], p.inputs['Coat Normal'])
        
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
        if slot.material:
            name = slot.material.name.lower().strip()
            # If a custom material name is loaded (not standard generic default names), assume it's valid
            if name and not name.startswith("material") and not name.startswith("default"):
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
                
            # Shade Smooth and apply Auto-Smooth to prevent flat facets on curved surfaces
            bpy.ops.object.select_all(action='DESELECT')
            imported_obj.select_set(True)
            bpy.context.view_layer.objects.active = imported_obj
            bpy.ops.object.shade_smooth()
            
            import math
            if hasattr(imported_obj.data, "use_auto_smooth"):
                imported_obj.data.use_auto_smooth = True
                imported_obj.data.auto_smooth_angle = math.radians(30)
            else:
                has_modifier = False
                for mod in imported_obj.modifiers:
                    if mod.type == 'EDGE_SPLIT':
                        has_modifier = True
                        break
                if not has_modifier:
                    imported_obj.modifiers.new(name="Edge Split", type='EDGE_SPLIT')
                    
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
def get_body_center_world():
    """Dynamically compute the collective 3D center of the guitar body objects in world coordinates."""
    import mathutils
    body_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name.startswith("Guitar_") and "backplate" not in obj.name.lower()]
    if not body_objs:
        return (0.0, 0.0, 0.0)
    
    world_coords = []
    for obj in body_objs:
        for v in obj.bound_box:
            world_coords.append(obj.matrix_world @ mathutils.Vector(v))
            
    if not world_coords:
        return (0.0, 0.0, 0.0)
        
    min_x = min(w[0] for w in world_coords)
    max_x = max(w[0] for w in world_coords)
    min_y = min(w[1] for w in world_coords)
    max_y = max(w[1] for w in world_coords)
    min_z = min(w[2] for w in world_coords)
    max_z = max(w[2] for w in world_coords)
    
    return ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0)


def setup_lighting(theme, target_center=(0.0, 0.0, 0.0)):
    """Build a lighting system based on a custom theme/feel.
    
    Uses a 3-point lighting rig designed to work correctly for front, back
    and angled camera views. Lights are positioned to rake across the
    guitar surface (side-lighting) so detail and depth are visible from
    all angles.
    """
    scene = bpy.context.scene
    
    # Purge any existing lights and previous light targets
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT' or obj.name == "Light_Target":
            bpy.data.objects.remove(obj, do_unlink=True)
            
    cx, cy, cz = target_center
    
    # Create a Light Target empty at the body center for lights to track
    target_obj = bpy.data.objects.new("Light_Target", None)
    bpy.context.collection.objects.link(target_obj)
    target_obj.location = (cx, cy, cz)
    
    # ------------------------------------------------------------------ #
    # Key light — raking from upper-left side (Y-right, Z-up space)
    # ------------------------------------------------------------------ #
    key_data = bpy.data.lights.new(name="Key Light", type='AREA')
    key_obj = bpy.data.objects.new(name="Key Light", object_data=key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (cx - 60.0, cy - 5.0, cz + 55.0)
    key_data.size = 15.0   # Soft but directional shadows

    # ------------------------------------------------------------------ #
    # Fill light — opposite side, softens shadows
    # ------------------------------------------------------------------ #
    fill_data = bpy.data.lights.new(name="Fill Light", type='AREA')
    fill_obj = bpy.data.objects.new(name="Fill Light", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (cx + 55.0, cy - 5.0, cz + 35.0)
    fill_data.size = 25.0

    # ------------------------------------------------------------------ #
    # Rim light — behind and above guitar to create edge definition
    # ------------------------------------------------------------------ #
    rim_data = bpy.data.lights.new(name="Rim Light", type='AREA')
    rim_obj = bpy.data.objects.new(name="Rim Light", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (cx + 15.0, cy + 55.0, cz + 30.0)
    rim_data.size = 15.0

    # ------------------------------------------------------------------ #
    # Top overhead softbox
    # ------------------------------------------------------------------ #
    top_data = bpy.data.lights.new(name="Top Fill", type='AREA')
    top_obj = bpy.data.objects.new(name="Top Fill", object_data=top_data)
    bpy.context.collection.objects.link(top_obj)
    top_obj.location = (cx, cy, cz + 90.0)
    top_obj.rotation_euler = (0, 0, 0)
    top_data.size = 40.0   # Moderately sized softbox to preserve shape definition

    # Add Track To constraints so lights automatically track and face the body center
    for light_obj in [key_obj, fill_obj, rim_obj]:
        constraint = light_obj.constraints.new(type='TRACK_TO')
        constraint.target = target_obj
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

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
        "dramatic": 0.22,
        "warm":     0.28,
        "sunset":   0.22,
        "studio":   0.32,  # studio needs bright background to feel like a studio
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
        
        # Soft ambient occlusion shadows in world settings for realistic contact shading
        try:
            scene.world.light_settings.use_ambient_occlusion = True
            scene.world.light_settings.ao_factor = 0.08
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Per-theme energies and colors
    # ------------------------------------------------------------------ #
    if theme == "dramatic":
        # Theatrical cyan-key / magenta-rim contrast lighting
        key_data.energy  = 8000.0
        key_data.color   = (0.15, 0.85, 1.0)   # Icy cyan

        fill_data.energy = 2500.0
        fill_data.color  = (1.0, 0.9, 1.0)     # Near-white

        rim_data.energy  = 9000.0
        rim_data.color   = (1.0, 0.05, 0.75)   # Hot magenta

        top_data.energy  = 1200.0
        top_data.color   = (0.6, 0.4, 1.0)     # Subtle violet overhead

    elif theme == "warm":
        # Soft amber studio with warm overhead
        key_data.energy  = 7500.0
        key_data.color   = (1.0, 0.78, 0.45)   # Amber

        fill_data.energy = 2500.0
        fill_data.color  = (1.0, 0.88, 0.65)

        rim_data.energy  = 6000.0
        rim_data.color   = (1.0, 0.96, 0.88)   # Warm white

        top_data.energy  = 1800.0
        top_data.color   = (1.0, 0.9, 0.75)

    elif theme == "sunset":
        # Sunset orange key, violet rim
        key_data.energy  = 8000.0
        key_data.color   = (1.0, 0.45, 0.08)   # Orange sun

        fill_data.energy = 2000.0
        fill_data.color  = (0.85, 0.2, 0.45)   # Pink

        rim_data.energy  = 8500.0
        rim_data.color   = (0.25, 0.0, 0.85)   # Deep violet

        top_data.energy  = 1200.0
        top_data.color   = (1.0, 0.5, 0.3)

    else:  # studio — clean neutral photography-style rig
        # Key rakes across body for shadows / material detail
        key_data.energy  = 6500.0
        key_data.color   = (1.0, 1.0, 1.0)

        # Moderate fill to keep shadow side visible without killing contrast
        fill_data.energy = 2000.0
        fill_data.color  = (0.95, 0.98, 1.0)   # Slightly cool fill

        # Rim adds edge separation, helps back view pop
        rim_data.energy  = 4500.0
        rim_data.color   = (1.0, 1.0, 1.0)

        # Top soft-box is the main diffuse fill for front/back views
        top_data.energy  = 1000.0
        top_data.color   = (1.0, 1.0, 1.0)

    # For all lights, enable contact shadows for EEVEE realism
    for light_obj in [key_obj, fill_obj, rim_obj, top_obj]:
        if light_obj and hasattr(light_obj.data, "use_contact_shadow"):
            try:
                light_obj.data.use_contact_shadow = True
                if hasattr(light_obj.data, "contact_shadow_distance"):
                    light_obj.data.contact_shadow_distance = 0.3
            except Exception:
                pass

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
            
            # Theme-specific floor settings for realistic reflections and bump
            floor_settings = {
                "dramatic": {
                    "c1": (0.015, 0.01, 0.03, 1.0),
                    "c2": (0.04, 0.025, 0.07, 1.0),
                    "metallic": 0.20,
                    "rough_min": 0.18,
                    "rough_max": 0.50,
                    "bump_strength": 0.08,
                    "bump_distance": 0.05
                },
                "warm": {
                    "c1": (0.06, 0.04, 0.025, 1.0),
                    "c2": (0.15, 0.11, 0.075, 1.0),
                    "metallic": 0.12,
                    "rough_min": 0.25,
                    "rough_max": 0.65,
                    "bump_strength": 0.15,
                    "bump_distance": 0.05
                },
                "sunset": {
                    "c1": (0.03, 0.01, 0.045, 1.0),
                    "c2": (0.09, 0.03, 0.13, 1.0),
                    "metallic": 0.15,
                    "rough_min": 0.22,
                    "rough_max": 0.60,
                    "bump_strength": 0.10,
                    "bump_distance": 0.05
                },
                "studio": {
                    "c1": (0.12, 0.12, 0.12, 1.0),
                    "c2": (0.32, 0.32, 0.32, 1.0),
                    "metallic": 0.10,
                    "rough_min": 0.30,
                    "rough_max": 0.70,
                    "bump_strength": 0.12,
                    "bump_distance": 0.05
                }
            }
            
            settings = floor_settings.get(theme, floor_settings["studio"])
            c1 = settings["c1"]
            c2 = settings["c2"]
            
            color_ramp.color_ramp.elements[0].position = 0.4
            color_ramp.color_ramp.elements[0].color = c1
            color_ramp.color_ramp.elements[1].position = 0.6
            color_ramp.color_ramp.elements[1].color = c2
            
            # Link noise factor to color ramp input
            links.new(noise.outputs['Factor'], color_ramp.inputs[0])
            # Link color ramp output to base color of Principled BSDF
            links.new(color_ramp.outputs['Color'], p.inputs[0])
                
            if "Metallic" in p.inputs:
                p.inputs["Metallic"].default_value = settings["metallic"]
            elif "Metallic Weight" in p.inputs:
                p.inputs["Metallic Weight"].default_value = settings["metallic"]
                
            # Map Range for roughness
            map_rough = nodes.new(type="ShaderNodeMapRange")
            map_rough.inputs[1].default_value = 0.0
            map_rough.inputs[2].default_value = 1.0
            map_rough.inputs[3].default_value = settings["rough_min"]  # Min Roughness (glossier parts)
            map_rough.inputs[4].default_value = settings["rough_max"]  # Max Roughness (matte parts)
            
            # Bump node for floor grain (very pronounced texture)
            bump = nodes.new(type="ShaderNodeBump")
            bump.inputs['Strength'].default_value = settings["bump_strength"]
            bump.inputs['Distance'].default_value = settings["bump_distance"]
            
            # Connect roughness and bump links
            links.new(noise.outputs['Factor'], map_rough.inputs[0])
            links.new(map_rough.outputs['Result'], p.inputs['Roughness'])
            
            links.new(noise.outputs['Factor'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], p.inputs['Normal'])
                
    if len(plane_obj.material_slots) == 0:
        plane_obj.data.materials.append(mat)
    else:
        plane_obj.material_slots[0].material = mat


def parse_rotation_string(rot_str):
    """Parse comma-separated rotation string into a tuple of 3 floats."""
    if not rot_str:
        return None
    try:
        parts = [float(x.strip()) for x in rot_str.split(",")]
        if len(parts) == 3:
            return tuple(parts)
    except Exception as e:
        print(f"Error parsing rotation string '{rot_str}': {e}")
    return None


def get_camera_fov(camera_obj):
    """Calculate the horizontal and vertical field of view in radians."""
    scene = bpy.context.scene
    render_width = scene.render.resolution_x
    render_height = scene.render.resolution_y
    aspect_ratio = render_width / render_height
    
    camera_data = camera_obj.data
    fov = camera_data.angle  # field of view in radians (depends on sensor fit)
    
    if camera_data.sensor_fit == 'HORIZONTAL':
        fov_x = fov
        fov_y = 2.0 * math.atan(math.tan(fov_x / 2.0) / aspect_ratio)
    elif camera_data.sensor_fit == 'VERTICAL':
        fov_y = fov
        fov_x = 2.0 * math.atan(math.tan(fov_y / 2.0) * aspect_ratio)
    else:  # AUTO
        if aspect_ratio >= 1.0:
            fov_x = fov
            fov_y = 2.0 * math.atan(math.tan(fov_x / 2.0) / aspect_ratio)
        else:
            fov_y = fov
            fov_x = 2.0 * math.atan(math.tan(fov_y / 2.0) * aspect_ratio)
            
    return fov_x, fov_y


def calculate_optimal_camera_distance(camera_obj, pitch_angle, guitar_objs, margin=0.85):
    """
    Calculate optimal camera distance d to frame the subject.
    Project bounding box points in camera-oriented space and find d.
    """
    import mathutils
    
    # Get camera field of view
    fov_x, fov_y = get_camera_fov(camera_obj)
    
    # Camera rotation matrix (pitch down around X axis)
    pitch_rad = math.radians(90.0 - pitch_angle)
    R_cam = mathutils.Euler((pitch_rad, 0.0, 0.0)).to_matrix()
    R_cam_inv = R_cam.inverted()
    
    # Collect all bounding box points in world space
    world_coords = []
    for obj in guitar_objs:
        for v in obj.bound_box:
            world_coords.append(obj.matrix_world @ mathutils.Vector(v))
            
    if not world_coords:
        return 90.0
        
    # Usable FOV tangents with margin
    tan_fov_x = math.tan(fov_x / 2.0) * margin
    tan_fov_y = math.tan(fov_y / 2.0) * margin
    
    max_d = 0.0
    for p_world in world_coords:
        q = R_cam_inv @ p_world
        
        # depth is d - q.z
        # we want |q.x| / (d - q.z) <= tan_fov_x  => d >= q.z + |q.x| / tan_fov_x
        # we want |q.y| / (d - q.z) <= tan_fov_y  => d >= q.z + |q.y| / tan_fov_y
        d_x = q.z + abs(q.x) / tan_fov_x
        d_y = q.z + abs(q.y) / tan_fov_y
        
        max_d = max(max_d, d_x, d_y)
        
    return max(max_d, 5.0)


def setup_guitar_rig(guitar_objs, rot_x=0.0, rot_y=0.0, rot_z=0.0):
    """Center subject meshes above the origin and apply 3-axis rotation."""
    import mathutils
    
    # 1. Compute collective bounding box center
    world_coords = []
    for obj in guitar_objs:
        for v in obj.bound_box:
            world_coords.append(obj.matrix_world @ mathutils.Vector(v))
            
    if not world_coords:
        return None
        
    min_x = min(w[0] for w in world_coords)
    max_x = max(w[0] for w in world_coords)
    min_y = min(w[1] for w in world_coords)
    max_y = max(w[1] for w in world_coords)
    min_z = min(w[2] for w in world_coords)
    max_z = max(w[2] for w in world_coords)
    
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0
    
    print(f"Centering subject around bbox center: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
    
    # 2. Create Empty parent object
    rig_name = "Guitar_Rig"
    old_rig = bpy.data.objects.get(rig_name)
    if old_rig:
        bpy.data.objects.remove(old_rig, do_unlink=True)
        
    rig_obj = bpy.data.objects.new(rig_name, None)
    bpy.context.collection.objects.link(rig_obj)
    rig_obj.location = (center_x, center_y, center_z)
    
    # Force update
    bpy.context.view_layer.update()
    
    # 3. Parent meshes keeping transform
    for obj in guitar_objs:
        obj.parent = rig_obj
        obj.matrix_parent_inverse = rig_obj.matrix_world.inverted()
        
    bpy.context.view_layer.update()
    
    # 4. Relocate rig to origin
    rig_obj.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    
    # 5. Apply rotations
    rig_obj.rotation_euler = (math.radians(rot_x), math.radians(rot_y), math.radians(rot_z))
    bpy.context.view_layer.update()
    
    return rig_obj


def cleanup_guitar_rig(rig_obj, guitar_objs):
    """Reset rig transformation, unparent children, and delete rig."""
    if not rig_obj:
        return
    # Reset rig
    rig_obj.rotation_euler = (0.0, 0.0, 0.0)
    rig_obj.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    
    # Unparent children keeping their centered world position
    for obj in guitar_objs:
        if obj.parent == rig_obj:
            world_mat = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = world_mat
            
    # Delete rig
    bpy.data.objects.remove(rig_obj, do_unlink=True)
    bpy.context.view_layer.update()


def setup_camera(view_angle, guitar_objs, custom_pitch=None, custom_guitar_rot=None, margin=0.85):
    """Add and configure camera and rig based on view angle, pitch, and rotation."""
    
    # 1. Define default view configs
    DEFAULT_VIEWS = {
        "front": {
            "pitch": 90.0,
            "guitar_rot": (0.0, 0.0, -90.0)
        },
        "back": {
            "pitch": 90.0,
            "guitar_rot": (0.0, 180.0, -90.0)
        },
        "angled": {
            "pitch": 35.0,
            "guitar_rot": (0.0, 0.0, 62.5)
        }
    }
    
    # Resolve pitch and rotation
    pitch = custom_pitch
    guitar_rot = custom_guitar_rot
    
    if pitch is None or guitar_rot is None:
        view_config = DEFAULT_VIEWS.get(view_angle, DEFAULT_VIEWS["front"])
        if pitch is None:
            pitch = view_config["pitch"]
        if guitar_rot is None:
            guitar_rot = view_config["guitar_rot"]
            
    print(f"Setting up view '{view_angle}' with camera pitch {pitch:.1f} and guitar rotation {guitar_rot}")
    
    # 2. Setup Guitar Rig (center at origin and apply rotations)
    rig_obj = setup_guitar_rig(guitar_objs, rot_x=guitar_rot[0], rot_y=guitar_rot[1], rot_z=guitar_rot[2])
    
    # 3. Create active camera
    camera_data = bpy.data.cameras.new(name="Render Camera")
    camera_obj = bpy.data.objects.new(name="Render Camera", object_data=camera_data)
    bpy.context.collection.objects.link(camera_obj)
    bpy.context.scene.camera = camera_obj
    
    # 4. Calculate optimal camera distance
    # Force a view layer update so the parented mesh matrices are fully recalculated
    bpy.context.view_layer.update()
    
    d = calculate_optimal_camera_distance(camera_obj, pitch, guitar_objs, margin=margin)
    print(f"Calculated optimal camera distance: {d:.2f}")
    
    # 5. Position and rotate camera
    pitch_rad = math.radians(pitch)
    camera_obj.location = (0.0, -d * math.cos(pitch_rad), d * math.sin(pitch_rad))
    camera_obj.rotation_euler = (math.radians(90.0 - pitch), 0.0, 0.0)
    
    bpy.context.view_layer.update()
    return rig_obj


def setup_animation(guitar_objs, margin=0.85, dynamic_zoom=False):
    """Create camera and guitar rig, solve locked camera distance, and set animation keyframes."""
    # 1. Purge any previous camera
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # 2. Setup Guitar Rig Empty (initially at (0, 0, -90.0) orientation)
    rig_obj = setup_guitar_rig(guitar_objs, rot_x=0.0, rot_y=0.0, rot_z=-90.0)
    if not rig_obj:
        print("Error: Could not set up guitar rig for animation.")
        return None
        
    # 3. Create active camera
    camera_data = bpy.data.cameras.new(name="Render Camera")
    camera_obj = bpy.data.objects.new(name="Render Camera", object_data=camera_data)
    bpy.context.collection.objects.link(camera_obj)
    bpy.context.scene.camera = camera_obj
    
    # 4. Calculate locked camera distance and ground plane drop by sampling key animation frames
    bpy.context.view_layer.update()
    d_samples = []
    
    # Track minimum Z coordinate across all sampled orientations
    import mathutils
    min_z_samples = []
    
    def record_state(pitch_val):
        d_val = calculate_optimal_camera_distance(camera_obj, pitch_val, guitar_objs, margin=margin)
        d_samples.append(d_val)
        for obj in guitar_objs:
            for v in obj.bound_box:
                world_coord = obj.matrix_world @ mathutils.Vector(v)
                min_z_samples.append(world_coord.z)

    # Sample front view
    record_state(90.0)
    
    # Sample Y spin orientations (90, 180, 270 degrees)
    for y_rot in [90.0, 180.0, 270.0]:
        rig_obj.rotation_euler = (0.0, math.radians(y_rot), math.radians(-90.0))
        bpy.context.view_layer.update()
        record_state(90.0)
        
    # Sample pitch / tilt transitions (neck tilts up to 45.0)
    for p, rx in [(67.5, 22.5), (45.0, 45.0)]:
        rig_obj.rotation_euler = (math.radians(rx), 0.0, math.radians(-90.0))
        bpy.context.view_layer.update()
        record_state(p)
        
    # Sample Z spin orientations (guitar rotated around Z from -90 to -450)
    for z_rot in [-90.0, -150.0, -210.0, -270.0, -330.0, -390.0, -450.0]:
        rig_obj.rotation_euler = (math.radians(45.0), 0.0, math.radians(z_rot))
        bpy.context.view_layer.update()
        record_state(45.0)
        
    d = max(d_samples)
    min_z_overall = min(min_z_samples) if min_z_samples else -30.0
    print(f"Calculated locked camera distance for animation: {d:.2f}")
    print(f"Recorded minimum Z coordinate of guitar: {min_z_overall:.2f}")
    
    # Adjust ground plane location dynamically to accommodate the tilt
    ground_plane = bpy.data.objects.get("Ground_Plane")
    if ground_plane:
        ground_plane.location.z = min_z_overall - 10.0
        print(f"Adjusted Ground_Plane Z location to: {ground_plane.location.z:.2f}")
        
    # Restore initial state
    rig_obj.rotation_euler = (0.0, 0.0, math.radians(-90.0))
    bpy.context.view_layer.update()
    
    # Clear any previous animation data
    if camera_obj.animation_data:
        camera_obj.animation_data_clear()
    if rig_obj.animation_data:
        rig_obj.animation_data_clear()
        
    # Set scene timeline bounds
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 870
    
    # 5. Insert Keyframes
    # Rig location is locked at (0, 0, 0)
    rig_obj.location = (0.0, 0.0, 0.0)
    rig_obj.keyframe_insert(data_path="location", frame=1)
    
    # Keyframe insertion helper
    def insert_keys(frame, pitch, rx, ry, rz):
        # Camera transform
        pitch_rad = math.radians(pitch)
        camera_obj.location = (0.0, -d * math.cos(pitch_rad), d * math.sin(pitch_rad))
        camera_obj.rotation_euler = (math.radians(90.0 - pitch), 0.0, 0.0)
        camera_obj.keyframe_insert(data_path="location", frame=frame)
        camera_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Rig rotation
        rig_obj.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        rig_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        
    # Phase 1: Pause in Front View (frame 1 to 60)
    insert_keys(1, 90.0, 0.0, 0.0, -90.0)
    insert_keys(60, 90.0, 0.0, 0.0, -90.0)
    
    # Phase 2: Y-axis 360 rotation (frame 61 to 360)
    insert_keys(360, 90.0, 0.0, 360.0, -90.0)
    
    # Phase 3: Drop camera to 45 while guitar X tilts to +45 (frame 361 to 510)
    insert_keys(510, 45.0, 45.0, 360.0, -90.0)
    
    # Phase 4: Z-axis 360 rotation (frame 511 to 810) - rotation goes from -90 to -450 (clockwise)
    insert_keys(810, 45.0, 45.0, 360.0, -450.0)
    
    # Phase 5: Final Pause (frame 811 to 870)
    insert_keys(870, 45.0, 45.0, 360.0, -450.0)
    
    # Force Bezier interpolation for all animation curves (ease-in/ease-out)
    def set_bezier_interpolation(obj):
        if not obj or not obj.animation_data or not obj.animation_data.action:
            return
        action = obj.animation_data.action
        
        # Try legacy action fcurves (Blender 3.x and 4.0-4.3)
        if hasattr(action, "fcurves"):
            for fcurve in action.fcurves:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'
            return
            
        # Try new layered action fcurves (Blender 4.4 and 5.x)
        if hasattr(action, "layers") and hasattr(obj.animation_data, "action_slot"):
            slot = obj.animation_data.action_slot
            if slot:
                for layer in action.layers:
                    for strip in layer.strips:
                        cb = strip.channelbag(slot, ensure=True)
                        if cb and hasattr(cb, "fcurves"):
                            for fcurve in cb.fcurves:
                                for kp in fcurve.keyframe_points:
                                    kp.interpolation = 'BEZIER'

    set_bezier_interpolation(camera_obj)
    set_bezier_interpolation(rig_obj)
    
    # If dynamic zoom is requested, run a frame-by-frame pass to calculate and keyframe the precise camera distance on every single frame
    if dynamic_zoom:
        print("Dynamic Zoom enabled. Calculating optimal camera distance for each frame...")
        # Force update of scene settings
        bpy.context.view_layer.update()
        
        for frame_idx in range(scene.frame_start, scene.frame_end + 1):
            # Move timeline to this frame to evaluate rig rotation and camera rotation curves
            scene.frame_set(frame_idx)
            # Update matrices for meshes at this frame's pose
            bpy.context.view_layer.update()
            
            # Read interpolated pitch from camera rotation_euler
            current_pitch = 90.0 - math.degrees(camera_obj.rotation_euler[0])
            
            # Calculate optimal camera distance for this frame
            d_frame = calculate_optimal_camera_distance(camera_obj, current_pitch, guitar_objs, margin=margin)
            
            # Zoom to halfway between the maximum distance for all frames and the ideal distance for this frame
            d_final = (d + d_frame) / 2.0
            
            # Reposition camera based on the frame-specific distance and pitch
            pitch_rad = math.radians(current_pitch)
            camera_obj.location = (0.0, -d_final * math.cos(pitch_rad), d_final * math.sin(pitch_rad))
            
            # Keyframe camera location on this frame
            camera_obj.keyframe_insert(data_path="location", frame=frame_idx)
            
        # Reset timeline to frame 1
        scene.frame_set(1)
        bpy.context.view_layer.update()
        print("Dynamic Zoom calculation and baking complete.")
                
    print("Animation timeline set up successfully.")
    return rig_obj, camera_obj


def find_ffmpeg():
    """Locate the ffmpeg executable on the system."""
    import subprocess
    # 1. Check if an environment variable FFMPEG_PATH is set
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path:
        if os.path.exists(env_path) and os.path.isfile(env_path):
            return env_path
        # If it's a directory, check if ffmpeg.exe exists inside
        elif os.path.exists(env_path) and os.path.isdir(env_path):
            exe = os.path.join(env_path, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if os.path.exists(exe):
                return exe

    # 2. Check if 'ffmpeg' is in the system PATH
    try:
        cmd = ["where", "ffmpeg"] if os.name == "nt" else ["which", "ffmpeg"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            path = result.stdout.strip().split('\n')[0].strip()
            if os.path.exists(path) and os.path.isfile(path):
                return path
    except Exception:
        pass

    # 3. Check known locations on Windows
    if os.name == "nt":
        known_paths = [
            r"E:\Tools\ffmpeg\bin\ffmpeg.exe",
            r"E:\Tools\video2x-4.8.1-win32-full\dependencies\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe"
        ]
        for path in known_paths:
            if os.path.exists(path):
                return path

    return "ffmpeg"  # Fallback to system command


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
    parser.add_argument("--exploded-body", "--exploded_body", "--explode-body", "--explode_body", action="store_true", help="Render only the guitar body in exploded view")
    parser.add_argument("--pitch", type=float, default=None, help="Camera pitch angle in degrees (0 = horizontal, 90 = looking straight down)")
    parser.add_argument("--guitar-rot", "--guitar_rot", default=None, help="Comma-separated rotation angles for the guitar around X, Y, Z axes in degrees (e.g. 15,30,-45)")
    parser.add_argument("--angle", default="all", choices=["front", "back", "angled", "all"], help="Camera view angle")
    parser.add_argument("--animate", action="store_true", help="Create an animation timeline and render a movie")
    parser.add_argument("--no-render-anim", "--no_render_anim", action="store_true", help="Only build the animation timeline without rendering the movie")
    parser.add_argument("--engine", default="eevee", choices=["eevee", "cycles"], help="Blender render engine")
    parser.add_argument("--material", default="gloss", help="Material preset (gloss, gloss:color, gold, chrome, chrome:color, glass, sunburst, sunburst:colors, random, or custom list)")
    parser.add_argument("--material-back", "--material_back", default="gloss:black", help="Material preset for backplate parts")
    parser.add_argument("--lighting", default="studio", choices=["studio", "dramatic", "warm", "sunset"], help="Lighting setup preset")
    parser.add_argument("--save-blend", action="store_true", help="Optionally save the .blend scene inside the renders directory")
    parser.add_argument("--preview", action="store_true", help="Fast preview mode with lower resolution, lower sample counts, and simplified EEVEE settings")
    parser.add_argument("--dynamic-zoom", "--dynamic_zoom", action="store_true", help="Calculate optimal camera distance for each individual frame instead of using a constant zoom level")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for material colors")
    
    args = parser.parse_args(args_to_parse)
    if args.no_render_anim:
        args.save_blend = True
    
    # Initialize Scene
    purge_scene()
    
    # Ensure Output Directory for renders exists
    renders_dir = os.path.join(args.config_dir, "renders")
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir)
        
    # Configure render parameters based on preview mode
    scene = bpy.context.scene
    
    # 1. Setup Engine & Samples
    if args.engine.lower() == "cycles":
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 16 if args.preview else 64
        try:
            scene.cycles.use_denoising = True  # Enable denoising for realistic, clean render output
        except AttributeError:
            pass
        
        # Try to use GPU devices if available for significantly faster render times
        try:
            preferences = bpy.context.preferences
            cycles_addon = preferences.addons.get('cycles')
            if cycles_addon:
                cycles_prefs = cycles_addon.preferences
                cycles_prefs.refresh_devices()
                
                # Check different GPU backend categories in order of preference
                gpu_device_types = ['OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL']
                gpu_activated = False
                for d_type in gpu_device_types:
                    devices = cycles_prefs.get_devices_for_type(d_type)
                    if devices:
                        cycles_prefs.compute_device_type = d_type
                        scene.cycles.device = 'GPU'
                        # Enable all GPU devices
                        for device in devices:
                            device.use = True
                        print(f"Cycles: Successfully configured GPU rendering using {d_type}")
                        gpu_activated = True
                        break
                if not gpu_activated:
                    scene.cycles.device = 'CPU'
                    print("Cycles: No GPU devices found. Defaulting to CPU rendering.")
            else:
                scene.cycles.device = 'CPU'
        except Exception as e:
            scene.cycles.device = 'CPU'
            print(f"Cycles: Error configuring GPU devices ({e}). Defaulting to CPU.")
    else:
        # EEVEE
        scene.render.engine = 'BLENDER_EEVEE'
        if hasattr(scene, "eevee"):
            try:
                # EEVEE samples settings
                scene.eevee.render_samples = 16 if args.preview else 64
            except AttributeError:
                pass
            try:
                # Enable raytracing in EEVEE-Next (Blender 4.2+)
                # Disable in preview mode for speed, enable in standard mode for quality
                scene.eevee.use_raytracing = False if args.preview else True
            except AttributeError:
                pass
            try:
                # Shadow quality
                shadow_size = '1024' if args.preview else '2048'
                scene.eevee.shadow_cascade_size = shadow_size
                scene.eevee.shadow_cube_size = shadow_size
            except AttributeError:
                pass
            try:
                # Screen Space Reflections / Ambient Occlusion for older EEVEE versions
                # Disable/simplify SSR in preview mode
                scene.eevee.use_ssr = False if args.preview else True
                scene.eevee.use_ssr_refraction = False if args.preview else True
                scene.eevee.use_gtao = True
                scene.eevee.gtao_distance = 1.0
            except AttributeError:
                pass
            
    # Color management for professional film-like realism
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = 'AgX'
            scene.view_settings.look = 'Medium High Contrast'
        except Exception:
            try:
                # Fallback to Filmic if AgX is not available (older Blender version)
                scene.view_settings.view_transform = 'Filmic'
                scene.view_settings.look = 'Medium High Contrast'
            except Exception:
                pass

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 50 if args.preview else 100
    
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
    
    # Setup Shaders and resolve random element color mappings
    has_random_element = "random" in args.material.lower() and args.material.lower().strip() != "random"
    distinct_colors = []
    num_random_per_part = 0
    
    if has_random_element:
        # Determine how many random colors we need
        parts = args.material.split(":")
        fixed_colors = []
        for p in parts[1:]:
            if p.lower().strip() != "random":
                try:
                    fixed_colors.append(parse_color(p))
                except Exception:
                    pass
        num_random_per_part = sum(1 for p in parts[1:] if p.lower().strip() == "random")
        # Pre-generate 8 parts * num_random_per_part colors
        total_random_needed = num_random_per_part * 8
        distinct_colors = generate_distinct_colors(fixed_colors, total_random_needed, seed=args.seed)
        
        # Resolve body_mat for index 0 as fallback
        body_mat_str = get_concrete_material_string(args.material, 0, distinct_colors, num_random_per_part)
        body_mat = get_material_by_name(body_mat_str)
    else:
        body_mat = get_material_by_name(args.material)
        
    chrome_mat = create_polished_chrome()
    backplate_mat = get_material_by_name(args.material_back)
    
    # Import Body Meshes
    body_objects = []
    
    if args.uncut:
        # Load single uncut body
        body_path = os.path.join(args.config_dir, "Guitar_Full_Body.stl")
        # Fallback to models/obj/guitar.obj if Full Body STL does not exist
        if not os.path.exists(body_path):
            print(f"Guitar_Full_Body.stl not found in {args.config_dir}. Falling back to default models...")
            # Detect config-specific obj
            config_name = os.path.basename(args.config_dir.strip(os.sep))
            body_path = os.path.join(models_dir, "obj", f"{config_name}.obj")
            if not os.path.exists(body_path):
                body_path = os.path.join(models_dir, "obj", "guitar.obj")
                
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
                body_path = os.path.join(models_dir, "obj", "guitar.obj")
                body_obj = import_obj(body_path, "Guitar_Body", rotation_x=90)
            else:
                body_obj = import_stl(body_path, "Guitar_Body", body_mat, scale_factor=0.1)
            if body_obj:
                body_objects.append(body_obj)
        else:
            # Parse material scheme for sliced parts
            material_mode = args.material.lower().strip()
            
            if "," in material_mode:
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
                if material_mode == "random":
                    part_mat = create_random_material(f"Random_{part_name}_{idx}")
                elif has_random_element:
                    part_mat_str = get_concrete_material_string(args.material, idx, distinct_colors, num_random_per_part)
                    part_mat = get_material_by_name(part_mat_str)
                elif custom_mats:
                    part_mat = custom_mats[idx % len(custom_mats)]
                else:
                    part_mat = body_mat
                    
                part_obj = import_stl(part_path, part_name, part_mat, scale_factor=0.1)
                if part_obj:
                    body_objects.append(part_obj)

    # Exploded view offset application
    if args.exploded_body and not args.uncut:
        print("Exploding body parts along cut lines in X and Y axis...")
        valid_objs = [obj for obj in body_objects if obj]
        if valid_objs:
            # Force update of scene matrix/geometry details before calculating center
            bpy.context.view_layer.update()
            
            # gap is the separation distance along each cut line (in Blender units)
            gap = 1.5
            
            # Explicit consistent step offsets based on the cuts:
            # - Bottom pieces: Y shift = -gap
            # - Mid pieces: Y shift = 0
            # - Top pieces: Y shift = gap
            # - Left pieces: X shift = -gap
            # - Right pieces: X shift = gap
            # - Mid pieces: X shift = 0
            # - Bottom Left piece: X shift = -0.5 * gap
            # - Bottom Right piece: X shift = 0.5 * gap
            offsets = {
                "Guitar_Bot_Left":  (-0.5 * gap, -gap),
                "Guitar_Bot_Right": (0.5 * gap,  -gap),
                "Guitar_Top_Left":  (-gap,       gap),
                "Guitar_Mid_Left":  (-gap,       0.0),
                "Guitar_Top_Right": (gap,        gap),
                "Guitar_Mid_Right": (gap,        0.0),
                "Guitar_Top_Mid":   (0.0,        gap),
                "Guitar_Mid":       (0.0,        0.0),
            }
            
            # Apply offsets to each slice
            for obj in valid_objs:
                matched = False
                for key, offset in offsets.items():
                    if key in obj.name:
                        obj.location.x += offset[0]
                        obj.location.y += offset[1]
                        print(f"Shifted {obj.name} (matched {key}) by ({offset[0]:.2f}, {offset[1]:.2f})")
                        matched = True
                        break
                if not matched:
                    print(f"Warning: No explicit offset defined for {obj.name}")
            
            # Force update to apply the new locations
            bpy.context.view_layer.update()

    # Configure all sunburst materials to center on the body size
    for mat in bpy.data.materials:
        configure_sunburst_material(mat)

    # Import Neck and Hardware (unless body-only or exploded-body is requested)
    if not args.body_only and not args.exploded_body:
        print("Importing references (neck and backplates) for full guitar view...")
        # Neck
        neck_path = os.path.join(third_party_dir, "NeckAmericanStandard.obj")
        neck_obj = import_obj(neck_path, "Neck", rotation_x=-90, rotation_z=90, offset_z=-0.85)
        if neck_obj:
            check_and_apply_neck_material(neck_obj)
            
        # Resolve electronics layout type based on config profile name
        config_name = os.path.basename(args.config_dir.strip(os.sep))
        layout = "sarcaster"
        if config_name:
            c_name = config_name.lower().strip()
            if "flying_v" in c_name or "sarcy_v" in c_name:
                layout = "flying_v"
            elif "les_paul" in c_name or "sg" in c_name or "single_cut" in c_name:
                layout = "les_paul"
                
        print(f"Using electronics layout for backplate: {layout}")
        
        elec_backplate_name = f"elec_backplate_{layout}.stl"
        stl_dir = os.path.join(models_dir, "stl")
        if not os.path.exists(os.path.join(stl_dir, elec_backplate_name)):
            elec_backplate_name = "elec_backplate.stl"

        # Backplates
        if layout == "sarcaster":
            backplate_path = os.path.join(models_dir, "stl", "backplate.stl")
            import_stl(backplate_path, "Hardware_backplate", backplate_mat)
        
        elec_backplate_path = os.path.join(stl_dir, elec_backplate_name)
        import_stl(elec_backplate_path, "Hardware_elec_backplate", backplate_mat)
        
        # Optionally, move the backplates into place relative to standard layout
        # (similar to setup_scene y offsets)
        if layout == "sarcaster":
            bp_obj = bpy.data.objects.get("Hardware_backplate")
            if bp_obj:
                bp_obj.rotation_euler[2] = math.radians(180)
                bp_obj.location.y = 40.0
                bp_obj.location.z = 2.0
            
        ebp_obj = bpy.data.objects.get("Hardware_elec_backplate")
        if ebp_obj:
            ebp_obj.location.z = 2.0
            
    # Setup initial static lighting and ground plane centered at the origin
    setup_lighting(args.lighting, (0.0, 0.0, 0.0))
    create_ground_plane(0.0, args.lighting)
    
    # Gather all guitar meshes for centering/zoom calculations
    guitar_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Ground_Plane"]
    
    if args.animate or args.no_render_anim:
        print("Configuring animation timeline...")
        anim_res = setup_animation(guitar_objs, margin=0.85, dynamic_zoom=args.dynamic_zoom)
        if anim_res:
            rig_obj, camera_obj = anim_res
            
            # Center lighting rig on the origin for the rotating guitar animation
            setup_lighting(args.lighting, (0.0, 0.0, 0.0))
            
            # Keep ground plane visible
            ground_plane = bpy.data.objects.get("Ground_Plane")
            if ground_plane:
                ground_plane.hide_render = False
                
            if not args.no_render_anim:
                sanitized_mat = args.material.replace(":", "_").replace(",", "-").replace("#", "")
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                preview_suffix = "_preview" if args.preview else ""
                zoom_suffix = "_dynzoom" if args.dynamic_zoom else ""
                seed_suffix = f"_seed{args.seed}" if args.seed is not None else ""
                
                video_name = f"animation_{sanitized_mat}_{args.lighting}_{args.engine}{preview_suffix}{zoom_suffix}{seed_suffix}_{timestamp}.mp4"
                output_moviepath = os.path.join(renders_dir, video_name)
                scene = bpy.context.scene
                
                # Check if FFMPEG format is natively supported by trying to assign it
                ffmpeg_supported = False
                try:
                    scene.render.image_settings.file_format = 'FFMPEG'
                    ffmpeg_supported = True
                except Exception:
                    pass
                    
                if ffmpeg_supported:
                    print(f"Rendering animation movie natively in Blender to: {output_moviepath}")
                    total_frames = scene.frame_end - scene.frame_start + 1
                    print(f"[ANIMATION_TOTAL_FRAMES] {total_frames}")
                    scene.render.filepath = output_moviepath
                    scene.render.ffmpeg.format = 'MPEG4'
                    scene.render.ffmpeg.codec = 'H264'
                    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
                    scene.render.ffmpeg.audio_codec = 'NONE'
                    
                    # Run native animation render
                    bpy.ops.render.render(animation=True)
                    print("Animation movie rendering complete.")
                else:
                    print("Native FFMPEG not supported in this Blender build. Rendering PNG sequence and compiling with system ffmpeg...")
                    frames_dir = os.path.join(renders_dir, f"frames_{timestamp}")
                    if not os.path.exists(frames_dir):
                        os.makedirs(frames_dir)
                        
                    # Set rendering options for PNG sequence
                    scene.render.image_settings.file_format = 'PNG'
                    scene.render.filepath = os.path.join(frames_dir, "frame_####")
                    
                    # Log total frames hook for parent process tracking
                    total_frames = scene.frame_end - scene.frame_start + 1
                    print(f"[ANIMATION_TOTAL_FRAMES] {total_frames}")
                    
                    # Render frame sequence
                    bpy.ops.render.render(animation=True)
                    
                    # Compile using system ffmpeg with high-quality H.264
                    import subprocess
                    ffmpeg_cmd = [
                        find_ffmpeg(), "-y",
                        "-r", "30",
                        "-i", os.path.join(frames_dir, "frame_%04d.png"),
                        "-c:v", "libx264",
                        "-crf", "18",
                        "-preset", "medium",
                        "-pix_fmt", "yuv420p",
                        output_moviepath
                    ]
                    print(f"Executing: {' '.join(ffmpeg_cmd)}")
                    res = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if res.returncode == 0:
                        print(f"Successfully compiled animation to: {output_moviepath}")
                        # Clean up frames folder
                        import shutil
                        shutil.rmtree(frames_dir)
                    else:
                        print(f"Error compiling movie with ffmpeg: {res.stderr.decode('utf-8', errors='ignore')}")
            else:
                print("Skipping animation rendering (--no-render-anim specified).")
    else:
        # Parse custom camera options
        custom_pitch = args.pitch
        custom_guitar_rot = parse_rotation_string(args.guitar_rot) if args.guitar_rot else None
        
        # Determine the views to render
        if custom_pitch is not None or custom_guitar_rot is not None:
            view_name = "custom" if args.angle == "all" else args.angle
            angles = [view_name]
        else:
            angles = ["front", "back", "angled"] if args.angle == "all" else [args.angle]
            
        for angle in angles:
            # Purge any previous camera
            for obj in list(bpy.data.objects):
                if obj.type == 'CAMERA':
                    bpy.data.objects.remove(obj, do_unlink=True)
                    
            # Setup Camera and Guitar Rig (applying pitch, rotation, and dynamic zoom-to-fit)
            rig_obj = setup_camera(
                view_angle=angle, 
                guitar_objs=guitar_objs, 
                custom_pitch=custom_pitch, 
                custom_guitar_rot=custom_guitar_rot,
                margin=0.85
            )
            
            # Dynamically position and face the lighting rig relative to the actual guitar body center in this view
            body_center = get_body_center_world()
            print(f"Angle '{angle}' body center in world space: ({body_center[0]:.2f}, {body_center[1]:.2f}, {body_center[2]:.2f})")
            setup_lighting(args.lighting, body_center)
            
            # Keep ground plane visible
            ground_plane = bpy.data.objects.get("Ground_Plane")
            if ground_plane:
                ground_plane.hide_render = False
                
            # Render
            output_filepath = os.path.join(renders_dir, f"{angle}.png")
            print(f"Rendering view '{angle}' to: {output_filepath}")
            
            scene.render.filepath = output_filepath
            bpy.ops.render.render(write_still=True)
            
            # Clean up the rig, restoring the meshes to their clean centered state
            cleanup_guitar_rig(rig_obj, guitar_objs)
            
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
