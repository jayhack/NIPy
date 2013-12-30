#-------------------------------------------------- #
# Module: MotionSequence
# ----------------------
# container class for all 'motion sequences,'
# which include both recordings and real-time
# streams of NI data from any combo of devices
# ------------------------------------------------- # 
import numpy as np
import pandas as pd
from ..interface.util import *
from ..devices.DeviceReceiver import DeviceReceiver


# class: MotionSequence
# ---------------------
# abstract class for representing motion sequences, either
# real-time or played back from a recording. 
# call iter_frames to iterate over the frames
# call get_dataframe to get a dataframe containing all
class MotionSequence:

	# Function: __str__
	# -----------------
	# returns the head of the dataframe
	def __str__ (self):
		return '===[ ' + self.seq_type + ']===\n' + str(self.get_dataframe ().head ())


	# Function: len
	# -------------
	# returns the length of the contained motion sequence
	def __len__ (self):
		return len(self.get_dataframe ())


	# Function: iter_frames
	# ---------------------
	# iterates through frames contained in this motionsequence as 
	# dicts
	def iter_frames (self):
		pass


	# Function: iter_dataframes
	# -------------------------
	# for each timestep, yields the dataframe as it was completed up until
	# that timestup
	def iter_dataframes (self):
		pass


	# Function: get_dataframe
	# -----------------------
	# returns a dataframe representing current motion sequence.
	# (Up to current point in time, if real-time)
	def get_dataframe (self):
		pass


	# Function: get_timespan
	# ----------------------
	# returns the total time spanned in this dataframe, in
	# seconds
	def get_timespan (self):
		df = self.get_dataframe ()
		return (df.iloc[-1]['timestamp'] - df.iloc[0]['timestamp'])


	# Function: trim_dataframe
	# ------------------------
	# given start, end, this trims the dataframe to the given
	# indices
	def trim_dataframe (self, start_index, end_index):
		pass


# class: PlayBackMotionSequence
# -----------------------------
# motion sequence constructed from a recording/pickled
# dataframe
class PlayBackMotionSequence (MotionSequence):

	seq_type = 'PlayBackMotionSequence'


	def __init__ (self, _dataframe):

		self.dataframe = _dataframe


	def iter_frames(self):
		
		for row_index in range(len(self.dataframe)):
			yield dict(self.dataframe.iloc[row_index])


	def iter_dataframes (self):

		for row_index in range(len(self.dataframe)):
			yield self.dataframe.iloc[:row_index]



	def get_dataframe (self):

		return self.dataframe



# class: PlayBackMotionSequence
# -----------------------------
# motion sequence constructed from a recording/pickled
# dataframe
class RealTimeMotionSequence (MotionSequence):

	seq_type = 'RealTimeMotionSequence' 


	def __init__ (self, _device_receivers):
		if type(_device_receivers) == type([]):
			self.device_receivers = _device_receivers
		else:
			self.device_receivers = [ _device_receivers]

		self.frames_list = []


	# Function: get_frame
	# -------------------
	# gets a single frame containing info from all of the 
	# device receivers; blocks until it gets one from all.
	def get_frame (self):
		
		total_frame = {}
		for device_frame in [dr.get_frame () for dr in self.device_receivers]:
			total_frame.update (device_frame)
		return total_frame


	# Function: add_frame 
	# -------------------
	# adds a single frame to the list of frames
	def add_frame (self):

		self.frames_list.append (self.get_frame ())


	# consume_frames
	# --------------
	# continuously adds frames 
	def gather_frames (self):
		print "--- gather frames ---"
		while True:
			self.frames_list.append (self.get_frame ())


	def iter_frames(self):
		
		while True:
			frame = self.get_frame ()
			self.frames_list.append (frame)
			yield frame

	def iter_dataframes (self):
		
		while True:
			frame = self.get_frame ()
			self.frames_list.append (frame)
			yield self.get_dataframe()


	def get_dataframe (self):

		return pd.DataFrame (self.frames_list)


	def trim_dataframe (self, start_index, end_index):

		self.frames_list = self.frames_list [start_index:end_index]
