import os

import pybullet as p

import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
from motor import Motor
from sensor import Sensor
import constants as c
import system_info as si


def get_joint_type(joint_name: str):
    parent_link_index = joint_name.index("_")

    parent_link_name = joint_name[0:parent_link_index]

    if parent_link_name == "torso":
        return "torso"
    else:
        return "lower_leg"


class Robot:
    """
    A class for controlling a simulated robot
    """
    def __init__(self, solution_id):
        self.solution_id = solution_id

        self.robotId = p.loadURDF(c.ROBOT_FILENAME)

        pyrosim.Prepare_To_Simulate(self.robotId)

        self.sensors = {}
        self.prepare_to_sense()

        # Setup Motors #
        self.motors = {}
        self.prepare_to_act()

        # Neural Network #
        brain_filename = c.OBJECTS_FOLDER_NAME + "brain" + str(self.solution_id) + ".nndf"
        self.nn = NEURAL_NETWORK(brain_filename)

        if si.WINDOWS:
            system_call = "del "
        else:
            system_call = "rm "

        system_call += "\"" + si.PROJECT_FILEPATH + brain_filename + "\""
        os.system(system_call)

    def prepare_to_sense(self):
        """
        Creates a list of all the robot's sensors
        :return:
        """
        for link_name in pyrosim.linkNamesToIndices:
            self.sensors[link_name] = Sensor(link_name)

    def sense(self, time_step):
        """
        Gets the value of every sensor
        :param time_step: The current time step of the simulation
        """
        for sensor in self.sensors.values():
            sensor.get_value(time_step)

    def prepare_to_act(self):
        """
        Creates a list of all the robot's joints
        :return:
        """
        for joint_name in pyrosim.jointNamesToIndices:
            self.motors[joint_name] = Motor(joint_name)

    def act(self):
        """
        Sets every motor to their determined angle
        """
        for neuronName in self.nn.Get_Neuron_Names():
            if self.nn.Is_Motor_Neuron(neuronName):
                joint_name = self.nn.Get_Motor_Neuron_Joint(neuronName)

                joint_type = get_joint_type(joint_name)
                if joint_type == "torso":
                    joint_range = c.TORSO_MOTOR_JOINT_RANGE
                else:
                    joint_range = c.LOWER_LEG_MOTOR_JOINT_RANGE

                desired_angle = self.nn.Get_Value_Of(neuronName) * joint_range

                joint_name_bytes = bytes(joint_name, "utf-8")
                self.motors[joint_name_bytes].set_value(self.robotId, desired_angle)

    def think(self, current_timestep: int, cpg_rate: int):
        """
        Updates the robot's neural network
        """
        self.nn.Update(current_timestep)

    def get_fitness(self):
        """
        Calculates the robot's fitness and writes it to a file with protection to allow for parallel simulations
        """
        x_position = p.getBasePositionAndOrientation(self.robotId)[0][0]
        # x_position = base_position[0]

        tmp_fitness_filename = c.FITNESS_FOLDER_NAME + "tmp" + str(self.solution_id) + ".txt"
        fitness_filename = c.FITNESS_FOLDER_NAME + "fitness" + str(self.solution_id) + ".txt"
        with open(tmp_fitness_filename, "w") as fileout:
            fileout.write(str(x_position))

        # Change the name of the file only after it has been written,
        #   this will prevent it being read early by the parallelized solution
        if si.WINDOWS:
            os.rename(tmp_fitness_filename, fitness_filename)
        else:
            system_call = "mv " + tmp_fitness_filename + " " + fitness_filename
            os.system(system_call)

    def save_values(self):
        """
        Saves the current values of the sensors and motors
        """
        for sensor in self.sensors.values():
            sensor.save_values()

        for motor in self.motors.values():
            motor.save_value()
