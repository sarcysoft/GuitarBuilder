// Import the rounded_poly module
use <_rounded_poly.scad>
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
    translate([9.0, 22.5, 0.7]) rotate([0,0,-60]) pickup_selector();

    translate([7.5, 18.0 ,0.7]) volume_knob();
    translate([12.0 ,13.5 ,0.7]) volume_knob();
    
    translate([11.0, 6.0 ,-0.3]) rotate([0,0,45]) audio_jack();
    
    translate([0,0,-2.8]) color("green") {
        cylinder_between_points([7.5, 18.0], [12.0, 13.5], radius=1.5, height=4.6);
        cylinder_between_points([7.5, 18.0], [8.75, 21.5], radius=1.5, height=4.6);
        cylinder_between_points([8.75, 21.5], [10.75, 17.5], radius=1.5, height=4.6);
        cylinder_between_points([10.75, 17.5], [12.0, 13.5], radius=1.5, height=4.6);
    }

    translate([9.0, 15.0, 0.0])  color("gray")
        rotate([90, 0, -10]) cylinder(6, 0.6, 0.6);
        
    translate([3.0, 21.0, 0.0])  color("gray")
        rotate([0, 90, 0]) cylinder(6, 0.8, 0.8);
 }

