"""
Modify these values to change the functioning of the simulation and evolution
"""
# Simulation and Evolution Controls #
NUM_FRAMES = 2000
RUN_SIM_IN_PARALLEL = True
SIMULATE = True  # Whether the simulation should run; Set to false for checking robot designs
MULTI_SIM = False  # Whether multiple leg configurations should be run; If false, you will be asked for number of legs
LEG_TESTS = [4, 6, 8, 10]  # The numbers of legs to be tested in multi_sim mode
RUN_WEIGHTS_FILE = True  # If false, you will need to provide a weights filename before simulation
SOLUTION_TO_RUN = 3  # The index of the solution that you want to run

# Output Controls #
PRINT_FITNESS_RESULTS = True
ROUND_FITNESS_OUTPUT = False
FITNESS_ROUND_LENGTH = 5

# Show Simulation Controls #
REQUIRE_KEYPRESS_TO_SHOW_SOLUTION = True
SHOW_SOLUTION_COUNTDOWN = False
COUNTDOWN_SECONDS = 5
