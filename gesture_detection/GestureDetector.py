#!/usr/bin/python
# ------------------------------------------------------------ #
# Class: Detection
# ----------------
# functions involved in detecting gestures, activities
# requires a 'frame_source' and a 'classifier'
# 
# ------------------------------------------------------------ #

#--- Numpy ---
import numpy as np

#--- Pandas ---
import pandas as pd

#--- MatPlotLib ---
import matplotlib.pyplot as plt

#--- My Files ---
from PlayBack import PlayBack
from util import *

########################################################################################################################
##############################[ --- UTILITIES --- ]#####################################################################
########################################################################################################################

# Function: sec_to_usec
# ---------------------
# converts seconds to microseconds
def sec_to_usec (sec):
	
	return sec*1000000


# Function: start_time_to_index
# -----------------------------
# given start time, returns the index of the time slice closest to it
def start_time_to_index (df, start_time):

	return np.argmin (np.abs(df['timestamp'] - start_time))


# Function: end_time_to_index
# ---------------------------
# given start time, returns the index of the time slice closest to it
def end_time_to_index (df, end_time):

	return np.argmin (np.abs(df['timestamp'] - end_time))


# Function: temporal_subsample
# ----------------------------
# given two times within the recording, this will return
# the portion of the dataframe that occurs between
def temporal_subsample (df, start_time, end_time):

	return df.loc[start_time_to_index (df, start_time) : end_time_to_index (df, end_time)]


# Function: extract_last_n_seconds
# --------------------------------
# given a dataframe and secs, this will return the portion
# of the dataframe that occured over the last n seconds
def extract_last_n_seconds (df, secs):

	### Step 1: get desired start/end timestamps ###
	end_time 	= df.iloc[-1]['timestamp']
	start_time 	= end_time - sec_to_usec (secs)

	### Step 2: try to temporal subsample, return none if impossible ###
	try:
		return temporal_subsample (df, start_time, end_time)
	except ValueError:
		return None


# Function: get_hand_gone_indices
# ----------------------------------
# given a dataframe of hand frames, returns a series where the index 
# maps to true if the hand is gone
def get_hand_gone_indices (df):

    return df['hands'] == 0


# Function: hand_leaves
# ---------------------
# given a dataframe of hand frames, returns true if the hand ever leaves
# the recording
def hand_leaves (df):

    return np.any(get_hand_gone_indices (df))





########################################################################################################################
##############################[ --- GESTURE --- ]#######################################################################
########################################################################################################################

# class: Gesture
# --------------
# container to represent a single detected gesture
class Gesture:

	# Function: constructor
	# ---------------------
	# pass in gesture name, window you detected it in
	def __init__ (self, _name, _window):

		### name of this gesture ###
		self.name = _name
		
		### start/end indices ###
		self.start_index = _window.iloc[0].name
		self.end_index = _window.iloc[-1].name

		### stard/end timestamps ###
		self.start_timestamp = _window.iloc[0]['timestamp']
		self.end_timestamp = _window.iloc[-1]['timestamp']




########################################################################################################################
##############################[ --- DETECTOR --- ]######################################################################
########################################################################################################################

