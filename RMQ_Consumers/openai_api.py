import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

MAX_TOKENS = 4000  # Safe token limit per request for GPT-4


def split_into_chunks(text, max_tokens):
    """
    Split text into smaller chunks to fit within the token limit.

    Args:
        text (str): The input text to split.
        max_tokens (int): Maximum token limit per chunk.

    Returns:
        list: List of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) > max_tokens:
            chunks.append(" ".join(current_chunk[:-1]))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def open_api_get_topics(file_content):
    # Split content into manageable chunks
    chunks = split_into_chunks(file_content, MAX_TOKENS)
    topics = []

    # for chunk in chunks:
    for index, chunk in enumerate(chunks):
        if index >=2:
            break
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
                Extract the main topics from the following content and summarize them. 
                Each topic should have a title and a brief summary:

                {chunk}

                Format the response as a JSON array of objects with 'title' and 'summary' keys.

                I will ask questions related to the content or topics. Your task is to assess the validity of each question. 
                If the question is valid, respond with "1"; otherwise, respond with "0." 
                If the question is valid, also include the relevant topic title to which the question pertains. 
                The output should always be in JSON format only, without any additional explanations.
            """}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            result = response['choices'][0]['message']['content']

            data = {
                "result": result,
                "id": response["id"]
            }

            topics.append(data)
        except Exception as e:
            print(f"Error during OpenAI API request: {e}")
            return None

    return topics


def open_api_get_question_relevancy(question, topics):
    """
    Assess the relevance of a question to the provided topics.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"""
            I will ask questions related to the content or topics. Your task is to assess the validity of each question. 
            If the question is valid, respond with "True"; otherwise, respond with "False." 
            If the question is valid, also include the relevant topic title to which the question pertains. 
            The output should always be in JSON format only, without any additional explanations.

            Question: {question}
            Topics: {topics}
        """}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        result = response['choices'][0]['message']['content']
        return json.loads(result)

    except Exception as e:
        print(f"Error during OpenAI API request: {e}")
        return None