# capacity constriant:
import json
from problem import ACLProblem
from solution import ACLSolution
from typing import Union

def total_capacity_constraint(problem: ACLProblem, solution: ACLSolution, distance_to_feasibility: bool = False) -> Union[bool, int]:
    transporter_capacity = problem.transporter.total_capacity
    # calculate the deck capacities from solution i.e., ACLSolution
    total_capacities_used = 0
    for decks in solution.current_truck_load:
        for vehicle_id, deck_state in decks.items():
            total_capacities_used += deck_state.capacity_used
    # Check if the total capacities used is less than or equal to the transporter capacity
    if distance_to_feasibility:
        return transporter_capacity - total_capacities_used
    else:
        return total_capacities_used  <= transporter_capacity 
        
def deck_capacity_constraint(problem: ACLProblem, solution: ACLSolution, distance_to_feasibility: bool = False) -> Union[bool, int]:
    total_distance_to_feasibility = 0
    for decks in solution.current_truck_load:
        for vehicle_id, deck_state in decks.items():
            if deck_state.capacity_remaining < 0:
                if not distance_to_feasibility:
                    return False
                total_distance_to_feasibility += abs(deck_state.capacity_remaining)
    if distance_to_feasibility:
        return total_distance_to_feasibility
    else:
        return True