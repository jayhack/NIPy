#-------------------------------------------------- #
# Class: StorageDelegate
# ----------------------
# takes care of all storage, including recordings,
# classifiers, figures and more
#-------------------------------------------------- #
import os
import sys
import pickle
import time
import pandas as pd
from ..interface.util import *
from ..motion_sequence.MotionSequence import *



# Function: ensure_dir_exists 
# ---------------------------
# given a directory name (i.e. that of a gesture), this will ensure that it exists
# by actually making it if it doesnt; 
def ensure_dir_exists (dir_name):

	if not os.path.isdir (dir_name):
		os.mkdir (dir_name)


# Function: get_new_filepath
# --------------------------
# returns a novel filename in directory 'dir_name' w/ extension 'extension'
def get_new_filepath (dir_name, extension):

	return os.path.join (dir_name, str(time.time()) + '.dataframe')  





class StorageDelegate:

	# Function: Constructor
	# ---------------------
	# initialize by passing in data_dir, the path to the directory containing
	# all of your data
	def __init__ (self, data_dir):

		#===[ Get Filestructure ]===
		self.build_filestructure (data_dir)

		#===[ Get contents of filestructure ]===
		self.update_filesystem_snapshot ()



	########################################################################################################################
	##############################[ --- INITIALIZATION/MAINTENANCE --- ]####################################################
	########################################################################################################################

	# Function: build_filestructure
	# -----------------------------
	# fills out self.filenames given a path to the data
	# directory, makes sure the filestructure exists as such.
	def build_filestructure (self, data_dir):
	
		#===[ get filestructure ]===
		self.filenames = {}
		self.filenames['data_dir'] 			= data_dir
		self.filenames['classifiers_dir']	= os.path.join (self.filenames['data_dir'], 'classifiers')
		self.filenames['gestures_dir']		= os.path.join (self.filenames['data_dir'], 'gestures')
		self.filenames['recordings_dir'] 	= os.path.join (self.filenames['data_dir'], 'recordings')
		self.filenames['figures_dir']		= os.path.join (self.filenames['data_dir'], 'figures')

		#===[ ensure the full structure is there ]===
		for d in self.filenames.values ():
			ensure_dir_exists (d)


	# Function: update_filesystem_snapshot
	# ------------------------------------
	# fills in self.filesystem w/ up-to-date information
	def update_filesystem_snapshot (self):

		### Step 1: motion_sequences ###
		current_gestures = os.listdir (self.filenames['gestures_dir'])
		self.filenames['gestures_dirs'] = {gesture: os.path.join (self.filenames['gestures_dir'], gesture) for gesture in current_gestures}
		
		### Step 2: classifiers ###

		### Step 3: recordings ###







	########################################################################################################################
	##############################[ --- GESTURES --- ]######################################################################
	########################################################################################################################

	# Function: get_gesture_dir
	# --------------------------
	# given a gesture, returns the directory containing recordings of it
	def get_gesture_dir (self, gesture_name):

		return os.path.join(self.filenames['gestures_dir'], gesture_name)


	# Function: get_existing_gestures
	# -------------------------------
	# returns a list of all of the existing gestures
	def get_existing_gestures (self):

		self.update_filesystem_snapshot ()
		return os.listdir(self.filenames['gestures_dir'])


	# Function: gesture_exists 
	# -------------------------
	# returns true <=> the specified gesture already exists in the filesystem
	def gesture_exists (self, gesture_name):

		if gesture_name in self.get_existing_gestures ():
			return True
		else:
			return False


	# Function: make_gesture
	# ----------------------
	# given the name of a gesture, makes a directory to store it
	def make_gesture (self, gesture_name):

		ensure_dir_exists(self.get_gesture_dir (gesture_name))


	# Function: ensure_gesture_exists
	# -------------------------------
	# given the name of a gesture, ensures that there is storage for it
	def ensure_gesture_exists (self, gesture_name):

		if not self.gesture_exists (gesture_name):
			self.make_gesture (gesture_name)


	# Function: get_gesture_recordings_list
	# -------------------------------------
	# given the name of a gesture, returns the names of all gestures recorded 
	def get_gesture_recordings_list (self, gesture_name):

		self.update_filesystem_snapshot ()
		return os.listdir (self.get_gesture_dir (gesture_name))


	# Function: get_num_gesture_recordings
	# ------------------------------------
	# given the name of a gesture, returns the number of recordings currently on record
	def get_gesture_num_recordings (self, gesture_name):

		return len (self.get_gesture_recordings_list (gesture_name))


	# Function: get_gesture_recording_filepaths
	# -----------------------------------------
	# given the name of a gesture, returns the filepaths to all recordings of it
	# as a list
	def get_gesture_recording_filepaths (self, gesture_name):

		if not self.gesture_exists (gesture_name):
			return []
		else:
			gesture_dir = self.get_gesture_dir (gesture_name)
			return [os.path.join (gesture_dir, r) for r in os.listdir (gesture_dir)]


	# Function: get_new_gesture_recording_filepath
	# --------------------------------------------
	# given a gesture name, this returns the full filepath of where
	# the next recording should be saved. Ensures the gesture exists.
	def get_new_gesture_recording_filepath (self, gesture_name):

		self.ensure_gesture_exists (gesture_name)
		return get_new_filepath (self.get_gesture_dir(gesture_name), '.gesture')


	# Function: save_gesture_recording 
	# --------------------------------
	# saves 'motion_sequence,' which contains a recording of a gesture, as an instance
	# of the gesture named 'gesture_name'
	def save_gesture_recording (self, motion_sequence, gesture_name):

		pickle.dump (motion_sequence.get_dataframe (), open(self.get_new_gesture_recording_filepath (gesture_name), 'w'))


	# Function: get_gesture_recordings
	# --------------------------------
	# given the name of a gesture, returns a list of all recordings of it 
	# (returns as MotionSequences)
	def get_gesture_recordings (self, gesture_name):

		if not self.gesture_exists (gesture_name):
			return []
		else:
			return [PlayBackMotionSequence(pickle.load (open(ms, 'r'))) for ms in self.get_gesture_recording_filepaths (gesture_name)]








	########################################################################################################################
	##############################[ --- CLASSIFIERS --- ]###################################################################
	########################################################################################################################

	# Function: get_classifier_filepath
	# ---------------------------------
	# given the classifier's name, returns a filepath to it
	def get_classifier_filepath (self, classifier_name):

		return os.path.join(self.filenames['classifiers_dir'], classifier_name + '.classifier')


	# Function: classifier_exists
	# ---------------------------
	# returns true if the named classifier exist
	def classifier_exists (self, classifier_name):

		return os.path.exists (self.get_classifier_filepath (classifier_name))


	# Function: save_classifier
	# -------------------------
	# Paramters (2):
	#	- classifier: sklearn classifier
	#	- classifier_name: name to save it as
	# Description:
	#	given a classifier/name to save it as, this will save it
	def save_classifier (self, classifier, classifier_name):

		pickle.dump(classifier, open(self.get_classifier_filepath (classifier_name), 'w'))


	# Function: load_classifier
	# -------------------------
	# Parameters (1):
	#	- classifier_name: name of the activity that you want recordings of
	# Description:
	# 	given the name of a classifier this function will unpickle/return it
	def load_classifier (self, classifier_name):

		if not self.classifier_exists (classifier_name):
			return None
		else:
			return pickle.load (open(self.get_classifier_filepath (classifier_name), 'r'))








	########################################################################################################################
	##############################[ --- RECORDINGS --- ]###################################################################
	########################################################################################################################

	# Function: get_recording_filepaths
	# ---------------------------------
	# returns the full filepath to all recordings in a list
	def get_recording_filepaths (self):

		return [os.path.join (self.filenames['recordings_dir'], r) for r in os.listdir (self.filenames['recordings_dir'])]


	# Function: save_recording 
	# ------------------------
	# saves a given recording
	def save_recording (self, recording):

		filepath = self.get_new_recording_filepath (self.filenames['recordings_dir'])
		pickle.dump (recording, open (filepath, 'w'))


	# Function: get_recording 
	# -----------------------
	# given the name of a recording, loads and retrieves it
	def get_recording (self, recording_name):
		full_filepath = os.path.join (self.filenames['recordings_dir'], recording_name)
		recording = pd.read_pickle (full_filepath)
		return recording


	# Function: load_recordings
	# -------------------------
	# returns a list of all recordings
	def load_recordings (self):

		return [pickle.load (open(f, 'r')) for f in self.get_recording_filepaths ()]





