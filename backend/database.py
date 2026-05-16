from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://qiyang1127:qiy12345@cluster0.hqjyw1m.mongodb.net/?appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
client.drop_database("electrical_usage")

db = client["EnerSenseAI"]
sensor_data = db["sensor_data"]
energy_log = db['energy_log']
users= db['users']
ai_insights= db["ai_insights"]
