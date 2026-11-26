extends Node3D

@onready var body_mesh = $GuitarBodyMesh
@onready var hardware_rig = $HardwareRig
@onready var camera_pivot = $CameraPivot
@onready var camera = $CameraPivot/Camera3D

# Camera View Buttons
@onready var btn_orbit = $UI/Panel/Scroll/VBox/ViewButtons/BtnOrbit
@onready var btn_front = $UI/Panel/Scroll/VBox/ViewButtons/BtnFront
@onready var btn_back = $UI/Panel/Scroll/VBox/ViewButtons/BtnBack
@onready var btn_side = $UI/Panel/Scroll/VBox/ViewButtons/BtnSide

# Global UI Sliders
@onready var slider_length = $UI/Panel/Scroll/VBox/GridGlobal/SliderLength
@onready var slider_thickness = $UI/Panel/Scroll/VBox/GridGlobal/SliderThickness
@onready var slider_radius = $UI/Panel/Scroll/VBox/GridGlobal/SliderRadius

# Symmetry
@onready var check_symmetric = $UI/Panel/Scroll/VBox/CheckSymmetric
@onready var symmetric_controls = $UI/Panel/Scroll/VBox/SymmetricControls
@onready var asymmetric_controls = $UI/Panel/Scroll/VBox/AsymmetricControls

# Symmetric Sliders
@onready var slider_hip = $UI/Panel/Scroll/VBox/SymmetricControls/SliderHip
@onready var slider_waist = $UI/Panel/Scroll/VBox/SymmetricControls/SliderWaist
@onready var slider_chest = $UI/Panel/Scroll/VBox/SymmetricControls/SliderChest
@onready var slider_shoulder = $UI/Panel/Scroll/VBox/SymmetricControls/SliderShoulder
@onready var slider_horn_reach = $UI/Panel/Scroll/VBox/SymmetricControls/SliderHornReach
@onready var slider_horn_roundness = $UI/Panel/Scroll/VBox/SymmetricControls/SliderHornRoundness

# Asymmetric Treble Sliders
@onready var slider_t_hip = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleHip
@onready var slider_t_waist = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleWaist
@onready var slider_t_chest = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleChest
@onready var slider_t_horn = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleHorn
@onready var slider_t_roundness = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleRoundness

# Asymmetric Bass Sliders
@onready var slider_b_hip = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassHip
@onready var slider_b_waist = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassWaist
@onready var slider_b_chest = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassChest
@onready var slider_b_horn = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassHorn
@onready var slider_b_roundness = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassRoundness

# Ergonomic Cuts
@onready var check_belly = $UI/Panel/Scroll/VBox/CheckBellyCut
@onready var belly_controls = $UI/Panel/Scroll/VBox/BellyControls
@onready var slider_belly_angle = $UI/Panel/Scroll/VBox/BellyControls/SliderBellyAngle
@onready var slider_belly_length = $UI/Panel/Scroll/VBox/BellyControls/SliderBellyLength

@onready var check_forearm = $UI/Panel/Scroll/VBox/CheckForearm
@onready var forearm_controls = $UI/Panel/Scroll/VBox/ForearmControls
@onready var slider_forearm_angle = $UI/Panel/Scroll/VBox/ForearmControls/SliderForearmAngle
@onready var slider_forearm_length = $UI/Panel/Scroll/VBox/ForearmControls/SliderForearmLength

# Hardware & Cavity Controls
@onready var option_pickups = $UI/Panel/Scroll/VBox/GridHardware/OptionPickups
@onready var option_bridge = $UI/Panel/Scroll/VBox/GridHardware/OptionBridge
@onready var slider_bridge_y = $UI/Panel/Scroll/VBox/GridHardware/SliderBridgeY
@onready var slider_bridge_slant = $UI/Panel/Scroll/VBox/GridHardware/SliderBridgeSlant
@onready var slider_clearance = $UI/Panel/Scroll/VBox/GridHardware/SliderClearance
@onready var slider_cavity_depth = $UI/Panel/Scroll/VBox/GridHardware/SliderCavityDepth
@onready var check_neck_pocket = $UI/Panel/Scroll/VBox/CheckNeckPocket
@onready var check_control_cavity = $UI/Panel/Scroll/VBox/CheckControlCavity
@onready var check_hardware_models = $UI/Panel/Scroll/VBox/CheckHardwareModels
@onready var check_neck = $UI/Panel/Scroll/VBox/CheckNeck
@onready var check_piezo = $UI/Panel/Scroll/VBox/CheckPiezo

# Phase 5: Body Shape Presets & Procedural Modifiers
@onready var lbl_shape_preset = $UI/Panel/Scroll/VBox/LblShapePreset
@onready var option_shape_preset = $UI/Panel/Scroll/VBox/OptionShapePreset
@onready var hsep_modifiers = $UI/Panel/Scroll/VBox/HSeparatorModifiers
@onready var lbl_modifiers = $UI/Panel/Scroll/VBox/LblModifiers
@onready var check_sphere = $UI/Panel/Scroll/VBox/CheckSphereModifiers
@onready var grid_sphere = $UI/Panel/Scroll/VBox/GridSphereModifiers
@onready var slider_sphere_count = $UI/Panel/Scroll/VBox/GridSphereModifiers/SliderSphereCount
@onready var slider_sphere_radius = $UI/Panel/Scroll/VBox/GridSphereModifiers/SliderSphereRadius
@onready var check_cylinder = $UI/Panel/Scroll/VBox/CheckCylinderModifiers
@onready var grid_cylinder = $UI/Panel/Scroll/VBox/GridCylinderModifiers
@onready var slider_cylinder_count = $UI/Panel/Scroll/VBox/GridCylinderModifiers/SliderCylinderCount
@onready var slider_cylinder_radius = $UI/Panel/Scroll/VBox/GridCylinderModifiers/SliderCylinderRadius
@onready var slider_cylinder_angle = $UI/Panel/Scroll/VBox/GridCylinderModifiers/SliderCylinderAngle
@onready var check_honeycomb = $UI/Panel/Scroll/VBox/CheckHoneycombModifiers
@onready var grid_honeycomb = $UI/Panel/Scroll/VBox/GridHoneycombModifiers
@onready var slider_honeycomb_cell = $UI/Panel/Scroll/VBox/GridHoneycombModifiers/SliderHoneycombCell
@onready var btn_reseed = $UI/Panel/Scroll/VBox/BtnReseedModifiers

# CAM Slicing Controls
@onready var slice_rig = $SliceRig
@onready var check_slicing = $UI/Panel/Scroll/VBox/CheckSlicing
@onready var slicing_controls = $UI/Panel/Scroll/VBox/SlicingControls
@onready var option_grid = $UI/Panel/Scroll/VBox/SlicingControls/GridSlicing/OptionGrid
@onready var slider_explode = $UI/Panel/Scroll/VBox/SlicingControls/GridSlicing/SliderExplode
@onready var check_color_slices = $UI/Panel/Scroll/VBox/SlicingControls/CheckColorSlices
@onready var check_dowel_pins = $UI/Panel/Scroll/VBox/SlicingControls/CheckDowelPins
@onready var btn_export_stl = $UI/Panel/Scroll/VBox/SlicingControls/ExportButtons/BtnExportSTL
@onready var btn_export_3mf = $UI/Panel/Scroll/VBox/SlicingControls/ExportButtons/BtnExport3MF
@onready var btn_export_dxf = $UI/Panel/Scroll/VBox/SlicingControls/ExportButtons/BtnExportDXF
@onready var lbl_export_status = $UI/Panel/Scroll/VBox/SlicingControls/LblExportStatus

# Mode Navigation & Section Groups
@onready var btn_tab_body = $UI/Panel/Scroll/VBox/ModeTabs/BtnTabBody
@onready var btn_tab_hardware = $UI/Panel/Scroll/VBox/ModeTabs/BtnTabHardware
@onready var btn_tab_slicing = $UI/Panel/Scroll/VBox/ModeTabs/BtnTabSlicing
@onready var btn_tab_finish = $UI/Panel/Scroll/VBox/ModeTabs/BtnTabFinish
@onready var btn_quick_slicing = $UI/BtnQuickSlicing
@onready var hsep_mode = $UI/Panel/Scroll/VBox/HSeparatorMode
@onready var lbl_global = $UI/Panel/Scroll/VBox/LblGlobal
@onready var grid_global = $UI/Panel/Scroll/VBox/GridGlobal
@onready var hsep_sym = $UI/Panel/Scroll/VBox/HSeparator2
@onready var hsep_cuts = $UI/Panel/Scroll/VBox/HSeparator3
@onready var lbl_ergo = $UI/Panel/Scroll/VBox/LblErgo
@onready var hsep_hw = $UI/Panel/Scroll/VBox/HSeparator4
@onready var lbl_hw = $UI/Panel/Scroll/VBox/LblHardware
@onready var grid_hw = $UI/Panel/Scroll/VBox/GridHardware
@onready var hsep_cam = $UI/Panel/Scroll/VBox/HSeparatorCAM
@onready var lbl_cam = $UI/Panel/Scroll/VBox/LblCAM
@onready var lbl_cam_sub = $UI/Panel/Scroll/VBox/LblCAMSub

# Finish & Materials Controls
@onready var hsep_finish = $UI/Panel/Scroll/VBox/HSeparatorFinish
@onready var lbl_finish = $UI/Panel/Scroll/VBox/LblFinish
@onready var grid_finish = $UI/Panel/Scroll/VBox/GridFinish
@onready var option_preset = $UI/Panel/Scroll/VBox/GridFinish/OptionPreset
@onready var option_finish_type = $UI/Panel/Scroll/VBox/GridFinish/OptionFinishType
@onready var color_base = $UI/Panel/Scroll/VBox/GridFinish/ColorBase
@onready var color_inner = $UI/Panel/Scroll/VBox/GridFinish/ColorInner
@onready var color_mid = $UI/Panel/Scroll/VBox/GridFinish/ColorMid
@onready var color_rim = $UI/Panel/Scroll/VBox/GridFinish/ColorRim
@onready var slider_burst_falloff = $UI/Panel/Scroll/VBox/GridFinish/SliderBurstFalloff
@onready var slider_waist_pinch = $UI/Panel/Scroll/VBox/GridFinish/SliderWaistPinch
@onready var slider_flake_sparkle = $UI/Panel/Scroll/VBox/GridFinish/SliderFlakeSparkle
@onready var slider_flame_intensity = $UI/Panel/Scroll/VBox/GridFinish/SliderFlameIntensity
@onready var slider_clearcoat = $UI/Panel/Scroll/VBox/GridFinish/SliderClearcoat
@onready var slider_clearcoat_roughness = $UI/Panel/Scroll/VBox/GridFinish/SliderClearcoatRoughness
@onready var hsep_project = $UI/Panel/Scroll/VBox/HSeparatorProject
@onready var lbl_project = $UI/Panel/Scroll/VBox/LblProject
@onready var project_buttons = $UI/Panel/Scroll/VBox/ProjectButtons
@onready var btn_save_project = $UI/Panel/Scroll/VBox/ProjectButtons/BtnSaveProject
@onready var btn_load_project = $UI/Panel/Scroll/VBox/ProjectButtons/BtnLoadProject
@onready var btn_reset_defaults = $UI/Panel/Scroll/VBox/ProjectButtons/BtnResetDefaults
@onready var lbl_project_status = $UI/Panel/Scroll/VBox/LblProjectStatus

