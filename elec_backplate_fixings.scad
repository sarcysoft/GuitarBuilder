// Import the rounded_poly module
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

        //translate([6.25, 17.5,-2.15]) screw();
        translate([12.75, 11.5,-2.15]) screw();
        translate([8.75, 23.5,-2.15]) screw();
    }    
}

elec_backplate_fixings();