import os
import pickle
import time
from collections import Counter
import threading
from copy import copy

from util import *
from interaction_parameters import pose_detection_parameters

from DataScience import *
from StoppableThread import StoppableThread


class PoseDataSet:
	"""
		Class: PoseDataSet 
		------------------
		abstraction for a dataset containing poses
	"""

	def __init__ (self):
		"""
			PUBLIC: Constructor
			-------------------
			creates the dataset 
		"""

		


class PoseDetector (StoppableThread):
	"""
		Class: PoseDetector
		-------------------
		class for determining what pose a user is in
	"""
	_name = 'PoseDetector'
	

	def __init__ (self, pose_dataset):
		"""
			PUBLIC: Constructor 
			-------------------
			attaches itself to the given motion sequence
		"""
		StoppableThread.__init__(self, self._name)

		#=====[ Watchers ]=====
		self.pose_watchers = pose_watchers

		#=====[ Classifiers ]=====
		self._load_classifiers ()
		self._last_frame = None
		self._pose_history = []

		#=====[ Poses ]=====
		self._current_pose 		= None	
		self._new_pose			= threading.Event () # indicator for pose just appearing
		self._pose_timestamp	= None 	# timestamp at which pose switched over

		#=====[ Clicking ]=====
		self._click_on 			= threading.Event () # indicator for click being 'on'
		self._new_click			= threading.Event () # indicator for click just appearing	
		self._click_timestamp 	= None	# timestamp at which click occured


	def attach (self, motion_sequence):
		"""
			PUBLIC: attach 
			--------------
			sets this pose detector so that it watches motion_sequence 
		"""
		self.motion_sequence = motion_sequence


	def load_classifiers (self):
		"""
			PRIVATE: load_classifiers
			-------------------------
			loads the classifiers
		"""

		self.classifiers = {}
		self.classifiers['pca'] 	= pickle.load (open(self.pca_filepath, 'r'))
		self.classifiers['svm']  	= pickle.load (open(self.svm_filepath, 'r'))
		self.classifiers['mlr']  	= pickle.load (open(self.mlr_filepath, 'r'))
		self.classifiers['dt']  	= pickle.load (open(self.dt_filepath, 'r'))		
		self.classifiers['nn']  	= pickle.load (open(self.nn_filepath, 'r'))				
	

	# PRIVATE: _get_frame
	# -------------------
	# returns the most recent frame from self.motion_sequence
	def _get_frame (self):
		self._last_frame = self.motion_sequence.get_frame ()


	# Function: is_valid 
	# ------------------
	# returns true if the frame doesn't contain nan
	def is_valid (self, frame):

		frame_json = frame_to_json (frame)
		for joint_index in range(frame_parameters['num_joints']):
			if np.isnan(np.sum(frame_json[joint_index].values())):
				return False
			else:
				return True


	# PRIVATE: frame_to_features
	# --------------------------
	# given a frame object, returns a feature vector representing it
	# (does preprocessing too, incl. PCA)
	def frame_to_features (self, frame):

		frame_json 		= frame_to_json (frame)
		frame_json_rel 	= convert_json_to_relative (frame_json)
		raw_features 	= extract_features (frame_json_rel)
		# features 		= self.classifiers['pca'].transform (raw_features)
		features 		= raw_features
		return features


	# PRIVATE: _update_pose_history
	# -----------------------------
	# classifies self._last_frame, updates self._pose_sequence
	def _update_pose_history (self, classifier_name='mlr'):

		features 	= self.frame_to_features (self._last_frame)
		prediction 	= self.classifiers[classifier_name].predict (features)[0]
		print_header ("PREDICTION: " + str(prediction))
		self._pose_history.append (prediction)


	# PRIVATE: get_relevant_poses
	# ---------------------------
	# returns a list of the recent poses that are relevant
	def get_relevant_poses (self):
		relevant_poses = []
		if len(self._pose_history) < self.parameters['history_length']:
			relevant_poses = copy(self._pose_history)
		else:
			relevant_poses = copy(self._pose_history[-self.parameters['history_length']:])
		return relevant_poses


	# PRIVATE: _update_pose
	# --------------------
	# sets self._current_pose, self._pose_timestamp
	def _update_pose (self):

		relevant_poses = self.get_relevant_poses ()
		most_common_pose = Counter(relevant_poses).most_common(1)[0][0]

		if most_common_pose != self._current_pose:
			self._current_pose = most_common_pose
			self._new_pose.set ()
			self._pose_timestamp = time.time ()
		else:
			self._new_pose.clear ()


	# PRIVATE: _update_click
	# ---------------------
	# sets self._click_on and self._click_timestamp where appropriate
	def _update_click (self):
		relevant_poses 		= self.get_relevant_poses ()
		if len(relevant_poses) < 1:
			return

		most_common_pose = Counter(relevant_poses).most_common(1)[0][0]

		if most_common_pose in self.parameters['click_gestures']:
			if not self._click_on.isSet ():
				self._click_on.set ()
				self._new_click.set ()
				self._click_timestamp = time.time ()
		else:	
			self._click_on.clear ()



	# PUBLIC: thread_iteration 
	# ------------------------
	# performs classification on every frame that comes through
	def thread_iteration (self):

		#===[ get frame, check validity ]===
		self._get_frame ()
		if not self.is_valid (self._last_frame):
			return

		#===[ update internal state ]===
		self._update_pose_history ()
		self._update_pose ()
		self._update_click ()

		#===[ broadcast internal state ]===
		if self._new_click.isSet ():
			self.broadcast_click ()
			self._new_click.clear ()
		if self._new_pose.isSet ():
			self.broadcast_pose ()
			self._new_pose.clear ()


	# PRIVATE: broadcast_click
	# ------------------------
	# notifies all objects in 'click_watchers' of the new click
	def broadcast_click (self):
		for o in self.click_watchers:
			o.notify_of_click (self._click_timestamp)


	# PRIVATE: broadcast_pose
	# -----------------------
	# notifies all objects in 'pose_watchers' of the new pose
	def broadcast_pose (self):
		for o in self.pose_watchers:
			o.notify_of_pose (self._current_pose, self._pose_timestamp)



	# PUBLIC: get_pose_timestamp 
	# --------------------------
	# returns the last time that 
	def get_pose_timestamp (self):
		return self.pose_timestamp


	# PUBLIC: get_click
	# -----------------
	# returns true if click is currently 'on'
	def get_click (self):
		return self._click_on.isSet ()


	# PUBLIC: get_click_timestamp
	# ---------------------------
	# returns the timestamp of the last time that clicking
	# went high
	def get_click_timestamp (self):
		return self._click_timestamp


	# PUBLIC: new_click_appeared 
	# --------------------------
	# returns true if a new click appeared recently
	def new_click_appeared (self):
		return self._new_click.isSet ()


	# PUBLIC: new_gesture_appeared
	# ----------------------------
	# returns true if a new getsure appeared recently
	def new_pose_appeared (self):
		return self._new_pose_appeared.isSet ()