var current_ui_mode: int = 0

# Materials for Hardware & Slices
var body_mat: StandardMaterial3D
var finish_mat: ShaderMaterial
var finish_shader: Shader
var chrome_mat: StandardMaterial3D
var black_plastic_mat: StandardMaterial3D
var cream_mat: StandardMaterial3D
var dowel_mat: StandardMaterial3D
var maple_mat: StandardMaterial3D
var rosewood_mat: StandardMaterial3D
var frets_mat: StandardMaterial3D
var nut_mat: StandardMaterial3D
var slice_materials: Array[StandardMaterial3D] = []

# Camera navigation state
var is_orbiting = false
var last_mouse_pos = Vector2.ZERO
var orbit_speed = 0.005
var zoom_speed = 0.05

func _ready():
	_setup_materials()
	_sync_ui_from_mesh()
	_connect_signals()
	_update_hardware_visuals()
	_update_finish_shader()
	_switch_ui_mode(0)
	_check_cli_capture()

func _setup_materials():
	if not body_mesh:
		return

	# PBR Guitar Finish Shader Material
	finish_shader = load("res://shaders/guitar_finish.gdshader")
	finish_mat = ShaderMaterial.new()
	finish_mat.shader = finish_shader
	body_mesh.material_override = finish_mat

	body_mat = StandardMaterial3D.new()
	body_mat.albedo_color = Color(0.85, 0.14, 0.16) # Candy Apple Fiesta Red
	body_mat.metallic = 0.15
	body_mat.roughness = 0.22
	body_mat.clearcoat_enabled = true
	body_mat.clearcoat = 0.9
	body_mat.clearcoat_roughness = 0.08
	body_mat.cull_mode = BaseMaterial3D.CULL_BACK

	chrome_mat = StandardMaterial3D.new()
	chrome_mat.albedo_color = Color(0.96, 0.97, 0.99)
	chrome_mat.metallic = 0.95
	chrome_mat.roughness = 0.10
	chrome_mat.clearcoat_enabled = true
	chrome_mat.clearcoat = 0.8
	chrome_mat.clearcoat_roughness = 0.05
	chrome_mat.cull_mode = BaseMaterial3D.CULL_BACK

	black_plastic_mat = StandardMaterial3D.new()
	black_plastic_mat.albedo_color = Color(0.08, 0.08, 0.09)
	black_plastic_mat.metallic = 0.05
	black_plastic_mat.roughness = 0.32
	black_plastic_mat.cull_mode = BaseMaterial3D.CULL_BACK

	cream_mat = StandardMaterial3D.new()
	cream_mat.albedo_color = Color(0.92, 0.88, 0.78)
	cream_mat.metallic = 0.05
	cream_mat.roughness = 0.38
	cream_mat.cull_mode = BaseMaterial3D.CULL_BACK

	dowel_mat = StandardMaterial3D.new()
	dowel_mat.albedo_color = Color(0.88, 0.74, 0.48) # Hardwood Dowel Pin
	dowel_mat.roughness = 0.45
	dowel_mat.cull_mode = BaseMaterial3D.CULL_BACK

	# Neck & Headstock Materials
	maple_mat = StandardMaterial3D.new()
	maple_mat.albedo_color = Color(0.89, 0.77, 0.60) # Satin Hard Rock Canadian Maple
	maple_mat.roughness = 0.38
	maple_mat.cull_mode = BaseMaterial3D.CULL_BACK

	rosewood_mat = StandardMaterial3D.new()
	rosewood_mat.albedo_color = Color(0.24, 0.16, 0.12) # Rich Dark Indian Rosewood Fretboard
	rosewood_mat.roughness = 0.55
	rosewood_mat.cull_mode = BaseMaterial3D.CULL_BACK

	frets_mat = StandardMaterial3D.new()
	frets_mat.albedo_color = Color(0.85, 0.85, 0.84) # 18% Nickel-Silver Frets
	frets_mat.metallic = 0.92
	frets_mat.roughness = 0.18
	frets_mat.cull_mode = BaseMaterial3D.CULL_BACK

	nut_mat = StandardMaterial3D.new()
	nut_mat.albedo_color = Color(0.92, 0.90, 0.82) # Aged Natural Bone Nut
	nut_mat.roughness = 0.35
	nut_mat.cull_mode = BaseMaterial3D.CULL_BACK

	var colors = [
		Color(0.25, 0.82, 0.65), # Mint Green
		Color(0.95, 0.45, 0.45), # Coral Pink
		Color(0.70, 0.55, 0.95), # Lavender
		Color(0.95, 0.75, 0.25), # Amber Gold
		Color(0.35, 0.75, 0.95), # Sky Blue
		Color(0.95, 0.58, 0.38), # Peach
		Color(0.20, 0.75, 0.78), # Teal
		Color(0.90, 0.35, 0.65)  # Rose
	]
	slice_materials.clear()
	for c in colors:
		var sm = StandardMaterial3D.new()
		sm.albedo_color = c
		sm.metallic = 0.10
		sm.roughness = 0.28
		sm.clearcoat_enabled = true
		sm.clearcoat = 0.5
		sm.cull_mode = BaseMaterial3D.CULL_BACK
		slice_materials.append(sm)

func _sync_ui_from_mesh():
	if not body_mesh:
		return
	slider_length.value = body_mesh.body_length
	slider_thickness.value = body_mesh.body_thickness
	slider_radius.value = body_mesh.edge_radius

	check_symmetric.button_pressed = body_mesh.symmetric_mode
	symmetric_controls.visible = body_mesh.symmetric_mode
	asymmetric_controls.visible = not body_mesh.symmetric_mode

	slider_hip.value = body_mesh.hip_width
	slider_waist.value = body_mesh.waist_width
	slider_chest.value = body_mesh.chest_width
	slider_shoulder.value = body_mesh.shoulder_width
	slider_horn_reach.value = body_mesh.horn_reach
	slider_horn_roundness.value = body_mesh.horn_roundness

	slider_t_hip.value = body_mesh.treble_hip_width
	slider_t_waist.value = body_mesh.treble_waist_width
	slider_t_chest.value = body_mesh.treble_chest_width
	slider_t_horn.value = body_mesh.treble_horn_length
	slider_t_roundness.value = body_mesh.treble_horn_roundness

	slider_b_hip.value = body_mesh.bass_hip_width
	slider_b_waist.value = body_mesh.bass_waist_width
	slider_b_chest.value = body_mesh.bass_chest_width
	slider_b_horn.value = body_mesh.bass_horn_length
	slider_b_roundness.value = body_mesh.bass_horn_roundness

	check_belly.button_pressed = body_mesh.belly_cut_enabled
	belly_controls.visible = body_mesh.belly_cut_enabled
	slider_belly_angle.value = body_mesh.belly_cut_angle
	slider_belly_length.value = body_mesh.belly_cut_length

	check_forearm.button_pressed = body_mesh.forearm_bevel_enabled
	forearm_controls.visible = body_mesh.forearm_bevel_enabled
	slider_forearm_angle.value = body_mesh.forearm_bevel_angle
	slider_forearm_length.value = body_mesh.forearm_bevel_length

	# Hardware
	option_pickups.selected = body_mesh.pickup_config
	option_bridge.selected = body_mesh.bridge_type
	slider_bridge_y.value = body_mesh.bridge_y
	slider_bridge_slant.value = body_mesh.bridge_pickup_slant
	slider_clearance.value = body_mesh.pickup_clearance
	slider_cavity_depth.value = body_mesh.pickup_depth
	check_neck_pocket.button_pressed = body_mesh.neck_pocket_enabled
	check_control_cavity.button_pressed = body_mesh.control_cavity_enabled
	check_piezo.button_pressed = body_mesh.piezo_saddles_enabled
	if is_instance_valid(check_neck): check_neck.button_pressed = true

	# Procedural Modifiers & Weight Relief
	if is_instance_valid(check_sphere):
		check_sphere.button_pressed = body_mesh.sphere_modifiers_enabled
		grid_sphere.visible = body_mesh.sphere_modifiers_enabled
		slider_sphere_count.value = body_mesh.sphere_count
		slider_sphere_radius.value = body_mesh.sphere_radius
	if is_instance_valid(check_cylinder):
		check_cylinder.button_pressed = body_mesh.cylinder_modifiers_enabled
		grid_cylinder.visible = body_mesh.cylinder_modifiers_enabled
		slider_cylinder_count.value = body_mesh.cylinder_count
		slider_cylinder_radius.value = body_mesh.cylinder_radius
		slider_cylinder_angle.value = body_mesh.cylinder_angle
	if is_instance_valid(check_honeycomb):
		check_honeycomb.button_pressed = body_mesh.honeycomb_modifiers_enabled
		grid_honeycomb.visible = body_mesh.honeycomb_modifiers_enabled
		slider_honeycomb_cell.value = body_mesh.honeycomb_cell_size

	# CAM & Slicing
	check_slicing.button_pressed = body_mesh.slicing_enabled
	slicing_controls.visible = body_mesh.slicing_enabled
	option_grid.selected = 0 if body_mesh.slice_grid_type == 1 else 1
	slider_explode.value = body_mesh.explode_distance
	check_dowel_pins.button_pressed = body_mesh.show_dowel_pins

