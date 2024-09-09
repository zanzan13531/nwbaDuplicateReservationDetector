import json
import time
import requests
import pytz
from datetime import datetime, timedelta


############################ Authentication ############################

# Client credentials and scope
CLIENT_ID = ""
SCOPE = "read:classes"  # Set this to scope, still not sure what this should be
ACCESS_TOKEN = ""
REFRESH_TOKEN = ""
EXPIRES_AT = 0
AUTH_URL = "https://api.partners.daxko.com/auth/token"

# Load the client ID from a file
with open ("login.json", "r") as f:
    data = json.load(f)
    CLIENT_ID = data["client_id"]

# Load the token data from a file
with open ("tokens.json", "r") as f:
    data = json.load(f)
    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data["refresh_token"]
    EXPIRES_AT = data["expires_at"]

# Write the current token data to a file for later use.
def write_tokens_to_file():
    with open("login.json", "w") as f:
        json.dump({
            "access_token": ACCESS_TOKEN,
            "refresh_token": REFRESH_TOKEN,
            "expires_at": EXPIRES_AT
        }, f)

# Get a new access token using the client credentials.
def get_new_token():
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

# Attempt to refresh the access token using the refresh token.
# If the refresh token is expired, re-authenticate using client credentials.
def refresh_token():
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

# Check if the access token is expired or about to expire, and refresh if needed.
def check_token_and_refresh():
    if time.time() > EXPIRES_AT - 60:  # Refresh 1 minute before expiry
        print("Token expired or about to expire, refreshing...")
        refresh_token()


############################ API Call Functions ############################

# Make an API call, ensuring the token is valid.
def make_api_call(url):
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

# Function to get the list of participants with their reservation times
def get_reservation_times(class_info):
    users = {}

    for class_id, start_time in class_info.items():
        # For each class, get the participants
        url = f"https://api.partners.daxko.com/api/v1/classes/{class_id}/participants"
        data = make_api_call(url)
        
        if data:
            class_participants = extract_participant_info(data)
            
            # Add the start time to each participant's reservation list
            for user_name in class_participants:
                if user_name in users:
                    users[user_name].append(start_time)
                else:
                    users[user_name] = [start_time]

    return users


############################ Data Processing ############################

# Function to extract participant information
def extract_participant_info(data):
    participants = []
    
    # Loop through each element in the 'elements' array
    for element in data.get('elements', []):
        person = element.get('person', {})
        
        # Extract firstName, lastName, and id
        first_name = person.get('firstName', '')
        last_name = person.get('lastName', '')
        person_id = person.get('id', '')
        
        # Format the name as "firstname_lastname_id"
        if first_name and last_name and person_id:
            formatted_name = f"{first_name}_{last_name}_{person_id}"
            participants.append(formatted_name)
    
    return participants

# Function to extract class information
def extract_class_info(data):
    classes = {} #format of { class_id: start_time }

    # Loop through each class in the response data
    for class_element in data.get("elements", []):
        class_id = class_element.get("id")  # Get the class ID
        start_time = class_element.get("startDate")  # Get the start time in UTC

        # Add to the dictionary
        if class_id and start_time:
            classes[class_id] = start_time

    return classes

# Function to find reservation rule violators
def reservation_violators(reservations):
    violators = {}
    
    for user, times in reservations.items():
        # Create a dictionary to track reservations per day
        reservations_per_day = {}
        
        for time in times:
            # Convert time to a date (assuming ISO 8601 format)
            date = datetime.fromisoformat(time.replace("Z", "+00:00")).date()
            
            # Count the number of reservations on this date
            if date in reservations_per_day:
                reservations_per_day[date] += 1
            else:
                reservations_per_day[date] = 1
        
        # Check if the user has more than 1 reservation on any day or more than 2 reservations in total
        if len(times) > 2 or any(count > 1 for count in reservations_per_day.values()):
            violators[user] = times
    
    return violators

