// Import the rounded_poly module
use <rounded_poly.scad>
$fn=128;

module elec_backplate_mask()
{
    translate([0,0,-2.1]) color("green") union() {
        cylinder_between_points([7.5, 18.0], [12.5, 12.5], radius=1.75, height=0.31);
        cylinder_between_points([7.5, 18.0], [8.75, 22.5], radius=1.75, height=0.31);
        cylinder_between_points([8.75, 22.5], [10.75, 17.5], radius=1.75, height=0.31);
        cylinder_between_points([10.75, 17.5], [12.5, 12.5], radius=1.75, height=0.31);
    }
}

elec_backplate_mask();