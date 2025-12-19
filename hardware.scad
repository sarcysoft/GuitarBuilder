// Import the rounded_poly module
use <rounded_poly.scad>
$fn=128;

module pickup() {
    translate([-2.65,0,0])
        cylinder_between_points([0, 0], [5.3, 0], radius=0.9, height=2.1);
    translate([-3.9,0,0]) cylinder(2.1, 0.2, 0.2);
    translate([3.9,0,0]) cylinder(2.1, 0.2, 0.2);
}



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

    translate([-3.5,12.6,0])
        cylinder_path([[0, 0],[7.0, 0],[7.0, 8.0],[0, 8.0]],
                        radius=0.8, height=1.7, fill_polygon=true);

    translate([-3.5,16.2,-3])
        cylinder_path([[0, 0],[7.0, 0],[7.0, 10.7],[0, 10.7]],
                        radius=0.8, height=3.1, fill_polygon=true);
                
                
    translate([0,9.6,0]) pickup();
    translate([-3.15,9.6,-3])
        cylinder_between_points([0, 0], [6.3, 0], radius=1.3, height=4.7);
        
    translate([0,15.4,0]) pickup();

    translate([0,20.1,0]) rotate([0,0,-7]) pickup();    
        
    for(i = [0 : 0.2 : 1])
        translate([-2.65 + i * 5.3,24.5 ,0]) cylinder(2,0.2,0.2);
 
    translate([-3.2,26.8,0])
        cylinder_between_points([0, 0], [6.4, 0], radius=0.8, height=2.1);
    translate([-3.2,26.8,-3])
        cylinder_between_points([0, 0], [6.4, 0], radius=0.9, height=4.7);

    translate([0,13,0.8]) rotate([90,0,0]) cylinder(3, 0.5, 0.5);

    translate([-1.6,16,-1.0]) rotate([90,0,0]) cylinder(4, 0.2, 0.2);
    translate([1.6,16,-1.0]) rotate([90,0,0]) cylinder(4, 0.2, 0.2);
}    