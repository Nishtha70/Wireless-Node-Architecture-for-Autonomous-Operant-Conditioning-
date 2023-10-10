#import the libraries
import cv2
import numpy
import torch
import imutils
import sys
import time
import yaml
import os
import json
import warnings
import random
from datetime import date
import csv
import pandas as pd
from twilio.rest import Client
from datetime import datetime
from Pre_training_standalone import Cichlids_preTrain_Exp
exp_instance = Cichlids_preTrain_Exp(tank_ID=1,
                                     max_pretraining_days=2,
                                     max_sessions_per_day=4,
                                     success_threshold=80,
                                     unfit_threshold = 0,
                                     max_session_duration=180000,             #in microseconds (30(mins)*60*1000 = 180000)
                                     session_interval=3600,                   #in seconds (1 hour)
                                     max_trial_per_session=10,
                                     display_neutral_after_time=3000,  #in mircoseconds(3sec)
                                     stimulus_image="/home/pi/Automatic_Conditioning_Apparatus/images/pre_train_stimulus_image.jpg",
                                     neutral_image="/home/pi/Automatic_Conditioning_Apparatus/images/pre_train_neutral_image.jpg",
                                     ROC1_x1=100,
                                     ROC1_x2=600,
                                     ROC1_y1=100,
                                     ROC1_y2=600,
                                     start_x1=0,
                                     start_x2=100,
                                     start_y1=0,
                                     start_y2=100)


#Twilio SMS setup
account_sid = 'AC174a0802c2e63396a3807e4d26b6bc88'
auth_token = '96cb5a74da1a5d243094e45ce2ef09e2'
client = Client(account_sid, auth_token)

#Enter path of neutral and stimulus display image
stimulus_display = "/home/pi/Downloads/red_wallpaper"
neutral_display = "/home/pi/Downloads/green_wallpaper"

# Set up the screen resolution and calculate the window sizes and positions
screen_width = 3840
screen_height = 1080
window_width = screen_width // 2
window_height = screen_height
left_window_pos = (0, 0)
right_window_pos = (window_width, 0)

model = torch.hub.load('/home/pi/yolov5', 'custom', path='/home/pi/yolov5/runs/exp_yolov5n/weights/best.pt', force_reload=True, source='local')

cap = cv2.VideoCapture(0)

fourcc_codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
fps = 20.0
capture_size = (int(cap.get(3)), int(cap.get(4)))
video_writer = cv2.VideoWriter("video_record.avi", fourcc_codec, fps, capture_size)

# Pins for Motor Driver Inputs
#Left Motor
motorLA = 24
motorLB = 23
motorLE = 25

#Right Motor
motorRA = 20
motorRB = 21
motorRE = 16

#Motor names
motor_left = [motorLA, motorLB, motorLE]
motor_right = [motorRA, motorRB, motorRE]


