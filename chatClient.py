import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import re
from imageClient import generate_fashion_image  # Import the generate function from imageClient.py

# Load environment variables
load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-08-01-preview"
)

# Select the model
model = os.getenv("CHAT_COMPLETION_NAME")

# Data to store user inputs dynamically
user_data = {
    "event": [],
    "style": [],
    "garment_type": [],
    "sex_age": [],
    "additional_details": []
}

# Function to reset the user data when starting over
def reset_user_data():
    global user_data
    user_data = {
        "event": [],
        "style": [],
        "garment_type": [],
        "sex_age": [],
        "additional_details": []
    }

# Function to interact with GPT-3.5 to determine the action (add, edit, delete)
def analyze_user_action(user_input):
    context = f"""
    The user said: '{user_input}'. 
    Please analyze if the user wants to:
    1. Add new information to their user_data - if user doesn't indicate, it is add
    2. Edit an existing entry in their user_data
    3. Delete or remove an entry from their user_data
    
    Output the intent: 
    - Add: if the user wants to add new information
    - Edit: if the user wants to edit an existing field
    - Delete: if the user wants to delete or remove a field
    """

    response = client.chat.completions.create(
        model="gpt-35-turbo-16k", 
        messages=[
            {"role": "system", "content": "Analyze the user's input and determine if they want to add, edit, or delete data."},
            {"role": "user", "content": context},
        ]
    )

    return response.choices[0].message.content.strip()


# Function to interact with GPT-3.5 for categorizing the input (event, style, garment_type, etc.)
def categorize_user_input(user_input):
    context = f"""
    The user said: '{user_input}'. 
    Extract and categorize the following information only if it is explicitly mentioned in the user's input:
        - event (e.g., 'wedding', 'birthday', 'interview', 'party',  etc.)
        - style (e.g., 'casual', 'formal', etc.)
        - garment_type (e.g., 'dress', 'shirt', 'jeans', etc.)
        - sex_age (e.g., 'female, male, boy, girl, 25 years old, 20 years old, 15 years old, 35, female 15, male 26 years old, 15 boy')
        - additional_details (e.g., 'color preference navy, no additional details, no, none, nope') - it could be none

    Other fashion details not related to event, style, garment_type or sex_age will go to the additional details
    Only present the categories that the user explicitly mentioned. 
    Do not include any categories that were not mentioned by the user.
    If not mentioned, never present the category that is not mentioned

    Output the intent: 
    - event: only if it is mentioned
    - style: only if it is mentioned
    - garment_type: only if it is mentioned
    - sex_age: only if it is mentioned
    - additional_details: only if it is mentioned

    """

    response = client.chat.completions.create(
        model="gpt-35-turbo-16k",  # Or any model you are using
        messages=[
            {"role": "system", "content": "Categorize the user's input into the appropriate fields."},
            {"role": "user", "content": context},
        ]
    )

    return response.choices[0].message.content.strip()

# Function to interact with GPT model to generate fashion suggestion based on user data
def fashion_suggestion(user_data):
    # Construct the context dynamically based on the collected user data
    context = "Given the following user preferences, please suggest a fashion style:\n"

    if user_data["event"]:
        context += f"Event: {', '.join(user_data['event'])}\n"
    if user_data["style"]:
        context += f"Style: {', '.join(user_data['style'])}\n"
    if user_data["garment_type"]:
        context += f"Garment Type: {', '.join(user_data['garment_type'])}\n"
    if user_data["sex_age"]:
        context += f"Sex/Age: {', '.join(user_data['sex_age'])}\n"
    if user_data["additional_details"]:
        context += f"Additional Details: {', '.join(user_data['additional_details'])}\n"


    # Interact with GPT to generate a fashion suggestion
    response = client.chat.completions.create(
        model="gpt-35-turbo-16k",  # Or any model you are using
        messages=[
            {"role": "system", "content": "You are a helpful fashion consultant. Based on the provided details, suggest a fashion style that matches to the event."},
            {"role": "user", "content": context},
        ]
    )

    return response.choices[0].message.content.strip()

