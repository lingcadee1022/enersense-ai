from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

uri=os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["EnerSenseAI"]
sensor_data = db["sensor_data"]
energy_log = db['energy_log']
users= db['users']
ai_insights= db["ai_insights"]
