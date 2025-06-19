from problem import ACLProblem
from solution import ACLSolution
import json
from pathlib import Path
import local_search
import click
import roar_net_api.algorithms as alg

import sys

@click.group()
def cli():
    """Command line interface for the ACL problem."""
    pass

@cli.command()
@click.argument('algorithm', type=click.Choice(['first_improvement', 'best_improvement'], case_sensitive=False))
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--initial_solution', type=click.Path(), default=None, help='Path to the output file for the initial solution.')
@click.option('--output', type=click.Path(), default=None, help='Path to the output file for the final solution.')
def local_search(algorithm: str, input_file: str, initial_solution: Path, output: Path):
    """
    Run local search algorithms on the ACL problem.
    ALGORITHM: The local search algorithm to use (first_improvement or best_improvement).
    INPUT_FILE: Path to the input JSON file containing the ACL problem data.
    --initial_solution INITIAL_SOLUTION: Path to the initial solution JSON file (optional).
    --output OUTPUT_FILE: Path to the output JSON file for the final solution (optional).
    """
    problem = ACLProblem(**json.load(open(input_file)))

    if initial_solution is not None:
        # Create a solution instance out of the json file
        initial_solution = ACLSolution(problem, json.load(open(initial_solution)))    
    else:
        # Generate a random initial solution
        initial_solution = problem.random_solution()
    
    click.secho(f"Initial solution: [{initial_solution.objective_value()}]\n{initial_solution}")

    # Run the local search algorithm selected
    if algorithm == 'best_improvement':
        new_solution = alg.best_improvement(problem, initial_solution)
    elif algorithm == 'first_improvement':
        new_solution = alg.first_improvement(problem, initial_solution)

    if output is not None:
        # Save the final solution to the output file
        with open(output, 'w') as f:
            json.dump(new_solution.to_json(), f, indent=4)
    else:
        click.echo(f"Final solution: [{new_solution.objective_value()}]\n{new_solution}")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), default=None, help='Path to the output file for the final solution.')
def constructive_search(input_file: str, output: Path):
    """
    Run constructive search algorithms on the ACL problem.
    INPUT_FILE: Path to the input JSON file containing the ACL problem data.
    --output OUTPUT_FILE: Path to the output JSON file for the final solution (optional).
    """
    problem = ACLProblem(**json.load(open(input_file)))

    new_solution = alg.greedy_construction(problem)

    if output is not None:
        # Save the final solution to the output file
        with open(output, 'w') as f:
            json.dump(new_solution.to_json(), f, indent=4)
    else:
        click.echo(f"Final solution: [{new_solution.objective_value()}]\n{new_solution}")

# def backup():
#     BASE_DIR = Path(__file__).resolve().parent
#     input_DATA_PATH = BASE_DIR.parent /"data"/"11CT_401696_s5_v13.json"  
#     output_DATA_PATH = BASE_DIR.parent /"solution"/"solution_example.json"  

#     input_file = input_DATA_PATH
#     output_file = output_DATA_PATH
    
#     main(input_file, output_file)

# For a command line interface, we use the click library to handle arguments and options.
if __name__ == "__main__":
    cli()