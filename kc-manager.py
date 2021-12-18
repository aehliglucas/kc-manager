import os
import subprocess
from dotenv import load_dotenv
import requests
import json
import getpass
from consolemenu import *
from consolemenu.items import *
import time
import socket

load_dotenv()

username = os.getenv('KEYCLOAK_USERNAME')
password = os.getenv('KEYCLOAK_PASSWORD')
rooturl = os.getenv('KEYCLOAK_ROOTURL')
realm = os.getenv('KEYCLOAK_REALM')
starter_password = os.getenv('STARTER_PASSWORD')
host = rooturl.split("//")[1]
port = host.split(":")[1]

def ping():
    print("\nChecking TCP connection to " + host + " .... ", end='')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if (s.connect_ex((host.split(":")[0], int(port))) == 0):
        return True
    else:
        return False

def startup():
    clear_terminal()
    print(" _                   _             _                                                       \n| |                 | |           | |                                                      \n| | _____ _   _  ___| | ___   __ _| | ________ _ __ ___   __ _ _ __   __ _  __ _  ___ _ __ \n| |/ / _ \ | | |/ __| |/ _ \ / _` | |/ /______| '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|\n|   <  __/ |_| | (__| | (_) | (_| |   <       | | | | | | (_| | | | | (_| | (_| |  __/ |   \n|_|\_\___|\__, |\___|_|\___/ \__,_|_|\_\      |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|   \n           __/ |                                                            __/ |          \n          |___/                                                            |___/           ")
    if (ping() == True):
        print("[ " + '\033[0;32m' + "OK" + '\033[0m' + " ]")
    else:
        print("[ " + '\033[1;31m' + "FAIL" + '\033[0m' + " ]")
        print("Failed to reach " + host + " on port " + port + "/tcp. Please check your .env-settings and try again.")
        exit()
    time.sleep(1)
    realm = input("What realm would you like to work on? \n > ")
    #initMenu()

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
        print("\nConnected to Keycloak successfully! Press q to return to menu")
    except:
        print("\nThere was an error connecting to Keycloak! Press q to return to menu")
    
    while (input(">") != "q"):
        print("Only 'q' is an option!")
    return

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

    if (response.status_code == 201):
        print("User created successfully!\nPress q to return to menu")
    else:
        print("There was an error in user creation! Keycloak responded with " + response.text + "\nPress q to return to menu")
    
    while (input(">") != "q"):
        print("Only 'q' is an option!")
    return


def deleteUser():
    user = input("\nEnter username (Once you hit Enter there will be no turning back!): ")
    headers = {'Authorization': 'Bearer ' + getAccessToken()}
    delete_response = requests.delete(rooturl + "/auth/admin/realms/" + realm + "/users/" + getIdByUsername(user), headers=headers)
    

    if (delete_response.status_code == 204):
        print("User deleted successfully!\nPress q to return to menu")
    else:
        print("There was an error in user deletion! Keycloak responded with " + delete_response.text + "\nPress q to return to menu")

    while (input(">") != "q"):
        print("Only 'q' is an option!")
    return


def resetUserPassword():
    user = input("\nEnter username (Once you hit Enter there will be no turning back!): ")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getAccessToken()
    }
    data = '{"type":"password","temporary":"true","value":"' + starter_password + '"}'
    change_response = requests.put(rooturl + "/auth/admin/realms/" + realm + "/users/" + getIdByUsername(user) + "/reset-password", headers=headers, data=data) 

    if (change_response.status_code == 204):
        print("Password was reset successfully!\nPress q to return to menu")
    else:
        print("There was an error in resetting the password! Keycloak responded with " + change_response.text + "\nPress q to return to menu")

    while (input(">") != "q"):
        print("Only 'q' is an option!")
    return


# Clients

def getClients():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getAccessToken()
    }

    show_response = requests.get(rooturl + "/auth/admin/realms/" + realm + "/clients/", headers=headers)
    if (show_response.status_code == 200):
        file = open('clients.json', 'w')
        file.write(json.dumps(json.loads(show_response.text), indent=4, sort_keys=True))
        print("The client list has been printed to 'clients.txt' in the current folder.\nPress q to return to menu")
    else:
        print("There was an error while requesting the client list! Keycloak responded with " + show_response.text + "\nPress q to return to menu")

    while (input(">") != "q"):
        print("Only 'q' is an option!")
    return


# Menu

def initMenu():
    # Menu initialization
    menu = ConsoleMenu("Home", "Please choose a management option:")
    sub_users = ConsoleMenu("User Management")
    sub_clients = ConsoleMenu("Client Management")
    
    # Submenu Triggers
    sub_call_users = SubmenuItem("Users", sub_users, menu=menu)
    sub_call_clients = SubmenuItem("Clients", sub_clients, menu=menu)

    # User Items
    func_user_create = FunctionItem("Create a new User", createUser, menu=sub_call_users)
    func_user_delete = FunctionItem("Delete a User", deleteUser, menu=sub_call_users)
    func_user_resetpw = FunctionItem("Reset Password", resetUserPassword, menu=sub_call_users)
    sub_users.append_item(func_user_create)
    sub_users.append_item(func_user_delete)
    sub_users.append_item(func_user_resetpw)

    func_client_get = FunctionItem("Print a list of all clients into a json-file", getClients, menu=sub_call_clients)
    sub_clients.append_item(func_client_get)

    # Menu building
    func_connect_check = FunctionItem("Check connection to keycloak", checkConnection, menu=menu)
    menu.append_item(sub_call_users)
    menu.append_item(sub_call_clients)
    menu.append_item(func_connect_check)
    menu.show()

startup()