# Function to map user responses to the correct user_data field
def map_user_response(user_input):
    # Step 1: Analyze user's intent (add, edit, delete) with GPT-3.5
    action = analyze_user_action(user_input)
    print("Action Analysis:", action)

    # Step 2: Categorize the user's input into the fields (event, style, etc.) with another GPT-3.5
    categorization = categorize_user_input(user_input)
    print("Categorization:", categorization)


    # Based on action, process categorization and update user_data accordingly
    if "add" in action.lower():
        # If the action is to add new data, extract relevant data from the categorization and append it to the user_data
        event_match = re.search(r"event:\s*(.*?)(?=\n|$)", categorization)
        style_match = re.search(r"style:\s*(.*?)(?=\n|$)", categorization)
        garment_type_match = re.search(r"garment_type:\s*(.*?)(?=\n|$)", categorization)
        sex_age_match = re.search(r"sex_age:\s*(.*?)(?=\n|$)", categorization)
        additional_details_match = re.search(r"additional_details:\s*(.*?)(?=\n|$)", categorization)

        if event_match:
            user_data["event"].append(event_match.group(1).strip())
        if style_match:
            user_data["style"].append(style_match.group(1).strip())
        if garment_type_match:
            user_data["garment_type"].append(garment_type_match.group(1).strip())
        if sex_age_match:
            user_data["sex_age"].append(sex_age_match.group(1).strip())
        if additional_details_match:
            user_data["additional_details"] = [additional_details_match.group(1).strip()]

    elif "edit" in action.lower():
        # If the action is to edit existing data, overwrite the current values with the new input
        event_match = re.search(r"event:\s*(.*?)(?=\n|$)", categorization)
        style_match = re.search(r"style:\s*(.*?)(?=\n|$)", categorization)
        garment_type_match = re.search(r"garment_type:\s*(.*?)(?=\n|$)", categorization)
        sex_age_match = re.search(r"sex_age:\s*(.*?)(?=\n|$)", categorization)
        additional_details_match = re.search(r"additional_details:\s*(.*?)(?=\n|$)", categorization)

        if event_match:
            user_data["event"] = [event_match.group(1).strip()]
        if style_match:
            user_data["style"] = [style_match.group(1).strip()]
        if garment_type_match:
            user_data["garment_type"] = [garment_type_match.group(1).strip()]
        if sex_age_match:
            user_data["sex_age"] = [sex_age_match.group(1).strip()]
        if additional_details_match:
            user_data["additional_details"] = [additional_details_match.group(1).strip()]

    elif "delete" in action.lower() or "remove" in action.lower() or "forget" in action.lower():
        # Logic to delete or clear the data
        if "event" in categorization:
            user_data["event"] = []
        if "style" in categorization:
            user_data["style"] = []
        if "garment_type" in categorization:
            user_data["garment_type"] = []
        if "sex_age" in categorization:
            user_data["sex_age"] = []
        if "additional_details" in categorization:
            user_data["additional_details"] = []

    # Print updated user data for verification
    print("Updated user_data:", user_data)

# Function to generate the next question or response based on user data
def generate_response():
    # Check for missing user data and ask the corresponding question
    if not user_data["event"]:
        return "What occasion or event do you need an outfit for? (e.g., party, wedding, casual event)"
    
    if not user_data["style"]:
        return "What style would you like? (e.g., casual, formal, sporty)"
    
    if not user_data["garment_type"]:
        return "What type of garment do you want? (e.g., dress, suit, jacket, shirt)"
    
    if not user_data["sex_age"]:
        return "Please provide your sex and age (e.g., male, female, 25 years old)."
    
    if not user_data["additional_details"]:
        return "Any additional preferences? (e.g., color, fabric, accessories)"
    
    # Once all fields are filled, generate a fashion suggestion
    fashion_report = fashion_suggestion(user_data)

    print("Fashion Report:", fashion_report)
    # Now generate the fashion image based on the fashion suggestion
    generate_fashion_image(fashion_report)
    
    # Ask to restart
    return fashion_report + "\nDo you like it?"


# The response function to handle incoming messages
def response(user_input):
    global user_data

    # Reset the user data when starting a new session
    if user_input.lower() == "yes":
      reset_user_data()
      return "Let's start over. Could you please tell me about the outfit you're looking for?"
    if user_input.lower() == "no":
      return "Thank you for using the fashion consultant. Have a great day!"
    
    # Process user input to update user data (similar to your previous logic)
    map_user_response(user_input)

    # Generate the next response
    return generate_response()
    