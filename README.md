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
- Ensure `blender` is in your system's PATH. If not, the Windows runner (`guitar_builder.bat`) will attempt to automatically locate it in standard paths (like `C:\Program Files\Blender Foundation\`).

---

## Usage (`guitar_builder`)

All setup, custom configuration profiling, and generation tasks can be performed using the unified `guitar_builder` script.

### 1. Slicing & Scene Setup (Full Pipeline)
To build the guitar model and run the complete scene setup (applying cuts and exporting the output parts):

#### On Windows:
```cmd
:: Run with default parameters
guitar_builder.bat

:: Run with a custom profile (e.g., config/sarcaster.json)
guitar_builder.bat sarcaster

:: Export full body model without cutting it
guitar_builder.bat --no-cut

:: Combined: Run custom profile and export full body without cuts
guitar_builder.bat sarcaster --no-cut
```

#### On macOS / Linux:
```bash
# Make the script executable first
chmod +x guitar_builder.sh

# Run with default parameters
./guitar_builder.sh

# Run with custom profile
./guitar_builder.sh sarcaster

# Run without cutting
./guitar_builder.sh --no-cut

# Combined
./guitar_builder.sh sarcaster --no-cut
```

### 2. Exporting Model Configuration
Extract the current parameters of the Blender model to a JSON file (stored under the `config/` directory by default):
```bash
# Export default parameters to config/guitar_config.json
./guitar_builder.sh --export-config

# Export parameters under a specific profile name (e.g. config/sarcaster.json)
./guitar_builder.sh sarcaster --export-config

# Export parameters to a custom file name
./guitar_builder.sh --export-config custom.json
```

---

## 3. Under the Hood: Configurator Script (`configure_guitar.py`)

If you want to bypass the main setup runners, you can execute `configure_guitar.py` directly to configure and build the base guitar mesh without doing any scene setup or cutting:

- **Export Config**: `python configure_guitar.py --export-config sarcaster.json`
- **Import Config**: `python configure_guitar.py --import-config sarcaster.json`
- **Generate Mesh**: `python configure_guitar.py --generate`
- **Combined Import & Generate**: `python configure_guitar.py --config sarcaster --generate`

---

## 4. OpenSCAD STL Compilation (`compile_scad.py`)

If you edit the `.scad` files in the `models/` folder, you can regenerate their corresponding `.stl` files by running:
```bash
python compile_scad.py
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
