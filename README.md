# Evolving Quadruped Robot
A simulation of a simple quadruped robot that uses evolutionary algorithms to learn how to walk. 

This was created as a project for the Evolutionary Robotics (CS 3060) course I took as a student at UVM.

## Table of Contents
* [Description](#description)
* [Installation & Setup](#installation--setup)
* [Operation](#operation)
* [Changes Made to Pyrosim](#changes-made-to-pyrosim)

## Description
This program creates a simple four-legged robot that is simulated for a given number of generations to maximize the 
distance walked in the given number of frames. The number of generations, population size, number of frames, and other 
parts of the evolutionary process can be changed.

After running, the best solution is shown and human-readable and csv versions of the evolution data are saved into the 
`data` folder.

A sample of the robot's evolution after 50 generations with a population size of 10 can be found 
[here](https://youtu.be/kV2cqIk2MxE).

### Software Used
This program is written in python and uses the `pybullet` and `pyrosim` python libraries.

## Installation & Setup
### Prerequisites 
This project uses the `pybullet` library for running the physics simulations. This library can be installed using 
`pip3 install pybullet`. A modified version of the `pyrosim` library, used to simplify interactions with `pybullet` was 
also used. The unmodified version can be found [here](https://github.com/jbongard/pyrosim) and the changes are detailed
below.

`Pybullet` requires the Visual C++ compiler to be installed on the machine. This compiler can be installed through 
installing Visual Studio, but after installation, Visual Studio is not required to run the program.

Note: This project has only been tested on Windows 10. It should work on other Windows versions as well as mac and 
linux, but it has not been tested on those systems.

### Setup
Before running the program, the values in `system_info.py` must be set to the correct values for your system.

## Operation
After setup is complete, run the file `search.py` to begin evolution of the robot.

The file `sim_controls.py` has been provided to allow for changes in the operation of the simulation and evolution of 
the robot.

## Changes Made to Pyrosim
Some changes were made to the base pyrosim code. These changes are detailed below.

1. <u>Added ability to update neuron values</u>
   - Added function `Update()` to pyrosim/neuralNetwork.py
   - Added the following functions to pyrosim/neuron.py
     - `Update_Sensor_Neuron()`
     - `Update_Hidden_Or_Motor_Neuron(neurons, synapses)`
     - `Allow_Presynaptic_Neuron_To_Influence_Me()`
2. <u>Added ability to get the value of a neuron</u>
   - Added function `Get_Value_Of()` to pyrosim/neuralNetwork.py
3. <u>Added ability to change joint axis of rotation</u>
   - `pyrosim/joint.py/Save()` changed to use user specified jointAxis
   - `pyrosim/pyrosim/Joint()` changed to pass user-specified value to joint.Save()
