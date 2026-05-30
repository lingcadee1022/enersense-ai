from fastapi import FastAPI 
from models import electrical_data, users_data, ai_suggestion, sensor_reading
from database import users, sensor_data,energy_log,ai_insights
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

@app.post("/user")
def create_user(user: users_data):
    users.insert_one(user.model_dump())
    return {"message": "User Created"}

@app.get("/user")
def get_user():
    data = users.find()
    return [user_serializer(user) for user in data]

def user_serializer(user):
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "age": user.get("age"),
        "gender": user.get("gender"),
        "income": user.get("income"),
        "occupation": user.get("occupation"),
        "marital_status": user.get("marital_status"),
        "religion": user.get("religion"),
        "household_size": user.get("household_size"),
    }


@app.post("/sensor")
def receive_sensor(data: sensor_reading):

    data_dict = data.model_dump()

    sensor_data.insert_one(data_dict)

    response = requests.post(
        "https://enersense-ai.onrender.com/sensor-data",
        json={
            "timestamp": str(data.timestamp),
            "power": data.power,
            "voltage": data.voltage,
            "current": data.current
        }
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "message": "AI service failed",
            "details": response.text
        }
    
    ai_result = response.json()

    final_data = {
        **data_dict,
        **ai_result
    }

    result=energy_log.insert_one(final_data)
    final_data["_id"] = str(result.inserted_id)

    return {
        "status": "success",
        "data": final_data
    }

@app.get("/live-usage")
def live_usage():
    latest = energy_log.find_one(
        sort=[("_id", -1)]
    )

    if latest is None:
        return {
            "message": "No data found"
        }

    latest["_id"] = str(
        latest["_id"]
    )

    return latest



@app.get("/history")
def get_all_history():

    data = energy_log.find().sort("timestamp", -1)

    history = []

    for item in data:
        history.append({
            "timestamp": item.get("timestamp"),
            "power": item.get("power"),
            "voltage": item.get("voltage"),
            "current": item.get("current"),
            "appliance": item.get("predicted_appliance"),
            "energy_score": item.get("energy_score"),
            "is_anomaly": item.get("is_anomaly"),
        })

    return {
        "count": len(history),
        "data": history
    }

@app.get("/history/{appliance}")
def get_history_by_appliance(appliance: str):

    data = energy_log.find({
        "predicted_appliance": appliance
    }).sort("_id", -1)

    history = []

    for item in data:
        history.append({
            "timestamp": item.get("timestamp"),
            "power": item.get("power"),
            "appliance": item.get("predicted_appliance"),
            "energy_score": item.get("energy_score"),
            "is_anomaly": item.get("is_anomaly"),
        })

    return {
        "appliance": appliance,
        "count": len(history),
        "data": history
    }

@app.get("/forecast")
def get_forecast():
    response = requests.get("https://enersense-ai.onrender.com/forecast")

    if response.status_code != 200:
        return {
            "message": "Forecast unavailable"
        }

    return response.json()

@app.get("/insights")
def get_insights():
    response = requests.get("https://enersense-ai.onrender.com/insights")
    if response.status_code != 200:
        return {
            "message": "Insights unavailable"
        }
    return response.json()

@app.get("/prediction")
def prediction():

    response = requests.get("https://enersense-ai.onrender.com/appliances")

    if response.status_code != 200:
        return {
            "message": "Prediction unavailable"
        }

    return response.json()

@app.get("/health")
def health():

    response = requests.get("https://enersense-ai.onrender.com/health")

    return response.json()