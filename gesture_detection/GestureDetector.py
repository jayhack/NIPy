#!/usr/bin/python
# ------------------------------------------------------------ #
# Class: GestureDetector
# ----------------------
# Class for detecting gestures in motion sequences
# 
# ------------------------------------------------------------ #
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..classification.GenerativeModel import GenerativeModel

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

class GestureDetector:

	# Function: Constructor
	# ---------------------
	# creates all of the generative models
	def __init__ (self, _gestures_dict):

		#===[ Get Generative Models]===
		self.gestures_dict = _gestures_dict
		self.generative_models = self.get_generative_models ()


	# Function: get_generative_models
	# -------------------------------
	# creates a GenerativeModel object for each gesture name, returns
	# as a dict mapping gesture name -> GenerativeModel
	def get_generative_models (self):

		return {n: GenerativeModel (e) for n, e in self.gestures_dict.items ()}


	# Function: detect 
	# ----------------
	# given a MotionSequence, applies all GenerativeModels to it
	def detect (self, ms):

		index = 0
		for df in ms.iter_dataframes ():
			print index
			index += 1
			print [name for name, model in self.generative_models.items () if model.detect (df)]


    


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












