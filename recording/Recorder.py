#-------------------------------------------------- #
# Class: Recorder
# ---------------
# class for recording motion sequences
#-------------------------------------------------- #
import threading
from ..devices.DeviceReceiver import DeviceReceiver
from ..motion_sequence.MotionSequence import RealTimeMotionSequence
from ..interface.util import *


class RecordingThread (threading.Thread):

	def __init__ (self, _recorder):
		
		threading.Thread.__init__(self)
		self.recorder = _recorder

	# Function: run
	# -------------
	# adds frames to the motion sequence while recorder.is_recording
	# evaluates to true
	def run (self):
		
		while self.recorder.is_recording ():
			self.recorder.get_motion_sequence ().add_frame ()



class Recorder:

	# Function: constructor
	# ---------------------
	# given a list of device receivers (or a single receiver),
	# creates a recorder
	def __init__ (self, _device_receivers):
		
		self.motion_sequence = RealTimeMotionSequence (_device_receivers)
		self.currently_recording = False


	# Function: is_recording
	# ----------------------
	# returns boolean value for wether this object is currently recording
	def is_recording (self):

		return self.currently_recording


	# Function: get_motion_sequence
	# -----------------------------
	# returns the product of this recording
	def get_motion_sequence (self):
		
		return self.motion_sequence


	# Function: start
	# ---------------
	# call to begin recording; puts frames into recording in a new thread.
	def start (self):

		print_status ("Recorder", "Beginning recording")
		self.currently_recording = True

		self.recording_thread = RecordingThread (self)
		self.recording_thread.start ()


	# Function: stop
	# --------------
	# call to end recording
	def stop (self):

		self.currently_recording = False
		print_status ("Recorder", "Ending recording")