func _connect_signals():
	# View presets
	btn_orbit.pressed.connect(func():
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
	)
	btn_front.pressed.connect(func():
		camera_pivot.rotation = Vector3(0.0, 0.0, 0.0)
	)
	btn_back.pressed.connect(func():
		camera_pivot.rotation = Vector3(0.0, PI, 0.0)
	)
	btn_side.pressed.connect(func():
		camera_pivot.rotation = Vector3(-0.15, 1.35, 0.0)
	)

	# Global
	slider_length.value_changed.connect(func(v):
		body_mesh.body_length = v
		_update_hardware_visuals()
	)
	slider_thickness.value_changed.connect(func(v):
		body_mesh.body_thickness = v
		_update_hardware_visuals()
	)
	slider_radius.value_changed.connect(func(v): body_mesh.edge_radius = v)

	# Symmetry
	check_symmetric.toggled.connect(func(v):
		body_mesh.symmetric_mode = v
		symmetric_controls.visible = v
		asymmetric_controls.visible = not v
		_update_hardware_visuals()
	)

	# Unified Symmetric
	slider_hip.value_changed.connect(func(v):
		body_mesh.hip_width = v
		slider_t_hip.value = v * 0.5
		slider_b_hip.value = v * 0.5
		_update_hardware_visuals()
	)
	slider_waist.value_changed.connect(func(v):
		body_mesh.waist_width = v
		slider_t_waist.value = v * 0.5
		slider_b_waist.value = v * 0.5
		_update_hardware_visuals()
	)
	slider_chest.value_changed.connect(func(v):
		body_mesh.chest_width = v
		slider_t_chest.value = v * 0.5
		slider_b_chest.value = v * 0.5
		_update_hardware_visuals()
	)
	slider_shoulder.value_changed.connect(func(v):
		body_mesh.shoulder_width = v
	)
	slider_horn_reach.value_changed.connect(func(v):
		body_mesh.horn_reach = v
		slider_t_horn.value = v
		slider_b_horn.value = v
	)
	slider_horn_roundness.value_changed.connect(func(v):
		body_mesh.horn_roundness = v
		slider_t_roundness.value = v
		slider_b_roundness.value = v
	)

	# Asymmetric Treble
	slider_t_hip.value_changed.connect(func(v):
		body_mesh.treble_hip_width = v
		_update_hardware_visuals()
	)
	slider_t_waist.value_changed.connect(func(v):
		body_mesh.treble_waist_width = v
		_update_hardware_visuals()
	)
	slider_t_chest.value_changed.connect(func(v):
		body_mesh.treble_chest_width = v
		_update_hardware_visuals()
	)
	slider_t_horn.value_changed.connect(func(v): body_mesh.treble_horn_length = v)
	slider_t_roundness.value_changed.connect(func(v): body_mesh.treble_horn_roundness = v)

	# Asymmetric Bass
	slider_b_hip.value_changed.connect(func(v):
		body_mesh.bass_hip_width = v
	)
	slider_b_waist.value_changed.connect(func(v): body_mesh.bass_waist_width = v)
	slider_b_chest.value_changed.connect(func(v): body_mesh.bass_chest_width = v)
	slider_b_horn.value_changed.connect(func(v): body_mesh.bass_horn_length = v)
	slider_b_roundness.value_changed.connect(func(v): body_mesh.bass_horn_roundness = v)

	# Belly Cut
	check_belly.toggled.connect(func(v):
		body_mesh.belly_cut_enabled = v
		belly_controls.visible = v
	)
	slider_belly_angle.value_changed.connect(func(v): body_mesh.belly_cut_angle = v)
	slider_belly_length.value_changed.connect(func(v): body_mesh.belly_cut_length = v)

	# Forearm Bevel
	check_forearm.toggled.connect(func(v):
		body_mesh.forearm_bevel_enabled = v
		forearm_controls.visible = v
	)
	slider_forearm_angle.value_changed.connect(func(v): body_mesh.forearm_bevel_angle = v)
	slider_forearm_length.value_changed.connect(func(v): body_mesh.forearm_bevel_length = v)

	# Hardware & Cavity Controls
	option_pickups.item_selected.connect(func(idx):
		body_mesh.pickup_config = idx
		_update_hardware_visuals()
	)
	option_bridge.item_selected.connect(func(idx):
		body_mesh.bridge_type = idx
		_update_hardware_visuals()
	)
	slider_bridge_y.value_changed.connect(func(v):
		body_mesh.bridge_y = v
		_update_hardware_visuals()
	)
	slider_bridge_slant.value_changed.connect(func(v):
		body_mesh.bridge_pickup_slant = v
		_update_hardware_visuals()
	)
	slider_clearance.value_changed.connect(func(v):
		body_mesh.pickup_clearance = v
	)
	slider_cavity_depth.value_changed.connect(func(v):
		body_mesh.pickup_depth = v
	)
	check_neck_pocket.toggled.connect(func(v):
		body_mesh.neck_pocket_enabled = v
	)
	check_control_cavity.toggled.connect(func(v):
		body_mesh.control_cavity_enabled = v
		_update_hardware_visuals()
	)
	check_hardware_models.toggled.connect(func(v):
		hardware_rig.visible = v
	)
	check_piezo.toggled.connect(func(v):
		body_mesh.piezo_saddles_enabled = v
		_update_hardware_visuals()
	)

	# CAM Slicing
	check_slicing.toggled.connect(func(v):
		body_mesh.slicing_enabled = v
		btn_quick_slicing.button_pressed = v
		btn_quick_slicing.text = "🪚 Slicing Mode: ON" if v else "🪚 Slicing Mode: OFF"
		slicing_controls.visible = (current_ui_mode == 2) and v
		_update_slice_visuals()
	)
	btn_quick_slicing.toggled.connect(func(v):
		check_slicing.button_pressed = v
		if v:
			_switch_ui_mode(2)
	)
	btn_tab_body.pressed.connect(func(): _switch_ui_mode(0))
	btn_tab_hardware.pressed.connect(func(): _switch_ui_mode(1))
	btn_tab_slicing.pressed.connect(func(): _switch_ui_mode(2))
	btn_tab_finish.pressed.connect(func(): _switch_ui_mode(3))

	option_grid.item_selected.connect(func(idx):
		body_mesh.slice_grid_type = 1 if idx == 0 else 2
		_update_slice_visuals()
	)
	slider_explode.value_changed.connect(func(v):
		body_mesh.explode_distance = v
		_update_slice_transforms()
	)
	check_color_slices.toggled.connect(func(_v):
		_update_slice_visuals()
	)
	check_dowel_pins.toggled.connect(func(v):
		body_mesh.show_dowel_pins = v
		_update_slice_visuals()
	)
	btn_export_stl.pressed.connect(_on_export_stl_pressed)
	btn_export_3mf.pressed.connect(_on_export_3mf_pressed)
	btn_export_dxf.pressed.connect(_on_export_dxf_pressed)

	# Phase 5: Body Shape Presets & Procedural Modifiers
	if is_instance_valid(option_shape_preset):
		option_shape_preset.item_selected.connect(_apply_shape_preset)
	if is_instance_valid(check_sphere):
		check_sphere.toggled.connect(func(v):
			body_mesh.sphere_modifiers_enabled = v
			grid_sphere.visible = v
		)
		slider_sphere_count.value_changed.connect(func(v): body_mesh.sphere_count = int(v))
		slider_sphere_radius.value_changed.connect(func(v): body_mesh.sphere_radius = v)

	if is_instance_valid(check_cylinder):
		check_cylinder.toggled.connect(func(v):
			body_mesh.cylinder_modifiers_enabled = v
			grid_cylinder.visible = v
		)
		slider_cylinder_count.value_changed.connect(func(v): body_mesh.cylinder_count = int(v))
		slider_cylinder_radius.value_changed.connect(func(v): body_mesh.cylinder_radius = v)
		slider_cylinder_angle.value_changed.connect(func(v): body_mesh.cylinder_angle = v)

	if is_instance_valid(check_honeycomb):
		check_honeycomb.toggled.connect(func(v):
			body_mesh.honeycomb_modifiers_enabled = v
			grid_honeycomb.visible = v
		)
		slider_honeycomb_cell.value_changed.connect(func(v): body_mesh.honeycomb_cell_size = v)

	if is_instance_valid(btn_reseed):
		btn_reseed.pressed.connect(func():
			body_mesh.modifier_seed = randi() % 100000
			body_mesh.rebuild_mesh()
		)

	if is_instance_valid(check_neck):
		check_neck.toggled.connect(func(_v): _update_hardware_visuals())

	# Finish & Materials
	option_preset.item_selected.connect(_apply_curated_preset)
	option_finish_type.item_selected.connect(func(_idx): _update_finish_shader())
	color_base.color_changed.connect(func(_c): _update_finish_shader())
	color_inner.color_changed.connect(func(_c): _update_finish_shader())
	color_mid.color_changed.connect(func(_c): _update_finish_shader())
	color_rim.color_changed.connect(func(_c): _update_finish_shader())
	slider_burst_falloff.value_changed.connect(func(_v): _update_finish_shader())
	slider_waist_pinch.value_changed.connect(func(_v): _update_finish_shader())
	slider_flake_sparkle.value_changed.connect(func(_v): _update_finish_shader())
	slider_flame_intensity.value_changed.connect(func(_v): _update_finish_shader())
	slider_clearcoat.value_changed.connect(func(_v): _update_finish_shader())
	slider_clearcoat_roughness.value_changed.connect(func(_v): _update_finish_shader())
	btn_save_project.pressed.connect(func(): _save_project_json())
	btn_load_project.pressed.connect(func(): _load_project_json())
	btn_reset_defaults.pressed.connect(_reset_project_defaults)

