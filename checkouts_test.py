import requests
import uuid
import json

class UserCheckoutsTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def generate_idempotency_key(self):
        """Generate a unique idempotency key for each request."""
        return str(uuid.uuid4())

    def test_get_user_checkouts(self, test_addresses):
        """
        Test retrieving checkouts for multiple user addresses.
        
        :param test_addresses: List of Ethereum addresses to test
        :return: List of responses for each address
        """
        print("\n--- Testing Get User Checkouts ---")
        results = []

        for address in test_addresses:
            payload = {
                "idempotencyKey": self.generate_idempotency_key(),
                "input": {"_user": address},
                "key": "",
                "options": {}
            }
            
            try:
                # Make the API request
                response = requests.post(
                    f"{self.base_url}/invoke/getUserCheckouts", 
                    headers=self.headers, 
                    data=json.dumps(payload)
                )
                
                # Raise an exception for HTTP errors
                response.raise_for_status()
                
                # Parse and store the response
                response_json = response.json()
                results.append({
                    "address": address,
                    "response": response_json
                })
                
                # Print detailed information
                print(f"User Checkouts for {address}:")
                print(json.dumps(response_json, indent=2))
                
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving checkouts for {address}: {e}")
                if hasattr(e, 'response'):
                    print(f"Response content: {e.response.text}")
                results.append({
                    "address": address,
                    "error": str(e)
                })
        
        return results

    def run_user_checkouts_test(self):
        """
        Run user checkouts test with predefined addresses.
        Include a mix of scenarios:
        1. Address that has checked out equipment
        2. Address that has no checkouts
        3. Multiple addresses
        """
        print("=== Starting User Checkouts Test ===")
        
        # Example Ethereum addresses (replace with actual addresses from your system)
        test_addresses = [
            "0xed3d14cf4e434fb49661f907fa0d63c291f5b40d",  # Example address 1
            "0x90ca4a0c9a834c9ec86db1a93a8a4abe23ed26c4",  # Example address 2
            "0xb5a1c30468774aa476dfbf245c1d710ecb6c547e"   # Another example address
        ]
        
        results = self.test_get_user_checkouts(test_addresses)
        
        print("\n=== User Checkouts Test Complete ===")
        return results

def main():
    # Replace with your actual base URL
    BASE_URL = "http://127.0.0.1:5000/api/v1/namespaces/default/apis/equip_manage"
    
    # Initialize and run tests
    test_runner = UserCheckoutsTest(BASE_URL)
    test_results = test_runner.run_user_checkouts_test()

if __name__ == "__main__":
    main()