// Les Paul Style Guitar Neck
// 24.75" scale length (62.865 cm), 22 frets, 14-degree tilted 3x3 open-book headstock
include <_fret_calc.scad>

part = "all"; // Options: "all", "shaft", "fretboard", "frets", "nut", "tuners"
$fn = 36;

// --- Key Dimensions (cm / Blender Units) ---
scale_len   = 62.865; // 24.75 inches in cm
nut_y       = 77.30;
nut_w       = 4.30;   // 43.0 mm
heel_y      = 31.00;   // Extends cleanly past 22nd fret at Y=32.08
heel_w      = 5.68;   // 56.8 mm
fretboard_h = 0.60;   // 6 mm thick
fretboard_z = 4.00;   // Fretboard base sits at Z=4.0
num_frets   = 22;

// Headstock geometry
headstock_angle = 14; // degrees tilted back
headstock_hinge_y = 77.64;
headstock_hinge_z = 4.60;
headstock_thick = 1.45;

// Tuner positions on headstock (relative to headstock local coords)
// 3x3 layout: local Y offsets from hinge
tuner_local_ys = [3.5, 7.5, 11.5];
tuner_local_x  = 1.95;

// ==========================================
// 1. FRETBOARD
// ==========================================
module lp_fretboard() {
    color("SaddleBrown") {
        difference() {
            // Tapered fretboard slab with squared tenon end
            hull() {
                // At Nut
                translate([-nut_w / 2, nut_y - 0.05, fretboard_z])
                    cube([nut_w, 0.1, fretboard_h]);
                // At Heel
                translate([-heel_w / 2, heel_y, fretboard_z])
                    cube([heel_w, 0.1, fretboard_h]);
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
module lp_frets() {
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
module lp_nut() {
    color("FloralWhite") {
        translate([0, nut_y, fretboard_z + fretboard_h - 0.25])
            guitar_nut(nut_w = nut_w, nut_thick = 0.34, nut_h = 0.55);
    }
}

// ==========================================
// 4. HEADSTOCK 2D OPEN-BOOK SILHOUETTE
// ==========================================
module lp_headstock_2d() {
    // Classic Gibson "open book" double-arch silhouette
    // Local coords: Y=0 is at hinge, Y extends to ~18cm
    polygon(points = [
        [-nut_w / 2, 0],
        [-2.3, 2.0],
        [-2.7, 5.0],
        [-3.4, 9.0],
        [-4.1, 13.0],
        [-4.3, 16.0],
        [-3.6, 17.5],
        [-2.0, 17.8],  // left wing peak
        [-0.8, 17.0],  // left inner slope
        [ 0.0, 16.4],  // center open-book notch dip
        [ 0.8, 17.0],  // right inner slope
        [ 2.0, 17.8],  // right wing peak
        [ 3.6, 17.5],
        [ 4.3, 16.0],
        [ 4.1, 13.0],
        [ 3.4, 9.0],
        [ 2.7, 5.0],
        [ 2.3, 2.0],
        [ nut_w / 2, 0]
    ]);
}

// Helper module for transformed headstock
module lp_headstock_transform() {
    translate([0, headstock_hinge_y, headstock_hinge_z])
        rotate([-headstock_angle, 0, 0])
        children();
}

// ==========================================
// 5. TUNERS (3x3 KEYSTONE TULIP)
// ==========================================
module lp_tuners() {
    color("Gold") {
        lp_headstock_transform() {
            for (ly = tuner_local_ys) {
                // Bass side (left, -X, button points -X)
                translate([-tuner_local_x, ly, 0])
                    tuner_peg(type = "vintage", post_h = 2.4, post_r = 0.30, button_dir = -1, headstock_thick = headstock_thick);

                // Treble side (right, +X, button points +X)
                translate([tuner_local_x, ly, 0])
                    tuner_peg(type = "vintage", post_h = 2.4, post_r = 0.30, button_dir = 1, headstock_thick = headstock_thick);
            }
        }
    }
}

// ==========================================
// 6. NECK SHAFT & HEEL
// ==========================================
module lp_shaft() {
    color("BurlyWood") {
        union() {
            difference() {
                union() {
                    // A. HEEL TENON BLOCK (fits into guitar neck pocket)
                    // Squared tenon block from Y=32.5 to Y=38.5, Z=2.0 to 4.0
                    hull() {
                        translate([-heel_w / 2, 38.5, 2.0]) cube([heel_w, 0.1, 2.0]);
                        translate([-heel_w / 2, heel_y, 2.0]) cube([heel_w, 0.1, 2.0]);
                    }

                    // B. NECK SHAFT CARVE (rounded 50s/60s C-profile)
                    difference() {
                        union() {
                            // Heel transition (Y=38.5) down to 12th fret (Y=45.9)
                            hull() {
                                translate([0, 38.5, fretboard_z])
                                    scale([heel_w / 2, 1, 2.0])
                                    rotate([-90, 0, 0])
                                    cylinder(r = 1, h = 0.1, $fn = 28);
                                translate([0, 45.9, fretboard_z])
                                    scale([fret_width(45.9, nut_y, heel_y, nut_w, heel_w) / 2, 1, 2.2])
                                    rotate([-90, 0, 0])
                                    cylinder(r = 1, h = 0.1, $fn = 28);
                            }
                            // 12th fret down to 1st fret (Y=73.8) and nut (Y=77.0)
                            hull() {
                                translate([0, 45.9, fretboard_z])
                                    scale([fret_width(45.9, nut_y, heel_y, nut_w, heel_w) / 2, 1, 2.2])
                                    rotate([-90, 0, 0])
                                    cylinder(r = 1, h = 0.1, $fn = 28);
                                translate([0, 73.8, fretboard_z])
                                    scale([fret_width(73.8, nut_y, heel_y, nut_w, heel_w) / 2, 1, 2.05])
                                    rotate([-90, 0, 0])
                                    cylinder(r = 1, h = 0.1, $fn = 28);
                                translate([0, 77.0, fretboard_z])
                                    scale([nut_w / 2, 1, 2.0])
                                    rotate([-90, 0, 0])
                                    cylinder(r = 1, h = 0.1, $fn = 28);
                            }
                        }
                        // Remove upper half: neck carve must remain strictly UNDER fretboard (Z <= fretboard_z)
                        translate([-15, 35, fretboard_z])
                            cube([30, 45, 10]);
                    }

                    // Shelf supporting the nut from nut_y to headstock_hinge_y
                    translate([-nut_w / 2, nut_y, fretboard_z])
                        cube([nut_w, headstock_hinge_y - nut_y + 0.01, fretboard_h - 0.25]);

                    // C. VOLUTE / BLEND TRANSITION BEHIND NUT (Bottom / back blend)
                    hull() {
                        translate([-nut_w / 2, 76.5, 2.0]) cube([nut_w, 0.5, 2.0]);
                        lp_headstock_transform()
                            translate([-nut_w / 2, 0.5, -headstock_thick]) cube([nut_w, 0.5, 0.5]);
                    }

                    // D. ANGLED HEADSTOCK SLAB
                    lp_headstock_transform() {
                        translate([0, 0, -headstock_thick])
                            linear_extrude(height = headstock_thick, convexity = 10)
                            lp_headstock_2d();
                    }
                }

                // Tuner peg holes through angled headstock
                lp_headstock_transform() {
                    for (ly = tuner_local_ys) {
                        translate([-tuner_local_x, ly, -headstock_thick - 0.5])
                            cylinder(r = 0.45, h = headstock_thick + 1.0, $fn = 24);
                        translate([ tuner_local_x, ly, -headstock_thick - 0.5])
                            cylinder(r = 0.45, h = headstock_thick + 1.0, $fn = 24);
                    }
                }
            }
        }
    }
}

// ==========================================
// RENDER DISPATCH
// ==========================================
if (part == "all") {
    lp_shaft();
    lp_fretboard();
    lp_frets();
    lp_nut();
    lp_tuners();
} else if (part == "shaft") {
    lp_shaft();
} else if (part == "fretboard") {
    lp_fretboard();
} else if (part == "frets") {
    lp_frets();
} else if (part == "nut") {
    lp_nut();
} else if (part == "tuners") {
    lp_tuners();
}
