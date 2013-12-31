# ------------------------------------------------------------ #
# Class: Threshold
# ----------------
# abstract class for applying thresholds within EventMonitors
# ------------------------------------------------------------ #

class Threshold:

	# Function: Constructor
	# ---------------------
	# apply_function: function to apply, then threshold
	def __init__ (self, _score_function):

		self.score_function = _score_function


	# Function: train
	# ---------------
	# trains the threshold
	def train (self):
		pass


	# Function: passes_threshold
	# --------------------------
	# given a score, returns True if it passes the threshold
	def passes_threshold(self, score):
		pass


	# Function: classify
	# ------------------
	# binary indicator of wether passed in example passes threshold
	def classify (self, example):

		return self.passes_threshold(self.score_function (example))





