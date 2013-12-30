#-------------------------------------------------- #
# Class: MotionSequenceEditor
# ---------------------------
# class for editing motion sequence data
#-------------------------------------------------- #
from ..visualization.Visualizer import Visualizer
from ..interface.util import *

class MotionSequenceEditor:

	def __init__ (self):
		self.visualizer = Visualizer ()


	# Function: trim
	# --------------
	# given a motion sequence, displays it via Visualizer
	# and asks you what frame range to keep, discards the rest.
	def trim (self, ms):

		### Step 1: ask for range ###
		print_notification ("Enter the range (start then end) to keep in the recording")

		### Step 2: display onscreen ###
		self.visualizer.plot_motion_sequence (ms)

		### Step 3: get range ###
		start_index = int(raw_input ('>>> Start frame index: '))
		end_index = int(raw_input ('>>> End frame index: '))

		### Step 4: remove all but that range ###
		ms.trim_dataframe (start_index, end_index)


