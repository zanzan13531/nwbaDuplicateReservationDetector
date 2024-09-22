Instructions for main_apiVersion.py, the browser version hasn't been written yet.

Files login.json and tokens.json need to be created.

login.json should look like:

    {
        "client_id": "your_username_here",
        "client_secret": "your_password_here"
    }

tokens.json should look like:

    {
        "access_token": "token",
        "refresh_token": "token",
        "expires_at": 0
    }

First time running the data in tokens.json can be garbage data. 

.gitignore set up to prevent these two files from being shared.

API reference:
https://docs.partners.daxko.com/openapi/ZenPlanner/v1/#tag/Classes/operation/get-class-attendances-by-classId