import random

from data_helper_class import Operation,Vehicle,Deck,Transporter
from pydantic import BaseModel, model_validator
from typing import Dict, List, Optional, Self
import sys
import json
from solution import ACLSolution


class ACLProblem(BaseModel):
    route: List[Operation]
    vehicles: Dict[str, Vehicle]
    transporter: Transporter

    @model_validator(mode='before')
    def populate_ids(cls, values: Dict) -> Dict:
        if 'vehicles' in values:
            # Transform vehicles dict to include IDs
            vehicles_with_ids = {}
            for vehicle_id, vehicle_data in values['vehicles'].items():
                # Add the vehicle ID to the vehicle data
                vehicle_data_with_id = {**vehicle_data, 'id': vehicle_id}
                vehicles_with_ids[vehicle_id] = vehicle_data_with_id
            values['vehicles'] = vehicles_with_ids
        if 'decks' in values.get('transporter', {}):
            # Transform decks dict to include IDs
            decks_with_ids = {}
            for deck_id, deck_data in values['transporter']['decks'].items():
                # Add the deck ID to the deck data
                deck_data_with_id = {**deck_data, 'id': deck_id}
                decks_with_ids[deck_id] = deck_data_with_id
            values['transporter']['decks'] = decks_with_ids
        return values
    
    @model_validator(mode='after')
    def validate_route_operations(self) -> Self:
        # Emtpy route is allowed, but if it exists, it must have a valid first and last operation
        if not self.route:
            return self
        if self.route[0].unload:
            raise ValueError("The first operation in the route must not have an 'unload' defined.")
        if self.route[-1].load:
            raise ValueError("The last operation in the route must not have a 'load' defined.")
        return self

    def random_solution(self) -> ACLSolution:
        vehicles = self.vehicles.keys()
        decks = list(self.transporter.decks.keys())
        solution = ACLSolution(self)
        for vehicle_id in vehicles:
            solution.deck_assignment[vehicle_id] = random.choice(decks)
        solution.update_truck_load()
        return solution
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python problem.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]        
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)
        problem = ACLProblem(**data)
        print(f"Problem: {problem}")
        print(f"Random solution: {problem.random_solution()}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("Problem loaded successfully.")