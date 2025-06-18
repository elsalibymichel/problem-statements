import copy
from typing import Optional

from roar_net_api.operations import SupportsApplyMove, SupportsRandomMove
from solution import ACLSolution
import random

class ChangeDeckMove(
    SupportsApplyMove[ACLSolution]
):
    def __init__(self, vehicle_id: str, deck_id: str):
        self.vehicle_id = vehicle_id
        self.deck_id = deck_id

    def apply_move(self, solution: ACLSolution) -> ACLSolution:
        new_solution = copy.deepcopy(solution)
        new_solution.deck_assignment[self.vehicle_id] = self.deck_id
        return new_solution

class ChangeDeckNeighbourhood(
    SupportsRandomMove[ACLSolution, ChangeDeckMove]
):

    def random_move(self, solution: ACLSolution) -> Optional[ChangeDeckMove]:
        problem = solution.problem
        rnd_vehicle_id = random.choice(list(problem.vehicles.keys()))
        decks = list(problem.decks.keys())
        decks.remove(solution.deck_assignment[rnd_vehicle_id])
        rnd_deck_id = random.choice(decks)
        return ChangeDeckMove(rnd_vehicle_id, rnd_deck_id)

