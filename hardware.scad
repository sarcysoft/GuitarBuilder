// Import the rounded_poly module
use <rounded_poly.scad>

// Create a filled rectangle using the cylinder_path function
// Parameters for the rectangle
rect_width = 4.2;
rect_height = 6.8;
corner_rad = 0.8;
rect_depth = 2.1;

// Define the four corners of the rectangle
neck_points = [
    [0, 0],
    [rect_width, 0],
    [rect_width, rect_height],
    [0, rect_height]
];

// Create the filled rectangle with rounded edges

translate([-2.1,0,0])
    cylinder_path(neck_points, radius=corner_rad, height=rect_depth, fill_polygon=true);

translate([-2.65,9.6,0])
    cylinder_between_points([0, 0], [5.3, 0], radius=0.9, height=2.1);
    
translate([-2.65,9.6 + 5.8,0])
    cylinder_between_points([0, 0], [5.3, 0], radius=0.9, height=2.1);

translate([-2.65,9.6 + 11.1,0]) rotate([0,0,-7])
    cylinder_between_points([0, 0], [5.3, 0], radius=0.9, height=2.1);    
    
translate([-3.2,9.6 + 5.8 + 11.3,0])
    cylinder_between_points([0, 0], [6.4, 0], radius=0.8, height=2.1);
    