func _switch_ui_mode(mode: int):
	current_ui_mode = mode
	if is_instance_valid(btn_tab_body): btn_tab_body.button_pressed = (mode == 0)
	if is_instance_valid(btn_tab_hardware): btn_tab_hardware.button_pressed = (mode == 1)
	if is_instance_valid(btn_tab_slicing): btn_tab_slicing.button_pressed = (mode == 2)
	if is_instance_valid(btn_tab_finish): btn_tab_finish.button_pressed = (mode == 3)

	# Body section
	for n in [lbl_shape_preset, option_shape_preset, lbl_global, grid_global, hsep_sym, check_symmetric, hsep_cuts, lbl_ergo, check_belly, check_forearm, hsep_modifiers, lbl_modifiers, check_sphere, check_cylinder, check_honeycomb, btn_reseed]:
		if is_instance_valid(n): n.visible = (mode == 0)
	if mode == 0 and is_instance_valid(body_mesh):
		symmetric_controls.visible = body_mesh.symmetric_mode
		asymmetric_controls.visible = not body_mesh.symmetric_mode
		belly_controls.visible = body_mesh.belly_cut_enabled
		forearm_controls.visible = body_mesh.forearm_bevel_enabled
		grid_sphere.visible = body_mesh.sphere_modifiers_enabled
		grid_cylinder.visible = body_mesh.cylinder_modifiers_enabled
		grid_honeycomb.visible = body_mesh.honeycomb_modifiers_enabled
	else:
		if is_instance_valid(symmetric_controls): symmetric_controls.visible = false
		if is_instance_valid(asymmetric_controls): asymmetric_controls.visible = false
		if is_instance_valid(belly_controls): belly_controls.visible = false
		if is_instance_valid(forearm_controls): forearm_controls.visible = false
		if is_instance_valid(grid_sphere): grid_sphere.visible = false
		if is_instance_valid(grid_cylinder): grid_cylinder.visible = false
		if is_instance_valid(grid_honeycomb): grid_honeycomb.visible = false

	# Hardware section
	for n in [hsep_hw, lbl_hw, grid_hw, check_neck_pocket, check_control_cavity, check_hardware_models, check_neck, check_piezo]:
		if is_instance_valid(n): n.visible = (mode == 1)

	# Slicing section
	for n in [hsep_cam, lbl_cam, lbl_cam_sub, check_slicing]:
		if is_instance_valid(n): n.visible = (mode == 2)
	if is_instance_valid(slicing_controls) and is_instance_valid(check_slicing):
		slicing_controls.visible = (mode == 2) and check_slicing.button_pressed

	# Finish & Project section
	for n in [hsep_finish, lbl_finish, grid_finish, hsep_project, lbl_project, project_buttons, lbl_project_status]:
		if is_instance_valid(n): n.visible = (mode == 3)

func _update_hardware_visuals():
	if not is_instance_valid(hardware_rig) or not is_instance_valid(body_mesh):
		return
	for c in hardware_rig.get_children():
		c.queue_free()

	hardware_rig.visible = check_hardware_models.button_pressed

	var scale_y = body_mesh.body_length / 446.0
	var thickness = body_mesh.body_thickness
	var center_y = 240.0 * scale_y * 0.001
	var center_z = thickness * 0.5 * 0.001
	var front_z = center_z

	var to_world = func(mx: float, my: float, mz_top: float = 0.0) -> Vector3:
		return Vector3(mx * 0.001, (my * scale_y) * 0.001 - center_y, front_z + mz_top * 0.001)

	# 1. Bridge
	if body_mesh.bridge_enabled:
		_create_bridge_visuals(to_world, scale_y)

	# 2. Pickups
	_create_pickup_visuals(to_world, scale_y)

	# 3. Potentiometer Knobs
	if body_mesh.control_cavity_enabled:
		_create_knob_visuals(to_world, scale_y)

	# 4. Output Jack Plate
	_create_jack_plate_visuals(to_world, scale_y)

	# 5. Full Neck & Headstock Assembly
	_create_neck_visuals(to_world, scale_y)

func _create_neck_visuals(to_world: Callable, scale_y: float):
	if not is_instance_valid(check_neck) or not check_neck.button_pressed:
		return
	if not body_mesh.neck_pocket_enabled:
		return

	var neck_group = Node3D.new()
	neck_group.name = "NeckRig"
	hardware_rig.add_child(neck_group)

	# Seated into the mortise pocket floor
	# Pocket floor is at -body_mesh.neck_pocket_depth relative to front face
	var my = 399.69 - (body_mesh.neck_pocket_length / scale_y)
	neck_group.position = to_world.call(0.0, my, -body_mesh.neck_pocket_depth)

	var parts = [
		{ "path": "res://assets/neck/neck_shaft.tres", "mat": maple_mat, "name": "NeckShaft" },
		{ "path": "res://assets/neck/fretboard.tres", "mat": rosewood_mat, "name": "Fretboard" },
		{ "path": "res://assets/neck/frets.tres", "mat": frets_mat, "name": "Frets" },
		{ "path": "res://assets/neck/nut.tres", "mat": nut_mat, "name": "Nut" },
		{ "path": "res://assets/neck/tuners.tres", "mat": chrome_mat, "name": "Tuners" }
	]

	for p in parts:
		if ResourceLoader.exists(p["path"]):
			var m = load(p["path"])
			if m:
				var mi = MeshInstance3D.new()
				mi.name = p["name"]
				mi.mesh = m
				mi.material_override = p["mat"]
				neck_group.add_child(mi)

func _apply_shape_preset(idx: int):
	if not body_mesh:
		return
	if is_instance_valid(option_shape_preset):
		option_shape_preset.selected = idx
	match idx:
		0: # Sarcaster '62 (Strat)
			body_mesh.body_length = 446.0
			body_mesh.body_thickness = 45.0
			body_mesh.edge_radius = 11.0
			body_mesh.symmetric_mode = false
			body_mesh.treble_hip_width = 159.0
			body_mesh.bass_hip_width = 163.0
			body_mesh.treble_waist_width = 106.0
			body_mesh.bass_waist_width = 122.0
			body_mesh.treble_chest_width = 135.0
			body_mesh.bass_chest_width = 145.0
			body_mesh.treble_shoulder_width = 125.0
			body_mesh.bass_shoulder_width = 125.0
			body_mesh.treble_horn_length = 400.0
			body_mesh.bass_horn_length = 458.0
			body_mesh.treble_horn_roundness = 1.0
			body_mesh.bass_horn_roundness = 1.0
			body_mesh.belly_cut_enabled = true
			body_mesh.forearm_bevel_enabled = true
		1: # Single-Cut Standard (LP)
			body_mesh.body_length = 440.0
			body_mesh.body_thickness = 48.0
			body_mesh.edge_radius = 6.0
			body_mesh.symmetric_mode = false
			body_mesh.treble_hip_width = 167.5
			body_mesh.bass_hip_width = 167.5
			body_mesh.treble_waist_width = 105.0
			body_mesh.bass_waist_width = 105.0
			body_mesh.treble_chest_width = 142.5
			body_mesh.bass_chest_width = 142.5
			body_mesh.treble_shoulder_width = 120.0
			body_mesh.bass_shoulder_width = 120.0
			body_mesh.treble_horn_length = 408.0
			body_mesh.bass_horn_length = 376.0
			body_mesh.treble_horn_roundness = 1.4
			body_mesh.bass_horn_roundness = 0.5
			body_mesh.belly_cut_enabled = false
			body_mesh.forearm_bevel_enabled = false
		2: # Double-Cut Custom (SG)
			body_mesh.body_length = 410.0
			body_mesh.body_thickness = 35.0
			body_mesh.edge_radius = 5.0
			body_mesh.symmetric_mode = true
			body_mesh.hip_width = 318.0
			body_mesh.waist_width = 232.0
			body_mesh.chest_width = 275.0
			body_mesh.shoulder_width = 270.0
			body_mesh.horn_reach = 450.0
			body_mesh.horn_roundness = 0.65
			body_mesh.belly_cut_enabled = false
			body_mesh.forearm_bevel_enabled = true
		3: # Offset Modern (Jazzmaster)
			body_mesh.body_length = 465.0
			body_mesh.body_thickness = 42.0
			body_mesh.edge_radius = 10.0
			body_mesh.symmetric_mode = false
			body_mesh.treble_hip_width = 175.0
			body_mesh.bass_hip_width = 170.0
			body_mesh.treble_waist_width = 112.0
			body_mesh.bass_waist_width = 126.0
			body_mesh.treble_chest_width = 140.0
			body_mesh.bass_chest_width = 155.0
			body_mesh.treble_shoulder_width = 128.0
			body_mesh.bass_shoulder_width = 132.0
			body_mesh.treble_horn_length = 406.0
			body_mesh.bass_horn_length = 452.0
			body_mesh.treble_horn_roundness = 1.1
			body_mesh.bass_horn_roundness = 1.0
			body_mesh.belly_cut_enabled = true
			body_mesh.forearm_bevel_enabled = true
		4: # Modern Flying V
			body_mesh.body_length = 480.0
			body_mesh.body_thickness = 38.0
			body_mesh.edge_radius = 4.0
			body_mesh.symmetric_mode = true
			body_mesh.hip_width = 410.0
			body_mesh.waist_width = 290.0
			body_mesh.chest_width = 200.0
			body_mesh.shoulder_width = 170.0
			body_mesh.horn_reach = 400.0
			body_mesh.horn_roundness = 0.5
			body_mesh.belly_cut_enabled = false
			body_mesh.forearm_bevel_enabled = false
		_:
			pass
	_sync_ui_from_mesh()
	_update_hardware_visuals()

func _create_bridge_visuals(to_world: Callable, scale_y: float):
	var bridge_group = Node3D.new()
	bridge_group.name = "BridgeRig"
	hardware_rig.add_child(bridge_group)

	var b_y = body_mesh.bridge_y

	if body_mesh.bridge_type == 0:
		# Hardtail baseplate (76mm x 40mm x 3mm)
		var plate = MeshInstance3D.new()
		var box = BoxMesh.new()
		box.size = Vector3(0.076, 0.040, 0.003)
		plate.mesh = box
		plate.material_override = chrome_mat
		plate.position = to_world.call(0.0, b_y, 0.0015)
		bridge_group.add_child(plate)

		# 6 individual chrome saddles
		for i in range(6):
			var sx = -26.25 + i * 10.5
			var saddle = MeshInstance3D.new()
			var s_box = BoxMesh.new()
			s_box.size = Vector3(0.010, 0.020, 0.006)
			saddle.mesh = s_box
			saddle.material_override = chrome_mat
			saddle.position = to_world.call(sx, b_y - 2.0 / scale_y, 0.005)
			bridge_group.add_child(saddle)

	else:
		# Tremolo baseplate (84mm x 40mm x 3.5mm)
		var plate = MeshInstance3D.new()
		var box = BoxMesh.new()
		box.size = Vector3(0.084, 0.040, 0.0035)
		plate.mesh = box
		plate.material_override = chrome_mat
		plate.position = to_world.call(0.0, b_y, 0.00175)
		bridge_group.add_child(plate)

		# 6 Saddles
		for i in range(6):
			var sx = -26.25 + i * 10.5
			var saddle = MeshInstance3D.new()
			var s_box = BoxMesh.new()
			s_box.size = Vector3(0.010, 0.020, 0.006)
			saddle.mesh = s_box
			saddle.material_override = chrome_mat
			saddle.position = to_world.call(sx, b_y - 2.0 / scale_y, 0.0055)
			bridge_group.add_child(saddle)

		# Tremolo Arm (Whammy bar)
		var arm = MeshInstance3D.new()
		var arm_mesh = CylinderMesh.new()
		arm_mesh.top_radius = 0.0025
		arm_mesh.bottom_radius = 0.0025
		arm_mesh.height = 0.110
		arm.mesh = arm_mesh
		arm.material_override = chrome_mat
		arm.position = to_world.call(34.0, b_y - 5.0 / scale_y, 0.035)
		arm.rotation = Vector3(deg_to_rad(-30.0), 0.0, deg_to_rad(10.0))
		bridge_group.add_child(arm)

	# Piezo Saddle Wire Slots (3mm wide slot from 6mm to 12mm in front of string holes, curved ends)
	if body_mesh.piezo_saddles_enabled:
		var slot_center_y = b_y + 9.0 * scale_y
		var hole_mat = StandardMaterial3D.new()
		hole_mat.albedo_color = Color(0.04, 0.04, 0.04)
		hole_mat.roughness = 0.95
		for i in range(6):
			var sx = -26.25 + i * 10.5
			# 3mm wide x 6mm long slot with curved ends on bridge plate
			var slot_mesh_inst = MeshInstance3D.new()
			var cap = CapsuleMesh.new()
			cap.radius = 0.0015
			cap.height = 0.006 * scale_y
			slot_mesh_inst.mesh = cap
			slot_mesh_inst.position = to_world.call(sx, slot_center_y, 3.05)
			slot_mesh_inst.material_override = hole_mat
			bridge_group.add_child(slot_mesh_inst)

			# Black Piezo transducer element on top of saddle
			var pz_elem = MeshInstance3D.new()
			var pz_box = BoxMesh.new()
			pz_box.size = Vector3(0.007, 0.004, 0.0015)
			pz_elem.mesh = pz_box
			pz_elem.position = to_world.call(sx, b_y - 2.0 / scale_y, 8.2)
			pz_elem.material_override = hole_mat
			bridge_group.add_child(pz_elem)

