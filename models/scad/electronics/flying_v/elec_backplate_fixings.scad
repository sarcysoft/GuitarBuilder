// Import the rounded_poly module
include <_electronics_layout.scad>
$fn=128;

module screw()
{
    union() {
        cylinder(0.25, 0.4, 0.2);
        cylinder(1.5, 0.2, 0.2);
    }
}

module elec_backplate_fixings()
{
    union()
    {
        translate(screw_p1) screw();
        translate(screw_p2) screw();
    }    
}

elec_backplate_fixings();