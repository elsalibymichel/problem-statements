from pydantic import BaseModel, model_validator
from typing import Dict, List, Optional
from utils import JSONValue

class Operation(BaseModel):
    load: Optional[List[str]] = []
    unload : Optional[List[str]] = []

    @model_validator(mode='before')
    def validate_operation(cls, values: JSONValue) -> JSONValue:
        if not (values.get('load', []) or values.get('unload', [])):
            raise ValueError("An operation must have either 'load' or 'unload' or both defined.")
        return values

class Vehicle(BaseModel):
    id: str
    dimension: int

class Deck(BaseModel):
    id: str
    capacity: int
    access_via: Optional[List[List[str]]] = None

class Transporter(BaseModel):
    total_capacity: int
    decks: Dict[str, Deck]
