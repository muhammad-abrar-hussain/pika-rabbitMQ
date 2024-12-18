import pika, sys, os, requests
from concurrent.futures import ThreadPoolExecutor
from textExtract import extract_text

# RabbitMQ connection details
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'start_learning_Queue'

# FastAPI API endpoint
FASTAPI_ENDPOINT = "http://127.0.0.1:8001/knowledgebase"

executor = ThreadPoolExecutor(max_workers=5)


def process_files(presentation_id, files):


    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, "assets", "sample2.pdf")

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



def callback(ch, method, properties, body):

    presentation_id = body.decode()
    response = requests.get(f"{FASTAPI_ENDPOINT}/{presentation_id}")

    if response.status_code == 200:
        files = response.json().get('files', [])

        # Submit file processing task to the thread pool
        executor.submit(process_files, presentation_id, files)
    else:
        print(f"Error: {response.status_code}, {response.json()}")

    # if response.status_code == 200:
    #     files = response.json()['files']
    #     print(f"Files for presentation_id {presentation_id}: {files}")
    #
    #     for file_info in files:
    #         file_path = file_info.get('filepath')
    #         if file_path:
    #             try:
    #                 file_path = "./assets/test.pdf"
    #                 extracted_text = extract_text(file_path)
    #                 print(f"Extracted text from {file_path}:\n{extracted_text}\n","=======================")
    #             except Exception as e:
    #                 print(f"Error extracting text from {file_path}: {e}")
    #         else:
    #             print("File path not found in file info.")
    # else:
    #     print(f"Error: {response.status_code}, {response.json()}")

def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=QUEUE_NAME)

    # Set up the consumer
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    print(f"Waiting for messages in queue '{QUEUE_NAME}'...")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
