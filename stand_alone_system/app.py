import os
from flask import Flask, render_template, request, jsonify, json
from pre_training_standalone import Cichlids_preTrain_Exp

app = Flask(__name__)

pre_training_parameters = None
training_parameters = None
pre_training_executed = False

# Define a route to display the form for setting up the experiment
@app.route("/", methods=["GET", "POST"])
def setup_experiment():
    global pre_training_parameters, training_parameters, pre_training_executed

    if request.method == "POST":
        # Get the form data for pre-training parameters
        pre_training_parameters = {
            "tank_ID": request.form["tank_ID"],
            "max_pretraining_days": request.form["max_pretraining_days"],
            "max_sessions_per_day": request.form["max_sessions_per_day"],
            "success_threshold": request.form["success_threshold"],
            "unfit_threshold": request.form["unfit_threshold"],
            "max_session_duration": request.form["max_session_duration"],
            "session_interval": request.form["session_interval"],
            "max_trial_per_session": request.form["max_trial_per_session"],
            "display_neutral_after_time": request.form["display_neutral_after_time"],
            "stimulus_image": request.form["stimulus_image"],
            "neutral_image": request.form["neutral_image"],
            "ROC1_x1": request.form["ROC1_x1"],
            "ROC1_x2": request.form["ROC1_x2"],
            "ROC1_y1": request.form["ROC1_y1"],
            "ROC1_y2": request.form["ROC1_y2"],
            "start_x1": request.form["start_x1"],
            "start_x2": request.form["start_x2"],
            "start_y1": request.form["start_y1"],
            "start_y2": request.form["start_y2"]
        }

        with open("pre_training_parameters.json", "w") as param_file:
            json.dump(pre_training_parameters, param_file)
            return "Pre-training parameters saved."
        
        command = [
        "python",  # Replace with the appropriate Python interpreter if needed
        "pre_training_client.py",
        f"--tank_ID={pre_training_parameters['tank_ID']}",
        f"--max_pretraining_days={pre_training_parameters['max_pretraining_days']}",
        f"--max_sessions_per_day={pre_training_parameters['max_sessions_per_day']}",
        f"--stimulus_display_time={pre_training_parameters['stimulus_display_time']}",
        f"--success_threshold={pre_training_parameters['success_threshold']}",
        f"--max_session_duration={pre_training_parameters['max_session_duration']}",
        f"--session_interval={pre_training_parameters['session_interval']}",
        f"--max_sessions_pretraining={pre_training_parameters['max_sessions_pretraining']}",
        f"--max_trial_per_session={pre_training_parameters['max_trial_per_session']}",
        f"--display_neutral_after_time={pre_training_parameters['display_neutral_after_time']}",
        f"--stimulus_image={pre_training_parameters['stimulus_image']}",
        f"--neutral_image={pre_training_parameters['neutral_image']}",
        f"--ROC1_x1={pre_training_parameters['ROC1_x1']}",
        f"--ROC1_x2={pre_training_parameters['ROC1_x2']}",
        f"--ROC1_y1={pre_training_parameters['ROC1_y1']}",
        f"--ROC1_y2={pre_training_parameters['ROC1_y2']}",
        f"--start_x1={pre_training_parameters['start_x1']}",
        f"--start_x2={pre_training_parameters['start_x2']}",
        f"--start_y1={pre_training_parameters['start_y1']}",
        f"--start_y2={pre_training_parameters['start_y2']}"
        ]
        # If pre-training has not been executed, execute it immediately
        if not pre_training_executed:
            subprocess.run(command)
            pre_training_executed = True

    return render_template("experiment_form.html")

# Define a route to save training parameters
@app.route("/save_training_parameters", methods=["POST"])
def save_training_params():
    global training_parameters

    # Get training parameters from the form
    training_parameters = {
        "max_training_days": request.form["max_training_days"],
        "max_sessions_per_day_train": request.form["max_sessions_per_day_train"],
        "success_threshold_train": request.form["success_threshold_train"],
        "unfit_threshold_train": request.form["unfit_threshold_train"],
        "max_session_duration_train": request.form["max_session_duration_train"],
        "session_interval_train": request.form["session_interval_train"],
        "max_trial_per_session_train": request.form["max_trial_per_session_train"],
        "display_neutral_after_time_train": request.form["display_neutral_after_time_train"],
        "correct_stimulus_train": request.form["correct_stimulus_train"],
        "incorrect_stimulus_train": request.form["incorrect_stimulus_train"],
        "neutral_image_train": request.form["neutral_image_train"],
        "left_ROI_x1": request.form["left_ROI_x1"],
        "left_ROI_x2": request.form["left_ROI_x2"],
        "left_ROI_y1": request.form["left_ROI_y1"],
        "left_ROI_y2": request.form["left_ROI_y2"],
        "right_ROI_x1": request.form["right_ROI_x1"],
        "right_ROI_x2": request.form["right_ROI_x2"],
        "right_ROI_y1": request.form["right_ROI_y1"],
        "right_ROI_y2": request.form["right_ROI_y2"]
    }

    # Save the training parameters to a JSON file
    with open("training_parameters.json", "w") as param_file:
        json.dump(training_parameters, param_file)

    return "Training parameters saved."

if __name__ == "__main__":
    app.run(debug=True)

