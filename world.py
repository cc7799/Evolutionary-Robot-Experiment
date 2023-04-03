import pybullet as p

from constants import WORLD_FILENAME


class World:
    """
    Creates the world of a simulation
    """
    def __init__(self):
        p.loadSDF(WORLD_FILENAME)
        self.planeId = p.loadURDF("plane.urdf")
