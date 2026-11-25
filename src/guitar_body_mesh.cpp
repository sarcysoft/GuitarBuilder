#include "guitar_body_mesh.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

#include "manifold/manifold.h"
#include "manifold/cross_section.h"

#include <cmath>
#include <vector>

using namespace godot;

GuitarBodyMesh::GuitarBodyMesh() {
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

    double L = body_length;
    double half_hip = hip_width * 0.5;
    double half_waist = waist_width * 0.5;
    double half_chest = chest_width * 0.5;
    double half_shoulder = shoulder_width * 0.5;
    double neck_pocket_half = 28.0; // Standard 56mm Fender heel width

    // Define 2D key perimeter waypoints (Right side first, from tail Y=0 to neck joint Y=L)
    std::vector<vec2> right_keys = {
        vec2{ 0.0, 0.0 },                        // 0: Tail center
        vec2{ half_hip * 0.65, L * 0.06 },       // 1: Butt flare
        vec2{ half_hip, L * 0.22 },              // 2: Hip apex (lower bout)
        vec2{ half_hip * 0.95, L * 0.35 },       // 3: Hip to waist transition
        vec2{ half_waist, L * 0.48 },            // 4: Waist pinch minimum
        vec2{ half_chest * 0.92, L * 0.60 },     // 5: Waist to chest transition
        vec2{ half_chest, L * 0.72 },            // 6: Chest apex (upper bout)
        vec2{ half_shoulder, L * 0.90 },         // 7: Shoulder / Horn flare
        vec2{ half_shoulder * 0.85, L * 0.96 },  // 8: Horn tip
        vec2{ neck_pocket_half * 1.5, L * 0.91 },// 9: Horn inner scoop
        vec2{ neck_pocket_half, L }              // 10: Neck pocket edge
    };

    // Interpolate smoothly through right-side waypoints
    SimplePolygon contour;
    int num_segments_per_key = 12;

    for (size_t i = 0; i < right_keys.size() - 1; ++i) {
        vec2 p0 = (i == 0) ? right_keys[0] : right_keys[i - 1];
        vec2 p1 = right_keys[i];
        vec2 p2 = right_keys[i + 1];
        vec2 p3 = (i + 2 < right_keys.size()) ? right_keys[i + 2] : p2;

        for (int step = 0; step < num_segments_per_key; ++step) {
            double t = (double)step / (double)num_segments_per_key;
            contour.push_back(catmull_rom(p0, p1, p2, p3, t));
        }
    }
    // Add neck pocket top boundary
    contour.push_back(right_keys.back());
    contour.push_back(vec2{ -neck_pocket_half, L });

    // Left side points (symmetric or asymmetric)
    std::vector<vec2> left_keys;
    for (int i = (int)right_keys.size() - 1; i >= 0; --i) {
        left_keys.push_back(vec2{ -right_keys[i].x, right_keys[i].y });
    }

    for (size_t i = 0; i < left_keys.size() - 1; ++i) {
        vec2 p0 = (i == 0) ? left_keys[0] : left_keys[i - 1];
        vec2 p1 = left_keys[i];
        vec2 p2 = left_keys[i + 1];
        vec2 p3 = (i + 2 < left_keys.size()) ? left_keys[i + 2] : p2;

        for (int step = 0; step < num_segments_per_key; ++step) {
            double t = (double)step / (double)num_segments_per_key;
            contour.push_back(catmull_rom(p0, p1, p2, p3, t));
        }
    }

    // Create 2D CrossSection
    CrossSection cs(contour, CrossSection::FillRule::Positive);

    // Optional 2D Fillet / Rounding
    if (edge_radius > 1.0) {
        cs = cs.Offset(edge_radius, CrossSection::JoinType::Round);
        cs = cs.Offset(-edge_radius, CrossSection::JoinType::Round);
    }

    // Extrude 2D silhouette to 3D Solid
    Manifold body = Manifold::Extrude(cs.ToPolygons(), body_thickness);

    // Ergonomic Cut 1: Belly Cut (Tummy contour on rear waist)
    if (belly_cut_enabled) {
        Manifold belly_cutter = Manifold::Cube(vec3{ half_hip * 2.5, L * 0.6, 60.0 }, true)
            .Rotate(belly_cut_angle, 0.0, 0.0)
            .Translate(vec3{ 0.0, L * 0.45, -15.0 });
        body = body - belly_cutter;
    }

    // Ergonomic Cut 2: Forearm Bevel (Front lower bout)
    if (forearm_bevel_enabled) {
        Manifold forearm_cutter = Manifold::Cube(vec3{ half_hip * 1.5, L * 0.5, 60.0 }, true)
            .Rotate(-forearm_bevel_angle, 12.0, 0.0)
            .Translate(vec3{ half_hip * 0.75, L * 0.25, body_thickness + 15.0 });
        body = body - forearm_cutter;
    }

    // Standard Luthier Neck Pocket Mortise
    if (neck_pocket_enabled) {
        double pocket_w = 56.5; // 56mm + 0.5mm tolerance
        double pocket_len = 76.2; // 3 inches
        double pocket_depth = 16.0; // 5/8 inch

        Manifold neck_pocket = Manifold::Cube(vec3{ pocket_w, pocket_len + 10.0, pocket_depth + 5.0 }, false)
            .Translate(vec3{ -pocket_w * 0.5, L - pocket_len, body_thickness - pocket_depth });
        body = body - neck_pocket;
    }

    // Extract Tessellated Mesh from Manifold
    MeshGL mesh_gl = body.GetMeshGL();

    if (mesh_gl.vertProperties.empty() || mesh_gl.triVerts.empty()) {
        UtilityFunctions::printerr("Manifold mesh extraction produced empty geometry.");
        return;
    }

    // Convert to Godot ArrayMesh via SurfaceTool
    Ref<SurfaceTool> st;
    st.instantiate();
    st->begin(Mesh::PRIMITIVE_TRIANGLES);

    // Scale from mm to meters for Godot physical units (1 unit = 1 meter)
    const float scale_factor = 0.001f;
    int num_props = mesh_gl.numProp;

    // Center body origin at waist / bridge reference
    float center_y = (float)(L * 0.45 * scale_factor);
    float center_z = (float)(body_thickness * 0.5 * scale_factor);

    for (size_t i = 0; i < mesh_gl.triVerts.size(); ++i) {
        uint32_t vert_idx = mesh_gl.triVerts[i];
        float px = mesh_gl.vertProperties[vert_idx * num_props + 0] * scale_factor;
        float py = mesh_gl.vertProperties[vert_idx * num_props + 1] * scale_factor;
        float pz = mesh_gl.vertProperties[vert_idx * num_props + 2] * scale_factor;

        // Godot coordinates: X = right, Y = up, Z = towards viewer
        // Guitar: thickness along Z, length along Y
        Vector3 pos(px, py - center_y, pz - center_z);

        // UV mapping based on bounding box
        Vector2 uv((px + (float)half_hip * scale_factor) / (float)hip_width * 1000.0f, py / (float)L * 1000.0f);
        st->set_uv(uv);

        st->add_vertex(pos);
    }

    st->generate_normals();
    st->generate_tangents();

    Ref<ArrayMesh> godot_mesh = st->commit();
    set_mesh(godot_mesh);
}
