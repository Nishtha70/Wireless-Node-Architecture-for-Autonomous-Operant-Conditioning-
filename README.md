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

We have trained a YOLOv5 model to detect cichlids in images. The training process can be found in the [`training.ipynb`](training.ipynb) notebook. The trained model weights (`yolov5_cichlid.pt`) are also available in the repository.
