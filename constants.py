# Folder Naming
DATA_FOLDER_NAME = "data\\"
WEIGHTS_FOLDER_NAME = DATA_FOLDER_NAME + "weights\\"
FITNESS_FOLDER_NAME = "fitness\\"
OBJECTS_FOLDER_NAME = "objects\\"

WORLD_FILENAME = OBJECTS_FOLDER_NAME + "world.sdf"
ROBOT_FILENAME = OBJECTS_FOLDER_NAME + "body.urdf"
FITNESS_DATA_FILENAME = DATA_FOLDER_NAME + "fitness.txt"


# Robot controls
NUM_SENSOR_NEURONS = 9
NUM_MOTOR_NEURONS = 8
TORSO_MOTOR_JOINT_RANGE = 0.2
LOWER_LEG_MOTOR_JOINT_RANGE = 0.5

# Other constants
gravity = {"x": 0, "y": 0, "z": -9.8}
joint_axes = {"x": "1 0 0", "y": "0 1 0", "z": "0 0 1"}
