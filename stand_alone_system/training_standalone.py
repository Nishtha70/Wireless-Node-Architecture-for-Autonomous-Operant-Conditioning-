import os
import sys
import time
import json
import warnings
import argparse
import random
from datetime import date, datetime
import yaml
import csv
import pyautogui

import cv2
import imutils
import pandas as pd
import torch
from twilio.rest import Client
import motor_config
from Pre_training_standalone import Cichlids_preTrain_Exp

#Twilio SMS setup
account_sid = 'AC174a0802c2e63396a3807e4d26b6bc88'
auth_token = '96cb5a74da1a5d243094e45ce2ef09e2'
client = Client(account_sid, auth_token)

# Set up the screen resolution and calculate the window sizes and positions
screen_width, screen_height = pyautogui.size()
window_width = screen_width // 2
window_height = screen_height
left_window_pos = (0, 0)
right_window_pos = (window_width, 0)

# Define paths relative to the current script or project root
repo_dir = os.path.dirname(os.path.abspath(__file__))
weights_path = os.path.join(repo_dir, 'weights', 'best.pt')

# Load the YOLOv5 model from the local directory
model = torch.hub.load(repo_dir, 'custom', path=weights_path, force_reload=True, source='local')

# Open the default camera (Camera 0), set video encoding parameters, and create a video writer
cap = cv2.VideoCapture(0)
fourcc_codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
fps = 20.0
capture_size = (int(cap.get(3)), int(cap.get(4)))
video_writer = cv2.VideoWriter("video_record.avi", fourcc_codec, fps, capture_size)

# Access the feeder's motor pins and names from the motor_config module
motor_left = motor_config.left_motor_pins
motor_right = motor_config.right_motor_pins

# Load pre-training parameters from the JSON file
with open("pre_training_parameters.json", "r") as param_file:
    pre_training_parameters = json.load(param_file)

# Create the Cichlids_preTrain_Exp instance using the parameters
exp_instance = Cichlids_preTrain_Exp(
    tank_ID=pre_training_parameters["tank_ID"],
    max_pretraining_days=pre_training_parameters["max_pretraining_days"],
    max_sessions_per_day=pre_training_parameters["max_sessions_per_day"],
    success_threshold=pre_training_parameters["success_threshold"],
    unfit_threshold=pre_training_parameters["unfit_threshold"],
    max_session_duration=pre_training_parameters["max_session_duration"],
    session_interval=pre_training_parameters["session_interval"],
    max_trial_per_session=pre_training_parameters["max_trial_per_session"],
    display_neutral_after_time=pre_training_parameters["display_neutral_after_time"],
    stimulus_image=pre_training_parameters["stimulus_image"],
    neutral_image=pre_training_parameters["neutral_image"],
    ROC1_x1=pre_training_parameters["ROC1_x1"],
    ROC1_x2=pre_training_parameters["ROC1_x2"],
    ROC1_y1=pre_training_parameters["ROC1_y1"],
    ROC1_y2=pre_training_parameters["ROC1_y2"],
    start_x1=pre_training_parameters["start_x1"],
    start_x2=pre_training_parameters["start_x2"],
    start_y1=pre_training_parameters["start_y1"],
    start_y2=pre_training_parameters["start_y2"]
)

# Load training parameters from the JSON file
with open("training_parameters.json", "r") as param_file:
    training_parameters = json.load(param_file)

#Assign the training parameters
tank_ID=training_parameters["tank_ID"],
max_training_days=training_parameters["max_training_days"],
max_sessions_per_day=training_parameters["max_sessions_per_day"],
success_threshold=training_parameters["success_threshold"],
unfit_threshold=training_parameters["unfit_threshold"],
max_session_duration=training_parameters["max_session_duration"],
session_interval=training_parameters["session_interval"],
max_trial_per_session=training_parameters["max_trial_per_session"],
display_neutral_after_time=training_parameters["display_neutral_after_time"],
correct_stimulus=training_parameters["correct_stimulus"],
incorrect_stimulus=training_parameters["incorrect_stimulus"],
neutral_image=training_parameters["neutral_image"],
left_ROI_x1=training_parameters["left_ROI_x1"],
left_ROI_x2=training_parameters["left_ROI_x2"],
left_ROI_y1=training_parameters["left_ROI_y1"],
left_ROI_y2=training_parameters["left_ROI_y2"],
right_ROI_x1=training_parameters["right_ROI_x1"],
right_ROI_x2=training_parameters["right_ROI_x2"],
right_ROI_y1=training_parameters["right_ROI_y1"],
right_ROI_y2=training_parameters["right_ROI_y2"]

