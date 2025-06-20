from copy import deepcopy
from typing import Optional
from itertools import product
from roar_net_api.operations import SupportsApplyMove, SupportsLowerBoundIncrement, SupportsRandomMove, SupportsLowerBoundIncrement, SupportsMoves
from typing import Iterator
from utils import random_pairs_iterator
import sys

from solution import ACLSolution


class AddMove(
    SupportsApplyMove[ACLSolution],
    SupportsLowerBoundIncrement[ACLSolution, int]
):
    """
    Move to assign a deck to a car.
    """
    def __init__(self, vehicle_id: int, deck_id: int):
        self.vehicle_id = vehicle_id
        self.deck_id = deck_id

    def apply_move(self, solution: ACLSolution) -> ACLSolution:
        new_solution = deepcopy(solution)
        new_solution.deck_assignment[self.vehicle_id] = self.deck_id
        new_solution.update_truck_load()  # TODO: make it more efficient
        if all(v for v, d in  solution.deck_assignment.items() if d is not None):
            new_solution.complete = True
        return new_solution

    def lower_bound_increment(self, solution: ACLSolution) -> Optional[int]:
        """Calculate value of the lower bound increment for this move."""
        # TODO: currently this just returns the difference in objective value
        new_solution = self.apply_move(solution.copy_solution())
        return new_solution.lower_bound() - solution.lower_bound()
    
class AddMoveNeighborhood(
    SupportsRandomMove[ACLSolution, AddMove],
    SupportsLowerBoundIncrement[ACLSolution, AddMove],
    SupportsMoves[ACLSolution, AddMove]
):
    def __init__(self, problem: 'ACLProblem'):
        self.problem = problem

    def random_move(self, solution: ACLSolution) -> Optional[AddMove]:
        """Generate a random constructive move for the given solution."""
        return next(self.random_moves_without_replacement(solution), None)
    
    def random_moves_without_replacement(self, solution: ACLSolution) -> Iterator[AddMove]:
        """Generate random moves without replacement."""
        problem = solution.problem
        remaining_vehicles = list(v for v, d in  solution.deck_assignment.items() if d is None)
        decks = list(problem.transporter.decks.keys())
        for vehicle_index, deck_index in random_pairs_iterator(len(remaining_vehicles), len(decks)):
            vehicle_id = remaining_vehicles[vehicle_index]
            deck_id = decks[deck_index]
            yield AddMove(vehicle_id, deck_id)
    
    def moves(self, solution: ACLSolution) -> Iterator[AddMove]:
        """Generate all possible moves for the given solution."""
        problem = solution.problem
        # These are the vehicles that do not have a deck assigned yet
        remaining_vehicles = list(v for v, d in  solution.deck_assignment.items() if d is None)
        decks = list(problem.transporter.decks.keys())
        for vehicle_id, deck_id in product(remaining_vehicles, decks):
            yield AddMove(vehicle_id, deck_id)            


