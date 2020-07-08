#!/usr/bin/env python
# -*- coding: utf-8 -*-


import udacidrone
from udacidrone import Drone
from udacidrone.connection import MavlinkConnection
import numpy as np




def create_drone( simulator = False):

	# mav-link connection class:
	conn = MavlinkConnection('tcp:127.0.0.1:8021', threaded=True) #MavlinkConnection('tcp:127.0.0.1:5460', threaded=True)

	#Drone-Class
	drone_ = Drone(conn)

	#Set Home
	drone_.set_home_position(drone_.global_position[0], drone_.global_position[1], drone_.global_position[2])

	return drone_

def py_command_drone(drone, r_step = 0.5, l_step = 0.5, u_step = 0.5, d_step = 0.5):
	do_py_control = True
	drone.start()

	while do_py_control and drone.connected:
		action = input("drone command??")

		if action =="stop":
			drone.stop()
			do_py_control = False

		elif action == "arm":
			drone.take_control()
			drone.arm()

		elif action == "pos":
			print(" global position: ", drone.global_position)
			print(" local position [NED]: ", drone.local_position)

		elif action =="take-off":
			drone.takeoff(10)

		elif action == "a":
			print (drone.local_position, r_step)
			p = drone.local_position + np.array([r_step, 0, 0])

			drone.cmd_position(p[0], p[1], p[2],0.22)

			print(drone.local_position)

		else:
			print("unavailable command")



def main():
	print('Hello => excercise started')
	drone = create_drone()
	py_command_drone(drone)


if __name__ == '__main__':
	main()
