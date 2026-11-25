// Physical Chrome Hardware Model: Standard Strat-style Hardware
// Includes chrome bridge plate with 6 adjustable block saddles,
// 3 single-coil pickups with chrome covers/pole pieces, and chrome output jack plate.
$fn = 48;

// ============================================================================
// 1. STRAT HARDTAIL / TREMOLO BRIDGE WITH 6 CHROME SADDLES
// ============================================================================
module bridge_saddle(w = 1.0, len = 2.1, h = 0.52) {
    difference() {
        // Main saddle block with beveled front
        hull() {
            translate([-w/2, -len/2, 0]) cube([w, len - 0.3, h]);
            translate([-w/2, len/2 - 0.3, 0]) cube([w, 0.1, h * 0.7]);
        }
        // String slot groove down the center
        translate([0, 0, h])
            rotate([-90, 0, 0])
            cylinder(r = 0.08, h = len + 0.2, center = true, $fn = 16);
        // Height adjustment allen screw holes
        translate([-w/3, -len/3, h - 0.2]) cylinder(r = 0.12, h = 0.3, $fn = 16);
        translate([ w/3, -len/3, h - 0.2]) cylinder(r = 0.12, h = 0.3, $fn = 16);
    }
    // Allen screws slightly raised
    translate([-w/3, -len/3, h - 0.05]) cylinder(r = 0.10, h = 0.12, $fn = 16);
    translate([ w/3, -len/3, h - 0.05]) cylinder(r = 0.10, h = 0.12, $fn = 16);
}

module strat_bridge() {
    // Bridge sits at Y=24.5, Z=2.1 (flush on body face)
    plate_w = 7.6;
    plate_len = 4.2;
    plate_h = 0.25;

    // Chrome base plate
    difference() {
        hull() {
            translate([-plate_w/2 + 0.4, 22.8, 2.1]) cylinder(r = 0.4, h = plate_h);
            translate([ plate_w/2 - 0.4, 22.8, 2.1]) cylinder(r = 0.4, h = plate_h);
            translate([-plate_w/2 + 0.4, 26.6, 2.1]) cylinder(r = 0.4, h = plate_h);
            translate([ plate_w/2 - 0.4, 26.6, 2.1]) cylinder(r = 0.4, h = plate_h);
        }
        // Front mounting screw countersinks (6 vintage screws)
        for (i = [-2.65 : 1.06 : 2.65]) {
            translate([i, 23.2, 2.1 + plate_h - 0.08])
                cylinder(r1 = 0.15, r2 = 0.30, h = 0.10);
        }
    }

    // 6 Vintage-style chrome mounting screws
    for (i = [-2.65 : 1.06 : 2.65]) {
        translate([i, 23.2, 2.1 + plate_h - 0.02])
            cylinder(r = 0.24, h = 0.06, $fn = 24);
    }

    // 6 Chrome block saddles sitting on plate
    for (i = [0 : 5]) {
        sx = -2.65 + i * 1.06;
        // Natural staggered intonation offsets
        sy_offset = (i == 0 || i == 3) ? 0.0 : (i == 1 || i == 4) ? 0.12 : 0.24;
        translate([sx, 24.5 + sy_offset, 2.1 + plate_h])
            bridge_saddle(w = 1.02, len = 1.9, h = 0.48);

        // Rear intonation screw & spring
        translate([sx, 25.9, 2.1 + plate_h + 0.22]) {
            rotate([90, 0, 0]) {
                cylinder(r = 0.14, h = 0.7, center = true, $fn = 16);
                // Screw head
                translate([0, 0, -0.4]) cylinder(r = 0.22, h = 0.12, $fn = 20);
            }
        }
    }
}

// ============================================================================
// 2. SINGLE COIL PICKUPS (CHROME COVERS & POLE PIECES)
// ============================================================================
module single_coil_pickup() {
    cover_w = 7.0;
    cover_len = 1.8;
    cover_h = 1.35;
    z_base = 1.4; // Sits in cavity and protrudes above body (Z=2.1)

    // Main rounded pickup cover
    hull() {
        translate([-cover_w/2 + 0.8, -cover_len/2 + 0.8, z_base])
            cylinder(r = 0.8, h = cover_h);
        translate([ cover_w/2 - 0.8, -cover_len/2 + 0.8, z_base])
            cylinder(r = 0.8, h = cover_h);
        translate([-cover_w/2 + 0.8,  cover_len/2 - 0.8, z_base])
            cylinder(r = 0.8, h = cover_h);
        translate([ cover_w/2 - 0.8,  cover_len/2 - 0.8, z_base])
            cylinder(r = 0.8, h = cover_h);
    }

    // 2 Mounting tabs with chrome height screws
    for (s = [-3.8, 3.8]) {
        translate([s, 0, z_base]) {
            cylinder(r = 0.55, h = 0.25);
            // Screw head
            translate([0, 0, 0.25]) cylinder(r = 0.22, h = 0.15, $fn = 20);
        }
    }

    // 6 Chrome pole pieces slightly protruding through cover
    for (i = [0 : 5]) {
        px = -2.60 + i * 1.04;
        // Staggered vintage pole heights
        ph = (i == 2 || i == 3) ? 0.12 : (i == 1 || i == 4) ? 0.08 : 0.05;
        translate([px, 0, z_base + cover_h])
            cylinder(r = 0.24, h = ph, $fn = 24);
    }
}

// ============================================================================
// 3. OUTPUT JACK PLATE
// ============================================================================
module jack_plate() {
    // Sits at Y=26.8, angled to match body contour
    translate([-3.2, 26.8, 2.1]) {
        difference() {
            // Football jack plate rim
            scale([1.8, 0.9, 1.0])
                cylinder(r = 1.4, h = 0.22, $fn = 48);
            // Recessed cup hole
            translate([0, 0, -0.1])
                cylinder(r = 0.75, h = 0.5, $fn = 32);
        }
        // Recessed cup
        translate([0, 0, -0.6]) {
            difference() {
                cylinder(r1 = 0.55, r2 = 0.75, h = 0.65, $fn = 32);
                translate([0, 0, -0.1]) cylinder(r1 = 0.40, r2 = 0.60, h = 0.85, $fn = 32);
            }
            // 1/4" Hex Nut
            cylinder(r = 0.42, h = 0.15, $fn = 6);
            // Jack barrel center
            translate([0, 0, -0.3]) cylinder(r = 0.32, h = 0.35, $fn = 24);
        }
        // 2 Mounting screws
        translate([-1.8, 0, 0.18]) cylinder(r = 0.18, h = 0.08, $fn = 20);
        translate([ 1.8, 0, 0.18]) cylinder(r = 0.18, h = 0.08, $fn = 20);
    }
}

// ============================================================================
// COMBINED HARDWARE ASSEMBLY
// ============================================================================
union() {
    // 1. Bridge
    strat_bridge();

    // 2. Neck Pickup (Y=9.6)
    translate([0, 9.6, 0])
        single_coil_pickup();

    // 3. Middle Pickup (Y=15.4)
    translate([0, 15.4, 0])
        single_coil_pickup();

    // 4. Bridge Pickup (Y=20.1, angled -7 deg)
    translate([0, 20.1, 0])
        rotate([0, 0, -7])
        single_coil_pickup();

    // 5. Output Jack
    jack_plate();
}
