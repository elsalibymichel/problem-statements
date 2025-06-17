from problem import ACLProblem
from solution import ACLSolution
import json

import sys

def main(input_file: str):
    # Load the problem from the input file
    problem = ACLProblem(**json.load(open(input_file)))
    
    # Create a solution instance
    solution = ACLSolution(problem)
    
    # Print the problem and solution for debugging
    print("Problem:", problem)
    print("Solution:", solution)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        main(input_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("Problem and solution loaded successfully.")