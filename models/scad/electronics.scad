// Import the rounded_poly module
use <_rounded_poly.scad>
include <_electronics_layout.scad>
$fn=128;

module volume_knob() {
    cylinder(1.1, 1.2, 1.2);
    cylinder(2.0, 0.4, 0.4);
    cylinder(2.9, 0.3, 0.3);
}

module audio_jack() {
    translate([0.0, 0.0, 1.0]) cylinder(1.5, 0.24, 0.24);
    translate([0.0, 7.1, 1.0]) cylinder(1.5, 0.24, 0.24);
    
    translate([0,2.5,-1.0]) {
        intersection() {
            scale([1,3.5,1]) cylinder(3.5, 1.13, 1.13);
            translate([-1.13,-1,0]) cube([2.26, 4.9, 3.5]);
        }
    }
}

module pickup_selector() {
    cylinder_between_points([0, 0], [6.0, 0], radius=0.3, height=1.1);
    cylinder_between_points([1, 0], [5.0, 0], radius=0.15, height=2.5);
    translate([0.5,0,0]) cylinder(2.5, 0.1, 0.1);
    translate([5.5,0,0]) cylinder(2.5, 0.1, 0.1);
}

union() {
    translate(switch_pos) rotate(switch_rot) pickup_selector();

    translate(vol1_pos) volume_knob();
    translate(vol2_pos) volume_knob();
    
    translate(jack_pos) rotate(jack_rot) audio_jack();
    
    translate([0,0,-2.8]) color("green") {
        cylinder_between_points(cav_p1, cav_p2, radius=1.5, height=4.6);
        cylinder_between_points(cav_p1, cav_p3, radius=1.5, height=4.6);
        cylinder_between_points(cav_p3, cav_p4, radius=1.5, height=4.6);
        cylinder_between_points(cav_p4, cav_p2, radius=1.5, height=4.6);
    }

    // Wiring channels using cylinder_between_points for dynamic placement
    color("gray") {
        cylinder_between_points(jack_wire_start, jack_wire_end, radius=0.6, height=1.2);
        cylinder_between_points(pickup_wire_start, pickup_wire_end, radius=0.8, height=1.6);
    }
}
