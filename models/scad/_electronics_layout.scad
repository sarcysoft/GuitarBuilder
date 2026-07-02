// Layout type (can be overridden via command line -D "layout_type=\"...\"")
layout_type = "sarcaster"; // options: "sarcaster", "flying_v", "les_paul"

// Default (Sarcaster)
vol1_pos = (layout_type == "flying_v") ? [5.5, 11.0, 0.7] :
           (layout_type == "les_paul") ? [6.75, 14.5, 0.7] :
           [7.5, 18.0, 0.7];

vol2_pos = (layout_type == "flying_v") ? [7.5, 7.5, 0.7] :
           (layout_type == "les_paul") ? [11.75, 14.5, 0.7] :
           [12.0, 13.5, 0.7];

switch_pos = (layout_type == "flying_v") ? [3.5, 14.5, 0.7] :
             (layout_type == "les_paul") ? [9.25, 19.0, 0.7] :
             [9.0, 22.5, 0.7];

switch_rot = (layout_type == "flying_v") ? [0, 0, -55] :
             (layout_type == "les_paul") ? [0, 0, -90] :
             [0, 0, -60];

jack_pos = (layout_type == "flying_v") ? [9.5, 4.0, -0.3] :
           (layout_type == "les_paul") ? [12.0, 7.5, -0.3] :
           [11.0, 6.0, -0.3];

jack_rot = (layout_type == "flying_v") ? [0, 0, 45] :
           (layout_type == "les_paul") ? [0, 0, 45] :
           [0, 0, 45];

// Cavity points
cav_p1 = (layout_type == "flying_v") ? [3.5, 14.5] : (layout_type == "les_paul") ? [6.75, 14.5] : [7.5, 18.0];
cav_p2 = (layout_type == "flying_v") ? [9.5, 4.0] : (layout_type == "les_paul") ? [11.75, 14.5] : [12.0, 13.5];
cav_p3 = (layout_type == "flying_v") ? [4.5, 16.0] : (layout_type == "les_paul") ? [9.25, 19.0] : [8.75, 21.5];
cav_p4 = (layout_type == "flying_v") ? [8.5, 6.0] : (layout_type == "les_paul") ? [12.0, 7.5] : [10.75, 17.5];

// Mask points
mask_p1 = (layout_type == "flying_v") ? [3.5, 14.5] : (layout_type == "les_paul") ? [5.25, 14.5] : [7.5, 18.0];
mask_p2 = (layout_type == "flying_v") ? [10.0, 3.0]  : (layout_type == "les_paul") ? [13.25, 14.5]  : [12.5, 12.5];
mask_p3 = (layout_type == "flying_v") ? [4.5, 16.0]  : (layout_type == "les_paul") ? [9.25, 20.5] : [8.75, 22.5];
mask_p4 = (layout_type == "flying_v") ? [8.5, 6.0]  : (layout_type == "les_paul") ? [12.5, 6.0] : [10.75, 17.5];

// Screw points
screw_p1 = (layout_type == "flying_v") ? [10.25, 2.0, -2.15] : (layout_type == "les_paul") ? [13.25, 11.5, -2.15] : [12.75, 11.5, -2.15];
screw_p2 = (layout_type == "flying_v") ? [4.5, 17.0, -2.15]  : (layout_type == "les_paul") ? [5.25, 17.5, -2.15]  : [8.75, 23.5, -2.15];

// Wire channels
pickup_wire_start = (layout_type == "flying_v") ? [0.0, 14.5] : (layout_type == "les_paul") ? [3.0, 19.0] : [3.0, 21.0];
pickup_wire_end   = (layout_type == "flying_v") ? [3.5, 14.5] : (layout_type == "les_paul") ? [9.25, 19.0] : [9.0, 21.0];

jack_wire_start = (layout_type == "flying_v") ? [7.5, 7.5]  : (layout_type == "les_paul") ? [11.75, 14.5] : [9.0, 15.0];
jack_wire_end   = (layout_type == "flying_v") ? [9.5, 4.0]  : (layout_type == "les_paul") ? [12.0, 7.5]  : [8.0, 9.0];