func _create_pickup_visuals(to_world: Callable, scale_y: float):
	var pickup_group = Node3D.new()
	pickup_group.name = "PickupsRig"
	hardware_rig.add_child(pickup_group)

	var config = body_mesh.pickup_config
	if config == 0:
		return

	if config == 1: # SSS
		_create_single_coil(pickup_group, to_world.call(0.0, body_mesh.bridge_pickup_y, 0.002), body_mesh.bridge_pickup_slant)
		_create_single_coil(pickup_group, to_world.call(0.0, body_mesh.middle_pickup_y, 0.002), 0.0)
		_create_single_coil(pickup_group, to_world.call(0.0, body_mesh.neck_pickup_y, 0.002), 0.0)
	elif config == 2: # HSS
		_create_humbucker(pickup_group, to_world.call(0.0, body_mesh.bridge_pickup_y, 0.002), 0.0)
		_create_single_coil(pickup_group, to_world.call(0.0, body_mesh.middle_pickup_y, 0.002), 0.0)
		_create_single_coil(pickup_group, to_world.call(0.0, body_mesh.neck_pickup_y, 0.002), 0.0)
	elif config == 3: # HH
		_create_humbucker(pickup_group, to_world.call(0.0, body_mesh.bridge_pickup_y, 0.002), 0.0)
		_create_humbucker(pickup_group, to_world.call(0.0, body_mesh.neck_pickup_y, 0.002), 0.0)

func _create_single_coil(parent: Node3D, pos: Vector3, slant_deg: float):
	var sc = Node3D.new()
	sc.position = pos
	sc.rotation.z = deg_to_rad(slant_deg)
	parent.add_child(sc)

	# Bobbin cover (70mm x 18mm x 12mm)
	var cover = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = Vector3(0.070, 0.018, 0.012)
	cover.mesh = box
	cover.material_override = black_plastic_mat
	cover.position = Vector3(0.0, 0.0, -0.004)
	sc.add_child(cover)

	# 6 Chrome pole pieces
	for p in range(6):
		var px = -26.0 + p * 10.4
		var pole = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.0025
		cyl.bottom_radius = 0.0025
		cyl.height = 0.004
		pole.mesh = cyl
		pole.material_override = chrome_mat
		pole.rotation.x = PI * 0.5
		pole.position = Vector3(px * 0.001, 0.0, 0.002)
		sc.add_child(pole)

func _create_humbucker(parent: Node3D, pos: Vector3, slant_deg: float):
	var hb = Node3D.new()
	hb.position = pos
	hb.rotation.z = deg_to_rad(slant_deg)
	parent.add_child(hb)

	# Mounting Bezel / Ring (89mm x 45mm x 3mm)
	var ring = MeshInstance3D.new()
	var r_box = BoxMesh.new()
	r_box.size = Vector3(0.089, 0.045, 0.003)
	ring.mesh = r_box
	ring.material_override = black_plastic_mat
	ring.position = Vector3(0.0, 0.0, 0.001)
	hb.add_child(ring)

	# Bobbin 1 (Slug coil, 68mm x 17mm x 12mm)
	var b1 = MeshInstance3D.new()
	var b1_mesh = BoxMesh.new()
	b1_mesh.size = Vector3(0.068, 0.017, 0.012)
	b1.mesh = b1_mesh
	b1.material_override = black_plastic_mat
	b1.position = Vector3(0.0, -0.009, -0.003)
	hb.add_child(b1)

	# Bobbin 2 (Screw coil, 68mm x 17mm x 12mm)
	var b2 = MeshInstance3D.new()
	var b2_mesh = BoxMesh.new()
	b2_mesh.size = Vector3(0.068, 0.017, 0.012)
	b2.mesh = b2_mesh
	b2.material_override = cream_mat # Zebra style for distinctive boutique appearance
	b2.position = Vector3(0.0, 0.009, -0.003)
	hb.add_child(b2)

	# 12 Chrome Pole Pieces
	for p in range(6):
		var px = -25.0 + p * 10.0
		# Slug coil poles
		var p1 = MeshInstance3D.new()
		var cyl1 = CylinderMesh.new()
		cyl1.top_radius = 0.0025
		cyl1.bottom_radius = 0.0025
		cyl1.height = 0.004
		p1.mesh = cyl1
		p1.material_override = chrome_mat
		p1.rotation.x = PI * 0.5
		p1.position = Vector3(px * 0.001, -0.009, 0.003)
		hb.add_child(p1)

		# Screw coil poles
		var p2 = MeshInstance3D.new()
		var cyl2 = CylinderMesh.new()
		cyl2.top_radius = 0.002
		cyl2.bottom_radius = 0.002
		cyl2.height = 0.0045
		p2.mesh = cyl2
		p2.material_override = chrome_mat
		p2.rotation.x = PI * 0.5
		p2.position = Vector3(px * 0.001, 0.009, 0.0032)
		hb.add_child(p2)

func _create_knob_visuals(to_world: Callable, scale_y: float):
	var knob_group = Node3D.new()
	knob_group.name = "KnobsRig"
	hardware_rig.add_child(knob_group)

	var cc_x = 88.0
	var cc_y = 175.0 * scale_y

	var pot_positions = [
		Vector2(cc_x, cc_y + 20.0),
		Vector2(cc_x + 6.0, cc_y - 12.0),
		Vector2(cc_x + 2.0, cc_y - 44.0)
	]

	for pos in pot_positions:
		var knob = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.009
		cyl.bottom_radius = 0.011
		cyl.height = 0.012
		knob.mesh = cyl
		knob.material_override = chrome_mat
		knob.rotation.x = PI * 0.5
		knob.position = to_world.call(pos.x, pos.y, 0.006)
		knob_group.add_child(knob)

func _create_jack_plate_visuals(to_world: Callable, scale_y: float):
	var jack_group = Node3D.new()
	jack_group.name = "JackPlateRig"
	hardware_rig.add_child(jack_group)

	var t_hip = body_mesh.treble_hip_width if not body_mesh.symmetric_mode else body_mesh.hip_width * 0.5
	var r_hip = 159.0
	var center_y = 240.0 * scale_y * 0.001

	# Waypoints 3, 4, 5 from body contour to derive exact position and tangent
	var p3 = Vector2(111.58 * (t_hip / r_hip), 30.43 * scale_y)
	var p4 = Vector2(145.13 * (t_hip / r_hip), 72.89 * scale_y)
	var p5 = Vector2(t_hip, 143.95 * scale_y)

	var world_pos = Vector3(p4.x * 0.001, p4.y * 0.001 - center_y, 0.0)
	var tangent_2d = (p5 - p3).normalized()

	# Orthonormal basis:
	# basis_x: major axis of oval plate along rim curve (tangent)
	var basis_x = Vector3(tangent_2d.x, tangent_2d.y, 0.0)
	# basis_y: minor axis of oval plate across body thickness (Z in world)
	var basis_y = Vector3(0.0, 0.0, 1.0)
	# basis_z: outward normal pointing out of guitar body
	var basis_z = Vector3(tangent_2d.y, -tangent_2d.x, 0.0)

	jack_group.transform = Transform3D(basis_x, basis_y, basis_z, world_pos)

	# Oval football baseplate
	# CylinderMesh: by default height is along Y, circle is in XZ.
	# Rotating 90 deg around X puts height along Z (normal), and circle in XY (rim plane).
	var plate = MeshInstance3D.new()
	var cyl = CylinderMesh.new()
	cyl.top_radius = 0.012
	cyl.bottom_radius = 0.012
	cyl.height = 0.0016
	plate.mesh = cyl
	plate.rotation = Vector3(PI * 0.5, 0.0, 0.0)
	plate.scale = Vector3(2.0, 1.0, 1.0) # 48mm along X (rim curve), 24mm along Y (body thickness)
	plate.position = Vector3(0.0, 0.0, 0.0008) # Flush on outer wood rim
	plate.material_override = chrome_mat
	jack_group.add_child(plate)

	# 1/4" Hex nut
	var nut = MeshInstance3D.new()
	var nut_mesh = CylinderMesh.new()
	nut_mesh.top_radius = 0.006
	nut_mesh.bottom_radius = 0.006
	nut_mesh.height = 0.0025
	nut_mesh.radial_segments = 6 # 6-sided hex
	nut.mesh = nut_mesh
	nut.rotation = Vector3(PI * 0.5, 0.0, 0.0)
	nut.position = Vector3(0.0, 0.0, 0.0022)
	nut.material_override = chrome_mat
	jack_group.add_child(nut)

	# Center 1/4" dark socket bore
	var socket_hole = MeshInstance3D.new()
	var sock_mesh = CylinderMesh.new()
	sock_mesh.top_radius = 0.0032 # 6.4mm jack bore
	sock_mesh.bottom_radius = 0.0032
	sock_mesh.height = 0.003
	socket_hole.mesh = sock_mesh
	socket_hole.rotation = Vector3(PI * 0.5, 0.0, 0.0)
	socket_hole.position = Vector3(0.0, 0.0, 0.0026)
	socket_hole.material_override = black_plastic_mat
	jack_group.add_child(socket_hole)

	# 2 Chrome mounting screws along long axis (X)
	for s_sign in [-1.0, 1.0]:
		var screw = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.0016
		s_mesh.height = 0.0016
		screw.mesh = s_mesh
		screw.position = Vector3(s_sign * 0.0165, 0.0, 0.0016)
		screw.material_override = chrome_mat
		jack_group.add_child(screw)

