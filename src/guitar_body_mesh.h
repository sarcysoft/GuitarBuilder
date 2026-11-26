#pragma once

#include <godot_cpp/classes/mesh_instance3d.hpp>
#include <godot_cpp/classes/array_mesh.hpp>
#include <godot_cpp/classes/surface_tool.hpp>
#include <godot_cpp/core/class_db.hpp>

#include "manifold/manifold.h"
#include <vector>

namespace godot {

class GuitarBodyMesh : public MeshInstance3D {
    GDCLASS(GuitarBodyMesh, MeshInstance3D);

private:
    double hip_width = 318.0;
    double waist_width = 231.0;
    double chest_width = 275.0;
    double shoulder_width = 250.0;
    double body_length = 446.0;
    double body_thickness = 45.0;
    double edge_radius = 8.0;

    bool symmetric_mode = true;
    double horn_reach = 446.4;
    double horn_roundness = 1.0;

    // Independent side parameters (Asymmetric mode)
    double treble_hip_width = 159.0;
    double bass_hip_width = 159.0;
    double treble_waist_width = 115.6;
    double bass_waist_width = 115.6;
    double treble_chest_width = 137.5;
    double bass_chest_width = 137.5;
    double treble_shoulder_width = 125.0;
    double bass_shoulder_width = 125.0;
    double treble_horn_length = 446.4;
    double bass_horn_length = 458.0;
    double treble_horn_roundness = 1.0;
    double bass_horn_roundness = 1.0;

    // Ergonomic cuts
    bool belly_cut_enabled = false;
    double belly_cut_depth = 14.0;
    double belly_cut_angle = 10.0;
    double belly_cut_length = 180.0;

    bool forearm_bevel_enabled = false;
    double forearm_bevel_depth = 12.0;
    double forearm_bevel_angle = 8.0;
    double forearm_bevel_length = 160.0;

    // Neck pocket
    bool neck_pocket_enabled = true;
    double neck_pocket_width = 56.5;
    double neck_pocket_length = 76.2;
    double neck_pocket_depth = 16.0;

    // Pickups
    int pickup_config = 1; // 0: None, 1: SSS, 2: HSS, 3: HH
    double bridge_pickup_y = 185.0;
    double middle_pickup_y = 240.0;
    double neck_pickup_y = 295.0;
    double bridge_pickup_slant = 0.0;
    double pickup_clearance = 1.5;
    double pickup_depth = 18.0;

    // Bridge & Tremolo
    bool bridge_enabled = true;
    int bridge_type = 0; // 0: Hardtail, 1: Tremolo
    double bridge_y = 145.0;

    // Control Cavity & Wiring
    bool control_cavity_enabled = true;
    bool control_cavity_rear = true;
    double control_cavity_depth = 38.0;
    bool wiring_tunnels_enabled = true;

    // Phase 3: CAM Slicing, Dowels & Production Export
    bool slicing_enabled = false;
    int slice_grid_type = 2; // 1: 4-Piece [2x2], 2: 8-Piece [2x4]
    double explode_distance = 0.0;
    bool show_dowel_pins = true;
    double dowel_diameter = 6.0;
    double dowel_length = 16.0;
    double dowel_clearance = 0.3;

    // Internal Manifold storage
    manifold::Manifold current_body;
    std::vector<manifold::Manifold> current_slices;
    std::vector<Ref<ArrayMesh>> slice_meshes;
    std::vector<Vector3> slice_directions;
    std::vector<Transform3D> dowel_transforms;
    std::vector<Vector3> dowel_directions;
    Ref<ArrayMesh> dowel_pin_mesh;

protected:
    static void _bind_methods();

public:
    GuitarBodyMesh();
    ~GuitarBodyMesh() override;

    void _ready() override;

    // Unified dimension accessors
    void set_hip_width(double p_val);
    double get_hip_width() const { return hip_width; }

    void set_waist_width(double p_val);
    double get_waist_width() const { return waist_width; }

    void set_chest_width(double p_val);
    double get_chest_width() const { return chest_width; }

    void set_shoulder_width(double p_val);
    double get_shoulder_width() const { return shoulder_width; }

    void set_body_length(double p_val);
    double get_body_length() const { return body_length; }

    void set_body_thickness(double p_val);
    double get_body_thickness() const { return body_thickness; }

    void set_edge_radius(double p_val);
    double get_edge_radius() const { return edge_radius; }

    void set_symmetric_mode(bool p_val);
    bool get_symmetric_mode() const { return symmetric_mode; }

    void set_horn_reach(double p_val);
    double get_horn_reach() const { return horn_reach; }

    void set_horn_roundness(double p_val);
    double get_horn_roundness() const { return horn_roundness; }

    // Independent Treble / Bass accessors
    void set_treble_hip_width(double p_val);
    double get_treble_hip_width() const { return treble_hip_width; }

    void set_bass_hip_width(double p_val);
    double get_bass_hip_width() const { return bass_hip_width; }

    void set_treble_waist_width(double p_val);
    double get_treble_waist_width() const { return treble_waist_width; }

    void set_bass_waist_width(double p_val);
    double get_bass_waist_width() const { return bass_waist_width; }

    void set_treble_chest_width(double p_val);
    double get_treble_chest_width() const { return treble_chest_width; }

    void set_bass_chest_width(double p_val);
    double get_bass_chest_width() const { return bass_chest_width; }

    void set_treble_shoulder_width(double p_val);
    double get_treble_shoulder_width() const { return treble_shoulder_width; }

