// Import the rounded_poly module
use <rounded_poly.scad>
use <backplate_mask.scad>
use <backplate_fixings.scad>
$fn=128;


difference()
{
    backplate_mask();
    
    backplate_fixings();
}