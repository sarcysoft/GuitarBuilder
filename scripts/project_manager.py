import os
import json
import shutil
import hashlib
from datetime import datetime

SLICED_BODY_PARTS = [
    "Guitar_Bot_Left.stl", "Guitar_Bot_Right.stl", "Guitar_Top_Left.stl", "Guitar_Mid_Left.stl",
    "Guitar_Top_Right.stl", "Guitar_Mid_Right.stl", "Guitar_Top_Mid.stl", "Guitar_Mid.stl"
]

class ProjectManager:
    """Manages guitar builder projects, their configurations, directory structures, and assets."""

    def __init__(self, repo_dir=None):
        if repo_dir is None:
            self.repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.repo_dir = os.path.abspath(repo_dir)

        self.projects_dir = os.path.join(self.repo_dir, "projects")
        self.config_dir = os.path.join(self.repo_dir, "config")
        
        # Ensure projects root exists
        if not os.path.exists(self.projects_dir):
            try:
                os.makedirs(self.projects_dir, exist_ok=True)
            except Exception:
                pass

    def get_body_models(self):
        """Scans config/*.json to get list of available body models."""
        models = []
        if os.path.exists(self.config_dir):
            for fname in sorted(os.listdir(self.config_dir)):
                if fname.endswith(".json") and not fname.startswith("exported_"):
                    models.append(os.path.splitext(fname)[0])
        if not models:
            models = ["sarcaster", "les_paul", "flying_v", "sg", "jazzmaster"]
        return models

    def get_default_body_dimensions(self, body_model="sarcaster"):
        """Loads default geometric node dimensions for a given body model from config/<body_model>.json."""
        config_path = os.path.join(self.config_dir, f"{body_model}.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed reading {config_path}: {e}")
        return {}

    def list_projects(self):
        """Returns a list of project folder names in the projects directory."""
        if not os.path.exists(self.projects_dir):
            return []
        projects = []
        for d in sorted(os.listdir(self.projects_dir)):
            full_path = os.path.join(self.projects_dir, d)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "project.json")):
                projects.append(d)
        return projects

    def resolve_project_dir(self, name_or_path):
        """Returns the absolute path to a project directory."""
        if os.path.isabs(name_or_path) or "/" in name_or_path or "\\" in name_or_path or os.path.exists(name_or_path):
            p = os.path.abspath(name_or_path)
            if os.path.isfile(p):
                return os.path.dirname(p)
            return p
        return os.path.join(self.projects_dir, name_or_path)

    def create_project(self, name, body_model="sarcaster"):
        """Creates a new project directory and writes default project.json."""
        # Sanitize folder name
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name.strip())
        if not safe_name:
            safe_name = "Untitled_Guitar"

        proj_dir = os.path.join(self.projects_dir, safe_name)
        renders_dir = os.path.join(proj_dir, "renders")
        stl_dir = os.path.join(proj_dir, "stl")

        os.makedirs(renders_dir, exist_ok=True)
        os.makedirs(os.path.join(stl_dir, "body"), exist_ok=True)
        os.makedirs(os.path.join(stl_dir, "neck"), exist_ok=True)
        os.makedirs(os.path.join(stl_dir, "hardware"), exist_ok=True)
        os.makedirs(os.path.join(stl_dir, "pins"), exist_ok=True)

        dims = self.get_default_body_dimensions(body_model)
        default_neck = "strat" if ("strat" in body_model or "sarcaster" in body_model) else "les_paul"

        proj_data = {
            "name": name,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "body_model": body_model,
            "body_dimensions": dims,
            "neck": {
                "style": default_neck,
                "shaft_material": "maple",
                "fretboard_material": "rosewood",
                "tuner_finish": "chrome"
            },
            "hardware": {
                "variant": "standard",
                "electronics": body_model if body_model in ["sarcaster", "les_paul", "flying_v"] else "auto"
            },
            "slicing": {
                "cut_type": "textured",
                "pin_diameter": 6.0,
                "pin_length": 16.0,
                "no_pins": False,
                "no_cut": False
            },
            "visuals": {
                "body_material": "sunburst",
                "backplate_material": "gloss:black",
                "lighting": "studio",
                "engine": "eevee",
                "angle": "angled",
                "animate": False,
                "dynamic_zoom": True,
                "seed": None
            }
        }

        # Fix Python booleans to lowercase in JSON via standard dump
        proj_json_path = os.path.join(proj_dir, "project.json")
        with open(proj_json_path, "w", encoding="utf-8") as f:
            json.dump(proj_data, f, indent=4)

        return proj_dir, proj_data

    def load_project(self, name_or_path):
        """Loads project.json for a project."""
        proj_dir = self.resolve_project_dir(name_or_path)
        proj_json_path = os.path.join(proj_dir, "project.json")
        if not os.path.exists(proj_json_path):
            raise FileNotFoundError(f"Project configuration not found at {proj_json_path}")

        with open(proj_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure required sub-keys exist with sensible defaults
        if "body_dimensions" not in data or not data["body_dimensions"]:
            data["body_dimensions"] = self.get_default_body_dimensions(data.get("body_model", "sarcaster"))
        if "neck" not in data:
            data["neck"] = {"style": "auto", "shaft_material": "maple", "fretboard_material": "rosewood", "tuner_finish": "chrome"}
        if "hardware" not in data:
            data["hardware"] = {"variant": "standard", "electronics": "auto"}
        if "slicing" not in data:
            data["slicing"] = {"cut_type": "textured", "pin_diameter": 6.0, "pin_length": 16.0, "no_pins": False, "no_cut": False}
        if "visuals" not in data:
            data["visuals"] = {"body_material": "sunburst", "backplate_material": "gloss:black", "lighting": "studio", "engine": "eevee", "angle": "angled", "animate": False, "dynamic_zoom": True, "seed": None}

        return data

    def save_project(self, name_or_path, project_data):
        """Saves project_data to project.json in the project folder."""
        proj_dir = self.resolve_project_dir(name_or_path)
        os.makedirs(proj_dir, exist_ok=True)
        os.makedirs(os.path.join(proj_dir, "renders"), exist_ok=True)
        os.makedirs(os.path.join(proj_dir, "stl"), exist_ok=True)

        project_data["updated_at"] = datetime.now().isoformat()
        proj_json_path = os.path.join(proj_dir, "project.json")

        with open(proj_json_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)

        return proj_json_path

    def duplicate_project(self, src_name_or_path, new_name):
        """Clones an existing project into a new project directory."""
        src_dir = self.resolve_project_dir(src_name_or_path)
        data = self.load_project(src_dir)

        data["name"] = new_name
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()

        safe_new_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in new_name.strip())
        new_proj_dir = os.path.join(self.projects_dir, safe_new_name)
        os.makedirs(new_proj_dir, exist_ok=True)

        self.save_project(new_proj_dir, data)
        return new_proj_dir, data

    def compute_slice_signature(self, project_data, cut_type=None, no_pins=None):
        """Computes a deterministic hash of parameters that affect physical sliced body geometry.
        Changes to materials, colors, neck wood, tuner finish, lighting, camera angle, and engine
        DO NOT alter this signature.
        """
        body_model = project_data.get("body_model", "sarcaster")
        body_dims = project_data.get("body_dimensions", {})
        hardware = project_data.get("hardware", {})
        slicing = project_data.get("slicing", {})

        actual_cut_type = str(cut_type if cut_type is not None else slicing.get("cut_type", "textured")).strip().lower()
        actual_no_pins = bool(no_pins if no_pins is not None else slicing.get("no_pins", False))

        relevant_spec = {
            "body_model": str(body_model).strip().lower(),
            "body_dimensions": {str(k): round(float(v), 4) if isinstance(v, (int, float)) else str(v) for k, v in sorted(body_dims.items())},
            "hardware_variant": str(hardware.get("variant", "standard")).strip().lower(),
            "electronics": str(hardware.get("electronics", "auto")).strip().lower(),
            "cut_type": actual_cut_type,
            "no_pins": actual_no_pins,
            "pin_diameter": round(float(slicing.get("pin_diameter", 6.0)), 2),
            "pin_length": round(float(slicing.get("pin_length", 16.0)), 2),
            "no_cut": bool(slicing.get("no_cut", False))
        }
        spec_json = json.dumps(relevant_spec, sort_keys=True)
        return hashlib.sha256(spec_json.encode("utf-8")).hexdigest()[:16]

    def get_slice_status(self, name_or_path, project_data=None, for_preview=False):
        """Checks whether sliced body parts exist and match current geometry settings.
        If for_preview=True:
            - If existing slices match current geometry and are either textured or flat, returns 'clean'.
              (Unless a textured cut has already been generated, then use that for the preview).
        If for_preview=False (production):
            - Slices must match the project's configured cut_type.
        """
        proj_dir = self.resolve_project_dir(name_or_path)
        if project_data is None:
            try:
                project_data = self.load_project(proj_dir)
            except Exception:
                return "missing"

        stl_dir = os.path.join(proj_dir, "stl")
        body_stl_dir = os.path.join(stl_dir, "body")

        for part in SLICED_BODY_PARTS:
            if not os.path.exists(os.path.join(stl_dir, part)) and not os.path.exists(os.path.join(body_stl_dir, part)):
                return "missing"

        # Check saved signature
        saved_sig = None
        sig_file = os.path.join(stl_dir, ".slice_signature")
        if os.path.exists(sig_file):
            try:
                with open(sig_file, "r", encoding="utf-8") as f:
                    saved_sig = f.read().strip()
            except Exception:
                pass

        if not saved_sig:
            saved_sig = project_data.get("slicing", {}).get("last_slice_signature")

        if not saved_sig:
            return "dirty"

        # Direct match with current project configuration
        current_sig = self.compute_slice_signature(project_data)
        if saved_sig == current_sig:
            return "clean"

        # For preview: textured cuts previously generated for this geometry should be reused directly!
        if for_preview:
            # Check if saved signature matches flat cuts
            flat_sig = self.compute_slice_signature(project_data, cut_type="flat", no_pins=True)
            if saved_sig == flat_sig:
                return "clean"
            # Or if textured cut was already generated for this geometry:
            textured_sig = self.compute_slice_signature(project_data, cut_type="textured", no_pins=project_data.get("slicing", {}).get("no_pins", False))
            if saved_sig == textured_sig:
                return "clean"

        return "dirty"

    def update_slice_signature(self, name_or_path, project_data=None, cut_type=None, no_pins=None):
        """Records current geometry signature to mark slices as up-to-date ('clean')."""
        proj_dir = self.resolve_project_dir(name_or_path)
        if project_data is None:
            project_data = self.load_project(proj_dir)

        sig = self.compute_slice_signature(project_data, cut_type=cut_type, no_pins=no_pins)
        actual_cut_type = cut_type if cut_type is not None else project_data.get("slicing", {}).get("cut_type", "textured")

        if "slicing" not in project_data:
            project_data["slicing"] = {}
        project_data["slicing"]["last_slice_signature"] = sig
        project_data["slicing"]["last_cut_type"] = actual_cut_type

        # Save to project.json
        proj_json_path = os.path.join(proj_dir, "project.json")
        try:
            with open(proj_json_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save signature to project.json: {e}")

        # Save to stl/.slice_signature
        stl_dir = os.path.join(proj_dir, "stl")
        os.makedirs(stl_dir, exist_ok=True)
        try:
            with open(os.path.join(stl_dir, ".slice_signature"), "w", encoding="utf-8") as f:
                f.write(sig)
        except Exception:
            pass
        return sig
        os.makedirs(stl_dir, exist_ok=True)
        try:
            with open(os.path.join(stl_dir, ".slice_signature"), "w", encoding="utf-8") as f:
                f.write(sig)
        except Exception:
            pass
        return sig