func _update_slice_visuals():
	if not is_instance_valid(slice_rig) or not is_instance_valid(body_mesh):
		return
	for c in slice_rig.get_children():
		c.queue_free()

	if not body_mesh.slicing_enabled:
		body_mesh.visible = true
		hardware_rig.visible = check_hardware_models.button_pressed
		return

	body_mesh.visible = false
	hardware_rig.visible = false

	var n = body_mesh.get_slice_count()
	var explode_dist = body_mesh.explode_distance * 0.001
	for i in range(n):
		var m = body_mesh.get_slice_mesh(i)
		if m:
			var mi = MeshInstance3D.new()
			mi.mesh = m
			mi.name = "SlicePart_%d" % i
			if check_color_slices.button_pressed:
				mi.material_override = slice_materials[i % slice_materials.size()]
			else:
				mi.material_override = finish_mat if is_instance_valid(finish_mat) else body_mat
			var dir: Vector3 = body_mesh.get_slice_direction(i)
			mi.position = dir * explode_dist
			mi.set_meta("slice_dir", dir)
			slice_rig.add_child(mi)

	if body_mesh.show_dowel_pins:
		var pin_mesh = body_mesh.get_dowel_pin_mesh()
		var pin_count = body_mesh.get_dowel_pin_count()
		for p in range(pin_count):
			var xf: Transform3D = body_mesh.get_dowel_pin_transform(p)
			var pin_dir: Vector3 = body_mesh.get_dowel_pin_direction(p)
			var pi = MeshInstance3D.new()
			pi.mesh = pin_mesh
			pi.transform = xf
			pi.position = xf.origin + pin_dir * explode_dist
			pi.set_meta("base_origin", xf.origin)
			pi.set_meta("pin_dir", pin_dir)
			pi.material_override = dowel_mat
			pi.name = "DowelPin_%d" % p
			slice_rig.add_child(pi)

func _update_slice_transforms():
	if not is_instance_valid(slice_rig) or not is_instance_valid(body_mesh):
		return
	var explode_dist = body_mesh.explode_distance * 0.001
	for c in slice_rig.get_children():
		if c.has_meta("slice_dir"):
			var dir: Vector3 = c.get_meta("slice_dir")
			c.position = dir * explode_dist
		elif c.has_meta("pin_dir") and c.has_meta("base_origin"):
			var pdir: Vector3 = c.get_meta("pin_dir")
			var borg: Vector3 = c.get_meta("base_origin")
			c.position = borg + pdir * explode_dist

func _on_export_stl_pressed():
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://export"))
	var full_ok = body_mesh.export_full_stl("res://export/guitar_body_full.stl")
	var slices_ok = body_mesh.export_slices_stl("res://export")
	if slices_ok:
		lbl_export_status.text = "STLs exported to res://export/"
		print("[GuitarBuilder] STLs exported to res://export/")
	else:
		lbl_export_status.text = "STL export failed!"

func _on_export_3mf_pressed():
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://export"))
	var res = body_mesh.export_3mf("res://export/guitar_body_slices.3mf")
	if res:
		lbl_export_status.text = "3MF exported to res://export/guitar_body_slices.3mf"
		print("[GuitarBuilder] 3MF exported to res://export/guitar_body_slices.3mf")
	else:
		lbl_export_status.text = "3MF export failed!"

func _on_export_dxf_pressed():
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://export"))
	var res = body_mesh.export_2d_dxf("res://export/guitar_templates.dxf")
	if res:
		lbl_export_status.text = "DXF exported to res://export/guitar_templates.dxf"
		print("[GuitarBuilder] DXF exported to res://export/guitar_templates.dxf")
	else:
		lbl_export_status.text = "DXF export failed!"

func _update_finish_shader():
	if not is_instance_valid(finish_mat) or not is_instance_valid(body_mesh):
		return
	finish_mat.set_shader_parameter("finish_type", option_finish_type.selected)
	finish_mat.set_shader_parameter("base_color", color_base.color)
	finish_mat.set_shader_parameter("color_inner", color_inner.color)
	finish_mat.set_shader_parameter("color_mid", color_mid.color)
	finish_mat.set_shader_parameter("color_rim", color_rim.color)
	finish_mat.set_shader_parameter("burst_falloff", slider_burst_falloff.value)
	finish_mat.set_shader_parameter("waist_pinch", slider_waist_pinch.value)
	finish_mat.set_shader_parameter("flake_sparkle", slider_flake_sparkle.value)
	finish_mat.set_shader_parameter("flame_intensity", slider_flame_intensity.value)
	finish_mat.set_shader_parameter("clearcoat", slider_clearcoat.value)
	finish_mat.set_shader_parameter("clearcoat_roughness", slider_clearcoat_roughness.value)
	var half_w = (body_mesh.hip_width * 0.5) * 0.001
	var half_l = (body_mesh.body_length * 0.5) * 0.001
	finish_mat.set_shader_parameter("body_half_extents", Vector2(half_w, half_l))
	finish_mat.set_shader_parameter("body_center", Vector2(0.0, 0.0))

func _apply_curated_preset(idx: int):
	match idx:
		1: # Vintage 3-Tone Sunburst
			option_finish_type.selected = 1
			color_inner.color = Color(1.0, 0.82, 0.28)
			color_mid.color = Color(0.85, 0.18, 0.08)
			color_rim.color = Color(0.04, 0.02, 0.02)
			slider_burst_falloff.value = 1.7
			slider_waist_pinch.value = 0.45
			slider_clearcoat.value = 0.95
			slider_clearcoat_roughness.value = 0.04
		2: # 2-Tone Tobacco Burst
			option_finish_type.selected = 1
			color_inner.color = Color(0.96, 0.86, 0.52)
			color_mid.color = Color(0.45, 0.22, 0.08)
			color_rim.color = Color(0.05, 0.02, 0.02)
			slider_burst_falloff.value = 1.5
			slider_waist_pinch.value = 0.40
			slider_clearcoat.value = 0.92
			slider_clearcoat_roughness.value = 0.05
		3: # Candy Apple Red Sparkle
			option_finish_type.selected = 2
			color_base.color = Color(0.88, 0.08, 0.12)
			slider_flake_sparkle.value = 1.2
			slider_clearcoat.value = 0.98
			slider_clearcoat_roughness.value = 0.03
		4: # Lake Placid Blue Metallic
			option_finish_type.selected = 2
			color_base.color = Color(0.18, 0.52, 0.78)
			slider_flake_sparkle.value = 1.1
			slider_clearcoat.value = 0.95
			slider_clearcoat_roughness.value = 0.04
		5: # Surf Green '62 Gloss
			option_finish_type.selected = 0
			color_base.color = Color(0.45, 0.78, 0.68)
			slider_clearcoat.value = 0.90
			slider_clearcoat_roughness.value = 0.06
		6: # Olympic White Vintage
			option_finish_type.selected = 0
			color_base.color = Color(0.94, 0.92, 0.85)
			slider_clearcoat.value = 0.88
			slider_clearcoat_roughness.value = 0.08
		7: # Natural Flame Maple Amber
			option_finish_type.selected = 3
			color_inner.color = Color(0.96, 0.75, 0.32)
			color_mid.color = Color(0.48, 0.26, 0.10)
			color_rim.color = Color(0.14, 0.07, 0.03)
			slider_flame_intensity.value = 0.75
			slider_clearcoat.value = 0.96
			slider_clearcoat_roughness.value = 0.04
		8: # Midnight Obsidian Black
			option_finish_type.selected = 0
			color_base.color = Color(0.04, 0.04, 0.05)
			slider_clearcoat.value = 1.00
			slider_clearcoat_roughness.value = 0.02
	_update_finish_shader()

