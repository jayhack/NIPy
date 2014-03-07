from NIPy.file_storage.StorageDelegate import StorageDelegate
from NIPy.motion_sequence.MotionSequence import PlayBackMotionSequence
from NIPy.visualization.Visualizer import PrimesenseVisualizer
from NIPy.pose_detecion import PoseDataset, PoseDetector

if __name__ == "__main__":

	#==========[ Step 1: construct the dataset	]==========
	storage_delegate = StorageDelegate ('./data')
	storage_delegate.get_all_poses ()
	# test_recording = storage_delegate.get_recording ('1392028946.84.dataframe')
	
	#==========[ Step 2: create visualizer, play recording	]==========
	visualizer = PrimesenseVisualizer ()
	visualizer.play (test_recording)


