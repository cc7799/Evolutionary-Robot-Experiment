import numpy

import pyrosim.pyrosim as pyrosim
import sim_controls as sc


class Sensor:
    """
    Controls a single sensor
    """
    def __init__(self, link_name: str):
        self.link_name = link_name
        self.sensor_values = numpy.zeros(sc.NUM_FRAMES)

    def get_value(self, time_step: int):
        """
        Determines and saves whether the sensor is touching the ground
        :param time_step: The current time step of the simulation
        :return: The current sensor value
        """
        sensor_value = pyrosim.Get_Touch_Sensor_Value_For_Link(self.link_name)
        self.sensor_values[time_step] = sensor_value
        return sensor_value

    def save_values(self):
        """
        Save the values of a sensor
        """
        filename = "data/" + self.link_name + "Sensor.npy"
        with open(filename, "wb"):
            numpy.save(filename, self.sensor_values)