func _save_project_json(path: String = "res://export/guitar_project_v2.json"):
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://export"))
	var proj = {
		"schema_version": "2.0.0",
		"project_metadata": {
			"name": "Custom_Guitar_Design",
			"created_at": Time.get_datetime_string_from_system(true),
			"units": "millimeters"
		},
		"body_spline": {
			"symmetric_mode": body_mesh.symmetric_mode,
			"dimensions": {
				"body_length": body_mesh.body_length,
				"body_thickness": body_mesh.body_thickness,
				"edge_radius": body_mesh.edge_radius,
				"hip_width": body_mesh.hip_width,
				"waist_width": body_mesh.waist_width,
				"chest_width": body_mesh.chest_width,
				"shoulder_width": body_mesh.shoulder_width,
				"treble_hip_width": body_mesh.treble_hip_width,
				"bass_hip_width": body_mesh.bass_hip_width,
				"treble_waist_width": body_mesh.treble_waist_width,
				"bass_waist_width": body_mesh.bass_waist_width,
				"treble_chest_width": body_mesh.treble_chest_width,
				"bass_chest_width": body_mesh.bass_chest_width,
				"horn_reach": body_mesh.horn_reach,
				"horn_roundness": body_mesh.horn_roundness
			},
			"contours": {
				"belly_cut": {
					"enabled": body_mesh.belly_cut_enabled,
					"angle": body_mesh.belly_cut_angle,
					"length": body_mesh.belly_cut_length,
					"depth": body_mesh.belly_cut_depth
				},
				"forearm_bevel": {
					"enabled": body_mesh.forearm_bevel_enabled,
					"angle": body_mesh.forearm_bevel_angle,
					"length": body_mesh.forearm_bevel_length,
					"depth": body_mesh.forearm_bevel_depth
				}
			}
		},
		"shape_preset": option_shape_preset.selected if is_instance_valid(option_shape_preset) else 0,
		"procedural_modifiers": {
			"sphere_modifiers_enabled": body_mesh.sphere_modifiers_enabled,
			"sphere_count": body_mesh.sphere_count,
			"sphere_radius": body_mesh.sphere_radius,
			"cylinder_modifiers_enabled": body_mesh.cylinder_modifiers_enabled,
			"cylinder_count": body_mesh.cylinder_count,
			"cylinder_radius": body_mesh.cylinder_radius,
			"cylinder_angle": body_mesh.cylinder_angle,
			"honeycomb_modifiers_enabled": body_mesh.honeycomb_modifiers_enabled,
			"honeycomb_cell_size": body_mesh.honeycomb_cell_size,
			"modifier_seed": body_mesh.modifier_seed
		},
		"hardware_stack": {
			"pickup_config": body_mesh.pickup_config,
			"bridge_type": body_mesh.bridge_type,
			"bridge_y": body_mesh.bridge_y,
			"bridge_pickup_slant": body_mesh.bridge_pickup_slant,
			"pickup_clearance": body_mesh.pickup_clearance,
			"pickup_depth": body_mesh.pickup_depth,
			"neck_pocket_enabled": body_mesh.neck_pocket_enabled,
			"neck_visible": check_neck.button_pressed if is_instance_valid(check_neck) else true,
			"control_cavity_enabled": body_mesh.control_cavity_enabled,
			"piezo_saddles_enabled": body_mesh.piezo_saddles_enabled
		},
		"slicing_cam": {
			"slicing_enabled": body_mesh.slicing_enabled,
			"slice_grid_type": body_mesh.slice_grid_type,
			"pin_diameter": 6.0,
			"pin_clearance": 0.4
		},
		"visuals": {
			"finish_type": option_finish_type.selected,
			"base_color": color_base.color.to_html(false),
			"color_inner": color_inner.color.to_html(false),
			"color_mid": color_mid.color.to_html(false),
			"color_rim": color_rim.color.to_html(false),
			"burst_falloff": slider_burst_falloff.value,
			"waist_pinch": slider_waist_pinch.value,
			"flake_sparkle": slider_flake_sparkle.value,
			"flame_intensity": slider_flame_intensity.value,
			"clearcoat": slider_clearcoat.value,
			"clearcoat_roughness": slider_clearcoat_roughness.value
		}
	}
	var f = FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(proj, "  "))
		f.close()
		lbl_project_status.text = "Saved v2.0 project to res://export/"
		print("[GuitarBuilder] Saved project schema to " + path)
	else:
		lbl_project_status.text = "Failed to save project file!"

func _load_project_json(path: String = "res://export/guitar_project_v2.json"):
	if not FileAccess.file_exists(path):
		lbl_project_status.text = "File not found: " + path
		return
	var f = FileAccess.open(path, FileAccess.READ)
	if not f:
		lbl_project_status.text = "Failed to open project file"
		return
	var text = f.get_as_text()
	f.close()
	var json = JSON.new()
	var err = json.parse(text)
	if err != OK:
		lbl_project_status.text = "JSON parse error!"
		return
	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		lbl_project_status.text = "Invalid JSON dictionary"
		return

	if data.has("body_spline"):
		var bs = data["body_spline"]
		if bs.has("symmetric_mode"): body_mesh.symmetric_mode = bs["symmetric_mode"]
		if bs.has("dimensions"):
			var d = bs["dimensions"]
			if d.has("body_length"): body_mesh.body_length = d["body_length"]
			if d.has("body_thickness"): body_mesh.body_thickness = d["body_thickness"]
			if d.has("edge_radius"): body_mesh.edge_radius = d["edge_radius"]
			if d.has("hip_width"): body_mesh.hip_width = d["hip_width"]
			if d.has("waist_width"): body_mesh.waist_width = d["waist_width"]
			if d.has("chest_width"): body_mesh.chest_width = d["chest_width"]
			if d.has("horn_reach"): body_mesh.horn_reach = d["horn_reach"]
			if d.has("horn_roundness"): body_mesh.horn_roundness = d["horn_roundness"]
		if bs.has("contours"):
			var c = bs["contours"]
			if c.has("belly_cut"):
				body_mesh.belly_cut_enabled = c["belly_cut"].get("enabled", true)
				body_mesh.belly_cut_angle = c["belly_cut"].get("angle", 18.0)
				body_mesh.belly_cut_length = c["belly_cut"].get("length", 190.0)
				body_mesh.belly_cut_depth = c["belly_cut"].get("depth", 14.0)
			if c.has("forearm_bevel"):
				body_mesh.forearm_bevel_enabled = c["forearm_bevel"].get("enabled", true)
				body_mesh.forearm_bevel_angle = c["forearm_bevel"].get("angle", 15.0)
				body_mesh.forearm_bevel_length = c["forearm_bevel"].get("length", 170.0)
				body_mesh.forearm_bevel_depth = c["forearm_bevel"].get("depth", 12.0)

	if data.has("hardware_stack"):
		var hw = data["hardware_stack"]
		if hw.has("pickup_config"): body_mesh.pickup_config = hw["pickup_config"]
		if hw.has("bridge_type"): body_mesh.bridge_type = hw["bridge_type"]
		if hw.has("bridge_y"): body_mesh.bridge_y = hw["bridge_y"]
		if hw.has("bridge_pickup_slant"): body_mesh.bridge_pickup_slant = hw["bridge_pickup_slant"]
		if hw.has("neck_pocket_enabled"): body_mesh.neck_pocket_enabled = hw["neck_pocket_enabled"]
		if hw.has("neck_visible") and is_instance_valid(check_neck): check_neck.button_pressed = hw["neck_visible"]
		if hw.has("control_cavity_enabled"): body_mesh.control_cavity_enabled = hw["control_cavity_enabled"]
		if hw.has("piezo_saddles_enabled"): body_mesh.piezo_saddles_enabled = hw["piezo_saddles_enabled"]

	if data.has("shape_preset") and is_instance_valid(option_shape_preset):
		option_shape_preset.selected = data["shape_preset"]

	if data.has("procedural_modifiers"):
		var pm = data["procedural_modifiers"]
		if pm.has("sphere_modifiers_enabled"): body_mesh.sphere_modifiers_enabled = pm["sphere_modifiers_enabled"]
		if pm.has("sphere_count"): body_mesh.sphere_count = pm["sphere_count"]
		if pm.has("sphere_radius"): body_mesh.sphere_radius = pm["sphere_radius"]
		if pm.has("cylinder_modifiers_enabled"): body_mesh.cylinder_modifiers_enabled = pm["cylinder_modifiers_enabled"]
		if pm.has("cylinder_count"): body_mesh.cylinder_count = pm["cylinder_count"]
		if pm.has("cylinder_radius"): body_mesh.cylinder_radius = pm["cylinder_radius"]
		if pm.has("cylinder_angle"): body_mesh.cylinder_angle = pm["cylinder_angle"]
		if pm.has("honeycomb_modifiers_enabled"): body_mesh.honeycomb_modifiers_enabled = pm["honeycomb_modifiers_enabled"]
		if pm.has("honeycomb_cell_size"): body_mesh.honeycomb_cell_size = pm["honeycomb_cell_size"]
		if pm.has("modifier_seed"): body_mesh.modifier_seed = pm["modifier_seed"]

	if data.has("visuals"):
		var v = data["visuals"]
		if v.has("finish_type"): option_finish_type.selected = v["finish_type"]
		if v.has("base_color"): color_base.color = Color.from_string(v["base_color"], Color(0.85, 0.14, 0.16))
		if v.has("color_inner"): color_inner.color = Color.from_string(v["color_inner"], Color(1.0, 0.82, 0.28))
		if v.has("color_mid"): color_mid.color = Color.from_string(v["color_mid"], Color(0.85, 0.18, 0.08))
		if v.has("color_rim"): color_rim.color = Color.from_string(v["color_rim"], Color(0.05, 0.02, 0.02))
		if v.has("burst_falloff"): slider_burst_falloff.value = v["burst_falloff"]
		if v.has("waist_pinch"): slider_waist_pinch.value = v["waist_pinch"]
		if v.has("flake_sparkle"): slider_flake_sparkle.value = v["flake_sparkle"]
		if v.has("flame_intensity"): slider_flame_intensity.value = v["flame_intensity"]
		if v.has("clearcoat"): slider_clearcoat.value = v["clearcoat"]
		if v.has("clearcoat_roughness"): slider_clearcoat_roughness.value = v["clearcoat_roughness"]

	_sync_ui_from_mesh()
	_update_hardware_visuals()
	_update_finish_shader()
	lbl_project_status.text = "Loaded v2.0 project from " + path
	print("[GuitarBuilder] Loaded project schema from " + path)

func _reset_project_defaults():
	body_mesh.body_length = 460.0
	body_mesh.body_thickness = 45.0
	body_mesh.edge_radius = 12.0
	body_mesh.hip_width = 320.0
	body_mesh.waist_width = 228.0
	body_mesh.chest_width = 276.0
	body_mesh.horn_reach = 430.0
	body_mesh.horn_roundness = 1.2
	body_mesh.symmetric_mode = true
	body_mesh.belly_cut_enabled = true
	body_mesh.forearm_bevel_enabled = true
	_apply_curated_preset(1) # Default 3-tone burst
	_sync_ui_from_mesh()
	_update_hardware_visuals()
	lbl_project_status.text = "Reset all parameters to factory defaults"

