import requests
import uuid
import json
import datetime

class GetAllEquipmentTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.added_equipment_ids = []

    def generate_idempotency_key(self):
        """Generate a unique idempotency key for each request."""
        return str(uuid.uuid4())

    def prepare_equipment_before_test(self):
        """
        Prepares equipment in the system before running getAllEquipment test.
        This ensures there's data to retrieve.
        """
        print("\n--- Preparing Equipment for Test ---")
        equipment_to_add = [
            {
                "_id": str(uuid.uuid4().int)[:8],
                "_equipment_name": f"Test Equipment {i}",
                "_description": f"Description for Test Equipment {i}",
                "_equipmentType": "Test" if i % 2 == 0 else "Misc"
            } for i in range(5)
        ]

        added_equipment = []
        for equipment in equipment_to_add:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": equipment,
                "key": "",
                "options": {}
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/invoke/addEquipment", 
                    headers=self.headers, 
                    data=json.dumps(payload)
                )
                response.raise_for_status()
                added_equipment.append(equipment)
                self.added_equipment_ids.append(equipment['_id'])
                print(f"Added Equipment: {equipment['_equipment_name']}")
            except requests.exceptions.RequestException as e:
                print(f"Error adding equipment: {e}")
        
        return added_equipment

    def test_get_all_equipment(self, test_iterations=3):
        """
        Test retrieving all equipment multiple times.
        
        :param test_iterations: Number of times to call getAllEquipment
        :return: List of responses
        """
        print("\n--- Testing Get All Equipment ---")
        results = []

        # Prepare equipment before testing
        prepared_equipment = self.prepare_equipment_before_test()

        for iteration in range(test_iterations):
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {},
                "key": "",
                "options": {}
            }
            
            try:
                # Make the API request
                start_time = datetime.datetime.now()
                response = requests.post(
                    f"{self.base_url}/invoke/getAllEquipment", 
                    headers=self.headers, 
                    data=json.dumps(payload)
                )
                
                # Raise an exception for HTTP errors
                response.raise_for_status()
                
                end_time = datetime.datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                # Parse the response
                response_json = response.json()
                
                # Detailed analysis of the response
                result_entry = {
                    "iteration": iteration + 1,
                    "response_time": response_time,
                    "total_equipment": len(response_json.get('data', [])) if isinstance(response_json, dict) else 0,
                    "full_response": response_json
                }
                
                # Validate response against prepared equipment
                prepared_names = [eq['_equipment_name'] for eq in prepared_equipment]
                retrieved_names = []
                if isinstance(response_json, dict) and 'data' in response_json:
                    retrieved_names = [eq.get('equipment_names', []) for eq in response_json['data']]
                    retrieved_names = [name for sublist in retrieved_names for name in sublist]
                
                result_entry['all_prepared_equipment_found'] = all(
                    name in retrieved_names for name in prepared_names
                )
                
                results.append(result_entry)
                
                # Print detailed information
                print(f"\nIteration {iteration + 1}:")
                print(f"Response Time: {response_time:.4f} seconds")
                print(f"Total Equipment Found: {result_entry['total_equipment']}")
                print(f"All Prepared Equipment Found: {result_entry['all_prepared_equipment_found']}")
                print("Full Response:")
                print(json.dumps(response_json, indent=2))
                
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving all equipment (Iteration {iteration + 1}): {e}")
                if hasattr(e, 'response'):
                    print(f"Response content: {e.response.text}")
                results.append({
                    "iteration": iteration + 1,
                    "error": str(e)
                })
        
        return results

    def cleanup_equipment(self):
        """
        Remove all equipment that was added during the test.
        """
        print("\n--- Cleaning Up Test Equipment ---")
        removal_results = []

        for equipment_id in self.added_equipment_ids:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {
                    "_id": equipment_id,
                    "_removalReason": "Test cleanup"
                },
                "key": "",
                "options": {}
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/invoke/removeEquipment", 
                    headers=self.headers, 
                    data=json.dumps(payload)
                )
                response.raise_for_status()
                
                removal_results.append({
                    "equipment_id": equipment_id,
                    "status": "Removed Successfully"
                })
                print(f"Removed Equipment ID: {equipment_id}")
            
            except requests.exceptions.RequestException as e:
                removal_results.append({
                    "equipment_id": equipment_id,
                    "status": "Removal Failed",
                    "error": str(e)
                })
                print(f"Failed to remove Equipment ID {equipment_id}: {e}")
        
        return removal_results

    def run_get_all_equipment_test(self):
        """
        Run get all equipment test with cleanup.
        """
        print("=== Starting Get All Equipment Test ===")
        
        try:
            # Run the test
            test_results = self.test_get_all_equipment()
            
            # Cleanup equipment after test
            cleanup_results = self.cleanup_equipment()
            
            print("\n=== Get All Equipment Test Complete ===")
            return {
                "test_results": test_results,
                "cleanup_results": cleanup_results
            }
        
        except Exception as e:
            print(f"An error occurred during the test: {e}")
            
            # Attempt cleanup even if test fails
            try:
                cleanup_results = self.cleanup_equipment()
                print("Cleanup completed after test failure.")
            except Exception as cleanup_error:
                print(f"Cleanup also failed: {cleanup_error}")
            
            raise

def main():
    # Replace with your actual base URL
    BASE_URL = "http://127.0.0.1:5000/api/v1/namespaces/default/apis/equip_manage"
    
    # Initialize and run tests
    test_runner = GetAllEquipmentTest(BASE_URL)
    test_results = test_runner.run_get_all_equipment_test()

if __name__ == "__main__":
    main()