class Cichlids_Train_Exp:
    def __init__(self, tank_ID, max_training_days, max_sessions_per_day,  success_threshold, unfit_threshold, max_session_duration, session_interval, max_trial_per_session, display_neutral_after_time, correct_stimulus, incorrect_stimulus, neutral_image, left_ROI_x1, left_ROI_x2, left_ROI_y1, left_ROI_y2, right_ROI_x1, right_ROI_x2, right_ROI_y1, right_ROI_y2):
        self.tank_ID = tank_ID
        self.max_training_days = max_training_days
        self.max_sessions_per_day = max_sessions_per_day
        self.success_threshold = success_threshold
        self.unfit_threshold = unfit_threshold
        self.max_session_duration = max_session_duration
        self.session_interval = session_interval
        self.max_trial_per_session = max_trial_per_session
        self.display_neutral_after_time = display_neutral_after_time
        self.correct_stimulus = correct_stimulus
        self.incorrect_stimulus = incorrect_stimulus
        self.neutral_image = neutral_image
        self.left_ROI_x1 = left_ROI_x1
        self.left_ROI_x2 = left_ROI_x2
        self.left_ROI_y1 = left_ROI_y1
        self.left_ROI_y2 = left_ROI_y2
        self.right_ROI_x1 = right_ROI_x1
        self.right_ROI_x2 = right_ROI_x2
        self.right_ROI_y1 = right_ROI_y1
        self.right_ROI_y2 = right_ROI_y2
        self.coordinates_data = []
        self.train_info = []
        self.trained = False
        
    #Save training routine information    
    def save_train_info(self, csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Session Number", "Number of Trials Performed", "Response Rate", "Learning_Success"])
            writer.writerows(self.coordinates_data)

    #Set up GPIO pins for motor control   
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        #Left Motor
        GPIO.setup(motorLA,GPIO.OUT)  # All pins as Outputs
        GPIO.setup(motorLB,GPIO.OUT)
        GPIO.setup(motorLE,GPIO.OUT)
        
        #Right Motor        
        GPIO.setup(motorRA,GPIO.OUT)  # All pins as Outputs
        GPIO.setup(motorRB,GPIO.OUT)
        GPIO.setup(motorRE,GPIO.OUT)

    #Operates the motor to drop food
    def food_drop(self, motor_name):
        # Going forward
        GPIO.output(motor_name[0],GPIO.HIGH)
        GPIO.output(motor_name[1],GPIO.LOW)
        GPIO.output(motor_name[2],GPIO.HIGH)
        sleep(5)
        # Going backwards
        GPIO.output(motor_name[0],GPIO.LOW)
        GPIO.output(motor_name[1],GPIO.HIGH)
        GPIO.output(motor_name[2],GPIO.HIGH)
        sleep(5)
        # Stop
        GPIO.output(motor_name[2],GPIO.LOW)
        
    #Executes a training session    
    def run_session(self, session, save_recording, save_coordinates):
        session+=1
        print("start")
        trial_count = 0
        success_count = 0
        response_count = 0
        trigger_count = 1
        food_drop_count = 0
        learning_success = 0
        response_rate = 0
        session_start_time = time.time()
        
        while trial_count < self.max_trial_per_session:
            while (time.time() - session_start_time) <self.max_session_duration:
                output_image, fish_x, fish_y = exp_instance.track_fish(session, save_recording)
                #Saves the recording and tracked coordinates
                video_writer.write(output_image)
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                exp_instance.save_coordinates_csv(save_coordinates)

                previous_pattern = " "
                current_pattern = " "
                consecutive_same_pattern_count=0
                
                #Random display of stimulus on the screen
                if random.choice([True, False]):
                    left_screen_image = self.correct_stimulus
                    right_screen_image = self.incorrect_stimulus
                    current_pattern = "Correct"
                else:
                    left_screen_image = self.incorrect_stimulus
                    right_screen_image = self.correct_stimulus
                    current_pattern = "Incorrect"
                    
                #Ensures pattern of correct/incorrect stimulus on-screen is not repeated more than thrice
                if current_pattern == previous_pattern:
                    consecutive_same_pattern_count+=1
                    print("consecutive_same_pattern:", consecutive_same_pattern)
                    if consecutive_same_pattern_count>=3:
                        #Swap the image
                        left_screen_image, right_screen_image = right_screen_image, left_screen_image
                else:
                    consecutive_same_pattern_count = 0
                    
                previous_pattern = current_pattern

                #Fish is in start area
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, exp_instance.start_x1, exp_instance.start_y1, exp_instance.start_x2, exp_instance.start_y2) == True:
                    exp_instance.displayn(left_screen_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                    exp_instance.displayn(right_screen_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                    if trigger_count <= 0:
                        trial_count+=1
                        trigger_count+=1
                        food_drop_count = 0

                #Fish is in region of choice
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, exp_instance.ROC_x1, exp_instance.ROC1_y1, exp_instance.ROC1_x2, exp_instance.ROC1_y2) == True:
                    trigger_count=0
                    response_count+=1
                    
                    if exp_instance.is_fish_in_ROI(fish_x, fish_y, self.left_ROI_x1, self.left_ROI_y1, self.left_ROI_x2, slef.left_ROI_y2) == True:
                        #Testing if fish made correct choice by entering left side
                        if left_screen_image == self.correct_stimulus:
                            fish_entry_ROC = time.time()
                            if time.time() - fish_entry_ROC > self.display_neutral_after_time:
                                self.displayn(self.neutral_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                                self.displayn(self.neutral_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                                if food_drop_count<=0:
                                    self.food_drop(motor_left)
                                    success_count+=1
                                    food_drop_count+=1
                                    
                    if exp_instance.is_fish_in_ROI(fish_x, fish_y, slef.right_ROI_x1, self.right_ROI_y1, self.right_ROI_x2, self.right_ROI_y2) == True:
                        #Testing if fish made correct choice by entering right side
                        if right_screen_image == self.correct_stimulus:
                            fish_entry_ROC = time.time()
                            if time.time() - fish_entry_ROC > self.display_neutral_after_time:
                                self.displayn(self.neutral_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                                self.displayn(self.neutral_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                                if food_drop_count<=0:
                                    self.motor_drop(motor_right)
                                    success_count+=1
                                    food_drop_count+=1              
            break
          
        print("Time:",time.time() - session_start_time)
        print("Trial_count:", trial_count)
        print("Maximum time or trial count reached")
        response_rate = (response_count/self.max_trial_per_session)*100
        learning_success = (success_count/self.max_trial_per_session)*100
        print(response_rate)
        print(learning_success)
        return trial_count, response_rate, learning_success
                                    
    #Executes the training routine                
    def run_train_exp(self): 
        session = 0
        consecutive_successful_sessions = 0
        consecutive_unfit_sessions = 0
        
        for day in range(self.max_training_days):
            while session <= self.max_sessions_per_day:
                date_session = date.today()
                save_recording = "T" + "_" + str(self.tank_ID)  + "_" + str(date_session) + ".avi"
                save_coordinates = "T" + "_" + str(self.tank_ID)  +  "_" + str(date_session) + "_coords.csv"
                save_training_details = "T" + "_" + str(self.tank_ID) + "_train_info.csv"
                
                output_image, fish_x, fish_y = exp_instance.track_fish(session, save_recording)
                #print(fish_x, fish_y)
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                #print(self.coordinates_data)
                exp_instance.save_coordinates_csv(save_coordinates)

                #Fish comes into start area for the first time and the training routine starts 
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, exp_instance.start_x1, exp_instance.start_y1, exp_instance.start_x2, exp_instance.start_y2) == True:
                    response_rate, learning_success, trial_count = self.run_session(session, save_recording, save_coordinates)
                    print("Session Ended")
                    time.sleep(self.session_interval)
                    self.train_info.append([session, trial_count, response_rate, learning_success])
                    self.save_train_info(save_training_details)
                    
                    if learning_success >= self.success_threshold:
                        consecutive_successful_sessions+=1
                    else:
                        consecutive_successful_sessions = 0
                        
                    if response_rate <= self.unfit_threshold:
                        consecutive_unfit_sessions+=1
                    else:
                        consecutive_unfit_sessions=0
                        
                    if consecutive_unfit_sessions >= 2:
                        print("Fish_unfit_for_training")
                        message = client.messages.create(body="Fish unfit for training. The system is in sleep mode. Re-execute the file", from_='+19408182187', to='+918529691031')
                        time.sleep(0)
                        
                    if consecutive_successful_sessions >= 2:
                        self.trained = True
                        try:
                            os.rename("video_record.avi", save_recording)
                        except OSError as e:
                            print("Error Renaming the file")
                        print("Fish is trained!")
                        
                    else:
                        print("Fish not trained yet")
                        continue
                        
                else:
                    continue
                
                
# Create the Cichlids_Train_Exp instance using the parameters
experiment1 = Cichlids_Train_Exp(
  tank_ID=tank_ID,
    max_training_days=max_training_days,
    max_sessions_per_day=max_sessions_per_day,
    success_threshold=success_threshold,
    unfit_threshold=unfit_threshold,
    max_session_duration=max_session_duration,
    session_interval=session_interval,
    max_trial_per_session=max_trial_per_session,
    display_neutral_after_time=display_neutral_after_time,
    correct_stimulus=correct_stimulus,
    incorrect_stimulus=incorrect_stimulus,
    neutral_image=neutral_image,
    left_ROI_x1=left_ROI_x1,
    left_ROI_x2=left_ROI_x2,
    left_ROI_y1=left_ROI_y1,
    left_ROI_y2=left_ROI_y2,
    right_ROI_x1=right_ROI_x1,
    right_ROI_x2=right_ROI_x2,
    right_ROI_y1=right_ROI_y1,
    right_ROI_y2=right_ROI_y2
)


if __name__ == "__main__":
    experiment.run_pretrain_exp()
        