func _check_cli_capture():
	var args = OS.get_cmdline_args() + OS.get_cmdline_user_args()
	var should_exit = false
	if "--test-cuts-front" in args:
		check_forearm.button_pressed = true
		check_belly.button_pressed = true
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-cuts-back" in args:
		check_forearm.button_pressed = true
		check_belly.button_pressed = true
		camera_pivot.rotation = Vector3(-0.25, PI + 0.4, 0.0)
		should_exit = true
	elif "--test-short-horns" in args:
		slider_horn_reach.value = 405.0
		slider_horn_roundness.value = 1.6
		camera_pivot.rotation = Vector3(0.0, 0.0, 0.0)
		should_exit = true
	elif "--test-sharp-horns" in args:
		slider_horn_reach.value = 460.0
		slider_horn_roundness.value = 0.65
		camera_pivot.rotation = Vector3(0.0, 0.0, 0.0)
		should_exit = true
	elif "--test-cuts" in args:
		check_forearm.button_pressed = true
		check_belly.button_pressed = true
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-asym" in args:
		check_symmetric.button_pressed = false
		should_exit = true
	elif "--test-hardware-front" in args:
		option_pickups.selected = 1
		body_mesh.pickup_config = 1
		option_bridge.selected = 0
		body_mesh.bridge_type = 0
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-cavities-wiring" in args:
		option_pickups.selected = 1
		body_mesh.pickup_config = 1
		option_bridge.selected = 0
		body_mesh.bridge_type = 0
		check_hardware_models.button_pressed = false
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		camera.position.z = 0.95
		should_exit = true
	elif "--test-hardware-tremolo" in args:
		option_pickups.selected = 2
		body_mesh.pickup_config = 2
		option_bridge.selected = 1
		body_mesh.bridge_type = 1
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-piezo" in args:
		_switch_ui_mode(1)
		body_mesh.bridge_enabled = true
		body_mesh.piezo_saddles_enabled = true
		check_piezo.button_pressed = true
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		var center_y = (body_mesh.body_length * 0.5) * 0.001
		var by_world = body_mesh.bridge_y * (body_mesh.body_length / 446.0) * 0.001 - center_y
		camera_pivot.position = Vector3(0.0, by_world, 0.0)
		camera_pivot.rotation = Vector3(-0.75, 0.0, 0.0)
		camera.position = Vector3(0.0, 0.0, 0.22)
		should_exit = true
	elif "--test-piezo-wood" in args:
		_switch_ui_mode(1)
		body_mesh.bridge_enabled = true
		body_mesh.piezo_saddles_enabled = true
		check_piezo.button_pressed = true
		check_hardware_models.button_pressed = false
		hardware_rig.visible = false
		var center_y = (body_mesh.body_length * 0.5) * 0.001
		var by_world = body_mesh.bridge_y * (body_mesh.body_length / 446.0) * 0.001 - center_y
		camera_pivot.position = Vector3(0.015, by_world + 0.01, 0.0)
		camera_pivot.rotation = Vector3(-0.6, 0.25, 0.0)
		camera.position = Vector3(0.0, 0.0, 0.22)
		should_exit = true
	elif "--test-nopiezo-wood" in args:
		_switch_ui_mode(1)
		body_mesh.bridge_enabled = true
		body_mesh.piezo_saddles_enabled = false
		check_piezo.button_pressed = false
		check_hardware_models.button_pressed = false
		hardware_rig.visible = false
		var center_y = (body_mesh.body_length * 0.5) * 0.001
		var by_world = body_mesh.bridge_y * (body_mesh.body_length / 446.0) * 0.001 - center_y
		camera_pivot.position = Vector3(0.015, by_world + 0.01, 0.0)
		camera_pivot.rotation = Vector3(-0.6, 0.25, 0.0)
		camera.position = Vector3(0.0, 0.0, 0.22)
		should_exit = true
	elif "--test-piezo-back" in args:
		_switch_ui_mode(1)
		body_mesh.bridge_enabled = true
		body_mesh.piezo_saddles_enabled = true
		check_piezo.button_pressed = true
		check_hardware_models.button_pressed = false
		hardware_rig.visible = false
		var center_y = (body_mesh.body_length * 0.5) * 0.001
		var by_world = body_mesh.bridge_y * (body_mesh.body_length / 446.0) * 0.001 - center_y
		camera_pivot.position = Vector3(0.0, by_world, 0.0)
		camera_pivot.rotation = Vector3(-0.35, PI, 0.0)
		camera.position = Vector3(0.0, 0.0, 0.22)
		should_exit = true
	elif "--test-hardware-back" in args:
		check_control_cavity.button_pressed = true
		body_mesh.control_cavity_enabled = true
		camera_pivot.rotation = Vector3(-0.25, PI + 0.4, 0.0)
		should_exit = true
	elif "--test-jack-closeup" in args:
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.15, 1.25, 0.0)
		camera.position.z = 0.85
		should_exit = true
	elif "--test-jack-morph" in args:
		slider_hip.value = 390.0
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.15, 1.25, 0.0)
		camera.position.z = 0.85
		should_exit = true
	elif "--test-slices-8way" in args:
		_switch_ui_mode(2)
		check_slicing.button_pressed = true
		body_mesh.slicing_enabled = true
		option_grid.selected = 1
		body_mesh.slice_grid_type = 2
		slider_explode.value = 25.0
		body_mesh.explode_distance = 25.0
		check_dowel_pins.button_pressed = true
		body_mesh.show_dowel_pins = true
		check_color_slices.button_pressed = true
		_update_slice_visuals()
		camera_pivot.rotation = Vector3(-0.45, 0.55, 0.0)
		camera.position.z = 1.30
		should_exit = true
	elif "--test-ui-default" in args:
		_switch_ui_mode(0)
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-slices-4way" in args:
		check_slicing.button_pressed = true
		body_mesh.slicing_enabled = true
		option_grid.selected = 0
		body_mesh.slice_grid_type = 1
		slider_explode.value = 25.0
		body_mesh.explode_distance = 25.0
		check_dowel_pins.button_pressed = true
		body_mesh.show_dowel_pins = true
		check_color_slices.button_pressed = true
		_update_slice_visuals()
		camera_pivot.rotation = Vector3(-0.45, 0.55, 0.0)
		camera.position.z = 1.30
		should_exit = true
	elif "--test-export" in args:
		body_mesh.slicing_enabled = true
		body_mesh.slice_grid_type = 2
		_on_export_stl_pressed()
		_on_export_3mf_pressed()
		_on_export_dxf_pressed()
		should_exit = true
	elif "--test-finish-sunburst" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 1
		_apply_curated_preset(1)
		camera_pivot.rotation = Vector3(-0.35, 0.40, 0.0)
		camera.position.z = 1.05
		should_exit = true
	elif "--test-finish-sparkle" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 3
		_apply_curated_preset(3)
		camera_pivot.rotation = Vector3(-0.35, 0.40, 0.0)
		camera.position.z = 1.05
		should_exit = true
	elif "--test-finish-flame" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 7
		_apply_curated_preset(7)
		camera_pivot.rotation = Vector3(-0.35, 0.40, 0.0)
		camera.position.z = 1.05
		should_exit = true
	elif "--test-finish-surfgreen" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 5
		_apply_curated_preset(5)
		camera_pivot.rotation = Vector3(-0.35, 0.40, 0.0)
		camera.position.z = 1.05
		should_exit = true
	elif "--test-finish-front" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 1
		_apply_curated_preset(1)
		camera_pivot.rotation = Vector3(0.0, 0.0, 0.0)
		camera.position.z = 1.15
		should_exit = true
	elif "--test-finish-side" in args:
		_switch_ui_mode(3)
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 1
		_apply_curated_preset(1)
		camera_pivot.rotation = Vector3(-0.15, 1.15, 0.0)
		camera.position.z = 1.15
		should_exit = true
	elif "--test-neck" in args:
		_switch_ui_mode(1)
		check_hardware_models.button_pressed = true
		check_neck.button_pressed = true
		_update_hardware_visuals()
		option_preset.selected = 1
		_apply_curated_preset(1)
		camera_pivot.rotation = Vector3(-0.25, 0.35, 0.0)
		camera_pivot.position = Vector3(0.0, 0.28, 0.0)
		camera.position.z = 1.85
		should_exit = true
	elif "--test-modifiers-spheres" in args:
		_switch_ui_mode(0)
		body_mesh.sphere_modifiers_enabled = true
		body_mesh.sphere_count = 18
		body_mesh.sphere_radius = 22.0
		_sync_ui_from_mesh()
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		camera.position.z = 1.0
		should_exit = true
	elif "--test-modifiers-cylinders" in args:
		_switch_ui_mode(0)
		body_mesh.sphere_modifiers_enabled = false
		body_mesh.cylinder_modifiers_enabled = true
		body_mesh.cylinder_count = 14
		body_mesh.cylinder_radius = 9.0
		_sync_ui_from_mesh()
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		camera.position.z = 1.0
		should_exit = true
	elif "--test-modifiers-honeycomb" in args:
		_switch_ui_mode(0)
		body_mesh.sphere_modifiers_enabled = false
		body_mesh.cylinder_modifiers_enabled = false
		body_mesh.honeycomb_modifiers_enabled = true
		body_mesh.honeycomb_cell_size = 22.0
		_sync_ui_from_mesh()
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		camera.position.z = 1.0
		should_exit = true
	elif "--test-presets" in args:
		_switch_ui_mode(0)
		_apply_shape_preset(1) # LP Single-Cut
		check_hardware_models.button_pressed = true
		check_neck.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.25, 0.35, 0.0)
		camera_pivot.position = Vector3(0.0, 0.15, 0.0)
		camera.position.z = 1.40
		should_exit = true
	elif "--test-preset-sg" in args:
		_switch_ui_mode(0)
		_apply_shape_preset(2) # SG Double-Cut
		check_hardware_models.button_pressed = true
		check_neck.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.25, 0.35, 0.0)
		camera_pivot.position = Vector3(0.0, 0.15, 0.0)
		camera.position.z = 1.40
		should_exit = true
	elif "--test-preset-v" in args:
		_switch_ui_mode(0)
		_apply_shape_preset(4) # Flying V
		check_hardware_models.button_pressed = true
		check_neck.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.25, 0.35, 0.0)
		camera_pivot.position = Vector3(0.0, 0.15, 0.0)
		camera.position.z = 1.40
		should_exit = true
	elif "--test-save-load" in args:
		_switch_ui_mode(3)
		var orig_len = body_mesh.body_length
		option_preset.selected = 1
		_apply_curated_preset(1)
		_save_project_json()
		# Mutate parameter
		body_mesh.body_length = orig_len + 30.0
		# Reload
		_load_project_json()
		assert(abs(body_mesh.body_length - orig_len) < 0.1, "Project load restored body length")
		print("[GuitarBuilder] Project schema v2.0 save/load verified successfully!")
		should_exit = true

	if should_exit or "--screenshot" in args or "--capture" in args:
		await get_tree().create_timer(0.6).timeout
		var img = get_viewport().get_texture().get_image()
		img.save_png("res://preview.png")
		print("[GuitarBuilder] Saved screenshot to res://preview.png")
		get_tree().quit()

func _unhandled_input(event):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT or (event.button_index == MOUSE_BUTTON_LEFT and event.alt_pressed):
			is_orbiting = event.pressed
			last_mouse_pos = event.position
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP:
			camera.position.z = max(0.4, camera.position.z - zoom_speed)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			camera.position.z = min(3.0, camera.position.z + zoom_speed)

	elif event is InputEventMouseMotion and is_orbiting:
		var delta = event.position - last_mouse_pos
		last_mouse_pos = event.position
		camera_pivot.rotation.y -= delta.x * orbit_speed
		camera_pivot.rotation.x = clamp(camera_pivot.rotation.x - delta.y * orbit_speed, -1.4, 1.4)
