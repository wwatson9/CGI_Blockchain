import requests
import uuid
import json

class EquipmentManagementTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.owner_key = "0xf85079078afdf384d84bf54a42bc7c75d39b968d"
        # Adding a non-owner key for testing unauthorized access
        self.non_owner_key = "0xfdc8671a3e511bd0e751f77be022ee072be25da7"
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

    def test_get_owner(self):
        """Test retrieving the contract owner."""
        print("\n--- Testing Get Owner ---")
        payload = {
            "idempotencyKey": self.generate_idempotency_key(),
            "input": {},
            "key": self.owner_key,
            "options": {}
        }
        
        response = self.make_request("/invoke/owner", data=payload)
        print("Contract Owner Response:", response)
        return response

    def test_add_equipment(self):
        """Test adding new equipment (owner-only)."""
        print("\n--- Testing Add Equipment ---")
        test_cases = [
            # Expanded equipment addition with more details
            {
                "_id": "9",
                "_equipment_name": "High-End Laptop",
                "_description": "MacBook Pro M2 Max, 32GB RAM, 1TB SSD",
                "_equipmentType": "Computing"
            },
            # Another equipment item with different characteristics
            {
                "_id": "10",
                "_equipment_name": "Professional Camera",
                "_description": "Sony Alpha A7 III Mirrorless Camera",
                "_equipmentType": "Photography"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": self.owner_key,  # Only owner can add equipment
                "options": {}
            }
            
            response = self.make_request("/invoke/addEquipment", data=payload)
            results.append(response)
            print(f"Added Equipment: {case['_equipment_name']} - Response: {response}")
        
        return results

    def test_unauthorized_add_equipment(self):
        """Test adding equipment by a non-owner (should fail)."""
        print("\n--- Testing Unauthorized Equipment Addition ---")
        test_case = {
            "_id": "11",
            "_equipment_name": "Unauthorized Equipment",
            "_description": "This should not be added by a non-owner",
            "_equipmentType": "Test"
        }

        payload = {
            "idempotencyKey": self.generate_idempotency_key(),
            "input": test_case,
            "key": self.non_owner_key,  # Non-owner key
            "options": {}
        }
        
        response = self.make_request("/invoke/addEquipment", data=payload)
        print("Unauthorized Equipment Addition Attempt - Response:", response)
        return response

    def test_checkout_equipment(self):
        """Test checking out equipment."""
        print("\n--- Testing Checkout Equipment ---")
        test_cases = [
            {
                "_id": "9",
                "_borrowerName": "Emily Rodriguez"
            },
            {
                "_id": "10", 
                "_borrowerName": "Michael Chen"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": "",  # Regular users can checkout
                "options": {}
            }
            
            response = self.make_request("/invoke/checkoutEquipment", data=payload)
            results.append(response)
            print(f"Checked Out Equipment ID {case['_id']} by {case['_borrowerName']} - Response: {response}")
        
        return results

    def test_return_equipment(self):
        """Test returning equipment."""
        print("\n--- Testing Return Equipment ---")
        test_cases = ["9", "10"]

        results = []
        for equipment_id in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {"_id": equipment_id},
                "key": "",  # Borrower returns
                "options": {}
            }
            
            response = self.make_request("/invoke/returnEquipment", data=payload)
            results.append(response)
            print(f"Returned Equipment ID {equipment_id} - Response: {response}")
        
        return results

    def test_remove_equipment(self):
        """Test removing equipment (owner-only)."""
        print("\n--- Testing Remove Equipment ---")
        test_cases = [
            {
                "_id": "9", 
                "_removalReason": "Depreciated"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": self.owner_key,  # Only owner can remove equipment
                "options": {}
            }
            
            response = self.make_request("/invoke/removeEquipment", data=payload)
            results.append(response)
            print(f"Removed Equipment ID {case['_id']} - Response: {response}")
        
        return results

    def test_unauthorized_remove_equipment(self):
        """Test removing equipment by a non-owner (should fail)."""
        print("\n--- Testing Unauthorized Equipment Removal ---")
        test_case = {
            "_id": "10", 
            "_removalReason": "Unauthorized Attempt"
        }

        payload = {
            "idempotencyKey": self.generate_idempotency_key(),
            "input": test_case,
            "key": self.non_owner_key,  # Non-owner key
            "options": {}
        }
        
        response = self.make_request("/invoke/removeEquipment", data=payload)
        print("Unauthorized Equipment Removal Attempt - Response:", response)
        return response

    def test_get_equipment_details(self):
        """Test retrieving equipment details."""
        print("\n--- Testing Get Equipment Details ---")
        test_cases = ["10"]  # Using remaining equipment ID

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
        """Test updating equipment status (owner-only)."""
        print("\n--- Testing Update Equipment Status ---")
        test_cases = [
            {
                "_id": "10", 
                "_newStatus": "Maintenance",
                "_statusReason": "Routine inspection"
            }
        ]

        results = []
        for case in test_cases:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": case,
                "key": self.owner_key,  # Only owner can update status
                "options": {}
            }
            
            response = self.make_request("/invoke/updateEquipmentStatus", data=payload)
            results.append(response)
            print(f"Updated Status for Equipment ID {case['_id']} - Response: {response}")
        
        return results

    def test_unauthorized_status_update(self):
        """Test updating equipment status by a non-owner (should fail)."""
        print("\n--- Testing Unauthorized Equipment Status Update ---")
        test_case = {
            "_id": "10", 
            "_newStatus": "Lost",
            "_statusReason": "Unauthorized Attempt"
        }

        payload = {
            "idempotencyKey": self.generate_idempotency_key(),
            "input": test_case,
            "key": self.non_owner_key,  # Non-owner key
            "options": {}
        }
        
        response = self.make_request("/invoke/updateEquipmentStatus", data=payload)
        print("Unauthorized Equipment Status Update Attempt - Response:", response)
        return response

    def run_full_test_suite(self):
        """Run all test methods in sequence."""
        print("=== Starting Full Equipment Management System Test Suite ===")
        results = {
            'get_owner': self.test_get_owner(),
            'add_equipment': self.test_add_equipment(),
            'unauthorized_add_equipment': self.test_unauthorized_add_equipment(),
            'checkout_equipment': self.test_checkout_equipment(),
            'return_equipment': self.test_return_equipment(),
            'remove_equipment': self.test_remove_equipment(),
            'unauthorized_remove_equipment': self.test_unauthorized_remove_equipment(),
            'get_equipment_details': self.test_get_equipment_details(),
            'get_all_equipment': self.test_get_all_equipment(),
            'update_equipment_status': self.test_update_equipment_status(),
            'unauthorized_status_update': self.test_unauthorized_status_update()
        }
        print("\n=== Test Suite Complete ===")
        return results

def main():
    # Replace with your actual base URL
    BASE_URL = "http://127.0.0.1:5000/api/v1/namespaces/default/apis/owner"
    
    # Initialize and run tests
    test_runner = EquipmentManagementTest(BASE_URL)
    test_results = test_runner.run_full_test_suite()

if __name__ == "__main__":
    main()