class Detector:

	#===[ Frame Source ]===
	frame_source = None

	#===[ Classification ]===


	# Function: Constructor
	# ---------------------
	def __init__ (self):
		pass




    ########################################################################################################################
    ##############################[ --- Detecting Gestures --- ]############################################################
    ########################################################################################################################

	# Function: get_valid_window 
	# --------------------------
	# given a list of frames, returns most recent window of specified timespan
	# if it contains a hand for its entirety, None otherwise
	def get_valid_window (self, total_df, timespan=0.7):
		
		### Step 1: get total dataframe ###
		if len(total_df) < 20:
			return None

		### Step 2: get window ###
		window_df = extract_last_n_seconds (total_df, timespan)
		if not window_df:
			return None


		### Step 3: validate window ###
		if not hand_leaves (window_df):
			return window_df
		else:
			return None


	# Function: get_valid_windows
	# ---------------------------
	# returns a list of valid windows
	def get_valid_windows (self, total_df, timespans=[0.4, 0.5, 0.6, 0.7, 0.75]):
		windows = [self.get_valid_window (total_df, t) for t in timespans]
		return [w for w in windows if w]

	

	# Function: detect_gesture
	# ------------------------
	# Parameters (2):
	# 	- frames: list of frames to find gestures in
	# 	- classifier: Classifier object to take care of classification
	# Description:
	# 	extracts windows from 'frames,' returns a list of Gesture objects
	# 	found in 'frames'
	# def detect_gesture (self, frames, classifier):

	# 	### Step 1: get valid windows ###
	# 	valid_windows = self.get_valid_windows (frames)

	# 	### Step 2: classify each window ###
	# 	gestures = []
	# 	for v in valid_windows:

	# 		gesture_name = classifier.classify (v)

	# 		if gesture_name:
	# 			new_gesture = Gesture (gesture_name, v)
	# 			gestures.append (new_gesture)

	# 	return gestures


	# Function: detect_gestures
	# -------------------------
	# given a frame source, this returns a list of gestures
	def detect_gestures (self, frame_source, classifier):

		gesture_names = ['swirl', 'swirl_cc']

		gestures = []
		frames = []
		for frame in frame_source.get_frames ():
			frames.append (frame)
			frames_df = pd.DataFrame (frames)

			windows = self.get_valid_windows (frames_df)
			for window in windows:
				scores = classifier.classify (window)
				print scores
				if np.max(scores) > -270:
					index = np.argmax (scores)
					new_gesture = Gesture (gesture_names[index], window)
					gestures.append (new_gesture)
					frames = []
					break

		return gestures





	# Function: find_gesture_probabilities
	# ------------------------------------
	# Parameters (2):
	#	- frame_source: playback or real-time source of frames
	#	- classifier: something to go from window -> prob dist. over gestures
	# Description:
	#	returns a dict Map: gesture_name -> p(gesture) for each index of frame_source
	def find_gesture_probabilities (self, frame_source, classifier):

		p_dist = [[], []]
		def update_p_dist (pd, new_values):
			if new_values == None:
				pd[0].append (0.0)
				pd[1].append (0.0)
			else:
				pd[0].append (new_values[0])
				pd[1].append (new_values[1])

		frames = []
		for frame in frame_source.get_frames ():

			frames.append (frame)
			frames_df = pd.DataFrame(frames)

			windows = get_valid_windows (frames_df)


			update_p_dist (p_dist, new_values)

			if len(frames) >= 200:
				frames.pop (0)

		return p_dist



    ########################################################################################################################
    ##############################[ --- Visualization --- ]#################################################################
    ########################################################################################################################

	# Function: plot_gesture 
	# ----------------------
	# given a gesture, this will plot it on the current plot
	def plot_gesture (self, gesture, gesture_color, marker='o'):

		gesture_X = range (int(gesture.start_index), int(gesture.end_index))
		gesture_y = [0 for x in gesture_X]
		plt.plot (gesture_X, gesture_y, 'o', color=gesture_color)


	# Function: plot_recording_dimension
	# ----------------------------------
	# given a recording and its title, this will plot it
	def plot_recording_dimension (self, recording, dim_name, recording_color):
        
		plt.plot (recording[dim_name], color=recording_color)
		plt.title (dim_name)


	# Function: plot_recording
	# ------------------------
	# given a recording, this plots it
	def plot_recording (self, recording):
		dim_colors = {	
						'palm_x': 'red',
						'palm_y': 'blue',
						'palm_z': 'green'
		}	
		for dim_name, dim_color in dim_colors.items():
			self.plot_recording_dimension (recording, dim_name, dim_color)
 

	# Function: visualize_gestures
	# ----------------------------
	# given a recording and gestures detected in it, plots them all 
	# together
	def visualize_recording (self, recording, gestures):

		#==========[ COLOR CODES ]==========
		dim_colors = {	
						'palm_x': 'red',
						'palm_y': 'blue',
						'palm_z': 'green'
		}			
		gesture_colors = {

						'swirl': 'cyan',
						'swirl_cc': 'magenta'
		}

		### Step 1: plot all hand movement ###
		self.plot_recording (recording)

		### Step 2: plot all detected gestures ###
		for g in gestures:
			self.plot_gesture (g, gesture_colors[g.name])

		### Step 3: annotate figure/save/visualize ###
		plt.title ('Gestures detected in recording (purple = detected gesture)')
		plt.xlabel ('timestamp')
		plt.ylabel ('coordinate')
		plt.savefig ('detected_gestures')
		plt.show ()


	# Function: visualize_recording_gesture_probs
	# -------------------------------------------
	# given a recording and two distributions over the gestures,
	# this plots them
	def visualize_recording_gesture_probs (self, recording, gesture_probs):

		### Step 1: plot the recording ###
		self.plot_recording (recording)
		plt.title ('recording')
		plt.savefig ('recording.png')
		plt.close ()

		### Step 2: plot the probability distributions ###
		plt.plot (gesture_probs[0], color='green')
		plt.plot (gesture_probs[1], color='red')
		plt.savefig('gesture_probs.png')
		plt.close ()


	# Function: detect_and_visualize 
	# ------------------------------
	# given a frame source (playback), this will detect gestures in it 
	# and then provide a visualization of its detected gestures
	def detect_and_visualize (self, recording, classifier):
		print_header ("Detect and Visualize")

		### Step 1: run detection on playback of the recording (get gestures) ###
		playback = PlayBack (recording)
		print_status ("Detect", "Getting dist. over gestures")
		gestures = self.detect_gestures (playback, classifier)
		# gesture_probs = self.find_gesture_probabilities (playback, classifier)

		### Step 2: visualize the recording and the gestures ###
		print_status ("Visualize", "Displaying palm motion, getures")
		self.visualize_recording (recording, gestures)
		# self.visualize_recording_gesture_probs (recording, gesture_probs)
		# print gesture_probs[0]












