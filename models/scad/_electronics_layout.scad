// Layout type (can be overridden via command line -D "layout_type=\"...\"")
layout_type = "sarcaster"; // options: "sarcaster", "flying_v", "les_paul"

// Default (Sarcaster)
vol1_pos = (layout_type == "flying_v") ? [8.5, 11.0, 0.7] :
           (layout_type == "les_paul") ? [8.0, 12.0, 0.7] :
           [7.5, 18.0, 0.7];

vol2_pos = (layout_type == "flying_v") ? [10.5, 7.5, 0.7] :
           (layout_type == "les_paul") ? [11.5, 10.0, 0.7] :
           [12.0, 13.5, 0.7];

switch_pos = (layout_type == "flying_v") ? [6.5, 14.5, 0.7] :
             (layout_type == "les_paul") ? [7.5, 15.0, 0.7] :
             [9.0, 22.5, 0.7];

switch_rot = (layout_type == "flying_v") ? [0, 0, -60] :
             (layout_type == "les_paul") ? [0, 0, -60] :
             [0, 0, -60];

jack_pos = (layout_type == "flying_v") ? [12.5, 4.0, -0.3] :
           (layout_type == "les_paul") ? [13.0, 7.0, -0.3] :
           [11.0, 6.0, -0.3];

jack_rot = (layout_type == "flying_v") ? [0, 0, 45] :
           (layout_type == "les_paul") ? [0, 0, 45] :
           [0, 0, 45];

// Cavity points
cav_p1 = (layout_type == "flying_v") ? [6.5, 14.5] : (layout_type == "les_paul") ? [7.5, 15.0] : [7.5, 18.0];
cav_p2 = (layout_type == "flying_v") ? [12.5, 4.0] : (layout_type == "les_paul") ? [11.5, 10.0] : [12.0, 13.5];
cav_p3 = (layout_type == "flying_v") ? [7.5, 16.0] : (layout_type == "les_paul") ? [8.75, 17.0] : [8.75, 21.5];
cav_p4 = (layout_type == "flying_v") ? [11.5, 6.0] : (layout_type == "les_paul") ? [12.0, 12.0] : [10.75, 17.5];

// Mask points
mask_p1 = (layout_type == "flying_v") ? [6.5, 14.5] : (layout_type == "les_paul") ? [7.5, 15.0] : [7.5, 18.0];
mask_p2 = (layout_type == "flying_v") ? [13.0, 3.0]  : (layout_type == "les_paul") ? [12.0, 9.0]  : [12.5, 12.5];
mask_p3 = (layout_type == "flying_v") ? [7.5, 16.0]  : (layout_type == "les_paul") ? [8.75, 17.5] : [8.75, 22.5];
mask_p4 = (layout_type == "flying_v") ? [11.5, 6.0]  : (layout_type == "les_paul") ? [12.0, 12.0] : [10.75, 17.5];

// Screw points
screw_p1 = (layout_type == "flying_v") ? [13.25, 2.0, -2.15] : (layout_type == "les_paul") ? [12.25, 8.0, -2.15] : [12.75, 11.5, -2.15];
screw_p2 = (layout_type == "flying_v") ? [7.5, 17.0, -2.15]  : (layout_type == "les_paul") ? [8.75, 18.5, -2.15]  : [8.75, 23.5, -2.15];

// Wire channels
pickup_wire_start = (layout_type == "flying_v") ? [3.0, 14.5] : (layout_type == "les_paul") ? [3.0, 15.0] : [3.0, 21.0];
pickup_wire_end   = (layout_type == "flying_v") ? [6.5, 14.5] : (layout_type == "les_paul") ? [7.5, 15.0] : [9.0, 21.0];

jack_wire_start = (layout_type == "flying_v") ? [10.5, 7.5]  : (layout_type == "les_paul") ? [11.5, 10.0] : [9.0, 15.0];
jack_wire_end   = (layout_type == "flying_v") ? [12.5, 4.0]  : (layout_type == "les_paul") ? [13.0, 7.0]  : [8.0, 9.0];
