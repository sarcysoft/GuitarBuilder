# GuitarBuilder Studio

A real-time, parametric luthier CAD and manufacturing preparation studio built with **Godot 4** and Adobe's **Manifold** geometry library via native **C++ GDExtension**.

## Overview

GuitarBuilder enables custom guitar body design, real-time parametric sculpting, interactive hardware cavity routing, and multi-part slicing with coaxial dowel pin registration for consumer 3D printing and CNC manufacturing.

### Key Features
- **Real-Time 60 FPS Viewport**: Instant feedback on body dimensions, ergonomic contours, and finishes powered by Godot 4 (Vulkan Forward+).
- **2D Parametric Spline Lofting**: Continuous cubic spline silhouette lofts with continuous edge fillets, belly cuts, and forearm bevels.
- **Interactive Hardware-to-Cavity Engine**: Eliminates separate cutter models—cavity routes are dynamically generated from physical hardware models with interactive clearance margins, step depths, wire tunnels, and rear cover lips.
- **Watertight Manifold CSG**: Adobe's Manifold geometry engine guarantees 100% 2-manifold watertight booleans with sub-millisecond execution.
- **CAM & Additive Manufacturing**: Two-tier asynchronous 8-way planar body slicing with coaxial 6mm locator pin hole subtraction (0.4mm epoxy relief) and one-click production 3MF / STL / 2D DXF export.
- **Real-Time PBR Visual Studio**: Live slider tuning for dual-layer clearcoats, procedural sunburst gradients, metallic flake, and 3D procedural wood grain.

---

## Repository Structure

- **`src/`**: C++ GDExtension source code (Manifold integration, parametric spline engine, CAM slicer).
- **`project/`**: Godot 4 project files (UI, viewports, materials, shaders, scenes).
- **`assets/`**: Standardized 3D hardware assets (bridges, pickups, pots, jacks).
- **`legacy_poc/`**: The archived Python 3.10 / OpenSCAD / Blender Geometry Nodes proof-of-concept toolchain. See [`legacy_poc/README.md`](legacy_poc/README.md) for historical documentation.
