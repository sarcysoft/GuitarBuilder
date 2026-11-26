import os

os.makedirs('project/assets/neck/strat', exist_ok=True)
os.makedirs('project/assets/neck/les_paul', exist_ok=True)

# 1. Stratocaster Neck Conversion
# Shaft heel min Y: 29.96 cm. Z heel base: 1.80 cm.
strat_parts = {
    'neck_shaft_strat.stl': ('neck_shaft.obj', 29.96, 1.80, False),
    'fretboard_strat.stl': ('fretboard.obj', 29.96, 1.80, True),  # Overhang enabled
    'frets_strat.stl': ('frets.obj', 29.96, 1.80, False),
    'nut_strat.stl': ('nut.obj', 29.96, 1.80, False),
    'tuners_strat.stl': ('tuners.obj', 29.96, 1.80, False)
}

for src_name, (dst_name, y_base, z_base, is_fretboard) in strat_parts.items():
    src_path = os.path.join('legacy_poc/models/stl', src_name)
    dst_path = os.path.join('project/assets/neck/strat', dst_name)
    verts = []
    faces = []
    v_map = {}
    
    with open(src_path, 'r', errors='ignore') as f:
        curr_tri = []
        for line in f:
            p = line.strip().split()
            if len(p) == 4 and p[0] == 'vertex':
                raw_x = float(p[1])
                raw_y = float(p[2])
                raw_z = float(p[3])
                
                # In fretboard, if near heel (Y < 32 cm), extend overhang slightly by 6mm (0.6cm)
                # so the 22nd fret fretboard overhangs cleanly over the guitar body face
                if is_fretboard and raw_y < 31.5:
                    # Taper the extension smoothly: max 6mm at the heel tip
                    factor = max(0.0, (31.5 - raw_y) / (31.5 - 29.76))
                    raw_y -= 0.6 * factor
                
                x = raw_x * 0.01
                y = (raw_y - y_base) * 0.01
                z = (raw_z - z_base) * 0.01
                pt = (round(x, 6), round(y, 6), round(z, 6))
                if pt not in v_map:
                    v_map[pt] = len(verts) + 1
                    verts.append(pt)
                curr_tri.append(v_map[pt])
                if len(curr_tri) == 3:
                    faces.append(curr_tri)
                    curr_tri = []
                    
    with open(dst_path, 'w') as out:
        out.write(f'# GuitarBuilder Strat {dst_name}\n')
        out.write(f'o {dst_name[:-4]}\n')
        for v in verts:
            out.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        for fc in faces:
            out.write(f'f {fc[0]} {fc[1]} {fc[2]}\n')
    print(f'Converted Strat {src_name} -> {dst_path} ({len(verts)} verts, {len(faces)} faces)')

# 2. Les Paul Neck Conversion (Square heel, 3+3 headstock)
# Shaft heel min Y: 31.00 cm. Z heel base: 2.00 cm.
lp_parts = {
    'neck_shaft_les_paul.stl': ('neck_shaft.obj', 31.00, 2.00),
    'fretboard_les_paul.stl': ('fretboard.obj', 31.00, 2.00),
    'frets_les_paul.stl': ('frets.obj', 31.00, 2.00),
    'nut_les_paul.stl': ('nut.obj', 31.00, 2.00),
    'tuners_les_paul.stl': ('tuners.obj', 31.00, 2.00)
}

for src_name, (dst_name, y_base, z_base) in lp_parts.items():
    src_path = os.path.join('legacy_poc/models/stl', src_name)
    dst_path = os.path.join('project/assets/neck/les_paul', dst_name)
    verts = []
    faces = []
    v_map = {}
    
    with open(src_path, 'r', errors='ignore') as f:
        curr_tri = []
        for line in f:
            p = line.strip().split()
            if len(p) == 4 and p[0] == 'vertex':
                x = float(p[1]) * 0.01
                y = (float(p[2]) - y_base) * 0.01
                z = (float(p[3]) - z_base) * 0.01
                pt = (round(x, 6), round(y, 6), round(z, 6))
                if pt not in v_map:
                    v_map[pt] = len(verts) + 1
                    verts.append(pt)
                curr_tri.append(v_map[pt])
                if len(curr_tri) == 3:
                    faces.append(curr_tri)
                    curr_tri = []
                    
    with open(dst_path, 'w') as out:
        out.write(f'# GuitarBuilder Les Paul {dst_name}\n')
        out.write(f'o {dst_name[:-4]}\n')
        for v in verts:
            out.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        for fc in faces:
            out.write(f'f {fc[0]} {fc[1]} {fc[2]}\n')
    print(f'Converted Les Paul {src_name} -> {dst_path} ({len(verts)} verts, {len(faces)} faces)')
