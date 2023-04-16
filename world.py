import pybullet as p

from constants import WORLD_FILENAME
import safe_file_access as sfa

class World:
    """
    Creates the world of a simulation
    """
    def __init__(self):
        sfa.safe_load_sdf(WORLD_FILENAME)
        self.planeId = p.loadURDF("plane.urdf")
