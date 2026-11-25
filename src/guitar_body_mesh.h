#pragma once

#include <godot_cpp/classes/mesh_instance3d.hpp>
#include <godot_cpp/classes/array_mesh.hpp>
#include <godot_cpp/classes/surface_tool.hpp>
#include <godot_cpp/core/class_db.hpp>

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

    bool neck_pocket_enabled = false;

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

    // Core Manifold rebuild routine
    void rebuild_mesh();
};

} // namespace godot
