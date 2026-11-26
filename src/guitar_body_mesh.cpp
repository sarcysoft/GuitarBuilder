#include "guitar_body_mesh.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/dir_access.hpp>

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
    neck_pocket_enabled = true;
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

    ClassDB::bind_method(D_METHOD("set_piezo_saddles_enabled", "val"), &GuitarBodyMesh::set_piezo_saddles_enabled);
    ClassDB::bind_method(D_METHOD("get_piezo_saddles_enabled"), &GuitarBodyMesh::get_piezo_saddles_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "piezo_saddles_enabled"), "set_piezo_saddles_enabled", "get_piezo_saddles_enabled");

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

    // Phase 5: Procedural Modifiers (Weight Relief & Acoustic Chambering)
    ClassDB::bind_method(D_METHOD("set_sphere_modifiers_enabled", "val"), &GuitarBodyMesh::set_sphere_modifiers_enabled);
    ClassDB::bind_method(D_METHOD("get_sphere_modifiers_enabled"), &GuitarBodyMesh::get_sphere_modifiers_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "sphere_modifiers_enabled"), "set_sphere_modifiers_enabled", "get_sphere_modifiers_enabled");

    ClassDB::bind_method(D_METHOD("set_sphere_count", "val"), &GuitarBodyMesh::set_sphere_count);
    ClassDB::bind_method(D_METHOD("get_sphere_count"), &GuitarBodyMesh::get_sphere_count);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "sphere_count"), "set_sphere_count", "get_sphere_count");

    ClassDB::bind_method(D_METHOD("set_sphere_radius", "val"), &GuitarBodyMesh::set_sphere_radius);
    ClassDB::bind_method(D_METHOD("get_sphere_radius"), &GuitarBodyMesh::get_sphere_radius);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "sphere_radius"), "set_sphere_radius", "get_sphere_radius");

    ClassDB::bind_method(D_METHOD("set_cylinder_modifiers_enabled", "val"), &GuitarBodyMesh::set_cylinder_modifiers_enabled);
    ClassDB::bind_method(D_METHOD("get_cylinder_modifiers_enabled"), &GuitarBodyMesh::get_cylinder_modifiers_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "cylinder_modifiers_enabled"), "set_cylinder_modifiers_enabled", "get_cylinder_modifiers_enabled");

    ClassDB::bind_method(D_METHOD("set_cylinder_count", "val"), &GuitarBodyMesh::set_cylinder_count);
    ClassDB::bind_method(D_METHOD("get_cylinder_count"), &GuitarBodyMesh::get_cylinder_count);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "cylinder_count"), "set_cylinder_count", "get_cylinder_count");

    ClassDB::bind_method(D_METHOD("set_cylinder_radius", "val"), &GuitarBodyMesh::set_cylinder_radius);
    ClassDB::bind_method(D_METHOD("get_cylinder_radius"), &GuitarBodyMesh::get_cylinder_radius);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "cylinder_radius"), "set_cylinder_radius", "get_cylinder_radius");

    ClassDB::bind_method(D_METHOD("set_cylinder_angle", "val"), &GuitarBodyMesh::set_cylinder_angle);
    ClassDB::bind_method(D_METHOD("get_cylinder_angle"), &GuitarBodyMesh::get_cylinder_angle);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "cylinder_angle"), "set_cylinder_angle", "get_cylinder_angle");

    ClassDB::bind_method(D_METHOD("set_honeycomb_modifiers_enabled", "val"), &GuitarBodyMesh::set_honeycomb_modifiers_enabled);
    ClassDB::bind_method(D_METHOD("get_honeycomb_modifiers_enabled"), &GuitarBodyMesh::get_honeycomb_modifiers_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "honeycomb_modifiers_enabled"), "set_honeycomb_modifiers_enabled", "get_honeycomb_modifiers_enabled");

    ClassDB::bind_method(D_METHOD("set_honeycomb_cell_size", "val"), &GuitarBodyMesh::set_honeycomb_cell_size);
    ClassDB::bind_method(D_METHOD("get_honeycomb_cell_size"), &GuitarBodyMesh::get_honeycomb_cell_size);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "honeycomb_cell_size"), "set_honeycomb_cell_size", "get_honeycomb_cell_size");

    ClassDB::bind_method(D_METHOD("set_modifier_seed", "val"), &GuitarBodyMesh::set_modifier_seed);
    ClassDB::bind_method(D_METHOD("get_modifier_seed"), &GuitarBodyMesh::get_modifier_seed);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "modifier_seed"), "set_modifier_seed", "get_modifier_seed");

    // Phase 3: CAM Slicing, Dowels & Production Export
    ClassDB::bind_method(D_METHOD("set_slicing_enabled", "val"), &GuitarBodyMesh::set_slicing_enabled);
    ClassDB::bind_method(D_METHOD("get_slicing_enabled"), &GuitarBodyMesh::get_slicing_enabled);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "slicing_enabled"), "set_slicing_enabled", "get_slicing_enabled");

    ClassDB::bind_method(D_METHOD("set_slice_grid_type", "val"), &GuitarBodyMesh::set_slice_grid_type);
    ClassDB::bind_method(D_METHOD("get_slice_grid_type"), &GuitarBodyMesh::get_slice_grid_type);
    ADD_PROPERTY(PropertyInfo(Variant::INT, "slice_grid_type"), "set_slice_grid_type", "get_slice_grid_type");

    ClassDB::bind_method(D_METHOD("set_explode_distance", "val"), &GuitarBodyMesh::set_explode_distance);
    ClassDB::bind_method(D_METHOD("get_explode_distance"), &GuitarBodyMesh::get_explode_distance);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "explode_distance"), "set_explode_distance", "get_explode_distance");

    ClassDB::bind_method(D_METHOD("set_show_dowel_pins", "val"), &GuitarBodyMesh::set_show_dowel_pins);
    ClassDB::bind_method(D_METHOD("get_show_dowel_pins"), &GuitarBodyMesh::get_show_dowel_pins);
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "show_dowel_pins"), "set_show_dowel_pins", "get_show_dowel_pins");

    ClassDB::bind_method(D_METHOD("set_dowel_diameter", "val"), &GuitarBodyMesh::set_dowel_diameter);
    ClassDB::bind_method(D_METHOD("get_dowel_diameter"), &GuitarBodyMesh::get_dowel_diameter);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "dowel_diameter"), "set_dowel_diameter", "get_dowel_diameter");

    ClassDB::bind_method(D_METHOD("set_dowel_length", "val"), &GuitarBodyMesh::set_dowel_length);
    ClassDB::bind_method(D_METHOD("get_dowel_length"), &GuitarBodyMesh::get_dowel_length);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "dowel_length"), "set_dowel_length", "get_dowel_length");

    ClassDB::bind_method(D_METHOD("set_dowel_clearance", "val"), &GuitarBodyMesh::set_dowel_clearance);
    ClassDB::bind_method(D_METHOD("get_dowel_clearance"), &GuitarBodyMesh::get_dowel_clearance);
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "dowel_clearance"), "set_dowel_clearance", "get_dowel_clearance");

    ClassDB::bind_method(D_METHOD("get_slice_count"), &GuitarBodyMesh::get_slice_count);
    ClassDB::bind_method(D_METHOD("get_slice_mesh", "idx"), &GuitarBodyMesh::get_slice_mesh);
    ClassDB::bind_method(D_METHOD("get_slice_direction", "idx"), &GuitarBodyMesh::get_slice_direction);

    ClassDB::bind_method(D_METHOD("get_dowel_pin_count"), &GuitarBodyMesh::get_dowel_pin_count);
    ClassDB::bind_method(D_METHOD("get_dowel_pin_transform", "idx"), &GuitarBodyMesh::get_dowel_pin_transform);
    ClassDB::bind_method(D_METHOD("get_dowel_pin_direction", "idx"), &GuitarBodyMesh::get_dowel_pin_direction);
    ClassDB::bind_method(D_METHOD("get_dowel_pin_mesh"), &GuitarBodyMesh::get_dowel_pin_mesh);

    ClassDB::bind_method(D_METHOD("export_full_stl", "filepath"), &GuitarBodyMesh::export_full_stl);
    ClassDB::bind_method(D_METHOD("export_slices_stl", "dirpath"), &GuitarBodyMesh::export_slices_stl);
    ClassDB::bind_method(D_METHOD("export_2d_dxf", "filepath"), &GuitarBodyMesh::export_2d_dxf);
    ClassDB::bind_method(D_METHOD("export_3mf", "filepath"), &GuitarBodyMesh::export_3mf);

    ClassDB::bind_method(D_METHOD("rebuild_slices"), &GuitarBodyMesh::rebuild_slices);
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

