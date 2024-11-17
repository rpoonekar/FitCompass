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

# Initialize Flask app
app = Flask(__name__)

# Home route to display the chat interface
@app.route('/')
def home():
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

if __name__ == "__main__":
    app.run(debug=True)