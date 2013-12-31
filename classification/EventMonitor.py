# ------------------------------------------------------------ #
# Class: EventMonitor
# -------------------# 
# abstract class for monitoring a stream for certain sets of 
# events
# ------------------------------------------------------------ #


class EventMonitorThread (threading.Thread):

	def __init__ (self, _event_monitor):
		threading.Thread.__init__(self)
		self.event_monitor = _event_monitor
		self._stop = threading.Event ()

	def stop (self):

		self._stop.set ()

	def is_stopped (self):

		return self._stop.isSet ()


	def run (self):

		self.event_monitor.monitor ()




class EventMonitor:

	# Function: Constructor
	# ---------------------
	# stores a reference to the motion sequence
	def __init__ (self, _motion_sequence):

		self.motion_sequence = _motion_sequence
		event_monitor_thread = 


	# Function: monitor
	# -----------------
	# monitors self.motion_sequence for events
	def monitor (self):
		pass









