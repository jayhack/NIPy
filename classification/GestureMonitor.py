# ------------------------------------------------------------ #
# Class: GestureMonitor
# ---------------------# 
# given a set of examples of a certain class of recordings, this 
# will build a generative model of them and, furthermore, interpret
# new examples as in the class or out
# 
# 
# ------------------------------------------------------------ #
import pickle
import numpy as np
import pandas as pd
from sklearn.hmm import GaussianHMM
from sklearn import cross_validation
import FeatureFunctions
import EventMonitor
from ..interface.util import *


# Function: sec_to_usec
# ---------------------
# converts seconds to microseconds
def sec_to_usec (sec):
	
	return sec*1000000

# Function: usec_to_sec
# ---------------------
# converts seconds to microseconds
def usec_to_sec (sec):
	
	return int(sec/float(1000000))


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

	if len(df) < 20:
		return None

	### Step 1: get desired start/end timestamps ###
	end_time 	= df.iloc[-1]['timestamp']
	start_time 	= end_time - sec_to_usec (secs)

	### Step 2: try to temporal subsample, return none if impossible ###
	try:
		return temporal_subsample (df, start_time, end_time)
	except ValueError:
		return None



class GestureMonitor (EventMonitor):

	num_hmm_states = 10
	feature_extractor = None				# object of class FeatureExtractor 
	hmm = None


	# Function: Constructor
	# ---------------------
	# given a list of recordings, this function converts them to its 
	# preferred format
	def __init__ (self, _motion_sequences, FeatureExtractor=FeatureFunctions.AVFeatureExtractor):

		#===[ Local Data ]===
		self.motion_sequences 	= _motion_sequences
		self.dataframes 		= [r.get_dataframe () for r in self.motion_sequences]
		self.feature_extractor 	= FeatureExtractor ()
		self.train ()


	# Function: fit
	# -------------
	# fits a generative model (HMM) to the data, returns it
	def fit_hmm (self):

		X = [self.feature_extractor.extract(x) for x in self.dataframes]
		print [x.shape for x in X]
		hmm = GaussianHMM ()
		hmm.fit (X)
		return hmm


	# Function: score_df
	# ------------------
	# scores a dataframe
	def score_df (self, df):

		return self.hmm.score (self.feature_extractor.extract (df))

	# Function: score
	# ---------------
	# returns a score of the current example, rep. as motion sequence
	def score (self, ms):

		return self.score_df(ms.get_dataframe ())


	# Function: get_threshold_score
	# -----------------------------
	# determines the threshold score and returns it
	# threshold score = score_avg - std_dev_range*score_std_dev
	def get_threshold_score (self, std_dev_range=3):

		scores = [self.score(ms) for ms in self.motion_sequences]
		avg, std = np.mean(scores), np.std(scores)
		return avg - std_dev_range*std


	# Function: calculate_window_timespans
	# ---------------------------------------
	# calculates and returns 'window_timespans', where the ith element
	# suggests that a window of timespan i should be submitted for detection
	def calculate_window_timespans (self):

		durations = [ms.get_timespan () for ms in self.motion_sequences]
		durations = [float(d)/float(1000000) for d in durations]
		mean, std = np.mean (durations), np.std(durations)
		return [mean-1*std, mean, mean+1*std]


	# Function: train
	# ---------------
	# trains the full classifier
	def train (self):

		#===[ Fit HMM ]===
		self.hmm = self.fit_hmm ()

		#===[ get dist. of scores, window sizes ]===
		self.threshold_score = self.get_threshold_score ()
		self.window_timespans = self.calculate_window_timespans ()


	# Function: detect_window
	# -----------------------
	# returns true if the given ms window is thought to have 
	# originated from the generative model
	def detect_window (self, df):

		if self.score_df (df) >= self.threshold_score:
			return True
		else:
			return False


	# Function: get_windows
	# ---------------------
	# given a motionsequence, extracts the appropriate
	# 'windows' to look at
	def get_windows (self, df):

		timespans =  [extract_last_n_seconds(df, timespan) for timespan in self.window_timespans]
		return [t for t in timespans if t]


	# Function: detect
	# ----------------
	# returns true if the given motion sequence is though to have
	# originated from the generative model
	def detect (self, df):

		windows = self.get_windows (df)
		detections = [self.detect_window (df) for df in windows]
		return any(detections)


		

