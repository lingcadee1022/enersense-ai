from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class sensor_reading(BaseModel):
    device_id : str
    timestamp :datetime
    voltage: float
    current: float
    power: float
    

class electrical_data(BaseModel):
    timestamp : datetime
    power: float
    voltage: float
    current: float
    predicted_appliance: str

class users_data(BaseModel):
    username : str
    email : str
    age : int
    gender : str
    education : str
    income: Optional[float]
    occupation: str
    marital_stasus : str
    religion : str
    household_size : int

class ai_suggestion(BaseModel):
    timestamp: datetime
    insight: str