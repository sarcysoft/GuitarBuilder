#include "guitar_body_mesh.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

#include "manifold/manifold.h"
#include "manifold/cross_section.h"
#include "manifold/polygon.h"

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

    ClassDB::bind_method(D_METHOD("set_horn_reach", "val"), &GuitarBodyMesh::set_horn_reach);
    ClassDB::bind_method(D_METHOD("get_horn_reach"), &GuitarBodyMesh::get_horn_reach);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "horn_reach"), "set_horn_reach", "get_horn_reach");

    ClassDB::bind_method(D_METHOD("set_horn_roundness", "val"), &GuitarBodyMesh::set_horn_roundness);
    ClassDB::bind_method(D_METHOD("get_horn_roundness"), &GuitarBodyMesh::get_horn_roundness);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "horn_roundness"), "set_horn_roundness", "get_horn_roundness");

    // Independent side properties
    ClassDB::bind_method(D_METHOD("set_treble_hip_width", "val"), &GuitarBodyMesh::set_treble_hip_width);
    ClassDB::bind_method(D_METHOD("get_treble_hip_width"), &GuitarBodyMesh::get_treble_hip_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_hip_width"), "set_treble_hip_width", "get_treble_hip_width");

    ClassDB::bind_method(D_METHOD("set_bass_hip_width", "val"), &GuitarBodyMesh::set_bass_hip_width);
    ClassDB::bind_method(D_METHOD("get_bass_hip_width"), &GuitarBodyMesh::get_bass_hip_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_hip_width"), "set_bass_hip_width", "get_bass_hip_width");

    ClassDB::bind_method(D_METHOD("set_treble_waist_width", "val"), &GuitarBodyMesh::set_treble_waist_width);
    ClassDB::bind_method(D_METHOD("get_treble_waist_width"), &GuitarBodyMesh::get_treble_waist_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_waist_width"), "set_treble_waist_width", "get_treble_waist_width");

    ClassDB::bind_method(D_METHOD("set_bass_waist_width", "val"), &GuitarBodyMesh::set_bass_waist_width);
    ClassDB::bind_method(D_METHOD("get_bass_waist_width"), &GuitarBodyMesh::get_bass_waist_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_waist_width"), "set_bass_waist_width", "get_bass_waist_width");

    ClassDB::bind_method(D_METHOD("set_treble_chest_width", "val"), &GuitarBodyMesh::set_treble_chest_width);
    ClassDB::bind_method(D_METHOD("get_treble_chest_width"), &GuitarBodyMesh::get_treble_chest_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_chest_width"), "set_treble_chest_width", "get_treble_chest_width");

    ClassDB::bind_method(D_METHOD("set_bass_chest_width", "val"), &GuitarBodyMesh::set_bass_chest_width);
    ClassDB::bind_method(D_METHOD("get_bass_chest_width"), &GuitarBodyMesh::get_bass_chest_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_chest_width"), "set_bass_chest_width", "get_bass_chest_width");

    ClassDB::bind_method(D_METHOD("set_treble_shoulder_width", "val"), &GuitarBodyMesh::set_treble_shoulder_width);
    ClassDB::bind_method(D_METHOD("get_treble_shoulder_width"), &GuitarBodyMesh::get_treble_shoulder_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_shoulder_width"), "set_treble_shoulder_width", "get_treble_shoulder_width");

    ClassDB::bind_method(D_METHOD("set_bass_shoulder_width", "val"), &GuitarBodyMesh::set_bass_shoulder_width);
    ClassDB::bind_method(D_METHOD("get_bass_shoulder_width"), &GuitarBodyMesh::get_bass_shoulder_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_shoulder_width"), "set_bass_shoulder_width", "get_bass_shoulder_width");

    ClassDB::bind_method(D_METHOD("set_treble_horn_length", "val"), &GuitarBodyMesh::set_treble_horn_length);
    ClassDB::bind_method(D_METHOD("get_treble_horn_length"), &GuitarBodyMesh::get_treble_horn_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_horn_length"), "set_treble_horn_length", "get_treble_horn_length");

    ClassDB::bind_method(D_METHOD("set_bass_horn_length", "val"), &GuitarBodyMesh::set_bass_horn_length);
    ClassDB::bind_method(D_METHOD("get_bass_horn_length"), &GuitarBodyMesh::get_bass_horn_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_horn_length"), "set_bass_horn_length", "get_bass_horn_length");

    ClassDB::bind_method(D_METHOD("set_treble_horn_roundness", "val"), &GuitarBodyMesh::set_treble_horn_roundness);
    ClassDB::bind_method(D_METHOD("get_treble_horn_roundness"), &GuitarBodyMesh::get_treble_horn_roundness);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "treble_horn_roundness"), "set_treble_horn_roundness", "get_treble_horn_roundness");

    ClassDB::bind_method(D_METHOD("set_bass_horn_roundness", "val"), &GuitarBodyMesh::set_bass_horn_roundness);
    ClassDB::bind_method(D_METHOD("get_bass_horn_roundness"), &GuitarBodyMesh::get_bass_horn_roundness);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bass_horn_roundness"), "set_bass_horn_roundness", "get_bass_horn_roundness");

    // Ergonomic cuts
    ClassDB::bind_method(D_METHOD("set_belly_cut_enabled", "val"), &GuitarBodyMesh::set_belly_cut_enabled);
    ClassDB::bind_method(D_METHOD("get_belly_cut_enabled"), &GuitarBodyMesh::get_belly_cut_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "belly_cut_enabled"), "set_belly_cut_enabled", "get_belly_cut_enabled");

    ClassDB::bind_method(D_METHOD("set_belly_cut_depth", "val"), &GuitarBodyMesh::set_belly_cut_depth);
    ClassDB::bind_method(D_METHOD("get_belly_cut_depth"), &GuitarBodyMesh::get_belly_cut_depth);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "belly_cut_depth"), "set_belly_cut_depth", "get_belly_cut_depth");

    ClassDB::bind_method(D_METHOD("set_belly_cut_angle", "val"), &GuitarBodyMesh::set_belly_cut_angle);
    ClassDB::bind_method(D_METHOD("get_belly_cut_angle"), &GuitarBodyMesh::get_belly_cut_angle);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "belly_cut_angle"), "set_belly_cut_angle", "get_belly_cut_angle");

    ClassDB::bind_method(D_METHOD("set_belly_cut_length", "val"), &GuitarBodyMesh::set_belly_cut_length);
    ClassDB::bind_method(D_METHOD("get_belly_cut_length"), &GuitarBodyMesh::get_belly_cut_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "belly_cut_length"), "set_belly_cut_length", "get_belly_cut_length");

    ClassDB::bind_method(D_METHOD("set_forearm_bevel_enabled", "val"), &GuitarBodyMesh::set_forearm_bevel_enabled);
    ClassDB::bind_method(D_METHOD("get_forearm_bevel_enabled"), &GuitarBodyMesh::get_forearm_bevel_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "forearm_bevel_enabled"), "set_forearm_bevel_enabled", "get_forearm_bevel_enabled");

    ClassDB::bind_method(D_METHOD("set_forearm_bevel_depth", "val"), &GuitarBodyMesh::set_forearm_bevel_depth);
    ClassDB::bind_method(D_METHOD("get_forearm_bevel_depth"), &GuitarBodyMesh::get_forearm_bevel_depth);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "forearm_bevel_depth"), "set_forearm_bevel_depth", "get_forearm_bevel_depth");

    ClassDB::bind_method(D_METHOD("set_forearm_bevel_angle", "val"), &GuitarBodyMesh::set_forearm_bevel_angle);
    ClassDB::bind_method(D_METHOD("get_forearm_bevel_angle"), &GuitarBodyMesh::get_forearm_bevel_angle);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "forearm_bevel_angle"), "set_forearm_bevel_angle", "get_forearm_bevel_angle");

    ClassDB::bind_method(D_METHOD("set_forearm_bevel_length", "val"), &GuitarBodyMesh::set_forearm_bevel_length);
    ClassDB::bind_method(D_METHOD("get_forearm_bevel_length"), &GuitarBodyMesh::get_forearm_bevel_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "forearm_bevel_length"), "set_forearm_bevel_length", "get_forearm_bevel_length");

    ClassDB::bind_method(D_METHOD("set_neck_pocket_enabled", "val"), &GuitarBodyMesh::set_neck_pocket_enabled);
    ClassDB::bind_method(D_METHOD("get_neck_pocket_enabled"), &GuitarBodyMesh::get_neck_pocket_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "neck_pocket_enabled"), "set_neck_pocket_enabled", "get_neck_pocket_enabled");

    ClassDB::bind_method(D_METHOD("set_neck_pocket_width", "val"), &GuitarBodyMesh::set_neck_pocket_width);
    ClassDB::bind_method(D_METHOD("get_neck_pocket_width"), &GuitarBodyMesh::get_neck_pocket_width);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "neck_pocket_width"), "set_neck_pocket_width", "get_neck_pocket_width");

    ClassDB::bind_method(D_METHOD("set_neck_pocket_length", "val"), &GuitarBodyMesh::set_neck_pocket_length);
    ClassDB::bind_method(D_METHOD("get_neck_pocket_length"), &GuitarBodyMesh::get_neck_pocket_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "neck_pocket_length"), "set_neck_pocket_length", "get_neck_pocket_length");

    ClassDB::bind_method(D_METHOD("set_neck_pocket_depth", "val"), &GuitarBodyMesh::set_neck_pocket_depth);
    ClassDB::bind_method(D_METHOD("get_neck_pocket_depth"), &GuitarBodyMesh::get_neck_pocket_depth);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "neck_pocket_depth"), "set_neck_pocket_depth", "get_neck_pocket_depth");

    // Pickups
    ClassDB::bind_method(D_METHOD("set_pickup_config", "val"), &GuitarBodyMesh::set_pickup_config);
    ClassDB::bind_method(D_METHOD("get_pickup_config"), &GuitarBodyMesh::get_pickup_config);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "pickup_config"), "set_pickup_config", "get_pickup_config");

    ClassDB::bind_method(D_METHOD("set_bridge_pickup_y", "val"), &GuitarBodyMesh::set_bridge_pickup_y);
    ClassDB::bind_method(D_METHOD("get_bridge_pickup_y"), &GuitarBodyMesh::get_bridge_pickup_y);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bridge_pickup_y"), "set_bridge_pickup_y", "get_bridge_pickup_y");

    ClassDB::bind_method(D_METHOD("set_middle_pickup_y", "val"), &GuitarBodyMesh::set_middle_pickup_y);
    ClassDB::bind_method(D_METHOD("get_middle_pickup_y"), &GuitarBodyMesh::get_middle_pickup_y);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "middle_pickup_y"), "set_middle_pickup_y", "get_middle_pickup_y");

    ClassDB::bind_method(D_METHOD("set_neck_pickup_y", "val"), &GuitarBodyMesh::set_neck_pickup_y);
    ClassDB::bind_method(D_METHOD("get_neck_pickup_y"), &GuitarBodyMesh::get_neck_pickup_y);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "neck_pickup_y"), "set_neck_pickup_y", "get_neck_pickup_y");

    ClassDB::bind_method(D_METHOD("set_bridge_pickup_slant", "val"), &GuitarBodyMesh::set_bridge_pickup_slant);
    ClassDB::bind_method(D_METHOD("get_bridge_pickup_slant"), &GuitarBodyMesh::get_bridge_pickup_slant);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bridge_pickup_slant"), "set_bridge_pickup_slant", "get_bridge_pickup_slant");

    ClassDB::bind_method(D_METHOD("set_pickup_clearance", "val"), &GuitarBodyMesh::set_pickup_clearance);
    ClassDB::bind_method(D_METHOD("get_pickup_clearance"), &GuitarBodyMesh::get_pickup_clearance);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "pickup_clearance"), "set_pickup_clearance", "get_pickup_clearance");

    ClassDB::bind_method(D_METHOD("set_pickup_depth", "val"), &GuitarBodyMesh::set_pickup_depth);
    ClassDB::bind_method(D_METHOD("get_pickup_depth"), &GuitarBodyMesh::get_pickup_depth);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "pickup_depth"), "set_pickup_depth", "get_pickup_depth");

    // Bridge
    ClassDB::bind_method(D_METHOD("set_bridge_enabled", "val"), &GuitarBodyMesh::set_bridge_enabled);
    ClassDB::bind_method(D_METHOD("get_bridge_enabled"), &GuitarBodyMesh::get_bridge_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "bridge_enabled"), "set_bridge_enabled", "get_bridge_enabled");

    ClassDB::bind_method(D_METHOD("set_bridge_type", "val"), &GuitarBodyMesh::set_bridge_type);
    ClassDB::bind_method(D_METHOD("get_bridge_type"), &GuitarBodyMesh::get_bridge_type);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "bridge_type"), "set_bridge_type", "get_bridge_type");

    ClassDB::bind_method(D_METHOD("set_bridge_y", "val"), &GuitarBodyMesh::set_bridge_y);
    ClassDB::bind_method(D_METHOD("get_bridge_y"), &GuitarBodyMesh::get_bridge_y);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "bridge_y"), "set_bridge_y", "get_bridge_y");

    // Control Cavity & Wiring
    ClassDB::bind_method(D_METHOD("set_control_cavity_enabled", "val"), &GuitarBodyMesh::set_control_cavity_enabled);
    ClassDB::bind_method(D_METHOD("get_control_cavity_enabled"), &GuitarBodyMesh::get_control_cavity_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "control_cavity_enabled"), "set_control_cavity_enabled", "get_control_cavity_enabled");

    ClassDB::bind_method(D_METHOD("set_control_cavity_rear", "val"), &GuitarBodyMesh::set_control_cavity_rear);
    ClassDB::bind_method(D_METHOD("get_control_cavity_rear"), &GuitarBodyMesh::get_control_cavity_rear);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "control_cavity_rear"), "set_control_cavity_rear", "get_control_cavity_rear");

    ClassDB::bind_method(D_METHOD("set_control_cavity_depth", "val"), &GuitarBodyMesh::set_control_cavity_depth);
    ClassDB::bind_method(D_METHOD("get_control_cavity_depth"), &GuitarBodyMesh::get_control_cavity_depth);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "control_cavity_depth"), "set_control_cavity_depth", "get_control_cavity_depth");

    ClassDB::bind_method(D_METHOD("set_wiring_tunnels_enabled", "val"), &GuitarBodyMesh::set_wiring_tunnels_enabled);
    ClassDB::bind_method(D_METHOD("get_wiring_tunnels_enabled"), &GuitarBodyMesh::get_wiring_tunnels_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "wiring_tunnels_enabled"), "set_wiring_tunnels_enabled", "get_wiring_tunnels_enabled");

    ClassDB::bind_method(D_METHOD("rebuild_mesh"), &GuitarBodyMesh::rebuild_mesh);
}

