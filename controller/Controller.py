from pymouse import PyMouse
from pykeyboard import PyKeyboard
from time import sleep, time
from gravityThread import gravityThread as gravT
from icon import Icon, iconList
import sys
import threading
from util import *
from displayThread import displayThread
import numpy as np
import Tkinter as tk
import AppKit
import math
from controller_parameters import controller_parameters as parameters

# from Quartz.CoreGraphics import CGEventCreateMouseEvent
# from Quartz.CoreGraphics import CGEventPost
# from Quartz.CoreGraphics import kCGEventMouseMoved
# from Quartz.CoreGraphics import kCGEventLeftMouseDown
# from Quartz.CoreGraphics import kCGEventLeftMouseDown
# from Quartz.CoreGraphics import kCGEventLeftMouseUp
# from Quartz.CoreGraphics import kCGMouseButtonLeft
# from Quartz.CoreGraphics import kCGHIDEventTap
class Controller(threading.Thread):

	# parameters = controller_parameters

	def signedExponent(self,vec, exp):
		new_vec = vec.copy()
		for i in range(len(vec)):
			if vec[i] < 0:
				new_vec[i] = -(abs(vec[i])**exp)
			else:
				new_vec[i] = vec[i]**exp

		return new_vec


	def normalize(self,vec):
		return vec / (np.linalg.norm(vec))

	def pocketStart(self):
		self.curr_time = None

	def precisionStart(self):
		self.curr_time = None


	def controlGesture(self, mode, vec):
		if mode == 'POCKET_MODE':
			
			if self.curr_time == None:
				self.curr_time = time()
				return
			else:
				# print "VEC: ", vec
				vec = np.array(vec)
				vec = self.signedExponent(vec, parameters['joystick_exponent'])
				# vec = np.array(vec)**2
				curr_time = time()
				time_diff = curr_time - self.curr_time
				self.curr_time = curr_time
				gravity_vec = self.grav_thread.get_velocity()
				# print "GRAV VEC: ", gravity_vec
				# print "\n\n"
				# print "gravity vec", gravity_vec
				# print "hand vec", vec

				combined_vec = vec + gravity_vec
				if np.linalg.norm(combined_vec) > self.velocity_cap:
					# print "norm was: ", np.linalg.norm(combined_vec)
					normalized_vec = self.normalize(combined_vec)
					new_vec = normalized_vec*self.velocity_cap
					combined_vec = new_vec


				# print combined_vec
				currPos = self.mk.getMousePosition()
				# if np.sum(gravity_vec) < .1:
					# print currPos
				displacement = (time_diff * combined_vec)/parameters['speed_scalar']
				self.mk.mouseMove(currPos + displacement)
				sleep (parameters['controller_sleep'])

		if mode == 'PRECISION_MODE':
			if self.curr_time == None:
				self.curr_time = time()
				return
			else:
				# self.precision_
				width = self.screen_rect[2] - self.screen_rect[0]
				height = self.screen_rect[3] - self.screen_rect[1]
				new_x = width*vec[0] + self.screen_rect[0]
				new_y = height*vec[1] + self.screen_rect[1]

				self.mk.mouseMove([new_x,new_y])

				# curr_time = time()
				# time_diff = curr_time - self.curr_time
				# self.curr_time = curr_time

				# gravity_vec = self.grav_thread.get_velocity()
				# displacement = (time_diff * gravity_vec)/parameters['speed_scalar']
				# self.mk.mouseMove(np.array([new_x,new_y]) + displacement)

		

