# Evolving Quadruped Robot
A simulation of a simple quadruped robot that uses evolutionary algorithms to learn how to walk. 

This was created as a project for the Evolutionary Robotics (CS 3060) course I took as a student at UVM.

## Table of Contents
* [Description](#description)
* [Installation & Setup](#installation--setup)
* [Operation](#operation)
* [Changes Made to Pyrosim](#changes-made-to-pyrosim)

## Description
This program allows for the simulation and evolution of robots with varying numbers of legs and with and without a
    Central Pattern Generator (CPG) node. 
The robots are evolved to maximize the distance walked in a given number of frames.
The number of generations, population size, number of frames, and other parts of the evolutionary process can be changed.

After running, the solutions are saved into the `solutions` folder and the fitness values are saved in text and
    csv forms in the `data` folder. The `fitness` and `objects` folders are used to store values during evolution. 

<add video

### Software Used
This program is written in python and uses the `pybullet` and `pyrosim` python libraries.

## Installation & Setup
### Prerequisites 
This project uses the `pybullet` library for running the physics simulations.
This library can be installed using `pip3 install pybullet`.

`Pybullet` requires the Visual C++ compiler to be installed on the machine. 
This compiler can be installed through installing Microsoft Visual Studio, but after installation, 
    Visual Studio is not required to run the program.

A modified version of the `pyrosim` library, used to simplify interactions with `pybullet`, was also used.
This does not need to be installed. 
The unmodified version can be found [here](https://github.com/jbongard/pyrosim) and the changes are detailed below.

<i>Note:</i> This project has only been tested on Windows 10. 
It should work on other Windows versions as well as mac and linux, but it has not been tested on those systems.

### Setup
Before running the program, the values in `system_info.py` must be set to the correct values for your system.

### Experiment Parameters
Many of the parameters of the evolution and simulation can be changed through the `sim_controls.py` file. 
Three evolution modes are provided.
Each parameter will be checked at runtime to ensure proper typing and that exactly one mode is active.

1. Standard Mode: Simulates one type of robot for a given number of generations
2. Multiple Robots Mode: Simulates multiple specified types of robots for a given number of generations.
      Will simulate all robot types with and without a CPG
3. Show Solution Mode: Shows a specific solution given its parameters, provided that the solution files are present

What each specific parameter does is detailed in the file.

## Operation
After setup is complete, run the file `search.py` to begin evolution of the robot.

## Changes Made to Pyrosim
Some changes were made to the base pyrosim code. These changes are detailed below.

1. <b>Added ability to update neuron values</b>
   - Added function `Update()` to `pyrosim/neuralNetwork.py`
   - Added the following functions to `pyrosim/neuron.py`
     - `Update_Sensor_Neuron()`
     - `Update_Hidden_Or_Motor_Neuron(neurons, synapses)`
     - `Allow_Presynaptic_Neuron_To_Influence_Me()`
2. <b>Added ability to get the value of a neuron</b>
   - Added function `Get_Value_Of()` to `pyrosim/neuralNetwork.py`
3. <b>Added ability to change joint axis of rotation</b>
   - `pyrosim/joint.py/Save()` changed to use user specified jointAxis
   - `pyrosim/pyrosim/Joint()` changed to pass user-specified value to joint.Save()
4. <b>Added ability to add hidden neurons to the neural network</b>
   - Added function `Send_Hidden_Neuron(name)` to `pyrosim/pyrosim.py` that adds a hidden neuron to the brain file
5. <b>Added CPG neurons as a special type of neuron</b>
   1. <u>Creating CPG neurons</u>
      - Created function `Send_CPG_Neuron()` in `pyrosim/pyrosim.py`
        - Saves the CPG neuron's name and pulse rate to a neuron entry in the .nndf file
   2. <u>Detecting and storing if a neuron is a CPG neuron</u>
      - Added case for CPG neurons to `determine_type()` in `pyrosim/neuron.py`
      - Added constant `CPG_NEURON` to `pyrosim/constants.py`
      - Added function `Is_CPG_Neuron()` to `pyrosim/neuron.py`
   3. <u>Getting and storing the pulse rate of the cpg</u>
      - Added field `self.Pulse_Rate` to `pyrosim/neuron.py`
        - Calculated by new function `self.Determine_Pulse_Rate()` that extracts the pulse rate from the .nndf file
   4. <u>Updating CPG neurons</u>
      - Added function `Update_CPG_Neuron()` to `pyrosim/neuron.py`
        - Sets the value to one every time the current time step is a multiple of the given rate
      