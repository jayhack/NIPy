#-------------------------------------------------- #
# Class: Recorder
# ---------------
# class for recording motion sequences
#-------------------------------------------------- #
import threading
from ..motion_sequence.MotionSequence import RealTimeMotionSequence
from ..interface.util import *


class Recorder (threading.Thread):

	# Function: Constructor
	# ---------------------
	# given a list of device receivers (or a single receiver), initializes
	def __init__ (self, _device_receivers, _verbose=True):
		
		threading.Thread.__init__ (self)
		self.motion_sequence = RealTimeMotionSequence (_device_receivers)
		self._recording = threading.Event ()
		self.verbose = _verbose
	

	def is_recording (self):

		return self._recording.isSet ()


	def run (self):

		self._recording.set ()
		while self.is_recording():
			self.motion_sequence.get_frame ()
			if self.verbose:
				print self.motion_sequence.get_dataframe ().iloc[-1]


	def stop (self):

		self._recording.clear ()


	# Function: get_motion_sequence
	# -----------------------------
	# returns the product of this recording
	def get_motion_sequence (self):
		
		return self.motion_sequence





