import socket
import subprocess
import argparse
import json

# Define the server address and port
server_address = ('10.129.12.213', 8080)  # Replace 'server_ip' with the actual IP of your server

# Create a socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect(server_address)
   
    client_id = 'client_1'
    client_socket.send(client_id.encode())
   
    greeting_message = client_socket.recv(1024).decode()
    print(greeting_message)

    # Receive parameters from the server
    json_data = client_socket.recv(1024).decode()
    parameters = json.loads(json_data)
    print(f"Received parameters from server: {parameters}")

    # Construct the command to run pre_training.py with the received parameters
    command = [
        "python",  # Replace with the appropriate Python interpreter if needed
        "pre_training_client.py",
        f"--tank_ID={parameters['tank_ID']}",
        f"--max_pretraining_days={parameters['max_pretraining_days']}",
        f"--max_sessions_per_day={parameters['max_sessions_per_day']}",
        f"--stimulus_display_time={parameters['stimulus_display_time']}",
        f"--success_threshold={parameters['success_threshold']}",
        f"--max_session_duration={parameters['max_session_duration']}",
        f"--session_interval={parameters['session_interval']}",
        f"--max_sessions_pretraining={parameters['max_sessions_pretraining']}",
        f"--max_trial_per_session={parameters['max_trial_per_session']}",
        f"--display_neutral_after_time={parameters['display_neutral_after_time']}",
        f"--stimulus_image={parameters['stimulus_image']}",
        f"--neutral_image={parameters['neutral_image']}",
        f"--ROC1_x1={parameters['ROC1_x1']}",
        f"--ROC1_x2={parameters['ROC1_x2']}",
        f"--ROC1_y1={parameters['ROC1_y1']}",
        f"--ROC1_y2={parameters['ROC1_y2']}",
        f"--start_x1={parameters['start_x1']}",
        f"--start_x2={parameters['start_x2']}",
        f"--start_y1={parameters['start_y1']}",
        f"--start_y2={parameters['start_y2']}"
    ]

    # Execute pre_training_3.py with the specified command
    subprocess.run(command)

except Exception as e:
    print(f"Error: {e}")

finally:
    client_socket.close()
