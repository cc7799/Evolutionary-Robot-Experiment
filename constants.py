# Folder Naming
DATA_FOLDER_NAME = "data\\"
WEIGHTS_FOLDER_NAME = DATA_FOLDER_NAME + "weights\\"
FITNESS_FOLDER_NAME = "fitness\\"
OBJECTS_FOLDER_NAME = "objects\\"

WORLD_FILENAME = OBJECTS_FOLDER_NAME + "world.sdf"
ROBOT_FILENAME = OBJECTS_FOLDER_NAME + "body.urdf"


# Robot controls
TORSO_MOTOR_JOINT_RANGE = 0.2
LOWER_LEG_MOTOR_JOINT_RANGE = 0.5
MIN_CPG_RATE = 1
MAX_CPG_RATE = 100
MAX_CPG_CHANGE = 20

# Other constants
gravity = {"x": 0, "y": 0, "z": -9.8}
joint_axes = {"x": "1 0 0", "y": "0 1 0", "z": "0 0 1"}
