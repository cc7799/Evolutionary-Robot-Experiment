import numpy
import os
import random
import time
from typing import List, Dict

import pyrosim.pyrosim as pyrosim
import safe_file_access as sfa
import simulate
import constants as c
import system_info as si


class Solution:
    """
    Data and controls for creating and simulation a single solution
    """
    def __init__(self, solution_id: int, num_legs: int):
        self.solution_id = solution_id
        assert(num_legs % 2 == 0)
        self.num_legs = num_legs

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
        def get_joint_x_pos():
            joint_x: Dict = {}

            half_gap_length = gap_length / 2
            half_leg_length = leg_length / 2

            if legs_per_side % 2 == 0:
                legs_per_region = int(legs_per_side / 2)
                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[legs_per_region:]

                next_pos_leg_pos = half_gap_length
                for positive_leg in positive_region_legs:
                    joint_x[positive_leg] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_length + gap_length)

                next_neg_leg_pos = -1 * half_gap_length
                for negative_leg in negative_region_legs:
                    joint_x[negative_leg] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_length + gap_length)

            else:
                # There will be a leg directly in the middle
                legs_per_region = int(legs_per_side / 2)
                center_leg = leg_types[legs_per_region]
                joint_x[center_leg] = 0

                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[(legs_per_region + 1):]

                next_pos_leg_pos = (leg_length / 2) + gap_length
                for positive_leg in positive_region_legs:
                    joint_x[positive_leg] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_length + gap_length)

                next_neg_leg_pos = -1 * ((leg_length / 2) + gap_length)
                for negative_leg in negative_region_legs:
                    joint_x[negative_leg] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_length + gap_length)

            return joint_x

        num_legs = self.num_legs

        leg_length = 0.2

        legs_per_side = int(num_legs / 2)

        gap_length = 2 * leg_length

        torso_x_length = (gap_length * (legs_per_side + 1)) + (leg_length * legs_per_side)

        leg_types = []
        for i in range(1, (legs_per_side + 1)):
            leg_types.append(str(i))

        body_dim = {"torso": {"x": torso_x_length, "y": 1, "z": 1},
                    "upper_leg": {"x": 0.2, "y": 1, "z": 0.2},
                    "lower_leg": {"x": 0.2, "y": 0.2, "z": 1}}

        torso_pos = {"x": 0, "y": 0, "z": 1}

        leg_pos = {
            "upper": {
                "left": {"x": 0, "y": -0.5, "z": 0},
                "right": {"x": 0, "y": 0.5, "z": 0}},
            "lower": {
                "left": {"x": 0, "y": 0, "z": -0.5},
                "right": {"x": 0, "y": 0, "z": -0.5}}}

        joint_x_pos = get_joint_x_pos()

        joints_pos: Dict = {"torso_upper": {},

                            "upper_lower": {
                                "left": {"x": 0, "y": -1, "z": 0},
                                "right": {"x": 0, "y": 1, "z": 0}}}

        for leg in leg_types:
            joints_pos["torso_upper"][leg] = {"left":  {"x": joint_x_pos[leg], "y": -0.5, "z": 1},
                                              "right": {"x": joint_x_pos[leg], "y":  0.5, "z": 1}}

        rotation_axes = {"upper": c.joint_axes["x"],
                         "lower": c.joint_axes["y"]}

        sfa.safe_start_urdf(c.ROBOT_FILENAME)

        self.create_torso(dim=body_dim["torso"], pos=torso_pos)
        self.create_legs(leg_types=leg_types,
                         body_dim=body_dim,
                         leg_pos=leg_pos, joints_pos=joints_pos,
                         rotation_axes=rotation_axes)

        pyrosim.End()

    def create_torso(self, dim, pos):
        pyrosim.Send_Cube(name="torso",
                          pos=[pos["x"], pos["y"], pos["z"]],
                          size=[dim["x"], dim["y"], dim["z"]])
        self.link_names.append("torso")

    def create_legs(self, leg_types: List,
                    body_dim: Dict, leg_pos: Dict, joints_pos: Dict,
                    rotation_axes: Dict):

        sides = ["left", "right"]

        for side in sides:
            for leg_type in leg_types:
                upper_leg_name = leg_type + side.capitalize() + "Leg"
                lower_leg_name = leg_type + side.capitalize() + "LowerLeg"

                self.create_upper_leg(name=upper_leg_name,
                                      dim=body_dim["upper_leg"],
                                      pos=leg_pos["upper"][side],
                                      joint_pos=joints_pos["torso_upper"][leg_type][side],
                                      joint_axis=rotation_axes["upper"])

                self.create_lower_leg(name=lower_leg_name, parent_name=upper_leg_name,
                                      dim=body_dim["lower_leg"],
                                      pos=leg_pos["lower"][side],
                                      joint_pos=joints_pos["upper_lower"][side],
                                      joint_axis=rotation_axes["lower"])

    def create_upper_leg(self, name: str, dim: Dict, pos: Dict, joint_pos: dict, joint_axis: str):
        pyrosim.Send_Cube(name=name,
                          pos=[pos["x"], pos["y"], pos["z"]],
                          size=[dim["x"], dim["y"], dim["z"]])
        self.link_names.append(name)

        joint_name = "torso_" + name
        pyrosim.Send_Joint(name=joint_name,
                           parent="torso", child=name,
                           type="revolute",
                           position=[joint_pos["x"],
                                     joint_pos["y"],
                                     joint_pos["z"]],
                           jointAxis=joint_axis)
        self.joint_names.append(joint_name)

    def create_lower_leg(self, name: str, parent_name, dim: Dict, pos: Dict, joint_pos: dict, joint_axis: str):
        pyrosim.Send_Cube(name=name,
                          pos=[pos["x"], pos["y"], pos["z"]],
                          size=[dim["x"], dim["y"], dim["z"]])
        self.link_names.append("frontLeftLowerLeg")

        joint_name = parent_name + "_" + name
        pyrosim.Send_Joint(name=joint_name,
                           parent=parent_name, child=name,
                           type="revolute",
                           position=[joint_pos["x"],
                                     joint_pos["y"],
                                     joint_pos["z"]],
                           jointAxis=joint_axis)
        self.joint_names.append("frontLeg_frontLowerLeg")

    def create_brain(self):
        """
        Initializes the robot's neurons
        """
        brain_filename = c.OBJECTS_FOLDER_NAME + "brain" + str(self.solution_id) + ".nndf"
        sfa.safe_start_neural_network(brain_filename)

        # Neurons #
        # current_neuron_name: int = 0
        # for link_name in self.link_names:
        #     pyrosim.Send_Sensor_Neuron(name=current_neuron_name, linkName=link_name)
        #     current_neuron_name += 1
        #
        # for joint_name in self.joint_names:
        #     pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName=joint_name)
        #     current_neuron_name += 1

        pass
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="torso_frontLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="frontLeg_frontLowerLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="torso_backLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="backLeg_backLowerLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="torso_leftLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="leftLeg_leftLowerLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="torso_rightLeg")
        # current_neuron_name += 1
        # pyrosim.Send_Motor_Neuron(name=current_neuron_name, jointName="rightLeg_rightLowerLeg")

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

        # # Motor Neurons
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
