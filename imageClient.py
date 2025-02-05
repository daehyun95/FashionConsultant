import os
from openai import AzureOpenAI
import requests
from PIL import Image
import json
from dotenv import load_dotenv
from requests.exceptions import RequestException
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import io
import time


# Load environment variables
load_dotenv()

client = AzureOpenAI(
  azure_endpoint="https://wjdeo-m6ikto09-swedencentral.cognitiveservices.azure.com", 
  api_key="DlfgZRjLJVMaNISxMV7cWckqWI0e2F7r6XQwJqr6CSOvtwMOo5OYJQQJ99BAACfhMk5XJ3w3AAAAACOGenNo",  
  api_version="2024-02-01"
)

# Azure Blob Storage configuration
connection_string = "DefaultEndpointsProtocol=https;AccountName=fashionstroage;AccountKey=OcJdDpurIkRdI8noNTzzhdVYwJMWMM1xaQjol4cZ4kVL7ZU5fiUQZkILdBQy+C/svtNVEf8UrB1f+AStxJ7xBQ==;EndpointSuffix=core.windows.net"  # Replace with your Azure Blob Storage connection string
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "fashion-images"
container_client = blob_service_client.get_container_client(container_name)

def retry_request(func, retries=5, delay=5):
    for attempt in range(retries):
        try:
            return func()
        except RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e


def generate_fashion_image(fashion_report):
    # Retry the image generation request
    result = retry_request(lambda: client.images.generate(
        model="dall-e-3",  # The model you're using for image generation (DALL·E 3)
        prompt=fashion_report,  # Pass the fashion suggestion to the DALL·E model
        n=1,  # Number of images to generate
        size="1024x1024"
    ))

    try:
        # Check if the result has 'data' and access the URL correctly
        if hasattr(result, 'data') and len(result.data) > 0:
            image_url = result.data[0].url  # Use the proper attribute for the image URL

            # Download the image from the generated URL
            generated_image = requests.get(image_url).content

            # Create a buffer for the image to save locally and upload to Azure
            image = Image.open(io.BytesIO(generated_image))
            
            # Show the image locally (on your machine)
            image.show()

            # Set the directory for storing the generated image locally (for testing purposes)
            image_dir = os.path.join(os.curdir, 'images')

            # Create the directory if it doesn't exist
            if not os.path.isdir(image_dir):
                os.mkdir(image_dir)

            # Define the local image file path
            image_path = os.path.join(image_dir, 'fashion_image.png')

            # Save the image locally
            with open(image_path, "wb") as image_file:
                image_file.write(generated_image)

            print(f"Image has been saved to: {image_path}")

            # Now upload the image to Azure Blob Storage
            # Create a blob client using the container and the blob name
            blob_client = blob_service_client.get_blob_client(container=container_name, blob="fashion_image.png")

            # Upload the image to Azure Blob Storage
            blob_client.upload_blob(generated_image, overwrite=True)
            print("Image successfully uploaded to Azure Blob Storage.")

        else:
            print("No image data returned in the response.")
    
    except Exception as e:
        print(f"An error occurred while generating or uploading the image: {e}")