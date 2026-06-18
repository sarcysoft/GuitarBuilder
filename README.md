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
- Ensure `blender` is in your system's PATH. If not, the Windows runner (`run_setup.bat`) will attempt to automatically locate it in standard paths (like `C:\Program Files\Blender Foundation\`).

---

## 1. Full Pipeline Execution (`run_setup`)

To run the complete setup pipeline (which processes the parameters, loads the models, performs boolean operations, cuts the guitar body, and exports the final parts):

### On Windows
```cmd
:: Run with default parameters and perform body cuts
run_setup.bat

:: Run with a custom profile (e.g., config/sarcaster.json)
run_setup.bat sarcaster

:: Export full body model without cutting it
run_setup.bat --no-cut

:: Combined: Run custom profile and export full body without cuts
run_setup.bat sarcaster --no-cut
```

### On macOS / Linux
```bash
# Make the script executable first
chmod +x run_setup.sh

# Run with default parameters
./run_setup.sh

# Run with custom profile
./run_setup.sh sarcaster

# Run without cutting
./run_setup.sh --no-cut

# Combined
./run_setup.sh sarcaster --no-cut
```

---

## 2. Command-Line Guitar Model Configurator (`configure_guitar.py`)

If you want to configure parameters or regenerate only the base guitar mesh without running the cutting and scene setup operations, you can run the utility script `configure_guitar.py`.

It runs directly from your system shell and launches Blender in background mode.

### Exporting parameters from Blender
Extract the current parameters of the Blender model to a JSON file (by default saved under the `config/` directory):
```bash
python configure_guitar.py --export-config sarcaster.json
```

### Importing parameters to Blender
Write parameters from a JSON configuration profile directly into the Blender file:
```bash
python configure_guitar.py --import-config sarcaster.json
```

### Generating the mesh only
Regenerate and export the custom guitar body geometry to `models/guitar.obj`:
```bash
python configure_guitar.py --generate
```

### Combined Profile import and generation
Import a config profile, save it to the `.blend` file, and export the custom mesh (e.g. `models/sarcaster.obj`) in a single step:
```bash
python configure_guitar.py --config sarcaster --generate
```

---

## 3. Custom Profiles

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
