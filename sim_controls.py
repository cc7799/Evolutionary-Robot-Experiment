"""
Modify these values to change the functioning of the simulation and evolution
"""

# `num_frames`:    How many frames the simulator should run for
# `parallel_mode`: Whether multiple simulations should be run in parallel
# `simulate`:      Whether the simulation should run; Set to false for checking robot designs
SIMULATION_CONTROLS = {"num_frames": 2000,
                       "parallel_mode": True,
                       "simulate": True}

# `print_results`: Whether the fitness of each generation should be printed to the console
# `round_results`: Whether the fitness values should be rounded
# `round_length`:  How many decimal places the fitness values should be rounded to
FITNESS_OUTPUT_CONTROLS = {"print_results": True,
                           "round_results": False,
                           "round_length": 5}

# `active`:  Whether multiple leg configurations should be run; If false, you will be asked for number of legs
# `leg_nums`:The numbers of legs to be tested
SIMULATE_MULTIPLE_ROBOTS_TYPES = {"active": True,
                                  "leg_nums": [4, 6]}

# `active`:    Set to `True` to show a specific solution; Set to `False` to evolve new ones
# `sol_index`: The index of the solution (the number after 'weights' in the filename)
# `num_legs`:  The number of legs of the solution you wish to view
SHOW_SPECIFIC_SOLUTION = {"active": True,
                          "sol_index": 4,
                          "num_legs": 6}

