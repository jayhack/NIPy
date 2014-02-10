#-------------------------------------------------- #
# Class: StoppableThread
# ----------------------
# abstract class for threads that can be 'stopped'
#-------------------------------------------------- #
import threading

class StoppableThread (threading.Thread):

	def __init__ (self, _name="<UNKNOWN_THREAD>"):
		threading.Thread.__init__(self)

		self._name = _name
		self._stop = threading.Event ()


	def run (self):
		"""
			PUBLIC: run
			-----------
			main thread execution
		"""
		while not self._stop.isSet ():
			self.thread_iteration ()


	def stop (self):
		"""
			PUBLIC: stop
			------------
			stops thread execution
		"""
		self._stop.set ()


	def thread_iteration (self):
		"""
			PRIVATE: thread_iteration
			-------------------------
			override this function with whatever activity
			the thread will undergo in a single iteration
		"""
		raise NotImplementedError