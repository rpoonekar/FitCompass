from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)



# Load model and scaler
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'model.pkl')
scaler_path = os.path.join(current_dir, 'scaler.pkl')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Feature mappings
activity_level_mapping = {
    'sedentary': 0,
    'lightly active': 1,
    'moderately active': 2,
    'very active': 3
}

numerical_features = ['Current Weight (lbs)', 'Gender', 'Age', 'Final Weight (lbs)', 'Physical Activity Level', 'Duration (weeks)']

@app.route('/')
def base():
    return render_template('base.html')  # Serves the frontend


@app.route('/workout')
def workout():
    # Render the Workout Plan page
    return render_template('workout.html')

@app.route('/Livetracker')
def livetracker():
    return render_template("tracker.html")


def macro_calculator(calories):
    fat_percent = 0.37
    protein_percent = 0.11
    carbs_percent = 0.52

    protein_calories = calories * protein_percent
    fat_calories = calories * fat_percent
    carbs_calories = calories * carbs_percent

    protein_grams = protein_calories / 4
    fat_grams = fat_calories / 9
    carbs_grams = carbs_calories / 4

    return {
        "protein_calories": round(protein_calories, 2),
        "protein_grams": round(protein_grams, 2),
        "fat_calories": round(fat_calories, 2),
        "fat_grams": round(fat_grams, 2),
        "carbs_calories": round(carbs_calories, 2),
        "carbs_grams": round(carbs_grams, 2),
    }


#predictive model


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input data
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract and preprocess inputs
        weight = float(data.get("weight"))
        gender = data.get("gender").strip().upper()
        age = int(data.get("age"))
        goal_weight = float(data.get("goal_weight"))
        activity_level = data.get("activity_level").strip().lower()
        duration = int(data.get("duration"))

        gender_encoded = 1 if gender == 'M' else 0
        activity_level_encoded = activity_level_mapping.get(activity_level, -1)

        if activity_level_encoded == -1:
            return jsonify({"error": f"Unrecognized Physical Activity Level: {activity_level}"}), 400

        # Prepare input data with correct feature names
        input_data = pd.DataFrame(
            [[weight, gender_encoded, age, goal_weight, activity_level_encoded, duration]],
            columns=numerical_features
        )

        print(f"Input data before scaling: {input_data}")
        input_data_scaled = scaler.transform(input_data)
        print(f"Input data after scaling: {input_data_scaled}")

        # Predict daily calories
        predicted_calories = model.predict(input_data_scaled)[0]

        # Calculate macros
        macros = macro_calculator(predicted_calories)

        return jsonify({
            "predicted_calories": round(predicted_calories, 2),
            "macros": macros
        })

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500



#Chatbot


import os
import boto3
from flask import Flask, render_template, request, jsonify
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up AWS credentials and Boto3 client
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-west-2",
)

# The model ID for the model you want to use
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"



# Home route to display the chat interface
@app.route('/chatbot')
def chatbot():
    return render_template('index.html')

# Route to handle user input and generate response
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    user_message = f"""
    System: You are a virtual assistant specializing in health, fitness, and recipes. Only respond to prompts related to these topics. If the prompt is unrelated, politely redirect the user to ask health or recipe-related queries.
    Prompt: {user_message}
    """

    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]

    try:
        streaming_response = client.converse_stream(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
        )

        response_text = ""
        for chunk in streaming_response["stream"]:
            if "contentBlockDelta" in chunk:
                text = chunk["contentBlockDelta"]["delta"]["text"]
                response_text += text
        response_text = response_text.replace("\n", "<br>")
        return jsonify({"response": response_text.strip()})

    except (ClientError, Exception) as e:
        return jsonify({"response": f"ERROR: Can't invoke '{model_id}'. Reason: {e}"})

from flask import Flask, render_template, Response
import cv2
from process_frame import ProcessFrame
from utils import get_mediapipe_pose
from thresholds import get_thresholds_beginner


# Setup video processing
thresholds = get_thresholds_beginner()
live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
pose = get_mediapipe_pose()

cap = cv2.VideoCapture(1)  # Use the first webcam
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

@app.route('/')
def index():
    return render_template('video.html')

def gen():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Process frame
        frame, _ = live_process_frame.process(frame, pose)

        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            # Yield frame in HTTP multipart response format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video')
def video():
    return render_template("video.html")

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')











if __name__ == "__main__":
    app.run(debug=True)
