#-------------------------------------------------- #
# Class: Visualizer
# -----------------
# class for creating visualizations of NI data
#-------------------------------------------------- #
from ..motion_sequence.MotionSequence import MotionSequence
from ..motion_sequence.MotionSequence import usec_to_sec
from ..motion_sequence.MotionSequence import PlayBackMotionSequence
from ..classification.FeatureFunctions import lower_time_resolution
from ..interface.util import print_message, print_status
from .parameters import parameters

#==========[ Matplotlib tools	]==========
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, RadioButtons


class Visualizer:
	"""
		Abstract Class: Visualizer
		--------------------------
		Class for visualizing motion sequences 
	"""


	def __init__ (self):
		pass


	def play (self, ms):
		"""
			PUBLIC: play
			------------
			visualizes the given motion sequence
		"""

		if ms.__class__ is PlayBackMotionSequence:
			self.play_PlayBack (ms)

		elif ms.__class__ is RealTimeMotionSequence:
			self.play_RealTime (ms)

		else:
			raise TypeError ("Visualizer does not support the following type: " + str (ms.__class__))


	def play_PlayBack (self, ms):
		""" 
			PRIVATE, OVERRIDE: play_PlayBack
			--------------------------------
			visualization function for PlayBackMotionSequences
		"""
		raise NotImplementedError


	def play_RealTime (self, ms):
		""" 
			PRIVATE, OVERRIDE: play_RealTime
			--------------------------------
			visualization function for RealTimeMotionSequences
		"""
		raise NotImplementedError


