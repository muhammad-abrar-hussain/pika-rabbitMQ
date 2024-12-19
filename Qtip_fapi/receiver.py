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
        Processes the files for start_learning_Queue.
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
    Processes the questions for question_Queue.
    """
    print(f"Received a new question: {question_data}")


def start_learning_callback(ch, method, properties, body):
    """
    Callback for start_learning_Queue.
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
    Callback for question_Queue.
    """
    question_id = body.decode()
    response = requests.get(f"{GET_QUESTION_BODY}/{question_id}")

    if response.status_code == 200:
        question = response.json()
        executor.submit(process_question, question)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_learning_consumer():
    """
    Consumer for start_learning_Queue.
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
    Consumer for question_Queue.
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
    Main function to start both consumers.
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
