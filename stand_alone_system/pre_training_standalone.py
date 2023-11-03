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

#Twilio SMS setup - send notifications if the camera fails to start
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


class Cichlids_preTrain_Exp:
    def __init__(self, tank_ID, max_pretraining_days, max_sessions_per_day, success_threshold, unfit_threshold,
             max_session_duration, session_interval, max_trial_per_session, display_neutral_after_time,
             stimulus_image, neutral_image, ROC1_x1, ROC1_y1, ROC1_x2, ROC1_y2, start_x1, start_y1, start_x2, start_y2):
        self.tank_ID = tank_ID
        self.max_pretraining_days = max_pretraining_days
        self.max_sessions_per_day = max_sessions_per_day
        self.success_threshold = success_threshold
        self.unfit_threshold = unfit_threshold
        self.max_session_duration = max_session_duration
        self.session_interval = session_interval
        self.max_trial_per_session = max_trial_per_session
        self.display_neutral_after_time = display_neutral_after_time
        self.stimulus_image = stimulus_image
        self.neutral_image = neutral_image
        self.ROC1_x1 = ROC1_x1
        self.ROC1_x2 = ROC1_x2
        self.ROC1_y1 = ROC1_y1
        self.ROC1_y2 = ROC1_y2
        self.start_x1 = start_x1
        self.start_x2 = start_x2
        self.start_y1 = start_y1
        self.start_y2 = start_y2
        self.coordinates_data = []
        self.pre_train_info = []
        self.pretrained = False
        
    #Method to detect and track fish   
    def track_fish(self, session, video_recording):
        cx = 0
        cy = 0
                 
        #Check if frame is received by the RasPy
        if not cap.isOpened():
            message = client.messages.create(body="Cannot open camera", from_='+19408182187', to='+918529691031')
            print("Cannot open camera")
            exit()
        ret, frame = cap.read()
        if not ret:
            message = client.messages.create(body="Cannot open camera", from_='+19408182187', to='+918529691031')
            print("Cant receive frame end")
            exit()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        results = model(frame, size=720)
        results.xyxy[0]  # im predictions (tensor)
        results.pandas().xyxy[0]
        json_results = results.pandas().xyxy[0].to_json(orient="records")
        results.render()
        output_image = results.ims[0] #output image after rendering
        output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)

        #calculate centroid
        data = json.loads(json_results)
        for objects in data:
            xmin = objects["xmin"]
            ymin = objects["ymin"]
            xmax = objects["xmax"]
            ymax = objects["ymax"]
            
            cx = int((xmin+xmax)/2.0)
            cy = int((ymin+ymax)/2.0)
    
        cv2.circle(output_image, (cx, cy), 2, (0,0,255), 2, cv2.FILLED)
        cv2.putText(output_image, str(str(cx)+ "," +str(cy)), (int(cx)-40, int(cy)+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(output_image, str("Session:"+str(session)+"TS:"+str(timestamp)), (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        return output_image, cx, cy

    #Checks if fish is present in the region of interest
    def is_fish_in_ROI(self, fish_x, fish_y, ROC1_x1, ROC1_y1, ROC1_x2, ROC1_y2):
        if ROC1_x1 <= fish_x<= ROC1_x2 and ROC1_y1 <= fish_y<= ROC1_y2:
            return True
        else:
            return False

    #Displays stimulus on the screens
    def displayn(self, image_path, screen_name,  width, height, window_position):
        window_pos = [width, height]
        image = cv2.imread(image_path)
        cv2.namedWindow(screen_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(screen_name, width, height)
        cv2.moveWindow(screen_name, window_position[0], window_position[1])
        cv2.imshow(screen_name, image)
        cv2.waitKey(2)

    #Saves tracked coordinates of fish in a csv
    def save_coordinates_csv(self, csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Session Number", "Timestamp", "Fish_X", "Fish_Y"])
            writer.writerows(self.coordinates_data)
            
    #Saves information about the pre-training routine
    def save_pretrain_info(self, csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Session Number", "Number of Trials Performed", "Learning_Success"])
            writer.writerows(self.coordinates_data)
            
    #Set up GPIO pins for motor control       
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(motor1A,GPIO.OUT)  
        GPIO.setup(motor1B,GPIO.OUT)
        GPIO.setup(motor1E,GPIO.OUT)
        GPIO.setup(motor2A,GPIO.OUT) 
        GPIO.setup(motor2B,GPIO.OUT)
        GPIO.setup(motor2E,GPIO.OUT)

    #Operates the motor
    def motor_run(self, motor_name):
        # Going forwards
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

    #Randomly select a fish feeder to drop the food
    def food_drop(self, motorX, motorY):
        motor_listed = [motorX, motorY]
        food_motor = random.choice(motor_listed)
        print(food_motor)
        motor_run(food_motor)

    #Execute a pre-training session
    def run_session(self, session, save_recording, save_coordinates):
        session+=1
        print("start")
        trial_count = 0
        trigger_count = 1
        food_drop_count = 0
        session_start_time = time.time()
        
        while trial_count <= self.max_trial_per_session:
            while (time.time() - session_start_time) <= self.max_session_duration:
                output_image, fish_x, fish_y = self.track_fish(session, save_recording)
                print(fish_x, fish_y)
                cv2.imshow("frame", output_image)
                video_writer.write(output_image)
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                #print(self.coordinates_data)
                self.save_coordinates_csv(save_coordinates)
                
                #Fish_in_start_area
                if self.is_fish_in_ROI(fish_x, fish_y, self.start_x1, self.start_y1, self.start_x2, self.start_y2) == True:
                    self.displayn(self.stimulus_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                    self.displayn(self.stimulus_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                    if trigger_count <= 0:
                        trial_count+=1
                        trigger_count+=1
                        food_drop_count = 0

                #Fish is in Region of choice
                if self.is_fish_in_ROI(fish_x, fish_y, self.ROC1_x1, self.ROC1_y1, self.ROC1_x2, self.ROC1_y2) == True:
                    trigger_count=0
                    fish_entry_ROC = time.time()
                    
                    if time.time() - fish_entry_ROC > self.display_neutral_after_time:
                        self.displayn(self.neutral_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                        self.displayn(self.neutral_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
                        if food_drop_count<=0:
                            self.food_drop(motor_left, motor_right)
                            food_drop_count+=1
                    else:
                        self.displayn(self.stimulus_image, "Left_Screen", int(window_width/2), window_height, left_window_pos)
                        self.displayn(self.stimulus_image, "Right_Screen", int(window_width/2), window_height, right_window_pos)
            break
            
        print("Time:",time.time() - session_start_time)
        print("Trial_count:", trial_count)
        print("Maximum time or trial count reached")
        learning_success = (trial_count/self.max_trial_per_session)*100
        print(learning_success)
        return trial_count, learning_success
        
    def run_pretrain_exp(self): 
        session = 0
        consecutive_successful_sessions = 0
        consecutive_unfit_sessions = 0
    
        for day in range(1, self.max_pretraining_days+1):
            for session in range(self.max_sessions_per_day):
                date_session = date.today()
                save_recording = "P" + "_" + str(self.tank_ID)  + "_" + str(date_session) + ".avi"
                save_coordinates = "P" + "_" + str(self.tank_ID)  +  "_" + str(date_session) + "_coords.csv"
                save_pretraining_details = "P" + "_" + str(self.tank_ID) + "_pretrain_info.csv"
                
                output_image, fish_x, fish_y = self.track_fish(session, save_recording)
                print(fish_x, fish_y)
                cv2.imshow("frame", output_image)
                video_writer.write(output_image)
                session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.coordinates_data.append([session, session_time, fish_x, fish_y])
                print(self.coordinates_data)
                self.save_coordinates_csv(save_coordinates)
                
                if self.is_fish_in_ROI(fish_x, fish_y, self.start_x1, self.start_y1, self.start_x2, self.start_y2) == True:
                    learning_success, trial_count = self.run_session(session, save_recording, save_coordinates)
                    print("Session Ended")
                    cv2.waitKey(self.session_interval)
                    self.pre_train_info.append([session, trial_count, learning_success])
                    self.save_pretrain_info(save_pretraining_details)
                    
                    if learning_success >= self.success_threshold:
                        consecutive_successful_sessions+=1
                    else:
                        consecutive_successful_sessions = 0
                        
                    if learning_success <= self.unfit_threshold:
                        consecutive_unfit_sessions+=1
                    else:
                        consecutive_unfit_sessions=0
                        
                    if consecutive_unfit_sessions >= 2:
                        print("Fish_unfit_for_training")
                        message = client.messages.create(body="Fish unfit for training. The system is in sleep mode. Re-execute the file", from_='+19408182187', to='+918529691031')
                        time.sleep(0)
                        
                    if consecutive_successful_sessions >= 2:
                        self.pretrained = True
                        try:
                            os.rename("video_record.avi", save_recording)
                        except OSError as e:
                            print("Error Renaming the file")
                        print("Fish is pre-trained!")   
                    else:
                        print("Fish not trained yet")
                        continue
                else:
                    continue
                
        if day < self.max_pretraining_days:
            time.sleep(12*3600)   #Sleep for 12 hours to simulate the passage of day else:

         
experiment = Cichlids_preTrain_Exp(
    tank_ID=1,
    max_pretraining_days=2,
    max_sessions_per_day=4,
    success_threshold=80,
    unfit_threshold = 0,
    max_session_duration=180000,             #in microseconds (30(mins)*60*1000 = 180000)
    session_interval=3600,                   #in seconds (1 hour)
    max_trial_per_session=10,
    display_neutral_after_time=3000,         #in mircoseconds(3sec)
    stimulus_image="/home/pi/Automatic_Conditioning_Apparatus/images/pre_train_stimulus_image.jpg",
    neutral_image="/home/pi/Automatic_Conditioning_Apparatus/images/pre_train_neutral_image.jpg",
    ROC1_x1=100,
    ROC1_x2=600,
    ROC1_y1=100,
    ROC1_y2=600,
    start_x1=0,
    start_x2=100,
    start_y1=0,
    start_y2=100
)

if __name__ == "__main__":
    experiment.run_pretrain_exp()

