#pragma once

#include <godot_cpp/classes/mesh_instance3d.hpp>
#include <godot_cpp/classes/array_mesh.hpp>
#include <godot_cpp/classes/surface_tool.hpp>
#include <godot_cpp/core/class_db.hpp>

namespace godot {

class GuitarBodyMesh : public MeshInstance3D {
    GDCLASS(GuitarBodyMesh, MeshInstance3D);

private:
    double hip_width = 320.0;
    double waist_width = 228.0;
    double chest_width = 276.0;
    double shoulder_width = 250.0;
    double body_length = 460.0;
    double body_thickness = 45.0;
    double edge_radius = 8.0;

    bool symmetric_mode = true;
    double right_hip_offset = 0.0;
    double right_waist_offset = 0.0;
    double right_chest_offset = 0.0;
    double right_shoulder_offset = 0.0;

    bool belly_cut_enabled = true;
    double belly_cut_depth = 14.0;
    double belly_cut_angle = 18.0;

    bool forearm_bevel_enabled = true;
    double forearm_bevel_depth = 12.0;
    double forearm_bevel_angle = 15.0;

    bool neck_pocket_enabled = true;

protected:
    static void _bind_methods();

public:
    GuitarBodyMesh();
    ~GuitarBodyMesh() override;

    void _ready() override;

    // Getters and Setters
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

    void set_belly_cut_enabled(bool p_val);
    bool get_belly_cut_enabled() const { return belly_cut_enabled; }

    void set_forearm_bevel_enabled(bool p_val);
    bool get_forearm_bevel_enabled() const { return forearm_bevel_enabled; }

    void set_neck_pocket_enabled(bool p_val);
    bool get_neck_pocket_enabled() const { return neck_pocket_enabled; }

    // Core Manifold rebuild routine
    void rebuild_mesh();
};

} // namespace godot
