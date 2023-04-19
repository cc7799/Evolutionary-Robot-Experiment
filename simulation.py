import random
import sys
import time

import pybullet
import pybullet as p
import pybullet_data
from robot import Robot
from world import World
import constants as c
import sim_controls as sc


class Simulation:
    """
    Controls a single simulation
    """
    def __init__(self, show_gui, solution_id):
        # Setup Sim #
        self.show_gui = show_gui
        if self.show_gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(c.gravity["x"], c.gravity["y"], c.gravity["z"])

        self.world = World()
        self.robot = Robot(solution_id)

    def run(self):
        """
        Runs the simulation for the given number of frames
        """
        try:
            random.seed()
            for time_step in range(0, sc.SIMULATION_CONTROLS["num_frames"]):
                if self.show_gui:
                    time.sleep(1/240)

                p.stepSimulation()

                if sc.SIMULATION_CONTROLS["simulate"]:
                    self.robot.sense(time_step)

                    self.robot.think(current_timestep=time_step, cpg_rate=10)

                    self.robot.act()
        # Should only ever occur when the simulation is being run in `show_gui` mode
        except pybullet.error:
            print("\n*** You closed the simulation window. Simulation aborted. ***")
            sys.exit(0)

    def get_fitness(self):
        """
        Gets the fitness of the simulation's robot
        """
        self.robot.get_fitness()

    def __del__(self):
        """
        Disconnects the pybullet simulation
        """
        try:
            p.disconnect()
        except pybullet.error:
            pass
