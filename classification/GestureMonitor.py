# ------------------------------------------------------------ #
# Class: GestureMonitor
# --------------------- 
# given a set of examples of a certain class of recordings, this 
# will build a generative model of them and, furthermore, interpret
# new examples as in the class or out
# ------------------------------------------------------------ #
import pickle
import numpy as np
import pandas as pd
from sklearn.hmm import GaussianHMM
from FeatureFunctions import AVFeatureExtractor
from EventMonitor import EventMonitor
from Threshold import Threshold
from ..interface.util import *



# Class: GMScoreThreshold
# -----------------------
# Threshold for the score received from a generative model
class GMScoreThreshold (Threshold):

	std_dev_range = 3

	def __init__ (self, _gm_score_function, examples):

		Threshold.__init__(self, _gm_score_function)
		self.train (examples)

	def train (self, examples):

		scores = [self.score_function(x) for x in examples]
		mean, std = np.mean(scores), np.std(scores)
		self._threshold_score = mean - self.std_dev_range*std

	def passes_threshold (self, score):

		return score >= self._threshold_score





# Class: GestureMonitor
# ---------------------
# event monitor that watches for gestures
class GestureMonitor (EventMonitor):

	# Function: Constructor
	# ---------------------
	# train_ms_list: list of motion sequences to train on
	# monitor_ms: motion sequence to monitor
	def __init__ (self, _train_ms_list, _monitor_ms, _gesture_name, FeatureExtractor=AVFeatureExtractor):

		EventMonitor.__init__(self, _monitor_ms)
		self.gesture_name = _gesture_name
		self.feature_extractor 	= FeatureExtractor ()
		self.train (_train_ms_list)


	# Function: train
	# ---------------
	# given a list of motion sequences, learns all paramters necessary to
	# detect a gesture from input
	def train (self, motion_sequences):

		dfs 					= [ms.get_dataframe () for ms in motion_sequences]
		examples				= [self.feature_extractor.extract (df) for df in dfs]
		examples				= [e for e in examples if not np.isnan(np.sum(e))]

		self.hmm 				= GaussianHMM (n_components=5).fit (examples)
		self.score_threshold 	= GMScoreThreshold (self.hmm.score, examples)
		self.window_timespans 	= self.calculate_window_timespans (motion_sequences)


	# Function: calculate_window_timespans
	# ---------------------------------------
	# calculates and returns 'window_timespans', where the ith element
	# suggests that a window of timespan i should be submitted for detection
	def calculate_window_timespans (self, motion_sequences):

		durations = [ms.get_timespan () for ms in motion_sequences]
		durations = [float(d)/float(1000000) for d in durations]
		mean, std = np.mean (durations), np.std(durations)
		return [mean-1.5*std, mean-1*std, mean, mean+1*std, mean+1.5*std]


	# Function: get_window_dfs
	# ------------------------
	# returns a df for each (available) window
	def get_window_dfs (self):

		window_dfs = [self.motion_sequence.get_window_df (timespan) for timespan in self.window_timespans]
		return [w_df for w_df in window_dfs if w_df]


	# Function: classify_window_df
	# ----------------------------
	# classifies a window_df as containing/not containing gesture
	def classify_window_df (self, window_df):

		features = self.feature_extractor.extract (window_df)
		return self.score_threshold.classify (features)


	# Function: monitor
	# -----------------
	# main function called in thread, applied repeatedly
	# to 'monitor_sequence'
	def monitor (self):

		self.motion_sequence._new_frame_available.wait ()
		window_dfs 	= self.get_window_dfs ()

		labels = [self.classify_window_df (df) for df in window_dfs]

		if any(labels):
			print "#####[ " + self.gesture_name + " ]#####"
		self.motion_sequence._new_frame_available.clear ()



		

