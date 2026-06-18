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
