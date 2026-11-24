// Stratocaster Style Guitar Neck
// 25.5" scale length (64.77 cm), 22 frets, flat stepped 6-in-line headstock
include <_fret_calc.scad>

part = "all"; // Options: "all", "shaft", "fretboard", "frets", "nut", "tuners"
$fn = 36;

// --- Key Dimensions (cm / Blender Units) ---
scale_len   = 64.77; // 25.5 inches in cm
nut_y       = 79.20;
nut_w       = 4.28;  // 42.8 mm
heel_y      = 31.75;
heel_w      = 5.58;  // 55.8 mm
fretboard_h = 0.60;  // 6 mm thick
fretboard_z = 4.00;  // Fretboard base sits at Z=4.0 (flush with body top)
num_frets   = 22;

// Tuner positions (6 in-line on bass side)
tuner_x = -1.35;
tuner_ys = [82.6, 84.9, 87.2, 89.5, 91.8, 94.1];
headstock_face_z = 3.20;

// ==========================================
// 1. FRETBOARD
// ==========================================
module strat_fretboard() {
    color("SaddleBrown") {
        difference() {
            // Tapered fretboard slab
            hull() {
                // At Nut
                translate([-nut_w / 2, nut_y - 0.05, fretboard_z])
                    cube([nut_w, 0.1, fretboard_h]);
                // At Heel
                translate([-heel_w / 2, heel_y + 0.8, fretboard_z])
                    cube([heel_w, 0.1, fretboard_h]);
                // Rounded heel end
                translate([0, heel_y + 0.8, fretboard_z])
                    cylinder(r = heel_w / 2, h = fretboard_h, $fn = 32);
            }
            // Cut slot for nut
            translate([-nut_w / 2 - 0.1, nut_y, fretboard_z + fretboard_h - 0.25])
                cube([nut_w + 0.2, 0.35, 0.3]);
        }
    }
}

// ==========================================
// 2. FRETS
// ==========================================
module strat_frets() {
    color("Silver") {
        for (n = [1 : num_frets]) {
            d = fret_dist(n, scale_len);
            y = nut_y - d;
            w = fret_width(y, nut_y, heel_y, nut_w, heel_w);
            translate([0, y, fretboard_z + fretboard_h])
                fret_wire(w = w - 0.06);
        }
    }
}

// ==========================================
// 3. NUT
// ==========================================
module strat_nut() {
    color("FloralWhite") {
        translate([0, nut_y, fretboard_z + fretboard_h - 0.25])
            guitar_nut(nut_w = nut_w, nut_thick = 0.34, nut_h = 0.55);
    }
}

// ==========================================
// 4. TUNERS (6 IN-LINE)
// ==========================================
module strat_tuners() {
    color("Silver") {
        for (ty = tuner_ys) {
            translate([tuner_x, ty, headstock_face_z])
                tuner_peg(type = "modern", post_h = 2.4, post_r = 0.30, button_dir = -1);
        }
    }
}

// ==========================================
// 5. HEADSTOCK PROFILE (2D Extrusion)
// ==========================================
module strat_headstock_2d() {
    // Smooth polygon approximating the classic Stratocaster headstock contour
    polygon(points = [
        [-nut_w / 2, 79.5],
        [-2.3, 81.0],
        [-2.6, 83.0],
        [-2.8, 86.0],
        [-2.8, 91.0],
        [-2.6, 94.0],
        [-2.0, 96.5],
        [-0.5, 97.6],
        [ 1.2, 97.4],
        [ 2.8, 96.0],
        [ 3.8, 94.0],
        [ 4.5, 91.5],
        [ 4.0, 89.0],
        [ 2.6, 87.5],
        [ 2.2, 85.0],
        [ 2.5, 82.5],
        [ nut_w / 2, 79.5]
    ]);
}

