import os
from openai import AzureOpenAI
import requests
from PIL import Image
import json
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

client = AzureOpenAI(
  azure_endpoint="https://wjdeo-m6ikto09-swedencentral.cognitiveservices.azure.com", 
  api_key="DlfgZRjLJVMaNISxMV7cWckqWI0e2F7r6XQwJqr6CSOvtwMOo5OYJQQJ99BAACfhMk5XJ3w3AAAAACOGenNo",  
  api_version="2024-02-01"
)

def generate_fashion_image(fashion_report):
    # Use the fashion report as the prompt to generate the fashion image
    result = client.images.generate(
        model="dall-e-3",  # The model you're using for image generation (DALL·E 3)
        prompt=fashion_report,  # Pass the fashion suggestion to the DALL·E model
        n=1  # Number of images to generate
    )

    # Get the JSON response
    json_response = json.loads(result.model_dump_json())

    # Set the directory for storing the generated image
    image_dir = os.path.join(os.curdir, 'images')

    # Create the directory if it doesn't exist
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Define the image file path
    image_path = os.path.join(image_dir, 'fashion_image.png')

    # Retrieve the generated image URL from the response
    image_url = json_response["data"][0]["url"]  # Extract image URL from the response
    generated_image = requests.get(image_url).content  # Download the image

    # Save the image locally
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)

    # Open and display the image
    image = Image.open(image_path)
    image.show()

    print(f"Image has been saved to: {image_path}")
