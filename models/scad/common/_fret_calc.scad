// _fret_calc.scad - Mathematical fret calculations, neck profiles, and tuner geometry
$fn = 48;

// Distance from nut to fret n for scale length L (cm)
// Standard 12-TET formula: d_n = L * (1 - 2^(-n/12))
function fret_dist(n, L) = L * (1 - pow(2, -n / 12));

// Linear width calculation between nut and heel at position y
function fret_width(y, nut_y, heel_y, nut_w, heel_w) =
    nut_w + (heel_w - nut_w) * ((nut_y - y) / (nut_y - heel_y));

// Fret wire crown module
// Crown sits on top of fretboard (centered at origin, spanning across X from -w/2 to w/2)
module fret_wire(w, crown_w = 0.24, crown_h = 0.11) {
    translate([-w / 2, 0, 0])
        rotate([0, 90, 0])
        scale([crown_h / (crown_w / 2), 1, 1])
        cylinder(r = crown_w / 2, h = w, $fn = 24);
}

// Slotted guitar nut (bone/ivory)
// Placed at Y = [nut_y, nut_y + nut_thick]
module guitar_nut(nut_w, nut_thick = 0.35, nut_h = 0.85, string_spacing = 3.5) {
    difference() {
        // Main contoured nut blank
        hull() {
            translate([-nut_w / 2, 0, 0]) cube([nut_w, nut_thick, nut_h * 0.7]);
            translate([-nut_w / 2 + 0.1, 0, nut_h * 0.7]) cube([nut_w - 0.2, nut_thick * 0.7, nut_h * 0.3]);
        }
        // 6 string slots (E to e)
        for (i = [0 : 5]) {
            x = -string_spacing / 2 + i * (string_spacing / 5);
            slot_r = 0.03 + (5 - i) * 0.008; // bass strings slightly thicker
            translate([x, -0.05, nut_h - slot_r * 0.8])
                rotate([-10, 0, 0])
                cylinder(r = slot_r, h = nut_thick * 1.5, $fn = 16);
        }
    }
}

// Tuning machine assembly: post, collar/bushing, shaft, and button
// type = "modern" (Strat kidney button) or "vintage" (LP keystone tulip button)
module tuner_peg(type = "modern", post_h = 2.4, post_r = 0.3, button_dir = -1) {
    // 1. Collar / Bushing on headstock face
    translate([0, 0, 0]) {
        cylinder(r = 0.52, h = 0.22, $fn = 24); // washer flange
        cylinder(r = 0.42, h = 0.45, $fn = 6);  // hex collar
    }

    // 2. String Post
    translate([0, 0, 0]) {
        cylinder(r = post_r, h = post_h, $fn = 24);
        // String through-hole
        translate([0, 0, post_h * 0.75])
            rotate([90, 0, 0])
            cylinder(r = 0.08, h = post_r * 3, center = true, $fn = 16);
        // Post cap bevel
        translate([0, 0, post_h])
            sphere(r = post_r, $fn = 20);
    }

    // 3. Gear housing on back of headstock (underneath headstock)
    translate([0, 0, -1.5]) {
        // Housing box
        hull() {
            translate([-0.55, -0.65, 0]) cube([1.1, 1.3, 0.9]);
            translate([0, 0.45, 0.45]) rotate([0, 90, 0]) cylinder(r = 0.45, h = 1.1, center = true, $fn = 20);
        }

        // Horizontal tuner shaft out towards button
        // button_dir is +1 (points +X) or -1 (points -X)
        translate([0, 0, 0.45])
            rotate([0, button_dir * 90, 0])
            cylinder(r = 0.18, h = 1.6, $fn = 20);

        // Tuning Button / Key
        if (type == "vintage") {
            // Keystone / Tulip button (Les Paul style)
            translate([button_dir * 2.1, 0, 0.45])
                rotate([0, 0, 90])
                scale([1.0, 0.35, 1.4])
                hull() {
                    sphere(r = 0.55, $fn = 20);
                    translate([0, 0, 0.4]) sphere(r = 0.75, $fn = 20);
                }
        } else {
            // Modern Kidney / Oval button (Strat style)
            translate([button_dir * 2.0, 0, 0.45])
                rotate([0, 0, 90])
                scale([1.1, 0.4, 0.8])
                sphere(r = 0.85, $fn = 24);
        }
    }
}
