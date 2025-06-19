# capacity constriant:
import json
from problem import ACLProblem
from solution import ACLSolution

def total_capacity_constraint(problem: ACLProblem, solution: ACLSolution):
    #
    # x is a list of binary variables indicating whether a car is loaded on a truck
    # or not. The total capacity constraint ensures that the number of cars loaded
    # does not exceed the truck's capacity.
    transporter_capacity = problem.transporter.total_capacity

    # calculate the deck capacities from solution ie. ACLSolution
    total_capacities_used = 0
    print("Decks in solution.current_truck_load:", solution.current_truck_load)
    for decks in solution.current_truck_load:
        for vehicle_id, deck_state in decks.items():
            total_capacities_used += deck_state.capacity_used
    print("Total deck capacities used from solution:", total_capacities_used)
    print("Total transporter capacity from the problem:", transporter_capacity)
    # Check if the total capacities used is less than or equal to the transporter capacity
    return total_capacities_used  <= transporter_capacity 
        
def deck_capacity_constraint(problem: ACLProblem, solution: ACLSolution):
    #
    # x is a list of binary variables indicating whether a car is loaded on a truck
    # or not. The deck capacity constraint ensures that the number of cars loaded
    # on each deck does not exceed the deck's capacity.

    for decks in solution.current_truck_load:
        for vehicle_id, deck_state in decks.items():
            print(f"Deck state for vehicle {vehicle_id}: {deck_state}")
            if deck_state.capacity_remaining < 0:
                print(f"Deck  exceeds. deck constraint not stisfied.")
                return False
    return True

if __name__ == "__main__":

    # ...existing code...
    import json

    input_file = 'instance_example.json'
    output_file = 'solution_example.json'

    # Load the problem instance
    with open(input_file) as f:
        problem = ACLProblem(**json.load(f))

    # Create a solution instance
    solution = ACLSolution(problem)
    # Load the solution assignments
    with open(output_file) as f:
        solution_json = json.load(f)
    solution.from_json(solution_json)
    print("Solution loaded from file:", solution)
    total_capacity_check = total_capacity_constraint(problem, solution)
    print("Total capacity constraint satisfied:", total_capacity_check)

    deck_capacity_check = deck_capacity_constraint(problem, solution)
    print("Deck capacity constraint satisfied:", deck_capacity_check)
