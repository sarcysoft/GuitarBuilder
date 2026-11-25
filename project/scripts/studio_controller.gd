extends Node3D

@onready var body_mesh = $GuitarBodyMesh
@onready var camera_pivot = $CameraPivot
@onready var camera = $CameraPivot/Camera3D

# UI Sliders
@onready var slider_hip = $UI/Panel/VBox/Grid/SliderHip
@onready var slider_waist = $UI/Panel/VBox/Grid/SliderWaist
@onready var slider_chest = $UI/Panel/VBox/Grid/SliderChest
@onready var slider_shoulder = $UI/Panel/VBox/Grid/SliderShoulder
@onready var slider_length = $UI/Panel/VBox/Grid/SliderLength
@onready var slider_thickness = $UI/Panel/VBox/Grid/SliderThickness
@onready var slider_radius = $UI/Panel/VBox/Grid/SliderRadius
@onready var check_symmetric = $UI/Panel/VBox/CheckSymmetric
@onready var check_belly = $UI/Panel/VBox/CheckBellyCut
@onready var check_forearm = $UI/Panel/VBox/CheckForearm

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
	body_mesh.material_override = mat

func _sync_ui_from_mesh():
	if not body_mesh:
		return
	slider_hip.value = body_mesh.hip_width
	slider_waist.value = body_mesh.waist_width
	slider_chest.value = body_mesh.chest_width
	slider_shoulder.value = body_mesh.shoulder_width
	slider_length.value = body_mesh.body_length
	slider_thickness.value = body_mesh.body_thickness
	slider_radius.value = body_mesh.edge_radius
	check_symmetric.button_pressed = body_mesh.symmetric_mode
	check_belly.button_pressed = body_mesh.belly_cut_enabled
	check_forearm.button_pressed = body_mesh.forearm_bevel_enabled

func _connect_signals():
	slider_hip.value_changed.connect(func(v): body_mesh.hip_width = v)
	slider_waist.value_changed.connect(func(v): body_mesh.waist_width = v)
	slider_chest.value_changed.connect(func(v): body_mesh.chest_width = v)
	slider_shoulder.value_changed.connect(func(v): body_mesh.shoulder_width = v)
	slider_length.value_changed.connect(func(v): body_mesh.body_length = v)
	slider_thickness.value_changed.connect(func(v): body_mesh.body_thickness = v)
	slider_radius.value_changed.connect(func(v): body_mesh.edge_radius = v)
	check_symmetric.toggled.connect(func(v): body_mesh.symmetric_mode = v)
	check_belly.toggled.connect(func(v): body_mesh.belly_cut_enabled = v)
	check_forearm.toggled.connect(func(v): body_mesh.forearm_bevel_enabled = v)

func _check_cli_capture():
	var args = OS.get_cmdline_user_args()
	if "--screenshot" in args or "--capture" in args:
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
		camera_pivot.rotation.x = clamp(camera_pivot.rotation.x - delta.y * orbit_speed, -1.4, 1.4)
