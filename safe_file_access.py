"""
Simple set of functions to allow for safe file reads and writes for the parallelized simulations
"""
import time
from typing import List

import numpy
import pybullet as p
import pyrosim.pyrosim as pyrosim


SECONDS_TO_WAIT = 1


def safe_file_read(filename: str) -> List:
    """
    Read a file. If read fails, wait, then try again
    :param filename: The name of the file to read from
    :return: The data from the file
    """
    try:
        with open(filename, "r") as filein:
            return filein.readlines()
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        with open(filename, "r") as filein:
            return filein.readlines()


def safe_numpy_file_load(filename: str):
    """
    Load a numpy file. If load fails, wait, then try again
    :param filename: The name of the file to read from
    :return: The data from the file
    """
    try:
        return numpy.load(filename)
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        return numpy.load(filename)


def safe_file_write(filename: str, data_to_write, overwrite: bool = False):
    """
    Write to a file. If write fails, wait, then try again
    :param filename: The name of the file to write to
    :param data_to_write: The data to be written to the file
    :param overwrite: Whether to overwrite any data already in the file
    """
    if overwrite:
        write_mode = "w"
    else:
        write_mode = "a"

    try:
        with open(filename, write_mode) as fileout:
            fileout.write(data_to_write)
    except PermissionError:
        time.sleep(1)
        with open(filename, write_mode) as fileout:
            fileout.write(data_to_write)


def safe_numpy_file_save(filename: str, array_to_save):
    """
    Save a numpy array to a .npy file. If save fails, wait, then try again
    :param filename: The name of the file to write to
    :param array_to_save: The data to be written to the file
    """

    try:
        numpy.save(filename, array_to_save)
    except PermissionError:
        time.sleep(1)
        numpy.save(filename, array_to_save)


def safe_start_sdf(filename: str):
    """
    Safely start an sdf file. If start fails, wait, then try again
    :param filename: The sdf file
    """
    try:
        pyrosim.Start_SDF(filename)
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        pyrosim.Start_SDF(filename)


def safe_load_sdf(filename: str):
    """
    Safely load an sdf file. If start fails, wait, then try again
    :param filename: The sdf file
    """
    try:
        p.loadSDF(filename)
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        p.loadSDF(filename)


def safe_start_urdf(filename: str):
    """
    Safely start a urdf file. If start fails, wait, then try again
    :param filename: The urdf file
    """
    try:
        pyrosim.Start_URDF(filename)
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        pyrosim.Start_URDF(filename)


def safe_start_neural_network(filename: str):
    """
    Safely start a neural network. If start fails, wait, then try again
    :param filename: The neural network (nndf) file
    """
    try:
        pyrosim.Start_NeuralNetwork(filename)
    except PermissionError:
        time.sleep(SECONDS_TO_WAIT)
        pyrosim.Start_NeuralNetwork(filename)