#==========[ PrimesenseVisualizer	]==========
class PrimesenseVisualizer (Visualizer):
	"""
		Class: PrimesenseVisualizer
		---------------------------
		Visualizer for data received from the Primesense 
	"""

	limb_joint_pairs = 	[
							('JOINT_HEAD_POSITION', 'JOINT_NECK_POSITION'),
							('JOINT_NECK_POSITION', 'JOINT_LEFT_SHOULDER_POSITION'),
							('JOINT_NECK_POSITION', 'JOINT_RIGHT_SHOULDER_POSITION'),
							('JOINT_LEFT_SHOULDER_POSITION', 'JOINT_LEFT_ELBOW_POSITION'),
							('JOINT_RIGHT_SHOULDER_POSITION', 'JOINT_RIGHT_ELBOW_POSITION'),
							('JOINT_LEFT_ELBOW_POSITION', 'JOINT_LEFT_HAND_POSITION'),
							('JOINT_RIGHT_ELBOW_POSITION', 'JOINT_RIGHT_HAND_POSITION'),
							('JOINT_NECK_POSITION', 'JOINT_TORSO_POSITION'),
							('JOINT_TORSO_POSITION', 'JOINT_LEFT_HIP_POSITION'),
							('JOINT_TORSO_POSITION', 'JOINT_RIGHT_HIP_POSITION'),
							('JOINT_LEFT_HIP_POSITION', 'JOINT_LEFT_KNEE_POSITION'),
							('JOINT_RIGHT_HIP_POSITION', 'JOINT_RIGHT_KNEE_POSITION'),
							('JOINT_LEFT_KNEE_POSITION', 'JOINT_LEFT_FOOT_POSITION'),
							('JOINT_RIGHT_KNEE_POSITION', 'JOINT_RIGHT_FOOT_POSITION')
						]


	def __init__ (self):
		"""
			PUBLIC: Constructor
			-------------------
			creates all static aspects of the plot
		"""
		#=====[ Create figure/axes	]=====
		self.fig 			= plt.figure (figsize=plt.figaspect(1)*1.5)
		self.ax 			= Axes3D (self.fig, rect=[0, 0.2, 1, 0.8], axisbg='#B0B0B0')
		self.ax_progress 	= plt.axes([0, 0, 1, 0.1], axisbg='#B0B0B0')
		self.ax_play	 	= plt.axes([0, 0.1, 0.5, 0.1])
		self.ax_mark	 	= plt.axes([0.5, 0.1, 0.5, 0.1])		
		self.ax.set_zticks ([])

		#=====[ Create/initialize controls	]=====
		self.init_controls ()





	####################################################################################################
	##############################[ --- CONTROLS --- ]##################################################
	####################################################################################################

	def init_controls (self):
		"""
			PRIVATE: init_controls
			----------------------
			sets all parameters that will be used for controls
		"""
		#=====[ Create controls	]=====
		self.progress_slider 	= Slider (self.ax_progress, 'Freq', 0, 1, valinit=0, color='#B31217')
		self.play_button 		= Button (self.ax_play, 'Play/Pause')
		self.mark_button 		= Button (self.ax_mark, 'Mark')

		#=====[ Connect callbacks	]=====
		self.progress_slider.on_changed (self.progress_callback)
		self.play_button.on_clicked (self.play_callback)
		self.mark_button.on_clicked (self.mark_callback)
	
		#=====[ Init relevant data	]=====
		self.current_frame_index = 0
		self.old_progress = 0
		self.paused = False


	def progress_callback (self, val):
		"""
			PRIVATE: progress_callback
			--------------------------
			callback for progress slider; changes point in 
			animation 
		"""
		pass


	def progress_moved (self):
		"""
			PRIVATE: progress_moved
			-----------------------
			returns true if the progress bar was moved 
		"""
		changed = False
		if abs(self.old_progress - self.progress_slider.val) > 0.01:
			changed = True
		self.old_progress = self.progress_slider.val 
		return changed


	def play_callback (self, event):
		"""
			PRIVATE: play_callback
			----------------------
			callback function for play button; pauses/resumes animation 
		"""
		self.paused = not self.paused


	def mark_callback (self, event):
		"""
			PRIVATE: mark_callback
			----------------------
			callback function for mark button; marks current point 
			in animation
		"""	
		pass


	def interpret_controls (self, ms):
		"""
			PRIVATE: interpret_controls
			---------------------------
			called in each animation cycle; interprets and manages
			the controls
		"""
		# num_frames = len(ms.get_dataframe())

		#=====[ Step 1: deal with progress slider ]===
		# if self.progress_moved ():
			# self.current_frame_index = int(self.progress_slider.val*num_frames)

		#=====[ Step 2: deal with pausing ]=====
		if not self.paused:
			self.current_frame_index += 1
			# self.progress_slider.set_val (float(self.current_frame_index) / float(num_frames))

		#=====[ Step 3: change slider position ]=====
		# self.progress_slider.set_val(float(self.current_frame_index) / float(num_frames))





	####################################################################################################
	##############################[ --- SETTING UP PLOT --- ]###########################################
	####################################################################################################

	def is_position_key (self, key):
		"""
			PRIVATE: is_position_key
			------------------------
			returns true if the key passed in maps to a position
		"""
		return key[-8:] == 'POSITION'


	def get_ms_stats (self, ms):
		"""	
			PRIVATE: get_ms_stats
			---------------------
			gathers statistics on movement within the motion sequence,
			including centroid of motion and boundaries
		"""
		#==========[ Step 1: get dataframe, columns	]==========
		df 					= ms.get_dataframe ()
		position_columns 	= [i for i in df.columns if self.is_position_key (i)]

		#==========[ Step 2: get list of all x, y, z coordinates	]==========
		xs = np.array([f['x'] for pos_col in position_columns for f in df[pos_col]]).flatten ()
		ys = np.array([f['y'] for pos_col in position_columns for f in df[pos_col]]).flatten ()
		zs = np.array([f['z'] for pos_col in position_columns for f in df[pos_col]]).flatten ()				

		#==========[ Step 3: compute centroid, shifted motion boundaries	]==========
		centroid = (np.mean(xs), np.mean(ys), np.mean(zs))
		x_lims = (np.min(xs) - centroid[0] - 200, np.max(xs) - centroid[0] + 200)
		y_lims = (np.min(ys) - centroid[1], np.max(ys) - centroid[1])
		z_lims = (np.min(zs) - centroid[2] - 200, np.max(zs) - centroid[2] + 200)		
		return centroid, x_lims, y_lims, z_lims


	def init_plot (self, ms):
		"""
			PRIVATE: init_plot
			------------------
			sets plot aspect ratio and bounds such that the body
			actually looks like a body; sets colors
		"""
		#==========[ Step 1: get centroid/limits for all dimensions ]==========
		self.centroid, self.x_lims, self.y_lims, self.z_lims = self.get_ms_stats (ms)
		self.y_floor = -640

		#==========[ Step 2: set limits ]==========
		self.ax.set_xlim (self.x_lims)
		self.ax.set_zlim (0, self.y_lims[1] - self.y_lims[0])#self.y_lims)
		self.ax.set_ylim (self.z_lims)		

		#==========[ Step 3: set aspect ratio	]==========
		x_span = self.x_lims[1] - self.x_lims[0]
		y_span = self.y_lims[1] - self.y_lims[0]
		z_span = self.z_lims[1] - self.z_lims[0]

		self.ax.set_aspect (x_span/z_span)





	####################################################################################################
	##############################[ --- DRAWING ON PLOT --- ]###########################################
	####################################################################################################

	def plot_line (self, p1, p2):
		"""
			PRIVATE: plot_line
			------------------
			given two points, plots a line between them
			necessary because matplotlib screws up the axes for us...
		"""
		xs = [p1['x'], p2['x']]
		ys = [p1['y'], p2['y']]
		zs = [p1['z'], p2['z']]
		return self.ax.plot (xs, zs, ys, color='#780000', linewidth=4, marker='o', markersize=12)


	def shift (self, frame, origin):
		"""
			PRIVATE: shift
			--------------
			given a frame, shifts it to the provided origin
		""" 
		joint_coords = {k:v for k, v in frame.items () if self.is_position_key(k)}

		return {	
				
					k:	{	
							'x':v['x'] - origin[0], 
							'y':v['y'] - self.y_floor,
							'z':v['z'] - origin[2]	
						} 
					
						for k, v in joint_coords.items ()
				}


	def update_animation (self, num, limbs, ms):
		"""
			PRIVATE: update_animation
			-------------------------
			callback function for animation; updates all limbs on screen
		"""
		#=====[ Step 1: interpret controls	]=====
		self.interpret_controls (ms)

		#=====[ Step 2: get correct frame	]=====
		current_frame = dict(ms.get_dataframe ().iloc [self.current_frame_index])

		#=====[ Step 3: apply shift to frame	]=====
		current_frame = self.shift(current_frame, self.centroid)

		#==========[ Step 4: update each limb with frame data	]==========
		for limb, joint_pair in zip(limbs, self.limb_joint_pairs):

			xs = [current_frame[joint_pair[0]]['x'], current_frame[joint_pair[1]]['x']]
			ys = [current_frame[joint_pair[0]]['y'], current_frame[joint_pair[1]]['y']]
			zs = [current_frame[joint_pair[0]]['z'], current_frame[joint_pair[1]]['z']]						

			limb = limb[0]
			limb.set_data (xs, zs)
			limb.set_3d_properties (ys)

		if num >= len(ms.get_dataframe()) - 2:
			ms.reset () 

		return limbs






	####################################################################################################
	##############################[ --- PLAYING --- ]###################################################
	####################################################################################################

	def play_PlayBack (self, ms):
		""" 	
			PUBLIC: play_PlayBack
			---------------------
			visualization function for PlayBackMotionSequences
		"""
		#==========[ Step 1: initialize limbs	]==========
		limbs = [self.ax.plot([], [], [], color='#A57257', linewidth=6, marker='o', markersize=12) for jp in self.limb_joint_pairs]

		#==========[ Step 2: initialize the plot	]==========
		self.init_plot (ms)

		#==========[ Step 3: create the animation	]==========
		limb_ani = animation.FuncAnimation(self.fig, self.update_animation, frames=len(ms.get_dataframe()), fargs=(limbs, ms), blit=False, interval=1)

		#==========[ Step 4: show the plot and exit	]==========
		plt.show ()


	def play_RealTime (self, ms):
		"""
			PUBLIC: play_RealTime
			---------------------
			visualization function for RealTimeMotionSequences
		"""
		raise NotImplementedError








