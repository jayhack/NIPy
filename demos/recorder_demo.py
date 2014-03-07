from NIPy.file_storage.StorageDelegate import StorageDelegate
from NIPy.motion_sequence.MotionSequence import PlayBackMotionSequence
from NIPy.devices.DeviceReceiver import DeviceReceiver
from NIPy.recording.Recorder import Recorder
import time

#==========[ Step 1: create device receiver	]==========
primesense_receiver = DeviceReceiver ('primesense')


#==========[ Step 2: create recorder	]==========
recorder = Recorder (primesense_receiver)


#==========[ Step 3: record on enter	]==========
raw_input("=====[ Press Enter to begin Recording]=====\n")
time.sleep (10)
print '==========[ 	RECORDING]=========='
recorder.start ()
raw_input(">>> ENTER TO STOP <<<\n")
recorder.stop ()


#==========[ Step 4: retrieve and save recorded motion sequence	]==========
storage_delegate = StorageDelegate ('./data')
recording = recorder.get_motion_sequence ()
storage_delegate.save_recording (recording)


