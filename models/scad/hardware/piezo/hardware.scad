// Physical Chrome Hardware Model: Piezo Hardware Variant
// Includes chrome piezo bridge plate with individual saddles and mounting screws.
$fn = 48;

module piezo_saddle(w = 1.0, len = 2.0, h = 0.50) {
    difference() {
        hull() {
            translate([-w/2, -len/2, 0]) cube([w, len - 0.2, h]);
            translate([-w/2, len/2 - 0.2, 0]) cube([w, 0.1, h * 0.75]);
        }
        // String slot
        translate([0, 0, h])
            rotate([-90, 0, 0])
            cylinder(r = 0.08, h = len + 0.2, center = true, $fn = 16);
    }
}

module piezo_bridge() {
    plate_w = 7.4;
    plate_len = 3.8;
    plate_h = 0.25;

    // Bridge base plate at Y=26.0, Z=2.1
    hull() {
        translate([-plate_w/2 + 0.3, 24.5, 2.1]) cylinder(r = 0.3, h = plate_h);
        translate([ plate_w/2 - 0.3, 24.5, 2.1]) cylinder(r = 0.3, h = plate_h);
        translate([-plate_w/2 + 0.3, 27.5, 2.1]) cylinder(r = 0.3, h = plate_h);
        translate([ plate_w/2 - 0.3, 27.5, 2.1]) cylinder(r = 0.3, h = plate_h);
    }

    // 6 Chrome block saddles
    for (i = [0 : 5]) {
        sx = -2.65 + i * 1.06;
        sy_offset = (i == 0 || i == 3) ? 0.0 : (i == 1 || i == 4) ? 0.10 : 0.20;
        translate([sx, 26.0 + sy_offset, 2.1 + plate_h])
            piezo_saddle(w = 1.0, len = 1.8, h = 0.45);
    }

    // 4 Corner mounting screws
    for (cx = [-3.0, 3.0]) {
        for (cy = [24.8, 27.2]) {
            translate([cx, cy, 2.1 + plate_h])
                cylinder(r = 0.22, h = 0.06, $fn = 20);
        }
    }
}

union() {
    piezo_bridge();
}
