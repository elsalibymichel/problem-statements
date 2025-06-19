from copy import deepcopy
from typing import Optional, Iterator

from roar_net_api.operations import SupportsApplyMove, SupportsRandomMove, SupportsObjectiveValueIncrement
from solution import ACLSolution
import random
from utils import random_pairs_iterator

class ChangeDeckMove(
    SupportsApplyMove[ACLSolution],
    SupportsObjectiveValueIncrement
):
    def __init__(self, vehicle_id: str, deck_id: str):
        self.vehicle_id = vehicle_id
        self.deck_id = deck_id

    def apply_move(self, solution: ACLSolution) -> ACLSolution:
        new_solution = deepcopy(solution)
        new_solution.deck_assignment[self.vehicle_id] = self.deck_id
        new_solution.update_truck_load() #TODO: make it more efficient
        return new_solution
    
    def objective_value_increment(self, solution: ACLSolution) -> Optional[int]:
        """Calculate the objective value increment for this move."""
        # TODO: currently this just returns the difference in objective value
        new_solution = self.apply_move(solution.copy_solution())
        return new_solution.objective_value() - solution.objective_value()

class ChangeDeckNeighbourhood(
    SupportsRandomMove[ACLSolution, ChangeDeckMove]
):
    def __init__(self, problem: 'ACLProblem'):
        self.problem = problem

    def random_move(self, solution: ACLSolution) -> Optional[ChangeDeckMove]:
        return next(self.random_moves_without_replacement(solution), None)
    
    def random_moves_without_replacement(self, solution: ACLSolution) -> Iterator[ChangeDeckMove]:
        """Generate random moves without replacement."""
        problem = solution.problem
        vehicles = list(problem.vehicles.keys())
        decks = list(problem.transporter.decks.keys())
        for vehicle_index, deck_index in random_pairs_iterator(len(vehicles), len(decks)):
            vehicle_id = vehicles[vehicle_index]
            deck_id = decks[deck_index]
            current_deck = solution.deck_assignment[vehicle_id]
            if current_deck == deck_id:
                continue
            yield ChangeDeckMove(vehicle_id, deck_id)

    def moves(self, solution: ACLSolution) -> Iterator[ChangeDeckMove]:
        """Generate all possible moves for the given solution."""
        problem = solution.problem
        vehicles = list(problem.vehicles.keys())
        decks = list(problem.transporter.decks.keys())
        for vehicle_id in vehicles:
            current_deck = solution.deck_assignment[vehicle_id]
            for deck_id in decks:
                if current_deck == deck_id:
                    continue
                yield ChangeDeckMove(vehicle_id, deck_id)