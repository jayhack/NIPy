#-------------------------------------------------- #
# Class: DeviceReceiver
# ---------------------
# receives data from NI devices over 
# TCP ports
#-------------------------------------------------- #
import os
import sys
import time
import json
import zmq
import threading
from parameters import *
from ..interface import util

class ReceiverThread (threading.Thread):
    
    def __init__ (self, _device_receiver):
        threading.Thread.__init__ (self)
        self.device_receiver = _device_receiver

    def run (self):
        while self.device_receiver.is_receiving ():
            self.device_receiver.read_frame ()



class DeviceReceiver:

    # Function: zmq_init
    # ------------------
    # sets up connection to tcp ports via zmq
    def zmq_init (self):

        self.context = zmq.Context ()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect (parameters['connect_address'])
        self.socket.setsockopt(zmq.SUBSCRIBE, device_filters[self.device])


    # Function: Constructor 
    # ---------------------
    # connects to the port, starts thread to receive frames
    def __init__ (self, _device):

        if not _device in device_filters.keys ():
            print_error ("Unsupported device", str(_device) + " is unrecognized")
        self.device = _device
        self.zmq_init ()
        self.currently_receiving = True
        self.frame_available = False
        self.last_frame = None
        self.begin_receiving ()


    # Function: Destructor
    # --------------------
    # terminates thread that receives frames
    def __del__ (self):

        self.stop_receiving ()


    # Function: is_receiving
    # ----------------------
    # indicator for wether this should be receiving or no
    def is_receiving (self):
       
        return self.currently_receiving


    # Function: begin_receiving
    # -------------------------
    # starts the thread that gets frames from UDP
    def begin_receiving (self):

        self.currently_receiving = True
        self.receiver_thread = ReceiverThread(self)
        self.receiver_thread.start ()


    # Function: stop_receiving
    # ------------------------
    # stops the thread that gets frames from UDP
    def stop_receiving (self):
        
        self.currently_receiving = False


    # Function: read_frame 
    # --------------------
    # blocks until it gets a frame from the device, sets it as self.last_frame
    def read_frame (self):

        self.last_frame = json.loads (self.socket.recv ()[len(device_filters[self.device]):])
        self.frame_available = True


    # Function: get_frame 
    # -------------------
    # blocks until a new frame is available, returns it
    def get_frame (self):

        while not self.frame_available:
            pass
        self.frame_available = False
        return self.last_frame


    # Function: get_framerate
    # -----------------------
    # empirically determines the framerate in frames/second
    def get_framerate (self, num_frames=5):

        start_time = time.time ()
        for i in range (int(num_frames)):
            self.read_frame ()
        end_time = time.time ()
        return (num_frames)/(end_time - start_time)





