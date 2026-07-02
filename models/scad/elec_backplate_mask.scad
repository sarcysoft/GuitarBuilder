// Import the rounded_poly module
use <_rounded_poly.scad>
include <_electronics_layout.scad>
$fn=128;

module elec_backplate_mask()
{
    translate([0,0,-2.1]) color("green") union() {
        cylinder_between_points(mask_p1, mask_p2, radius=1.75, height=0.31);
        cylinder_between_points(mask_p1, mask_p3, radius=1.75, height=0.31);
        cylinder_between_points(mask_p3, mask_p4, radius=1.75, height=0.31);
        cylinder_between_points(mask_p4, mask_p2, radius=1.75, height=0.31);
    }
}

elec_backplate_mask();