// ==========================================
// 6. NECK SHAFT & HEEL
// ==========================================
module strat_shaft() {
    color("BurlyWood") {
        difference() {
            union() {
                // A. HEEL BLOCK (fits in guitar neck pocket)
                // Width = heel_w, Z = 2.0 to 4.0, Y = 31.75 to 39.0
                hull() {
                    translate([-heel_w / 2, 38.5, 2.0]) cube([heel_w, 0.1, 2.0]);
                    translate([-heel_w / 2, heel_y + 1.0, 2.0]) cube([heel_w, 0.1, 2.0]);
                    // Rounded heel end
                    translate([0, heel_y + 1.0, 2.0]) cylinder(r = heel_w / 2, h = 2.0, $fn = 32);
                }

                // B. NECK SHAFT CARVE (C-profile half-ellipse along length)
                // Transitioning from heel (Y=38.5) down to nut (Y=78.5)
                difference() {
                    union() {
                        hull() {
                            // Heel transition cross section
                            translate([0, 38.5, fretboard_z])
                                scale([heel_w / 2, 1, 2.0])
                                rotate([-90, 0, 0])
                                cylinder(r = 1, h = 0.1, $fn = 28);
                            // 12th fret cross section (thickness ~ 2.15cm)
                            translate([0, 46.8, fretboard_z])
                                scale([fret_width(46.8, nut_y, heel_y, nut_w, heel_w) / 2, 1, 2.1])
                                rotate([-90, 0, 0])
                                cylinder(r = 1, h = 0.1, $fn = 28);
                        }
                        hull() {
                            // 12th fret cross section
                            translate([0, 46.8, fretboard_z])
                                scale([fret_width(46.8, nut_y, heel_y, nut_w, heel_w) / 2, 1, 2.1])
                                rotate([-90, 0, 0])
                                cylinder(r = 1, h = 0.1, $fn = 28);
                            // 1st fret cross section (thickness ~ 1.95cm)
                            translate([0, 75.5, fretboard_z])
                                scale([fret_width(75.5, nut_y, heel_y, nut_w, heel_w) / 2, 1, 1.95])
                                rotate([-90, 0, 0])
                                cylinder(r = 1, h = 0.1, $fn = 28);
                            // Nut transition
                            translate([0, 78.8, fretboard_z])
                                scale([nut_w / 2, 1, 1.90])
                                rotate([-90, 0, 0])
                                cylinder(r = 1, h = 0.1, $fn = 28);
                        }
                    }
                    // Remove upper half: neck shaft carve must sit strictly UNDER fretboard (Z <= fretboard_z)
                    translate([-15, 35, fretboard_z])
                        cube([30, 48, 10]);
                }

                // C. HEADSTOCK BASE & TRANSITION SCOOP
                // Transition ramp from nut to flat headstock plane
                hull() {
                    translate([-nut_w / 2, 78.5, 2.1]) cube([nut_w, 0.5, 1.9]);
                    translate([-nut_w / 2, 80.5, 1.8]) cube([nut_w, 0.5, headstock_face_z - 1.8]);
                }

                // Flat Headstock Extrusion
                translate([0, 0, 1.80])
                    linear_extrude(height = headstock_face_z - 1.80, convexity = 10)
                    strat_headstock_2d();
            }

            // Tuner peg holes through headstock
            for (ty = tuner_ys) {
                translate([tuner_x, ty, 1.5])
                    cylinder(r = 0.45, h = 2.5, $fn = 24);
            }
        }
    }
}

// ==========================================
// RENDER DISPATCH
// ==========================================
if (part == "all") {
    strat_shaft();
    strat_fretboard();
    strat_frets();
    strat_nut();
    strat_tuners();
} else if (part == "shaft") {
    strat_shaft();
} else if (part == "fretboard") {
    strat_fretboard();
} else if (part == "frets") {
    strat_frets();
} else if (part == "nut") {
    strat_nut();
} else if (part == "tuners") {
    strat_tuners();
}
