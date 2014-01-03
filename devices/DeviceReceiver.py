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


# Class: DeviceReceiver
# ---------------------
# class for receiving frames from a device; runs in its own thread.
# - start () to start getting frames (starts thread)
# - stop () to terminate frame-getting (terminates thread)
# - get_frame () to get most recent frame
class DeviceReceiver (threading.Thread):

    # Function: zmq_init
    # ------------------
    # sets up connection to tcp ports via zmq
    def zmq_init (self):

        self.context = zmq.Context ()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect (parameters['connect_address'])
        self.socket.setsockopt(zmq.SUBSCRIBE, device_filters[self.device_name])


    # Function: Constructor 
    # ---------------------
    # connects to the port, starts thread to receive frames
    def __init__ (self, _device_name):

        #===[ Thread-related setup ]===
        threading.Thread.__init__(self)
        self._stop = threading.Event ()
        self._new_frame_available = threading.Event ()
        self.last_frame = None

        #===[ Connect to Device ]===
        if not _device_name in device_filters.keys ():
            print_error ("Unsupported device", str(_device) + " is unrecognized")
        self.device_name = _device_name
        self.column_names = column_names[self.device_name]
        self.zmq_init ()



    # Function: run
    # -------------
    # main for this thread: getting frames
    def run (self):

        while not self._stop.isSet ():
            self.read_frame ()


    # Function: stop
    # --------------
    # call to terminate this thread's operation
    def stop (self):

        self._stop.set ()


    # Function: read_frame 
    # --------------------
    # sets self.last_frame, sets self._frame_available
    def read_frame (self):

        self.last_frame = json.loads (self.socket.recv ()[len(device_filters[self.device_name]):])
        self._new_frame_available.set ()


    # Function: get_frame 
    # -------------------
    # blocks until a new frame is available, returns it
    def get_frame (self):

        self._new_frame_available.wait ()
        self._new_frame_available.clear ()
        return self.last_frame






