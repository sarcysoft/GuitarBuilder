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

## Graphical User Interface (`gui.py`)

A graphical desktop frontend is provided to configure profiles, slice models, and render scenes without memorizing command-line flags.

To launch the GUI:
```bash
python gui.py
# or
python guitar_builder.py --gui
```

### GUI Features:
- **Profile Selector & Parameter Editor:** Select any body profile (`sarcaster`, `flying_v`, `les_paul`, etc.) from a dropdown, live-edit Geometry Nodes values in a table, and save new profiles.
- **Slicing & Manufacturing Controls:** One-click toggle between **Flat Cuts** (vertical printing + 6mm locator pin holes) and **Textured Cuts** (legacy horizontal printing), with live pin diameter and length spinboxes.
- **Photo Studio & Rendering:** Configure camera views, lighting themes (`studio`, `dramatic`, `warm`, `sunset`), materials (`gloss`, `sunburst`, `sparkle`, `chrome`, `glass`), exploded views, and render engines (`eevee`/`cycles`).
- **Render Gallery:** Built-in thumbnail viewer for previewing generated `front.png`, `back.png`, and `angled.png` renders without leaving the app.
- **Realtime Console & Command Preview:** Live subprocess terminal log streaming with cancel support, and a live CLI preview showing the exact command being generated.

---

## Usage (`guitar_builder.py`)

All setup, custom configuration profiling, and generation tasks can also be performed via the CLI using `guitar_builder.py`.

### 1. Slicing & Scene Setup (Full Pipeline)
To build the guitar model and run the complete scene setup (applying cuts, creating alignment locator pin holes, and exporting the output parts):

```bash
# Run with default parameters (Flat cuts with 6mm locator pin holes for vertical 3D printing)
python guitar_builder.py

# Run with a custom profile (e.g., config/sarcaster.json)
python guitar_builder.py sarcaster

# Select a specific hardware variant (e.g. piezo bridge - omits backplate)
python guitar_builder.py sarcaster --hardware piezo

# Select specific hardware and electronics variants
python guitar_builder.py sarcaster --hardware standard --electronics sarcaster

# Custom pin dimensions (e.g. 5mm diameter, 20mm length)
python guitar_builder.py sarcaster --pin-diameter 5.0 --pin-length 20.0

# Flat cuts without any pin holes
python guitar_builder.py sarcaster --no-pins

# Legacy horizontal-printing textured puzzle joints (displaced wavy cuts)
python guitar_builder.py sarcaster --cut-type textured

# Export full body model without cutting it
python guitar_builder.py --no-cut

# Combined: Run custom profile and export full body without cuts
python guitar_builder.py sarcaster --no-cut
```

#### Cutting & Alignment Methods:
- **`--cut-type flat` (Default):** Produces perfectly flat cut lines designed for **vertical 3D printing**. Sections can sit flat directly on the print bed with zero supports on the joint face, maximizing bed adhesion and layer strength under string tension.
  - Generates coaxial blind holes across all mating seams for **locator dowel pins** (default: 6mm diameter $\times$ 16mm length with 0.4mm diametral clearance for epoxy relief).
  - Also automatically exports `locator_pin.stl` with chamfered lead-in ends into the output directory for easy printing.
- **`--cut-type textured`:** Legacy procedural noise-displaced interlocking cuts intended for horizontal print orientations.
- **`--pin-diameter <float>`:** Nominal locator pin diameter in mm (default: `6.0`).
- **`--pin-length <float>`:** Total pin length in mm (default: `16.0`, 8mm depth per side).
- **`--no-pins`:** Disables pin hole subtraction and pin export on flat cuts.

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

## 4. OpenSCAD STL Compilation & Variant Packages (`scripts/compile_scad.py`)

Hardware and electronics are organized into modular variant packages under `models/scad/`:

```
models/scad/
  common/                       # Shared utility modules (_fret_calc.scad, _rounded_poly.scad, etc.)
  hardware/
    standard/                   # Standard tremolo + single-coil pickups
      hardware.scad
      backplate.scad            # Tremolo spring cavity cover
      backplate_mask.scad
      backplate_fixings.scad
    piezo/                      # Piezo bridge (omits backplate.scad to skip backplate)
      hardware.scad
  electronics/
    sarcaster/                  # Standard 5-way blade + pots
      electronics.scad
      elec_backplate.scad
      elec_backplate_mask.scad
      elec_backplate_fixings.scad
    flying_v/
    les_paul/
  neck/
    strat/                      # 25.5" scale, 22 frets, flat stepped 6-in-line headstock
      neck.scad
    les_paul/                   # 24.75" scale, 22 frets, 14° tilted 3x3 open-book headstock
      neck.scad
```

- **Omitting Backplates:** If a hardware or electronics variant does not require a rear cover plate (e.g. `piezo`), simply omit `backplate.scad` from its folder. The compiler and scene setup will cleanly skip all backplate subtractions and covers.
- **Compiling Variants:** To compile all variants into `models/stl/`:
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

# Render exploded body-only views with random materials
python guitar_builder.py sarcaster --render --exploded-body --material random

# Render with dramatic neon-tinted lighting and a striped multi-color body
python guitar_builder.py sarcaster --render --lighting dramatic --material striped

# Render with warm lighting and a blue sparkle body
python guitar_builder.py sarcaster --render --lighting warm --material sparkle:blue:silver
```

### Options:
- `--render`: Triggers the background rendering pipeline.
- `--uncut`: Force-renders the uncut full body mesh (`Guitar_Full_Body.stl`) instead of the sliced parts.
- `--body-only`: Renders only the guitar body (excludes neck and backplates).
- `--exploded-body`: Renders only the guitar body in exploded view, separating the sliced parts in the X and Y axes.
- `--save-blend`: Optionally saves the completed Blender scene as a `.blend` file inside the renders directory.
- `--angle <front|back|angled|all>` (default: `all`): Camera angle view.
- `--engine <eevee|cycles>` (default: `eevee`): Blender render engine.
- `--material <preset>` (default: `gloss`): Material preset for the main body components. Supported values include: gloss paint (`gloss`), Gold Top (`gold`), Chrome (`chrome`), Refractive Glass (`glass`), Radial Sunburst (`sunburst`), alternates (`striped`), random (`random`), custom list, sparkles, or colored glass:
  - `gloss:<color>` (e.g. `gloss:blue`, `gloss:black`, `gloss:#ff0000`).
  - `chrome:<color>` (e.g. `chrome:gold`, `chrome:blue`).
  - `sunburst:<center_color>:<mid_color>:<outer_color>` (e.g. `sunburst:yellow:red:black`, `sunburst:gold:orange:purple`).
  - `sparkle:<base_color>:<flake_color>` (e.g. `sparkle:blue:silver`).
  - `glass:<color>` (e.g. `glass:blue`, `glass:red`, `glass:#00ff00`).
- `--material_back <preset>` (default: `gloss:black`): Material preset for the backplate components (accepts the same formats as `--material`).
- `--lighting <theme>` (default: `studio`): Studio lighting (`studio`), dramatic cyan/magenta (`dramatic`), amber/vintage (`warm`), orange/violet gradient (`sunset`).
- `--neck <auto|strat|les_paul>` (default: `auto`): Modular OpenSCAD guitar neck model to import and display.
- `--neck-material <maple|rosewood|ebony>` (default: `maple`): Wood material shader for the main neck shaft.
- `--fretboard-material <rosewood|maple|ebony>` (default: `rosewood`): Wood material shader for the fretboard.
- `--tuner-finish <chrome|gold|black>` (default: `chrome`): Hardware finish for the tuning pegs.

Renders are saved in `output/<config_name>/renders/` (e.g., `front.png`, `back.png`, `angled.png`).
