import itertools
from copy import deepcopy

from roar_net_api.operations import SupportsObjectiveValue, SupportsCopySolution

from data_helper_class import Vehicle
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from constraints import deck_capacity_constraint, total_capacity_constraint

@dataclass
class DeckState():
    load: list[Vehicle]
    capacity_remaining: int
    capacity_used: int

class ACLSolution(
    SupportsObjectiveValue,
    SupportsCopySolution
):
    def __init__(self, problem : 'ACLProblem', json_data: Optional[List[Dict[str, Any]]] = None):
        self.problem = problem
        self.deck_assignment = {v: None for v in problem.vehicles.keys()}
        self.current_truck_load = [{deck_id: DeckState(load=[], capacity_remaining=self.problem.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.problem.transporter.decks.keys()} for _ in range(len(self.problem.route))]
        if json_data is not None:
            self.from_json(json_data)

    def from_json(self, json_data :  List[Dict[str, Any]]) -> None:
        """Load the solution from a JSON string."""
        for assignment in json_data:
            vehicle_id = assignment['vehicle']
            deck_id = assignment['deck']
            self.deck_assignment[vehicle_id] = deck_id
        self.update_truck_load()

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the solution to a JSON serializable format."""
        json_data = []
        for vehicle_id, deck_id in self.deck_assignment.items():
            json_data.append({
                'vehicle': vehicle_id,
                'deck': deck_id
            })
        return json_data

    def copy_solution(self) -> 'ACLSolution':
        """Create a deep copy of the solution."""
        new_solution = ACLSolution(self.problem)
        new_solution.deck_assignment = deepcopy(self.deck_assignment)
        new_solution.current_truck_load = deepcopy(self.current_truck_load)
        return new_solution
    
    def objective_value(self) -> int:
        """Calculate the objective value of the solution."""
        # The objective value is the sum of moves needed to unload vehicles at each stop
        # plus the violation of the deck capacity constraints.
        moves_to_unload = self.sum_moves_to_unload_and_load()
        capacity_violations = self.sum_capacity_violations()
        return moves_to_unload + capacity_violations
    
    def sum_capacity_violations(self) -> int:
        """Return the sum of the capacity violations for all decks."""
        total_violations = 0
        for stop_load in self.current_truck_load:
            for deck_id, deck_state in stop_load.items():
                if deck_state.capacity_remaining < 0:
                    total_violations += abs(deck_state.capacity_remaining)
        assert deck_capacity_constraint(self.problem, self, distance_to_feasibility=True) == total_violations, "The total capacity violations do not match the deck capacity constraint."
        return total_violations

    def update_truck_load(self):
        """Update the current truck load based on the deck assignments."""
        current_load = {deck_id: DeckState(load=[], capacity_remaining=self.problem.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.problem.transporter.decks.keys()}
        for stop, operation in enumerate(self.problem.route):
            for vehicle_id in operation.unload or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                vehicle_capacity = self.problem.vehicles[vehicle_id].dimension
                #current_load[assigned_deck].load.remove(vehicle_id)
                #current_load[assigned_deck].capacity_used -= vehicle_capacity
                #current_load[assigned_deck].capacity_remaining += vehicle_capacity
            for vehicle_id in operation.load or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                vehicle_capacity = self.problem.vehicles[vehicle_id].dimension
                #current_load[assigned_deck].load.append(vehicle_id)
                #current_load[assigned_deck].capacity_used += vehicle_capacity
                #current_load[assigned_deck].capacity_remaining -= vehicle_capacity
            self.current_truck_load[stop] = deepcopy(current_load)        

    def __repr__(self):
        """Return a string representation of the solution."""
        return f"ACLSolution(deck_assignment={self.deck_assignment}, current_truck_load={self.current_truck_load})"
    
    def __eq__(self, other: 'ACLSolution') -> bool:
        """Check if two solutions are equal."""
        if not isinstance(other, ACLSolution):
            return False
        return (self.deck_assignment == other.deck_assignment and
                self.current_truck_load == other.current_truck_load)

    def sum_moves_to_unload(self) -> int:
        """Return the sum of the minimum unnecessary car moves needed at any stop to access vehicles to unload."""
        min_moves_per_stop = []

        for stop_index, stop_truck_load in enumerate(self.current_truck_load):
            if stop_index == len(self.problem.route)-1:
                continue
            operation = self.problem.route[stop_index + 1]
            cars_to_unload = operation.unload
            if not cars_to_unload:
                min_moves_per_stop.append(0)
                continue

            # Identify decks from which we need to unload
            decks_with_car_to_unload = set()
            for car in cars_to_unload:
                for deck_id, deck_state in stop_truck_load.items():
                    if car in deck_state.load:
                        decks_with_car_to_unload.add(deck_id)
                        continue

            # Build blocking vehicle sets per deck
            path_combinations = {}
            for deck_id in decks_with_car_to_unload:
                deck = self.problem.transporter.decks[deck_id]
                blocking_sets = []

                if deck.access_via:
                    # Add blocking vehicles from access paths
                    for path in deck.access_via:
                        blocking_vehicles = set()
                        for via_deck_id in path:
                            blocking_vehicles.update(stop_truck_load[via_deck_id].load)
                        blocking_sets.append(blocking_vehicles - set(cars_to_unload))
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
        print("Mover for unload for each stop (ignoring stop 0): ", min_moves_per_stop)
        return sum(min_moves_per_stop)

    def sum_moves_to_unload_and_load(self) -> int:
        """Return the sum of the minimum unnecessary car moves needed at any stop to access vehicles to unload."""
        min_moves_per_stop = []
        min_sets_per_stop = []

        for stop_index, stop_truck_load in enumerate(self.current_truck_load):
            if stop_index == len(self.problem.route)-1:
                continue
            operation = self.problem.route[stop_index + 1]
            cars_to_unload = operation.unload
            cars_to_load = operation.load

            if not cars_to_unload and not cars_to_load:
                min_moves_per_stop.append(0)
                continue

            path_combinations = {}

            #-------------------UNLOADING--------------------
            if cars_to_unload:
                # Unloading: identify decks from which we need to unload
                decks_with_car_to_unload = set()
                for car in cars_to_unload:
                    for deck_id, vehicles in stop_truck_load.items():
                        if car in vehicles.load:
                            decks_with_car_to_unload.add(deck_id)
                            continue
                # Unloading: build blocking vehicle sets per deck
                for deck_id in decks_with_car_to_unload:
                    deck = self.problem.transporter.decks[deck_id]
                    blocking_sets = []
                    if deck.access_via:
                        # Add blocking vehicles from access paths
                        for path in deck.access_via:
                            blocking_vehicles = set()
                            for via_deck_id in path:
                                blocking_vehicles.update(stop_truck_load[via_deck_id].load)
                            blocking_sets.append(blocking_vehicles - set(cars_to_unload))
                    else:
                        # Freely accessible deck
                        blocking_sets.append(set())
                    #TODO for now, we are assume the absence of blocking cars on the same deck, but it should be considered
                    path_combinations[deck_id + "-unload"] = blocking_sets

            #--------------------LOADING---------------------
            if cars_to_load:
                # Loading: identify decks from which we need to unload
                decks_with_car_to_load = set()
                for car_id in cars_to_load:
                    deck_id = self.deck_assignment[car_id]
                    decks_with_car_to_load.add(deck_id)
                # Loading: build blocking vehicle sets per deck
                for deck_id in decks_with_car_to_load:
                    deck = self.problem.transporter.decks[deck_id]
                    blocking_sets = []
                    if deck.access_via:
                        # Add blocking vehicles from access paths
                        for path in deck.access_via:
                            blocking_vehicles = set()
                            for via_deck_id in path:
                                blocking_vehicles.update(stop_truck_load[via_deck_id].load)
                            blocking_sets.append(blocking_vehicles - set(cars_to_unload))
                    else:
                        # Freely accessible deck
                        blocking_sets.append(set())
                    # For loading, it's not necessary to consider other cars on same deck
                    path_combinations[deck_id + "-load"] = blocking_sets

            # Compute the minimal number of moves (for both load and unload) needed across all combinations of paths
            moves_per_combination = []

            for combination in itertools.product(*path_combinations.values()):
                cars_to_move = set()
                for car_set in combination:
                    cars_to_move.update(car_set)
                moves_per_combination.append((len(cars_to_move), cars_to_move))

            if moves_per_combination:
                min_len, min_cars = min(moves_per_combination, key=lambda x: x[0])
                min_moves_per_stop.append(min_len)
                #min_sets_per_stop.append(min_cars + set(cars_to_unload))
                min_sets_per_stop.append(min_cars.union(cars_to_unload))
            else:
                min_moves_per_stop.append(0)
                min_sets_per_stop.append(set())

        print("Mover for unload and load for each stop (ignoring stop 0): ", min_moves_per_stop, min_sets_per_stop)
        return sum(min_moves_per_stop),min_sets_per_stop