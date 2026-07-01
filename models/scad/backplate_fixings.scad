// Import the rounded_poly module
$fn=128;

module screw()
{
    union() {
        cylinder(0.25, 0.4, 0.2);
        cylinder(1.5, 0.2, 0.2);
    }
}

module backplate_fixings()
{
    union()
    {

        translate([-4.75,16.2,-2.15]) screw();
        translate([4.75,16.2,-2.15]) screw();
        translate([-4.75,26.55,-2.15]) screw();
        translate([4.75,26.55,-2.15]) screw();
                        

        translate([-5.0,9.6,-2.15]) screw();
        translate([5.0,9.6,-2.15]) screw();
    }    
}

backplate_fixings();