# ---------------------------------------------------------- #
# File: util.py
# -------------
# common interface-related utilities
# ---------------------------------------------------------- #

def print_message (message):
	"""
		Function: print_message
		-----------------------
		prints the specified message in a salient format
	"""

	print "-" * len(message)
	print message
	print "-" * len(message)


def print_status (stage, status, indent=0):
	"""
		Function: print_status
		----------------------
		prints the stage/status message at desired indent
	"""
	print '	'*indent + '----> ' + stage + ": " + status
