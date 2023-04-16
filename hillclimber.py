import copy
import os
from typing import Dict

from solution import Solution
import constants as c
import sim_controls as sc
import system_info as sys


def delete_leftover_files():
    """
    Deletes any fitness or tmp_fitness files that may have been left behind by previous run
    (leftover non-data files will only exist if previous run glitched)
    """

    if sys.WINDOWS:
        system_call = "del "
    else:
        system_call = "rm "

    system_calls = [system_call + "\"" + sys.PROJECT_FILEPATH + c.FITNESS_FOLDER_NAME + "fitness*.txt\"",
                    system_call + "\"" + sys.PROJECT_FILEPATH + c.FITNESS_FOLDER_NAME + "tmp*.txt\"",
                    system_call + "\"" + sys.PROJECT_FILEPATH + c.OBJECTS_FOLDER_NAME + "brain*.nndf\""]

    for system_call in system_calls:
        os.system(system_call)


class Hillclimber:
    """
    Simulates and evolves a set of quadruped robots
    """
    def __init__(self, num_generations: int, population_size: int, num_legs: int, parallel: bool):
        delete_leftover_files()

        self.num_generations = num_generations
        self.population_size = population_size
        self.parallel = parallel
        self.num_legs = num_legs

        self.next_available_id = 0
        self.generation = 0

        self.parents:  Dict[int, Solution] = {}
        self.children: Dict[int: Solution] = {}

        # Create initial population
        for i in range(self.population_size):
            self.parents[i] = Solution(self.get_next_available_id(), self.num_legs)

    def evolve(self):
        """
        Evolves the set of robots
        """
        # Evaluate each first generation robot
        self.evaluate(self.parents)

        # Evolve the robots
        for current_generation in range(self.num_generations):
            self.generation = current_generation
            self.evolve_for_one_generation()

    def evolve_for_one_generation(self):
        """
        Performs a single generation evolution
        """
        self.spawn()
        self.mutate()
        self.evaluate(self.children)

        self.output_generation_fitness()

        self.select()

        self.write_generation_fitness_to_csv()

    def spawn(self):
        """
        Creates a child solution for every parent solution
        """
        for index, parent in self.parents.items():
            self.children[index] = copy.deepcopy(parent)
            self.children[index].set_id(self.get_next_available_id())

    def mutate(self):
        """
        Mutate every child solution
        """
        for child in self.children.values():
            child.mutate()

    def evaluate(self, solutions: Dict[int, Solution]):
        """
        Runs a set of solutions to evaluate their fitness
        :param solutions: The solutions to be evaluated
        """
        if self.parallel:
            for solution in solutions.values():
                solution.start_simulation()

            for solution in solutions.values():
                solution.wait_for_sim_to_end()
        else:
            # Waits for one simulation to finish before starting the next one
            for solution in solutions.values():
                solution.start_simulation(parallel=False)
                solution.wait_for_sim_to_end()

    def select(self):
        """
        For each parent-child pair, determine which is the fittest and store that as the parent
        """
        for i in range(0, len(self.parents)):
            if self.children[i].fitness > self.parents[i].fitness:
                self.parents[i] = self.children[i]
            self.parents[i].save_weights()

    def show_best(self):
        """
        Display the best solution
        """
        max_fitness = self.parents[0].fitness
        max_fitness_index = 0
        for i in range(1, len(self.parents)):
            if self.parents[i].fitness > max_fitness:
                max_fitness = self.parents[i].fitness
                max_fitness_index = i

        self.parents[max_fitness_index].start_simulation(show_gui=True)

    def get_next_available_id(self) -> int:
        """
        Calculates the next consecutive solution id number so that no two solutions will have the sam id
        :return: The next available id
        """
        output = self.next_available_id
        self.next_available_id += 1
        return output

    def get_generation_fitness(self, round_vals: bool = False) -> str:
        """
        Creates a string representation of the current generation's fitness
        :param round_vals: Whether to round the decimal places in the fitness values
        :return: A string representation of the current generation's fitness
        """
        output = "*** Generation " + str(self.generation + 1) + "/" + str(self.num_generations) \
                 + " (" + str(self.num_legs) + " legs) ***"
        for i in range(0, len(self.parents)):
            output += "\nSolution " + str(i) + "\n"
            if round_vals:
                output += ("Parent: " + str(round(self.parents[i].fitness, sc.FITNESS_ROUND_LENGTH))
                           + ", Child: " + str(round(self.children[i].fitness, sc.FITNESS_ROUND_LENGTH)))
            else:
                output += ("Parent: " + str(self.parents[i].fitness)
                           + ", Child: " + str(self.children[i].fitness))

        return output

    def print_generation_fitness(self):
        """
        Prints the current generation's fitness
        """
        output = "\n\n******************************\n"
        output += self.get_generation_fitness(round_vals=sc.ROUND_FITNESS_OUTPUT)
        output += "\n******************************\n\n"

        print(output)

    def write_generation_fitness_to_file(self):
        """
        Writes the current generation's fitness in a human-readable format to a file
        """
        output = "******************************\n"
        output += self.get_generation_fitness() + "\n"

        if self.generation == 0:
            with open(c.FITNESS_DATA_FILENAME, "w") as fileout:
                fileout.write(output)
        else:
            with open(c.FITNESS_DATA_FILENAME, "a") as fileout:
                fileout.write(output)

    def write_generation_fitness_to_csv(self):
        """
        Writes the current generation's fitness to a csv file
        """
        filename = c.DATA_FOLDER_NAME + "fitness(" + str(self.num_legs) + "_legs).csv"
        if self.generation == 0:
            output = "generation,highest_fitness,solution,pop_size\n"
            with open(filename, "w") as fileout:
                fileout.write(output)

        max_fitness = self.parents[0].fitness
        max_fitness_index = 0
        for i in range(1, len(self.parents)):
            if self.parents[i].fitness > max_fitness:
                max_fitness = self.parents[i].fitness
                max_fitness_index = i

        output = str(self.generation + 1) + "," + str(self.parents[max_fitness_index].fitness) + "," \
            + str(max_fitness_index) + "," + str(self.population_size) + "\n"

        with open(filename, "a") as fileout:
            fileout.write(output)

    def output_generation_fitness(self):
        """
        Outputs the current generation's fitness
        """
        if sc.PRINT_FITNESS_RESULTS:
            self.print_generation_fitness()

        self.write_generation_fitness_to_file()
