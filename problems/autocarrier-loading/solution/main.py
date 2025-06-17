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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        main(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("Problem and solution loaded successfully.")