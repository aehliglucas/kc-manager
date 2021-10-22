## kc-manager
A lightweight console based python app to manage Keycloak without having a web interface on hand.

## How to use?

**Using KC-Manager is ez! There are just a few steps:**

### Prerequisites

To use kc-manager you need to have python installed on your system. To find out how to install it check the official docs:
https://www.python.org/downloads/

### 1. Cloning the git repo

Run the following command on the host you would like to run kc-manager on: \

```git clone https://github.com/aehliglucas/kc-manager.git```


### 2. Creating the .env

The .env-file is used to set environmental variables like your Keycloak host, usernames and passwords.
To create it you only have to rename the ".env-sample"-file to ".env" and edit it to match your settings.


### 3. Installing dependencies

If you have python installed you just have to run \

```python -m pip install -r requirements.txt``` \

to install all needed dependencies.


### 4. Running the script

```python kc-manager.py```


## And you're all set!
