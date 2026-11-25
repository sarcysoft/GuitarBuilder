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

# Materials for Hardware
var chrome_mat: StandardMaterial3D
var black_plastic_mat: StandardMaterial3D
var cream_mat: StandardMaterial3D

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
	_check_cli_capture()

func _setup_materials():
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
	slider_t_hip.value_changed.connect(func(v): body_mesh.treble_hip_width = v)
	slider_t_waist.value_changed.connect(func(v): body_mesh.treble_waist_width = v)
	slider_t_chest.value_changed.connect(func(v): body_mesh.treble_chest_width = v)
	slider_t_horn.value_changed.connect(func(v): body_mesh.treble_horn_length = v)
	slider_t_roundness.value_changed.connect(func(v): body_mesh.treble_horn_roundness = v)

	# Asymmetric Bass
	slider_b_hip.value_changed.connect(func(v): body_mesh.bass_hip_width = v)
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

	var cc_x = 55.0
	var cc_y = 150.0

	var pot_positions = [
		Vector2(cc_x + 8.0, cc_y + 35.0),
		Vector2(cc_x + 5.0, cc_y - 5.0),
		Vector2(cc_x - 5.0, cc_y - 40.0)
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
	var edge_x = (t_hip * 0.945) * 0.001
	var center_y = 240.0 * scale_y * 0.001
	var edge_y = (70.0 * scale_y) * 0.001 - center_y
	var edge_z = 0.0 # mid-body rim where coaxial tunnel emerges

	jack_group.position = Vector3(edge_x, edge_y, edge_z)
	# Align to lower bout perimeter rim normal
	jack_group.rotation = Vector3(0.0, deg_to_rad(85.0), deg_to_rad(-34.0))

	# Football baseplate (oval shape)
	var plate = MeshInstance3D.new()
	var cyl = CylinderMesh.new()
	cyl.top_radius = 0.012
	cyl.bottom_radius = 0.012
	cyl.height = 0.002
	plate.mesh = cyl
	plate.scale = Vector3(1.0, 1.0, 2.0)
	plate.rotation.x = PI * 0.5
	plate.material_override = chrome_mat
	jack_group.add_child(plate)

	# 1/4" Jack hex nut
	var nut = MeshInstance3D.new()
	var nut_mesh = CylinderMesh.new()
	nut_mesh.top_radius = 0.006
	nut_mesh.bottom_radius = 0.006
	nut_mesh.height = 0.003
	nut_mesh.radial_segments = 6 # 6-sided hex nut
	nut.mesh = nut_mesh
	nut.rotation.x = PI * 0.5
	nut.position = Vector3(0.0, 0.0, 0.0015)
	nut.material_override = chrome_mat
	jack_group.add_child(nut)

	# Center 1/4" socket hole
	var socket_hole = MeshInstance3D.new()
	var sock_mesh = CylinderMesh.new()
	sock_mesh.top_radius = 0.0032
	sock_mesh.bottom_radius = 0.0032
	sock_mesh.height = 0.004
	socket_hole.mesh = sock_mesh
	socket_hole.rotation.x = PI * 0.5
	socket_hole.position = Vector3(0.0, 0.0, 0.002)
	socket_hole.material_override = black_plastic_mat
	jack_group.add_child(socket_hole)

	# 2 Chrome mounting screws
	for s_sign in [-1.0, 1.0]:
		var screw = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.0016
		s_mesh.height = 0.0016
		screw.mesh = s_mesh
		screw.position = Vector3(0.0, s_sign * 0.018, 0.001)
		screw.material_override = chrome_mat
		jack_group.add_child(screw)

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
	elif "--test-hardware-tremolo" in args:
		option_pickups.selected = 2
		body_mesh.pickup_config = 2
		option_bridge.selected = 1
		body_mesh.bridge_type = 1
		check_hardware_models.button_pressed = true
		_update_hardware_visuals()
		camera_pivot.rotation = Vector3(-0.35, 0.45, 0.0)
		should_exit = true
	elif "--test-hardware-back" in args:
		check_control_cavity.button_pressed = true
		body_mesh.control_cavity_enabled = true
		camera_pivot.rotation = Vector3(-0.25, PI + 0.4, 0.0)
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
