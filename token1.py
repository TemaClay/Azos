import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "Наталия"
PASSWORD = "#P21v0!D"
EQUIPMENT_ENDPOINT = "/api/equipment/"
JSON_FILE = "temp.json"

def get_jwt_token():
    """Get JWT token from the authentication endpoint"""
    url = f"{BASE_URL}/api/token/"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {str(e)}")
        return None

def post_equipment_data(token):
    """Post equipment data using the JWT token"""
    url = f"{BASE_URL}{EQUIPMENT_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        response = requests.post(url, json=json_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except FileNotFoundError:
        print(f"Error: File {JSON_FILE} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {JSON_FILE}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error posting equipment data: {str(e)}")
        return None

def main():
    print("Getting JWT token...")
    token_data = get_jwt_token()
    
    if not token_data or 'access' not in token_data:
        print("Failed to obtain access token")
        if token_data:
            print("Response:", token_data)
        input("Press Enter to exit...")
        sys.exit(1)
    
    access_token = token_data['access']
    print(f"Successfully obtained access token: {access_token}")
    
    print("\nMaking API request with the token...")
    result = post_equipment_data(access_token)
    
    if result:
        print("Successfully posted equipment data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Failed to post equipment data")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