void GuitarBodyMesh::_ready() {
    rebuild_mesh();
}

void GuitarBodyMesh::set_hip_width(double p_val) {
    if (hip_width != p_val) {
        hip_width = p_val;
        treble_hip_width = p_val * 0.5;
        bass_hip_width = p_val * 0.5;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_waist_width(double p_val) {
    if (waist_width != p_val) {
        waist_width = p_val;
        treble_waist_width = p_val * 0.5;
        bass_waist_width = p_val * 0.5;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_chest_width(double p_val) {
    if (chest_width != p_val) {
        chest_width = p_val;
        treble_chest_width = p_val * 0.5;
        bass_chest_width = p_val * 0.5;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_shoulder_width(double p_val) {
    if (shoulder_width != p_val) {
        shoulder_width = p_val;
        treble_shoulder_width = p_val * 0.5;
        bass_shoulder_width = p_val * 0.5;
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

void GuitarBodyMesh::set_treble_hip_width(double p_val) {
    if (treble_hip_width != p_val) {
        treble_hip_width = p_val;
        hip_width = treble_hip_width + bass_hip_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_hip_width(double p_val) {
    if (bass_hip_width != p_val) {
        bass_hip_width = p_val;
        hip_width = treble_hip_width + bass_hip_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_treble_waist_width(double p_val) {
    if (treble_waist_width != p_val) {
        treble_waist_width = p_val;
        waist_width = treble_waist_width + bass_waist_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_waist_width(double p_val) {
    if (bass_waist_width != p_val) {
        bass_waist_width = p_val;
        waist_width = treble_waist_width + bass_waist_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_treble_chest_width(double p_val) {
    if (treble_chest_width != p_val) {
        treble_chest_width = p_val;
        chest_width = treble_chest_width + bass_chest_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_chest_width(double p_val) {
    if (bass_chest_width != p_val) {
        bass_chest_width = p_val;
        chest_width = treble_chest_width + bass_chest_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_treble_shoulder_width(double p_val) {
    if (treble_shoulder_width != p_val) {
        treble_shoulder_width = p_val;
        shoulder_width = treble_shoulder_width + bass_shoulder_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_shoulder_width(double p_val) {
    if (bass_shoulder_width != p_val) {
        bass_shoulder_width = p_val;
        shoulder_width = treble_shoulder_width + bass_shoulder_width;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_treble_horn_length(double p_val) {
    if (treble_horn_length != p_val) {
        treble_horn_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_horn_length(double p_val) {
    if (bass_horn_length != p_val) {
        bass_horn_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_horn_reach(double p_val) {
    if (horn_reach != p_val) {
        horn_reach = p_val;
        treble_horn_length = p_val;
        bass_horn_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_horn_roundness(double p_val) {
    if (horn_roundness != p_val) {
        horn_roundness = p_val;
        treble_horn_roundness = p_val;
        bass_horn_roundness = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_treble_horn_roundness(double p_val) {
    if (treble_horn_roundness != p_val) {
        treble_horn_roundness = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bass_horn_roundness(double p_val) {
    if (bass_horn_roundness != p_val) {
        bass_horn_roundness = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_belly_cut_enabled(bool p_val) {
    if (belly_cut_enabled != p_val) {
        belly_cut_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_belly_cut_depth(double p_val) {
    if (belly_cut_depth != p_val) {
        belly_cut_depth = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_belly_cut_angle(double p_val) {
    if (belly_cut_angle != p_val) {
        belly_cut_angle = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_belly_cut_length(double p_val) {
    if (belly_cut_length != p_val) {
        belly_cut_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_forearm_bevel_enabled(bool p_val) {
    if (forearm_bevel_enabled != p_val) {
        forearm_bevel_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_forearm_bevel_depth(double p_val) {
    if (forearm_bevel_depth != p_val) {
        forearm_bevel_depth = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_forearm_bevel_angle(double p_val) {
    if (forearm_bevel_angle != p_val) {
        forearm_bevel_angle = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_forearm_bevel_length(double p_val) {
    if (forearm_bevel_length != p_val) {
        forearm_bevel_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pocket_enabled(bool p_val) {
    if (neck_pocket_enabled != p_val) {
        neck_pocket_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pocket_width(double p_val) {
    if (neck_pocket_width != p_val) {
        neck_pocket_width = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pocket_length(double p_val) {
    if (neck_pocket_length != p_val) {
        neck_pocket_length = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pocket_depth(double p_val) {
    if (neck_pocket_depth != p_val) {
        neck_pocket_depth = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_pickup_config(int p_val) {
    if (pickup_config != p_val) {
        pickup_config = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bridge_pickup_y(double p_val) {
    if (bridge_pickup_y != p_val) {
        bridge_pickup_y = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_middle_pickup_y(double p_val) {
    if (middle_pickup_y != p_val) {
        middle_pickup_y = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_neck_pickup_y(double p_val) {
    if (neck_pickup_y != p_val) {
        neck_pickup_y = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bridge_pickup_slant(double p_val) {
    if (bridge_pickup_slant != p_val) {
        bridge_pickup_slant = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_pickup_clearance(double p_val) {
    if (pickup_clearance != p_val) {
        pickup_clearance = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_pickup_depth(double p_val) {
    if (pickup_depth != p_val) {
        pickup_depth = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bridge_enabled(bool p_val) {
    if (bridge_enabled != p_val) {
        bridge_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bridge_type(int p_val) {
    if (bridge_type != p_val) {
        bridge_type = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_bridge_y(double p_val) {
    if (bridge_y != p_val) {
        bridge_y = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_control_cavity_enabled(bool p_val) {
    if (control_cavity_enabled != p_val) {
        control_cavity_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_control_cavity_rear(bool p_val) {
    if (control_cavity_rear != p_val) {
        control_cavity_rear = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_control_cavity_depth(double p_val) {
    if (control_cavity_depth != p_val) {
        control_cavity_depth = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_wiring_tunnels_enabled(bool p_val) {
    if (wiring_tunnels_enabled != p_val) {
        wiring_tunnels_enabled = p_val;
        rebuild_mesh();
    }
}

// Centripetal Catmull-Rom spline (alpha = 0.5): guarantees no cusps, loops, or overshoot
static inline double get_cr_t(double t, double alpha, const manifold::vec2& p0, const manifold::vec2& p1) {
    double d = std::hypot(p1.x - p0.x, p1.y - p0.y);
    return t + std::pow(std::max(1e-4, d), alpha);
}

static manifold::vec2 catmull_rom(
    const manifold::vec2& p0,
    const manifold::vec2& p1,
    const manifold::vec2& p2,
    const manifold::vec2& p3,
    double t
) {
    const double alpha = 0.5; // Centripetal
    double t0 = 0.0;
    double t1 = get_cr_t(t0, alpha, p0, p1);
    double t2 = get_cr_t(t1, alpha, p1, p2);
    double t3 = get_cr_t(t2, alpha, p2, p3);

    double u = t1 + t * (t2 - t1);

    manifold::vec2 a1 = {
        ((t1 - u) * p0.x + (u - t0) * p1.x) / (t1 - t0),
        ((t1 - u) * p0.y + (u - t0) * p1.y) / (t1 - t0)
    };
    manifold::vec2 a2 = {
        ((t2 - u) * p1.x + (u - t1) * p2.x) / (t2 - t1),
        ((t2 - u) * p1.y + (u - t1) * p2.y) / (t2 - t1)
    };
    manifold::vec2 a3 = {
        ((t3 - u) * p2.x + (u - t2) * p3.x) / (t3 - t2),
        ((t3 - u) * p2.y + (u - t2) * p3.y) / (t3 - t2)
    };

    manifold::vec2 b1 = {
        ((t2 - u) * a1.x + (u - t0) * a2.x) / (t2 - t0),
        ((t2 - u) * a1.y + (u - t0) * a2.y) / (t2 - t0)
    };
    manifold::vec2 b2 = {
        ((t3 - u) * a2.x + (u - t1) * a3.x) / (t3 - t1),
        ((t3 - u) * a2.y + (u - t1) * a3.y) / (t3 - t1)
    };

    return manifold::vec2{
        ((t2 - u) * b1.x + (u - t1) * b2.x) / (t2 - t1),
        ((t2 - u) * b1.y + (u - t1) * b2.y) / (t2 - t1)
    };
}

void GuitarBodyMesh::rebuild_mesh() {
    using namespace manifold;

    double L = body_length; // standard reference 446.0 mm
    double scale_y = L / 446.0;

    double t_hip = treble_hip_width;
    double t_waist = treble_waist_width;
    double t_chest = treble_chest_width;
    double t_shoulder = treble_shoulder_width;
    double t_horn_len = treble_horn_length;
    double t_rnd = treble_horn_roundness;

    double b_hip = bass_hip_width;
    double b_waist = bass_waist_width;
    double b_chest = bass_chest_width;
    double b_shoulder = bass_shoulder_width;
    double b_horn_len = bass_horn_length;
    double b_rnd = bass_horn_roundness;

    if (symmetric_mode) {
        t_hip = hip_width * 0.5;
        t_waist = waist_width * 0.5;
        t_chest = chest_width * 0.5;
        t_shoulder = shoulder_width * 0.5;
        t_horn_len = horn_reach;
        t_rnd = horn_roundness;

        b_hip = t_hip;
        b_waist = t_waist;
        b_chest = t_chest;
        b_shoulder = t_shoulder;
        b_horn_len = horn_reach;
        b_rnd = horn_roundness;
    }

    const double r_hip = 159.0;
    const double r_waist = 115.6;
    const double r_chest = 137.5;

    // Treble Horn Waypoints calculation (proportional reach and roundness)
    double t_w = t_shoulder / 125.0;
    double t_tip_x = 124.06 * t_w;
    double t_h = std::max(10.0, t_horn_len - 366.6);
    double t_h_ref = 446.35 - 366.6; // 79.75 mm ref reach
    double t_h_ratio = t_h / t_h_ref;
    double t_rnd_c = std::clamp(t_rnd, 0.4, 2.5);
    double t_tip_y = (366.6 + t_h) * scale_y;
    double tip_drop = 22.0 * t_h_ratio * (0.65 + 0.35 * t_rnd_c);

    double p10_x = t_tip_x + (136.31 - 124.06) * t_w * t_rnd_c;
    double p10_y = std::max(364.0 * scale_y, t_tip_y - tip_drop * scale_y);

    double p11_x = t_tip_x;
    double p11_y = t_tip_y;

    double p12_x = t_tip_x + (105.72 - 124.06) * t_w * t_rnd_c;
    double p12_y = p10_y;

    double p13_x = t_tip_x + (91.72 - 124.06) * t_w * (0.35 + 0.65 * t_rnd_c);
    double p13_y = std::max(367.0 * scale_y, (366.6 + 0.27 * t_h) * scale_y);

    // Authentic double-cutaway Stratocaster contour waypoints
    // Right side (+X, Treble side): starts from bottom tail (0,0) and sweeps CCW to the neck pocket center (0, 399.7)
    std::vector<vec2> right_keys = {
        vec2{   0.00,                                 0.00 },                // 0: Tail bottom center
        vec2{  27.23 * (t_hip / r_hip),               1.69 * scale_y },      // 1: Tail bottom curve
        vec2{  66.95 * (t_hip / r_hip),               8.80 * scale_y },      // 2: Lower bout entry
        vec2{ 111.58 * (t_hip / r_hip),              30.43 * scale_y },      // 3: Lower bout sweep
        vec2{ 145.13 * (t_hip / r_hip),              72.89 * scale_y },      // 4: Lower bout curve
        vec2{ t_hip,                                143.95 * scale_y },      // 5: Hip apex (widest lower bout ~318.6mm)
        vec2{ 146.33 * (t_hip / r_hip),             207.40 * scale_y },      // 6: Lower bout to waist transition
        vec2{ t_waist,                              256.50 * scale_y },      // 7: Waist minimum (~238mm)
        vec2{ 122.20 * (t_waist / r_waist),         309.62 * scale_y },      // 8: Waist to chest rise
        vec2{ t_chest,                              362.05 * scale_y },      // 9: Chest / Upper bout apex
        vec2{ p10_x,                                p10_y },                 // 10: Horn outer rise
        vec2{ p11_x,                                p11_y },                 // 11: Horn tip apex
        vec2{ p12_x,                                p12_y },                 // 12: Horn inner slope
        vec2{ p13_x,                                p13_y },                 // 13: Horn inner flank
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
        // Independent asymmetric Bass side (-X)
        double b_w = b_shoulder / 125.0;
        double b_tip_x = -124.06 * b_w;
        double b_h = std::max(10.0, b_horn_len - 376.0);
        double b_h_ref = 458.0 - 376.0; // 82.0 mm ref reach
        double b_h_ratio = b_h / b_h_ref;
        double b_rnd_c = std::clamp(b_rnd, 0.4, 2.5);
        double b_tip_y = (376.0 + b_h) * scale_y;
        double b_tip_drop = 22.0 * b_h_ratio * (0.65 + 0.35 * b_rnd_c);

        double bp_slope_x = b_tip_x + (-95.0 - (-124.06)) * b_w * (0.4 + 0.6 * b_rnd_c);
        double bp_slope_y = std::max(380.0 * scale_y, (376.0 + 0.51 * b_h) * scale_y);

        double bp_in_x = b_tip_x + (-108.0 - (-124.06)) * b_w * b_rnd_c;
        double bp_in_y = std::max(380.0 * scale_y, b_tip_y - b_tip_drop * scale_y);

        double bp_tip_x = b_tip_x;
        double bp_tip_y = b_tip_y;

        double bp_out_x = b_tip_x + (-136.31 - (-124.06)) * b_w * b_rnd_c;
        double bp_out_y = bp_in_y;

        left_keys = {
            vec2{  -14.00,                               399.69 * scale_y },
            vec2{  -28.25,                               399.69 * scale_y },
            vec2{  -32.00,                               388.00 * scale_y },
            vec2{  -40.00,                               378.00 * scale_y },
            vec2{  -56.00,                               376.00 * scale_y },
            vec2{  -78.00 * (b_shoulder / 125.0),        388.00 * scale_y },
            vec2{ bp_slope_x,                            bp_slope_y },
            vec2{ bp_in_x,                               bp_in_y },
            vec2{ bp_tip_x,                              bp_tip_y }, // Bass horn apex
            vec2{ bp_out_x,                              bp_out_y },
            vec2{ -b_chest,                              362.05 * scale_y },
            vec2{ -122.20 * (b_waist / r_waist),         309.62 * scale_y },
            vec2{ -b_waist,                              256.50 * scale_y },
            vec2{ -146.33 * (b_hip / r_hip),             207.40 * scale_y },
            vec2{ -b_hip,                                143.95 * scale_y },
            vec2{ -145.13 * (b_hip / r_hip),              72.89 * scale_y },
            vec2{ -111.58 * (b_hip / r_hip),              30.43 * scale_y },
            vec2{  -66.95 * (b_hip / r_hip),               8.80 * scale_y },
            vec2{  -27.23 * (b_hip / r_hip),               1.69 * scale_y }
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

    Manifold body;
    double r = std::min(edge_radius, body_thickness * 0.45);

    if (r <= 0.1) {
        // Flat sharp extrusion if edge_radius is effectively zero
        body = Manifold::Extrude(cs.ToPolygons(), body_thickness);
    } else {
        // Multi-ring 3D roundover fillet mesh
        size_t M = contour.size();

        // 1. Compute 2D outward unit normals for each contour vertex
        std::vector<vec2> normals(M);
        for (size_t i = 0; i < M; ++i) {
            vec2 prev_p = contour[(i + M - 1) % M];
            vec2 next_p = contour[(i + 1) % M];
            double dx = next_p.x - prev_p.x;
            double dy = next_p.y - prev_p.y;
            double len = std::hypot(dx, dy);
            if (len > 1e-9) {
                normals[i] = vec2{ dy / len, -dx / len }; // CCW outward normal
            } else {
                normals[i] = vec2{ 0.0, 1.0 };
            }
        }

        // 2. Define roundover profile rings
        // Bottom roundover: 3 steps, straight side wall: 1 step, Top roundover: 3 steps -> 8 rings total
        const int S = 3;
        const double PI_2 = 1.5707963267948966;

        struct RingDef {
            double z;
            double inset;
        };
        std::vector<RingDef> ring_defs;

        // Bottom roundover rings (from z = 0, inset = r up to z = r, inset = 0)
        for (int s = 0; s <= S; ++s) {
            double alpha = (double)s / (double)S * PI_2;
            double z = r * (1.0 - std::cos(alpha));
            double inset = r * (1.0 - std::sin(alpha));
            ring_defs.push_back({ z, inset });
        }

        // Top edge of straight side wall (z = body_thickness - r, inset = 0)
        ring_defs.push_back({ body_thickness - r, 0.0 });

        // Top roundover rings (from z = body_thickness - r, inset = 0 up to z = body_thickness, inset = r)
        for (int s = 1; s <= S; ++s) {
            double beta = (double)s / (double)S * PI_2;
            double z = (body_thickness - r) + r * std::sin(beta);
            double inset = r * (1.0 - std::cos(beta));
            ring_defs.push_back({ z, inset });
        }

        size_t num_rings = ring_defs.size();

        // 3. Generate vertices for all rings
        MeshGL mgl;
        mgl.numProp = 3;
        mgl.vertProperties.reserve(num_rings * M * 3);

        for (size_t ring = 0; ring < num_rings; ++ring) {
            double z = ring_defs[ring].z;
            double inset = ring_defs[ring].inset;
            for (size_t i = 0; i < M; ++i) {
                double vx = contour[i].x - normals[i].x * inset;
                double vy = contour[i].y - normals[i].y * inset;
                mgl.vertProperties.push_back((float)vx);
                mgl.vertProperties.push_back((float)vy);
                mgl.vertProperties.push_back((float)z);
            }
        }

        // 4. Generate side wall and fillet triangles connecting adjacent rings
        for (size_t ring = 0; ring < num_rings - 1; ++ring) {
            for (size_t i = 0; i < M; ++i) {
                size_t i_next = (i + 1) % M;
                uint32_t a = (uint32_t)(ring * M + i);
                uint32_t b = (uint32_t)(ring * M + i_next);
                uint32_t c = (uint32_t)((ring + 1) * M + i_next);
                uint32_t d = (uint32_t)((ring + 1) * M + i);

                // CCW triangles viewed from outside:
                mgl.triVerts.push_back(a);
                mgl.triVerts.push_back(b);
                mgl.triVerts.push_back(c);

                mgl.triVerts.push_back(a);
                mgl.triVerts.push_back(c);
                mgl.triVerts.push_back(d);
            }
        }

        // 5. Triangulate top and bottom caps using Manifold's Triangulate
        std::vector<ivec3> cap_tris = Triangulate(cs.ToPolygons());

        // Bottom cap (z = 0, ring 0): normal points down (-Z), so reverse winding
        for (const ivec3& t : cap_tris) {
            mgl.triVerts.push_back((uint32_t)t[0]);
            mgl.triVerts.push_back((uint32_t)t[2]);
            mgl.triVerts.push_back((uint32_t)t[1]);
        }

        // Top cap (z = body_thickness, last ring): normal points up (+Z), CCW
        uint32_t top_base = (uint32_t)((num_rings - 1) * M);
        for (const ivec3& t : cap_tris) {
            mgl.triVerts.push_back(top_base + (uint32_t)t[0]);
            mgl.triVerts.push_back(top_base + (uint32_t)t[1]);
            mgl.triVerts.push_back(top_base + (uint32_t)t[2]);
        }

        body = Manifold(mgl);
    }

    // Ergonomic Cut 1: Belly Cut (Tummy contour on rear waist Z=0, bass side only)
    if (belly_cut_enabled) {
        size_t v_before = body.NumVert();
        double cut_len = belly_cut_length * scale_y;
        Manifold belly_cutter = Manifold::Cube(vec3{ 350.0, cut_len, 120.0 }, false)
            .Translate(vec3{ -350.0, -cut_len * 0.5, -120.0 })
            .Rotate(0.0, belly_cut_angle, -35.0)
            .Translate(vec3{ -20.0, 290.0 * scale_y, 0.0 });
        body = body - belly_cutter;
    }

    // Ergonomic Cut 2: Forearm Bevel (Front lower bout, Z near body_thickness, treble side only)
    if (forearm_bevel_enabled) {
        size_t v_before = body.NumVert();
        double cut_len = forearm_bevel_length * scale_y;
        Manifold forearm_cutter = Manifold::Cube(vec3{ 350.0, cut_len, 120.0 }, false)
            .Translate(vec3{ 0.0, -cut_len * 0.5, 0.0 })
            .Rotate(0.0, forearm_bevel_angle, -25.0)
            .Translate(vec3{ 55.0, 150.0 * scale_y, body_thickness });
        body = body - forearm_cutter;
    }

    // Standard Luthier Neck Pocket Mortise
    if (neck_pocket_enabled) {
        double pocket_w = neck_pocket_width;
        double pocket_len = neck_pocket_length;
        double pocket_depth = neck_pocket_depth;
        double pocket_top_y = 399.69 * scale_y;

        Manifold neck_pocket = Manifold::Cube(vec3{ pocket_w, pocket_len + 15.0, pocket_depth + 4.0 }, false)
            .Translate(vec3{ -pocket_w * 0.5, pocket_top_y - pocket_len, body_thickness - pocket_depth });
        body = body - neck_pocket;
    }

    // Procedural Pickup Cavity Generator
    if (pickup_config > 0) {
        auto make_pickup_cavity = [](bool is_hb, double clr, double depth) -> Manifold {
            double w = (is_hb ? 70.0 : 70.0) + 2.0 * clr;
            double l = (is_hb ? 38.0 : 18.0) + 2.0 * clr;
            double w_ears = 84.0 + 2.0 * clr;
            double l_ears = 16.0 + 2.0 * clr;
            double ear_depth = depth + 4.0;

            CrossSection cs_main = CrossSection::Square(vec2{ w, l }, true);
            CrossSection cs_ears = CrossSection::Square(vec2{ w_ears, l_ears }, true);

            Manifold m_main = Manifold::Extrude(cs_main.ToPolygons(), depth)
                .Translate(vec3{ 0.0, 0.0, ear_depth - depth });
            Manifold m_ears = Manifold::Extrude(cs_ears.ToPolygons(), ear_depth);

            return (m_main + m_ears).Translate(vec3{ 0.0, 0.0, -ear_depth });
        };

        if (pickup_config == 1) { // SSS
            // Bridge (single coil with optional slant)
            Manifold bridge_cav = make_pickup_cavity(false, pickup_clearance, pickup_depth)
                .Rotate(0.0, 0.0, bridge_pickup_slant)
                .Translate(vec3{ 0.0, bridge_pickup_y * scale_y, body_thickness });
            // Middle
            Manifold mid_cav = make_pickup_cavity(false, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, middle_pickup_y * scale_y, body_thickness });
            // Neck
            Manifold neck_cav = make_pickup_cavity(false, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, neck_pickup_y * scale_y, body_thickness });
            body = body - bridge_cav - mid_cav - neck_cav;
        } else if (pickup_config == 2) { // HSS
            // Bridge (Humbucker)
            Manifold bridge_cav = make_pickup_cavity(true, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, bridge_pickup_y * scale_y, body_thickness });
            // Middle (Single Coil)
            Manifold mid_cav = make_pickup_cavity(false, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, middle_pickup_y * scale_y, body_thickness });
            // Neck (Single Coil)
            Manifold neck_cav = make_pickup_cavity(false, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, neck_pickup_y * scale_y, body_thickness });
            body = body - bridge_cav - mid_cav - neck_cav;
        } else if (pickup_config == 3) { // HH
            // Bridge (Humbucker)
            Manifold bridge_cav = make_pickup_cavity(true, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, bridge_pickup_y * scale_y, body_thickness });
            // Neck (Humbucker)
            Manifold neck_cav = make_pickup_cavity(true, pickup_clearance, pickup_depth)
                .Translate(vec3{ 0.0, neck_pickup_y * scale_y, body_thickness });
            body = body - bridge_cav - neck_cav;
        }
    }

    // Bridge Routing & String Holes
    if (bridge_enabled) {
        double b_y = bridge_y * scale_y;
        if (bridge_type == 0) { // Hardtail: 6 string-through ferrule holes
            double spacing = 10.5; // 52.5mm standard E-to-E string spread
            for (int i = 0; i < 6; ++i) {
                double sx = -26.25 + i * spacing;
                // String-through drill hole (3.5mm diameter)
                Manifold string_hole = Manifold::Cylinder(body_thickness + 4.0, 1.75, 1.75, 16)
                    .Translate(vec3{ sx, b_y, -2.0 });
                // Rear ferrule counterbore (8.0mm diameter, 9mm depth from rear Z=0)
                Manifold ferrule = Manifold::Cylinder(9.0, 4.0, 4.0, 20)
                    .Translate(vec3{ sx, b_y, -1.0 });
                body = body - string_hole - ferrule;
            }
        } else { // Tremolo: Through-body block slot + rear spring cavity
            Manifold block_slot = Manifold::Cube(vec3{ 76.0, 20.0, body_thickness + 4.0 }, true)
                .Translate(vec3{ 0.0, b_y, body_thickness * 0.5 });
            Manifold spring_cavity = Manifold::Cube(vec3{ 54.0, 105.0, 19.0 }, true)
                .Translate(vec3{ 0.0, b_y + 40.0 * scale_y, 8.5 });
            body = body - block_slot - spring_cavity;
        }
    }

    // Control Cavity & Potentiometer Shaft Holes
    // Placed at cc_x = 68.0, cc_y = 138.0 to guarantee ample clearance (> 15mm)
    // from the high-E string-through hole (sx = +26.25, by = 145.0) and ferrule counterbore.
    double cc_x = 68.0;
    double cc_y = 138.0 * scale_y;

    if (control_cavity_enabled) {
        double pocket_depth = std::min(control_cavity_depth, body_thickness - 6.0);

        // Organic control cavity polygon extended downward into the lower bout
        // to provide generous internal space (> 28mm clearance) for the bottom CTS pot,
        // tone capacitors, and wiring.
        SimplePolygon cc_pts = {
            vec2{ -14.0, -70.0 }, // Extended tail end
            vec2{  14.0, -68.0 }, // Extended tail end right
            vec2{  20.0, -35.0 }, // Lower-right flank
            vec2{  24.0,  10.0 }, // Mid-right flank
            vec2{  14.0,  52.0 }, // Top-right flank
            vec2{ -14.0,  50.0 }, // Top-left
            vec2{ -14.0,   5.0 }  // Mid-left (facing bridge ferrules with >17mm wall)
        };
        CrossSection cs_cc(cc_pts, CrossSection::FillRule::Positive);
        cs_cc = cs_cc.Offset(8.0, CrossSection::JoinType::Round).Offset(-2.0, CrossSection::JoinType::Round);

        if (control_cavity_rear) {
            Manifold main_pocket = Manifold::Extrude(cs_cc.ToPolygons(), pocket_depth + 2.0)
                .Translate(vec3{ cc_x, cc_y, -1.0 });
            CrossSection cs_lip = cs_cc.Offset(4.0, CrossSection::JoinType::Round);
            Manifold lip_recess = Manifold::Extrude(cs_lip.ToPolygons(), 2.4)
                .Translate(vec3{ cc_x, cc_y, -0.2 });
            body = body - main_pocket - lip_recess;
        } else {
            Manifold front_pocket = Manifold::Extrude(cs_cc.ToPolygons(), pocket_depth + 2.0)
                .Translate(vec3{ cc_x, cc_y, body_thickness - pocket_depth });
            body = body - front_pocket;
        }

        // Potentiometer shaft holes (3 CTS 9.5mm holes for Vol, Tone1, Tone2)
        std::vector<vec2> pot_positions = {
            vec2{ cc_x + 2.0, cc_y + 36.0 },
            vec2{ cc_x + 6.0, cc_y - 4.0 },
            vec2{ cc_x - 2.0, cc_y - 42.0 }
        };
        for (const auto& pos : pot_positions) {
            Manifold pot_hole = Manifold::Cylinder(body_thickness + 4.0, 4.8, 4.8, 20)
                .Translate(vec3{ pos.x, pos.y, -2.0 });
            body = body - pot_hole;
        }
    }

    // Wiring Tunnels
    if (wiring_tunnels_enabled) {
        // Tunnel drill height: breaks cleanly through the bottom of the pickup cavities into control pocket
        double drill_z = std::max(12.0, body_thickness - pickup_depth - 1.5);

        // Helper lambda for straight cylindrical tunnels between two 3D points
        auto make_tunnel = [](const vec3& start, const vec3& end, double radius) -> Manifold {
            vec3 dir{ end.x - start.x, end.y - start.y, end.z - start.z };
            double len = std::sqrt(dir.x * dir.x + dir.y * dir.y + dir.z * dir.z);
            if (len < 1e-3) return Manifold();
            double pitch_deg = -std::asin(dir.z / len) * 180.0 / 3.141592653589793;
            double yaw_deg = std::atan2(dir.y, dir.x) * 180.0 / 3.141592653589793;
            return Manifold::Cylinder(len + 4.0, radius, radius, 16)
                .Translate(vec3{ 0.0, 0.0, -2.0 })
                .Rotate(0.0, 90.0, 0.0)
                .Rotate(0.0, pitch_deg, yaw_deg)
                .Translate(start);
        };

        // 1. Pickup Inter-Pocket Tunnels (treble side channel at X = 22.0)
        double p_channel_x = 22.0;

        if (pickup_config == 1 || pickup_config == 2) { // SSS or HSS
            // Neck to Middle tunnel (8.0mm diameter)
            vec3 p_neck{ p_channel_x, neck_pickup_y * scale_y, drill_z };
            vec3 p_mid{ p_channel_x, middle_pickup_y * scale_y, drill_z };
            body = body - make_tunnel(p_neck, p_mid, 4.0);

            // Middle to Bridge tunnel (8.0mm diameter)
            vec3 p_brg{ p_channel_x, bridge_pickup_y * scale_y, drill_z };
            body = body - make_tunnel(p_mid, p_brg, 4.0);

            // Bridge to Control Cavity main harness tunnel (9.0mm diameter)
            vec3 p_cc{ cc_x - 10.0, cc_y + 25.0 * scale_y, drill_z };
            body = body - make_tunnel(p_brg, p_cc, 4.5);
        } else if (pickup_config == 3) { // HH
            // Direct Neck to Bridge tunnel (8.0mm diameter)
            vec3 p_neck{ p_channel_x, neck_pickup_y * scale_y, drill_z };
            vec3 p_brg{ p_channel_x, bridge_pickup_y * scale_y, drill_z };
            body = body - make_tunnel(p_neck, p_brg, 4.0);

            // Bridge to Control Cavity tunnel (9.0mm diameter)
            vec3 p_cc{ cc_x - 10.0, cc_y + 25.0 * scale_y, drill_z };
            body = body - make_tunnel(p_brg, p_cc, 4.5);
        }

        // 2. Bridge Ground Wire Tunnel (4.0mm diameter)
        // Drilled from bridge position into the control cavity
        vec3 gnd_start{ 14.0, bridge_y * scale_y, body_thickness - 2.0 };
        vec3 gnd_end{ cc_x - 14.0, cc_y + 5.0 * scale_y, drill_z };
        body = body - make_tunnel(gnd_start, gnd_end, 2.0);

        // 3. Output Jack Tunnel (12.0mm diameter)
        // Drilled from control cavity to the side rim at waypoint 4
        vec3 j_start{ cc_x, cc_y - 25.0 * scale_y, drill_z };
        vec3 j_end{ 145.13 * (t_hip / 159.0), 72.89 * scale_y, drill_z };
        body = body - make_tunnel(j_start, j_end, 6.0);
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

        float total_hip = (float)(t_hip + b_hip);
        float u = (px + (float)b_hip * scale_factor) / (total_hip * scale_factor);
        float v_coord = py / ((float)L * scale_factor);
        uvs[(int64_t)v] = Vector2(u, v_coord);
    }

    size_t num_indices = mesh_gl.triVerts.size();
    indices.resize((int64_t)num_indices);
    // Convert Manifold's CCW triangle winding to Godot's CW front-facing winding by swapping indices 1 and 2
    for (size_t t = 0; t < num_indices / 3; ++t) {
        indices[(int64_t)(t * 3 + 0)] = (int32_t)mesh_gl.triVerts[t * 3 + 0];
        indices[(int64_t)(t * 3 + 1)] = (int32_t)mesh_gl.triVerts[t * 3 + 2];
        indices[(int64_t)(t * 3 + 2)] = (int32_t)mesh_gl.triVerts[t * 3 + 1];
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