void GuitarBodyMesh::set_piezo_saddles_enabled(bool p_val) {
    if (piezo_saddles_enabled != p_val) {
        piezo_saddles_enabled = p_val;
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

void GuitarBodyMesh::set_sphere_modifiers_enabled(bool p_val) {
    if (sphere_modifiers_enabled != p_val) {
        sphere_modifiers_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_sphere_count(int p_val) {
    if (sphere_count != p_val) {
        sphere_count = p_val;
        if (sphere_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_sphere_radius(double p_val) {
    if (sphere_radius != p_val) {
        sphere_radius = p_val;
        if (sphere_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_cylinder_modifiers_enabled(bool p_val) {
    if (cylinder_modifiers_enabled != p_val) {
        cylinder_modifiers_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_cylinder_count(int p_val) {
    if (cylinder_count != p_val) {
        cylinder_count = p_val;
        if (cylinder_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_cylinder_radius(double p_val) {
    if (cylinder_radius != p_val) {
        cylinder_radius = p_val;
        if (cylinder_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_cylinder_angle(double p_val) {
    if (cylinder_angle != p_val) {
        cylinder_angle = p_val;
        if (cylinder_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_honeycomb_modifiers_enabled(bool p_val) {
    if (honeycomb_modifiers_enabled != p_val) {
        honeycomb_modifiers_enabled = p_val;
        rebuild_mesh();
    }
}

void GuitarBodyMesh::set_honeycomb_cell_size(double p_val) {
    if (honeycomb_cell_size != p_val) {
        honeycomb_cell_size = p_val;
        if (honeycomb_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_modifier_seed(int p_val) {
    if (modifier_seed != p_val) {
        modifier_seed = p_val;
        if (sphere_modifiers_enabled || cylinder_modifiers_enabled) rebuild_mesh();
    }
}

void GuitarBodyMesh::set_slicing_enabled(bool p_val) {
    if (slicing_enabled != p_val) {
        slicing_enabled = p_val;
        if (slicing_enabled) {
            rebuild_slices();
        }
    }
}

void GuitarBodyMesh::set_slice_grid_type(int p_val) {
    if (slice_grid_type != p_val) {
        slice_grid_type = p_val;
        if (slicing_enabled) {
            rebuild_slices();
        }
    }
}

void GuitarBodyMesh::set_explode_distance(double p_val) {
    if (explode_distance != p_val) {
        explode_distance = p_val;
    }
}

void GuitarBodyMesh::set_show_dowel_pins(bool p_val) {
    if (show_dowel_pins != p_val) {
        show_dowel_pins = p_val;
    }
}

void GuitarBodyMesh::set_dowel_diameter(double p_val) {
    if (dowel_diameter != p_val) {
        dowel_diameter = p_val;
        if (slicing_enabled) {
            rebuild_slices();
        }
    }
}

void GuitarBodyMesh::set_dowel_length(double p_val) {
    if (dowel_length != p_val) {
        dowel_length = p_val;
        if (slicing_enabled) {
            rebuild_slices();
        }
    }
}

void GuitarBodyMesh::set_dowel_clearance(double p_val) {
    if (dowel_clearance != p_val) {
        dowel_clearance = p_val;
        if (slicing_enabled) {
            rebuild_slices();
        }
    }
}

Ref<ArrayMesh> GuitarBodyMesh::get_slice_mesh(int p_idx) const {
    if (p_idx >= 0 && p_idx < (int)slice_meshes.size()) {
        return slice_meshes[p_idx];
    }
    return Ref<ArrayMesh>();
}

Vector3 GuitarBodyMesh::get_slice_direction(int p_idx) const {
    if (p_idx >= 0 && p_idx < (int)slice_directions.size()) {
        return slice_directions[p_idx];
    }
    return Vector3();
}

Transform3D GuitarBodyMesh::get_dowel_pin_transform(int p_idx) const {
    if (p_idx >= 0 && p_idx < (int)dowel_transforms.size()) {
        return dowel_transforms[p_idx];
    }
    return Transform3D();
}

Vector3 GuitarBodyMesh::get_dowel_pin_direction(int p_idx) const {
    if (p_idx >= 0 && p_idx < (int)dowel_directions.size()) {
        return dowel_directions[p_idx];
    }
    return Vector3(0, 0, 0);
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

static Ref<ArrayMesh> convert_mesh_gl_to_godot(
    const manifold::MeshGL& mesh_gl,
    float scale_factor,
    float center_y,
    float center_z,
    double total_hip = 318.0,
    double L = 446.0,
    double b_hip = 159.0
) {
    size_t num_verts = mesh_gl.NumVert();
    int num_props = mesh_gl.numProp;
    if (num_verts == 0) return Ref<ArrayMesh>();

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

        vertices[(int64_t)v] = Vector3(px, py - center_y, pz - center_z);

        if (num_props >= 6) {
            float nx = mesh_gl.vertProperties[v * num_props + 3];
            float ny = mesh_gl.vertProperties[v * num_props + 4];
            float nz = mesh_gl.vertProperties[v * num_props + 5];
            normals[(int64_t)v] = Vector3(nx, ny, nz);
        } else {
            normals[(int64_t)v] = Vector3(0, 0, 1);
        }

        float u = (px + (float)b_hip * scale_factor) / (float)(total_hip * scale_factor);
        float v_coord = py / (float)(L * scale_factor);
        uvs[(int64_t)v] = Vector2(u, v_coord);
    }

    size_t num_indices = mesh_gl.triVerts.size();
    indices.resize((int64_t)num_indices);
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
    return godot_mesh;
}

static bool write_binary_stl(const String& p_filepath, const manifold::MeshGL& mesh_gl, float scale_factor, float center_y, float center_z) {
    Ref<FileAccess> file = FileAccess::open(p_filepath, FileAccess::WRITE);
    if (!file.is_valid()) {
        return false;
    }
    uint8_t header[80] = {0};
    const char* title = "GuitarBuilder 3D Production - Watertight Manifold";
    memcpy(header, title, std::min((size_t)80, strlen(title)));
    file->store_buffer(header, 80);

    size_t num_indices = mesh_gl.triVerts.size();
    uint32_t num_triangles = (uint32_t)(num_indices / 3);
    file->store_32(num_triangles);

    int num_props = mesh_gl.numProp;
    for (size_t t = 0; t < num_triangles; ++t) {
        uint32_t i0 = mesh_gl.triVerts[t * 3 + 0];
        uint32_t i1 = mesh_gl.triVerts[t * 3 + 1];
        uint32_t i2 = mesh_gl.triVerts[t * 3 + 2];

        float v0x = mesh_gl.vertProperties[i0 * num_props + 0] * scale_factor;
        float v0y = mesh_gl.vertProperties[i0 * num_props + 1] * scale_factor - center_y;
        float v0z = mesh_gl.vertProperties[i0 * num_props + 2] * scale_factor - center_z;

        float v1x = mesh_gl.vertProperties[i1 * num_props + 0] * scale_factor;
        float v1y = mesh_gl.vertProperties[i1 * num_props + 1] * scale_factor - center_y;
        float v1z = mesh_gl.vertProperties[i1 * num_props + 2] * scale_factor - center_z;

        float v2x = mesh_gl.vertProperties[i2 * num_props + 0] * scale_factor;
        float v2y = mesh_gl.vertProperties[i2 * num_props + 1] * scale_factor - center_y;
        float v2z = mesh_gl.vertProperties[i2 * num_props + 2] * scale_factor - center_z;

        float e1x = v1x - v0x, e1y = v1y - v0y, e1z = v1z - v0z;
        float e2x = v2x - v0x, e2y = v2y - v0y, e2z = v2z - v0z;
        float nx = e1y * e2z - e1z * e2y;
        float ny = e1z * e2x - e1x * e2z;
        float nz = e1x * e2y - e1y * e2x;
        float nlen = std::sqrt(nx * nx + ny * ny + nz * nz);
        if (nlen > 1e-6f) { nx /= nlen; ny /= nlen; nz /= nlen; }

        file->store_float(nx);
        file->store_float(ny);
        file->store_float(nz);

        file->store_float(v0x);
        file->store_float(v0y);
        file->store_float(v0z);

        file->store_float(v1x);
        file->store_float(v1y);
        file->store_float(v1z);

        file->store_float(v2x);
        file->store_float(v2y);
        file->store_float(v2z);

        file->store_16(0);
    }
    file->close();
    return true;
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

    // Control Cavity & Potentiometer Shaft Holes
    // Situated at cc_x = 88.0, cc_y = 175.0 to guarantee ample clearance (> 16mm)
    // from the vertical slicing plane (X=50), > 17mm from horizontal bridge cut (Y=110),
    // and completely self-contained within the right wing.
    double cc_x = 88.0;
    double cc_y = 175.0 * scale_y;
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

        // Piezo saddle wire slots & angled routing into main electronics cavity
        // Slots are not cut all the way through; they plunge to progressive depths
        // (slot 1 shallow at 8mm, slot 6 deep at 18mm) and connect to an angled tunnel guiding wires directly into the control cavity.
        if (piezo_saddles_enabled) {
            double r = 1.5;
            double y_bot = b_y + 7.5 * scale_y;
            double y_top = b_y + 10.5 * scale_y;
            double y_center = b_y + 9.0 * scale_y;
            double spacing = 10.5;
            const int segs = 12;

            for (int i = 0; i < 6; ++i) {
                double sx = -26.25 + i * spacing;
                SimplePolygon slot_pts;
                for (int s = 0; s <= segs; ++s) {
                    double ang = s * 3.141592653589793 / segs;
                    slot_pts.push_back(vec2{ sx + r * std::cos(ang), y_top + r * std::sin(ang) });
                }
                for (int s = 0; s <= segs; ++s) {
                    double ang = 3.141592653589793 + s * 3.141592653589793 / segs;
                    slot_pts.push_back(vec2{ sx + r * std::cos(ang), y_bot + r * std::sin(ang) });
                }
                CrossSection cs_slot(slot_pts, CrossSection::FillRule::Positive);
                // Progressive depth: 8mm for 1st slot up to 18mm for 6th slot
                double slot_depth = 8.0 + i * 2.0;
                Manifold piezo_slot = Manifold::Extrude(cs_slot.ToPolygons(), slot_depth + 2.0)
                    .Translate(vec3{ 0.0, 0.0, body_thickness - slot_depth });
                body = body - piezo_slot;
            }

            // Angled channel sloping under all 6 slots (from slot 1 at depth 8mm to slot 6 at depth 18mm)
            vec3 p_first{ -26.25, y_center, body_thickness - 8.0 };
            vec3 p_last{   26.25, y_center, body_thickness - 18.0 };
            Manifold saddle_wire_ramp = make_tunnel(p_first, p_last, 2.5);
            saddle_wire_ramp = saddle_wire_ramp + Manifold::Sphere(2.5, 16).Translate(p_first);

            // Angled tunnel routing from 6th slot directly across to the main electronics cavity
            vec3 p_cc{ cc_x - 14.0, cc_y, drill_z };
            Manifold piezo_to_cavity = make_tunnel(p_last, p_cc, 3.0);
            piezo_to_cavity = piezo_to_cavity + Manifold::Sphere(3.0, 16).Translate(p_last);

            body = body - saddle_wire_ramp - piezo_to_cavity;
        }
    }

    if (control_cavity_enabled) {
        double pocket_depth = std::min(control_cavity_depth, body_thickness - 6.0);

        // Organic control cavity polygon contained within [X: 56..98, Y: 121..219]
        SimplePolygon cc_pts = {
            vec2{ -14.0, -48.0 }, // Bottom tail
            vec2{  14.0, -46.0 }, // Bottom tail right
            vec2{  20.0, -20.0 }, // Lower-right flank
            vec2{  22.0,  15.0 }, // Mid-right flank
            vec2{  14.0,  38.0 }, // Top-right flank
            vec2{ -14.0,  38.0 }, // Top-left
            vec2{ -14.0,   5.0 }  // Mid-left (facing bridge with >28mm solid wood wall)
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
            vec2{ cc_x, cc_y + 20.0 },
            vec2{ cc_x + 6.0, cc_y - 12.0 },
            vec2{ cc_x + 2.0, cc_y - 44.0 }
        };
        for (const auto& pos : pot_positions) {
            Manifold pot_hole = Manifold::Cylinder(body_thickness + 4.0, 4.8, 4.8, 20)
                .Translate(vec3{ pos.x, pos.y, -2.0 });
            body = body - pot_hole;
        }
    }

    // Wiring Tunnels
    if (wiring_tunnels_enabled) {
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
            vec3 p_cc{ cc_x - 10.0, cc_y + 15.0 * scale_y, drill_z };
            body = body - make_tunnel(p_brg, p_cc, 4.5);
        } else if (pickup_config == 3) { // HH
            // Direct Neck to Bridge tunnel (8.0mm diameter)
            vec3 p_neck{ p_channel_x, neck_pickup_y * scale_y, drill_z };
            vec3 p_brg{ p_channel_x, bridge_pickup_y * scale_y, drill_z };
            body = body - make_tunnel(p_neck, p_brg, 4.0);

            // Bridge to Control Cavity tunnel (9.0mm diameter)
            vec3 p_cc{ cc_x - 10.0, cc_y + 15.0 * scale_y, drill_z };
            body = body - make_tunnel(p_brg, p_cc, 4.5);
        }

        // 2. Output Jack Tunnel (12.0mm diameter)
        // Drilled from control cavity to the side rim at waypoint 4
        vec3 j_start{ cc_x, cc_y - 35.0 * scale_y, drill_z };
        vec3 j_end{ 145.13 * (t_hip / 159.0), 72.89 * scale_y, drill_z };
        body = body - make_tunnel(j_start, j_end, 6.0);
    }

    // Phase 5: Procedural Modifiers (Sphere Chambering, Angled Cylinders, Honeycomb Lattice)
    // Central Spine Keep-out: X in [-55, +55] mm must remain solid wood (holds neck mortise, pickups, bridge, strings).
    // Control Cavity Exclusion: X in [50, 110], Y in [110 * scale_y, 230 * scale_y].
    if (sphere_modifiers_enabled || cylinder_modifiers_enabled || honeycomb_modifiers_enabled) {
        auto is_protected = [&](double px, double py, double pr) -> bool {
            // 1. Central spine keep-out core
            if (std::abs(px) - pr < 55.0) {
                return true;
            }
            // 2. Control cavity exclusion zone on treble side
            if (px + pr > 50.0 && px - pr < 110.0 && py + pr > 110.0 * scale_y && py - pr < 230.0 * scale_y) {
                return true;
            }
            // 3. Keep within body length bounds
            if (py - pr < 40.0 * scale_y || py + pr > 430.0 * scale_y) {
                return true;
            }
            return false;
        };

        // 1. Sphere Chambering Cutouts
        if (sphere_modifiers_enabled && sphere_count > 0 && sphere_radius > 1.0) {
            uint32_t rng = (uint32_t)(modifier_seed * 1103515245 + 12345);
            auto rand_f = [&]() -> double {
                rng = rng * 1103515245 + 12345;
                return (double)(rng & 0x7FFFFFFF) / (double)0x7FFFFFFF;
            };
            int placed = 0;
            int attempts = 0;
            while (placed < sphere_count && attempts < 300) {
                attempts++;
                bool left_side = (rand_f() > 0.40);
                double px = left_side ? (-70.0 - rand_f() * (b_hip - 85.0)) : (70.0 + rand_f() * (t_hip - 85.0));
                double py = (60.0 + rand_f() * 320.0) * scale_y;
                double pz = body_thickness * 0.5;

                if (is_protected(px, py, sphere_radius)) continue;

                body = body - Manifold::Sphere(sphere_radius, 16).Translate(vec3{ px, py, pz });
                placed++;
            }
        }

        // 2. Angled Perforating Cylinders
        if (cylinder_modifiers_enabled && cylinder_count > 0 && cylinder_radius > 1.0) {
            uint32_t rng = (uint32_t)((modifier_seed + 101) * 1103515245 + 12345);
            auto rand_f = [&]() -> double {
                rng = rng * 1103515245 + 12345;
                return (double)(rng & 0x7FFFFFFF) / (double)0x7FFFFFFF;
            };
            int placed = 0;
            int attempts = 0;
            while (placed < cylinder_count && attempts < 300) {
                attempts++;
                bool left_side = (rand_f() > 0.40);
                double px = left_side ? (-70.0 - rand_f() * (b_hip - 85.0)) : (70.0 + rand_f() * (t_hip - 85.0));
                double py = (60.0 + rand_f() * 320.0) * scale_y;

                if (is_protected(px, py, cylinder_radius)) continue;

                double ang_x = (rand_f() * 2.0 - 1.0) * cylinder_angle;
                double ang_y = (rand_f() * 2.0 - 1.0) * cylinder_angle;

                Manifold cyl = Manifold::Cylinder(body_thickness + 20.0, cylinder_radius, cylinder_radius, 16)
                    .Translate(vec3{ 0.0, 0.0, -10.0 })
                    .Rotate(ang_x, ang_y, 0.0)
                    .Translate(vec3{ px, py, 0.0 });
                body = body - cyl;
                placed++;
            }
        }

        // 3. Honeycomb Lattice
        if (honeycomb_modifiers_enabled && honeycomb_cell_size >= 10.0) {
            double s = honeycomb_cell_size;
            double r_hex = s * 0.44;
            double dx = s * 1.5;
            double dy = s * 0.8660254037844386 * 2.0;

            for (double px = -b_hip + s * 0.5; px <= -55.0 - r_hex; px += dx) {
                for (double py = 60.0 * scale_y; py <= 380.0 * scale_y; py += dy * 0.5) {
                    double offset_x = (((int)(py / (dy * 0.5))) % 2 == 0) ? 0.0 : (dx * 0.5);
                    double cur_x = px + offset_x;
                    if (cur_x > -55.0 - r_hex || is_protected(cur_x, py, r_hex)) continue;

                    Manifold hex = Manifold::Cylinder(body_thickness + 10.0, r_hex, r_hex, 6)
                        .Translate(vec3{ cur_x, py, -5.0 });
                    body = body - hex;
                }
            }

            for (double px = 55.0 + r_hex; px <= t_hip - s * 0.5; px += dx) {
                for (double py = 60.0 * scale_y; py <= 360.0 * scale_y; py += dy * 0.5) {
                    double offset_x = (((int)(py / (dy * 0.5))) % 2 == 0) ? 0.0 : (dx * 0.5);
                    double cur_x = px + offset_x;
                    if (cur_x < 55.0 + r_hex || is_protected(cur_x, py, r_hex)) continue;

                    Manifold hex = Manifold::Cylinder(body_thickness + 10.0, r_hex, r_hex, 6)
                        .Translate(vec3{ cur_x, py, -5.0 });
                    body = body - hex;
                }
            }
        }
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
    float center_y = (float)(240.0 * scale_y * scale_factor);
    float center_z = (float)(body_thickness * 0.5 * scale_factor);

    current_body = body;
    Ref<ArrayMesh> godot_mesh = convert_mesh_gl_to_godot(mesh_gl, scale_factor, center_y, center_z, (float)(t_hip + b_hip), (float)L, (float)b_hip);
    set_mesh(godot_mesh);

    if (slicing_enabled) {
        rebuild_slices();
    }
}

void GuitarBodyMesh::rebuild_slices() {
    using namespace manifold;

    slice_meshes.clear();
    current_slices.clear();
    slice_directions.clear();
    dowel_transforms.clear();

    if (current_body.IsEmpty()) {
        return;
    }

    double L = body_length;
    double scale_y = L / 446.0;
    float scale_factor = 0.001f;
    float center_y = (float)(240.0 * scale_y * scale_factor);
    float center_z = (float)(body_thickness * 0.5 * scale_factor);

    std::vector<Manifold> parts;

    // --- Structural 8-Piece Cutting Strategy (matches original Python PoC) ---
    // 1. Cut 1: Horizontal cut below the bridge (preserving unified bridge and ferrules)
    double y_bridge_cut = 110.0 * scale_y;
    // Normal {0, -1, 0} at -y_bridge_cut:
    // first has -y > -y_bridge_cut => y < y_bridge_cut (Bottom)
    // second has y > y_bridge_cut (Top)
    auto [body_bottom, body_top] = current_body.SplitByPlane(vec3{ 0.0, -1.0, 0.0 }, -y_bridge_cut);

    // 2. Cut 2: Bottom part cut in half vertically along centerline X = 0
    // first: -x > 0 => x < 0 (Bot Left)
    // second: x > 0 (Bot Right)
    auto [part_bot_left, part_bot_right] = body_bottom.SplitByPlane(vec3{ -1.0, 0.0, 0.0 }, 0.0);

    // 3. Cut 3 & 4: Top half cut vertically either side of neck/bridge
    // Center block width: 100mm (from X = -50 to X = +50)
    // Encompasses entire neck pocket (56mm), pickups (70-84mm), and bridge (76-84mm)
    double center_x = 50.0;
    // Split at X = -50:
    // first: -x > 50 => x < -50 (Left Wing)
    // second: x > -50 (Center Core + Right Wing)
    auto [wing_left, center_and_right] = body_top.SplitByPlane(vec3{ -1.0, 0.0, 0.0 }, center_x);

    // Split at X = +50:
    // first: -x > -50 => x < 50 (Center Core: -50 <= x <= 50)
    // second: x > 50 (Right Wing)
    auto [center_core, wing_right] = center_and_right.SplitByPlane(vec3{ -1.0, 0.0, 0.0 }, -center_x);

    // 4. Cut 5, 6, 7: Cut the 3 resultant parts horizontally once each in sensible places
    // Wing cuts at waist/chest horizontal line (Y = 260mm)
    double y_wing_cut = 260.0 * scale_y;
    auto [part_mid_left, part_top_left] = wing_left.SplitByPlane(vec3{ 0.0, -1.0, 0.0 }, -y_wing_cut);
    auto [part_mid_right, part_top_right] = wing_right.SplitByPlane(vec3{ 0.0, -1.0, 0.0 }, -y_wing_cut);

    // Center Core cut between middle pickup and neck pickup (Y = 267.5mm)
    // Preserves pickups without cutting through cavities or the neck pocket!
    double y_center_cut = 267.5 * scale_y;
    auto [part_mid, part_top_mid] = center_core.SplitByPlane(vec3{ 0.0, -1.0, 0.0 }, -y_center_cut);

    // 8 distinct parts
    parts = {
        part_bot_left,   // 0: Bot Left
        part_bot_right,  // 1: Bot Right
        part_mid_left,   // 2: Mid Left Wing
        part_top_left,   // 3: Top Left Horn
        part_mid_right,  // 4: Mid Right Wing
        part_top_right,  // 5: Top Right Horn
        part_mid,        // 6: Center Mid (Unified Bridge, Saddles & Pickups)
        part_top_mid     // 7: Center Top Mid (Unified Neck Pocket Mortise)
    };

    slice_directions = {
        Vector3(-0.707f, -0.707f, 0.0f), // 0: Bot Left
        Vector3( 0.707f, -0.707f, 0.0f), // 1: Bot Right
        Vector3(-1.000f, -0.100f, 0.0f), // 2: Mid Left
        Vector3(-0.707f,  0.707f, 0.0f), // 3: Top Left Horn
        Vector3( 1.000f, -0.100f, 0.0f), // 4: Mid Right
        Vector3( 0.707f,  0.707f, 0.0f), // 5: Top Right Horn
        Vector3( 0.000f, -0.350f, 0.0f), // 6: Center Bridge block
        Vector3( 0.000f,  0.850f, 0.0f)  // 7: Center Neck block
    };

    // Dowel Pin Specs (pos, axis, part_a, part_b) in model mm
    // Carefully placed in solid wood regions avoiding all cavities and wiring channels.
    struct DowelSpec {
        vec3 pos;
        vec3 axis;
        int part_a;
        int part_b;
    };
    std::vector<DowelSpec> specs;
    double mid_z = body_thickness * 0.5;

    // 1. Bot_Left (0) <-> Bot_Right (1) (centerline below bridge)
    specs.push_back({ vec3{ 0.0, 55.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 0, 1 });

    // 2. Horizontal seam below bridge (Y = y_bridge_cut)
    specs.push_back({ vec3{ -95.0, y_bridge_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 0, 2 }); // Bot_Left <-> Mid_Left
    specs.push_back({ vec3{ -25.0, y_bridge_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 0, 6 }); // Bot_Left <-> Center_Mid
    specs.push_back({ vec3{  25.0, y_bridge_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 1, 6 }); // Bot_Right <-> Center_Mid
    specs.push_back({ vec3{ 130.0, y_bridge_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 1, 4 }); // Bot_Right <-> Mid_Right

    // 3. Vertical seams between wings and center core (X = -50 and X = +50)
    // Left seam (X = -50): 100% solid wood throughout
    specs.push_back({ vec3{ -center_x, 150.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 2, 6 }); // Mid_Left <-> Center_Mid (low)
    specs.push_back({ vec3{ -center_x, 210.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 2, 6 }); // Mid_Left <-> Center_Mid (high)
    // Right seam (X = +50): solid wood below control cavity (Y=120) and between pickups (Y=210, well clear of middle pickup)
    specs.push_back({ vec3{  center_x, 120.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 4, 6 }); // Mid_Right <-> Center_Mid (low)
    specs.push_back({ vec3{  center_x, 210.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 4, 6 }); // Mid_Right <-> Center_Mid (high)

    // 4. Horizontal seams on wings (Y = y_wing_cut)
    specs.push_back({ vec3{ -90.0, y_wing_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 2, 3 }); // Mid_Left <-> Top_Left
    specs.push_back({ vec3{  90.0, y_wing_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 4, 5 }); // Mid_Right <-> Top_Right

    // 5. Vertical seams on horns to top center (X = -50 and X = +50)
    // In solid wood between pickups and neck pocket (Y=315), well clear of cutaway scoop floor (Y=368)
    specs.push_back({ vec3{ -center_x, 315.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 3, 7 }); // Top_Left <-> Top_Mid
    specs.push_back({ vec3{  center_x, 315.0 * scale_y, mid_z }, vec3{ 1.0, 0.0, 0.0 }, 5, 7 }); // Top_Right <-> Top_Mid

    // 6. Horizontal seam in center core (Y = y_center_cut)
    // In solid wood between middle pickup and neck pickup, avoiding treble wiring tunnel at X=22
    specs.push_back({ vec3{ -25.0, y_center_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 6, 7 }); // Center_Mid <-> Top_Mid (bass side)
    specs.push_back({ vec3{  38.0, y_center_cut, mid_z }, vec3{ 0.0, 1.0, 0.0 }, 6, 7 }); // Center_Mid <-> Top_Mid (treble side)

    // Drill blind dowel holes and store dowel transforms and motion directions
    dowel_directions.clear();
    double hole_rad = (dowel_diameter + dowel_clearance) * 0.5;
    for (const auto& sp : specs) {
        Manifold hole = Manifold::Cylinder(dowel_length, hole_rad, hole_rad, 20)
            .Translate(vec3{ 0.0, 0.0, -dowel_length * 0.5 });
        Basis b;
        if (std::abs(sp.axis.x) > 0.9) {
            hole = hole.Rotate(0.0, 90.0, 0.0);
            b = Basis(Vector3(0, 0, -1), Vector3(0, 1, 0), Vector3(1, 0, 0));
        } else if (std::abs(sp.axis.y) > 0.9) {
            hole = hole.Rotate(-90.0, 0.0, 0.0);
            b = Basis(Vector3(1, 0, 0), Vector3(0, 0, 1), Vector3(0, -1, 0));
        }
        hole = hole.Translate(sp.pos);

        for (auto& p : parts) {
            p = p - hole;
        }

        Vector3 w_pos(sp.pos.x * scale_factor, sp.pos.y * scale_factor - center_y, sp.pos.z * scale_factor - center_z);
        dowel_transforms.push_back(Transform3D(b, w_pos));

        // Dowel pin motion vector: average of its two mating pieces so it stays centered in the seam gap!
        Vector3 pin_dir = (slice_directions[sp.part_a] + slice_directions[sp.part_b]) * 0.5f;
        dowel_directions.push_back(pin_dir);
    }

    // Create printable chamfered dowel pin mesh
    SimplePolygon pin_pts = {
        vec2{ 0.0, -dowel_length * 0.5 },
        vec2{ dowel_diameter * 0.5 - 0.8, -dowel_length * 0.5 },
        vec2{ dowel_diameter * 0.5, -dowel_length * 0.5 + 0.8 },
        vec2{ dowel_diameter * 0.5,  dowel_length * 0.5 - 0.8 },
        vec2{ dowel_diameter * 0.5 - 0.8,  dowel_length * 0.5 },
        vec2{ 0.0,  dowel_length * 0.5 }
    };
    CrossSection cs_pin(pin_pts, CrossSection::FillRule::Positive);
    Manifold m_pin = Manifold::Revolve(cs_pin.ToPolygons(), 24);
    dowel_pin_mesh = convert_mesh_gl_to_godot(m_pin.CalculateNormals(0, 45.0).GetMeshGL(), scale_factor, 0.0f, 0.0f);

    // Save current slices and convert to ArrayMesh
    current_slices = parts;
    for (auto& p : parts) {
        p = p.CalculateNormals(0, 45.0);
        Ref<ArrayMesh> am = convert_mesh_gl_to_godot(p.GetMeshGL(), scale_factor, center_y, center_z);
        slice_meshes.push_back(am);
    }
}

bool GuitarBodyMesh::export_full_stl(const String& p_filepath) {
    using namespace manifold;
    if (current_body.IsEmpty()) return false;
    return write_binary_stl(p_filepath, current_body.GetMeshGL(), 1.0f, 0.0f, 0.0f);
}

bool GuitarBodyMesh::export_slices_stl(const String& p_dirpath) {
    using namespace manifold;
    Ref<DirAccess> dir = DirAccess::open(p_dirpath);
    if (!dir.is_valid()) {
        DirAccess::make_dir_recursive_absolute(p_dirpath);
    }
    if (current_slices.empty()) {
        rebuild_slices();
    }
    std::vector<String> part_tags = {
        "bot_left",
        "bot_right",
        "mid_left",
        "top_left_horn",
        "mid_right",
        "top_right_horn",
        "center_bridge",
        "center_neck"
    };
    for (size_t i = 0; i < current_slices.size(); ++i) {
        String num_name = p_dirpath.path_join("guitar_body_part_" + String::num_int64(i + 1) + ".stl");
        write_binary_stl(num_name, current_slices[i].GetMeshGL(), 1.0f, 0.0f, 0.0f);
        if (i < part_tags.size()) {
            String desc_name = p_dirpath.path_join("guitar_body_part_" + String::num_int64(i + 1) + "_" + part_tags[i] + ".stl");
            write_binary_stl(desc_name, current_slices[i].GetMeshGL(), 1.0f, 0.0f, 0.0f);
        }
    }
    // Export 6mm dowel pin
    SimplePolygon pin_pts = {
        vec2{ 0.0, -dowel_length * 0.5 },
        vec2{ dowel_diameter * 0.5 - 0.8, -dowel_length * 0.5 },
        vec2{ dowel_diameter * 0.5, -dowel_length * 0.5 + 0.8 },
        vec2{ dowel_diameter * 0.5,  dowel_length * 0.5 - 0.8 },
        vec2{ dowel_diameter * 0.5 - 0.8,  dowel_length * 0.5 },
        vec2{ 0.0,  dowel_length * 0.5 }
    };
    CrossSection cs_pin(pin_pts, CrossSection::FillRule::Positive);
    manifold::Manifold m_pin = manifold::Manifold::Revolve(cs_pin.ToPolygons(), 24);
    String pin_fname = p_dirpath.path_join("dowel_pin_6mm.stl");
    write_binary_stl(pin_fname, m_pin.GetMeshGL(), 1.0f, 0.0f, 0.0f);
    return true;
}

bool GuitarBodyMesh::export_2d_dxf(const String& p_filepath) {
    using namespace manifold;
    Ref<FileAccess> file = FileAccess::open(p_filepath, FileAccess::WRITE);
    if (!file.is_valid()) return false;

    // Header & Tables
    file->store_string("0\nSECTION\n2\nHEADER\n0\nENDSEC\n");
    file->store_string("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n5\n");
    auto write_layer = [&](const char* name, int color) {
        file->store_string("0\nLAYER\n2\n");
        file->store_string(name);
        file->store_string("\n70\n0\n62\n");
        file->store_string(String::num_int64(color) + "\n6\nCONTINUOUS\n");
    };
    write_layer("PERIMETER", 1);       // Red
    write_layer("CONTROL_CAVITY", 3);  // Green
    write_layer("NECK_POCKET", 5);     // Blue
    write_layer("PICKUPS", 4);         // Cyan
    write_layer("BRIDGE_HOLES", 2);    // Yellow
    file->store_string("0\nENDTAB\n0\nENDSEC\n");

    // Entities
    file->store_string("0\nSECTION\n2\nENTITIES\n");

    auto write_poly = [&](const std::vector<manifold::vec2>& pts, const char* layer, bool closed) {
        file->store_string("0\nPOLYLINE\n8\n");
        file->store_string(layer);
        file->store_string("\n66\n1\n70\n");
        file->store_string(closed ? "1\n" : "0\n");
        for (const auto& pt : pts) {
            file->store_string("0\nVERTEX\n8\n");
            file->store_string(layer);
            file->store_string("\n10\n" + String::num_real(pt.x) + "\n20\n" + String::num_real(pt.y) + "\n30\n0.0\n");
        }
        file->store_string("0\nSEQEND\n");
    };

    auto write_circ = [&](double cx, double cy, double rad, const char* layer) {
        file->store_string("0\nCIRCLE\n8\n");
        file->store_string(layer);
        file->store_string("\n10\n" + String::num_real(cx) + "\n20\n" + String::num_real(cy) + "\n30\n0.0\n");
        file->store_string("40\n" + String::num_real(rad) + "\n");
    };

    double scale_y = body_length / 446.0;

    // 1. Neck Pocket Box
    if (neck_pocket_enabled) {
        double nw = neck_pocket_width * 0.5;
        double ny_start = (399.7 - neck_pocket_length) * scale_y;
        double ny_end = 399.7 * scale_y;
        std::vector<manifold::vec2> np_pts = {
            manifold::vec2{ -nw, ny_start }, manifold::vec2{ nw, ny_start },
            manifold::vec2{ nw, ny_end }, manifold::vec2{ -nw, ny_end }
        };
        write_poly(np_pts, "NECK_POCKET", true);
    }

    // 2. Pickups
    auto write_pickup = [&](double py, bool is_hum, double slant) {
        double w = is_hum ? 84.0 : 70.0;
        double l = is_hum ? 38.0 : 18.0;
        double cos_a = std::cos(slant * 3.141592653589793 / 180.0);
        double sin_a = std::sin(slant * 3.141592653589793 / 180.0);
        std::vector<manifold::vec2> box = {
            manifold::vec2{ -w * 0.5, -l * 0.5 }, manifold::vec2{ w * 0.5, -l * 0.5 },
            manifold::vec2{  w * 0.5,  l * 0.5 }, manifold::vec2{ -w * 0.5,  l * 0.5 }
        };
        std::vector<manifold::vec2> rot_box;
        for (const auto& b : box) {
            rot_box.push_back(manifold::vec2{ b.x * cos_a - b.y * sin_a, py + b.x * sin_a + b.y * cos_a });
        }
        write_poly(rot_box, "PICKUPS", true);
    };

    if (pickup_config == 1) { // SSS
        write_pickup(bridge_pickup_y * scale_y, false, bridge_pickup_slant);
        write_pickup(middle_pickup_y * scale_y, false, 0.0);
        write_pickup(neck_pickup_y * scale_y, false, 0.0);
    } else if (pickup_config == 2) { // HSS
        write_pickup(bridge_pickup_y * scale_y, true, 0.0);
        write_pickup(middle_pickup_y * scale_y, false, 0.0);
        write_pickup(neck_pickup_y * scale_y, false, 0.0);
    } else if (pickup_config == 3) { // HH
        write_pickup(bridge_pickup_y * scale_y, true, 0.0);
        write_pickup(neck_pickup_y * scale_y, true, 0.0);
    }

    // 3. Bridge string holes / ferrules
    if (bridge_enabled) {
        double by = bridge_y * scale_y;
        for (int i = 0; i < 6; ++i) {
            double sx = -26.25 + i * 10.5;
            write_circ(sx, by, 1.75, "BRIDGE_HOLES");
            write_circ(sx, by, 4.0, "BRIDGE_HOLES");
        }
        if (piezo_saddles_enabled) {
            double r = 1.5;
            double y_bot = by + 7.5 * scale_y;
            double y_top = by + 10.5 * scale_y;
            const int segs = 12;
            for (int i = 0; i < 6; ++i) {
                double sx = -26.25 + i * 10.5;
                std::vector<manifold::vec2> slot_pts;
                for (int s = 0; s <= segs; ++s) {
                    double ang = s * 3.141592653589793 / segs;
                    slot_pts.push_back(manifold::vec2{ sx + r * std::cos(ang), y_top + r * std::sin(ang) });
                }
                for (int s = 0; s <= segs; ++s) {
                    double ang = 3.141592653589793 + s * 3.141592653589793 / segs;
                    slot_pts.push_back(manifold::vec2{ sx + r * std::cos(ang), y_bot + r * std::sin(ang) });
                }
                write_poly(slot_pts, "BRIDGE_HOLES", true);
            }
        }
    }

    // 4. Control Cavity
    if (control_cavity_enabled) {
        double cc_x = 88.0;
        double cc_y = 175.0 * scale_y;
        manifold::SimplePolygon cc_pts = {
            manifold::vec2{ -14.0, -48.0 }, manifold::vec2{  14.0, -46.0 }, manifold::vec2{  20.0, -20.0 },
            manifold::vec2{  22.0,  15.0 }, manifold::vec2{  14.0,  38.0 }, manifold::vec2{ -14.0,  38.0 },
            manifold::vec2{ -14.0,   5.0 }
        };
        manifold::CrossSection cs_cc(cc_pts, manifold::CrossSection::FillRule::Positive);
        cs_cc = cs_cc.Offset(8.0, manifold::CrossSection::JoinType::Round).Offset(-2.0, manifold::CrossSection::JoinType::Round);
        for (const auto& poly : cs_cc.ToPolygons()) {
            std::vector<manifold::vec2> cc_world;
            for (const auto& pt : poly) {
                cc_world.push_back(manifold::vec2{ cc_x + pt.x, cc_y + pt.y });
            }
            write_poly(cc_world, "CONTROL_CAVITY", true);
        }
        write_circ(cc_x, cc_y + 20.0, 4.75, "CONTROL_CAVITY");
        write_circ(cc_x + 6.0, cc_y - 12.0, 4.75, "CONTROL_CAVITY");
        write_circ(cc_x + 2.0, cc_y - 44.0, 4.75, "CONTROL_CAVITY");
    }

    file->store_string("0\nENDSEC\n0\nEOF\n");
    file->close();
    return true;
}

bool GuitarBodyMesh::export_3mf(const String& p_filepath) {
    Ref<FileAccess> file = FileAccess::open(p_filepath, FileAccess::WRITE);
    if (!file.is_valid()) return false;

    if (current_slices.empty()) {
        rebuild_slices();
    }

    file->store_string("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    file->store_string("<model unit=\"millimeter\" xml:lang=\"en-US\" xmlns=\"http://schemas.microsoft.com/3dmanufacturing/core/2015/02\">\n");
    file->store_string("  <metadata name=\"Title\">GuitarBuilder Production Slices</metadata>\n");
    file->store_string("  <resources>\n");

    for (size_t i = 0; i < current_slices.size(); ++i) {
        manifold::MeshGL gl = current_slices[i].GetMeshGL();
        file->store_string("    <object id=\"" + String::num_int64(i + 1) + "\" type=\"model\">\n");
        file->store_string("      <mesh>\n        <vertices>\n");
        size_t n_verts = gl.NumVert();
        int n_props = gl.numProp;
        for (size_t v = 0; v < n_verts; ++v) {
            float x = gl.vertProperties[v * n_props + 0];
            float y = gl.vertProperties[v * n_props + 1];
            float z = gl.vertProperties[v * n_props + 2];
            file->store_string("          <vertex x=\"" + String::num_real(x) + "\" y=\"" + String::num_real(y) + "\" z=\"" + String::num_real(z) + "\" />\n");
        }
        file->store_string("        </vertices>\n        <triangles>\n");
        size_t n_tris = gl.triVerts.size() / 3;
        for (size_t t = 0; t < n_tris; ++t) {
            uint32_t v1 = gl.triVerts[t * 3 + 0];
            uint32_t v2 = gl.triVerts[t * 3 + 1];
            uint32_t v3 = gl.triVerts[t * 3 + 2];
            file->store_string("          <triangle v1=\"" + String::num_int64(v1) + "\" v2=\"" + String::num_int64(v2) + "\" v3=\"" + String::num_int64(v3) + "\" />\n");
        }
        file->store_string("        </triangles>\n      </mesh>\n    </object>\n");
    }

    file->store_string("  </resources>\n  <build>\n");
    for (size_t i = 0; i < current_slices.size(); ++i) {
        file->store_string("    <item objectid=\"" + String::num_int64(i + 1) + "\" />\n");
    }
    file->store_string("  </build>\n</model>\n");
    file->close();
    return true;
}
