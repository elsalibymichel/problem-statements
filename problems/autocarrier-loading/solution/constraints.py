# capacity constriant:
def objective_function(x):
    #
    # x is a list of binary variables indicating whether a car is loaded on a truck
    # or not. The objective is to maximize the number of cars loaded on the truck.
    #
    return sum(x)

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
    deck_capacities = {deck_id: problem.transporter.decks[deck_id].capacity for deck_id in problem.transporter.decks.keys()}
    print("Deck capacities from the problem:", deck_capacities)
    for deck_id, deck_state in solution.current_truck_load[-1].items():
        if len(deck_state.load) > deck_capacities[deck_id]:
            print(f"Deck {deck_id} exceeds its capacity with {len(deck_state.load)} vehicles loaded.")
            return False
    return True

# ...existing code...
import json

input_file = 'instance_example.json'
output_file = 'wrong_solution_example.json'

# Load the problem instance
with open(input_file) as f:
    problem = ACLProblem(**json.load(f))

# Create a solution instance
solution = ACLSolution(problem)
# Load the solution assignments
with open(output_file) as f:
    solution_json = json.load(f)
solution.from_json(solution_json)
total_capacity_check = total_capacity_constraint(problem, solution)
print("Total capacity constraint satisfied:", total_capacity_check)

deck_capacity_check = deck_capacity_constraint(problem, solution)
print("Deck capacity constraint satisfied:", deck_capacity_check)
