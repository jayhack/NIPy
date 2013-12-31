# ------------------------------------------------------------ #
# Class: EventMonitor
# -------------------# 
# abstract class for monitoring a stream for certain sets of 
# events
# ------------------------------------------------------------ #
import threading
from ..motion_sequence import MotionSequence

class EventMonitor (threading.Thread):

	# Function: Constructor
	# ---------------------
	# stores a reference to the motion sequence
	def __init__ (self, _motion_sequence):
		threading.Thread.__init__ (self)
		self.motion_sequence = _motion_sequence	
		self._stop = threading.Event ()
		self.event_occurred = threading.Event ()


	# Function: run
	# -------------
	# main thread operation
	def run (self):
		
		while not self._stop.isSet ():
			self.monitor ()


	# Function: stop
	# --------------
	# terminate this event monitor
	def stop (self):
		
		self._stop.set ()


	# Function: monitor
	# -----------------
	# monitors self.motion_sequence for events
	# override this method
	def monitor (self):
		pass









