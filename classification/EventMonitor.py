# ------------------------------------------------------------ #
# Class: EventMonitor
# -------------------# 
# abstract class for monitoring a stream for certain sets of 
# events
# ------------------------------------------------------------ #
import threading
from ..motion_sequence import MotionSequence
from ..interface.util import *

class EventMonitor (threading.Thread):

	# Function: Constructor
	# ---------------------
	# stores a reference to the motion sequence
	def __init__ (self):
		threading.Thread.__init__ (self)
		self.motion_sequence = None	
		self._stop = threading.Event ()
		self.event_occurred = threading.Event ()


	# Function: attach
	# ----------------
	# attaches this EventMonitor to a motion sequence
	def attach (self, _motion_sequence):
		
		self.motion_sequence = _motion_sequence

	# Function: run
	# -------------
	# main thread operation
	def run (self):
	
		if not self.motion_sequence:
			print_error ("Event monitor not attached to a motion sequence", "make sure to <attach ()> before <start ()>ing")
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

	# Function: visualize
	# -------------------
	# returns data on the current state of the monitor w/r/t its 
	# motion sequence
	def current_reaction (self):
		pass








