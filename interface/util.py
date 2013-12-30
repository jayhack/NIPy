# ---------------------------------------------------------- #
# File: util.py
# -------------
# common interface-related utilities
# ---------------------------------------------------------- #

# Function: print_welcome
# -----------------------
# prints out a welcome message
def print_welcome ():
	
	print "######################################################################"
	print "#########[ --- PyMotion: Natural Interaction for Python --- ]#########"
	print "###############[ -   by Jay Hack, Fall 2013      - ]##################"
	print "######################################################################"
	print "\n"


# Function: print_header
# -----------------------
# prints the specified header text in a salient way
def print_header (header_text):
	
	print "-" * (len(header_text) + 12)
	print ('#' * 5) + ' ' +  header_text + ' ' + ('#' * 5)
	print "-" * (len(header_text) + 12)


# Function: print_error
# ---------------------
# prints an error and exits 
def print_error (top_string, bottom_string):
	
	print "Error: " + top_string
	print "---------------------"
	print bottom_string
	exit ()


# Function: print_status
# ----------------------
# prints out a status message 
def print_status (stage, status):	
	
	print "-----> " + stage + ": " + status


# Function: print_inner_status
# ----------------------------
# prints out a status message for inner programs
def print_inner_status (stage, status):
	
	print "	-----> " + stage + ": " + status


# Function: print_notification
# ----------------------------
# prints a notification for the user
# using the format '	>>> [notification text] <<<'
def print_notification (notification_text):

	print "	>>> " + notification_text + " <<<"


# Function: print_countdown
# -------------------------
# Parameters (3):
#	- end_message: message to display at the end
# 	- count: # of counts
# 	- interval: interval between counts, in seconds
# Description:
# 	prints a countdown w/ the final message indicated 
def print_coundtown (end_message, count=3, interval=0.5):
		
	for i in range (count):
		print_notification(str(i))
		time.sleep (interval)
	print_notification(end_message)



