#-------------------------------------------------- #
# Class: Visualizer
# -----------------
# class for creating visualizations of NI data
#-------------------------------------------------- #
import matplotlib.pyplot as plt
from ..motion_sequence.MotionSequence import MotionSequence

class Visualizer:

	#===[ PLOTTING PARAMETERS ]===
	palm_colors = {
					'palm_x': 'red',
					'palm_y': 'blue',
					'palm_z': 'green',
	}

	def __init__ (self):
		pass


	# Function: plot_motion_sequence
	# ------------------------------
	# plots a single motion sequence
	def plot_motion_sequence (self, ms):

		for dim_name, dim_color in self.palm_colors.items ():
			plt.plot (ms.get_dataframe ()[dim_name], dim_color)
		plt.show ()


    # # Function: plot_recording_dimension
    # # ----------------------------------
    # # given a recording and its title, this will plot it
    # def plot_recording_dimension (self, recording, dim_name, recording_color):
        
    #     plt.plot (recording[dim_name], color=recording_color)
    #     plt.title (dim_name)


    # # Function: plot_recording
    # # ------------------------
    # # given a recording, this plots it
    # def plot_recording (self, recording):
    #     dim_colors = {  
    #                     'palm_x': 'red',
    #                     'palm_y': 'blue',
    #                     'palm_z': 'green'
    #     }   
    #     for dim_name, dim_color in dim_colors.items():
    #         self.plot_recording_dimension (recording, dim_name, dim_color)


    # # Function: plot_gesture_recordings
    # # ---------------------------------
    # # for each gesture, plot its palm_(x|y|z) on the same axis
    # def plot_gesture_recordings (self):

    #     self.get_gesture_recordings ()
    #     for gesture_name, gesture_recordings in self.gesture_recordings.items ():

    #         for r in gesture_recordings:
    #             self.plot_recording (r)
    #         plt.title (gesture_name + '_examples')
    #         plt.savefig (gesture_name + '_examples.png')
    #         plt.close ()
