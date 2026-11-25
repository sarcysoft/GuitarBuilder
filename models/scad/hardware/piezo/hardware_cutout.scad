// Import the rounded_poly module
use <../../common/_rounded_poly.scad>
$fn=128;



union()
{
    translate([-2.1,0,0])
        cylinder_path([[0, 0],[4.2, 0],[4.2, 6.8],[0, 6.8]],
                        radius=0.8, height=2.1, fill_polygon=true);

    translate([-1.8,0.9,-3]) cylinder(5,0.2,0.2);
    translate([1.8,0.9,-3]) cylinder(5,0.2,0.2);
    translate([-1.8,5.9,-3]) cylinder(5,0.2,0.2);
    translate([1.8,5.9,-3]) cylinder(5,0.2,0.2);

    translate([-2.1,0,-3])
        cylinder_path([[0, 0],[4.2, 0],[4.2, 6.8],[0, 6.8]],
                        radius=0.9, height=1.05, fill_polygon=true);
             
                
    translate([-2.7,26.0,0])
        cylinder_path([[0, 0],[5.4, 0]],
                        radius=0.5, height=2.5, fill_polygon=true);
 
    translate([-3.35 ,27.1 ,0]) cylinder(2.5,0.2,0.2);
    translate([0 ,27.1 ,0]) cylinder(2.5,0.2,0.2);
    translate([3.35 ,27.1 ,0]) cylinder(2.5,0.2,0.2);
    translate([-3.35 ,24.4 ,0]) cylinder(2.5,0.2,0.2);
    translate([3.35 ,24.4 ,0]) cylinder(2.5,0.2,0.2);
    
    translate([-3.5,24.4,-3])
        cylinder_path([[0, 0],[7.0, 0],[7.0, 2.5],[0, 2.5]],
                        radius=0.8, height=3.1, fill_polygon=true);
}    