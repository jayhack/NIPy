from ..threads.StoppableThread import StoppableThread
from ..motion_sequence.MotionSequence import RealTimeMotionSequence

class Recorder (StoppableThread):
	"""
		Class: Recorder
		---------------
		class for recording motion sequences 
	"""
	_name = "Recorder"


	#==========[ Initialization	]==========
	def __init__ (self, _device_receivers, _verbose=True):
		""" 
			PUBLIC: Constructor
			-------------------
			given a list of device receivers (or a single device receiver), initializes
		"""
		#=====[ Step 1: initialize StoppableThread	]=====
		StoppableThread.__init__ (self, self._name)

		#=====[ Step 2: set optional parameters ]=====
		self._verbose = _verbose

		#=====[ Step 3: create motion sequence to write to	]=====
		self.motion_sequence = RealTimeMotionSequence (_device_receivers)


	def is_recording (self):
		"""
			PUBLIC: is_recording
			--------------------
			returns true if it is currently recording
		"""
		return self._stop.isSet ()


	def thread_iteration (self):
		"""
			PRIVATE: thread_iteration
			-------------------------
			on each thread iteration, adds a new frame to motion sequence
			optionally prints out info on most recent frame, if appropriate
		"""
		self.motion_sequence.get_frame ()
		if self._verbose:
			print self.motion_sequence.get_dataframe ().iloc[-1]


	def get_motion_sequence (self):
		""" 
			PUBLIC: get_motion_sequence
			---------------------------
			returns the product of this recording as a motion sequence
		"""
		return self.motion_sequence





