# Folder Naming #
DATA_FOLDER_NAME = "data\\"
SOLUTIONS_FOLDER_NAME = "solutions\\"
FITNESS_FOLDER_NAME = "fitness\\"
OBJECTS_FOLDER_NAME = "objects\\"

WORLD_FILENAME = OBJECTS_FOLDER_NAME + "world.sdf"
ROBOT_FILENAME = OBJECTS_FOLDER_NAME + "body.urdf"


# Robot Controls #
# How much the joints connecting to the torso can rotate
UPPER_LEG_MOTOR_JOINT_RANGE = 0.2
# How much the joints connecting to the lower legs can rotate
LOWER_LEG_MOTOR_JOINT_RANGE = 0.5
# The smallest the CPG rate can get
MIN_CPG_RATE = 1
# The highest the CPG rate can be initialized to
MAX_INITIAL_CPG_RATE = 100
# The most the CPG can change in a given generation
MAX_CPG_CHANGE = 20

# Other Constants #
# The gravity of the simulation
gravity = {"x": 0, "y": 0, "z": -9.8}
# The vectors used to set rotation through the various axes
joint_axes = {"x": "1 0 0", "y": "0 1 0", "z": "0 0 1"}
