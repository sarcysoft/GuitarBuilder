extends Node3D

@onready var body_mesh = $GuitarBodyMesh
@onready var camera_pivot = $CameraPivot
@onready var camera = $CameraPivot/Camera3D

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

# Asymmetric Treble Sliders
@onready var slider_t_hip = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleHip
@onready var slider_t_waist = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleWaist
@onready var slider_t_chest = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleChest
@onready var slider_t_horn = $UI/Panel/Scroll/VBox/AsymmetricControls/GridTreble/SliderTrebleHorn

# Asymmetric Bass Sliders
@onready var slider_b_hip = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassHip
@onready var slider_b_waist = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassWaist
@onready var slider_b_chest = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassChest
@onready var slider_b_horn = $UI/Panel/Scroll/VBox/AsymmetricControls/GridBass/SliderBassHorn

# Ergonomic Cuts
@onready var check_belly = $UI/Panel/Scroll/VBox/CheckBellyCut
@onready var belly_controls = $UI/Panel/Scroll/VBox/BellyControls
@onready var slider_belly_angle = $UI/Panel/Scroll/VBox/BellyControls/SliderBellyAngle
@onready var slider_belly_length = $UI/Panel/Scroll/VBox/BellyControls/SliderBellyLength

@onready var check_forearm = $UI/Panel/Scroll/VBox/CheckForearm
@onready var forearm_controls = $UI/Panel/Scroll/VBox/ForearmControls
@onready var slider_forearm_angle = $UI/Panel/Scroll/VBox/ForearmControls/SliderForearmAngle
@onready var slider_forearm_length = $UI/Panel/Scroll/VBox/ForearmControls/SliderForearmLength

# Camera navigation state
var is_orbiting = false
var last_mouse_pos = Vector2.ZERO
var orbit_speed = 0.005
var zoom_speed = 0.05

func _ready():
	_setup_default_material()
	_sync_ui_from_mesh()
	_connect_signals()
	_check_cli_capture()

func _setup_default_material():
	if not body_mesh:
		return
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.85, 0.14, 0.16) # Candy Apple Fiesta Red
	mat.metallic = 0.15
	mat.roughness = 0.22
	mat.clearcoat_enabled = true
	mat.clearcoat = 0.9
	mat.clearcoat_roughness = 0.08
	mat.cull_mode = BaseMaterial3D.CULL_BACK
	body_mesh.material_override = mat

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

	slider_t_hip.value = body_mesh.treble_hip_width
	slider_t_waist.value = body_mesh.treble_waist_width
	slider_t_chest.value = body_mesh.treble_chest_width
	slider_t_horn.value = body_mesh.treble_horn_length

	slider_b_hip.value = body_mesh.bass_hip_width
	slider_b_waist.value = body_mesh.bass_waist_width
	slider_b_chest.value = body_mesh.bass_chest_width
	slider_b_horn.value = body_mesh.bass_horn_length

	check_belly.button_pressed = body_mesh.belly_cut_enabled
	belly_controls.visible = body_mesh.belly_cut_enabled
	slider_belly_angle.value = body_mesh.belly_cut_angle
	slider_belly_length.value = body_mesh.belly_cut_length

	check_forearm.button_pressed = body_mesh.forearm_bevel_enabled
	forearm_controls.visible = body_mesh.forearm_bevel_enabled
	slider_forearm_angle.value = body_mesh.forearm_bevel_angle
	slider_forearm_length.value = body_mesh.forearm_bevel_length

func _connect_signals():
	# Global
	slider_length.value_changed.connect(func(v): body_mesh.body_length = v)
	slider_thickness.value_changed.connect(func(v): body_mesh.body_thickness = v)
	slider_radius.value_changed.connect(func(v): body_mesh.edge_radius = v)

	# Symmetry
	check_symmetric.toggled.connect(func(v):
		body_mesh.symmetric_mode = v
		symmetric_controls.visible = v
		asymmetric_controls.visible = not v
	)

	# Unified Symmetric
	slider_hip.value_changed.connect(func(v):
		body_mesh.hip_width = v
		slider_t_hip.value = v * 0.5
		slider_b_hip.value = v * 0.5
	)
	slider_waist.value_changed.connect(func(v):
		body_mesh.waist_width = v
		slider_t_waist.value = v * 0.5
		slider_b_waist.value = v * 0.5
	)
	slider_chest.value_changed.connect(func(v):
		body_mesh.chest_width = v
		slider_t_chest.value = v * 0.5
		slider_b_chest.value = v * 0.5
	)
	slider_shoulder.value_changed.connect(func(v):
		body_mesh.shoulder_width = v
		slider_t_horn.value = body_mesh.treble_horn_length
		slider_b_horn.value = body_mesh.bass_horn_length
	)

	# Asymmetric Treble
	slider_t_hip.value_changed.connect(func(v): body_mesh.treble_hip_width = v)
	slider_t_waist.value_changed.connect(func(v): body_mesh.treble_waist_width = v)
	slider_t_chest.value_changed.connect(func(v): body_mesh.treble_chest_width = v)
	slider_t_horn.value_changed.connect(func(v): body_mesh.treble_horn_length = v)

	# Asymmetric Bass
	slider_b_hip.value_changed.connect(func(v): body_mesh.bass_hip_width = v)
	slider_b_waist.value_changed.connect(func(v): body_mesh.bass_waist_width = v)
	slider_b_chest.value_changed.connect(func(v): body_mesh.bass_chest_width = v)
	slider_b_horn.value_changed.connect(func(v): body_mesh.bass_horn_length = v)

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

func _check_cli_capture():
	var args = OS.get_cmdline_user_args()
	if "--test-cuts" in args:
		check_forearm.button_pressed = true
		check_belly.button_pressed = true
		camera_pivot.rotation.y = 0.6
		camera_pivot.rotation.x = -0.3
	elif "--test-asym" in args:
		check_symmetric.button_pressed = false

	if "--screenshot" in args or "--capture" in args or "--test-cuts" in args or "--test-asym" in args:
		await get_tree().create_timer(0.4).timeout
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
		camera_pivot.rotation.x = clamp(camera_pivot.rotation.x + delta.y * orbit_speed, -1.4, 1.4)
