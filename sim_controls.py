"""
Modify these values to change the functioning of the simulation and evolution
"""

# CONTROLS #

# `num_frames`:    How many frames the simulator should run for
# `parallel_mode`: Whether multiple simulations should be run in parallel
# `simulate`:      Whether the simulation should run; Set to false for checking robot designs
SIMULATION_CONTROLS = {"num_frames": 2000,
                       "parallel_mode": True,
                       "simulate": True}

# `print_results`: Whether the fitness of each generation should be printed to the console
# `round_results`: Whether the fitness values should be rounded
# `round_length`:  How many decimal places the fitness values should be rounded to
# `run_index`:     The index of the current evolutionary run. Changes the name and solution index of the data outputs
FITNESS_OUTPUT_CONTROLS = {"print_results": True,
                           "round_results": False,
                           "round_length": 5,
                           "run_index": 0}

# OPERATION MODES #

# `active`: Whether the evolution should be run for just one type of robot
# `generations`: How many generations the robot should evolve for
# 'pop_size`: The population size of each generation
# `num_legs`: The number of legs of the robot; Must be an even number
# `cpg`: Whether the robot should have a CPG node
STANDARD_OPERATING_MODE = {"active": True,
                           "generations": 1,
                           "pop_size": 1,
                           "num_legs": 6,
                           "cpg": False}

# `active`:  Whether multiple leg configurations should be run
# `leg_nums`: The numbers of legs to be tested; Must be an even number
SIMULATE_MULTIPLE_ROBOTS_TYPES = {"active": False,
                                  "generations": 500,
                                  "pop_size": 10,
                                  "leg_nums": [4, 6, 8]}

# `active`:    Set to `True` to show a specific solution; Set to `False` to evolve new ones
# `sol_index`: The index of the solution (the number after 'weights' in the filename)
# `num_legs`:  The number of legs of the solution you wish to view
SHOW_SPECIFIC_SOLUTION = {"active": False,
                          "sol_index": 9,
                          "num_legs": 4,
                          "cpg": True}
