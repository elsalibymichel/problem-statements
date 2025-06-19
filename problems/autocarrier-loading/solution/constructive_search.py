from copy import deepcopy
from typing import Optional

from roar_net_api.operations import SupportsApplyMove, SupportsLowerBoundIncrement, SupportsObjectiveValueIncrement

from solution import ACLSolution


class AddMove(
    SupportsApplyMove[ACLSolution],
    SupportsLowerBoundIncrement[ACLSolution]
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
        return new_solution

    def lower_bound_increment(self, solution: ACLSolution) -> Optional[int]:
        """Calculate value of the lower bound increment for this move."""
        # TODO: currently this just returns the difference in objective value
        new_solution = self.apply_move(solution.copy_solution())
        return new_solution.objective_value() - solution.objective_value()