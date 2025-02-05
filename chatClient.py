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
    
    Please analyze the user's input and determine the intended action with the following criteria:
    
    1. **Add**: If the user is providing new information that has not been mentioned before or is not clear if it exists in the data. 
       - Example: "I want a red dress for my wedding" (Adding new data for wedding event with a new color preference).
       - If the user simply describes their preference or a new item, treat it as an "add" action.
       - Even if the word "add" is not mentioned, look for requests that imply adding new information such as "want," "plan," or "choose."

    2. **Edit**: If the user wants to modify an existing entry. This would typically involve:
       - Changing previously mentioned details.
       - Example: "Actually, I want a black dress instead of red for my wedding."
       - Look for indications where they are adjusting previously provided data, rather than adding a new piece.
       - Look for words like "change," "modify," "adjust," "update," "replace."

    3. **Delete**: If the user wants to remove a specific item or piece of information. This could be indicated explicitly or implied by phrases like:
       - "Forget about the wedding dress" or "I no longer want to include a dress."
       - If the user requests to remove a detail or stop considering something, treat it as a delete action.
       - Look for negative phrases like "remove," "forget," "delete," or "stop considering."

    Please ensure the following:
    - If the input indicates a modification or change of an existing entry, classify it as "Edit".
    - If it is a direct removal or negation of data, classify it as "Delete".
    - If no prior context is mentioned (like a first-time request), classify it as "Add".
    - If the user mentions something like "trip," "vacation," or "celebrate," treat it as an **event** (in this case, "travel").
    - Words like "want," "choose," or "plan" generally suggest that the user wants to **add** something new.
    - If the user requests specific details (e.g., "blue," "floral," "formal"), treat them as **attributes** of the main data, such as color or style.

    Output the intent:
    - "Add": for introducing new information or requests
    - "Edit": for changes to existing information
    - "Delete": for requests to remove something
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

    Your task is to extract and categorize the following information based on context, even if the key terms are not explicitly mentioned:
    
    1. **Event/Occasion**: Any mention of a significant event or occasion like "wedding," "vacation," "birthday," "party," or "celebrate." 
       - Look for context clues like "celebrate," "trip," "want to go," "have to prepare," or "plan a."

    2. **Style**: Identify any references to the style or look of an outfit (e.g., casual, formal, boho, chic, elegant, vintage, etc.).
       - Words like "comfortable," "casual," "elegant," or "modern" can hint at style preferences.

    3. **Garment Type**: Recognize clothing items like "dress," "shirt," "jeans," "blouse," etc., even if they're part of a broader description.
       - Look for words like "wear," "outfit," "clothing," or "pick."

    4. **Sex/Age**: Identify gender and age details when the user mentions them.
       - Words like "boy," "girl," "15 years old," or "teenager" will help categorize this.

    5. **Additional Details**: Extract any other relevant details like color preferences, fabric choices, or accessories.
       - Look for details like "color," "material," "style," or "specific details."

    **Important Notes**:
    - Don't rely solely on exact matches—use the context to infer categories.
    - If the user mentions "trip" or "celebrate," infer that they are referring to an **event** (like "travel" or "vacation").
    - If the input includes any hints of specific preferences or choices, associate them with the appropriate category.

    Output should be appeared only
    - event: if an event is mentioned or inferred
    - style: if a style preference is mentioned
    - garment_type: if a clothing item is mentioned
    - sex_age: if sex and age are mentioned
    - additional_details: if specific attributes like color, fabric, etc., are mentioned

    Output the response in the following format only if it is mentioned (without any extra labels):
    Categorization:
    - event: <event>
    - style: <style>
    - garment_type: <garment_type>
    - sex_age: <sex_age>
    - additional_details: <additional_details>
    
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

    prompt = f"""
    You are a professional fashion consultant. Based on the user's preferences and the event, please generate a fashion suggestion that meets the following criteria:

    - **Event**: Consider the occasion (e.g., wedding, party, interview). Is it formal or casual? Provide a suggestion that fits well for the event.
    - **Style**: The user may have a specific style (e.g., casual, formal, boho). Choose clothing that matches this style. Ensure that the outfit feels cohesive and stylish.
    - **Garment Type**: Suggest specific garments (e.g., dress, shirt, pants). Ensure the chosen garment complements the event and style.
    - **Sex/Age**: Tailor the suggestion to the user’s age and gender.
    - **Additional Details**: Consider any extra details, such as color preferences or specific design elements. Is the user looking for a bright, bold color or something more neutral? Take those preferences into account.
    
    Provide a clear, step-by-step suggestion, considering the following:
    - Seasonality: If it's a summer or winter event, suggest appropriate fabrics (e.g., lightweight cotton or warm wool).
    - Comfort: Ensure the suggested outfit is comfortable for the user, especially if it's for an event they’ll be at for a long time.
    - Budget: If the user has mentioned a budget (e.g., affordable), suggest options that fall within reasonable price ranges.
    - Accessories: Offer accessory ideas like shoes, jewelry, or bags that would complement the outfit.
    - Fabrics: Mention specific fabrics that would be most appropriate for the suggested garment (e.g., silk for a formal wedding dress, denim for a casual outing).
    - Occasion Appropriateness: Ensure the outfit is respectful and suitable for the event (e.g., no over-the-top outfits for a professional interview).

    Here’s the user’s information:
    {context}
    Based on this, suggest an outfit that is appropriate for the occasion, stylish, and fits the user’s preferences.
    """

    # Interact with GPT to generate a fashion suggestion
    response = client.chat.completions.create(
        model="gpt-35-turbo-16k",  # Or any model you are using
        messages=[
            {"role": "system", "content": "You are a helpful fashion consultant. Provide detailed, customized fashion suggestions based on the user's input."},
            {"role": "user", "content": prompt},
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
    