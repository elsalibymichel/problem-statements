class ACLSolution():
    def __init__(self, problem):
        self.instance = problem
        self.deck_assignment = {v: None for v in problem.vehicles.keys()}

    def from_json(self, json_data):
        """Load the solution from a JSON string."""
        import json
        data = json.loads(json_data)
        for assignment in data:
            vehicle_id = assignment['vehicle']
            deck_id = assignment['deck']
            self.deck_assignment[vehicle_id] = deck_id

    def __repr__(self):
        """Return a string representation of the solution."""
        return f"ACLSolution(deck_assignment={self.deck_assignment})"