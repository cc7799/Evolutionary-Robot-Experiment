"""
Searches through a set of solutions to find the most fit
"""
from hillclimber import Hillclimber
from solution import Solution
import sim_controls as sc


def get_sim_details(get_legs: bool):
    try:
        output = []

        generations = int(input("Generations: "))
        output.append(generations)

        population_size = int(input("Population Size: "))
        output.append(population_size)

        if get_legs:
            legs = int(input("Number of Legs: "))
            assert (legs % 2 == 0)
            output.append(legs)

        return output

    except ValueError:
        print("The value must be an integer, please try again.")
        exit()


def run_sim(simulation: Hillclimber, show_best: bool):
    simulation.evolve()

    if show_best:
        print("\n*** Press any key to show best solution ***")
        input()

        simulation.show_best()


if __name__ == "__main__":
    parallel_mode = sc.SIMULATION_CONTROLS["parallel_mode"]

    if sc.SHOW_SPECIFIC_SOLUTION["active"]:
        sol = Solution(solution_id=0, num_legs=sc.SHOW_SPECIFIC_SOLUTION["num_legs"])
        sol.show_solution(sc.SHOW_SPECIFIC_SOLUTION["sol_index"])

    elif sc.SIMULATE_MULTIPLE_ROBOTS_TYPES["active"]:
        num_generations, pop_size = get_sim_details(get_legs=False)

        for num_legs in sc.SIMULATE_MULTIPLE_ROBOTS_TYPES["leg_nums"]:
            sim = Hillclimber(num_generations, pop_size, num_legs, parallel_mode)
            run_sim(sim, show_best=False)
    else:
        num_generations, pop_size, num_legs = get_sim_details(get_legs=True)

        sim = Hillclimber(num_generations, pop_size, num_legs, parallel_mode)
        run_sim(sim, show_best=True)
