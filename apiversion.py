import json
import time
import requests


############################ Authentication ############################

# Your client credentials and scope
CLIENT_ID = ""
SCOPE = "<YOUR_SCOPE>"  # Set this to scope, still not sure what this should be
ACCESS_TOKEN = ""
REFRESH_TOKEN = ""
EXPIRES_AT = 0
AUTH_URL = "https://api.partners.daxko.com/auth/token"

with open ("login.json", "r") as f:
    data = json.load(f)
    CLIENT_ID = data["client_id"]

with open ("tokens.json", "r") as f:
    data = json.load(f)
    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data["refresh_token"]
    EXPIRES_AT = data["expires_at"]

def write_tokens_to_file():
    """
    Write the current token data to a file for later use.
    """
    with open("login.json", "w") as f:
        json.dump({
            "access_token": ACCESS_TOKEN,
            "refresh_token": REFRESH_TOKEN,
            "expires_at": EXPIRES_AT
        }, f)

def get_new_token():
    """
    Get a new access token using the client credentials.
    """
    CLIENT_SECRET = "" # load password from login.json
    with open ("login.json", "r") as f:
        data = json.load(f)
        CLIENT_SECRET = data["client_secret"]

    response = requests.post(AUTH_URL, json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,  # Including scope in the request
        "grant_type": "client_credentials"
    })
    
    if response.status_code == 200:
        data = response.json()
        ACCESS_TOKEN = data["access_token"]
        REFRESH_TOKEN = data["refresh_token"]
        EXPIRES_AT = time.time() + data["expires_in"]  # Calculate expiration time
        write_tokens_to_file()
        print("New token acquired")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        raise Exception("Unable to acquire new token")

def refresh_token():
    """
    Attempt to refresh the access token using the refresh token.
    If the refresh token is expired, re-authenticate using client credentials.
    """
    response = requests.post(AUTH_URL, json={
        "client_id": CLIENT_ID,
        "refresh_token": REFRESH_TOKEN,
        "scope": SCOPE,
        "grant_type": "refresh_token"
    })

    if response.status_code == 200:
        data = response.json()
        ACCESS_TOKEN = data["access_token"]
        EXPIRES_AT = time.time() + data["expires_in"]
        write_tokens_to_file()
        print("Token refreshed")
    elif response.status_code == 401:  # Refresh token expired
        print("Refresh token expired, re-authenticating...")
        get_new_token()  # Fall back to full re-authentication
    else:
        print(f"Error refreshing token: {response.status_code}, {response.text}")
        raise Exception("Unable to refresh or re-authenticate")


def check_token_and_refresh():
    """
    Check if the access token is expired or about to expire, and refresh if needed.
    """
    if time.time() > EXPIRES_AT - 60:  # Refresh 1 minute before expiry
        print("Token expired or about to expire, refreshing...")
        refresh_token()


############################ API Calls ############################


def make_api_call(url):
    """
    Make an API call, ensuring the token is valid.
    """
    check_token_and_refresh()  # Ensure the token is valid
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


refresh_token()  # Ensure the token is valid before starting



# Define the API endpoint
api_url = "https://api.partners.daxko.com/api/v1/classes"

# Define the query parameters
params = { # should be 65 classes per week which fits in a page of 100
    "beginDate": "2024-09-01T00:00:00.000Z",  # Example date
    "endDate": "2024-09-07T00:00:00.000Z",    # Example date
    "isDropInAllowed": "true",                # Example boolean
    "isFreeTrialAllowed": "false",            # Example boolean
    "locationId": "c63abd58-73a9-4319-bf54-83dfb1ebef31",  # Example location ID
}

# Set the headers with the Authorization token
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Make the GET request to the API
response = requests.get(api_url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON
    classes_data = response.json()
    print("Classes Data:", classes_data)
else:
    print(f"Failed to retrieve classes. Status Code: {response.status_code}")
    print("Response:", response.text)




