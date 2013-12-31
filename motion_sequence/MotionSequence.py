#-------------------------------------------------- #
# Module: MotionSequence
# ----------------------
# container class for all 'motion sequences,'
# which include both recordings and real-time
# streams of NI data from any combo of devices.
# call iter_frames () in the main thread to get them
# real-time, either in playback or real mode.
# ------------------------------------------------- # 
import numpy as np
import pandas as pd
import threading
import time
from ..interface.util import *
from ..devices.DeviceReceiver import DeviceReceiver


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

	# print "df start, end timestamp: ", df.iloc[0]['timestamp'], df.iloc[-1]['timestamp']
	if start_time < df.iloc[0]['timestamp']:
		# print "start time is earlier than possible"
		raise ValueError
	return df.loc[start_time_to_index (df, start_time) : end_time_to_index (df, end_time)]




# class: MotionSequence
# ---------------------
# abstract class for representing motion sequences, either
# real-time or played back from a recording. 
# call iter_frames to iterate over the frames
# call get_dataframe to get a dataframe containing all
class MotionSequence:

	def __init__ (self):

		self._frames_exhausted 		= threading.Event ()
		self._new_frame_available 	= threading.Event ()


	########################################################################################################################
	##############################[ --- ACCESSING PROPERTIES --- ]##########################################################
	########################################################################################################################

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




	########################################################################################################################
	##############################[ --- GETTING FRAMES/WINDOWS --- ]########################################################
	########################################################################################################################

	# Function: get_frame
	# -------------------
	# gets the next frame
	def get_frame (self):
		pass


	# Function: stream_frames 
	# -----------------------
	# iterates through the frames in this motion sequence
	def stream_frames (self):

		while not self._frames_exhausted.isSet ():
			new_frame = self.get_frame ()
			self._new_frame_available.set ()
			yield new_frame


	# Function: get_window_df
	# -----------------------
	# given timespan, returns the appropriate window at current
	# point in streaming 
	def get_window_df (self):
		pass


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

		MotionSequence.__init__ (self)
		self.dataframe = _dataframe

		if len(self.dataframe) == 0:
			self._frames_exhausted.set ()

		self.current_frame_index = 0	


	def get_frame (self, timeout=0.03):

		assert not self._frames_exhausted.isSet()
		time.sleep (timeout)
		new_frame = dict(self.dataframe.iloc[self.current_frame_index])
		self.current_frame_index += 1
		if self.current_frame_index >= len (self.dataframe):
			self._frames_exhausted.set ()
		return new_frame


	def get_dataframe (self):

		return self.dataframe


	def trim_dataframe (self, start_index, end_index):
		
		self.dataframe = self.dataframe.iloc[start_index:end_index]


	def get_window_df (self, timespan):

		end_time 	= self.dataframe.iloc[self.current_frame_index]['timestamp']
		start_time 	= end_time - sec_to_usec (timespan)

		try:
			return temporal_subsample (self.get_dataframe (), start_time, end_time)
		except ValueError:
			return None






# Class: RealTimeMotionSequence
# -----------------------------
# motion sequence gathered real-time from a (set of) device(s)
class RealTimeMotionSequence (MotionSequence):

	seq_type = 'RealTimeMotionSequence' 


	def __init__ (self, _device_receivers):
		
		MotionSequence.__init__(self)
		if type(_device_receivers) == type([]):
			self.device_receivers = _device_receivers
		else:
			self.device_receivers = [ _device_receivers]
		self.frames_list = []


	def get_frame (self):

		new_frame = {}
		for device_specific_frame in [dr.get_frame () for dr in self.device_receivers]:
			new_frame.update (device_specific_frame)

		self.frames_list.append (new_frame)
		return new_frame


	def get_dataframe (self):

		return pd.DataFrame (self.frames_list)


	def get_window_df (self, timespan):

		end_time 	= self.get_dataframe().iloc[-1]['timestamp']
		start_time 	= end_time - sec_to_usec (timespan)

		### Step 2: try to temporal subsample, return none if impossible ###
		try:
			return temporal_subsample (self.get_dataframe (), start_time, end_time)
		except ValueError:
			return None


	def trim_dataframe (self, start_index, end_index):

		self.frames_list = self.frames_list [start_index:end_index]
