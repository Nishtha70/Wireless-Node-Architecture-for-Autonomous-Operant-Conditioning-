# Development of Network of Automated Operant Conditioning Apparatus to investigate cognition

This repository contains the code and resources for the Wireless-Node-Architecture of multiple autonomous operant conditioning devices. Please note that this project is currently a work in progress, and code is being actively added and refined.

## Objectives of the project

The purpose of this project is to:
1. Implemented the live automated tracking, identification, and video recording of cichlids
2. Automated the pre-training, training protocol and switching between different routines of cognitive experiments
3. Development of a Client-server architecture of multiple Raspberry Pis to improve existing data consolidation and management pipelines in automated cognition testing 

For a more detailed overview of the project's purpose, goals, and methodology, you can refer to the complete **CONTRIBUTING.md** and **Thesis Proposal** document. Contributing.md contains details of project's organization and code. The proposal outlines the project's background, objectives, methodology, and expected outcomes in depth.

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
│ ├── pre_training_standalone.py
│ ├── training_standalone.py
│ ├── app.py
│ ├── experiment_form.html
│ |
├── Client/
│ ├── client.py
│ ├── pre_training_client.py
│ ├── training_client.py
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
│ ├── experiment_form.py
│ │ 
│
├── README.md
├── CONTRIBUTING.md
├── Cichlid_detection.ipynb
├── weights


