import requests
import uuid
import json

class EquipmentManagementTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def generate_idempotency_key(self):
        """Generate a unique idempotency key for each request."""
        return str(uuid.uuid4())

    def make_request(self, endpoint, method='post', data=None):
        """
        Helper method to make API requests with error handling.
        
        :param endpoint: API endpoint to call
        :param method: HTTP method (default: post)
        :param data: Request payload
        :return: Response JSON
        """
        full_url = f"{self.base_url}{endpoint}"
        
        try:
            if method.lower() == 'post':
                response = requests.post(full_url, 
                                         headers=self.headers, 
                                         data=json.dumps(data))
            elif method.lower() == 'get':
                response = requests.get(full_url, 
                                        headers=self.headers, 
                                        params=data)
            
            # Raise an exception for HTTP errors
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in {endpoint}: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return None

    def test_add_equipment(self):
        """Test adding new equipment."""
        print("\n--- Testing Add Equipment ---")
        test_cases = [
            # Basic equipment addition
            {
                "_id": "1",
                "_equipment_name": "Laptop",
                "_description": "Dell XPS Laptop",
                "_equipmentType": "Electronics"
            },
            # Another equipment item
            {
                "_id": "2",
                "_equipment_name": "Projector",
                "_description": "4K Conference Room Projector",
                "_equipmentType": "Presentation"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/addEquipment", data=payload)
            results.append(response)
            print(f"Added Equipment: {case['_equipment_name']} - Response: {response}")
        
        return results

    def test_checkout_equipment(self):
        """Test checking out equipment."""
        print("\n--- Testing Checkout Equipment ---")
        test_cases = [
            {
                "_id": "1",
                "_borrowerName": "John Doe"
            },
            {
                "_id": "2", 
                "_borrowerName": "Jane Smith"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/checkoutEquipment", data=payload)
            results.append(response)
            print(f"Checked Out Equipment ID {case['_id']} by {case['_borrowerName']} - Response: {response}")
        
        return results

    def test_return_equipment(self):
        """Test returning equipment."""
        print("\n--- Testing Return Equipment ---")
        test_cases = ["1", "2"]

        results = []
        for equipment_id in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {"_id": equipment_id},
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/returnEquipment", data=payload)
            results.append(response)
            print(f"Returned Equipment ID {equipment_id} - Response: {response}")
        
        return results

    def test_remove_equipment(self):
        """Test removing equipment."""
        print("\n--- Testing Remove Equipment ---")
        test_cases = [
            {
                "_id": "1", 
                "_removalReason": "Obsolete"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/removeEquipment", data=payload)
            results.append(response)
            print(f"Removed Equipment ID {case['_id']} - Response: {response}")
        
        return results

    def test_get_equipment_details(self):
        """Test retrieving equipment details."""
        print("\n--- Testing Get Equipment Details ---")
        test_cases = ["2"]  # Using remaining equipment ID

        results = []
        for equipment_id in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {"_id": equipment_id},
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/getEquipmentDetails", data=payload)
            results.append(response)
            print(f"Equipment Details for ID {equipment_id} - Response: {response}")
        
        return results

    def test_get_all_equipment(self):
        """Test retrieving all equipment."""
        print("\n--- Testing Get All Equipment ---")
        payload = {
            "idempotencyKey": self.generate_idempotency_key(),
            "input": {},
            "key": "",
            "options": {}
        }
        
        response = self.make_request("/invoke/getAllEquipment", data=payload)
        print("All Equipment Response:", response)
        return response

    def test_update_equipment_status(self):
        """Test updating equipment status."""
        print("\n--- Testing Update Equipment Status ---")
        test_cases = [
            {
                "_id": "2", 
                "_newStatus": "Maintenance",
                "_statusReason": "Routine check"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": "",
                "options": {}
            }
            
            response = self.make_request("/invoke/updateEquipmentStatus", data=payload)
            results.append(response)
            print(f"Updated Status for Equipment ID {case['_id']} - Response: {response}")
        
        return results

    def run_full_test_suite(self):
        """Run all test methods in sequence."""
        print("=== Starting Full Equipment Management System Test Suite ===")
        results = {
            'add_equipment': self.test_add_equipment(),
            'checkout_equipment': self.test_checkout_equipment(),
            'return_equipment': self.test_return_equipment(),
            'remove_equipment': self.test_remove_equipment(),
            'get_equipment_details': self.test_get_equipment_details(),
            'get_all_equipment': self.test_get_all_equipment(),
            'update_equipment_status': self.test_update_equipment_status()
        }
        print("\n=== Test Suite Complete ===")
        return results

def main():
    # Replace with your actual base URL
    BASE_URL = "http://127.0.0.1:5000/api/v1/namespaces/default/apis/equip_manage"
    
    # Initialize and run tests
    test_runner = EquipmentManagementTest(BASE_URL)
    test_results = test_runner.run_full_test_suite()

if __name__ == "__main__":
    main()