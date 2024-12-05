from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class EquipmentQuery(BaseModel):
    prompt: str  # Prompt asking about equipment location

@app.post("/query_equipment")
async def query_equipment(request: EquipmentQuery):
    # URL of the JSON server
    json_server_url = "http://localhost:5000/equipment"

    # Fetch equipment data from JSON server
    try:
        response = requests.get(json_server_url)
        response.raise_for_status()
        equipment_data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to JSON server: {e}")

    # Create a list of all equipment names
    equipment_names = [equipment["equipment_name"].lower() for equipment in equipment_data.get("equipment", [])]

    # Parse the prompt to extract an equipment name
    prompt_lower = request.prompt.lower()
    matched_name = next((name for name in equipment_names if name in prompt_lower), None)

    if matched_name:
        # Find the matching equipment in the data
        for equipment in equipment_data.get("equipment", []):
            if equipment["equipment_name"].lower() == matched_name:
                return {
                    "equipment_name": equipment["equipment_name"],
                    "location": equipment.get("location", "Location data not available"),
                    "last_checked_out_at": equipment.get("last_checked_out_at", "N/A"),
                    "checked_out_by": equipment.get("checked_out_by", "N/A")
                }

    # If no match is found
    return {"message": f"No matching equipment found in the database for the given prompt."}
