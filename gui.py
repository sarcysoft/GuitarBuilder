"""
GuitarBuilder Studio - Python GUI Frontend
A modern, intuitive graphical interface for configuring, slicing, and rendering
parametric guitar bodies in Blender.
"""

import os
import sys
import json
import subprocess
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Try enabling DPI awareness on Windows for crisp high-res rendering
if sys.platform == "win32":
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class GuitarBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GuitarBuilder Studio")
        self.root.geometry("1020x820")
        self.root.minsize(860, 680)

        # Base directories
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(self.repo_dir, "config")
        self.output_dir = os.path.join(self.repo_dir, "output")
        self.scripts_dir = os.path.join(self.repo_dir, "scripts")

        # Process management
        self.current_process = None
        self.log_queue = queue.Queue()
        self.is_running = False

        # Find blender executable
        self.blender_exe = self._locate_blender()

        # UI Variables
        self._init_variables()

        # Build UI layout
        self._setup_styles()
        self._build_ui()

        # Start periodic log pump
        self.root.after(100, self._process_log_queue)

        # Initial config scan and command preview update
        self._refresh_config_list()
        self._update_command_preview()

    def _locate_blender(self):
        """Find Blender executable using guitar_builder logic."""
        try:
            import guitar_builder
            return guitar_builder.find_blender()
        except Exception:
            # Fallback search
            if sys.platform == "win32":
                pf = os.environ.get("ProgramFiles", "C:\\Program Files")
                bf = os.path.join(pf, "Blender Foundation")
                if os.path.exists(bf):
                    subdirs = [os.path.join(bf, d) for d in os.listdir(bf) if d.startswith("Blender")]
                    subdirs.sort(reverse=True)
                    for sd in subdirs:
                        exe = os.path.join(sd, "blender.exe")
                        if os.path.exists(exe):
                            return exe
            return None

    def _init_variables(self):
        """Initialize all reactive Tkinter variables."""
        # Config profile
        self.var_config = tk.StringVar(value="sarcaster")

        # Slicing & Manufacturing
        self.var_cut_type = tk.StringVar(value="flat")
        self.var_enable_pins = tk.BooleanVar(value=True)
        self.var_pin_diameter = tk.DoubleVar(value=6.0)
        self.var_pin_length = tk.DoubleVar(value=16.0)
        self.var_no_cut = tk.BooleanVar(value=False)
        self.var_hardware = tk.StringVar(value="standard")
        self.var_electronics = tk.StringVar(value="auto")

        # Rendering & Materials
        self.var_render_pipeline = tk.BooleanVar(value=False)
        self.var_render_uncut = tk.BooleanVar(value=False)
        self.var_body_only = tk.BooleanVar(value=False)
        self.var_exploded_body = tk.BooleanVar(value=False)
        self.var_angle = tk.StringVar(value="all")
        self.var_engine = tk.StringVar(value="eevee")
        self.var_material = tk.StringVar(value="gloss")
        self.var_material_back = tk.StringVar(value="gloss:black")
        self.var_lighting = tk.StringVar(value="studio")
        self.var_pitch = tk.StringVar(value="")
        self.var_guitar_rot = tk.StringVar(value="")
        self.var_dynamic_zoom = tk.BooleanVar(value=False)
        self.var_animate = tk.BooleanVar(value=False)
        self.var_save_blend = tk.BooleanVar(value=False)
        self.var_seed = tk.StringVar(value="")

        # Realtime command preview
        self.var_cmd_preview = tk.StringVar()

    def _setup_styles(self):
        """Setup custom TTK styles for a clean, modern look."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # General colors
        self.bg_color = "#f5f6f8"
        self.accent_color = "#2563eb"  # Royal blue
        self.success_color = "#16a34a" # Forest green
        self.dark_bg = "#1e293b"

        self.root.configure(bg=self.bg_color)
        self.style.configure(".", background=self.bg_color, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color)
        self.style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#0f172a")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#64748b")
        self.style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        self.style.configure("CardHeader.TLabel", background="#ffffff", font=("Segoe UI", 11, "bold"), foreground="#1e293b")
        self.style.configure("CardDesc.TLabel", background="#ffffff", font=("Segoe UI", 9), foreground="#64748b")

        # Custom Buttons
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#2563eb")
        self.style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("disabled", "#94a3b8")])

        self.style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#16a34a")
        self.style.map("Success.TButton", background=[("active", "#15803d"), ("disabled", "#94a3b8")])

        self.style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), foreground="#ffffff", background="#dc2626")
        self.style.map("Danger.TButton", background=[("active", "#b91c1c")])

        # Notebook tabs
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 6])
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff"), ("active", "#e2e8f0")])

    def _build_ui(self):
        """Construct the main GUI window layout."""
        # Top Header Bar
        header_frame = ttk.Frame(self.root, padding=(16, 12, 16, 8))
        header_frame.pack(fill="x")

        # Title + status
        title_box = ttk.Frame(header_frame)
        title_box.pack(side="left", fill="y")
        
        lbl_title = ttk.Label(title_box, text="🎸 GuitarBuilder Studio", font=("Segoe UI", 16, "bold"), foreground="#0f172a")
        lbl_title.pack(anchor="w")
        
        blender_text = f"Blender: {os.path.basename(os.path.dirname(self.blender_exe))}" if self.blender_exe else "Blender: NOT FOUND"
        blender_color = "#16a34a" if self.blender_exe else "#dc2626"
        lbl_blender = tk.Label(title_box, text=f"● {blender_text}", font=("Segoe UI", 9, "bold"), fg=blender_color, bg=self.bg_color)
        lbl_blender.pack(anchor="w", pady=(2, 0))

        # Profile selection box in header
        profile_box = ttk.Frame(header_frame)
        profile_box.pack(side="right", fill="y")

        ttk.Label(profile_box, text="Active Profile:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))
        self.combo_config = ttk.Combobox(profile_box, textvariable=self.var_config, width=22, state="readonly")
        self.combo_config.pack(side="left", padx=(0, 6))
        self.combo_config.bind("<<ComboboxSelected>>", self._on_config_selected)

        btn_refresh = ttk.Button(profile_box, text="↻ Refresh", width=9, command=self._refresh_config_list)
        btn_refresh.pack(side="left", padx=(0, 4))

        btn_open_configs = ttk.Button(profile_box, text="📁 Configs", width=9, command=lambda: self._open_folder(self.config_dir))
        btn_open_configs.pack(side="left")

        # Separator line
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=16, pady=4)

        # Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(4, 8))

        # Build individual tabs
        self.tab_slicing = ttk.Frame(self.notebook, padding=12)
        self.tab_rendering = ttk.Frame(self.notebook, padding=12)
        self.tab_config_editor = ttk.Frame(self.notebook, padding=12)
        self.tab_gallery = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_slicing, text="  ✂ Slicing & Manufacturing  ")
        self.notebook.add(self.tab_rendering, text="  🎨 Photo Studio (Render)  ")
        self.notebook.add(self.tab_config_editor, text="  ⚙ Parameters Editor  ")
        self.notebook.add(self.tab_gallery, text="  🖼 Render Gallery  ")

        self._build_tab_slicing()
        self._build_tab_rendering()
        self._build_tab_config_editor()
        self._build_tab_gallery()

        # Command Preview Bar
        preview_frame = ttk.Frame(self.root, padding=(16, 2, 16, 4))
        preview_frame.pack(fill="x")
        ttk.Label(preview_frame, text="Command Preview:", font=("Segoe UI", 9, "bold"), foreground="#475569").pack(side="left", padx=(0, 6))
        ent_preview = ttk.Entry(preview_frame, textvariable=self.var_cmd_preview, state="readonly", font=("Consolas", 9))
        ent_preview.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(preview_frame, text="Copy CLI", width=9, command=self._copy_command_preview).pack(side="left")

        # Bottom Area: Live Console
        self._build_console_area()

    # =========================================================================
    # TAB 1: Slicing & Manufacturing
    # =========================================================================
    def _build_tab_slicing(self):
        container = ttk.Frame(self.tab_slicing)
        container.pack(fill="both", expand=True)

        # Left Column: Cutting Strategy & Locator Pins
        left_col = ttk.Frame(container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Card 1: Cutting Strategy
        card_cut = ttk.LabelFrame(left_col, text=" Cutting Mechanism (Printing Orientation) ", padding=12)
        card_cut.pack(fill="x", pady=(0, 10))

        rb_flat = ttk.Radiobutton(
            card_cut, 
            text="Flat Cuts (Vertical 3D Printing - Default & Recommended)", 
            value="flat", 
            variable=self.var_cut_type,
            command=self._on_cut_type_changed
        )
        rb_flat.pack(anchor="w", pady=(0, 2))
        lbl_flat_desc = ttk.Label(
            card_cut, 
            text="  • Cut surfaces are perfectly flat to sit directly on the print bed with no supports.\n"
                 "  • Maximizes layer adhesion and tensile strength under string tension.\n"
                 "  • Uses 6mm coaxial locator pins to align sections during epoxy glue-up.",
            font=("Segoe UI", 8),
            foreground="#475569"
        )
        lbl_flat_desc.pack(anchor="w", padx=(20, 0), pady=(0, 8))

        rb_tex = ttk.Radiobutton(
            card_cut, 
            text="Textured Cuts (Horizontal 3D Printing - Legacy)", 
            value="textured", 
            variable=self.var_cut_type,
            command=self._on_cut_type_changed
        )
        rb_tex.pack(anchor="w", pady=(4, 2))
        lbl_tex_desc = ttk.Label(
            card_cut, 
            text="  • Procedural noise-displaced interlocking puzzle joints for horizontal prints.\n"
                 "  • Mating faces are textured and cannot be placed flat on the print bed.",
            font=("Segoe UI", 8),
            foreground="#475569"
        )
        lbl_tex_desc.pack(anchor="w", padx=(20, 0))

        # Card 2: Locator Pin Parameters
        self.card_pins = ttk.LabelFrame(left_col, text=" Alignment Locator Pins ", padding=12)
        self.card_pins.pack(fill="x", pady=(0, 10))

        chk_pins = ttk.Checkbutton(
            self.card_pins, 
            text="Generate Locator Pin Holes across Seams", 
            variable=self.var_enable_pins,
            command=self._update_command_preview
        )
        chk_pins.pack(anchor="w", pady=(0, 8))

        params_grid = ttk.Frame(self.card_pins)
        params_grid.pack(fill="x", padx=16)

        ttk.Label(params_grid, text="Pin Diameter:").grid(row=0, column=0, sticky="w", pady=4)
        sp_diam = ttk.Spinbox(
            params_grid, 
            from_=3.0, 
            to=12.0, 
            increment=0.5, 
            textvariable=self.var_pin_diameter, 
            width=8,
            command=self._update_command_preview
        )
        sp_diam.grid(row=0, column=1, sticky="w", padx=(6, 4), pady=4)
        ttk.Label(params_grid, text="mm (Default: 6.0 mm)").grid(row=0, column=2, sticky="w", pady=4)

        ttk.Label(params_grid, text="Pin Length:").grid(row=1, column=0, sticky="w", pady=4)
        sp_len = ttk.Spinbox(
            params_grid, 
            from_=8.0, 
            to=35.0, 
            increment=1.0, 
            textvariable=self.var_pin_length, 
            width=8,
            command=self._update_command_preview
        )
        sp_len.grid(row=1, column=1, sticky="w", padx=(6, 4), pady=4)
        ttk.Label(params_grid, text="mm (Default: 16.0 mm, 8mm per side)").grid(row=1, column=2, sticky="w", pady=4)

        lbl_clearance = ttk.Label(
            self.card_pins,
            text="ℹ Holes are subtracted with +0.4mm diametral clearance and +1mm depth relief\n"
                 "   to allow epoxy flow and ensure joint faces sit completely flush.\n"
                 "ℹ Automatically generates and exports matching 'locator_pin.stl'.",
            font=("Segoe UI", 8),
            foreground="#2563eb"
        )
        lbl_clearance.pack(anchor="w", padx=4, pady=(8, 0))

        # Right Column: Execution & Export Options
        right_col = ttk.Frame(container)
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0))

        # Card: Hardware & Electronics Variants
        card_variants = ttk.LabelFrame(right_col, text=" Hardware & Electronics Setup ", padding=12)
        card_variants.pack(fill="x", pady=(0, 10))

        v_grid = ttk.Frame(card_variants)
        v_grid.pack(fill="x")

        ttk.Label(v_grid, text="Hardware:").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_hardware = ttk.Combobox(v_grid, textvariable=self.var_hardware, width=16, state="readonly")
        self.combo_hardware.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        self.combo_hardware.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(v_grid, text="Electronics:").grid(row=1, column=0, sticky="w", pady=4)
        self.combo_electronics = ttk.Combobox(v_grid, textvariable=self.var_electronics, width=16, state="readonly")
        self.combo_electronics.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)
        self.combo_electronics.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        lbl_var_note = ttk.Label(
            card_variants,
            text="ℹ Hardware 'piezo' omits backplate (self-contained cavity).\n"
                 "ℹ Electronics 'auto' derives cavity layout from the active profile.",
            font=("Segoe UI", 8),
            foreground="#475569"
        )
        lbl_var_note.pack(anchor="w", pady=(6, 0))

        card_export = ttk.LabelFrame(right_col, text=" Slicing Scope & Export ", padding=12)
        card_export.pack(fill="x", pady=(0, 10))

        chk_nocut = ttk.Checkbutton(
            card_export, 
            text="Export Uncut Full Body Only (--no-cut)", 
            variable=self.var_no_cut,
            command=self._update_command_preview
        )
        chk_nocut.pack(anchor="w", pady=(0, 6))

        lbl_export_info = ttk.Label(
            card_export,
            text="When slicing is enabled, the model is split into 8 printable components:\n"
                 "  • Guitar_Bot_Left, Guitar_Bot_Right\n"
                 "  • Guitar_Mid_Left, Guitar_Mid, Guitar_Mid_Right\n"
                 "  • Guitar_Top_Left, Guitar_Top_Mid, Guitar_Top_Right\n"
                 "  • locator_pin.stl (printable registration pin)",
            font=("Segoe UI", 8),
            foreground="#475569"
        )
        lbl_export_info.pack(anchor="w", pady=(0, 8))

        # Action Buttons Box
        card_actions = ttk.LabelFrame(right_col, text=" Actions & Pipeline Execution ", padding=14)
        card_actions.pack(fill="x", pady=(0, 10))

        btn_build_slice = ttk.Button(
            card_actions, 
            text="▶  Build & Slice Guitar Body", 
            style="Success.TButton", 
            command=self._action_build_and_slice
        )
        btn_build_slice.pack(fill="x", pady=(0, 8), ipady=4)

        btn_mesh_only = ttk.Button(
            card_actions, 
            text="⚡  Generate Base Mesh Only (--generate)", 
            command=self._action_generate_mesh_only
        )
        btn_mesh_only.pack(fill="x", pady=(0, 8))

        btn_open_out = ttk.Button(
            card_actions, 
            text="📁  Open Output Folder", 
            command=self._open_current_output_dir
        )
        btn_open_out.pack(fill="x", pady=(0, 8))

        btn_scad = ttk.Button(
            card_actions, 
            text="🛠  Recompile OpenSCAD Hardware STLs", 
            command=self._action_compile_scad
        )
        btn_scad.pack(fill="x")

    def _on_cut_type_changed(self):
        """Update pin card availability when cut type switches."""
        is_flat = (self.var_cut_type.get() == "flat")
        state = "normal" if is_flat else "disabled"
        for child in self.card_pins.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass
        self._update_command_preview()

    # =========================================================================
    # TAB 2: Photo Studio (Rendering)
    # =========================================================================
    def _build_tab_rendering(self):
        container = ttk.Frame(self.tab_rendering)
        container.pack(fill="both", expand=True)

        left_col = ttk.Frame(container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Card 1: Assembly & Views
        card_views = ttk.LabelFrame(left_col, text=" Assembly & Camera Views ", padding=12)
        card_views.pack(fill="x", pady=(0, 10))

        chk_uncut_render = ttk.Checkbutton(
            card_views, 
            text="Render Uncut Body (Guitar_Full_Body.stl) (--uncut)", 
            variable=self.var_render_uncut,
            command=self._update_command_preview
        )
        chk_uncut_render.pack(anchor="w", pady=(0, 4))

        chk_body_only = ttk.Checkbutton(
            card_views, 
            text="Body Only (Exclude Neck & Backplates) (--body-only)", 
            variable=self.var_body_only,
            command=self._update_command_preview
        )
        chk_body_only.pack(anchor="w", pady=(0, 4))

        chk_explode = ttk.Checkbutton(
            card_views, 
            text="Exploded View (Spaced along X/Y seams) (--exploded-body)", 
            variable=self.var_exploded_body,
            command=self._update_command_preview
        )
        chk_explode.pack(anchor="w", pady=(0, 8))

        view_grid = ttk.Frame(card_views)
        view_grid.pack(fill="x", pady=(0, 4))

        ttk.Label(view_grid, text="Camera Angle:").grid(row=0, column=0, sticky="w", pady=4)
        combo_angle = ttk.Combobox(
            view_grid, 
            textvariable=self.var_angle, 
            values=["all", "front", "back", "angled"], 
            width=14, 
            state="readonly"
        )
        combo_angle.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_angle.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(view_grid, text="Dynamic Zoom:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Checkbutton(view_grid, text="Tight Framing", variable=self.var_dynamic_zoom, command=self._update_command_preview).grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)

        ttk.Label(view_grid, text="Custom Pitch (°):").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(view_grid, textvariable=self.var_pitch, width=15).grid(row=2, column=1, sticky="w", padx=(6, 0), pady=4)

        ttk.Label(view_grid, text="Guitar Rot (X,Y,Z):").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(view_grid, textvariable=self.var_guitar_rot, width=15).grid(row=3, column=1, sticky="w", padx=(6, 0), pady=4)

        # Right Column: Materials & Lighting
        right_col = ttk.Frame(container)
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0))

        card_mats = ttk.LabelFrame(right_col, text=" Materials & Lighting Theme ", padding=12)
        card_mats.pack(fill="x", pady=(0, 10))

        mat_grid = ttk.Frame(card_mats)
        mat_grid.pack(fill="x")

        ttk.Label(mat_grid, text="Render Engine:").grid(row=0, column=0, sticky="w", pady=4)
        combo_engine = ttk.Combobox(
            mat_grid, 
            textvariable=self.var_engine, 
            values=["eevee", "cycles"], 
            width=18, 
            state="readonly"
        )
        combo_engine.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_engine.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(mat_grid, text="Lighting Theme:").grid(row=1, column=0, sticky="w", pady=4)
        combo_light = ttk.Combobox(
            mat_grid, 
            textvariable=self.var_lighting, 
            values=["studio", "dramatic", "warm", "sunset"], 
            width=18, 
            state="readonly"
        )
        combo_light.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_light.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(mat_grid, text="Body Material:").grid(row=2, column=0, sticky="w", pady=4)
        body_mats = [
            "gloss", "gloss:candy_red", "gloss:blue", "gloss:black", "gloss:white",
            "gold", "chrome", "silver", "glass", "glass:blue",
            "sunburst", "sunburst:yellow:red:black", "sparkle:blue:silver",
            "striped", "random"
        ]
        combo_bmat = ttk.Combobox(mat_grid, textvariable=self.var_material, values=body_mats, width=18)
        combo_bmat.grid(row=2, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_bmat.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())
        combo_bmat.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Label(mat_grid, text="Backplate Material:").grid(row=3, column=0, sticky="w", pady=4)
        back_mats = ["gloss:black", "gloss:white", "chrome", "gold", "gloss:red"]
        combo_bkmat = ttk.Combobox(mat_grid, textvariable=self.var_material_back, values=back_mats, width=18)
        combo_bkmat.grid(row=3, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_bkmat.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(mat_grid, text="Random Seed:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(mat_grid, textvariable=self.var_seed, width=12).grid(row=4, column=1, sticky="w", padx=(6, 0), pady=4)

        ttk.Checkbutton(
            card_mats, 
            text="Generate Turntable Animation (--animate)", 
            variable=self.var_animate, 
            command=self._update_command_preview
        ).pack(anchor="w", pady=(8, 4))

        ttk.Checkbutton(
            card_mats, 
            text="Save Completed .blend Scene (--save-blend)", 
            variable=self.var_save_blend, 
            command=self._update_command_preview
        ).pack(anchor="w", pady=(0, 4))

        # Render Button Card
        card_render_act = ttk.LabelFrame(right_col, text=" Launch Studio ", padding=12)
        card_render_act.pack(fill="x")

        btn_run_render = ttk.Button(
            card_render_act, 
            text="🎨  Render Images in Background", 
            style="Primary.TButton", 
            command=self._action_render
        )
        btn_run_render.pack(fill="x", ipady=4, pady=(0, 6))

        btn_view_renders = ttk.Button(
            card_render_act, 
            text="🖼  Open Renders Folder", 
            command=self._open_renders_folder
        )
        btn_view_renders.pack(fill="x")

    # =========================================================================
    # TAB 3: Configuration Parameters Editor
    # =========================================================================
    def _build_tab_config_editor(self):
        container = ttk.Frame(self.tab_config_editor)
        container.pack(fill="both", expand=True)

        toolbar = ttk.Frame(container)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Label(toolbar, text="Profile Parameters:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(toolbar, text="💾 Save Changes", command=self._save_current_config).pack(side="right", padx=(4, 0))
        ttk.Button(toolbar, text="Save As New...", command=self._save_config_as).pack(side="right", padx=(4, 0))
        ttk.Button(toolbar, text="⟲ Reload Profile", command=self._load_current_config_into_editor).pack(side="right")

        # Treeview / Table for JSON parameters
        table_frame = ttk.Frame(container)
        table_frame.pack(fill="both", expand=True)

        columns = ("key", "value")
        self.param_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.param_tree.heading("key", text="Parameter Name")
        self.param_tree.heading("value", text="Value")
        self.param_tree.column("key", width=300, anchor="w")
        self.param_tree.column("value", width=180, anchor="w")

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.param_tree.yview)
        self.param_tree.configure(yscrollcommand=tree_scroll.set)

        self.param_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Edit box beneath table
        edit_box = ttk.Frame(container, padding=(0, 8, 0, 0))
        edit_box.pack(fill="x")
        ttk.Label(edit_box, text="Selected Param:").pack(side="left", padx=(0, 6))
        self.ent_param_name = ttk.Entry(edit_box, width=28, state="readonly")
        self.ent_param_name.pack(side="left", padx=(0, 8))
        ttk.Label(edit_box, text="New Value:").pack(side="left", padx=(0, 6))
        self.ent_param_val = ttk.Entry(edit_box, width=16)
        self.ent_param_val.pack(side="left", padx=(0, 8))
        ttk.Button(edit_box, text="Apply Edit", command=self._apply_param_edit).pack(side="left")

        self.param_tree.bind("<<TreeviewSelect>>", self._on_param_row_selected)

    def _on_param_row_selected(self, event):
        selected = self.param_tree.selection()
        if selected:
            item = self.param_tree.item(selected[0])
            key, val = item["values"]
            self.ent_param_name.configure(state="normal")
            self.ent_param_name.delete(0, tk.END)
            self.ent_param_name.insert(0, str(key))
            self.ent_param_name.configure(state="readonly")

            self.ent_param_val.delete(0, tk.END)
            self.ent_param_val.insert(0, str(val))

    def _apply_param_edit(self):
        selected = self.param_tree.selection()
        if not selected:
            return
        key = self.ent_param_name.get().strip()
        new_val_str = self.ent_param_val.get().strip()
        try:
            # Try parsing as float or int or bool
            if new_val_str.lower() in ["true", "false"]:
                new_val = (new_val_str.lower() == "true")
            elif "." in new_val_str:
                new_val = float(new_val_str)
            else:
                new_val = int(new_val_str)
        except ValueError:
            new_val = new_val_str

        self.param_tree.item(selected[0], values=(key, new_val))

    def _load_current_config_into_editor(self):
        config_name = self.var_config.get().strip()
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        if not os.path.exists(config_path):
            return

        for item in self.param_tree.get_children():
            self.param_tree.delete(item)

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
            for k, v in data.items():
                self.param_tree.insert("", "end", values=(k, v))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config file: {e}")

    def _save_current_config(self):
        config_name = self.var_config.get().strip()
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        self._write_tree_to_json(config_path)
        messagebox.showinfo("Saved", f"Profile '{config_name}.json' saved successfully!")

    def _save_config_as(self):
        new_name = filedialog.asksaveasfilename(
            initialdir=self.config_dir,
            title="Save Profile As",
            filetypes=[("JSON Files", "*.json")],
            defaultextension=".json"
        )
        if new_name:
            self._write_tree_to_json(new_name)
            self._refresh_config_list()
            base_name = os.path.splitext(os.path.basename(new_name))[0]
            self.var_config.set(base_name)
            messagebox.showinfo("Saved", f"Profile '{base_name}' created successfully!")

    def _write_tree_to_json(self, filepath):
        data = {}
        for child in self.param_tree.get_children():
            k, v = self.param_tree.item(child)["values"]
            try:
                if str(v).lower() in ["true", "false"]:
                    data[k] = (str(v).lower() == "true")
                elif "." in str(v):
                    data[k] = float(v)
                else:
                    data[k] = int(v)
            except ValueError:
                data[k] = v
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    # =========================================================================
    # TAB 4: Render Gallery
    # =========================================================================
    def _build_tab_gallery(self):
        container = ttk.Frame(self.tab_gallery)
        container.pack(fill="both", expand=True)

        toolbar = ttk.Frame(container)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Label(toolbar, text="Render Output Previews:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(toolbar, text="↻ Refresh Previews", command=self._refresh_gallery).pack(side="right")
        ttk.Button(toolbar, text="📁 Open Renders Folder", command=self._open_renders_folder).pack(side="right", padx=(0, 6))

        # Canvas / Frame for image previews
        self.gallery_frame = ttk.Frame(container)
        self.gallery_frame.pack(fill="both", expand=True)
        self.gallery_images = []  # Keep references to avoid garbage collection

        self.lbl_no_renders = ttk.Label(
            self.gallery_frame, 
            text="No renders found for active profile.\nLaunch a render from the Photo Studio tab to view images here.",
            font=("Segoe UI", 11),
            foreground="#64748b",
            justify="center"
        )
        self.lbl_no_renders.pack(expand=True)

    def _refresh_gallery(self):
        # Clear existing images
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.gallery_images.clear()

        config_name = self.var_config.get().strip()
        renders_dir = os.path.join(self.output_dir, config_name, "renders")

        if not os.path.exists(renders_dir):
            lbl = ttk.Label(self.gallery_frame, text=f"No renders folder found at:\n{renders_dir}", justify="center", foreground="#64748b")
            lbl.pack(expand=True)
            return

        png_files = [f for f in os.listdir(renders_dir) if f.lower().endswith(".png")]
        if not png_files:
            lbl = ttk.Label(self.gallery_frame, text=f"No PNG render images found in:\n{renders_dir}", justify="center", foreground="#64748b")
            lbl.pack(expand=True)
            return

        # Display images in a grid
        row_frame = ttk.Frame(self.gallery_frame)
        row_frame.pack(fill="both", expand=True)

        col = 0
        row = 0
        for png in png_files:
            full_path = os.path.join(renders_dir, png)
            try:
                raw_img = tk.PhotoImage(file=full_path)
                # Subsample for thumbnail (around 4x to 5x downscale)
                sub_factor = max(1, raw_img.width() // 320)
                thumb = raw_img.subsample(sub_factor, sub_factor)
                self.gallery_images.append(thumb)

                card = ttk.Frame(row_frame, relief="solid", borderwidth=1, padding=6)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

                lbl_img = tk.Label(card, image=thumb, bg="#ffffff", cursor="hand2")
                lbl_img.pack()
                lbl_img.bind("<Button-1>", lambda e, p=full_path: self._open_file(p))

                lbl_name = ttk.Label(card, text=png, font=("Segoe UI", 9, "bold"))
                lbl_name.pack(pady=(4, 0))

                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading thumbnail for {png}: {e}")

    # =========================================================================
    # Bottom Console / Log Area
    # =========================================================================
    def _build_console_area(self):
        console_container = ttk.Frame(self.root, padding=(16, 4, 16, 12))
        console_container.pack(fill="both", expand=False)

        header_bar = ttk.Frame(console_container)
        header_bar.pack(fill="x", pady=(0, 4))

        self.lbl_status = ttk.Label(header_bar, text="Status: Ready", font=("Segoe UI", 9, "bold"), foreground="#0f172a")
        self.lbl_status.pack(side="left")

        self.btn_cancel = ttk.Button(header_bar, text="⏹ Stop Process", style="Danger.TButton", state="disabled", command=self._cancel_process)
        self.btn_cancel.pack(side="right", padx=(6, 0))

        ttk.Button(header_bar, text="Clear Log", command=self._clear_log).pack(side="right")

        # Text Console with Scrollbar
        txt_frame = ttk.Frame(console_container)
        txt_frame.pack(fill="both", expand=True)

        self.txt_console = tk.Text(
            txt_frame, 
            height=9, 
            bg="#0f172a", 
            fg="#f8fafc", 
            insertbackground="#38bdf8",
            font=("Consolas", 9),
            wrap="word",
            relief="flat",
            padx=8,
            pady=6
        )
        scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=self.txt_console.yview)
        self.txt_console.configure(yscrollcommand=scroll.set)

        self.txt_console.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # =========================================================================
    # Command Construction & Execution
    # =========================================================================
    def _update_command_preview(self):
        """Construct the exact CLI argument string based on active options."""
        cmd = [sys.executable, "guitar_builder.py"]

        config_name = self.var_config.get().strip()
        if config_name and config_name != "default":
            cmd.append(config_name)

        # Slicing options
        if self.var_no_cut.get():
            cmd.append("--no-cut")
        else:
            cut_type = self.var_cut_type.get()
            if cut_type != "flat":
                cmd.extend(["--cut-type", cut_type])

            if cut_type == "flat":
                if not self.var_enable_pins.get():
                    cmd.append("--no-pins")
                else:
                    diam = self.var_pin_diameter.get()
                    length = self.var_pin_length.get()
                    if diam != 6.0:
                        cmd.extend(["--pin-diameter", str(diam)])
                    if length != 16.0:
                        cmd.extend(["--pin-length", str(length)])

        # Hardware & Electronics variants
        hw = self.var_hardware.get().strip()
        if hw and hw != "standard":
            cmd.extend(["--hardware", hw])

        elec = self.var_electronics.get().strip()
        if elec and elec != "auto":
            cmd.extend(["--electronics", elec])

        # Rendering options
        if self.var_render_pipeline.get():
            cmd.append("--render")
            if self.var_render_uncut.get():
                cmd.append("--uncut")
            if self.var_body_only.get():
                cmd.append("--body-only")
            if self.var_exploded_body.get():
                cmd.append("--exploded-body")

            angle = self.var_angle.get().strip()
            if angle and angle != "all":
                cmd.extend(["--angle", angle])

            engine = self.var_engine.get().strip()
            if engine != "eevee":
                cmd.extend(["--engine", engine])

            material = self.var_material.get().strip()
            if material and material != "gloss":
                cmd.extend(["--material", material])

            material_back = self.var_material_back.get().strip()
            if material_back and material_back != "gloss:black":
                cmd.extend(["--material-back", material_back])

            lighting = self.var_lighting.get().strip()
            if lighting and lighting != "studio":
                cmd.extend(["--lighting", lighting])

            pitch = self.var_pitch.get().strip()
            if pitch:
                cmd.extend(["--pitch", pitch])

            guitar_rot = self.var_guitar_rot.get().strip()
            if guitar_rot:
                cmd.extend(["--guitar-rot", guitar_rot])

            if self.var_dynamic_zoom.get():
                cmd.append("--dynamic-zoom")

            if self.var_animate.get():
                cmd.append("--animate")

            if self.var_save_blend.get():
                cmd.append("--save-blend")

            seed = self.var_seed.get().strip()
            if seed:
                cmd.extend(["--seed", seed])

        self.var_cmd_preview.set(" ".join(cmd))
        return cmd

    def _copy_command_preview(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.var_cmd_preview.get())
        messagebox.showinfo("Copied", "Command line copied to clipboard!")

    def _action_build_and_slice(self):
        """Run standard build and cut pipeline."""
        self.var_render_pipeline.set(False)
        cmd = self._update_command_preview()
        self._start_subprocess(cmd, "Building and Slicing Guitar Body...")

    def _action_generate_mesh_only(self):
        """Run Stage 1 generate mesh only."""
        config_name = self.var_config.get().strip()
        cmd = [sys.executable, "guitar_builder.py", "--config", config_name, "--generate"]
        self._start_subprocess(cmd, "Generating Base 3D Mesh Only...")

    def _action_render(self):
        """Run background render pipeline."""
        self.var_render_pipeline.set(True)
        cmd = self._update_command_preview()
        self._start_subprocess(cmd, "Running Photo Studio Rendering...")

    def _action_compile_scad(self):
        """Run OpenSCAD STL compilation."""
        compile_script = os.path.join(self.scripts_dir, "compile_scad.py")
        cmd = [sys.executable, compile_script]
        self._start_subprocess(cmd, "Compiling OpenSCAD Hardware STLs...")

    def _start_subprocess(self, cmd, description):
        """Execute a command line in a background worker thread."""
        if self.is_running:
            messagebox.showwarning("Busy", "A process is already running. Please wait or cancel it first.")
            return

        self._clear_log()
        self._log(f"=== {description} ===\n")
        self._log(f"Command: {' '.join(cmd)}\n\n")

        self.lbl_status.configure(text=f"Status: {description}", foreground="#2563eb")
        self.btn_cancel.configure(state="normal")
        self.is_running = True

        def worker():
            start_time = time.time()
            try:
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=self.repo_dir
                )

                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        self.log_queue.put(line)

                self.current_process.stdout.close()
                returncode = self.current_process.wait()
                elapsed = time.time() - start_time

                if returncode == 0:
                    self.log_queue.put(f"\n[SUCCESS] Completed in {elapsed:.1f}s with return code 0.\n")
                    self.root.after(0, lambda: self._on_process_complete(True))
                else:
                    self.log_queue.put(f"\n[ERROR] Process finished with error code {returncode} (in {elapsed:.1f}s).\n")
                    self.root.after(0, lambda: self._on_process_complete(False))

            except Exception as e:
                self.log_queue.put(f"\n[CRITICAL ERROR] Failed to launch process: {e}\n")
                self.root.after(0, lambda: self._on_process_complete(False))
            finally:
                self.current_process = None

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _cancel_process(self):
        if self.current_process and self.is_running:
            try:
                self._log("\n--> Terminating process...\n")
                self.current_process.terminate()
            except Exception as e:
                self._log(f"Failed to terminate process: {e}\n")

    def _on_process_complete(self, success):
        self.is_running = False
        self.btn_cancel.configure(state="disabled")
        status_text = "Status: Completed Successfully" if success else "Status: Failed / Finished with errors"
        status_color = "#16a34a" if success else "#dc2626"
        self.lbl_status.configure(text=status_text, foreground=status_color)
        self._refresh_gallery()

    def _process_log_queue(self):
        while not self.log_queue.empty():
            line = self.log_queue.get_nowait()
            self._log(line)
        self.root.after(100, self._process_log_queue)

    def _log(self, text):
        self.txt_console.insert(tk.END, text)
        self.txt_console.see(tk.END)

    def _clear_log(self):
        self.txt_console.delete("1.0", tk.END)

    # =========================================================================
    # Helpers & File Operations
    # =========================================================================
    def _refresh_config_list(self):
        configs = []
        if os.path.exists(self.config_dir):
            for f in sorted(os.listdir(self.config_dir)):
                if f.endswith(".json") and not f.startswith("last_"):
                    configs.append(os.path.splitext(f)[0])

        current = self.var_config.get()
        self.combo_config["values"] = configs
        if current in configs:
            self.combo_config.set(current)
        elif configs:
            self.combo_config.set(configs[0])

        # Scan hardware variants from models/scad/hardware/
        hw_base = os.path.join(self.repo_dir, "models", "scad", "hardware")
        hw_variants = []
        if os.path.exists(hw_base):
            hw_variants = [d for d in sorted(os.listdir(hw_base)) if os.path.isdir(os.path.join(hw_base, d))]
        if not hw_variants:
            hw_variants = ["standard", "piezo"]
        self.combo_hardware["values"] = hw_variants
        if self.var_hardware.get() not in hw_variants:
            self.var_hardware.set(hw_variants[0] if hw_variants else "standard")

        # Scan electronics variants from models/scad/electronics/
        elec_base = os.path.join(self.repo_dir, "models", "scad", "electronics")
        elec_variants = ["auto"]
        if os.path.exists(elec_base):
            elec_variants += [d for d in sorted(os.listdir(elec_base)) if os.path.isdir(os.path.join(elec_base, d))]
        else:
            elec_variants += ["sarcaster", "flying_v", "les_paul"]
        self.combo_electronics["values"] = elec_variants

        self._load_current_config_into_editor()
        self._sync_variants_from_config()
        self._update_command_preview()

    def _sync_variants_from_config(self):
        """Read default hardware and electronics variants from the active config JSON if present."""
        cfg_name = self.var_config.get().strip()
        cfg_path = os.path.join(self.config_dir, f"{cfg_name}.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r") as f:
                    cdata = json.load(f)
                if "hardware" in cdata:
                    self.var_hardware.set(cdata["hardware"])
                if "electronics" in cdata:
                    self.var_electronics.set(cdata["electronics"])
                elif "electronics" not in cdata:
                    self.var_electronics.set("auto")
            except Exception:
                pass

    def _on_config_selected(self, event=None):
        self._load_current_config_into_editor()
        self._sync_variants_from_config()
        self._refresh_gallery()
        self._update_command_preview()

    def _open_current_output_dir(self):
        config_name = self.var_config.get().strip()
        path = os.path.join(self.output_dir, config_name)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        self._open_folder(path)

    def _open_renders_folder(self):
        config_name = self.var_config.get().strip()
        path = os.path.join(self.output_dir, config_name, "renders")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        self._open_folder(path)

    def _open_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _open_file(self, path):
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


def main():
    root = tk.Tk()
    app = GuitarBuilderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
