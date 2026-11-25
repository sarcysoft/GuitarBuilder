#include "guitar_body_mesh.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

#include "manifold/manifold.h"
#include "manifold/cross_section.h"

#include <cmath>
#include <vector>
#include <algorithm>

using namespace godot;

GuitarBodyMesh::GuitarBodyMesh() {
    belly_cut_enabled = false;
    forearm_bevel_enabled = false;
    neck_pocket_enabled = false;
}

GuitarBodyMesh::~GuitarBodyMesh() {
}

void GuitarBodyMesh::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_hip_width", "val"), &GuitarBodyMesh::set_hip_width);
    ClassDB::bind_method(D_METHOD("get_hip_width"), &GuitarBodyMesh::get_hip_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "hip_width"), "set_hip_width", "get_hip_width");

    ClassDB::bind_method(D_METHOD("set_waist_width", "val"), &GuitarBodyMesh::set_waist_width);
    ClassDB::bind_method(D_METHOD("get_waist_width"), &GuitarBodyMesh::get_waist_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "waist_width"), "set_waist_width", "get_waist_width");

    ClassDB::bind_method(D_METHOD("set_chest_width", "val"), &GuitarBodyMesh::set_chest_width);
    ClassDB::bind_method(D_METHOD("get_chest_width"), &GuitarBodyMesh::get_chest_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "chest_width"), "set_chest_width", "get_chest_width");

    ClassDB::bind_method(D_METHOD("set_shoulder_width", "val"), &GuitarBodyMesh::set_shoulder_width);
    ClassDB::bind_method(D_METHOD("get_shoulder_width"), &GuitarBodyMesh::get_shoulder_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "shoulder_width"), "set_shoulder_width", "get_shoulder_width");

    ClassDB::bind_method(D_METHOD("set_body_length", "val"), &GuitarBodyMesh::set_body_length);
    ClassDB::bind_method(D_METHOD("get_body_length"), &GuitarBodyMesh::get_body_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "body_length"), "set_body_length", "get_body_length");

    ClassDB::bind_method(D_METHOD("set_body_thickness", "val"), &GuitarBodyMesh::set_body_thickness);
    ClassDB::bind_method(D_METHOD("get_body_thickness"), &GuitarBodyMesh::get_body_thickness);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "body_thickness"), "set_body_thickness", "get_body_thickness");

    ClassDB::bind_method(D_METHOD("set_edge_radius", "val"), &GuitarBodyMesh::set_edge_radius);
    ClassDB::bind_method(D_METHOD("get_edge_radius"), &GuitarBodyMesh::get_edge_radius);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "edge_radius"), "set_edge_radius", "get_edge_radius");

    ClassDB::bind_method(D_METHOD("set_symmetric_mode", "val"), &GuitarBodyMesh::set_symmetric_mode);
    ClassDB::bind_method(D_METHOD("get_symmetric_mode"), &GuitarBodyMesh::get_symmetric_mode);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "symmetric_mode"), "set_symmetric_mode", "get_symmetric_mode");

    ClassDB::bind_method(D_METHOD("set_belly_cut_enabled", "val"), &GuitarBodyMesh::set_belly_cut_enabled);
    ClassDB::bind_method(D_METHOD("get_belly_cut_enabled"), &GuitarBodyMesh::get_belly_cut_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "belly_cut_enabled"), "set_belly_cut_enabled", "get_belly_cut_enabled");

    ClassDB::bind_method(D_METHOD("set_forearm_bevel_enabled", "val"), &GuitarBodyMesh::set_forearm_bevel_enabled);
    ClassDB::bind_method(D_METHOD("get_forearm_bevel_enabled"), &GuitarBodyMesh::get_forearm_bevel_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "forearm_bevel_enabled"), "set_forearm_bevel_enabled", "get_forearm_bevel_enabled");

    ClassDB::bind_method(D_METHOD("set_neck_pocket_enabled", "val"), &GuitarBodyMesh::set_neck_pocket_enabled);
    ClassDB::bind_method(D_METHOD("get_neck_pocket_enabled"), &GuitarBodyMesh::get_neck_pocket_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "neck_pocket_enabled"), "set_neck_pocket_enabled", "get_neck_pocket_enabled");

    ClassDB::bind_method(D_METHOD("rebuild_mesh"), &GuitarBodyMesh::rebuild_mesh);
}

void GuitarBodyMesh::_ready() {
    rebuild_mesh();
}

