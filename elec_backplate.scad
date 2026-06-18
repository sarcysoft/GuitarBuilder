// Import the rounded_poly module
use <rounded_poly.scad>
use <elec_backplate_mask.scad>
use <elec_backplate_fixings.scad>
$fn=128;


difference()
{
    elec_backplate_mask();
    
    elec_backplate_fixings();
}