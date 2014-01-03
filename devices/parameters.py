parameters = {
	'connect_address':"tcp://localhost:5555",
}
device_filters = { 
					'primesense':'__primesense__',
					'leap':'__leap__',
					'eyetribe':'__eyetribe__'
}
column_names = {
	'leap': ['timestamp', 'yaw', 'hands', 'fingers', 'palm_z', 'palm_y', 'palm_x', 'pitch', 'hand_sphere_radius', 'roll']
}