## PASSABLE STRINGS INTO discreteGesture: 'click', 'divvy_left', 'divvy_right', 'divvy_full'
	def discreteGesture(self, gesture):
		self.gesture_map[gesture]()

	def readInIconList(self, icon_list_file):
		#pass
		# icon = Icon(361.1, 661.4, lambda x: (self.max_velocity/(x)), 25)
		# icon2 = Icon(227.3, 710.85, lambda x: (self.max_velocity/x), 25)
		# return [icon, icon2]


		icons = []
		icon_file = open(icon_list_file, 'r')
		for line in icon_file:
			splits = line.rstrip('\r').rstrip('\n').rstrip('\r').split(',')
			icon = Icon(float(splits[0]),float(splits[1]), lambda x:self.grav_pull/(x+1))
			icons.append(icon)
		


		return icons

	def readInGestureMap(self, gesture_map_file):
		gesture_map = {}
		map_file = open(gesture_map_file, 'r')
		for line in map_file:
			splits = line.rstrip('\r').rstrip('\n').rstrip('\r').split(',')
			gesture_map[splits[0]] = splits[1]

		return gesture_map


	def find_max_gravity(self):
		thresh = parameters['joystick_threshold']
		exp = parameters['joystick_exponent']
		radius = parameters['beder_radius']
		max_gravity = (thresh*radius)#**exp
		return max_gravity


	def currMouseClick(self):
		currPos = self.mk.getMousePosition()
		self.mk.mouseClick(currPos)

	def minimize(self):
		self.mk.keyboard.press_key('shift')
		sleep(.1)
		self.mk.keyboard.tap_key('d')
		sleep(.1)
		self.mk.keyboard.release_key('shift')

		self.mk.keyboard.tap_key('m')

	def divvyLeft(self):
		self.mk.keyboard.press_key('shift')
		sleep(.1)
		self.mk.keyboard.tap_key('d')
		sleep(.1)
		self.mk.keyboard.release_key('shift')

		self.mk.keyboard.tap_key('l')

		# self.mk.nKeysSequential(['shiftd','l'])

	def divvyRight(self):
		self.mk.keyboard.press_key('shift')
		sleep(.1)
		self.mk.keyboard.tap_key('d')
		sleep(.1)
		self.mk.keyboard.release_key('shift')

		self.mk.keyboard.tap_key('r')

		# self.mk.nKeysSequential(['shiftd','r'])

	def divvyFull(self):
		self.mk.keyboard.press_key('shift')
		sleep(.1)
		self.mk.keyboard.tap_key('d')
		sleep(.1)
		self.mk.keyboard.release_key('shift')

		self.mk.keyboard.tap_key('f')

		# self.mk.nKeysSequential(['shiftd','f'])

	def __init__(self, icon_list_file='icon_list_file.txt', max_velocity=parameters['gravitational_pull'], gesture_map_file=None, precision_scale=1.):
		threading.Thread.__init__(self)
		self.mk = mk()
		self.curr_time = None
		# self.display_thread = displayThread()
		# self.max_velocity = max_velocity
		# self.icons = self.calibrate_icons()
		self.icons= self.readInIconList(icon_list_file)
		# self.icon_list = iconList(self.icons)
		self.grav_thread = None
		self.grav_pull = parameters['gravitational_pull']
		self.max_gravity = self.find_max_gravity()
		self.velocity_cap = parameters['velocity_cap']
		self.screen_rect = self.mk.boundary
		# self.precision_scale = precision_scale
		# self.precision_start_hand = None
		# self.precision_start_mouse
		self.gesture_map = {	'CLICK':self.currMouseClick, 
								'precision':self.precisionStart,
								'pocket':self.pocketStart,
								'divvy_minimize':self.minimize,
								'swipe_left':self.divvyLeft, 
								'swipe_right':self.divvyRight, 
								'divvy_fulli':self.divvyFull,
								'precision_clicking':self.ignore,
								'pocket_clicking':self.ignore							
								}
		# self.gesture_map = self.readInGestureMap(gesture_map)


	def ignore (self):
		pass

	def run(self):
		print_notification('Controller has started running.')

	def startGravity(self):
		# self.display_thread.start()


		self.grav_thread = gravT(self.icons, self.mk,self.max_gravity, self.grav_pull, None, .01)
		# self.grav_thread.start()



	def endGravity(self):
		try:
			self.grav_thread.stop()
			self.grav_thread.join()
		except:
			print "Grav thread wasn't started"



class mk(object):
	def getMousePosition(self):
		mouseposition = self.mouse.position()
		return np.array([mouseposition[0], mouseposition[1]])

	def __init__(self):
		self.mouse = PyMouse()
		self.keyboard = PyKeyboard()
		self.multikey_mapping = {'cmdd':(['cmd'],'d'), 'shiftd':(['shift'],'d')}
		self.boundary = [0,0,AppKit.NSScreen.mainScreen().frame().origin.x + AppKit.NSScreen.mainScreen().frame().size.width, AppKit.NSScreen.mainScreen().frame().origin.y + AppKit.NSScreen.mainScreen().frame().size.height]

	def nKeysSameTime(self, list_of_mod, tap_key):
		for key in list_of_mod:
			self.keyboard.press_key(key)
		sleep(.1)
		self.keyboard.tap_key(tap_key)
		for key in list_of_mod:
			self.keyboard.release_key(key)

	def decompMultiKey(self,key):
		(mod,tap_key) = self.multikey_mapping[key]
		return (mod, tap_key)

	def nKeysSequential(self, list_of_keys):
		for key in list_of_keys:
			try:
				self.keyboard.tap_key(key)
			except RuntimeError:
				try:
					decomp = self.decompMultiKey(key)
				except:
					raise RuntimeError("Key %s not implemented" % key)
				self.nKeysSameTime(decomp[0],decomp[1])
			sleep(.15)
			
		

	def mouseEvent(self, thetype, pos_vec):
		posx = pos_vec[0]
		posy = pos_vec[1]
		theEvent = CGEventCreateMouseEvent(None, thetype, (posx,posy), kCGMouseButtonLeft)
		CGEventPost(kCGHIDEventTap, theEvent)

	def mouseMove(self, pos_vec):
		if pos_vec[0] < self.boundary[0]:
			posx = self.boundary[0]
		elif pos_vec[0] > self.boundary[2]:
			posx = self.boundary[2]
		else:
			posx = pos_vec[0]


		if pos_vec[1] < self.boundary[1]:
			posy = self.boundary[1]
		elif pos_vec[1] > self.boundary[3]:
			posy = self.boundary[3]
		else:
			posy = pos_vec[1]
		
		self.mouse.move(posx,posy)
		# self.mouseEvent(kCGEventMouseMoved, posx, posy)

	def mouseClick(self, pos_vec):
		posx = pos_vec[0]
		posy = pos_vec[1]
		self.mouse.press(posx,posy,button=1)
		self.mouse.release(posx,posy,button=1)

		# self.mouseEvent(kCGEventLeftMouseDown, posx, posy)
		# self.mouseEvent(kCGEventLeftMouseUp, posx, posy)

	def mouseDrag(self,posx,posy):
		self.mouse.press(self.mouse.position()[0],self.mouse.position()[1])
		self.mouse.drag(posx,posy)
		self.mouse.release(posx,posy)



		# self.mouseEvent(kCGEventLeftMouseDown, posx, posy)

	# def endMouseDrag(self,posx,posy):
	# 	self.mouseMove(posx, posy)
	# 	self.mouseEvent(kCGEventLeftMouseUp, posx, posy)

