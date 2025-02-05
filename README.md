# Virtual Fashion Consultant

This project is a web-based fashion consultant tool built using Python, Flask, and OpenAI's DALL·E 3 API to generate fashion images based on user inputs. The tool uses machine learning to suggest fashion styles and generate images for various events and occasions.

You can access the live version of the application at: [Fashion Consultant Live](https://fashionconsultantnew.azurewebsites.net/)


## Features

- **User input**: The user can input details such as event type, style, garment type, sex and age, and additional preferences (e.g., color).
- **Fashion suggestions**: Based on the user input, the system provides a fashion report with suitable clothing suggestions.
- **Image generation**: The tool generates a fashion image using OpenAI's DALL·E 3 model based on the generated fashion report.
- **Azure integration**: The project is designed to run on Azure App Services, using Azure Blob Storage for storing generated images.



## Installation

Follow these steps to set up the project locally:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/virtual-fashion-consultant.git
    cd virtual-fashion-consultant
    ```

2. **Create and activate a virtual environment**:

    For **Windows**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    For **Mac/Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:

    Create a `.env` file in the root directory of the project, and add the following environment variables:

    ```
    OPENAI_API_KEY=<your-openai-api-key>
    AZURE_STORAGE_CONNECTION_STRING=<your-azure-blob-storage-connection-string>
    ```

    Replace `<your-openai-api-key>` and `<your-azure-blob-storage-connection-string>` with your actual API keys and connection strings.

## Running Locally

To run the project locally, you can start the Flask app using Gunicorn with the following command:


```bash
gunicorn app:app --timeout 180 --workers 4 --worker-class gevent
```

After the server starts, open your browser and navigate to http://127.0.0.1:8000 to interact with the fashion consultant.

### Dependencies
- **Flask**: A lightweight web framework for Python.
- **gunicorn**: A Python WSGI HTTP server for UNIX.
- **requests**: HTTP library to make requests to APIs.
- **Pillow**: Image processing library to open and display images.
- **OpenAI**: Python client for OpenAI's API.
- **Azure SDK**: To interact with Azure services like Blob Storage.
- **dotenv**:  Loads environment variables from a .env file.

You can find the full list of dependencies in requirements.txt.



## Project Structure

consultant
├── app.py                     # Main application entry point (Flask app)
├── chatClient.py               # Handles user interaction and image generation
├── imageClient.py              # Handles interaction with OpenAI DALL·E 3 API
├── requirements.txt            # Python dependencies
├── Procfile                    # Azure-specific deployment file
├── .env                        # Configuration file with API keys and connection strings
├── templates/                  # Folder for HTML templates
│   └── index.html              # Main HTML page for the app
├── static/                     # Folder for static files (CSS, JS, images)
│   └── style.css               # CSS styles for the app
├── images/                     # Folder to store generated images (if saved locally)
└── README.md                   # This file
             