from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

# Load the JSON data
with open("equipment_data.json", "r") as f:
    data = json.load(f)

@app.get("/equipment")
async def get_equipment():
    return data

@app.get("/equipment/{equipment_id}")
async def get_equipment_by_id(equipment_id: str):
    # Search for the equipment by ID
    for equipment in data["equipment"]:
        if equipment["equipment_id"] == equipment_id:
            return equipment
    raise HTTPException(status_code=404, detail="Equipment not found.")
