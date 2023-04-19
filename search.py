"""
Searches through a set of solutions to find the most fit
"""
import sys
from typing import Dict, List

from hillclimber import Hillclimber
from solution import Solution
import sim_controls as sc


def verify_controls():
    """
    Verifies that all the simulation and evolution controls have the correct type.
    If any are incorrect, prints and error message and exits.
    """
    def verify_active_modes():
        """
        Verify that exactly one mode is active.
        """
        mode_status = [sc.STANDARD_OPERATING_MODE["active"],
                       sc.SIMULATE_MULTIPLE_ROBOTS_TYPES["active"],
                       sc.SHOW_SPECIFIC_SOLUTION["active"]]

        valid_input: bool = False
        for mode in mode_status:
            if mode is True:
                if not valid_input:
                    valid_input = True
                else:
                    print("You have multiple modes set to active. Fix this before continuing.")
                    sys.exit(-1)

        if not valid_input:
            print("You have no modes set to active. Fix this before continuing.")
            sys.exit(-1)

    def get_type_name_with_article(desired_type: type) -> str:
        """
        Gets the name of the type and prepends `an ` or `a ` depending on if it starts with a vowel or not.
        :param desired_type: The type object to get the name of
        :return: The name of the type object with `an ` of `a ` prepended to it.
        """
        if desired_type.__name__[0] in "aeiou":
            type_name_with_article = "an " + desired_type.__name__
        else:
            type_name_with_article = "a " + desired_type.__name__

        return type_name_with_article

    def verify_control_group_types(control_group: Dict, control_names: List[str], desired_types: List[type]):
        """
        Verifies that in a given control group,
            each name in `control_names` has the corresponding type in `desired_types`.
        :param control_group: The dictionary that contains the group of controls to verify.
        :param control_names: A list of names in the control group to verify.
        :param desired_types: A list of the types that each name should have.
            If the type is a container object, use a tuple in the form (<container_type>, <item_type>)
        """
        for control_name, desired_type in zip(control_names, desired_types):
            control = control_group[control_name]

            if type(desired_type) == tuple:
                container_type = desired_type[0]
                item_type = desired_type[1]

                if type(control) != container_type:
                    print((control_name + " must be " + get_type_name_with_article(container_type) + "."))
                    sys.exit(-1)

                for item in control:
                    if type(item) != item_type:
                        print("Each item in " + control_name + " must be "
                              + get_type_name_with_article(item_type) + ".")
                        sys.exit(-1)

            elif type(control) != desired_type:
                print((control_name + " must be " + get_type_name_with_article(desired_type) + "."))
                sys.exit(-1)

    verify_active_modes()

    verify_control_group_types(control_group=sc.SIMULATION_CONTROLS,
                               control_names=["num_frames", "parallel_mode", "simulate"],
                               desired_types=[int, bool, bool])

    verify_control_group_types(control_group=sc.FITNESS_OUTPUT_CONTROLS,
                               control_names=["print_results", "round_results", "round_length"],
                               desired_types=[bool, bool, int])

    verify_control_group_types(control_group=sc.STANDARD_OPERATING_MODE,
                               control_names=["generations", "pop_size", "num_legs"],
                               desired_types=[int, int, int])

    verify_control_group_types(control_group=sc.SIMULATE_MULTIPLE_ROBOTS_TYPES,
                               control_names=["active", "generations", "pop_size", "leg_nums"],
                               desired_types=[bool, int, int, (list, int)])

    verify_control_group_types(sc.SHOW_SPECIFIC_SOLUTION,
                               control_names=["active", "sol_index", "num_legs"],
                               desired_types=[bool, int, int])


def run_sim(simulation: Hillclimber, show_best: bool):
    simulation.evolve()

    if show_best:
        print("\n*** Press any key to show best solution ***")
        input()

        simulation.show_best()


if __name__ == "__main__":
    verify_controls()

    parallel_mode = sc.SIMULATION_CONTROLS["parallel_mode"]

    if sc.STANDARD_OPERATING_MODE["active"]:
        controls = sc.STANDARD_OPERATING_MODE

        num_generations = controls["generations"]
        pop_size = controls["pop_size"]
        num_legs = controls["num_legs"]

        sim = Hillclimber(num_generations, pop_size, num_legs, parallel_mode)
        run_sim(sim, show_best=True)

    elif sc.SHOW_SPECIFIC_SOLUTION["active"]:
        controls = sc.SHOW_SPECIFIC_SOLUTION

        num_legs = controls["num_legs"]
        sol_index = controls["sol_index"]

        sol = Solution(solution_id=0, num_legs=num_legs)
        sol.show_solution(sol_index)

    elif sc.SIMULATE_MULTIPLE_ROBOTS_TYPES["active"]:
        controls = sc.SIMULATE_MULTIPLE_ROBOTS_TYPES

        num_generations = controls["generations"]
        pop_size = controls["pop_size"]
        leg_nums = controls["leg_nums"]

        for num_legs in leg_nums:
            sim = Hillclimber(num_generations, pop_size, num_legs, parallel_mode)
            run_sim(sim, show_best=False)
