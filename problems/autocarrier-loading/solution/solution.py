import itertools
from copy import deepcopy
import click

from roar_net_api.operations import SupportsObjectiveValue, SupportsLowerBound, SupportsCopySolution

from data_helper_class import Vehicle
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from constraints import deck_capacity_constraint, total_capacity_constraint

if TYPE_CHECKING:
    from problem import ACLProblem

@dataclass
class DeckState():
    load: list[Vehicle]
    capacity_remaining: int
    capacity_used: int

class ACLSolution(
    SupportsObjectiveValue[int],
    SupportsCopySolution,
    SupportsLowerBound[int]
):
    def __init__(self, problem : 'ACLProblem', json_data: Optional[List[Dict[str, Any]]] = None):
        self.problem : 'ACLProblem' = problem
        self.deck_assignment : Dict[str, Optional[str]]= {v: None for v in problem.vehicles.keys()}
        self.current_truck_load : List[Dict[str, DeckState]] = [{deck_id: DeckState(load=[], capacity_remaining=self.problem.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.problem.transporter.decks.keys()} for _ in range(len(self.problem.route))]
        self.complete : bool = False
        if json_data is not None:
            self.from_json(json_data)

    def from_json(self, json_data :  List[Dict[str, Any]]) -> None:
        """Load the solution from a JSON string."""
        for assignment in json_data:
            vehicle_id = assignment['vehicle']
            deck_id = assignment['deck']
            self.deck_assignment[vehicle_id] = deck_id
        if all(self.deck_assignment[v] is not None for v in self.problem.vehicles.keys()):
            self.complete = True
        self.update_truck_load()

    def to_json(self) -> List[Dict[str, Any]]:
        """Convert the solution to a JSON serializable format."""
        json_data = []
        for vehicle_id, deck_id in self.deck_assignment.items():
            if deck_id is None:
                continue
            json_data.append({
                'vehicle': vehicle_id,
                'deck': deck_id
            })
        return json_data
    
    def __str__(self):
        """Return a string representation of the solution."""
        min_vector_dimension = min(self.problem.vehicles[v].dimension for v in self.problem.vehicles.keys())
        representation = "ACLSolution:\n"
        representation += "Deck Assignments:\n"
        for vehicle_id, deck_id in self.deck_assignment.items():            
            representation += f"  Vehicle {vehicle_id} -> Deck {deck_id}\n"
        representation += "Current Truck Load:\n"
        for stop_index, stop_load in enumerate(self.current_truck_load):
            representation += f"  Stop {stop_index}:\n"
            for deck_id, deck_state in stop_load.items():
                color = 'red' if deck_state.capacity_remaining < 0 else 'yellow' if deck_state.capacity_remaining < min_vector_dimension else 'green'
                representation += click.style(f"    Deck {deck_id}: Load: {deck_state.load}, Capacity (remaining/used): {deck_state.capacity_remaining}/{deck_state.capacity_used}\n", fg=color)
        return representation

    def copy_solution(self) -> 'ACLSolution':
        """Create a deep copy of the solution."""
        new_solution = ACLSolution(self.problem)
        new_solution.deck_assignment = deepcopy(self.deck_assignment)
        new_solution.current_truck_load = deepcopy(self.current_truck_load)
        new_solution.complete = self.complete
        return new_solution
    
    def objective_value(self) -> Optional[int]:
        """Calculate the objective value of the solution."""
        # The objective value is the sum of moves needed to unload vehicles at each stop
        # plus the violation of the deck capacity constraints.
        if not self.complete:
            return None
        car_movements = self.sum_moves_to_unload_and_load()
        capacity_violations = deck_capacity_constraint(self.problem, self, distance_to_feasibility=True)
        total_capacity_violations = total_capacity_constraint(self.problem, self, distance_to_feasibility=True)
        # Probably the car_movements[1] should be changed to consider from which deck the vehicle is unloaded
        return car_movements[0] + capacity_violations + total_capacity_violations
    
    def update_truck_load(self, start_stop: int = 0, end_stop: int = -1) -> None:
        """Update the current truck load based on the deck assignments."""
        if start_stop == 0:
            current_load = {deck_id: DeckState(load=[], capacity_remaining=self.problem.transporter.decks[deck_id].capacity, capacity_used=0) for deck_id in self.problem.transporter.decks.keys()}
        else:
            current_load = deepcopy(self.current_truck_load[start_stop - 1])
        end_stop = end_stop if end_stop >= 0 else len(self.problem.route) + end_stop
        # Check that start_stop and end_stop are within the range of the route
        assert 0 <= start_stop < len(self.problem.route), "start_stop must be within the range of the route"
        assert 0 <= end_stop < len(self.problem.route), "end_stop must be within the range of the route"
        assert start_stop <= end_stop, "start_stop must be less than or equal to end_stop"
        for stop in range(start_stop, end_stop + 1):
            operation = self.problem.route[stop]
            for vehicle_id in operation.unload or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                if not assigned_deck: # the vehicle is not assigned to any deck (i.e., partial solution)
                    continue
                vehicle_capacity = self.problem.vehicles[vehicle_id].dimension
                current_load[assigned_deck].load.remove(vehicle_id)
                current_load[assigned_deck].capacity_used -= vehicle_capacity
                current_load[assigned_deck].capacity_remaining += vehicle_capacity
            for vehicle_id in operation.load or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                if not assigned_deck: # the vehicle is not assigned to any deck (i.e., partial solution)
                    continue
                vehicle_capacity = self.problem.vehicles[vehicle_id].dimension
                current_load[assigned_deck].load.append(vehicle_id)
                current_load[assigned_deck].capacity_used += vehicle_capacity
                current_load[assigned_deck].capacity_remaining -= vehicle_capacity
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
        return sum(min_moves_per_stop)

    def sum_moves_to_unload_and_load(self) -> int:
        """Return the sum of the minimum unnecessary car moves needed at any stop to access vehicles to unload."""
        min_moves_per_stop = []
        min_sets_per_stop = []

        for stop_index, stop_truck_load in enumerate(self.current_truck_load):
            if stop_index == len(self.problem.route) - 1:
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
                    if deck_id is not None: # the vehicle is assigned to a deck, might be none because of partial solution
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

        return sum(min_moves_per_stop), min_sets_per_stop
    
    def lower_bound(self) -> int:
        """
        Calculate a lower bound for the objective value.
        Basically, it is the same as the objective value, but it does not require the solution to be complete.
        """
        car_movements = self.sum_moves_to_unload_and_load()
        capacity_violations = deck_capacity_constraint(self.problem, self, distance_to_feasibility=True)
        total_capacity_violations = total_capacity_constraint(self.problem, self, distance_to_feasibility=True)
        # Probably the car_movements[1] should be changed to consider from which deck the vehicle is unloaded
        return car_movements[0] + capacity_violations + total_capacity_violations
