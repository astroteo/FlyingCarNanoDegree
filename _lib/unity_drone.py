#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import udacidrone
from udacidrone import Drone
from udacidrone.connection import MavlinkConnection, WebSocketConnection
import numpy as np
import time
import math
from enum import Enum
import visdom
from udacidrone.messaging import MsgID

class States(Enum):
    """
    all states:
    to be used as States.MANUAL or others

    """
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5

def get_waypoints(height = 5):
        """TODO: Fill out this method

        1. Return waypoints to fly a box
        """
        print("Setting Home")
        local_waypoints = [[15.0, 0.0, height], [15.0, 15.0, height], [0.0, 15.0,height], [0.0, 0.0, height]]
        return local_waypoints


class BackyardFlyerDrone(Drone):
    def __init__(self,connection_ , name_ = None):
        super().__init__(connection_)
        self.connection = connection_
        self.in_mission = True

        self.name = name_ if name_ else "unkonwn_drone"
        print("created a  drone named: " + str(self.name))

        self.all_waypoints = get_waypoints()

        self.register_callback(MsgID.LOCAL_POSITION, self.do_mission)
        self.flight_state = States.MANUAL

    def start_drone(self, keyboard_control_drone = True):
        super().start()
        self.take_control()
        self.arm()
        time.sleep(1)
        print("... start logging ...")
        self.start_log("Logs", "NavLog"+self.name+".txt")
        self.set_home_position(self.global_position[0],
                               self.global_position[1],
                               self.global_position[2])


        if keyboard_control_drone:
            print(" drone @ keyboard-control mode")
            self.keyboard_control()
        else:
            print(" drone @ automated mode")
            self.do_mission()

    def keyboard_control(self):
        while True:
            self.action = input("drone command??")

            if self.action =="stop":
                self.stop()

            elif self.action == "pos":
                print(" global position: ", self.global_position)
                print(" local position [NED]: ", self.local_position)

            elif self.action =="take-off":
                self.set_home_as_current_position()
                self.takeoff(3)

            elif self.action == "land":
                self.land()

            elif self.action == "state":
                print(self.flight_state)

            elif self.action == "a":
                x = self.local_position[0] - 1
                y = self.local_position[1]
                z = self.local_position[2]
                self.cmd_position(2, 3, 3 ,0)

            elif self.action == "w":
                p_new = (self.local_position + np.array([0, 1, 0])).tolist()
                self.cmd_position(float(p_new[0]), float(p_new[1]), float(p_new[2]) ,0)

            elif self.action == "s":
                p_new = (self.local_position + np.array([0, -1, 0])).tolist()
                self.cmd_position(float(p_new[0]), float(p_new[1]), float(p_new[2]) ,0)

            elif self.action == "d":
                p_new = (self.local_position + np.array([1, 0, 0])).tolist()
                self.cmd_position(float(p_new[0]), float(p_new[1]), float(p_new[2]) ,0)

            elif self.action == "arm":
                self.take_control()
                self.arm()

            else:
                print("unavailable command")

    def do_mission(self, height = 5):
        print("take off ...")
        if self.flight_state == States.MANUAL and self.flight_state != States.TAKEOFF and self.flight_state != States.READY:
            self.flight_state = States.TAKEOFF
            self.takeoff(height)
            self.flight_state = States.READY

            print( self.flight_state , self.all_waypoints)

        elif self.flight_state == States.READY and len(self.all_waypoints) > 0:
            print("transition...")
            self.flight_state = States.WAYPOINT
            self.target_position = self.all_waypoints.pop(0)
            self.cmd_position(self.target_position[0], self.target_position[1], self.target_position[2], 0.0)
            if  math.sqrt ((self.local_position[0] - self.target_position[0])**2 + (self.local_position[1] - self.target_position[1])**2+ (self.local_position[2] - self.target_position[2])**2) < 1:
                self.flight_state = States.READY
                print("HERE => transition completed to: " + str(self.target_position))
        else:
            pass
            #land


        #print("waypoint transition")
        #print( self.all_waypoints)

        #print('target position', self.target_position)
        #


    def waypoint_transition(self):
        print("waypoint transition")
        self.target_position = self.all_waypoints.pop(0)
        print('target position', self.target_position)
        self.cmd_position(self.target_position[0], self.target_position[1], self.target_position[2], 0.0)
        self.flight_state = States.WAYPOINT



if __name__ == "__main__":
    web_socket = False
    conn = None
    conn_iter = 1
    if web_socket:
        conn = WebSocketConnection('ws://127.0.0.1:5760')
    else:
        conn = MavlinkConnection('tcp:127.0.0.1:5760', threaded=True, PX4=False)
                            # simulator-unity + keyboard_control  =>threaded = True, PX4 = False

    if conn:
        byfl = BackyardFlyerDrone(conn, name_ = "pippo")
        time.sleep(2)
        print("... let's start! ")
        byfl.start_drone(keyboard_control_drone = False)
