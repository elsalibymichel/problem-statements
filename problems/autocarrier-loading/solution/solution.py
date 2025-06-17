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