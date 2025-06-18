from problem import ACLProblem
from solution import ACLSolution
import json

import sys

def main(input_file: str, output_file: str):
    """Main function to load the problem and create a solution."""
    problem = ACLProblem(**json.load(open(input_file)))
    
    # Create a solution instance
    solution = ACLSolution(problem)
    solution.from_json(json.load(open(output_file)))
    
    # Print the problem and solution for debugging
    print("Problem:", problem)
    print("Solution:", solution)
    print("Sum of moves to unload and load:", solution.sum_moves_to_unload_and_load())
    print("Sum of moves to unload only:", solution.sum_moves_to_unload())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_file, output_file)
    print("Problem and solution loaded successfully.")