# class Visualizer_OLD:


# 	# Function: add_relative_timestamp
# 	# --------------------------------
# 	# given a dataframe, this adds a 'relative_timestamp' field, in seconds
# 	def add_relative_timestamp (self, ms):

# 		df = ms.get_dataframe ()
# 		df['relative_timestamp'] = df['timestamp'].map(lambda x: (x - df.iloc[0]['timestamp'])/1000000.0)


# 	# Function: plot_dimension
# 	# ------------------------
# 	# plots the given dimension of the ms w/r/t x_axis
# 	def plot_dimension (self, ms, plot_dim, x_axis):

# 		df = ms.get_dataframe ()
# 		if not plot_dim in df.columns:
# 			print_error ("visualizer.plot_dimension", "you asked to plot nonexistant dimension: " + plot_dim)
# 		if x_axis:
# 			if not x_axis in df.columns:
# 				print_error ("visualizer.plot_dimension", "you asked to plot nonexistant x_axis: " + x_axis)	

# 		if x_axis:
# 			plt.plot (df[x_axis], df[plot_dim], self.plot_colors[plot_dim])
# 		else:
# 			plt.plot (df[plot_dim], self.plot_colors[plot_dim])


# 	# Function: plot_palm_xyz
# 	# -----------------------
# 	# plots the xyz coordinates of a motion sequence w/r/t x_axis
# 	def plot_palm_xyz (self, ms, x_axis):

