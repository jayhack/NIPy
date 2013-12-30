# -------------------------------------------------- #
# File: FeatureFunctions
# ----------------------
# contains all feature extracting functions
# (functions that take in a dataframe, returns features)
# as well as FeatureExtractor classes
# -------------------------------------------------- #
import math
from collections import Counter
import pickle
import pandas as pd
import numpy as np
import scipy
from sklearn.hmm import GaussianHMM
from sklearn.preprocessing import scale
from ..interface.util import *
from copy import copy



########################################################################################################################
##############################[ --- UTILITIES --- ]#####################################################################
########################################################################################################################

# Function: lower_time_resolution
# -------------------------------
# given a dataframe and the number of frames desired,
# this returns a new dataframe w/ the desired number of frames,
# each (roughly) evenly spaced
def lower_time_resolution (df, new_res=10):

	elapsed_time = df.iloc[-1]['timestamp'] - df.iloc[0]['timestamp']
	desired_interval = int(float(elapsed_time) / float(new_res - 1))

	include_series = []
	time_knotch = df.iloc[0]['timestamp']
	for index in range (len(df)):

		if df.iloc[index]['timestamp'] >= time_knotch: 
			include_series.append (df.iloc[index])
			time_knotch += desired_interval

	return pd.DataFrame (include_series)


# Function: add_velocity_acceleration
# -----------------------------------
# given a hand df, adds velocity/acceleration values for the hand
# on palm_(x|y|z), (yaw|pitch|roll)
def add_velocity_acceleration (df):

	### Step 1: velocity column ###
	df ['v_py'] 	= df['palm_y'].diff ()
	df ['v_px'] 	= df['palm_x'].diff ()
	df ['v_pz'] 	= df['palm_z'].diff ()
	df ['v_pitch']	= df['pitch'].diff ()
	df ['v_roll']	= df['roll'].diff ()
	df ['v_yaw']	= df['yaw'].diff ()

	### Step 2: acceleration ###
	df ['a_py'] 	= df ['v_py'].diff ()
	df ['a_px'] 	= df ['v_px'].diff ()
	df ['a_pz'] 	= df ['v_pz'].diff ()
	df ['a_pitch']	= df ['v_pitch'].diff ()
	df ['a_roll']	= df ['v_roll'].diff ()
	df ['a_yaw']	= df ['v_yaw'].diff ()


	### Step 3: get rid of nans ###
	df['v_py'].iloc[0] = 0.0
	df['v_px'].iloc[0] = 0.0
	df['v_pz'].iloc[0] = 0.0	
	df['v_pitch'].iloc[0] = 0.0
	df['v_roll'].iloc[0] = 0.0
	df['v_yaw'].iloc[0] = 0.0

	df['a_py'].iloc[0] = 0.0
	df['a_px'].iloc[0] = 0.0
	df['a_pz'].iloc[0] = 0.0	
	df['a_pitch'].iloc[0] = 0.0
	df['a_roll'].iloc[0] = 0.0
	df['a_yaw'].iloc[0] = 0.0
	df['a_py'].iloc[1] = 0.0
	df['a_px'].iloc[1] = 0.0
	df['a_pz'].iloc[1] = 0.0	
	df['a_pitch'].iloc[1] = 0.0
	df['a_roll'].iloc[1] = 0.0
	df['a_yaw'].iloc[1] = 0.0


	return df


# Function: add_relative_position
# -------------------------------
# changes positions to relative (palm_x -> px)
def add_relative_position (df):

	def get_relative (series):
		mean = np.mean (series)
		return series.map (lambda x: x - mean)

	df['px'] = get_relative (df['palm_x'])
	df['py'] = get_relative (df['palm_y'])
	df['pz'] = get_relative (df['palm_z'])		

	return df


# Function: get_cleaned_dataframe 
# -------------------------------
# returns a dataframe w/ relative positions, pitch, roll, yaw velocity, accel
# and that's it
def get_cleaned_dataframe (df):

	df = lower_time_resolution (df, new_res=10)
	# df = add_relative_position (df)
	df = add_velocity_acceleration (df)
	df = df.drop (['fingers', 'hand_sphere_radius', 'hands', 'palm_x', 'palm_y', 'palm_z', 'timestamp'], 1)
	return df


# Function: av_matrix
# -------------------
# returns a numpy matrix containing only acceleration, velocity features
def av_matrix (df):

	return np.matrix (get_cleaned_dataframe (df))


# Function: get_elapsed_time
# --------------------------
# given a recording, returns the elapsed time, 
def get_elapsed_time (recording):
	
	return recording['timestamp'].iloc[-1] - recording['timestamp'].iloc[0]



# Function: get_valid_recordings
# ------------------------------
# evaluates all recordings contained in raw_recordings, returns only those
# that satisfy indicator_function
# (indicator function )
def get_valid_recordings (raw_recordings_list, evaluation_function):

	return [r for r in raw_recordings_list if evaluation_function (r)]




########################################################################################################################
##############################[ --- Validators --- ]############################################################
########################################################################################################################

# Class: Validator
# ----------------
# abstract class for all classes that take in a recording
# and return wether it is 'valid' or not.
class Validator ():

	def __init__ (self, recordings_list):
		pass

	def evaluate (self, recording):
		pass


