from fastapi import FastAPI 
from models import electrical_data, users_data, ai_suggestion, sensor_reading
from database import users, sensor_data,energy_log,ai_insights
from bson import ObjectId

app = FastAPI()

@app.get("/")
def greet():
    return "Hello"

@app.post("/user")
def create_user(user: users_data):
    users.insert_one(user.dict())
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
    result = sensor_data.insert_one(data_dict)

    return{
        "stasus" : "success",
        "message": "Data stored successfully",
        "id": str(result.inserted_id)
    }

@app.get("/live-usage")
def live_usage():
    #latest = energy_log.find_one(sort=[("_id", -1)])
    #if latest:
    #    latest["_id"] = str(latest["_id"])
    #    return latest
    #return {
     #   "message": "No data found"
    #}
    pass


@app.post("/ai")
def add_inssight(data: ai_suggestion):
    #return{
     #   "insight": "No data found"
    #}

    pass


@app.get("/history/{appliance}")
def history(appliance : str):

    history_data=[]
    data = energy_log.find({"appliance": appliance}).sort("_id", -1)

    for i in data:
        i["_id"] = str(i["_id"])
        history_data.append({
            "timestamp": i.get("timestamp"),
            "power": i.get("power")
        })

    return history_data

@app.get("/prediction")
def ai_prediction():
    data = list(energy_log.find())

    if len(data) == 0:
        return {
            "message": "No data available"
        }

    total_power = 0

    appliance_power = {}
    for item in data:
        power = item.get("estimated_power",0)
        appliance = item.get("appliance","Unknown")
        total_power += power
        if appliance not in appliance_power:
            appliance_power[appliance] = 0

        appliance_power[appliance] += power

    if appliance not in appliance_power:
            appliance_power[appliance] = 0

    appliance_power[appliance] += power

    average_power = total_power / len(data)

    estimated_daily_cost = round(
        (average_power * 24) / 1000 * 0.218,
        2
    )

    estimated_monthly_cost = round(
        estimated_daily_cost * 30,
        2
    )

    highest_appliance = max(
        appliance_power,
        key=appliance_power.get
    )

    return {
        "estimated_daily_cost": estimated_daily_cost,
        "estimated_monthly_cost": estimated_monthly_cost,
        "highest_consumption_appliance": highest_appliance
    }


