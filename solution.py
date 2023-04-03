import numpy
import os
import random
import time
from typing import List

import pyrosim.pyrosim as pyrosim
import safe_file_access as sfa
import simulate
import constants as c
import system_info as si


class Solution:
    """
    Data and controls for creating and simulation a single solution
    """
    def __init__(self, solution_id):
        self.solution_id = solution_id

        # Generate a random matrix to store neuron weights normalized to [-1, 1]
        self.weights = (numpy.random.rand(c.NUM_SENSOR_NEURONS, c.NUM_MOTOR_NEURONS) * 2) - 1

        self.fitness: float = -1

        self.link_names: List[str] = []
        self.joint_names: List[str] = []

    def start_simulation(self, show_gui=False, parallel=True):
        """
        Start the simulation
        :param show_gui: Whether the graphical representation of the simulation should be shown
        :param parallel: Whether the simulation should start as a separate process
        """
        self.create_world()
        self.create_body()
        self.create_brain()

        # Run Simulation #
        if parallel:
            os.system(self.create_simulate_begin_system_call(show_gui))
        else:
            simulate.begin_simulation(show_gui=show_gui, solution_id=self.solution_id)

    def wait_for_sim_to_end(self):
        """
        Wait for the simulation to end and get its fitness
        """
        fitness_filename = c.FITNESS_FOLDER_NAME + "fitness" + str(self.solution_id) + ".txt"

        # Wait until simulations are done before reading fitness values
        while not os.path.exists(fitness_filename):
            time.sleep(0.01)

        self.fitness = float(sfa.safe_file_read(fitness_filename)[0])

        # Delete the fitness file after it has been read
        if si.WINDOWS:
            system_call = "del "
        else:
            system_call = "rm "

        system_call += "\"" + si.PROJECT_FILEPATH + fitness_filename + "\""

        os.system(system_call)

    def set_id(self, solution_id: int):
        """
        Set the solution's id
        :param solution_id: The value that should be set as the id
        """
        self.solution_id = solution_id

    def create_world(self):
        """
        Initializes world
        """
        sfa.safe_start_sdf(c.WORLD_FILENAME)

        pyrosim.End()

    def create_body(self):
        """
        Initializes the robot's links, joints, and motors
        """
        body_dims = {"length": 1, "width": 1, "height": 1}
        leg_dims = {"short_dim": 0.2, "long_dim": 1}
        joint_axes = {"x": "1 0 0", "y": "0 1 0", "z": "0 0 1"}

        x = 0
        y = 0
        z = body_dims["height"]

        sfa.safe_start_urdf(c.ROBOT_FILENAME)

        # Torso
        pyrosim.Send_Cube(name="torso", pos=[x, y, z],
                          size=[body_dims["length"], body_dims["width"], body_dims["height"]])

        # Front Leg
        pyrosim.Send_Cube(name="frontLeg", pos=[0, 0.5, 0],
                          size=[leg_dims["short_dim"], leg_dims["long_dim"], leg_dims["short_dim"]])

        pyrosim.Send_Joint(name="torso_frontLeg", parent="torso", child="frontLeg",
                           type="revolute", position=[0, 0.5, 1],
                           jointAxis=joint_axes["x"])

        pyrosim.Send_Cube(name="frontLowerLeg", pos=[0, 0, -0.5],
                          size=[leg_dims["short_dim"], leg_dims["short_dim"], leg_dims["long_dim"]])

        pyrosim.Send_Joint(name="frontLeg_frontLowerLeg", parent="frontLeg", child="frontLowerLeg",
                           type="revolute", position=[0, 1, 0],
                           jointAxis=joint_axes["x"])

        # Back Leg
        pyrosim.Send_Cube(name="backLeg", pos=[0, -0.5, 0],
                          size=[leg_dims["short_dim"], leg_dims["long_dim"], leg_dims["short_dim"]])

        pyrosim.Send_Joint(name="torso_backLeg", parent="torso", child="backLeg",
                           type="revolute", position=[0, -0.5, 1],
                           jointAxis=joint_axes["x"])

        pyrosim.Send_Cube(name="backLowerLeg", pos=[0, 0, -0.5],
                          size=[leg_dims["short_dim"], leg_dims["short_dim"], leg_dims["long_dim"]])

        pyrosim.Send_Joint(name="backLeg_backLowerLeg", parent="backLeg", child="backLowerLeg",
                           type="revolute", position=[0, -1, 0],
                           jointAxis=joint_axes["x"])

        # Left Leg
        pyrosim.Send_Cube(name="leftLeg", pos=[-0.5, 0, 0],
                          size=[leg_dims["long_dim"], leg_dims["short_dim"], leg_dims["short_dim"]])

        pyrosim.Send_Joint(name="torso_leftLeg", parent="torso", child="leftLeg",
                           type="revolute", position=[-0.5, 0, 1],
                           jointAxis=joint_axes["y"])

        pyrosim.Send_Cube(name="leftLowerLeg", pos=[0, 0, -0.5],
                          size=[leg_dims["short_dim"], leg_dims["short_dim"], leg_dims["long_dim"]])

        pyrosim.Send_Joint(name="leftLeg_leftLowerLeg", parent="leftLeg", child="leftLowerLeg",
                           type="revolute", position=[-1, 0, 0],
                           jointAxis=joint_axes["y"])

        # Right Leg
        pyrosim.Send_Cube(name="rightLeg", pos=[0.5, 0, 0],
                          size=[leg_dims["long_dim"], leg_dims["short_dim"], leg_dims["short_dim"]])

        pyrosim.Send_Joint(name="torso_rightLeg", parent="torso", child="rightLeg",
                           type="revolute", position=[0.5, 0, 1],
                           jointAxis=joint_axes["y"])

        pyrosim.Send_Cube(name="rightLowerLeg", pos=[0, 0, -0.5],
                          size=[leg_dims["short_dim"], leg_dims["short_dim"], leg_dims["long_dim"]])

        pyrosim.Send_Joint(name="rightLeg_rightLowerLeg", parent="rightLeg", child="rightLowerLeg",
                           type="revolute", position=[1, 0, 0],
                           jointAxis=joint_axes["y"])

        pyrosim.End()

    def create_brain(self):
        """
        Initializes the robot's neurons
        """
        brain_filename = c.OBJECTS_FOLDER_NAME + "brain" + str(self.solution_id) + ".nndf"
        sfa.safe_start_neural_network(brain_filename)

        # Neurons #
        # Sensor Neurons
        pyrosim.Send_Sensor_Neuron(name=0, linkName="torso")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="frontLeg")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="frontLowerLeg")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="backLeg")
        pyrosim.Send_Sensor_Neuron(name=4, linkName="backLowerLeg")
        pyrosim.Send_Sensor_Neuron(name=5, linkName="leftLeg")
        pyrosim.Send_Sensor_Neuron(name=6, linkName="leftLowerLeg")
        pyrosim.Send_Sensor_Neuron(name=7, linkName="rightLowerLeg")
        pyrosim.Send_Sensor_Neuron(name=8, linkName="rightLowerLeg")

        # Motor Neurons
        pyrosim.Send_Motor_Neuron(name=9, jointName="torso_frontLeg")
        pyrosim.Send_Motor_Neuron(name=10, jointName="frontLeg_frontLowerLeg")
        pyrosim.Send_Motor_Neuron(name=11, jointName="torso_backLeg")
        pyrosim.Send_Motor_Neuron(name=12, jointName="backLeg_backLowerLeg")
        pyrosim.Send_Motor_Neuron(name=13, jointName="torso_leftLeg")
        pyrosim.Send_Motor_Neuron(name=14, jointName="leftLeg_leftLowerLeg")
        pyrosim.Send_Motor_Neuron(name=15, jointName="torso_rightLeg")
        pyrosim.Send_Motor_Neuron(name=16, jointName="rightLeg_rightLowerLeg")

        # Synapses #
        num_sensor_neurons = len(self.weights)
        num_motor_neurons  = len(self.weights[0])

        for row in range(num_sensor_neurons):
            for col in range(num_motor_neurons):
                pyrosim.Send_Synapse(sourceNeuronName=row,
                                     targetNeuronName=(col + num_sensor_neurons),
                                     weight=self.weights[row][col])

        pyrosim.End()

    def mutate(self):
        """
        Randomly changes one neuron weight
        """
        row_to_change = random.randint(0, (len(self.weights)    - 1))
        col_to_change = random.randint(0, (len(self.weights[0]) - 1))

        self.weights[row_to_change][col_to_change] = (random.random() * 2 - 1)

    def create_simulate_begin_system_call(self, show_gui) -> str:
        """
        Creates a system call that runs simulate.py in parallel mode
        :param show_gui: Whether the graphical representation of the simulation should be shown
        :return: The system call to be run
        """
        system_call = "python simulate.py"

        if show_gui:
            system_call += " GUI"
        else:
            system_call += " DIRECT"

        system_call += " " + str(self.solution_id)

        if si.WINDOWS:
            system_call = "start /B " + system_call
        else:
            system_call += " &"

        return system_call
