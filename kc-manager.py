import os
from dotenv import load_dotenv
import requests
import json
import getpass
from consolemenu import *
from consolemenu.items import *
import time

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


def checkConnection():
    try:
        getAccessToken()
        print("\nConnected to Keycloak successfully! Returning to menu in 5 seconds...")
    except:
        print("\nThere was an error connecting to Keycloak! Returning to menu in 5 seconds...")
    time.sleep(5)

# Users

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


# Menu

def initMenu():
    # Menu initialization
    menu = ConsoleMenu("Home", "Please choose a management option:")
    sub_users = ConsoleMenu("User Management")
    #sub_groups = ConsoleMenu("Group Management")
    
    # Submenu Triggers
    sub_call_users = SubmenuItem("Users", sub_users, menu=menu)
    #sub_call_groups = SubmenuItem("Groups", sub_groups, menu=menu)

    # User Items
    func_user_create = FunctionItem("Create a new User", createUser, menu=sub_call_users)
    func_user_delete = FunctionItem("Delete a User", deleteUser, menu=sub_call_users)
    func_user_resetpw = FunctionItem("Reset Password", resetUserPassword, menu=sub_call_users)
    sub_users.append_item(func_user_create)
    sub_users.append_item(func_user_delete)
    sub_users.append_item(func_user_resetpw)


    func_connect_check = FunctionItem("Check connection to keycloak", checkConnection, menu=menu)
    menu.append_item(sub_call_users)
    #menu.append_item(sub_call_groups)
    menu.append_item(func_connect_check)
    menu.show()

print(" _                   _             _                                                       \n| |                 | |           | |                                                      \n| | _____ _   _  ___| | ___   __ _| | ________ _ __ ___   __ _ _ __   __ _  __ _  ___ _ __ \n| |/ / _ \ | | |/ __| |/ _ \ / _` | |/ /______| '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|\n|   <  __/ |_| | (__| | (_) | (_| |   <       | | | | | | (_| | | | | (_| | (_| |  __/ |   \n|_|\_\___|\__, |\___|_|\___/ \__,_|_|\_\      |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|   \n           __/ |                                                            __/ |          \n          |___/                                                            |___/           ")
initMenu()
