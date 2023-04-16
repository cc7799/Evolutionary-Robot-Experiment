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
        self.num_legs = num_legs

        self.weights: numpy.matrix

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

    def show_solution(self, solution_index: int):
        self.create_world()
        self.create_body()

        weights_filename = c.WEIGHTS_FOLDER_NAME + "weights" + str(solution_index) + ".npy"
        self.create_brain(new_brain=False, weights_filename=weights_filename)

        simulate.begin_simulation(show_gui=True, solution_id=self.solution_id)

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
        def get_joint_x_positions():
            joint_x: Dict = {}

            half_gap_length = gap_length / 2
            half_leg_length = leg_width / 2

            if legs_per_side % 2 == 0:
                legs_per_region = int(legs_per_side / 2)
                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[legs_per_region:]

                next_pos_leg_pos = half_gap_length
                for positive_leg in positive_region_legs:
                    joint_x[positive_leg] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_width + gap_length)

                next_neg_leg_pos = -1 * half_gap_length
                for negative_leg in negative_region_legs:
                    joint_x[negative_leg] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_width + gap_length)

            else:
                # There will be a leg directly in the middle
                legs_per_region = int(legs_per_side / 2)
                center_leg = leg_types[legs_per_region]
                joint_x[center_leg] = 0

                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[(legs_per_region + 1):]

                next_pos_leg_pos = (leg_width / 2) + gap_length
                for positive_leg in positive_region_legs:
                    joint_x[positive_leg] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_width + gap_length)

                next_neg_leg_pos = -1 * ((leg_width / 2) + gap_length)
                for negative_leg in negative_region_legs:
                    joint_x[negative_leg] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_width + gap_length)

            return joint_x

        num_legs = self.num_legs

        leg_width = 0.2

        legs_per_side = int(num_legs / 2)

        gap_length = 5 * leg_width

        torso_x_length = (gap_length * (legs_per_side - 1)) + (leg_width * legs_per_side)

        leg_types = []
        for i in range(1, (legs_per_side + 1)):
            leg_types.append(str(i))

        body_dimensions = {
            "torso":     {"x": torso_x_length, "y": 1, "z": 1},
            "upper_leg": {"x": 0.2, "y": 1, "z": 0.2},
            "lower_leg": {"x": 0.2, "y": 0.2, "z": 1}}

        torso_position = {"x": 0, "y": 0, "z": 1}

        leg_positions = {
            "upper": {
                "left": {"x": 0, "y": -0.5, "z": 0},
                "right": {"x": 0, "y": 0.5, "z": 0}},
            "lower": {
                "left": {"x": 0, "y": 0, "z": -0.5},
                "right": {"x": 0, "y": 0, "z": -0.5}}}

        joint_x_positions = get_joint_x_positions()

        joint_positions: Dict = {"torso_upper": {},
                                 "upper_lower": {
                                    "left": {"x": 0, "y": -1, "z": 0},
                                    "right": {"x": 0, "y": 1, "z": 0}}}

        for leg in leg_types:
            joint_positions["torso_upper"][leg] = {
                "left":  {"x": joint_x_positions[leg], "y": -0.5, "z": 1},
                "right": {"x": joint_x_positions[leg], "y":  0.5, "z": 1}}

        rotation_axes = {"upper": c.joint_axes["x"],
                         "lower": c.joint_axes["y"]}

        sfa.safe_start_urdf(c.ROBOT_FILENAME)

        self.create_torso(dim=body_dimensions["torso"], pos=torso_position)
        self.create_legs(leg_types=leg_types,
                         body_dim=body_dimensions,
                         leg_pos=leg_positions, joints_pos=joint_positions,
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

        self.link_names = []
        self.joint_names = []

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
        self.link_names.append(name)

        joint_name = parent_name + "_" + name
        pyrosim.Send_Joint(name=joint_name,
                           parent=parent_name, child=name,
                           type="revolute",
                           position=[joint_pos["x"],
                                     joint_pos["y"],
                                     joint_pos["z"]],
                           jointAxis=joint_axis)
        self.joint_names.append(joint_name)

    def create_brain(self, new_brain: bool = True, weights_filename: str = None):
        """
        Initializes the robot's neurons
        """
        def create_synapse_weights():
            if new_brain:
                return (numpy.random.rand(num_sensor_neurons, num_motor_neurons) * 2) - 1
            else:
                return numpy.load(weights_filename)

        brain_filename = c.OBJECTS_FOLDER_NAME + "brain" + str(self.solution_id) + ".nndf"
        sfa.safe_start_neural_network(brain_filename)

        # Neurons #
        current_neuron_name: int = 0
        for link_name in self.link_names:
            pyrosim.Send_Sensor_Neuron(name=current_neuron_name, linkName=link_name)
            current_neuron_name += 1

        for joint_name in self.joint_names:
            pyrosim.Send_Motor_Neuron(current_neuron_name, joint_name)
            current_neuron_name += 1

        # Synapses #
        num_sensor_neurons = len(self.link_names)
        num_motor_neurons = len(self.joint_names)

        # Generate a random matrix to store neuron weights normalized to [-1, 1]
        self.weights = create_synapse_weights()

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

    def save_weights(self, index: int):
        with open(c.WEIGHTS_FOLDER_NAME + "num_legs.txt", "w") as fileout:
            fileout.write(str(self.num_legs))

        filename = c.WEIGHTS_FOLDER_NAME + "weights" + str(index) + ".npy"
        numpy.save(filename, self.weights)