    void set_bass_shoulder_width(double p_val);
    double get_bass_shoulder_width() const { return bass_shoulder_width; }

    void set_treble_horn_length(double p_val);
    double get_treble_horn_length() const { return treble_horn_length; }

    void set_bass_horn_length(double p_val);
    double get_bass_horn_length() const { return bass_horn_length; }

    void set_treble_horn_roundness(double p_val);
    double get_treble_horn_roundness() const { return treble_horn_roundness; }

    void set_bass_horn_roundness(double p_val);
    double get_bass_horn_roundness() const { return bass_horn_roundness; }

    // Ergonomic cuts accessors
    void set_belly_cut_enabled(bool p_val);
    bool get_belly_cut_enabled() const { return belly_cut_enabled; }

    void set_belly_cut_depth(double p_val);
    double get_belly_cut_depth() const { return belly_cut_depth; }

    void set_belly_cut_angle(double p_val);
    double get_belly_cut_angle() const { return belly_cut_angle; }

    void set_belly_cut_length(double p_val);
    double get_belly_cut_length() const { return belly_cut_length; }

    void set_forearm_bevel_enabled(bool p_val);
    bool get_forearm_bevel_enabled() const { return forearm_bevel_enabled; }

    void set_forearm_bevel_depth(double p_val);
    double get_forearm_bevel_depth() const { return forearm_bevel_depth; }

    void set_forearm_bevel_angle(double p_val);
    double get_forearm_bevel_angle() const { return forearm_bevel_angle; }

    void set_forearm_bevel_length(double p_val);
    double get_forearm_bevel_length() const { return forearm_bevel_length; }

    void set_neck_pocket_enabled(bool p_val);
    bool get_neck_pocket_enabled() const { return neck_pocket_enabled; }

    void set_neck_pocket_width(double p_val);
    double get_neck_pocket_width() const { return neck_pocket_width; }

    void set_neck_pocket_length(double p_val);
    double get_neck_pocket_length() const { return neck_pocket_length; }

    void set_neck_pocket_depth(double p_val);
    double get_neck_pocket_depth() const { return neck_pocket_depth; }

    // Pickups
    void set_pickup_config(int p_val);
    int get_pickup_config() const { return pickup_config; }

    void set_bridge_pickup_y(double p_val);
    double get_bridge_pickup_y() const { return bridge_pickup_y; }

    void set_middle_pickup_y(double p_val);
    double get_middle_pickup_y() const { return middle_pickup_y; }

    void set_neck_pickup_y(double p_val);
    double get_neck_pickup_y() const { return neck_pickup_y; }

    void set_bridge_pickup_slant(double p_val);
    double get_bridge_pickup_slant() const { return bridge_pickup_slant; }

    void set_pickup_clearance(double p_val);
    double get_pickup_clearance() const { return pickup_clearance; }

    void set_pickup_depth(double p_val);
    double get_pickup_depth() const { return pickup_depth; }

    // Bridge & Tremolo
    void set_bridge_enabled(bool p_val);
    bool get_bridge_enabled() const { return bridge_enabled; }

    void set_bridge_type(int p_val);
    int get_bridge_type() const { return bridge_type; }

    void set_bridge_y(double p_val);
    double get_bridge_y() const { return bridge_y; }

    // Control Cavity & Wiring
    void set_control_cavity_enabled(bool p_val);
    bool get_control_cavity_enabled() const { return control_cavity_enabled; }

    void set_control_cavity_rear(bool p_val);
    bool get_control_cavity_rear() const { return control_cavity_rear; }

    void set_control_cavity_depth(double p_val);
    double get_control_cavity_depth() const { return control_cavity_depth; }

    void set_wiring_tunnels_enabled(bool p_val);
    bool get_wiring_tunnels_enabled() const { return wiring_tunnels_enabled; }

    // Phase 3: CAM Slicing, Dowels & Production Export
    void set_slicing_enabled(bool p_val);
    bool get_slicing_enabled() const { return slicing_enabled; }

    void set_slice_grid_type(int p_val);
    int get_slice_grid_type() const { return slice_grid_type; }

    void set_explode_distance(double p_val);
    double get_explode_distance() const { return explode_distance; }

    void set_show_dowel_pins(bool p_val);
    bool get_show_dowel_pins() const { return show_dowel_pins; }

    void set_dowel_diameter(double p_val);
    double get_dowel_diameter() const { return dowel_diameter; }

    void set_dowel_length(double p_val);
    double get_dowel_length() const { return dowel_length; }

    void set_dowel_clearance(double p_val);
    double get_dowel_clearance() const { return dowel_clearance; }

    int get_slice_count() const { return (int)slice_meshes.size(); }
    Ref<ArrayMesh> get_slice_mesh(int p_idx) const;
    Vector3 get_slice_direction(int p_idx) const;

    int get_dowel_pin_count() const { return (int)dowel_transforms.size(); }
    Transform3D get_dowel_pin_transform(int p_idx) const;
    Vector3 get_dowel_pin_direction(int p_idx) const;
    Ref<ArrayMesh> get_dowel_pin_mesh() const { return dowel_pin_mesh; }

    // Production export functions
    bool export_full_stl(const String& p_filepath);
    bool export_slices_stl(const String& p_dirpath);
    bool export_2d_dxf(const String& p_filepath);
    bool export_3mf(const String& p_filepath);

    void rebuild_slices();

    // Core Manifold rebuild routine
    void rebuild_mesh();
};

} // namespace godot
