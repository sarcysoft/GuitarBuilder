// Import the rounded_poly module
use <../../common/_rounded_poly.scad>
$fn=128;

module backplate_mask()
{
    union()
    {

        translate([-4.5,22.2,-2.1])
            cylinder_path([[0, 0],[9.0, 0],[9.0, 4.7],[0, 4.7]],
                            radius=1.0, height=0.31, fill_polygon=true);

    }
}

backplate_mask();