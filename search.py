"""
Searches through a set of solutions to find the most fit
"""
import time

from hillclimber import Hillclimber
import sim_controls as sc


def get_sim_details():
    try:
        generations = int(input("Generations: "))
        population_size = int(input("Population Size: "))
    except ValueError:
        print("The value must be an integer, please try again.")
        exit()

    return generations, population_size


def run_sim(generations: int, population: int, num_legs: int, parallel: bool):
    sim = Hillclimber(generations, population, num_legs, parallel)

    sim.evolve()

    if sc.REQUIRE_KEYPRESS_TO_SHOW_SOLUTION:
        print("\n*** Press any key to show best solution ***")
        input()
    if sc.SHOW_SOLUTION_COUNTDOWN:
        print("Simulation beginning in")
        for i in range(sc.COUNTDOWN_SECONDS, 0, -1):
            print(i)
            time.sleep(1)

    sim.show_best()


if __name__ == "__main__":
    num_generations, pop_size = get_sim_details()
    run_sim(num_generations, pop_size, num_legs=50, parallel=sc.RUN_SIM_IN_PARALLEL)
