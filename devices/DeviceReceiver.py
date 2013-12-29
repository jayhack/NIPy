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
from parameters import *
from ..interface import util


class DeviceReceiver:


    ########################################################################################################################
    ##############################[ --- INITIALIZATION --- ]################################################################
    ########################################################################################################################

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
    # connects to the port
    def __init__ (self, _device):

        #===[ DEVICE ]===
        if not _device in device_filters.keys ():
            print_error ("Unsupported device", str(_device) + " is unrecognized")
        self.device = _device

        #===[ ZMQ ]===
        self.zmq_init ()





    ########################################################################################################################
    ##############################[ --- INTERFACE --- ]#####################################################################
    ########################################################################################################################

    # Function: get_frame 
    # -------------------
    # blocks until you get a frame from device.
    # returns a dict representing the most recent frame.
    def get_frame (self):

        return json.loads (self.socket.recv ()[len(device_filters[self.device]):])


    # Function: get_framerate
    # -----------------------
    # empirically determines the framerate in frames/second
    def get_framerate (self, num_frames=5):

        start_time = time.time ()
        for i in range (int(num_frames)):
            self.get_frame ()
        end_time = time.time ()
        return (num_frames)/(end_time - start_time)