void GuitarBodyMesh::set_hip_width(double p_val) {
    if (hip_width != p_val) {
        hip_width = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_waist_width(double p_val) {
    if (waist_width != p_val) {
        waist_width = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_chest_width(double p_val) {
    if (chest_width != p_val) {
        chest_width = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_shoulder_width(double p_val) {
    if (shoulder_width != p_val) {
        shoulder_width = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_body_length(double p_val) {
    if (body_length != p_val) {
        body_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_body_thickness(double p_val) {
    if (body_thickness != p_val) {
        body_thickness = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_edge_radius(double p_val) {
    if (edge_radius != p_val) {
        edge_radius = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_symmetric_mode(bool p_val) {
    if (symmetric_mode != p_val) {
        symmetric_mode = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_belly_cut_enabled(bool p_val) {
    if (belly_cut_enabled != p_val) {
        belly_cut_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_forearm_bevel_enabled(bool p_val) {
    if (forearm_bevel_enabled != p_val) {
        forearm_bevel_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pocket_enabled(bool p_val) {
    if (neck_pocket_enabled != p_val) {
        neck_pocket_enabled = p_val;
        rebuild_mesh();
    }
}

// Catmull-Rom cubic spline interpolation helper
static manifold::vec2 catmull_rom(
    const manifold::vec2& p0,
    const manifold::vec2& p1,
    const manifold::vec2& p2,
    const manifold::vec2& p3,
    double t
) {
    double t2 = t * t;
    double t3 = t2 * t;

    double f0 = -0.5 * t3 + t2 - 0.5 * t;
    double f1 =  1.5 * t3 - 2.5 * t2 + 1.0;
    double f2 = -1.5 * t3 + 2.0 * t2 + 0.5 * t;
    double f3 =  0.5 * t3 - 0.5 * t2;

    return manifold::vec2{
        p0.x * f0 + p1.x * f1 + p2.x * f2 + p3.x * f3,
        p0.y * f0 + p1.y * f1 + p2.y * f2 + p3.y * f3
    };
}

void GuitarBodyMesh::rebuild_mesh() {
    using namespace manifold;

    double L = body_length; // standard reference 446.0 mm
    double scale_y = L / 446.0;
    double half_hip = hip_width * 0.5;
    double half_waist = waist_width * 0.5;
    double half_chest = chest_width * 0.5;
    double half_shoulder = shoulder_width * 0.5;

    const double r_hip = 159.0;
    const double r_waist = 115.6;
    const double r_chest = 137.5;

    // Authentic double-cutaway Stratocaster contour waypoints
    // Right side (+X, Treble side): starts from bottom tail (0,0) and sweeps CCW to the neck pocket center (0, 399.7)
    std::vector<vec2> right_keys = {
        vec2{   0.00,                                 0.00 },                // 0: Tail bottom center
        vec2{  27.23 * (half_hip / r_hip),            1.69 * scale_y },      // 1: Tail bottom curve
        vec2{  66.95 * (half_hip / r_hip),            8.80 * scale_y },      // 2: Lower bout entry
        vec2{ 111.58 * (half_hip / r_hip),           30.43 * scale_y },      // 3: Lower bout sweep
        vec2{ 145.13 * (half_hip / r_hip),           72.89 * scale_y },      // 4: Lower bout curve
        vec2{ half_hip,                             143.95 * scale_y },      // 5: Hip apex (widest lower bout ~318.6mm)
        vec2{ 146.33 * (half_hip / r_hip),          207.40 * scale_y },      // 6: Lower bout to waist transition
        vec2{ half_waist,                           256.50 * scale_y },      // 7: Waist minimum (~238mm)
        vec2{ 122.20 * (half_waist / r_waist),      309.62 * scale_y },      // 8: Waist to chest rise
        vec2{ half_chest,                           362.05 * scale_y },      // 9: Chest / Upper bout apex
        vec2{ 136.31 * (half_shoulder / 125.0),     416.30 * scale_y },      // 10: Horn outer rise
        vec2{ 124.06 * (half_shoulder / 125.0),     446.35 * scale_y },      // 11: Horn tip apex
        vec2{ 105.72 * (half_shoulder / 125.0),     421.13 * scale_y },      // 12: Horn inner slope
        vec2{  91.72 * (half_shoulder / 125.0),     388.22 * scale_y },      // 13: Horn inner flank
        vec2{  74.38,                               367.52 * scale_y },      // 14: Cutaway scoop descent
        vec2{  54.52,                               366.60 * scale_y },      // 15: Cutaway scoop floor
        vec2{  40.00,                               374.00 * scale_y },      // 16: Scoop rise to neck
        vec2{  32.00,                               388.00 * scale_y },      // 17: Neck pocket corner rise
        vec2{  28.25,                               399.69 * scale_y },      // 18: Neck pocket outer edge (56.5mm heel width)
        vec2{  14.00,                               399.69 * scale_y },      // 19: Neck shelf seat
        vec2{   0.00,                               399.69 * scale_y }       // 20: Neck pocket center
    };

    std::vector<vec2> left_keys;

    if (symmetric_mode) {
        // Mirrored symmetric cutaways
        for (int i = (int)right_keys.size() - 2; i >= 1; --i) {
            left_keys.push_back(vec2{ -right_keys[i].x, right_keys[i].y });
        }
    } else {
        // Asymmetric Stratocaster: Extended bass horn (+12mm) and shallower bass cutaway scoop
        left_keys = {
            vec2{  -14.00,                               399.69 * scale_y },
            vec2{  -28.25,                               399.69 * scale_y },
            vec2{  -32.00,                               388.00 * scale_y },
            vec2{  -40.00,                               378.00 * scale_y },
            vec2{  -56.00,                               376.00 * scale_y },
            vec2{  -78.00 * (half_shoulder / 125.0),     388.00 * scale_y },
            vec2{  -95.00 * (half_shoulder / 125.0),     418.00 * scale_y },
            vec2{ -108.00 * (half_shoulder / 125.0),     438.00 * scale_y },
            vec2{ -124.06 * (half_shoulder / 125.0),     458.00 * scale_y }, // Extended bass horn (+12mm)
            vec2{ -136.31 * (half_shoulder / 125.0),     428.00 * scale_y },
            vec2{ -half_chest,                           362.05 * scale_y },
            vec2{ -122.20 * (half_waist / r_waist),      309.62 * scale_y },
            vec2{ -half_waist,                           256.50 * scale_y },
            vec2{ -146.33 * (half_hip / r_hip),          207.40 * scale_y },
            vec2{ -half_hip,                             143.95 * scale_y },
            vec2{ -145.13 * (half_hip / r_hip),           72.89 * scale_y },
            vec2{ -111.58 * (half_hip / r_hip),           30.43 * scale_y },
            vec2{  -66.95 * (half_hip / r_hip),            8.80 * scale_y },
            vec2{  -27.23 * (half_hip / r_hip),            1.69 * scale_y }
        };
    }

    // Build seamless closed ring (start at tail, go CCW along right side, across neck, down left side)
    std::vector<vec2> all_keys = right_keys;
    for (size_t i = 0; i < left_keys.size(); ++i) {
        all_keys.push_back(left_keys[i]);
    }

    // Smooth Catmull-Rom interpolation around the closed loop
    SimplePolygon contour;
    size_t N_keys = all_keys.size();
    int num_segments_per_key = 10;

    for (size_t i = 0; i < N_keys; ++i) {
        vec2 p0 = all_keys[(i + N_keys - 1) % N_keys];
        vec2 p1 = all_keys[i];
        vec2 p2 = all_keys[(i + 1) % N_keys];
        vec2 p3 = all_keys[(i + 2) % N_keys];

        for (int step = 0; step < num_segments_per_key; ++step) {
            double t = (double)step / (double)num_segments_per_key;
            contour.push_back(catmull_rom(p0, p1, p2, p3, t));
        }
    }

    // Enforce Counter-Clockwise (CCW) winding for Manifold
    double signed_area = 0.0;
    size_t num_contour = contour.size();
    for (size_t i = 0; i < num_contour; ++i) {
        vec2 p1 = contour[i];
        vec2 p2 = contour[(i + 1) % num_contour];
        signed_area += (p1.x * p2.y - p2.x * p1.y);
    }
    if (signed_area < 0.0) {
        std::reverse(contour.begin(), contour.end());
    }

    // Create 2D CrossSection
    CrossSection cs(contour, CrossSection::FillRule::Positive);

    // Extrude 2D silhouette to 3D Solid along Z (from Z=0 back to Z=body_thickness front)
    Manifold body = Manifold::Extrude(cs.ToPolygons(), body_thickness);

    // Ergonomic Cut 1: Belly Cut (Tummy contour on rear waist Z=0, bass side only)
    if (belly_cut_enabled) {
        Manifold belly_cutter = Manifold::Cube(vec3{ 140.0, 160.0 * scale_y, 40.0 }, true)
            .Rotate(-12.0, 10.0, 0.0)
            .Translate(vec3{ -half_hip * 0.70, 250.0 * scale_y, -14.0 });
        body = body - belly_cutter;
    }

    // Ergonomic Cut 2: Forearm Bevel (Front lower bout, Z near body_thickness, treble side only)
    if (forearm_bevel_enabled) {
        Manifold forearm_cutter = Manifold::Cube(vec3{ 140.0, 150.0 * scale_y, 40.0 }, true)
            .Rotate(12.0, -8.0, 0.0)
            .Translate(vec3{ half_hip * 0.80, 140.0 * scale_y, body_thickness + 14.0 });
        body = body - forearm_cutter;
    }

    // Standard Luthier Neck Pocket Mortise (56.5mm x 76.2mm x 16.0mm)
    // Sits nested between the horns from Y = 399.7 - 76.2 to Y = 399.7
    if (neck_pocket_enabled) {
        double pocket_w = 56.5; // Standard 56mm Fender heel + 0.5mm clearance
        double pocket_len = 76.2; // 3 inches standard length
        double pocket_depth = 16.0; // 5/8 inch standard depth
        double pocket_top_y = 399.69 * scale_y;

        Manifold neck_pocket = Manifold::Cube(vec3{ pocket_w, pocket_len + 10.0, pocket_depth + 4.0 }, false)
            .Translate(vec3{ -pocket_w * 0.5, pocket_top_y - pocket_len, body_thickness - pocket_depth });
        body = body - neck_pocket;
    }

    // Calculate Smooth Vertex Normals directly in Manifold (smooth up to 50 degree dihedral angle)
    body = body.CalculateNormals(0, 50.0);

    // Extract Tessellated Mesh from Manifold
    MeshGL mesh_gl = body.GetMeshGL(0);

    if (mesh_gl.vertProperties.empty() || mesh_gl.triVerts.empty()) {
        UtilityFunctions::printerr("Manifold mesh extraction produced empty geometry.");
        return;
    }

    // Scale from mm to meters for Godot physical units (1 unit = 1 meter)
    const float scale_factor = 0.001f;
    int num_props = mesh_gl.numProp;
    size_t num_verts = mesh_gl.NumVert();

    // Center body origin at waist / bridge reference
    float center_y = (float)(240.0 * scale_y * scale_factor);
    float center_z = (float)(body_thickness * 0.5 * scale_factor);

    PackedVector3Array vertices;
    PackedVector3Array normals;
    PackedVector2Array uvs;
    PackedInt32Array indices;

    vertices.resize((int64_t)num_verts);
    normals.resize((int64_t)num_verts);
    uvs.resize((int64_t)num_verts);

    for (size_t v = 0; v < num_verts; ++v) {
        float px = mesh_gl.vertProperties[v * num_props + 0] * scale_factor;
        float py = mesh_gl.vertProperties[v * num_props + 1] * scale_factor;
        float pz = mesh_gl.vertProperties[v * num_props + 2] * scale_factor;

        // Godot coordinates: X = right, Y = up, Z = towards viewer
        vertices[(int64_t)v] = Vector3(px, py - center_y, pz - center_z);

        if (num_props >= 6) {
            float nx = mesh_gl.vertProperties[v * num_props + 3];
            float ny = mesh_gl.vertProperties[v * num_props + 4];
            float nz = mesh_gl.vertProperties[v * num_props + 5];
            normals[(int64_t)v] = Vector3(nx, ny, nz);
        } else {
            normals[(int64_t)v] = Vector3(0, 0, 1);
        }

        float u = (px + (float)half_hip * scale_factor) / ((float)hip_width * scale_factor);
        float v_coord = py / ((float)L * scale_factor);
        uvs[(int64_t)v] = Vector2(u, v_coord);
    }

    size_t num_indices = mesh_gl.triVerts.size();
    indices.resize((int64_t)num_indices);
    for (size_t i = 0; i < num_indices; ++i) {
        indices[(int64_t)i] = (int32_t)mesh_gl.triVerts[i];
    }

    Array arrays;
    arrays.resize(Mesh::ARRAY_MAX);
    arrays[Mesh::ARRAY_VERTEX] = vertices;
    if (num_props >= 6) {
        arrays[Mesh::ARRAY_NORMAL] = normals;
    }
    arrays[Mesh::ARRAY_TEX_UV] = uvs;
    arrays[Mesh::ARRAY_INDEX] = indices;

    Ref<ArrayMesh> godot_mesh;
    godot_mesh.instantiate();
    godot_mesh->add_surface_from_arrays(Mesh::PRIMITIVE_TRIANGLES, arrays);
    set_mesh(godot_mesh);
}
