from problem import ACLProblem
from solution import ACLSolution
import json
from pathlib import Path
import local_search
import roar_net_api.algorithms as alg

import sys

def main(input_file: str, output_file: str = None):
    """Main function to load the problem and create a solution."""
    problem = ACLProblem(**json.load(open(input_file)))
    
    # Create a solution instance out of the json file
    if output_file is not None:
        initial_solution = ACLSolution(problem, json.load(open(output_file)))
    else:
        initial_solution = problem.random_solution()

    print("Initial solution:", initial_solution, initial_solution.objective_value())
    new_solution = alg.sa(problem, initial_solution, 30, 50.0)
    print("Final solution:", new_solution, new_solution.objective_value())
    
    # Print the problem and solution for debugging
    #print("Problem:", problem)
    #print("Solution:", solution)
    #print("Sum of moves to unload and load:", solution.sum_moves_to_unload_and_load())
    #print("Sum of moves to unload only:", solution.sum_moves_to_unload())

def backup():
    BASE_DIR = Path(__file__).resolve().parent
    input_DATA_PATH = BASE_DIR.parent /"data"/"11CT_401696_s5_v13.json"  
    output_DATA_PATH = BASE_DIR.parent /"solution"/"solution_example.json"  

    input_file = input_DATA_PATH
    output_file = output_DATA_PATH
    
    main(input_file, output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        print("Run default calling")
#        backup()
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    main(input_file)