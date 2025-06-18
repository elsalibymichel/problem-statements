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
    print("Total capacity constraint check:")
    print(f"Transporter total capacity: {problem.transporter.total_capacity}")
    print(f"Deck capacities: {[deck.capacity for deck in problem.transporter.decks.values()]}")
    
    return problem.transporter.total_capacity <= ACLSolution.transporter.capacity



# input_file = 'instance_example.json'
# output_file = 'solution_example.json'

# problem = ACLProblem(**json.load(open(output_file)))
    
# # Create a solution instance
# solution = ACLSolution(problem)

# print(solution)
# capacity_state = total_capacity_constraint(current_state)

# driver function to check the constraints
# total_capacity_constraint = total_capacity_constraint(ACLSolution.instance.transporter.current_truck_load)


# ...existing code...
import json

input_file = 'instance_example.json'
output_file = 'solution_example.json'

# Load the problem instance
with open(input_file) as f:
    problem = ACLProblem(**json.load(f))
print(f"Deck capacities from the problem: {[deck.capacity for deck in problem.transporter.decks.values()]}")
# print("Problem loaded successfully:", problem)
# print("transporter loaded successfully:", problem.transporter.total_capacity)
# Create a solution instance
solution = ACLSolution(problem)
# Load the solution assignments
with open(output_file) as f:
    solution_json = json.load(f)
solution.from_json(solution_json)
print("Solution loaded successfully:", solution)
'''
ACLSolution(deck_assignment={'v1': 'd1', 'v2': 'd2', 'v3': 'd3', 'v4': 'd1', 'v5': 'd3', 'v6': 'd1', 'v7': 'd2', 'v8': 'd3'}, current_truck_load=[{'d1': ['v1', 'v4'], 'd2': ['v2'], 'd3': ['v3']}, {'d1': ['v1', 'v6'], 'd2': ['v7'], 'd3': ['v5']}, {'d1': ['v1', 'v6'], 'd2': ['v7'], 'd3': ['v5', 'v8']}, {'d1': [], 'd2': [], 'd3': []}])
'''
# calculate the deck capacities from solution ie. ACLSolution
 

