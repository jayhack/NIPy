from NIPy.file_storage.StorageDelegate import StorageDelegate
from NIPy.motion_sequence.MotionSequence import PlayBackMotionSequence
from NIPy.visualization.Visualizer import PrimesenseVisualizer

if __name__ == "__main__":

	#==========[ Step 1: load in the recording to display	]==========
	storage_delegate = StorageDelegate ('./data')
	test_recording = storage_delegate.get_recording ('1392028946.84.dataframe')
	
	#==========[ Step 2: create visualizer, play recording	]==========
	visualizer = PrimesenseVisualizer ()
	visualizer.play (test_recording)


