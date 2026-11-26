import os

os.makedirs('project/assets/neck', exist_ok=True)

parts = {
    'neck_shaft_strat.stl': 'neck_shaft.obj',
    'fretboard_strat.stl': 'fretboard.obj',
    'frets_strat.stl': 'frets.obj',
    'nut_strat.stl': 'nut.obj',
    'tuners_strat.stl': 'tuners.obj'
}

y_base = 29.76
z_base = 1.80

for src_name, dst_name in parts.items():
    src_path = os.path.join('legacy_poc/models/stl', src_name)
    dst_path = os.path.join('project/assets/neck', dst_name)
    verts = []
    faces = []
    v_map = {}
    
    with open(src_path, 'r', errors='ignore') as f:
        curr_tri = []
        for line in f:
            p = line.strip().split()
            if len(p) == 4 and p[0] == 'vertex':
                # Convert cm to meters and shift so heel starts at origin (0, 0, 0)
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
        out.write(f'# GuitarBuilder {dst_name}\n')
        out.write(f'o {dst_name[:-4]}\n')
        for v in verts:
            out.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        for f in faces:
            out.write(f'f {f[0]} {f[1]} {f[2]}\n')
    
    size_kb = os.path.getsize(dst_path) / 1024
    print(f'Converted {src_name} -> {dst_name}: {len(verts)} verts, {len(faces)} faces ({size_kb:.1f} KB)')