# Class: DefaultValidator
# -----------------------
# returns true for all recordingss
class DefaultValidator (Validator):

	def evaluate (self, recording):
		return True


# Class: TimeValidator
# --------------------
# validates based on proximity (in std dev) to 
# to the mean elapsed time in all recordings in the list
class TimeValidator (Validator):

	def __init__ (self, r_list, threshold_std_dev=0.3):

		ets = [get_elapsed_time(r) for r in r_list]
		self.mean 		= np.mean (ets)
		self.std_dev 	= np.std (ets)	
		self.threshold 	= threshold_std_dev*self.std_dev

	def evaluate (self, recording):

		if abs(get_elapsed_time(recording) - self.mean) < self.threshold:
			return True
		else:
			return False



########################################################################################################################
##############################[ --- Feature Extractors --- ]############################################################
########################################################################################################################

# Class: FeatureExtractor
# -----------------------
# abstract class for all feature-extraction classes.
class FeatureExtractor ():

	# Function: Constructor
	# ---------------------
	# Parameters (1):
	#	- raw_recordings_dict: Map: label -> list of raw recordings
	# Description: 
	# 	pass a dict of raw recordings, this trains the feature extraction
	# 	function (if necessary)
	def __init__ (self):
		pass


	# Function: extract
	# -----------------
	# Parameters (2):
	#	- raw_recording: dataframe containing a recording 
	# Description:
	#	given a dataframe containign a recording, this returns a numpy
	#	array containing a feature representation of it
	def extract (self, raw_recording):
		pass


# FeatureExtractor: BaselineFeatureExtractor
# ------------------------------------------
# - downsamples recording w/ lower_time_resolution
# - retains fields: 
#	- palm_(x|y|z)
#	- (yaw|pitch|roll)
#	- (fingers|hands)
class BaselineFeatureExtractor (FeatureExtractor):

	def extract (self, raw_recording):

		recording = lower_time_resolution (raw_recording)
		recording = recording.drop (['timestamp', 'hand_sphere_radius'])
		return np.matrix (recording)



# FeatureExtractor: AVFeatureExtractor 
# --------------------------
# - downsamples recording w/ lower_time_resolution
# - returns w/ relative position, acceleration and velocity features
class AVFeatureExtractor (FeatureExtractor):

	def extract (self, raw_recording):

		return np.array(av_matrix (copy(raw_recording)))



# FeatureExtractor: CompressedAVFeatureExtractor
# ----------------------------------------------
# AVFeatureExtractor, except every column is distilled to mean, stddev,
# min, max
class CompressedAVFeatureExtractor (FeatureExtractor):

	def extract (self, recording_dataframe):

		avm = av_matrix (copy(recording_dataframe))
		stats_functions = [np.mean, np.std, np.max, np.min]
		stats = []
		for f in stats_functions:
			stats += np.mean(avm, axis=0).tolist()[0]
		return np.array(stats)


# FeatureExtractor: HMMScoreFeatureExtractor 
# -------------------------------------
# uses HMMs on relative position/velocity/acceleration data
# to extract features;
# returns an array of the scores of the HMMs
# gets above 0.95 accuracy on 5-fold CV
class HMMScoreFeatureExtractor (FeatureExtractor):


	# Function: get_av_matrices 
	# -------------------------
	# returns a dict Map: label -> list of av matrices
	def get_av_matrices (self, recordings):

		for label in recordings:
			recordings[label] = [np.array(av_matrix(r)) for r in recordings[label]]
		return recordings


	# Function: preprocess_recordings
	# -------------------------------
	# preprocesses for feeding into hmm:
	# 	- lowers time resolution to a standard amount
	#	- adds relative position/velocity/acceleration features
	def preprocess_recordings (self, recordings):

		### Step 1: remove invalid entries for each label ###
		recordings = self.filter_recordings (self.recordings)

		### Step 2: convert each to an AV Matrix ###
		recordings = self.get_av_matrices (self.recordings)

		return recordings


	# Function: get_hmms
	# --------------------
	# trains an HMM for each label, returns it
	def get_hmms (self, av_matrices):

		hmms = {}
		for label, matrices in av_matrices.items ():

			hmms[label] = GaussianHMM (n_components=self.num_hmm_states)
			hmms[label].fit(matrices)

		return hmms


	# Function: Constructor
	# ---------------------
	def __init__ (self, recordings, num_hmm_states=10): 

		self.num_hmm_states = num_hmm_states
		self.recordings = copy (recordings)

		### Step 1: get AV matrices ###
		self.av_matrices = self.get_av_matrices (self.recordings)

		### Step 2: train HMMs ###
		self.hmms = self.get_hmms (self.av_matrices)


	# Function: extract
	# -----------------
	# given a recording, returns the hmm sequence of the highest scoring
	# hmm, plus its score at the very end.
	def extract (self, recording):

		### Step 1: get hmm representations, scores ###
		av_mat = np.array(av_matrix (recording))
		hmm_scores 	= [self.hmms[label].score (av_mat) for label in self.hmms.keys ()]

		features = np.array (hmm_scores)
		return features












