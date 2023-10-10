import socket
import threading
from flask import Flask, render_template, request, redirect, url_for

# Define the server address and port
server_address = ('0.0.0.0', 8888)

# Create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the specified address and port
server_socket.bind(server_address)

# Listen for incoming connections (max 2 clients)
server_socket.listen(2)
print("Server is listening for connections...")

# Initialize Flask app
app = Flask(__name__)


# Dictionary to store values from clients
client1_values = {
    'tank_ID': None,
    'max_pretraining_days': None,
    'max_sessions_per_day': None,
    'stimulus_display_time': None,
    'success_threshold': None,
    'max_session_duration': None,
    'session_interval': None,
    'max_sessions_pretraining': None,
    'max_trial_per_session': None,
    'display_neutral_after_time': None,
    'stimulus_image': None,
    'neutral_image': None,
    'ROC1_x1': None,
    'ROC1_x2': None,
    'ROC1_y1': None,
    'ROC1_y2': None,
    'start_x1': None,
    'start_x2': None,
    'start_y1': None,
    'start_y2': None,
}

client2_values = {
    'tank_ID': None,
    'max_pretraining_days': None,
    'max_sessions_per_day': None,
    'stimulus_display_time': None,
    'success_threshold': None,
    'max_session_duration': None,
    'session_interval': None,
    'max_sessions_pretraining': None,
    'max_trial_per_session': None,
    'display_neutral_after_time': None,
    'stimulus_image': None,
    'neutral_image': None,
    'ROC1_x1': None,
    'ROC1_x2': None,
    'ROC1_y1': None,
    'ROC1_y2': None,
    'start_x1': None,
    'start_x2': None,
    'start_y1': None,
    'start_y2': None,
}

# Dictionary to store client sockets
client_sockets = {}

# Function to handle client connections
def handle_client(client_socket):
    try:
        # Receive data from the client (client identifier)
        client_id = client_socket.recv(1024).decode()
        print(f"Received connection from {client_id}")

        while True:
            # Send a response to the client to indicate readiness for input
            client_socket.send("Ready for input. Enter 'q' to quit.".encode())

            # Receive data (parameters) from the client
            data = client_socket.recv(1024).decode()

            if data.lower() == 'q':
                break  # Exit loop if 'q' is received

            print(f"Received data from {client_id}: {data}")
           
            # Store user input in the dictionary
            client_inputs[client_id] = data

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the client socket
        client_socket.close()

# Route to display the web form and collect user input
@app.route('/', methods=['GET', 'POST'])
def index():
    
    global client1_values, client2_values
    
    
    if request.method == 'POST':
        # Get the submitted data from the form
        if "client1_submit" in request.form:
            for field in client1_values.keys():
                client_values = globals()[f'{client_name}_values']
                client_values[field] = request.form.get(f"{client_name}_{field}")
        
        
        if "client2_submit" in request.form:
            for field in client2_values.keys():
                client_values = globals()[f'{client_name}_values']
                client_values[field] = request.form.get(f"{client_name}_{field}")
        

        # Find the client socket based on the client identifier
        client_socket = client_sockets[client_id]
       
        # Send the parameters to the respective client
        client_socket.send(parameters.encode())

    return render_template('index.html', client1_values=client1_values, client2_values=client2_values)



    #return redirect(url_for('index'))  # Redirect back to the main page after submitting

if __name__ == '__main__':
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5001})
    flask_thread.daemon = True
    flask_thread.start()

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receive client identifier (client1 or client2)
        client_id = client_socket.recv(1024).decode()
       
        # Store the client socket for future use
        client_sockets[client_id] = client_socket

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()