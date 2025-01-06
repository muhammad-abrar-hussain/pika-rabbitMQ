import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def open_api_get_topics(files_content):
    """
    Interact with OpenAI API to generate topics based on the provided content.

    Args:
        content (str): The text content extracted from files.

    Returns:
        dict: A dictionary containing the generated topics and metadata, or an error message if the API call fails.
    """
    try:
        prompt = (
            "Extract the main topics from the following content and summarize them. "
            "Each topic should have a title and a brief summary:\n\n"
            f"{files_content}\n\n"
            "Format the response as a JSON array of objects with 'title' and 'summary' keys."
        )

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )

        # Parse the response
        generated_text = response.choices[0].text.strip()

        # Convert the response to a Python dictionary
        topics = eval(generated_text)  # Use `json.loads` if the response is in JSON string format

        return topics
    except Exception as e:
        return {"error": str(e)}
