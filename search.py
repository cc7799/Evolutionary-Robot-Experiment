"""
Searches through a set of solutions to find the most fit
"""
import time

from hillclimber import Hillclimber
import sim_controls as sc

MULTI_SIM = False


def get_sim_details(get_legs: bool):
    try:
        generations = int(input("Generations: "))
        population_size = int(input("Population Size: "))

        if get_legs:
            legs = int(input("Number of Legs: "))
            assert (legs % 2 == 0)
            return generations, population_size, legs
        else:
            return generations, population_size
    except ValueError:
        print("The value must be an integer, please try again.")
        exit()


def run_sim(generations: int, population: int, num_legs: int, parallel: bool, show_best: bool):
    sim = Hillclimber(generations, population, num_legs, parallel)

    sim.evolve()

    if show_best:
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
    if MULTI_SIM:
        num_generations, pop_size = get_sim_details(get_legs=False)

        leg_tests = [4, 6, 8, 10]

        for num_legs in leg_tests:
            run_sim(num_generations, pop_size, num_legs=num_legs, parallel=sc.RUN_SIM_IN_PARALLEL, show_best=False)
    else:
        num_generations, pop_size, num_legs = get_sim_details(get_legs=True)
        run_sim(num_generations, pop_size, num_legs=num_legs, parallel=sc.RUN_SIM_IN_PARALLEL, show_best=True)
