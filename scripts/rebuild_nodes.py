import bpy
import os
import sys

def rebuild_nodes():
    print("Starting Geometry Nodes rebuild...")
    
    # 1. Get Guitar Body object
    guitar_body = bpy.data.objects.get("Guitar Body")
    if not guitar_body:
        print("Error: 'Guitar Body' object not found.")
        sys.exit(1)
        
    # 2. Get Geometry Nodes modifier
    geom_modifier = None
    for mod in guitar_body.modifiers:
        if mod.type == 'NODES':
            geom_modifier = mod
            break
            
    if not geom_modifier:
        print("Error: Geometry Nodes modifier not found on 'Guitar Body'.")
        sys.exit(1)
        
    node_group = geom_modifier.node_group
    print(f"Modifying Node Group: {node_group.name}")
    
    # 3. Add "Symmetric Mode" Boolean Input if it doesn't exist
    symmetric_input_name = "Symmetric Mode"
    
    # Check in interface sockets
    has_symmetric_mode = False
    for item in node_group.interface.items_tree:
        if item.name == symmetric_input_name and getattr(item, 'in_out', None) == 'INPUT':
            has_symmetric_mode = True
            break
            
    if not has_symmetric_mode:
        print("Adding 'Symmetric Mode' socket to interface...")
        node_group.interface.new_socket(name=symmetric_input_name, in_out='INPUT', socket_type='NodeSocketBool')
    else:
        print("'Symmetric Mode' socket already exists.")
        
    # 4. Define Left/Right pairs to redirect
    SYMMETRIC_PAIRS = [
        ("Left Hip Height", "Right Hip Height"),
        ("Left Waist Height", "Right Waist Height"),
        ("Left Chest Height", "Right Chest Height"),
        ("Left Shoulder Height", "Right Shoulder Height"),
        ("Left Shoulder Curve", "Right Shoulder Curve"),
        ("Left Shoulder Blade", "Right Shoulder Blade"),
        ("Left Shoulder Slope", "Right Shoulder Slope"),
        ("Left Collar Height", "Right Collar Height"),
        ("Left Collar Bone", "Right Collar Bone"),
        ("Left Neck Curve", "Right Neck Curve")
    ]
    
    # Locate a NodeGroupInput node to connect from
    input_nodes = [n for n in node_group.nodes if n.bl_idname == 'NodeGroupInput']
    if not input_nodes:
        print("Error: No NodeGroupInput node found in node group.")
        sys.exit(1)
    input_node = input_nodes[0]
    
    # Clean up any existing switch nodes we created in a previous run to allow clean regeneration
    existing_switches = [n for n in node_group.nodes if n.name.startswith("Switch_Right_")]
    if existing_switches:
        print(f"Cleaning up {len(existing_switches)} old Switch nodes...")
        for n in existing_switches:
            node_group.nodes.remove(n)
            
    # Process each pair
    for left_name, right_name in SYMMETRIC_PAIRS:
        print(f"Setting up symmetry for: {right_name} -> {left_name}")
        
        # Create a new Switch node
        switch_node = node_group.nodes.new(type="GeometryNodeSwitch")
        switch_node.input_type = 'FLOAT'
        switch_node.name = f"Switch_{right_name.replace(' ', '_')}"
        switch_node.label = f"Symmetric {right_name}"
        
        # Find all destination sockets currently linked to the right_name socket on ANY NodeGroupInput node
        destinations = []
        for inp_node in input_nodes:
            right_socket = inp_node.outputs.get(right_name)
            if right_socket and right_socket.is_linked:
                for link in right_socket.links:
                    destinations.append(link.to_socket)
                    
        # If there are destinations, route them through the switch
        if destinations:
            print(f"  Found {len(destinations)} destination sockets for {right_name}. Routing through switch...")
            
            # Connect input control to the switch
            node_group.links.new(input_node.outputs[symmetric_input_name], switch_node.inputs['Switch'])
            # Connect True input (use Left value)
            node_group.links.new(input_node.outputs[left_name], switch_node.inputs['True'])
            # Connect False input (use Right value)
            node_group.links.new(input_node.outputs[right_name], switch_node.inputs['False'])
            
            # Connect switch output to all destinations
            for dest in destinations:
                node_group.links.new(switch_node.outputs['Output'], dest)
        else:
            print(f"  Warning: No active destinations found for {right_name}. Skipping link routing.")
            
    print("Geometry Nodes rebuild completed successfully.")
    
if __name__ == "__main__":
    rebuild_nodes()
    # Save the file
    bpy.ops.wm.save_mainfile()
    print("Saved changes to guitar.blend.")
