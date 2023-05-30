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

    def __init__(self, solution_id: int, num_legs: int, cpg_active: bool):
        self.solution_id = solution_id
        self.num_legs = num_legs
        self.cpg_active = cpg_active

        self.fitness: float = -1
        self.link_names: List[str] = []
        self.joint_names: List[str] = []

        self.weights: numpy.matrix
        self.cpg_rate: int
        self.num_sensor_or_hidden_neurons: int
        self.num_motor_neurons: int

        self.create_world()
        self.create_body()
        self.initialize_weights_and_rate(new_brain=True)

    def start_simulation(self, show_gui=False, parallel=True):
        """
        Start the simulation
        :param show_gui: Whether the graphical representation of the simulation should be shown
        :param parallel: Whether the simulation should start as a separate process
        """

        def create_simulate_begin_system_call() -> str:
            """
            Creates a system call that runs simulate.py in parallel mode
            :return: The system call
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

        self.create_brain()

        # Run Simulation #
        if parallel:
            os.system(create_simulate_begin_system_call())
        else:
            simulate.begin_simulation(show_gui=show_gui, solution_id=self.solution_id)

    def wait_for_sim_to_end(self):
        """
        Waits for the simulation to end and gets its fitness
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
        """
        Show a specific solution without evolving the solution at all
        :param solution_index: The index of the solution to be shown
        """
        self.create_world()
        self.create_body()

        if self.cpg_active:
            weights_filename, cpg_rate_filename = self.create_weights_and_rate_filenames(solution_index)

            self.initialize_weights_and_rate(new_brain=False,
                                             weights_filename=weights_filename, cpg_rate_filename=cpg_rate_filename)
        else:
            weights_filename = self.create_weights_and_rate_filenames(solution_index)[0]

            self.initialize_weights_and_rate(new_brain=False, weights_filename=weights_filename)

        self.create_brain()

        simulate.begin_simulation(show_gui=True, solution_id=self.solution_id)

    def create_world(self):
        """
        Initializes world
        """
        sfa.safe_start_sdf(c.WORLD_FILENAME)

        pyrosim.End()

    def create_body(self):
        """
        Creates the body of the robot
        """
        def get_joint_x_positions() -> Dict[str, float]:
            """
            Gets the x-positions where the joints of the upper legs should be placed on the torso
            :return: A dictionary containing the names of each leg matched to it's x-position
            """
            joint_x: Dict = {}

            half_gap_length = gap_length / 2
            half_leg_length = leg_width / 2

            if legs_per_side % 2 == 0:
                legs_per_region = int(legs_per_side / 2)
                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[legs_per_region:]

                next_pos_leg_pos = half_gap_length
                for positive_leg_name in positive_region_legs:
                    joint_x[positive_leg_name] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_width + gap_length)

                next_neg_leg_pos = -1 * half_gap_length
                for negative_leg_name in negative_region_legs:
                    joint_x[negative_leg_name] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_width + gap_length)

            else:
                # There will be a leg directly in the middle
                legs_per_region = int(legs_per_side / 2)
                center_leg = leg_types[legs_per_region]
                joint_x[center_leg] = 0

                positive_region_legs = leg_types[0: legs_per_region]
                negative_region_legs = leg_types[(legs_per_region + 1):]

                next_pos_leg_pos = (leg_width / 2) + gap_length
                for positive_leg_name in positive_region_legs:
                    joint_x[positive_leg_name] = next_pos_leg_pos + half_leg_length
                    next_pos_leg_pos += (leg_width + gap_length)

                next_neg_leg_pos = -1 * ((leg_width / 2) + gap_length)
                for negative_leg_name in negative_region_legs:
                    joint_x[negative_leg_name] = next_neg_leg_pos - half_leg_length
                    next_neg_leg_pos -= (leg_width + gap_length)

            return joint_x

        def create_torso():
            """
            Creates the torso of the robot
            """
            dimensions = body_dimensions["torso"]
            positions = torso_position

            pyrosim.Send_Cube(name="torso",
                              pos=[positions["x"], positions["y"], positions["z"]],
                              size=[dimensions["x"], dimensions["y"], dimensions["z"]])
            self.link_names.append("torso")

        def create_legs():
            """
            Creates the legs of the robot
            """
            def create_upper_leg(name: str, dim: Dict, pos: Dict, joint_pos: dict, joint_axis: str):
                """
                Creates a single upper leg of the robot
                :param name: The name of the leg
                :param dim: The dimensions of the leg
                :param pos: The position of the leg
                :param joint_pos: The position of the leg's joint
                :param joint_axis: The axis of rotation
                """
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

            def create_lower_leg(name: str, parent_name, dim: Dict, pos: Dict, joint_pos: dict, joint_axis: str):
                """
                Creates a single lower leg of the robot
                :param name: The name of the leg
                :param parent_name: The name of the leg's upper-leg parent
                :param dim: The dimensions of the leg
                :param pos: The position of the leg
                :param joint_pos: The position of the leg's joint
                :param joint_axis: The axis of rotation
                """
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

            self.link_names = []
            self.joint_names = []

            sides = ["left", "right"]

            for side in sides:
                for leg_type in leg_types:
                    upper_leg_name = leg_type + side.capitalize() + "Leg"
                    lower_leg_name = leg_type + side.capitalize() + "LowerLeg"

                    create_upper_leg(name=upper_leg_name,
                                     dim=body_dimensions["upper_leg"],
                                     pos=leg_positions["upper"][side],
                                     joint_pos=joint_positions["torso_upper"][leg_type][side],
                                     joint_axis=rotation_axes["upper"])

                    create_lower_leg(name=lower_leg_name, parent_name=upper_leg_name,
                                     dim=body_dimensions["lower_leg"],
                                     pos=leg_positions["lower"][side],
                                     joint_pos=joint_positions["upper_lower"][side],
                                     joint_axis=rotation_axes["lower"])

        num_legs = self.num_legs

        leg_width = 0.2

        legs_per_side = int(num_legs / 2)

        gap_length = 5 * leg_width

        torso_x_length = (gap_length * (legs_per_side - 1)) + (leg_width * legs_per_side)

        leg_types = []
        for i in range(1, (legs_per_side + 1)):
            leg_types.append(str(i))

        body_dimensions = {
            "torso": {"x": torso_x_length, "y": 1, "z": 1},
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
                "left": {"x": joint_x_positions[leg], "y": -0.5, "z": 1},
                "right": {"x": joint_x_positions[leg], "y": 0.5, "z": 1}}

        rotation_axes = {"upper": c.joint_axes["x"],
                         "lower": c.joint_axes["y"]}

        sfa.safe_start_urdf(c.ROBOT_FILENAME)

        create_torso()
        create_legs()

        self.num_sensor_or_hidden_neurons = len(self.link_names) + 1
        self.num_motor_neurons = len(self.joint_names)

        pyrosim.End()

    def create_brain(self):
        """
        Initializes the robot's neurons and synapses
        """
        brain_filename = c.OBJECTS_FOLDER_NAME + "brain" + str(self.solution_id) + ".nndf"
        sfa.safe_start_neural_network(brain_filename)

        # Neurons #
        # Sensor Neurons
        current_neuron_name: int = 0
        for link_name in self.link_names:
            pyrosim.Send_Sensor_Neuron(name=current_neuron_name, linkName=link_name)
            current_neuron_name += 1

        # Central Pattern Generator (CPG) Neuron
        if self.cpg_active:
            pyrosim.Send_CPG_Neuron(current_neuron_name, self.cpg_rate)
            current_neuron_name += 1

        # Motor Neurons
        for joint_name in self.joint_names:
            pyrosim.Send_Motor_Neuron(current_neuron_name, joint_name)
            current_neuron_name += 1

        # Synapses #
        for row in range(self.num_sensor_or_hidden_neurons):
            for col in range(self.num_motor_neurons):
                pyrosim.Send_Synapse(sourceNeuronName=row,
                                     targetNeuronName=(col + self.num_sensor_or_hidden_neurons),
                                     weight=self.weights[row][col])

        pyrosim.End()

    def initialize_weights_and_rate(self, new_brain: bool, weights_filename: str = None, cpg_rate_filename: str = None):
        """
        Initializes the synapse weights and cpg rate
        :param new_brain: Should the weights a cpg rate be randomly generated
        :param weights_filename: The .npy file storing the weights matrix
        :param cpg_rate_filename: The .txt file storing the cpg rate, if this is a robot with a cpg
        """
        if new_brain:
            # Generate a random matrix to store neuron weights normalized to [-1, 1]
            self.weights = (numpy.random.rand(self.num_sensor_or_hidden_neurons, self.num_motor_neurons) * 2) - 1

            if self.cpg_active:
                self.cpg_rate = random.randint(1, c.MAX_INITIAL_CPG_RATE)
        else:
            self.weights = sfa.safe_numpy_file_load(weights_filename)

            if self.cpg_active:
                self.cpg_rate = sfa.safe_file_read(cpg_rate_filename)[0]

    def mutate(self):
        """
        Randomly changes either one neuron weight or, if cpg_active is true, the cpg_rate
        """
        def mutate_weights():
            """
            Randomly changes one synapse weight
            """
            row_to_change = random.randint(0, (len(self.weights) - 1))
            col_to_change = random.randint(0, (len(self.weights[0]) - 1))

            self.weights[row_to_change][col_to_change] = (random.random() * 2 - 1)

        def mutate_cpg_rate():
            """
            Randomly changes the cpg rate by at most plus or minus `c.MAX_CPG_CHANGE`
            """
            rate_change = max(c.MIN_CPG_RATE, random.randint(-c.MAX_CPG_CHANGE, c.MAX_CPG_CHANGE))
            self.cpg_rate += rate_change

        if self.cpg_active:
            if random.randint(1, 2) % 2 == 0:
                mutate_weights()
            else:
                mutate_cpg_rate()
        else:
            mutate_weights()

    def save_weights(self, index: int):
        """
        Saves the matrix storing the synapse weights to a .npy file and, if there's a cpg, saves the rate to a .txt file
        """
        weights_filename, cpg_rate_filename = self.create_weights_and_rate_filenames(index)

        sfa.safe_numpy_file_save(weights_filename, self.weights)

        if self.cpg_active:
            cpg_rate_filename = c.SOLUTIONS_FOLDER_NAME + "cpg_rate" + str(index) \
                                + "(" + str(self.num_legs) + "_legs)" + ".txt"

            sfa.safe_file_write(cpg_rate_filename, str(self.cpg_rate), overwrite=True)

    def create_weights_and_rate_filenames(self, index: int):
        """
        Creates the filenames for storing and reading the synapse weights and cpg rate
        :return: A tuple containing the weights filename and either the cpg rate filename or None, if there is no cpg
        """
        if self.cpg_active:
            cpg_rate_filename = c.SOLUTIONS_FOLDER_NAME + "cpg_rate" + str(index) \
                                + "(" + str(self.num_legs) + "_legs)" + ".txt"

            cpg_type_name = "active"

        else:
            cpg_rate_filename = None

            cpg_type_name = "inactive"

        weights_filename = c.SOLUTIONS_FOLDER_NAME + "weights" + str(index) \
            + "(" + str(self.num_legs) + "_legs, " + cpg_type_name + "_cpg)" + ".npy"

        return weights_filename, cpg_rate_filename

    def set_id(self, solution_id: int):
        """
        Set the solution's id
        :param solution_id: The value that should be set as the id
        """
        self.solution_id = solution_id
