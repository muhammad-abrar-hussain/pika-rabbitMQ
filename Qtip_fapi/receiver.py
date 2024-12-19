"""
RabbitMQ Consumer Module

This script initializes RabbitMQ consumers for two queues: `start_learning_Queue` and `question_Queue`.
It processes incoming messages from these queues and performs corresponding actions, such as extracting text from
files or processing questions.

Features:
- Uses `pika` for RabbitMQ messaging.
- Utilizes `ThreadPoolExecutor` for handling tasks asynchronously.
- Implements multithreading to run multiple consumers in parallel.
- Fetches data from FastAPI endpoints for further processing.
- Handles graceful shutdown on keyboard interruption.

Attributes:
    RABBITMQ_HOST (str): The hostname for RabbitMQ.
    START_LEARNING_QUEUE (str): Queue name for processing "start learning" tasks.
    QUESTION_QUEUE (str): Queue name for processing "question" tasks.
    GET_PRESENTATION_FILES (str): FastAPI endpoint to fetch presentation file paths.
    GET_QUESTION_BODY (str): FastAPI endpoint to fetch question details.
    executor (ThreadPoolExecutor): Thread pool executor for asynchronous task handling.
"""

import pika, sys, os, requests
from concurrent.futures import ThreadPoolExecutor
from textExtract import extract_text
from threading import Thread

RABBITMQ_HOST = 'localhost'
START_LEARNING_QUEUE = 'start_learning_Queue'
QUESTION_QUEUE = 'question_Queue'

# FastAPI API endpoint
GET_PRESENTATION_FILES = "http://127.0.0.1:8001/knowledgebase"
GET_QUESTION_BODY = "http://127.0.0.1:8001/question"

executor = ThreadPoolExecutor(max_workers=5)


def process_files(presentation_id, files):
    """
    Processes files for the `start_learning_Queue` messages.

    Args:
        presentation_id (str): The ID of the presentation whose files are being processed.
        files (list): List of file information dictionaries containing file paths.

    Actions:
        - Extracts text from the files provided in the `files` list.
        - Prints extracted text for debugging.

    Note:
        Uses a test file path for demonstration purposes. Replace with actual file paths from `files`.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, "assets", "test.pdf")

    extracted_texts = []

    for file_info in files:
        file_path = file_info.get('filepath')
        if file_path:
            try:
                text = extract_text(test_file_path)
                extracted_texts.append(text + "\n")
            except Exception as e:
                print(f"Error extracting text from {test_file_path}: {e}")
        else:
            print("File path not found in file info.")
    print(extracted_texts)
    print("".join(extracted_texts))

def process_question(question_data):
    """
    Processes questions for the `question_Queue` messages.

    Args:
        question_data (dict): A dictionary containing question details fetched from the API.

    Actions:
        - Prints received question data for debugging.
    """
    print(f"Received a new question: {question_data}")


def start_learning_callback(ch, method, properties, body):
    """
        RabbitMQ callback function for `start_learning_Queue`.

        Args:
            ch: The channel object.
            method: The delivery method.
            properties: Message properties.
            body (bytes): Message body containing the presentation ID.

        Actions:
            - Fetches file paths for a given presentation ID via the FastAPI endpoint.
            - Submits file processing tasks to the thread pool.
            - Acknowledges message receipt.
        """

    presentation_id = body.decode()
    response = requests.get(f"{GET_PRESENTATION_FILES}/{presentation_id}")
    if response.status_code == 200:
        files = response.json().get('files', [])
        executor.submit(process_files, presentation_id, files)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(f"Error: {response.status_code}, {response.json()}")


def question_callback(ch, method, properties, body):
    """
    RabbitMQ callback function for `question_Queue`.

    Args:
        ch: The channel object.
        method: The delivery method.
        properties: Message properties.
        body (bytes): Message body containing the question ID.

    Actions:
        - Fetches question details for a given question ID via the FastAPI endpoint.
        - Submits question processing tasks to the thread pool.
        - Acknowledges message receipt.
    """

    question_id = body.decode()
    response = requests.get(f"{GET_QUESTION_BODY}/{question_id}")

    if response.status_code == 200:
        question = response.json()
        executor.submit(process_question, question)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_learning_consumer():
    """
    Initializes the RabbitMQ consumer for `start_learning_Queue`.

    Actions:
        - Declares the `start_learning_Queue` queue.
        - Consumes messages from the queue.
        - Prints logs indicating consumer activity.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=START_LEARNING_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=START_LEARNING_QUEUE, on_message_callback=start_learning_callback)

    print(f"Waiting for messages in queue '{START_LEARNING_QUEUE}'...")
    channel.start_consuming()


def question_consumer():
    """
    Initializes the RabbitMQ consumer for `question_Queue`.

    Actions:
        - Declares the `question_Queue` queue.
        - Consumes messages from the queue.
        - Prints logs indicating consumer activity.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUESTION_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUESTION_QUEUE, on_message_callback=question_callback)

    print(f"Waiting for messages in queue '{QUESTION_QUEUE}'...")
    channel.start_consuming()


def main():
    """
    Main function to start RabbitMQ consumers for both queues.

    Actions:
        - Launches the `start_learning_consumer` and `question_consumer` in separate threads.
        - Ensures the main thread stays alive while consumers are running.
        - Handles graceful shutdown on keyboard interruption.
    """

    # Run both consumers in separate threads
    learning_thread = Thread(target=start_learning_consumer)
    question_thread = Thread(target=question_consumer)

    learning_thread.start()
    question_thread.start()

    # Keep the main thread alive
    learning_thread.join()
    question_thread.join()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
