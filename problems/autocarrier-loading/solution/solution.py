import itertools
from copy import deepcopy
from problem import Vehicle
from dataclasses import dataclass

@dataclass
class DeckState():
    load: list[Vehicle]
    capacity_remaining: int
    capacity_used: int

class ACLSolution():
    def __init__(self, problem):
        self.instance = problem
        self.deck_assignment = {v: None for v in problem.vehicles.keys()}

        self.current_truck_load = [{ deck_id: DeckState(load=[], capacity_remaining=self.instance.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.instance.transporter.decks.keys()} for _ in range(len(self.instance.route))]

    def from_json(self, json_data):
        """Load the solution from a JSON string."""
        for assignment in json_data:
            vehicle_id = assignment['vehicle']
            deck_id = assignment['deck']
            self.deck_assignment[vehicle_id] = deck_id
        self.update_truck_load()

    def update_truck_load(self):
        """Update the current truck load based on the deck assignments."""
        current_load = {deck_id: DeckState(load=[], capacity_remaining=self.instance.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.instance.transporter.decks.keys()}
        for stop, operation in enumerate(self.instance.route):
            for vehicle_id in operation.unload or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                # CHANGE HERE: Remove the vehicle from the current load
                current_load[assigned_deck].remove(vehicle_id)
            for vehicle_id in operation.load or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                # CHANGE HERE: Remove the vehicle from the current load
                current_load[assigned_deck].append(vehicle_id)
            self.current_truck_load[stop] = deepcopy(current_load)        

    def __repr__(self):
        """Return a string representation of the solution."""
        return f"ACLSolution(deck_assignment={self.deck_assignment}, current_truck_load={self.current_truck_load})"

    #TODO account also car moves for loading
    def sum_moves_to_unload(self) -> int:
        """Return the sum of the minimum unnecessary car moves needed at any stop to access vehicles to unload."""
        min_moves_per_stop = []

        for stop_index, stop_truck_load in enumerate(self.current_truck_load):
            if stop_index == len(self.instance.route)-1:
                continue
            operation = self.instance.route[stop_index+1]
            if not operation.unload:
                min_moves_per_stop.append(0)
                continue

            # Identify decks from which we need to unload
            decks_with_car_to_unload = set()
            for car in operation.unload:
                for deck_id, vehicles in stop_truck_load.items():
                    if car in vehicles:
                        decks_with_car_to_unload.add(deck_id)
                        continue

            # Build blocking vehicle sets per deck
            path_combinations = {}
            for deck_id in decks_with_car_to_unload:
                deck = self.instance.transporter.decks[deck_id]
                blocking_sets = []

                if deck.access_via:
                    # Add blocking vehicles from access paths
                    for path in deck.access_via:
                        blocking_vehicles = set()
                        for via_deck_id in path:
                            blocking_vehicles.update(stop_truck_load[via_deck_id])
                        blocking_sets.append(blocking_vehicles - set(operation.unload))
                else:
                    # Freely accessible deck
                    blocking_sets.append(set())

                #TODO for now, we are assume the absence of blocking cars on the same deck, but it should be considered
                path_combinations[deck_id] = blocking_sets

            # Compute the minimal number of moves needed across all combinations of paths
            moves_per_combination = []
            for combination in itertools.product(*path_combinations.values()):
                cars_to_move = set()
                for car_set in combination:
                    cars_to_move.update(car_set)
                moves_per_combination.append(len(cars_to_move))

            if moves_per_combination:
                min_moves_per_stop.append(min(moves_per_combination))
            else:
                min_moves_per_stop.append(0)
        # print(min_moves_per_stop)
        return sum(min_moves_per_stop)
    
    def objective_value(self) -> int:
        """Return the objective value of the solution."""
        # TODO: compute the amount of violation of constraints + Number of moves to unload
        return self.sum_moves_to_unload()