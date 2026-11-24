import os
import sys
import json
import time
import queue
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Windows DPI Awareness
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from scripts.project_manager import ProjectManager


class ScrollableFrame(ttk.Frame):
    """A clean scrollable frame container that automatically supports vertical scrolling with mousewheel."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#f5f6f8")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = ttk.Frame(self.canvas, padding=10)
        
        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mousewheel when pointer is over this container
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Button-5>", self._on_mousewheel, add="+")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        try:
            x, y = self.canvas.winfo_pointerxy()
            w = self.canvas.winfo_containing(x, y)
            if w is not None and (w == self.canvas or str(w).startswith(str(self))):
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
                elif event.delta:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class GuitarBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GuitarBuilder Studio")
        
        # Responsive initial window size based on screen resolution
        try:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            target_w = min(1400, max(1160, int(screen_w * 0.88)))
            target_h = min(1000, max(820, int(screen_h * 0.88)))
            pos_x = max(0, (screen_w - target_w) // 2)
            pos_y = max(0, (screen_h - target_h) // 2)
            self.root.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")
        except Exception:
            self.root.geometry("1240x880")
        self.root.minsize(980, 640)

        # Base directories & Project Manager
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
        self.scripts_dir = os.path.join(self.repo_dir, "scripts")
        self.project_manager = ProjectManager(self.repo_dir)

        # Active project state
        self.active_project_name = tk.StringVar()
        self.active_project_dir = ""
        self.active_project_data = {}

        # Process management
        self.current_process = None
        self.log_queue = queue.Queue()
        self.is_running = False

        # Image references to prevent garbage collection
        self._cached_preview_img = None
        self.gallery_images = []

        # Find blender executable
        self.blender_exe = self._locate_blender()

        # UI Variables
        self._init_variables()

        # Build UI layout
        self._setup_styles()
        self._build_ui()

        # Start periodic log pump
        self.root.after(100, self._process_log_queue)

        # Initial project loading
        self._init_projects()

    def _locate_blender(self):
        """Find Blender executable using guitar_builder logic."""
        try:
            import guitar_builder
            return guitar_builder.find_blender()
        except Exception:
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
        # 1. Design & Spec
        self.var_body_model = tk.StringVar(value="sarcaster")
        self.var_neck = tk.StringVar(value="strat")
        self.var_neck_material = tk.StringVar(value="maple")
        self.var_fretboard_material = tk.StringVar(value="rosewood")
        self.var_tuner_finish = tk.StringVar(value="chrome")
        self.var_hardware = tk.StringVar(value="standard")
        self.var_electronics = tk.StringVar(value="auto")

        # 2. Visuals & Finish
        self.var_presentation_mode = tk.StringVar(value="sliced")  # "sliced", "uncut", "exploded"
        self.var_finish_mode = tk.StringVar(value="uniform")  # "uniform", "random_parts"
        self.var_random_style = tk.StringVar(value="gloss:random")
        self.var_material = tk.StringVar(value="sunburst")
        self.var_material_back = tk.StringVar(value="gloss:black")
        self.var_lighting = tk.StringVar(value="studio")
        self.var_engine = tk.StringVar(value="eevee")
        self.var_preview_angle = tk.StringVar(value="angled")
        self.var_angle = tk.StringVar(value="all")
        self.var_dynamic_zoom = tk.BooleanVar(value=True)
        self.var_animate = tk.BooleanVar(value=False)
        self.var_save_blend = tk.BooleanVar(value=False)
        self.var_seed = tk.StringVar(value="")

        # 3. Slicing & 3D Print
        self.var_cut_type = tk.StringVar(value="textured")
        self.var_enable_pins = tk.BooleanVar(value=True)
        self.var_pin_diameter = tk.DoubleVar(value=6.0)
        self.var_pin_length = tk.DoubleVar(value=16.0)
        self.var_no_cut = tk.BooleanVar(value=False)

        # Realtime command preview
        self.var_cmd_preview = tk.StringVar()

    def _setup_styles(self):
        """Setup custom TTK styles for a clean, modern look."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.bg_color = "#f8fafc"
        self.card_bg = "#ffffff"
        self.primary_color = "#2563eb"
        self.primary_hover = "#1d4ed8"

        self.root.configure(bg=self.bg_color)

        self.style.configure(".", background=self.bg_color, font=("Segoe UI", 9))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground="#1e293b")
        
        self.style.configure("TLabelframe", background=self.bg_color, relief="groove")
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"), foreground="#0f172a", background=self.bg_color)

        self.style.configure("TNotebook", background=self.bg_color, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", padding=[14, 6], font=("Segoe UI", 9, "bold"), background="#e2e8f0", foreground="#475569")
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#0f172a")])

        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=self.primary_color, foreground="#ffffff", borderwidth=0, padding=6)
        self.style.map("Primary.TButton", background=[("active", self.primary_hover), ("pressed", "#1e40af")])

        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), background="#059669", foreground="#ffffff", padding=8)
        self.style.map("Action.TButton", background=[("active", "#047857")])

        self.style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), background="#ef4444", foreground="#ffffff")
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])

    # =========================================================================
    # UI Construction
    # =========================================================================
    def _build_ui(self):
        # Header Frame: Project management bar
        header_frame = ttk.Frame(self.root, padding=(16, 10, 16, 6))
        header_frame.pack(fill="x")

        # Title & Blender status
        title_box = ttk.Frame(header_frame)
        title_box.pack(side="left")

        lbl_title = tk.Label(title_box, text="🎸 GuitarBuilder Studio", font=("Segoe UI", 14, "bold"), fg="#0f172a", bg=self.bg_color)
        lbl_title.pack(anchor="w")

        blender_text = f"Blender: {os.path.basename(os.path.dirname(self.blender_exe))}" if self.blender_exe else "Blender: Not Found"
        blender_color = "#16a34a" if self.blender_exe else "#dc2626"
        lbl_blender = tk.Label(title_box, text=f"● {blender_text}", font=("Segoe UI", 9, "bold"), fg=blender_color, bg=self.bg_color)
        lbl_blender.pack(anchor="w", pady=(1, 0))

        # Project Bar in Header
        proj_bar = ttk.Frame(header_frame)
        proj_bar.pack(side="right", fill="y")

        ttk.Label(proj_bar, text="Project:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))
        self.combo_project = ttk.Combobox(proj_bar, textvariable=self.active_project_name, width=22, state="readonly")
        self.combo_project.pack(side="left", padx=(0, 6))
        self.combo_project.bind("<<ComboboxSelected>>", self._on_project_selected)

        ttk.Button(proj_bar, text="＋ New", width=7, command=self._action_new_project).pack(side="left", padx=(0, 4))
        ttk.Button(proj_bar, text="💾 Save", width=7, style="Primary.TButton", command=self._action_save_project).pack(side="left", padx=(0, 4))
        ttk.Button(proj_bar, text="Save As...", width=9, command=self._action_save_project_as).pack(side="left", padx=(0, 4))
        ttk.Button(proj_bar, text="📁 Folder", width=8, command=self._open_project_folder).pack(side="left")

        # Separator line
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=16, pady=4)

        # Vertical PanedWindow: Top = Notebook (weight 9), Bottom = Console & Preview (weight 1)
        self.paned_window = ttk.PanedWindow(self.root, orient="vertical")
        self.paned_window.pack(fill="both", expand=True, padx=16, pady=(4, 6))

        # Top Pane: Tabbed Notebook
        self.notebook_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.notebook_frame, weight=9)

        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Build 3-Step Journey Tabs + Gallery
        self.tab_spec = ttk.Frame(self.notebook)
        self.tab_finish = ttk.Frame(self.notebook)
        self.tab_slicing = ttk.Frame(self.notebook)
        self.tab_gallery = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_spec, text="  🎸 1. Design & Spec  ")
        self.notebook.add(self.tab_finish, text="  🎨 2. Visuals & Finish  ")
        self.notebook.add(self.tab_slicing, text="  ✂ 3. Slicing & 3D Print  ")
        self.notebook.add(self.tab_gallery, text="  🖼 Project Gallery  ")

        self._build_tab_spec()
        self._build_tab_finish()
        self._build_tab_slicing()
        self._build_tab_gallery()

        # Bottom Pane: Command Preview Bar + Live Console
        self.bottom_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.bottom_frame, weight=1)

        # Command Preview Bar
        preview_frame = ttk.Frame(self.bottom_frame, padding=(0, 1, 0, 2))
        preview_frame.pack(fill="x")
        ttk.Label(preview_frame, text="Command Preview:", font=("Segoe UI", 9, "bold"), foreground="#475569").pack(side="left", padx=(0, 6))
        ent_preview = ttk.Entry(preview_frame, textvariable=self.var_cmd_preview, state="readonly", font=("Consolas", 9))
        ent_preview.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(preview_frame, text="Copy CLI", command=self._copy_command_preview).pack(side="right")

        # Console Area
        self._build_console_area(self.bottom_frame)

    # =========================================================================
    # TAB 1: Design & Specification
    # =========================================================================
    def _build_tab_spec(self):
        scroll = ScrollableFrame(self.tab_spec)
        scroll.pack(fill="both", expand=True)
        container = scroll.scrollable_content

        # Card 1: Body Model Selection
        card_body = ttk.LabelFrame(container, text=" 1. Guitar Body Model & Geometry ", padding=10)
        card_body.pack(fill="x", pady=(0, 8))

        row_b = ttk.Frame(card_body)
        row_b.pack(fill="x", pady=(0, 6))

        ttk.Label(row_b, text="Base Body Model:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self.combo_body_model = ttk.Combobox(row_b, textvariable=self.var_body_model, width=22, state="readonly")
        self.combo_body_model.pack(side="left", padx=(0, 12))
        self.combo_body_model.bind("<<ComboboxSelected>>", self._on_body_model_selected)

        self.btn_toggle_dims = ttk.Button(row_b, text="▸ Fine-Tune Dimensions (36 Parameters)", command=self._toggle_dimensions_drawer)
        self.btn_toggle_dims.pack(side="left")

        # Dimensions Drawer (Initially hidden)
        self.dims_drawer_visible = False
        self.dims_frame = ttk.Frame(card_body, padding=(0, 8, 0, 0))

        tbl_frame = ttk.Frame(self.dims_frame)
        tbl_frame.pack(fill="x", expand=True)

        self.param_tree = ttk.Treeview(tbl_frame, columns=("key", "value"), show="headings", height=8)
        self.param_tree.heading("key", text="Geometry Node Dimension")
        self.param_tree.heading("value", text="Value (cm)")
        self.param_tree.column("key", width=260, anchor="w")
        self.param_tree.column("value", width=120, anchor="w")

        p_scroll = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.param_tree.yview)
        self.param_tree.configure(yscrollcommand=p_scroll.set)
        self.param_tree.pack(side="left", fill="x", expand=True)
        p_scroll.pack(side="right", fill="y")

        edit_bar = ttk.Frame(self.dims_frame, padding=(0, 4, 0, 0))
        edit_bar.pack(fill="x")
        ttk.Label(edit_bar, text="Selected:").pack(side="left", padx=(0, 4))
        self.ent_dim_name = ttk.Entry(edit_bar, width=22, state="readonly")
        self.ent_dim_name.pack(side="left", padx=(0, 8))
        ttk.Label(edit_bar, text="Value:").pack(side="left", padx=(0, 4))
        self.ent_dim_val = ttk.Entry(edit_bar, width=12)
        self.ent_dim_val.pack(side="left", padx=(0, 8))
        ttk.Button(edit_bar, text="Apply Edit", command=self._apply_dim_edit).pack(side="left")
        ttk.Button(edit_bar, text="Reset to Model Defaults", command=self._reset_dims_to_model).pack(side="right")
        self.param_tree.bind("<<TreeviewSelect>>", self._on_dim_selected)

        # Card 2: Neck & Headstock Specification
        card_neck = ttk.LabelFrame(container, text=" 2. Neck, Fretboard & Headstock Specification ", padding=10)
        card_neck.pack(fill="x", pady=(0, 8))

        grid_neck = ttk.Frame(card_neck)
        grid_neck.pack(fill="x")

        ttk.Label(grid_neck, text="Neck Style:").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_neck = ttk.Combobox(
            grid_neck,
            textvariable=self.var_neck,
            values=["strat", "les_paul", "auto"],
            width=18,
            state="readonly"
        )
        self.combo_neck.grid(row=0, column=1, sticky="w", padx=(6, 20), pady=4)
        self.combo_neck.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_neck, text="Neck Shaft Wood:").grid(row=0, column=2, sticky="w", pady=4)
        combo_nwood = ttk.Combobox(
            grid_neck,
            textvariable=self.var_neck_material,
            values=["maple", "rosewood", "ebony"],
            width=18,
            state="readonly"
        )
        combo_nwood.grid(row=0, column=3, sticky="w", padx=(6, 0), pady=4)
        combo_nwood.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_neck, text="Fretboard Wood:").grid(row=1, column=0, sticky="w", pady=4)
        combo_fbwood = ttk.Combobox(
            grid_neck,
            textvariable=self.var_fretboard_material,
            values=["rosewood", "maple", "ebony"],
            width=18,
            state="readonly"
        )
        combo_fbwood.grid(row=1, column=1, sticky="w", padx=(6, 20), pady=4)
        combo_fbwood.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_neck, text="Tuner Finish:").grid(row=1, column=2, sticky="w", pady=4)
        combo_tuner = ttk.Combobox(
            grid_neck,
            textvariable=self.var_tuner_finish,
            values=["chrome", "gold", "black"],
            width=18,
            state="readonly"
        )
        combo_tuner.grid(row=1, column=3, sticky="w", padx=(6, 0), pady=4)
        combo_tuner.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        lbl_neck_specs = ttk.Label(
            card_neck, 
            text="ℹ Features: 22 medium jumbo nickel-silver crowned frets (mathematically exact 12th-root-of-two spacing), slotted bone nut, and sealed tuning machine pegs.",
            foreground="#64748b"
        )
        lbl_neck_specs.pack(anchor="w", pady=(6, 0))

        # Card 3: Hardware & Cavities
        card_hw = ttk.LabelFrame(container, text=" 3. Hardware Cavities & Electronics Layout ", padding=10)
        card_hw.pack(fill="x", pady=(0, 6))

        grid_hw = ttk.Frame(card_hw)
        grid_hw.pack(fill="x")

        ttk.Label(grid_hw, text="Hardware Cavity:").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_hardware = ttk.Combobox(grid_hw, textvariable=self.var_hardware, width=18, state="readonly")
        self.combo_hardware.grid(row=0, column=1, sticky="w", padx=(6, 20), pady=4)
        self.combo_hardware.bind("<<ComboboxSelected>>", self._on_geometry_setting_changed)

        ttk.Label(grid_hw, text="Electronics Layout:").grid(row=0, column=2, sticky="w", pady=4)
        self.combo_electronics = ttk.Combobox(grid_hw, textvariable=self.var_electronics, width=18, state="readonly")
        self.combo_electronics.grid(row=0, column=3, sticky="w", padx=(6, 0), pady=4)
        self.combo_electronics.bind("<<ComboboxSelected>>", self._on_geometry_setting_changed)

        lbl_hw_note = ttk.Label(
            card_hw,
            text="ℹ Backplate cavities and flush screw fixings are subtracted automatically based on selected variants.",
            foreground="#64748b"
        )
        lbl_hw_note.pack(anchor="w", pady=(6, 0))

        # Card 4: Body Presentation & Slice Status
        card_slice_stat = ttk.LabelFrame(container, text=" 4. Body Presentation & Slicing Status ", padding=10)
        card_slice_stat.pack(fill="x", pady=(0, 6))

        row_stat = ttk.Frame(card_slice_stat)
        row_stat.pack(fill="x")

        ttk.Label(row_stat, text="Presentation Mode:").pack(side="left", padx=(0, 8))
        combo_pres = ttk.Combobox(
            row_stat,
            textvariable=self.var_presentation_mode,
            values=["sliced", "uncut", "exploded"],
            width=16,
            state="readonly"
        )
        combo_pres.pack(side="left", padx=(0, 16))
        combo_pres.bind("<<ComboboxSelected>>", self._on_presentation_mode_change)

        self.lbl_slice_status = ttk.Label(row_stat, text="○ Slices: Unknown", font=("Segoe UI", 9, "bold"))
        self.lbl_slice_status.pack(side="left", padx=(0, 16))

        btn_cut_tab1 = ttk.Button(row_stat, text="✂️ Slice / Re-Cut Body", command=self._action_slice_body)
        btn_cut_tab1.pack(side="left")

        lbl_slice_desc = ttk.Label(
            card_slice_stat,
            text="ℹ Sliced mode renders the 8 3D-printable parts with visible seam cuts. Changes to geometry or hardware cavity mark slices as 'Needs Cut'.",
            foreground="#64748b"
        )
        lbl_slice_desc.pack(anchor="w", pady=(6, 0))

    def _toggle_dimensions_drawer(self):
        if self.dims_drawer_visible:
            self.dims_frame.pack_forget()
            self.btn_toggle_dims.configure(text="▸ Fine-Tune Dimensions (36 Parameters)")
            self.dims_drawer_visible = False
        else:
            self.dims_frame.pack(fill="x", pady=(8, 0))
            self.btn_toggle_dims.configure(text="▾ Close Dimensions Editor")
            self.dims_drawer_visible = True

    def _on_dim_selected(self, event):
        selected = self.param_tree.selection()
        if selected:
            key, val = self.param_tree.item(selected[0])["values"]
            self.ent_dim_name.configure(state="normal")
            self.ent_dim_name.delete(0, tk.END)
            self.ent_dim_name.insert(0, str(key))
            self.ent_dim_name.configure(state="readonly")

            self.ent_dim_val.delete(0, tk.END)
            self.ent_dim_val.insert(0, str(val))

    def _apply_dim_edit(self):
        selected = self.param_tree.selection()
        if not selected:
            return
        key = self.ent_dim_name.get().strip()
        val_str = self.ent_dim_val.get().strip()
        try:
            val = float(val_str) if "." in val_str else int(val_str)
        except ValueError:
            val = val_str

        self.param_tree.item(selected[0], values=(key, val))
        if "body_dimensions" not in self.active_project_data:
            self.active_project_data["body_dimensions"] = {}
        self.active_project_data["body_dimensions"][key] = val
        self._update_slice_status_badge()

    def _reset_dims_to_model(self):
        model = self.var_body_model.get().strip()
        dims = self.project_manager.get_default_body_dimensions(model)
        self.active_project_data["body_dimensions"] = dims
        self._populate_dims_table(dims)
        self._update_slice_status_badge()

    # =========================================================================
    # TAB 2: Visuals & Finish (with Quick Preview)
    # =========================================================================
    def _build_tab_finish(self):
        scroll = ScrollableFrame(self.tab_finish)
        scroll.pack(fill="both", expand=True)
        container = scroll.scrollable_content

        # Two-Column Layout
        left_col = ttk.Frame(container)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = ttk.Frame(container)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Left Column: Material & Lighting Controls
        # Card 1: Presentation Mode & Slices Status
        card_pres = ttk.LabelFrame(left_col, text=" 1. Body Presentation Mode & Slices ", padding=10)
        card_pres.pack(fill="x", pady=(0, 8))

        row_pres = ttk.Frame(card_pres)
        row_pres.pack(fill="x", pady=(0, 4))

        ttk.Label(row_pres, text="Body Mode:").pack(side="left", padx=(0, 6))
        combo_pres_t2 = ttk.Combobox(
            row_pres,
            textvariable=self.var_presentation_mode,
            values=["sliced", "uncut", "exploded"],
            width=14,
            state="readonly"
        )
        combo_pres_t2.pack(side="left", padx=(0, 10))
        combo_pres_t2.bind("<<ComboboxSelected>>", self._on_presentation_mode_change)

        self.lbl_slice_status_tab2 = ttk.Label(row_pres, text="○ Slices: Unknown", font=("Segoe UI", 9, "bold"))
        self.lbl_slice_status_tab2.pack(side="left", padx=(0, 10))

        btn_cut_tab2 = ttk.Button(row_pres, text="✂️ Slice / Re-Cut", command=self._action_slice_body)
        btn_cut_tab2.pack(side="left")

        ttk.Label(
            card_pres,
            text="• Sliced: Renders 8 printable sections with joint seams.\n• Seamless Uncut: Fast single-piece body preview (5-10s).\n• Exploded: Separates sliced parts along cut lines.",
            foreground="#64748b"
        ).pack(anchor="w", pady=(4, 0))

        # Card 2: Paint Scheme & Multi-Color Sections
        card_mats = ttk.LabelFrame(left_col, text=" 2. Finish Scheme & Section Colors ", padding=10)
        card_mats.pack(fill="x", pady=(0, 8))

        mode_row = ttk.Frame(card_mats)
        mode_row.pack(fill="x", pady=(0, 6))

        ttk.Label(mode_row, text="Finish Mode:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        r1 = ttk.Radiobutton(
            mode_row,
            text="Uniform Finish",
            variable=self.var_finish_mode,
            value="uniform",
            command=self._on_finish_mode_change
        )
        r1.pack(side="left", padx=(0, 12))

        r2 = ttk.Radiobutton(
            mode_row,
            text="Random Colors Per Section",
            variable=self.var_finish_mode,
            value="random_parts",
            command=self._on_finish_mode_change
        )
        r2.pack(side="left")

        # Container for Uniform Finish controls
        self.frame_uniform_finish = ttk.Frame(card_mats)
        self.frame_uniform_finish.pack(fill="x", pady=(0, 4))

        row_u = ttk.Frame(self.frame_uniform_finish)
        row_u.pack(fill="x", pady=2)
        ttk.Label(row_u, text="Body Paint / Finish:").pack(side="left", padx=(0, 8))
        body_mats = [
            "sunburst", "gloss:candy_red", "gloss:blue", "gloss:black", "gloss:white",
            "matte:black", "matte:white", "matte:red", "matte:blue",
            "gold", "chrome", "chrome:red", "chrome:blue", "silver",
            "glass", "glass:blue", "glass:red", "glass:amber",
            "sparkle:blue:silver", "sparkle:red:gold", "striped"
        ]
        self.combo_bmat = ttk.Combobox(row_u, textvariable=self.var_material, values=body_mats, width=22)
        self.combo_bmat.pack(side="left", padx=(0, 8))
        self.combo_bmat.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())
        self.combo_bmat.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Container for Random Finish controls
        self.frame_random_finish = ttk.Frame(card_mats)

        row_r = ttk.Frame(self.frame_random_finish)
        row_r.pack(fill="x", pady=2)
        ttk.Label(row_r, text="Finish Style:").pack(side="left", padx=(0, 8))
        rand_styles = [
            "gloss:random",
            "matte:random",
            "sparkle:random",
            "chrome:random",
            "glass:random",
            "random"
        ]
        combo_rstyle = ttk.Combobox(row_r, textvariable=self.var_random_style, values=rand_styles, width=16, state="readonly")
        combo_rstyle.pack(side="left", padx=(0, 10))
        combo_rstyle.bind("<<ComboboxSelected>>", lambda e: self._on_random_style_selected())

        ttk.Label(row_r, text="Seed:").pack(side="left", padx=(0, 4))
        ent_seed = ttk.Entry(row_r, textvariable=self.var_seed, width=10)
        ent_seed.pack(side="left", padx=(0, 6))
        ent_seed.bind("<KeyRelease>", lambda e: self._update_command_preview())

        btn_roll = ttk.Button(row_r, text="🎲 Roll Colors", command=self._roll_random_seed)
        btn_roll.pack(side="left")

        ttk.Label(
            self.frame_random_finish,
            text="ℹ Distinct randomized colors are assigned to each of the 8 sliced 3D print sections.",
            foreground="#64748b"
        ).pack(anchor="w", pady=(4, 0))

        # Card 3: Studio Lighting & Scene Setup
        card_scene = ttk.LabelFrame(left_col, text=" 3. Studio Lighting & Scene Setup ", padding=10)
        card_scene.pack(fill="x", pady=(0, 8))

        grid_s = ttk.Frame(card_scene)
        grid_s.pack(fill="x")

        ttk.Label(grid_s, text="Backplate Material:").grid(row=0, column=0, sticky="w", pady=4)
        back_mats = ["gloss:black", "gloss:white", "chrome", "gold", "gloss:red"]
        combo_bkmat = ttk.Combobox(grid_s, textvariable=self.var_material_back, values=back_mats, width=20)
        combo_bkmat.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_bkmat.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_s, text="Studio Lighting:").grid(row=1, column=0, sticky="w", pady=4)
        combo_light = ttk.Combobox(
            grid_s,
            textvariable=self.var_lighting,
            values=["studio", "dramatic", "warm", "sunset"],
            width=20,
            state="readonly"
        )
        combo_light.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_light.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_s, text="Render Engine:").grid(row=2, column=0, sticky="w", pady=4)
        combo_eng = ttk.Combobox(
            grid_s,
            textvariable=self.var_engine,
            values=["eevee", "cycles"],
            width=20,
            state="readonly"
        )
        combo_eng.grid(row=2, column=1, sticky="w", padx=(6, 0), pady=4)
        combo_eng.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(grid_s, text="Preview Angle:").grid(row=3, column=0, sticky="w", pady=4)
        combo_pangle = ttk.Combobox(
            grid_s,
            textvariable=self.var_preview_angle,
            values=["angled", "front", "back"],
            width=20,
            state="readonly"
        )
        combo_pangle.grid(row=3, column=1, sticky="w", padx=(6, 0), pady=4)

        ttk.Checkbutton(
            card_scene,
            text="Generate 360° Turntable Video (--animate)",
            variable=self.var_animate,
            command=self._update_command_preview
        ).pack(anchor="w", pady=(6, 2))

        ttk.Checkbutton(
            card_scene,
            text="Save .blend Scene in Project (--save-blend)",
            variable=self.var_save_blend,
            command=self._update_command_preview
        ).pack(anchor="w", pady=(0, 2))

        # Right Column: Visual Preview Canvas & Actions
        card_prev = ttk.LabelFrame(right_col, text=" Project Visual Preview ", padding=10)
        card_prev.pack(fill="both", expand=True)

        self.lbl_preview_canvas = tk.Label(
            card_prev,
            text="No preview rendered yet.\nClick '⚡ Quick Preview' to render.",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        self.lbl_preview_canvas.pack(fill="both", expand=True, pady=(0, 8))
        self.lbl_preview_canvas.bind("<Button-1>", lambda e: self._open_popout_preview())

        btn_row = ttk.Frame(card_prev)
        btn_row.pack(fill="x", pady=(0, 4))

        btn_quick = ttk.Button(
            btn_row,
            text="⚡  Quick Preview (2s)",
            style="Primary.TButton",
            command=self._action_quick_preview
        )
        btn_quick.pack(side="left", fill="x", expand=True, padx=(0, 3))

        btn_popout = ttk.Button(
            btn_row,
            text="🔍  Pop-Out (100% Size)",
            command=self._open_popout_preview
        )
        btn_popout.pack(side="left", fill="x", expand=True, padx=3)

        btn_full = ttk.Button(
            btn_row,
            text="🎨  Full Studio Set",
            command=self._action_full_render
        )
        btn_full.pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.lbl_prev_info = ttk.Label(
            card_prev,
            text="Fast Preview: EEVEE (50% Res, 16 samples) | Click preview image to pop out",
            foreground="#64748b"
        )
        self.lbl_prev_info.pack(anchor="center")

    def _action_quick_preview(self):
        """Runs fast background preview render and updates live image on completion."""
        self._action_save_project()

        def do_render(force_uncut=False):
            angle = self.var_preview_angle.get().strip() or "angled"
            cmd = [
                sys.executable,
                "guitar_builder.py",
                "--project", self.active_project_dir,
                "--preview",
                "--angle", angle
            ]
            mode = self.var_presentation_mode.get()
            if force_uncut or mode == "uncut":
                cmd.append("--uncut")
            elif mode == "exploded":
                cmd.append("--exploded-body")
            else:
                cmd.append("--sliced")

            mat = self.var_material.get().strip()
            if mat:
                cmd.extend(["--material", mat])

            seed_str = self.var_seed.get().strip()
            if seed_str:
                cmd.extend(["--seed", seed_str])

            self._start_subprocess(cmd, f"Rendering Quick Preview ({angle} view)...", on_success=self._load_project_preview_image)

        self._check_and_prompt_slicing(do_render, is_preview=True)

    def _action_full_render(self):
        """Runs full production studio render for active project."""
        self._action_save_project()

        def do_render(force_uncut=False):
            cmd = [
                sys.executable,
                "guitar_builder.py",
                "--project", self.active_project_dir,
                "--render",
                "--angle", "all"
            ]
            mode = self.var_presentation_mode.get()
            if force_uncut or mode == "uncut":
                cmd.append("--uncut")
            elif mode == "exploded":
                cmd.append("--exploded-body")
            else:
                cmd.append("--sliced")
            if self.var_animate.get():
                cmd.append("--animate")
            if self.var_save_blend.get():
                cmd.append("--save-blend")

            mat = self.var_material.get().strip()
            if mat:
                cmd.extend(["--material", mat])

            seed_str = self.var_seed.get().strip()
            if seed_str:
                cmd.extend(["--seed", seed_str])

            self._start_subprocess(cmd, "Rendering Production Studio Set...", on_success=self._load_project_preview_image)

        self._check_and_prompt_slicing(do_render, is_preview=False)

    def _check_and_prompt_slicing(self, on_ready, is_preview=True):
        """Checks if slicing is needed before rendering based on presentation mode.
        If sliced presentation is active and slices are missing or dirty, prompts user.
        For previews: uses fast straight cuts without pins (unless textured cuts already exist!).
        For production: uses the full configured cuts.
        """
        mode = self.var_presentation_mode.get()
        if mode in ["sliced", "exploded"]:
            status = self.project_manager.get_slice_status(self.active_project_dir, self.active_project_data, for_preview=is_preview)
            if status != "clean":
                reason = "have not been generated yet" if status == "missing" else "need to be remade because geometry/hardware settings changed"
                action_text = "make quick straight cuts (~10s)" if is_preview else "generate full 3D print cuts (~1-2 mins)"
                msg = (
                    f"The 3D sliced body parts {reason}.\n\n"
                    f"• Click 'YES' to {action_text} and render multi-section cuts.\n"
                    f"• Click 'NO' to preview as a seamless uncut body immediately (~5-10s).\n"
                    f"• Click 'CANCEL' to abort."
                )
                ans = messagebox.askyesnocancel("Body Slicing Choice", msg, parent=self.root)
                if ans is True:
                    cut_type = "flat" if is_preview else None
                    no_pins = True if is_preview else None
                    self._action_slice_body(cut_type=cut_type, no_pins=no_pins, on_success=on_ready)
                    return
                elif ans is False:
                    on_ready(force_uncut=True)
                    return
                else:
                    return

        on_ready(force_uncut=(mode == "uncut"))

    def _action_slice_body(self, cut_type=None, no_pins=None, on_success=None):
        """Runs dedicated physical slicing of body parts and updates slice signature."""
        self._action_save_project()
        cmd = [
            sys.executable,
            "guitar_builder.py",
            "--project", self.active_project_dir,
            "--slice-only"
        ]
        if cut_type:
            cmd.extend(["--cut-type", cut_type])
        if no_pins:
            cmd.append("--no-pins")

        def _after_slice():
            self._update_slice_status_badge()
            if on_success:
                on_success()
        desc = "Fast Straight-Cut Slicing..." if cut_type == "flat" else "Slicing 3D Body Parts for Project..."
        self._start_subprocess(cmd, desc, on_success=_after_slice)

    def _update_slice_status_badge(self):
        if not self.active_project_dir:
            return
        status_preview = self.project_manager.get_slice_status(self.active_project_dir, self.active_project_data, for_preview=True)
        status_prod = self.project_manager.get_slice_status(self.active_project_dir, self.active_project_data, for_preview=False)

        if status_prod == "clean":
            text = "● Slices: Up-to-Date (Production)"
            fg = "#16a34a"
        elif status_preview == "clean":
            text = "● Slices: Up-to-Date (Preview)"
            fg = "#16a34a"
        elif status_preview == "dirty" or status_prod == "dirty":
            text = "● Slices: Geometry Changed (Needs Cut)"
            fg = "#d97706"
        else:
            text = "○ Slices: Not Sliced (Uncut)"
            fg = "#64748b"

        for attr in ["lbl_slice_status", "lbl_slice_status_tab2", "lbl_slice_status_tab3"]:
            lbl = getattr(self, attr, None)
            if lbl:
                try:
                    lbl.configure(text=text, foreground=fg)
                except Exception:
                    pass

    def _roll_random_seed(self):
        import random
        new_seed = random.randint(1000, 999999)
        self.var_seed.set(str(new_seed))
        self._update_command_preview()

    def _on_finish_mode_change(self):
        mode = self.var_finish_mode.get()
        if mode == "random_parts":
            style = self.var_random_style.get() or "gloss:random"
            self.var_material.set(style)
            self.var_presentation_mode.set("sliced")
            if not self.var_seed.get().strip():
                import random
                self.var_seed.set(str(random.randint(1000, 999999)))
            if hasattr(self, "frame_uniform_finish"):
                self.frame_uniform_finish.pack_forget()
            if hasattr(self, "frame_random_finish"):
                self.frame_random_finish.pack(fill="x", pady=4)
        else:
            current_mat = self.var_material.get()
            if "random" in current_mat:
                self.var_material.set("sunburst")
            if hasattr(self, "frame_random_finish"):
                self.frame_random_finish.pack_forget()
            if hasattr(self, "frame_uniform_finish"):
                self.frame_uniform_finish.pack(fill="x", pady=4)
        self._update_command_preview()

    def _on_random_style_selected(self):
        self.var_material.set(self.var_random_style.get())
        self._update_command_preview()

    def _on_presentation_mode_change(self, *args):
        self._update_command_preview()

    def _load_project_preview_image(self):
        """Loads and scales preview.png into the preview canvas."""
        if not self.active_project_dir:
            return
        renders_dir = os.path.join(self.active_project_dir, "renders")
        preview_path = os.path.join(renders_dir, "preview.png")

        # Fallback to any png if preview.png doesn't exist
        if not os.path.exists(preview_path):
            candidates = [os.path.join(renders_dir, f) for f in os.listdir(renders_dir) if f.lower().endswith(".png")] if os.path.exists(renders_dir) else []
            preview_path = candidates[0] if candidates else None

        self.active_preview_path = preview_path

        if preview_path and os.path.exists(preview_path):
            try:
                import base64
                with open(preview_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("ascii")
                raw_img = tk.PhotoImage(data=b64_data)
                # Generous width (~640px) so the preview fills the right pane
                sub_factor = max(1, raw_img.width() // 640)
                sub_img = raw_img.subsample(sub_factor, sub_factor)
                self._cached_preview_img = sub_img
                self.lbl_preview_canvas.configure(image=sub_img, text="", width=sub_img.width(), height=sub_img.height())
                self.lbl_prev_info.configure(text=f"Preview: {os.path.basename(preview_path)} ({raw_img.width()}×{raw_img.height()}) • Click to pop out")
            except Exception as e:
                print(f"Error loading preview image: {e}")

    def _open_popout_preview(self):
        """Opens a pop-out window showing the render at full 100% actual size with scrollbars."""
        preview_path = getattr(self, "active_preview_path", None)
        if not preview_path or not os.path.exists(preview_path):
            if self.active_project_dir:
                p = os.path.join(self.active_project_dir, "renders", "preview.png")
                if os.path.exists(p):
                    preview_path = p
                    self.active_preview_path = p

        if not preview_path or not os.path.exists(preview_path):
            messagebox.showinfo("No Preview", "No preview image has been rendered yet. Click '⚡ Quick Preview' first.")
            return

        pop = tk.Toplevel(self.root)
        pop.title(f"Preview - {self.active_project_name.get()} (Actual Size)")

        try:
            import base64
            with open(preview_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("ascii")
            full_img = tk.PhotoImage(data=b64_data)
            w = full_img.width()
            h = full_img.height()
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            win_w = min(w + 30, int(screen_w * 0.9))
            win_h = min(h + 80, int(screen_h * 0.9))
            pop.geometry(f"{win_w}x{win_h}")

            # Top toolbar
            bar = ttk.Frame(pop, padding=6)
            bar.pack(fill="x")
            ttk.Label(bar, text=f"File: {os.path.basename(preview_path)} | Native: {w} × {h} px", font=("Segoe UI", 9, "bold")).pack(side="left", padx=6)
            ttk.Button(bar, text="📁 Open in System Viewer", command=lambda: self._open_file(preview_path)).pack(side="right", padx=4)
            ttk.Button(bar, text="Close", command=pop.destroy).pack(side="right")

            # Scrollable canvas for full image
            canvas_frame = ttk.Frame(pop)
            canvas_frame.pack(fill="both", expand=True)

            canvas = tk.Canvas(canvas_frame, bg="#0f172a", scrollregion=(0, 0, w, h))
            v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
            canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

            canvas.grid(row=0, column=0, sticky="nsew")
            v_scroll.grid(row=0, column=1, sticky="ns")
            h_scroll.grid(row=1, column=0, sticky="ew")

            canvas_frame.rowconfigure(0, weight=1)
            canvas_frame.columnconfigure(0, weight=1)

            canvas.create_image(w // 2, h // 2, image=full_img)
            pop._img_ref = full_img

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image in pop-out: {e}")

    # =========================================================================
    # TAB 3: Slicing & 3D Print
    # =========================================================================
    def _build_tab_slicing(self):
        scroll = ScrollableFrame(self.tab_slicing)
        scroll.pack(fill="both", expand=True)
        container = scroll.scrollable_content

        # Card 1: Slicing Seam & Pins
        card_cut = ttk.LabelFrame(container, text=" Slicing Joint & Alignment Pins ", padding=10)
        card_cut.pack(fill="x", pady=(0, 8))

        grid_cut = ttk.Frame(card_cut)
        grid_cut.pack(fill="x")

        ttk.Label(grid_cut, text="Joint Slicing Method:").grid(row=0, column=0, sticky="w", pady=4)
        combo_cut = ttk.Combobox(
            grid_cut,
            textvariable=self.var_cut_type,
            values=["textured", "flat"],
            width=18,
            state="readonly"
        )
        combo_cut.grid(row=0, column=1, sticky="w", padx=(6, 20), pady=4)
        combo_cut.bind("<<ComboboxSelected>>", self._on_geometry_setting_changed)

        ttk.Checkbutton(
            grid_cut,
            text="Enable Locator Pins",
            variable=self.var_enable_pins,
            command=self._on_geometry_setting_changed
        ).grid(row=0, column=2, sticky="w", padx=(0, 20), pady=4)

        ttk.Label(grid_cut, text="Pin Diameter (mm):").grid(row=1, column=0, sticky="w", pady=4)
        combo_pind = ttk.Combobox(
            grid_cut,
            textvariable=self.var_pin_diameter,
            values=[6.0, 5.0, 4.0, 8.0],
            width=18,
            state="readonly"
        )
        combo_pind.grid(row=1, column=1, sticky="w", padx=(6, 20), pady=4)
        combo_pind.bind("<<ComboboxSelected>>", self._on_geometry_setting_changed)

        ttk.Label(grid_cut, text="Pin Length (mm):").grid(row=1, column=2, sticky="w", pady=4)
        combo_pinl = ttk.Combobox(
            grid_cut,
            textvariable=self.var_pin_length,
            values=[16.0, 12.0, 20.0, 24.0],
            width=14,
            state="readonly"
        )
        combo_pinl.grid(row=1, column=3, sticky="w", padx=(6, 0), pady=4)
        combo_pinl.bind("<<ComboboxSelected>>", self._on_geometry_setting_changed)

        lbl_pin_info = ttk.Label(
            card_cut,
            text="ℹ Pin holes feature tapered end chamfers and fractional depth clearance for tight seamless mating.",
            foreground="#64748b"
        )
        lbl_pin_info.pack(anchor="w", pady=(6, 0))

        # Card 2: Print Manifest & Generate Action
        card_act = ttk.LabelFrame(container, text=" 3D Print Manifest & STL Generation ", padding=12)
        card_act.pack(fill="x")

        box_manifest = ttk.Frame(card_act, relief="solid", borderwidth=1, padding=8)
        box_manifest.pack(fill="x", pady=(0, 10))

        row_mf_header = ttk.Frame(box_manifest)
        row_mf_header.pack(fill="x", pady=(0, 4))
        ttk.Label(row_mf_header, text="Output Directory: projects/<project>/stl/", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.lbl_slice_status_tab3 = ttk.Label(row_mf_header, text="○ Slices: Unknown", font=("Segoe UI", 9, "bold"))
        self.lbl_slice_status_tab3.pack(side="right")

        ttk.Label(box_manifest, text="• Body Parts: 8 sliced sections (Guitar_Bot_Left.stl ... Guitar_Top_Right.stl)").pack(anchor="w", padx=(8, 0))
        ttk.Label(box_manifest, text="• Hardware & Electronics: Backplate.stl & Elec_Backplate.stl").pack(anchor="w", padx=(8, 0))
        ttk.Label(box_manifest, text="• Locator Pins: 4x 6mm tapered alignment pins").pack(anchor="w", padx=(8, 0))
        ttk.Label(box_manifest, text="• Neck Components: Modular neck shaft, fretboard, frets, nut, and tuners").pack(anchor="w", padx=(8, 0))

        btn_gen = ttk.Button(
            card_act,
            text="⚡  Generate All 3D Print STLs",
            style="Action.TButton",
            command=self._action_generate_stls
        )
        btn_gen.pack(fill="x", ipady=4, pady=(0, 6))

        btn_open_stl = ttk.Button(
            card_act,
            text="📁  Open STLs Folder in Explorer",
            command=self._open_stl_folder
        )
        btn_open_stl.pack(fill="x")

    def _action_generate_stls(self):
        """Runs complete STL generation pipeline for active project."""
        self._action_save_project()
        cmd = [
            sys.executable,
            "guitar_builder.py",
            "--project", self.active_project_dir,
            "--generate"
        ]
        if self.var_no_cut.get():
            cmd.append("--no-cut")
        else:
            cmd.extend(["--cut-type", self.var_cut_type.get()])
            if not self.var_enable_pins.get():
                cmd.append("--no-pins")
            else:
                cmd.extend(["--pin-diameter", str(self.var_pin_diameter.get()), "--pin-length", str(self.var_pin_length.get())])

        self._start_subprocess(cmd, "Generating All 3D Printable STLs for Project...", on_success=self._update_slice_status_badge)

    def _open_stl_folder(self):
        if self.active_project_dir:
            stl_dir = os.path.join(self.active_project_dir, "stl")
            self._open_folder(stl_dir)

    # =========================================================================
    # TAB 4: Project Gallery
    # =========================================================================
    def _build_tab_gallery(self):
        scroll = ScrollableFrame(self.tab_gallery)
        scroll.pack(fill="both", expand=True)
        container = scroll.scrollable_content

        bar = ttk.Frame(container)
        bar.pack(fill="x", pady=(0, 8))

        ttk.Button(bar, text="↻ Refresh Gallery", command=self._refresh_gallery).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="📁 Open Renders Folder", command=self._open_project_renders_folder).pack(side="left")

        self.gallery_frame = ttk.Frame(container)
        self.gallery_frame.pack(fill="both", expand=True)

    def _refresh_gallery(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.gallery_images.clear()

        if not self.active_project_dir:
            return

        renders_dir = os.path.join(self.active_project_dir, "renders")
        if not os.path.exists(renders_dir):
            ttk.Label(self.gallery_frame, text=f"No renders folder found for this project.", foreground="#64748b").pack(pady=20)
            return

        png_files = [f for f in sorted(os.listdir(renders_dir)) if f.lower().endswith(".png")]
        if not png_files:
            ttk.Label(self.gallery_frame, text="No render images generated yet.\nUse Step 2 (Visuals & Finish) to render.", foreground="#64748b").pack(pady=20)
            return

        grid_box = ttk.Frame(self.gallery_frame)
        grid_box.pack(fill="both", expand=True)

        col = 0
        row = 0
        for png in png_files:
            full_path = os.path.join(renders_dir, png)
            try:
                raw_img = tk.PhotoImage(file=full_path)
                sub_factor = max(1, raw_img.width() // 320)
                thumb = raw_img.subsample(sub_factor, sub_factor)
                self.gallery_images.append(thumb)

                card = ttk.Frame(grid_box, relief="solid", borderwidth=1, padding=6)
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
                print(f"Error loading gallery thumbnail: {e}")

    # =========================================================================
    # Console / Log Area
    # =========================================================================
    def _build_console_area(self, parent=None):
        target_parent = parent if parent is not None else self.root
        console_container = ttk.Frame(target_parent, padding=(0, 1, 0, 2))
        console_container.pack(fill="both", expand=True)

        header_bar = ttk.Frame(console_container)
        header_bar.pack(fill="x", pady=(0, 2))

        self.lbl_status = ttk.Label(header_bar, text="Status: Ready", font=("Segoe UI", 9, "bold"), foreground="#0f172a")
        self.lbl_status.pack(side="left")

        self.btn_cancel = ttk.Button(header_bar, text="⏹ Stop Process", style="Danger.TButton", state="disabled", command=self._cancel_process)
        self.btn_cancel.pack(side="right", padx=(4, 0))

        ttk.Button(header_bar, text="Clear Log", command=self._clear_log).pack(side="right", padx=(4, 0))

        self.console_collapsed = False
        self.btn_toggle_console = ttk.Button(header_bar, text="▾ Minimize", width=11, command=self._toggle_console)
        self.btn_toggle_console.pack(side="right")

        self.console_body = ttk.Frame(console_container)
        self.console_body.pack(fill="both", expand=True)

        self.txt_console = tk.Text(
            self.console_body,
            height=4,
            bg="#0f172a",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            font=("Consolas", 9),
            wrap="word",
            relief="flat",
            padx=8,
            pady=3
        )
        scroll = ttk.Scrollbar(self.console_body, orient="vertical", command=self.txt_console.yview)
        self.txt_console.configure(yscrollcommand=scroll.set)

        self.txt_console.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _toggle_console(self):
        if self.console_collapsed:
            self.console_body.pack(fill="both", expand=True)
            self.btn_toggle_console.configure(text="▾ Minimize")
            self.console_collapsed = False
        else:
            self.console_body.pack_forget()
            self.btn_toggle_console.configure(text="▴ Expand Log")
            self.console_collapsed = True

    # =========================================================================
    # Project Management Methods
    # =========================================================================
    def _init_projects(self):
        """Discovers existing projects or creates a default project."""
        models = self.project_manager.get_body_models()
        self.combo_body_model["values"] = models

        # Scan hardware variants
        hw_base = os.path.join(self.repo_dir, "models", "scad", "hardware")
        hw_variants = [d for d in sorted(os.listdir(hw_base)) if os.path.isdir(os.path.join(hw_base, d))] if os.path.exists(hw_base) else ["standard", "piezo"]
        self.combo_hardware["values"] = hw_variants

        # Scan electronics variants
        elec_base = os.path.join(self.repo_dir, "models", "scad", "electronics")
        elec_variants = ["auto"]
        if os.path.exists(elec_base):
            elec_variants += [d for d in sorted(os.listdir(elec_base)) if os.path.isdir(os.path.join(elec_base, d))]
        else:
            elec_variants += ["sarcaster", "flying_v", "les_paul"]
        self.combo_electronics["values"] = elec_variants

        projects = self.project_manager.list_projects()
        if not projects:
            pdir, pdata = self.project_manager.create_project("Default_Sarcaster", "sarcaster")
            projects = [os.path.basename(pdir)]

        self.combo_project["values"] = projects
        self.combo_project.set(projects[0])
        self._load_project(projects[0])

    def _on_project_selected(self, event=None):
        name = self.active_project_name.get().strip()
        if name:
            self._load_project(name)

    def _load_project(self, name_or_path):
        """Loads a project and updates all GUI fields."""
        try:
            self.active_project_dir = self.project_manager.resolve_project_dir(name_or_path)
            self.active_project_data = self.project_manager.load_project(self.active_project_dir)
            self.active_project_name.set(os.path.basename(self.active_project_dir))

            # 1. Spec
            body_model = self.active_project_data.get("body_model", "sarcaster")
            self.var_body_model.set(body_model)
            dims = self.active_project_data.get("body_dimensions", {})
            self._populate_dims_table(dims)

            neck = self.active_project_data.get("neck", {})
            self.var_neck.set(neck.get("style", "auto"))
            self.var_neck_material.set(neck.get("shaft_material", "maple"))
            self.var_fretboard_material.set(neck.get("fretboard_material", "rosewood"))
            self.var_tuner_finish.set(neck.get("tuner_finish", "chrome"))

            hw = self.active_project_data.get("hardware", {})
            self.var_hardware.set(hw.get("variant", "standard"))
            self.var_electronics.set(hw.get("electronics", "auto"))

            # 2. Visuals
            vis = self.active_project_data.get("visuals", {})
            bmat = vis.get("body_material", "sunburst")
            self.var_material.set(bmat)
            self.var_presentation_mode.set(vis.get("presentation_mode", "sliced"))
            if "random" in bmat.lower():
                self.var_finish_mode.set("random_parts")
                if bmat.lower() in ["gloss:random", "matte:random", "sparkle:random", "chrome:random", "glass:random", "random"]:
                    self.var_random_style.set(bmat.lower())
                else:
                    self.var_random_style.set("gloss:random")
                if hasattr(self, "frame_uniform_finish"):
                    self.frame_uniform_finish.pack_forget()
                if hasattr(self, "frame_random_finish"):
                    self.frame_random_finish.pack(fill="x", pady=4)
            else:
                self.var_finish_mode.set("uniform")
                if hasattr(self, "frame_random_finish"):
                    self.frame_random_finish.pack_forget()
                if hasattr(self, "frame_uniform_finish"):
                    self.frame_uniform_finish.pack(fill="x", pady=4)

            self.var_material_back.set(vis.get("backplate_material", "gloss:black"))
            self.var_lighting.set(vis.get("lighting", "studio"))
            self.var_engine.set(vis.get("engine", "eevee"))
            self.var_preview_angle.set(vis.get("angle", "angled"))
            self.var_animate.set(vis.get("animate", False))
            self.var_dynamic_zoom.set(vis.get("dynamic_zoom", True))
            seed = vis.get("seed", "")
            self.var_seed.set(str(seed) if seed is not None else "")

            # 3. Slicing
            sl = self.active_project_data.get("slicing", {})
            self.var_cut_type.set(sl.get("cut_type", "textured"))
            self.var_enable_pins.set(not sl.get("no_pins", False))
            self.var_pin_diameter.set(float(sl.get("pin_diameter", 6.0)))
            self.var_pin_length.set(float(sl.get("pin_length", 16.0)))
            self.var_no_cut.set(sl.get("no_cut", False))

            self._update_command_preview()
            self._update_slice_status_badge()
            self._load_project_preview_image()
            self._refresh_gallery()
            self.lbl_status.configure(text=f"Loaded Project: {self.active_project_name.get()}", foreground="#0f172a")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def _populate_dims_table(self, dims):
        for item in self.param_tree.get_children():
            self.param_tree.delete(item)
        for k, v in dims.items():
            self.param_tree.insert("", "end", values=(k, v))

    def _action_save_project(self):
        """Pulls current GUI variables into active_project_data and saves project.json."""
        if not self.active_project_dir:
            return

        self.active_project_data["body_model"] = self.var_body_model.get().strip()

        # Neck
        self.active_project_data["neck"] = {
            "style": self.var_neck.get().strip(),
            "shaft_material": self.var_neck_material.get().strip(),
            "fretboard_material": self.var_fretboard_material.get().strip(),
            "tuner_finish": self.var_tuner_finish.get().strip()
        }

        # Hardware
        self.active_project_data["hardware"] = {
            "variant": self.var_hardware.get().strip(),
            "electronics": self.var_electronics.get().strip()
        }

        # Visuals
        seed_str = self.var_seed.get().strip()
        try:
            seed_val = int(seed_str) if seed_str else None
        except ValueError:
            seed_val = None

        self.active_project_data["visuals"] = {
            "presentation_mode": self.var_presentation_mode.get().strip(),
            "body_material": self.var_material.get().strip(),
            "backplate_material": self.var_material_back.get().strip(),
            "lighting": self.var_lighting.get().strip(),
            "engine": self.var_engine.get().strip(),
            "angle": self.var_preview_angle.get().strip(),
            "animate": self.var_animate.get(),
            "dynamic_zoom": self.var_dynamic_zoom.get(),
            "seed": seed_val
        }

        # Slicing
        self.active_project_data["slicing"] = {
            "cut_type": self.var_cut_type.get().strip(),
            "pin_diameter": self.var_pin_diameter.get(),
            "pin_length": self.var_pin_length.get(),
            "no_pins": not self.var_enable_pins.get(),
            "no_cut": self.var_no_cut.get()
        }

        try:
            self.project_manager.save_project(self.active_project_dir, self.active_project_data)
            self._update_slice_status_badge()
            self.lbl_status.configure(text=f"Project Saved: {self.active_project_name.get()}", foreground="#16a34a")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {e}")

    def _action_new_project(self):
        """Opens modal dialog to create a new project."""
        dlg = tk.Toplevel(self.root)
        dlg.title("New Guitar Project")
        dlg.geometry("380x200")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text="Create New Guitar Project", font=("Segoe UI", 11, "bold")).pack(pady=(14, 12))

        f = ttk.Frame(dlg, padding=12)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Project Name:").grid(row=0, column=0, sticky="w", pady=6)
        ent_name = ttk.Entry(f, width=22)
        ent_name.insert(0, "My_Guitar")
        ent_name.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=6)
        ent_name.focus()

        ttk.Label(f, text="Base Body Style:").grid(row=1, column=0, sticky="w", pady=6)
        combo_b = ttk.Combobox(f, values=self.project_manager.get_body_models(), width=20, state="readonly")
        combo_b.set("sarcaster")
        combo_b.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=6)

        def on_create():
            name = ent_name.get().strip()
            if not name:
                messagebox.showwarning("Name Required", "Please enter a valid project name.")
                return
            body_model = combo_b.get().strip()
            pdir, pdata = self.project_manager.create_project(name, body_model)
            dlg.destroy()

            # Refresh list
            projects = self.project_manager.list_projects()
            self.combo_project["values"] = projects
            safe_name = os.path.basename(pdir)
            self.combo_project.set(safe_name)
            self._load_project(safe_name)

        btn_box = ttk.Frame(dlg, padding=10)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Create Project", style="Primary.TButton", command=on_create).pack(side="right", padx=(4, 0))
        ttk.Button(btn_box, text="Cancel", command=dlg.destroy).pack(side="right")

    def _action_save_project_as(self):
        """Duplicates current project with a new name."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Save Project As")
        dlg.geometry("360x160")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text="Duplicate Project As New Variant", font=("Segoe UI", 10, "bold")).pack(pady=(14, 10))
        f = ttk.Frame(dlg, padding=12)
        f.pack(fill="x")

        ttk.Label(f, text="New Project Name:").pack(side="left", padx=(0, 6))
        ent = ttk.Entry(f, width=22)
        ent.insert(0, f"{self.active_project_name.get()}_copy")
        ent.pack(side="left")
        ent.focus()

        def on_duplicate():
            new_name = ent.get().strip()
            if not new_name:
                return
            new_dir, new_data = self.project_manager.duplicate_project(self.active_project_dir, new_name)
            dlg.destroy()
            projects = self.project_manager.list_projects()
            self.combo_project["values"] = projects
            safe_name = os.path.basename(new_dir)
            self.combo_project.set(safe_name)
            self._load_project(safe_name)

        btn_box = ttk.Frame(dlg, padding=10)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Duplicate", style="Primary.TButton", command=on_duplicate).pack(side="right", padx=(4, 0))
        ttk.Button(btn_box, text="Cancel", command=dlg.destroy).pack(side="right")

    def _on_body_model_selected(self, event=None):
        model = self.var_body_model.get().strip()
        dims = self.project_manager.get_default_body_dimensions(model)
        self.active_project_data["body_model"] = model
        self.active_project_data["body_dimensions"] = dims
        self._populate_dims_table(dims)

        # Auto-recommend neck style
        if "strat" in model or "sarcaster" in model:
            self.var_neck.set("strat")
            self.var_electronics.set("sarcaster")
        elif "les_paul" in model or "sg" in model or "single_cut" in model:
            self.var_neck.set("les_paul")
            self.var_electronics.set("les_paul")
        elif "flying_v" in model or "sarcy_v" in model:
            self.var_electronics.set("flying_v")

        self._update_slice_status_badge()
        self._update_command_preview()

    def _on_geometry_setting_changed(self, event=None):
        self._update_command_preview()
        self._update_slice_status_badge()

    # =========================================================================
    # Subprocess Execution & Command Preview
    # =========================================================================
    def _update_command_preview(self):
        """Construct the exact CLI argument string based on active options."""
        proj = self.active_project_dir or self.active_project_name.get()
        cmd = [sys.executable, "guitar_builder.py", "--project", proj]
        mode = self.var_presentation_mode.get()
        if mode == "uncut":
            cmd.append("--uncut")
        elif mode == "exploded":
            cmd.append("--exploded-body")
        else:
            cmd.append("--sliced")

        mat = self.var_material.get().strip()
        if mat and mat != "sunburst":
            cmd.extend(["--material", mat])

        seed = self.var_seed.get().strip()
        if seed:
            cmd.extend(["--seed", seed])

        self.var_cmd_preview.set(" ".join(cmd))
        return cmd

    def _copy_command_preview(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.var_cmd_preview.get())
        messagebox.showinfo("Copied", "Command line copied to clipboard!")

    def _start_subprocess(self, cmd, description, on_success=None):
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
                    self.root.after(0, lambda: self._on_process_complete(True, on_success))
                else:
                    self.log_queue.put(f"\n[ERROR] Process finished with error code {returncode} (in {elapsed:.1f}s).\n")
                    self.root.after(0, lambda: self._on_process_complete(False, None))

            except Exception as e:
                self.log_queue.put(f"\n[CRITICAL ERROR] Failed to launch process: {e}\n")
                self.root.after(0, lambda: self._on_process_complete(False, None))
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

    def _on_process_complete(self, success, callback=None):
        self.is_running = False
        self.btn_cancel.configure(state="disabled")
        status_text = "Status: Completed Successfully" if success else "Status: Failed / Finished with errors"
        status_color = "#16a34a" if success else "#dc2626"
        self.lbl_status.configure(text=status_text, foreground=status_color)
        if success and callback:
            callback()
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
    # Folder & File Helpers
    # =========================================================================
    def _open_project_folder(self):
        if self.active_project_dir:
            self._open_folder(self.active_project_dir)

    def _open_project_renders_folder(self):
        if self.active_project_dir:
            self._open_folder(os.path.join(self.active_project_dir, "renders"))

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
