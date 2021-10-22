from logging import root
import os
from dotenv import load_dotenv
import requests
import json
import getpass

load_dotenv()

username = os.getenv('KEYCLOAK_USERNAME')
password = os.getenv('KEYCLOAK_PASSWORD')
rooturl = os.getenv('KEYCLOAK_ROOTURL')
realm = os.getenv('KEYCLOAK_REALM')
starter_password = os.getenv('STARTER_PASSWORD')

def getAccessToken():
    # Grab access token from Keycloak

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
    'username': username,
    'password': password,
    'grant_type': 'password',
    'client_id': 'admin-cli'
    }

    response = requests.post(rooturl + '/auth/realms/'+ realm +'/protocol/openid-connect/token', data=data, headers=headers)

    return json.loads(response.text)['access_token']


def getIdByUsername(username):
    headers = {'Authorization': 'Bearer ' + getAccessToken()}
    response = requests.get(rooturl + "/auth/admin/realms/" + realm + "/users?username=" + username, headers=headers)

    return json.loads(response.text)[0]["id"]


def createUser(has_temporary_password = True):
    user = input('Enter the desired username: ')
    first_name = input('First Name: ')
    last_name = input('Last Name: ')
    email = input('E-Mail: ')
    creds = starter_password
    data = '{"firstName":"' + first_name + '","lastName":"' + last_name + '", "email":"' + email + '", "enabled":"true", "username":"' + user + '","credentials":[{"type":"password","value":"' + creds + '","temporary":"true"}]}'

    if(has_temporary_password == False):
        creds = getpass.getpass('Password: ')
        data = '{"firstName":"' + first_name + '","lastName":"' + last_name + '", "email":"' + email + '", "enabled":"true", "username":"' + user + '","credentials":[{"type":"password","value":"' + creds + '","temporary":"false"}]}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getAccessToken()
    }

    print("Creating user...")
    response = requests.post(rooturl + '/auth/admin/realms/' + realm + '/users', data=data, headers=headers)

    return response.status_code


def deleteUser():
    user = input("\nEnter username (Once you hit Enter there will be no turning back!): ")
    headers = {'Authorization': 'Bearer ' + getAccessToken()}
    delete_response = requests.delete(rooturl + "/auth/admin/realms/" + realm + "/users/" + getIdByUsername(user), headers=headers)
    
    return delete_response.status_code


def resetUserPassword():
    user = input("\nEnter username (Once you hit Enter there will be no turning back!): ")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getAccessToken()
    }
    data = '{"type":"password","temporary":"true","value":"' + starter_password + '"}'
    change_response = requests.put(rooturl + "/auth/admin/realms/" + realm + "/users/" + getIdByUsername(user) + "/reset-password", headers=headers, data=data)

    return change_response.status_code


def initMenu():
    print("\nPlease choose an option: \n")
    while True:
        sel = input("(1) Create a new user\n(2) Delete an existing user\n(3) Set user back to starter password\n(0) Test connection to keycloak\n(q) Quit\n\n > ")
        if (sel not in {"1", "2", "3", "0", "q"}):
            print("Please enter a valid option!\n")
        else:
            break

    if(sel == "q"):
        exit()

    elif (sel == "1"):
        while True:
            r = input("\nWould you like to set a temporary starter password? (y/n) ")
            if (r not in {"y", "n"}):
                print("Please enter a valid option!")
            else:
                break

        if (r == "y"):
            if (createUser() == 201):
                print("Done!")
                initMenu()
            else:
                print("There was an error while creating a new user.")
        elif (r == "n"):
            if (createUser(False) == 201):
                print("Done!")
                initMenu()
            else:
                print("There was an error while creating a new user.")

    elif (sel == "2"):
        if (deleteUser() == 204):
                print("Done!")
                initMenu()
        else:
            print("There was an error while deleting the user.")

    elif (sel == "3"):
        if (resetUserPassword() == 204):
                print("Done!")
                initMenu()
        else:
            print("There was an error while deleting the user.")

    elif (sel == "0"):
        try:
            getAccessToken()
            print("\nConnected to Keycloak successfully!")
        except:
            print("\nThere was an error connecting to Keycloak!")
        finally:
            initMenu()

print(" _                   _             _                                                       \n| |                 | |           | |                                                      \n| | _____ _   _  ___| | ___   __ _| | ________ _ __ ___   __ _ _ __   __ _  __ _  ___ _ __ \n| |/ / _ \ | | |/ __| |/ _ \ / _` | |/ /______| '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|\n|   <  __/ |_| | (__| | (_) | (_| |   <       | | | | | | (_| | | | | (_| | (_| |  __/ |   \n|_|\_\___|\__, |\___|_|\___/ \__,_|_|\_\      |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|   \n           __/ |                                                            __/ |          \n          |___/                                                            |___/           ")
initMenu()
