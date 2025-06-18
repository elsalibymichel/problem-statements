import itertools
from copy import deepcopy

class ACLSolution():
    def __init__(self, problem):
        self.instance = problem
        self.deck_assignment = {v: None for v in problem.vehicles.keys()}
        self.current_truck_load = [{ deck_id: [] for deck_id in self.instance.transporter.decks.keys()} for _ in range(len(self.instance.route))]

    def from_json(self, json_data):
        """Load the solution from a JSON string."""
        for assignment in json_data:
            vehicle_id = assignment['vehicle']
            deck_id = assignment['deck']
            self.deck_assignment[vehicle_id] = deck_id
        self.update_truck_load()

    def update_truck_load(self):
        """Update the current truck load based on the deck assignments."""
        current_load = {deck_id: [] for deck_id in self.instance.transporter.decks.keys()}
        for stop, operation in enumerate(self.instance.route):
            for vehicle_id in operation.unload or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
                current_load[assigned_deck].remove(vehicle_id)
            for vehicle_id in operation.load or []:
                assigned_deck = self.deck_assignment.get(vehicle_id)
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
            cars_to_unload = operation.unload
            if not cars_to_unload:
                min_moves_per_stop.append(0)
                continue

            # Identify decks from which we need to unload
            decks_with_car_to_unload = set()
            for car in cars_to_unload:
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
        # print("Mover for unload for each stop (ignoring stop 0): ", min_moves_per_stop)
        return sum(min_moves_per_stop)

    #TODO test this function
    def sum_moves_to_unload_and_load(self) -> int:
        """Return the sum of the minimum unnecessary car moves needed at any stop to access vehicles to unload."""
        min_moves_per_stop = []

        for stop_index, stop_truck_load in enumerate(self.current_truck_load):
            if stop_index == len(self.instance.route)-1:
                continue
            operation = self.instance.route[stop_index+1]
            cars_to_unload = operation.unload
            cars_to_load = operation.load

            if not cars_to_unload and not cars_to_load:
                min_moves_per_stop.append(0)
                continue

            path_combinations = {}

            # Unloading: identify decks from which we need to unload
            decks_with_car_to_unload = set()
            for car in cars_to_unload:
                for deck_id, vehicles in stop_truck_load.items():
                    if car in vehicles:
                        decks_with_car_to_unload.add(deck_id)
                        continue
            # Unloading: build blocking vehicle sets per deck
            for deck_id in decks_with_car_to_unload:
                deck = self.instance.transporter.decks[deck_id]
                blocking_sets = []
                if deck.access_via:
                    # Add blocking vehicles from access paths
                    for path in deck.access_via:
                        blocking_vehicles = set()
                        for via_deck_id in path:
                            blocking_vehicles.update(stop_truck_load[via_deck_id])
                        blocking_sets.append(blocking_vehicles - set(cars_to_unload))
                else:
                    # Freely accessible deck
                    blocking_sets.append(set())
                #TODO for now, we are assume the absence of blocking cars on the same deck, but it should be considered
                path_combinations[deck_id + "-unload"] = blocking_sets

            # Loading: identify decks from which we need to unload
            decks_with_car_to_load = set()
            for car in cars_to_load:
                for deck_id, vehicles in stop_truck_load.items():
                    if car in vehicles:
                        decks_with_car_to_load.add(deck_id)
                        continue
            # Loading: build blocking vehicle sets per deck
            for deck_id in decks_with_car_to_load:
                deck = self.instance.transporter.decks[deck_id]
                blocking_sets = []
                if deck.access_via:
                    # Add blocking vehicles from access paths
                    for path in deck.access_via:
                        blocking_vehicles = set()
                        for via_deck_id in path:
                            blocking_vehicles.update(stop_truck_load[via_deck_id])
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
                moves_per_combination.append(len(cars_to_move))

            if moves_per_combination:
                min_moves_per_stop.append(min(moves_per_combination))
            else:
                min_moves_per_stop.append(0)

        # print("Mover for unload and load for each stop (ignoring stop 0): ", min_moves_per_stop)
        return sum(min_moves_per_stop)