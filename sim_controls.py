"""
Modify these values to change the functioning of the simulation and evolution
"""
# Simulation and Evolution Controls #
NUM_FRAMES = 2000
RUN_SIM_IN_PARALLEL = True
SIMULATE = True  # Whether the simulation should run; Set to false for checking robot designs
MULTI_SIM = True  # Whether multiple leg configurations should be run; If false, you will be asked for number of legs
LEG_TESTS = [4, 6]  # The numbers of legs to be tested in multi_sim mode

# Output Controls #
PRINT_FITNESS_RESULTS = True
ROUND_FITNESS_OUTPUT = False
FITNESS_ROUND_LENGTH = 5

# Show Simulation Controls #

# Change the first value to determine whether to show a specific solution,
#   Change the other values to desired solution
SHOW_SPECIFIC_SOLUTION = {"show_solution": True,
                          "sol_index": 0,
                          "num_legs": 4}

REQUIRE_KEYPRESS_TO_SHOW_SOLUTION = True
SHOW_SOLUTION_COUNTDOWN = False
COUNTDOWN_SECONDS = 5