class Cichlids_Train_Exp:
    def __init__(self, tank_ID, max_training_days, max_sessions_per_day,  success_threshold, unfit_threshold, max_session_duration, session_interval, max_trial_per_session, display_neutral_after_time, correct_stimulus, incorrect_stimulus, neutral_image, start_x1, start_x2, start_y1, start_y2, ROC_x1, ROC_x2, ROC_y1, ROC_y2, left_ROI_x1, left_ROI_x2, left_ROI_y1, left_ROI_y2, right_ROI_x1, right_ROI_x2, right_ROI_y1, right_ROI_y2):
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
        self.start_x1 = start_x1
        self.start_x2 = start_x2
        self.start_y1 = start_y1
        self.start_y2 = start_y2
        self.ROC_x1 = ROC_x1
        self.ROC_x2 = ROC_x2
        self.ROC_y1 = ROC_y1
        self.ROC_y2 = ROC_y2
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
        
        
    def save_train_info(self, csv_filename):
        
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Session Number", "Number of Trials Performed", "Response Rate", "Learning_Success"])
            writer.writerows(self.coordinates_data)
            
            
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
        
    def food_drop(self, motor_name):
        # Going forward
        GPIO.output(motor_name[0],GPIO.HIGH)
        GPIO.output(motor_name[1],GPIO.LOW)
        GPIO.output(motor_name[2],GPIO.HIGH)
        print(2)
        sleep(5)
        # Going backwards
        GPIO.output(motor_name[0],GPIO.LOW)
        GPIO.output(motor_name[1],GPIO.HIGH)
        GPIO.output(motor_name[2],GPIO.HIGH)
        sleep(5)
        # Stop
        GPIO.output(motor_name[2],GPIO.LOW)
        
        
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
                #video_writer.write(output_image)
                #print(time.time() - session_start_time)
               
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                #print(self.coordinates_data)
                exp_instance.save_coordinates_csv(save_coordinates)
                
                previous_pattern = " "
                current_pattern = " "
                consecutive_same_pattern_count=0
                
                #Random Choice
                if random.choice([True, False]):
                    left_screen_image = self.correct_stimulus
                    right_screen_image = self.incorrect_stimulus
                    current_pattern = "Correct"
                else:
                    left_screen_image = self.incorrect_stimulus
                    right_screen_image = self.correct_stimulus
                    current_pattern = "Incorrect"
                    
                #Ensures same pattern is not repeated more than thrice
                if current_pattern == previous_pattern:
                    consecutive_same_pattern_count+=1
                    print("consecutive_same_pattern:", consecutive_same_pattern)
                    if consecutive_same_pattern_count>=3:
                        #Swap the image
                        left_screen_image, right_screen_image = right_screen_image, left_screen_image
                else:
                    consecutive_same_pattern_count = 0
                    
                previous_pattern = current_pattern
                
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, start_x1, start_y1, start_x2, start_y2) == True:
                    exp_instance.displayn(left_screen_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                    exp_instance.displayn(right_screen_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                    if trigger_count <= 0:
                        trial_count+=1
                        trigger_count+=1
                        food_drop_count = 0
                        
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, self.ROC_x1, self.ROC1_y1, self.ROC1_x2, self.ROC1_y2) == True:
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
                                    
                    
    def run_train_exp(self):
        
        session = 0
        consecutive_successful_sessions = 0
        consecutive_unfit_sessions = 0
        
        for day in range(self.max_training_days):
            
            
            while session <= self.max_sessions_per_day:
                
                date_session = date.today()
                print('****')
                save_recording = "T" + "_" + str(self.tank_ID)  + "_" + str(date_session) + ".avi"
                
                save_coordinates = "T" + "_" + str(self.tank_ID)  +  "_" + str(date_session) + "_coords.csv"
                
                save_training_details = "T" + "_" + str(self.tank_ID) + "_train_info.csv"
                
                
                output_image, fish_x, fish_y = exp_instance.track_fish(session, save_recording)
                #print(fish_x, fish_y)
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                #print(self.coordinates_data)
                exp_instance.save_coordinates_csv(save_coordinates)
                
                if exp_instance.is_fish_in_ROI(fish_x, fish_y, self.start_x1, self.start_y1, self.start_x2, self.start_y2) == True:
                    
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
                
                
               
                    

                
experiment1 = Cichlids_Train_Exp(
    tank_ID = 1,
    max_training_days = 4,
    max_sessions_per_day = 2,
    success_threshold = 80,
    unfit_threshold = 10,
    max_session_duration = 180000,             #in microseconds (30(mins)*60*1000 = 180000)
    session_interval = 3600,                  #in seconds (1 hour)
    max_trial_per_session = 10,
    display_neutral_after_time = 3000,         #in microseconds (3 seconds)
    correct_stimulus = "/home/pi/Automatic_Conditioning_Apparatus/images/train_correct_colour.jpg",
    incorrect_stimulus = "/home/pi/Automatic_Conditioning_Apparatus/images/train_incorrect_colour.jpg",
    neutral_image = "/home/pi/Automatic_Conditioning_Apparatus/images/pre_train_neutral_image.jpg",
    start_x1=100,
    start_x2 = 100,
    start_y1 = 0,
    start_y2 = 100,
    ROC_x1 = 100,
    ROC_x2 = 600,
    ROC_y1 = 100,
    ROC_y2 = 600,
    left_ROI_x1 = 100,
    left_ROI_x2 = 300,
    left_ROI_y1 = 100,
    left_ROI_y2 = 600,
    right_ROI_x1 = 300,
    right_ROI_x2 = 600,
    right_ROI_y1 = 100,
    right_ROI_y2 = 600)

experiment1.run_train_exp()
        