# 		for plot_dim in ['palm_x', 'palm_y', 'palm_z']:
# 			self.plot_dimension (ms, plot_dim, x_axis)


# 	# Function: plot_palm_ypr
# 	# ----------------------
# 	# plots the yaw/pitch/roll coordinates of a motion sequence w/r/t x_axis
# 	def plot_palm_ypr (self, ms, x_axis):

# 		for plot_dim in ['yaw', 'pitch', 'roll']:
# 			self.plot_dimension (ms, plot_dim, x_axis)


# 	# Function: plot_score
# 	# --------------------
# 	# plots score of a monitor over time
# 	def plot_monitor_reaction (self, ms, x_axis):

# 		for plot_dim in ['monitor_score']:
# 			self.plot_dimension (ms, plot_dim, x_axis)


# 	# Function: plot_motion_sequence
# 	# ------------------------------
# 	# plots a single motion sequence, including x/y/z/y/p/r,
# 	# w/r/t relative timestamp
# 	def plot_motion_sequence (self, ms, x_axis='relative_timestamp', xlabel='relative timestamp'):

# 		self.add_relative_timestamp (ms)
# 		self.plot_palm_xyz (ms, x_axis)
# 		# self.plot_palm_ypr (ms, 'relative_timestamp')
# 		plt.xlabel (xlabel)
# 		plt.ylabel ('Coordinates')


# 	# Function: plot_gesture_recordings 
# 	# ---------------------------------
# 	# given a list of gesture recordings, this will downsample appropriately
# 	# and print them all on the same axis
# 	def plot_gesture_recordings (self, gesture_recordings):
		
# 		low_res_motion_sequences = [PlayBackMotionSequence(lower_time_resolution (r.get_dataframe ())) for r in gesture_recordings]
# 		print [len(ms) for ms in low_res_motion_sequences]
# 		for ms in low_res_motion_sequences:
# 			self.plot_motion_sequence (ms, x_axis=None, xlabel='length-normalized timestep')


# 	# Function: visualize_monitor
# 	# ---------------------------
# 	# given a gesture monitor and a recording, this will visualize
# 	# how the monitor reacts to the motion sequence (defined by the
# 	# monitor's 'current_reaction' method)
# 	def visualize_monitor (self, monitor, motion_sequence):

# 		#===[ initialize monitor ]===
# 		monitor.attach (motion_sequence)	# attach the monitor to the motion sequence
# 		monitor.start ()					# and start it

# 		#===[ associate reaction w/ each frame ]===
# 		frames = []
# 		for frame in motion_sequence.iter_frames ():
# 			score = monitor.get_current_reaction ()
# 			frame.update ({'monitor_score':score})
# 			print frame
# 			frames.append (frame)
# 		ms = PlayBackMotionSequence(pd.DataFrame (frames))

# 		#===[ plot it ]===
# 		self.plot_motion_sequence (ms, x_axis='relative_timestamp')
# 		self.plot_monitor_reaction (ms, x_axis='relative_timestamp')


# 	# Function: show
# 	# --------------
# 	# displays the final plot
# 	def show (self):
# 		plt.show ()


# 	# Function: clear 
# 	# ---------------
# 	# starts a new plot
# 	def clear (self):
# 		plt.clear ()






    # # Function: plot_recording_dimension
    # # ----------------------------------
    # # given a recording and its title, this will plot it
    # def plot_recording_dimension (self, recording, dim_name, recording_color):
        
    #     plt.plot (recording[dim_name], color=recording_color)
    #     plt.title (dim_name)


    # # Function: plot_recording
    # # ------------------------
    # # given a recording, this plots it
    # def plot_recording (self, recording):
    #     dim_colors = {  
    #                     'palm_x': 'red',
    #                     'palm_y': 'blue',
    #                     'palm_z': 'green'
    #     }   
    #     for dim_name, dim_color in dim_colors.items():
    #         self.plot_recording_dimension (recording, dim_name, dim_color)


    # # Function: plot_gesture_recordings
    # # ---------------------------------
    # # for each gesture, plot its palm_(x|y|z) on the same axis
    # def plot_gesture_recordings (self):

    #     self.get_gesture_recordings ()
    #     for gesture_name, gesture_recordings in self.gesture_recordings.items ():

    #         for r in gesture_recordings:
    #             self.plot_recording (r)
    #         plt.title (gesture_name + '_examples')
    #         plt.savefig (gesture_name + '_examples.png')
    #         plt.close ()
