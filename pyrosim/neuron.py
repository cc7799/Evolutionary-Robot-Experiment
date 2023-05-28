import math

import pybullet

import pyrosim.pyrosim as pyrosim

import pyrosim.constants as c

class NEURON: 

    def __init__(self,line):

        self.Determine_Name(line)

        self.Determine_Type(line)

        self.Search_For_Link_Name(line)

        self.Search_For_Joint_Name(line)

        # The time steps per pulse if this neuron is a CPG; None if it is not
        self.Determine_Pulse_Rate(line)

        self.Set_Value(0.0)

    def Add_To_Value( self, value ):

        self.Set_Value( self.Get_Value() + value )

    def Get_Joint_Name(self):

        return self.jointName

    def Get_Link_Name(self):

        return self.linkName

    def Get_Name(self):

        return self.name

    def Get_Value(self):

        return self.value

    def Is_Sensor_Neuron(self):

        return self.type == c.SENSOR_NEURON

    def Is_Hidden_Neuron(self):

        return self.type == c.HIDDEN_NEURON

    def Is_CPG_Neuron(self):

        return self.type == c.CPG_NEURON

    def Is_Motor_Neuron(self):

        return self.type == c.MOTOR_NEURON

    def Print(self):

        # self.Print_Name()

        # self.Print_Type()

        self.Print_Value()

        # print("")

    def Set_Value(self,value):

        self.value = value

    def Update_Sensor_Neuron(self):
        self.Set_Value(pyrosim.Get_Touch_Sensor_Value_For_Link(self.Get_Link_Name()))

    def Update_CPG_Neuron(self, timestep: int):
        """
        Update a Central Pattern Generator neuron
        :param timestep: The current timestep of the simulation. Used to determine if the CPG should pulse
        """
        # This function should never be called on a non-cpg neuron. This will prevent it in case any mistakes are made
        assert (self.Pulse_Rate is not None)

        if timestep % self.Pulse_Rate == 0:
            self.Set_Value(1)
        else:
            self.Set_Value(0)

    def Update_Hidden_Or_Motor_Neuron(self, neurons, synapses):
        self.Set_Value(0)
        for synapse_name in synapses.keys():
            pre_synaptic_neuron = synapse_name[0]
            post_synaptic_neuron = synapse_name[1]

            synapse_weight = synapses[synapse_name].Get_Weight()
            pre_synaptic_value = neurons[pre_synaptic_neuron].Get_Value()

            # If the neuron currently being updated is the post-synaptic neuron
            if self.Get_Name() == post_synaptic_neuron:
                self.Allow_Presynaptic_Neuron_To_Influence_Me(synapse_weight, pre_synaptic_value)

        self.Threshold()

    def Allow_Presynaptic_Neuron_To_Influence_Me(self, synapse_weight: float, pre_synaptic_value: float):
        weighted_value = pre_synaptic_value * synapse_weight
        self.Add_To_Value(weighted_value)


# -------------------------- Private methods -------------------------

    def Determine_Name(self,line):

        if "name" in line:

            splitLine = line.split('"')

            self.name = splitLine[1]

    def Determine_Type(self,line):

        if "sensor" in line:

            self.type = c.SENSOR_NEURON

        elif "motor" in line:

            self.type = c.MOTOR_NEURON

        elif "cpg" in line:

            self.type = c.CPG_NEURON

        else:

            self.type = c.HIDDEN_NEURON

    def Determine_Pulse_Rate(self, line):

        if "cpg" in line:
            rate_index = line.index("rate = \"") + 8
            end_of_rate_index = line.index("/") - 2

            rate = int(line[rate_index: end_of_rate_index])

            self.Pulse_Rate = rate
        else:
            self.Pulse_Rate = None

    def Print_Name(self):

       print(self.name)

    def Print_Type(self):

       print(self.type)

    def Print_Value(self):

       print(self.value , " " , end="" )

    def Search_For_Joint_Name(self,line):

        if "jointName" in line:

            splitLine = line.split('"')

            self.jointName = splitLine[5]

    def Search_For_Link_Name(self,line):

        if "linkName" in line:

            splitLine = line.split('"')

            self.linkName = splitLine[5]

    def Threshold(self):

        self.value = math.tanh(self.value)
