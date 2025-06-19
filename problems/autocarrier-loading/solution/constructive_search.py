from copy import deepcopy

from roar_net_api.operations import SupportsApplyMove, SupportsLowerBoundIncrement, SupportsObjectiveValueIncrement

from solution import ACLSolution


class AddMove(
    SupportsApplyMove[ACLSolution],
    SupportsLowerBoundIncrement[ACLSolution],
    SupportsObjectiveValueIncrement[ACLSolution]
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