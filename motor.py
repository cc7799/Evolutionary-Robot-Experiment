import pybullet as p

import pyrosim.pyrosim as pyrosim


class Motor:
    """
    Controls a single motor
    """
    def __init__(self, motor_name: str):
        self.motor_name = motor_name

    def set_value(self, robot_id: int, desired_angle: float):
        """
        Sets the angle of the motor
        :param robot_id: The id of the robot that the motor is part of
        :param desired_angle: The angle that the motor should be set at
        """
        pyrosim.Set_Motor_For_Joint(bodyIndex=robot_id,
                                    jointName=self.motor_name,
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=desired_angle,
                                    maxForce=40)
