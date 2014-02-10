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
from ..threads.StoppableThread import StoppableThread
from .parameters import *


# Class: DeviceReceiver
# ---------------------
# class for receiving frames from a device; runs in its own thread.
# - start () to start getting frames (starts thread)
# - stop () to terminate frame-getting (terminates thread)
# - get_frame () to get most recent frame
class DeviceReceiver (StoppableThread):

    _name = "DeviceReceiver"


    #==========[ Constructor ]==========
    def __init__ (self, _device_name):
        """ 
            PUBLIC: Constructor
            -------------------
            given device name, begins communication with device
        """
        #=====[ Step 1: initialize StoppableThread ]=====
        StoppableThread.__init__ (self, self._name)

        #=====[ Step 2: IPC setup ]=====
        self._new_frame_available = threading.Event ()
        self.last_frame = None

        #===[ Step 3: verify/setup device ]===
        if not _device_name in device_filters.keys ():
            raise TypeError ("Device not supported: " + _device_name)
        self.device_name = _device_name

        #=====[ Step 4: connect to UDP ]=====
        self.zmq_init ()

        #=====[ Step 5: start this thread ]=====
        self.start ()

    #==========[ Destructor ]==========
    def __del__ (self):
        """
            PUBLIC: Destructor
            ------------------
            stops/joins this thread
        """
        self.stop ()
        self.join ()


    #==========[ ZeroMQ: Port Communication ]==========
    def zmq_init (self):
        """
            PRIVATE: zmq_init
            -----------------
            initializes communication with PrimeSenseReceiver via TCP
        """
        self.context = zmq.Context ()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect (connect_parameters['connect_address'])
        self.socket.setsockopt(zmq.SUBSCRIBE, device_filters[self.device_name])


    def thread_iteration (self):
        """
            PRIVATE: thread_iteration
            -------------------------
            grabs a frame via self.read_frame
        """
        self.read_frame ()



    def format_coords (self, d):
        """
            PRIVATE: format_coords
            ----------------------
            goes from strings to floats, puts in nan where appropriate
        """
        return {k:float(v) if not v in connect_parameters['none_substitutes'] else None for k, v in d.items()}


    def format_frame_primesense (self, frame):
        """
            PRIVATE: format_frame_primesense
            ---------------------------------
            given a frame from PrimesenseReceiver, this will format it so that it 
            can go into a pandas dataframe easily
        """
        formatted_frame = {}
        for joint_name, data in frame.iteritems ():
            position = self.format_coords(data['REAL_WORLD_POSITION'])
            orientation = self.format_coords (data['ORIENTATION'])
            formatted_frame [joint_name + "_POSITION"] = position
            formatted_frame [joint_name + "_ORIENTATION"] = orientation
        return formatted_frame



    def read_frame (self):
        """
            PRIVATE: read_frame
            -------------------
            grabs a frame from device communication channel
            sets self.last_frame, self._new_frame_available
        """
        #==========[ Step 1: get raw json dict ]==========
        raw_frame  = json.loads (self.socket.recv ()[len(device_filters[self.device_name]):])

        #==========[ Step 2: reformat ]==========
        formatted_frame = self.format_frame_primesense (raw_frame)

        #==========[ Step 3: store/update ]==========
        self.last_frame = formatted_frame
        self._new_frame_available.set ()


    def get_frame (self):
        """
            PUBLIC: get_frame
            -----------------
            blocks until a new frame is available, then returns it
        """
        self._new_frame_available.wait ()
        self._new_frame_available.clear ()
        return self.last_frame






