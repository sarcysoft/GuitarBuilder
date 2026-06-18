# Guitar Builder

An automated toolchain for generating custom guitar body models in Blender and preparing them for cutting/manufacturing. 

The pipeline uses Geometry Nodes inside Blender for parametric body generation, subtracts hardware and electronics fittings, and exports sliced components for physical manufacturing.

---

## Workspace Directory Structure

- **`models/`**: Stores input CAD assets (`.scad`, `.stl`, `.obj`, `.mtl`). The primary guitar body mesh is built/exported to this directory.
- **`config/`**: JSON configuration profiles containing parameters for the Geometry Nodes builder.
- **`3rdParty/`**: External reference assets (such as the neck model) used for display/verification.
- **`output/`**: The directory where final generated pieces/sliced models are exported.
- **`debug/`**: Houses debug files (e.g. `cut_log.txt` and `debug_guitar_result.blend`) and is ignored by Git.

---

## Setup & Requirements

- **Blender 4.0+** (Blender 5.1+ is recommended/tested).
- **Python 3.10+**.
- Ensure `blender` is in your system's PATH. If not, the script will attempt to automatically locate it in standard installation paths for your platform (Windows, macOS, and Linux).

---

## Usage (`guitar_builder.py`)

All setup, custom configuration profiling, and generation tasks can be performed using the unified `guitar_builder.py` script.

### 1. Slicing & Scene Setup (Full Pipeline)
To build the guitar model and run the complete scene setup (applying cuts and exporting the output parts):

```bash
# Run with default parameters
python guitar_builder.py

# Run with a custom profile (e.g., config/sarcaster.json)
python guitar_builder.py sarcaster

# Export full body model without cutting it
python guitar_builder.py --no-cut

# Combined: Run custom profile and export full body without cuts
python guitar_builder.py sarcaster --no-cut
```

### 2. Exporting Model Configuration
Extract the current parameters of the Blender model to a JSON file (stored under the `config/` directory by default):
```bash
# Export default parameters to config/guitar_config.json
python guitar_builder.py --export-config

# Export parameters under a specific profile name (e.g. config/sarcaster.json)
python guitar_builder.py sarcaster --export-config

# Export parameters to a custom file name
python guitar_builder.py --export-config custom.json
```

### 3. Importing and Configurator Utility (Bypassing Slicing)
If you want to configure and build the base guitar mesh directly without doing any scene setup or cutting:

- **Export Config**: `python guitar_builder.py --export-config sarcaster.json`
- **Import Config**: `python guitar_builder.py --import-config sarcaster.json`
- **Generate Mesh**: `python guitar_builder.py --generate`
- **Combined Import & Generate**: `python guitar_builder.py --config sarcaster --generate`

---

## 4. OpenSCAD STL Compilation (`scripts/compile_scad.py`)

If you edit the `.scad` files in the `models/` folder, you can regenerate their corresponding `.stl` files by running:
```bash
python scripts/compile_scad.py
```
- **Utility Exclusions**: Any `.scad` file starting with an underscore (such as `_rounded_poly.scad`) is treated as a utility script and is skipped during compilation.
- **Custom Path**: If the script cannot automatically locate `openscad.exe`, you can define its path using the `OPENSCAD_PATH` environment variable.

---

## 5. Custom Profiles

Configuration JSON files (saved inside the `config/` directory) contain human-readable keys corresponding to Blender's Geometry Nodes parameters. Example structure (`config/sarcaster.json`):

```json
{
    "Offset Scale": 4.0,
    "Hip Width": 32.0,
    "Waist Width": 22.8,
    "Chest Width": 27.6,
    "Shoulder Width": 25.0,
    "Neck Height": 40.0,
    "Neck Width": 7.4
}
```

Updating these parameters and running the configuration tool enables repeatable, parameterized setups for different guitar body shapes.

---

## 6. Rendering Pipeline (`scripts/render_guitar.py`)

Headless, background rendering generates photorealistic images of your configured guitars from multiple camera angles without launching the Blender GUI. It operates on previously generated STL/OBJ files.

To render the generated models for a configuration:

```bash
# Render all views (front, back, angled) for the 'sarcaster' cut profile
python guitar_builder.py sarcaster --render

# Render uncut, body-only meshes with Cycles renderer
python guitar_builder.py sarcaster --render --uncut --body-only --engine cycles

# Render with dramatic neon-tinted lighting and a striped multi-color body
python guitar_builder.py sarcaster --render --lighting dramatic --material striped

# Render with warm lighting and a blue sparkle body
python guitar_builder.py sarcaster --render --lighting warm --material sparkle:blue:silver
```

### Options:
- `--render`: Triggers the background rendering pipeline.
- `--uncut`: Force-renders the uncut full body mesh (`Guitar_Full_Body.stl`) instead of the sliced parts.
- `--body-only`: Renders only the guitar body (excludes neck and backplates).
- `--angle <front|back|angled|all>` (default: `all`): Camera angle view.
- `--engine <eevee|cycles>` (default: `eevee`): Blender render engine.
- `--material <preset>` (default: `gloss`): Gloss paint (`gloss`), colored gloss (`gloss:blue`, `gloss:#ff0000`), Gold Top (`gold`), Glossy Black (`black`), Chrome (`chrome`), Refractive Glass (`glass`), Radial Sunburst (`sunburst`), alternates (`striped`), random (`random`), custom list, sparkles, or colored glass:
  - `sparkle:<base_color>:<flake_color>` (e.g. `sparkle:blue:silver`).
  - `glass:<color>` (e.g. `glass:blue`, `glass:red`, `glass:#00ff00`).
- `--lighting <theme>` (default: `studio`): Studio lighting (`studio`), dramatic cyan/magenta (`dramatic`), amber/vintage (`warm`), orange/violet gradient (`sunset`).

Renders are saved in `output/<config_name>/renders/` (e.g., `front.png`, `back.png`, `angled.png`).
