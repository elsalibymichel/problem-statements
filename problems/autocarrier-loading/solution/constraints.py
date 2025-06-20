# capacity constriant:
from typing import Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from problem import ACLProblem
    from solution import ACLSolution

def total_capacity_constraint(problem: 'ACLProblem', solution: 'ACLSolution', distance_to_feasibility: bool = False) -> Union[bool, int]:
    transporter_capacity : int = problem.transporter.total_capacity
    # calculate the deck capacities from solution i.e., ACLSolution
    total_capacities_violations : int = 0
    for decks in solution.current_truck_load:
        total_capacity_used : int = 0
        for vehicle_id, deck_state in decks.items():            
            total_capacity_used += deck_state.capacity_used
        if total_capacity_used > transporter_capacity:
            if not distance_to_feasibility:
                return False
            total_capacities_violations += total_capacity_used - transporter_capacity
    # Check if the total capacities used is less than or equal to the transporter capacity
    if distance_to_feasibility:
        return total_capacities_violations
    else:
        return True
        
def deck_capacity_constraint(problem: 'ACLProblem', solution: 'ACLSolution', distance_to_feasibility: bool = False) -> Union[bool, int]:
    total_distance_to_feasibility : int = 0
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