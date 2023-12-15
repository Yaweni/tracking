import requests
import platform
import getpass
import json
import time
import psutil

# Replace 'your_server_address' with the actual address of your Flask server
SERVER_URL = 'http://localhost:5000/update_status'
software_list=['chrome.exe']
def get_computer_name():
    return platform.node()

def get_username():
    return getpass.getuser()

def get_software_status(software_list):
    software_statuses=[]
    for software in software_list:
        status = software in (p.name() for p in psutil.process_iter())
        sof_tup=(software,status)
        software_statuses.append(sof_tup)

    return software_statuses

def send_status_to_server(computer_name, username, software_statuses):
    payload = {
        'computer_name': computer_name,
        'username': username,
        'software_status': software_statuses
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print('Status sent successfully.')
        else:
            print(f'Error sending status. Status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    while True:
        computer_name = get_computer_name()
        username = get_username()
        software_statuses = get_software_status()
        send_status_to_server(computer_name, username, software_statuses)
        # Sleep for 5 minutes before sending the next update
        time.sleep(300)
