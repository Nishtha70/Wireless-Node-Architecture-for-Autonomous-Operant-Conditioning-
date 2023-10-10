# Project Name

This repository contains the code and resources for the Wireless-Node-Architecture of multiple autonomous operant conditioning devices. Please note that this project is currently a work in progress, and code is being actively added and refined.


## Thesis Proposal

The purpose of this project is to:
1. Implementing live tracking of cichlids using YOLOv5 to develop Raspberry-Pi-based Automated Conditional Training Apparatus for Cognition Testing in Fishes and testing the apparatus in Field conditions
2. Development of a Client-server architecture of multiple Raspberry Pis to improve existing data consolidation and management pipelines in automated cognition testing.

For a more detailed overview of the project's purpose, goals, and methodology, you can refer to the complete **Thesis Proposal** document. The proposal outlines the project's background, objectives, methodology, and expected outcomes in depth.

## Dependencies

To run this project on your Raspberry Pi, you'll need the following dependencies:

- `RPi.GPIO`: A Python library for controlling Raspberry Pi GPIO pins. Install it using:  pip install RPi.GPIO
- YOLOv5 (Ultralytics)`: A powerful object detection framework. Install it using: pip install ultralytics
- Twilio: To notify the user by SMS if the camera fails to start or receive frames, notify the user when the pre-training and training routine is completed
- Flask: To create the web app for users to enter different parameters of pre-training and training routine

## Hardware Requirements
- RaspberryPi 4B
- PiCaera/USB Camera
- Eheim Fish Feeder
- L293D motor driver
  

## Repository Structure
Wireless-Node-Architecture-for-Autonomous-Operant-Conditioning/
│
├── stand-alone-system/
│ ├── resources/
│ │ ├── hardware setup and feeder.pdf
│ │ ├── Thesis proposal.pdf
│ │
│ ├── images/
│ │ ├── pre_train_neutral_image.jpg
| | ├── pre_train_stimulus_image.jpg
│ │ ├── train_correct_colour.jpg
│ │ ├── train_incorrect_colour.jpg
│ │
│ ├── Pre_training_standalone.py
│ ├── Training_standalone.py
│ ├── Find_ROI.py
│ |
├── Client/
│ ├── client.py
│ ├── Pre_training_client.py
│ ├── Training_client.py
│ |
│ ├── images/
│ │ ├── pre_train_neutral_image.jpg
| | ├── pre_train_stimulus_image.jpg
│ │ ├── train_correct_colour.jpg
│ │ ├── train_incorrect_colour.jpg
│ |
│ |
├──Server/
│ ├── server.py
│ ├── templates
│ │ ├── index.html
│
├── README.md
├── Cichlid_detection.ipynb
├── weights


## YOLOv5 Cichlid Detection Model

We have trained a YOLOv5 model to detect cichlids in images. The training process can be found in the [`Cichlid_detection.ipynb`](Cichlid_detection.ipynb) notebook. The trained model weights are also available in the weights sub-repository.

## stand-alone system
This repository contains the files for running the system independently on a single computer without the need for a client-server architecture.
1. Resources: Consists of thesis proposal, installation instructions, electrical connections of hardware components, and a troubleshooting guide.
   - Thesis proposal.pdf: Detailed report on the project's purpose, goals, and experiment design with flowcharts of pre-training and training routine
   - hardware setup and feeder: Instructions to install ultralytics on Raspberry Pi 64-bit system, connection diagram of RaspberryPi with Eheim fish feeder and troubleshooting guide for hardware-related issues.

2. Images: Consists of image files used in pre-training and training
   - pre_train_neutral_image.jpg: Used for establishing a baseline response to the stimulus shown on screen.
   - pre_train_stimulus_image.jpg: Used as a stimulus in the pre-training routine to establish an association between the presentation of a visual stimulus on a screen and the delivery of food reinforcement to the cichlid subjects Food (Reward) is dropped when the subject approaches this stimulus
   - train_correct_colour.jpg: In the training routine, this stimulus represents the correct response and leads to food reinforcement upon approach by the cichlid subject
   - train_incorrect_colour.jpg:  In the training routine, this stimulus represents incorrect response and does not lead to food reinforcement upon approach by the cichlid subject

3.Pre_training_standalone.py: Automates the pre-training routine. It consists of methods to automate live tracking and detection of cichlid subjects, identifying the Region of Interest fish is present in, and generating CSV files containing coordinate data and information about the experiment, such as the number of trials performed and learning success in each session.
  - track_fish(): Captures video frames from a camera pointed at the fish tank and processes these frames to extract positional coordinates of the cichlid subject in the tank. Returns the x-y coordinates and processed frame with a bounding box around 
    the detected subject and centroid of the bounding box.
  - displayn(): Displays the image files on the screen
  - setup(): Sets up the GPIO pins of RaspberryPi to control external hardware (fish feeder) outputs
  - motor_run(): Controls the direction and speed of DC motor in the fish feeder 
  - food_drop(): Responsible for selecting and activating one of two motors to drop food reinforcement.
  - save_coordinates_csv(): Saves the coordinates of the detected cichlid subject along with the timestamp
  - save_petrain_info(): Saves the information about session number, number of trials, learning success in each session in a CSV file
  - run_session(): Executes a single experimental session, including fish tracking, stimulus presentation, and food reinforcement. Returns the number of trials completed by the cichlid subject in the session and learning success
  - run_pretrain_exp(): Executes the pre-training experiment as the fish enters the start area of the tank. Responsible for managing multiple sessions over several days, collecting data, and determining if the fish is pre-trained or unfit for 
    further training based on consecutive session outcomes
    
4. Training_standalone.py: Automates the training routine. Uses the methods in Pre_training_standalone.py to facilitate the process of training cichlid subjects to discriminate between two distinct visual stimuli. The script executes training sessions, monitors subjects' responses, and records pertinent data to assess learning success.

5. find_ROI.py: Used for determining the coordinates of the Start area and Region of choice as calculated by OpenCV.

## client system
This repository contains the files for establishing the connection with the server through Socket, receiving the parameters from the server and executing the Pre-training and training routine.
1. app.py: Tries connecting to the server using the provided server IP address, receives the custom parameters and executes the pre_training_client.py
2. Pre_training_client.py: Use same methods as in Pre_training_standalone.py to execute pre-training routine in the client.  Additionally, contains the code to parse the parameters required for the pre-training script to run from the app.

## server system
This repository contains the files for establishing the client-server communication over the socket, flask web-app where the experimenter enters various parameters for pre-training and training routine and sends the parameters to the client.
1. server.py: Uses the 'socket' library to create a socket server and identify the client based on a unique client ID sent by the client. Initializes the Flask web application to handle the web form where users enter  and submit input parameters for the clients. Send the parameters to respective clients and execute pre-training and training routines on the client.
2. templates/index.html: Contains the code for the frontend design of the Flask web-app