# Function to print violators and write to a file
def print_and_save_violators(violators, begin_date, end_date, isweekend):
    # Get the current timestamp to add to the filename
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Generate the filename based on the begin_date, end_date, and current timestamp
    filename = ""
    if (isweekend):
        filename = f"violators_{begin_date[:10]}_{end_date[:10]}_weekend_{current_timestamp}.txt"
    else:
        filename = f"violators_{begin_date[:10]}_{end_date[:10]}_weekdays_{current_timestamp}.txt"

    # Open the file for writing
    with open(filename, 'w') as file:
        for user, times in violators.items():
            # Print to console
            print(f"{user}:")
            # Write user to file
            file.write(f"{user}:\n")

            # Convert all times to PST and format them
            formatted_times = []
            for time in times:
                # Assuming 'time' is a string in ISO 8601 format (UTC)
                utc_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
                pst = pytz.timezone('America/Los_Angeles')  # PST timezone
                pst_time = utc_time.astimezone(pst)
                formatted_time = pst_time.strftime("%Y-%m-%d %I:%M %p %Z")
                formatted_times.append(formatted_time)

            # Join all formatted times into a single string and print them
            formatted_time_str = ", ".join(formatted_times)
            print(formatted_time_str)
            
            # Write times to file
            file.write(f"  {formatted_time_str}\n")
    
    print(f"\nResults written to {filename}")


############################ Execution ############################

refresh_token()  # Ensure the token is valid before starting

gotWeekdayData = False
gotWeekendData = False

# Define the API endpoint
api_url = "https://api.partners.daxko.com/api/v1/classes"

# time calculations
utc = pytz.utc
pst = pytz.timezone('America/Los_Angeles')
current_date_pst = datetime.now(pst)
# Calculate the Monday of this week (weekday() returns 0 for Monday)
monday = current_date_pst - timedelta(days=current_date_pst.weekday())

# Set begin and end dates for weekdays (Monday to Friday)
begin_date_weekdays = monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
end_date_weekdays = (monday + timedelta(days=4)).replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

# Set begin and end dates for the weekend (Saturday to Sunday)
begin_date_weekend = (monday + timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
end_date_weekend = (monday + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

# Define the query parameters for weekdays
params_weekdays = {
    "beginDate": begin_date_weekdays,  # Monday to Friday
    "endDate": end_date_weekdays
} # IMPORTANT, MAYBE NEED TO ALSO FILTER LOCATION TO NWBA BELLEVUE

# Define the query parameters for the weekend
params_weekend = {
    "beginDate": begin_date_weekend,  # Saturday to Sunday
    "endDate": end_date_weekend
}

# Set the headers with the Authorization token
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Fetch classes for weekdays
response_weekdays = requests.get(api_url, headers=headers, params=params_weekdays)

# Check if the request was successful for weekdays
if response_weekdays.status_code == 200:
    response_weekdays = response_weekdays.json()
    gotWeekdayData = True
    # print("Classes for the weekdays (Monday to Friday):", classes_weekdays)
else:
    print(f"Failed to retrieve weekdays classes. Status Code: {response_weekdays.status_code}")
    print("Response:", response_weekdays.text)

# Fetch classes for the weekend
response_weekend = requests.get(api_url, headers=headers, params=params_weekend)

# Check if the request was successful for the weekend
if response_weekend.status_code == 200:
    response_weekend = response_weekend.json()
    gotWeekendData = True
    # print("Classes for the weekend (Saturday to Sunday):", classes_weekend)
else:
    print(f"Failed to retrieve weekend classes. Status Code: {response_weekend.status_code}")
    print("Response:", response_weekend.text)

if (gotWeekdayData):
    class_id_list = extract_class_info(response_weekdays)
    del response_weekdays
    reservation_dict = get_reservation_times(class_id_list)
    del class_id_list
    violators = reservation_violators(reservation_dict)

    print("Weekday Violoators: ")
    print_and_save_violators(violators, begin_date_weekdays, end_date_weekdays, False)

if (gotWeekdayData):
    class_id_list = extract_class_info(response_weekend)
    del response_weekend
    reservation_dict = get_reservation_times(class_id_list)
    del class_id_list
    violators = reservation_violators(reservation_dict)

    print("Weekend Violoators: ")
    print_and_save_violators(violators, begin_date_weekend, end_date_weekend, True)

# Can also presumably write code to delete the reservations of the violators