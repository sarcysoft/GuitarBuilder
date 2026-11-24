import os
import json
import shutil
from datetime import datetime

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
        if os.path.isabs(name_or_path) or os.path.sep in name_or_path:
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
