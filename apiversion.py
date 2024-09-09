import json
import time
import requests


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

def write_token_to_file():
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

# Initial token acquisition
get_new_token()

# Example API call
api_url = "https://api.partners.daxko.com/v1/some/endpoint"
response_data = make_api_call(api_url)

print(response_data)





# Your API endpoint and data
url = 'https://api.partners.daxko.com/auth/token'
data = {
    "client_id": "<YOUR_CLIENT_ID>",
    "client_secret": "<YOUR_CLIENT_SECRET>",
    "scope": "<CLIENT_SCOPE>",
    "grant_type": "client_credentials"
}

# Send the POST request
response = requests.post(url, json=data)

# Check the response
if response.status_code == 200:
    print("Access token:", response.json().get("access_token"))
else:
    print(f"Failed with status code: {response.status_code}")

