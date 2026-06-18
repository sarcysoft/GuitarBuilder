// Import the rounded_poly module
use <rounded_poly.scad>
$fn=128;

module backplate_mask()
{
    union()
    {

        translate([-4.5,16.2,-2.1])
            cylinder_path([[0, 0],[9.0, 0],[9.0, 10.7],[0, 10.7]],
                            radius=1.0, height=0.31, fill_polygon=true);
                  

        translate([-4.5,9.6,-2.1])
            cylinder_between_points([0, 0], [9, 0], radius=1.5, height=0.31);
    }
}

backplate_mask();