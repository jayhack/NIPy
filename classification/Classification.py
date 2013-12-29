# ------------------------------------------------------------ #
# Class: Classification
# ---------------------
# functions and classes for classifying dataframes containing
# NI data
# 
# ------------------------------------------------------------ #
#--- Numpy ---
import numpy as np

#--- Pandas ---
import pandas as pd

#--- Scikit-Learn ---
# from sklearn.neural_network import BernoulliRBM
from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation

#--- My Files ---
import FeatureFunctions
from util import *


########################################################################################################################
##############################[ --- UTILITIES --- ]######################################################################
########################################################################################################################

# Function: dict_to_X_y
# -----------------
# given a dict of examples, this gets X and y
# returns (X, y)
def dict_to_X_y (examples_dict):

	X, y = [], []
	for label, matrices in examples_dict.items ():
		X += matrices
		y += [label for matrix in matrices]
	return np.array(X), np.array(y)





########################################################################################################################
##############################[ --- Classifier --- ]####################################################################
########################################################################################################################

class Classifier:

	#==========[ Parameters ]==========
	num_hmm_states = 10

	#==========[ Preprocessing ]==========
	feature_extractor = None				# object of class FeatureExtractor 

	#==========[ Classifiers ]==========
	classifier = None

	#==========[ Data ]==========	
	examples = {}							# Map: label -> list of Feature Matrices



    ########################################################################################################################
    ##############################[ --- Constructor/Initialization --- ]####################################################
    ########################################################################################################################

	# Function: Constructor
	# ---------------------
	# given a list of recordings, this function converts them to its 
	# preferred format
	def __init__ (self, raw_recordings_dict, FeatureExtractor=FeatureFunctions.AVFeatureExtractor):

		### Step 1: create feature extractor ###
		print_inner_status ("Initializing Classifier", "Getting feature extractor")
		self.feature_extractor = FeatureExtractor (raw_recordings_dict)

		### Step 2: get features for each recording, store in examples, X, y ###
		print_inner_status ("Initializing Classifier", "Converting recordings to features")
		self.examples = self.recordings_dict_to_features_dict (raw_recordings_dict)

		### Step 3: train self.classifier ###
		print_inner_status ("Initializing Classifier", "Training the classifier")
		self.classifier = self.train ()


	# Function: recordings_dict_to_features_dict
	# ------------------------------------------
	# given a dict Map: label -> panel of 
	# returns dict Map: label -> list of features for recordings
	def recordings_dict_to_features_dict (self, raw_recordings_dict):

		return {label:[self.feature_extractor.extract(r) for r in recordings] for label,recordings in raw_recordings_dict.items()}






    ########################################################################################################################
    ##############################[ --- Training/Classification --- ]#######################################################
    ########################################################################################################################


	# Function: train
	# ---------------
	# train self.classifier on data
	def train (self):

		X, y = dict_to_X_y (self.examples)
		classifier = LogisticRegression ()
		classifier.fit (X, y)
		return classifier


	# Function: classify
	# ------------------
	# returns a pseudo-probability distribution over the classes
	def classify (self, df):

		### Step 1: extract features ###
		features = self.feature_extractor.extract (df)

		### Step 2: return prediction ###
		return features
		# return self.classifier.predict_proba (features)






    ########################################################################################################################
    ##############################[ --- Evaluation --- ]####################################################################
    ########################################################################################################################

    # Function: evaluate_model
    # ------------------------
    # does 5-fold CV to determine how good your classification accuracy is
	def evaluate_model (self):
		
		X, y = dict_to_X_y (self.examples)
		scores = cross_validation.cross_val_score (LogisticRegression(), X, y, cv=5, verbose=1)
		print("===[ Cross Validation Scores: ]===")
		print scores






