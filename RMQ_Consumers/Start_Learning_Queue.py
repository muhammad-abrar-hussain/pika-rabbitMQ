#!/usr/bin/env python

import os
import sys

# Add the 'packages' folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'packages'))

import pika
from database import db_fetch_files, db_save_topics
from openai_api import open_api_get_topics
from extracFileText import extract_text

RABBITMQ_HOST = 'localhost'
START_LEARNING_QUEUE = 'start_learning_queue'


def prepare_content(files):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, "assets", "test.pdf")

    extracted_texts = []

    for file_info in files:
        file_path = file_info.get('filepath')
        if file_path:
            try:
                text = extract_text(test_file_path)
                extracted_texts.append(text)
            except Exception as e:
                print(f"Error extracting text from {test_file_path}: {e}")
        else:
            print("File path not found in file info.")
    return "".join(extracted_texts)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=START_LEARNING_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)


    def callback(ch, method, properties, body):
        presentation_id = body.decode()
        files = db_fetch_files(presentation_id)
        if "error" in files:
            print(files["error"])
            return

        files_content = prepare_content(files)

        topics = open_api_get_topics(files_content)
        topics = {
                  "presenter_id": "2",
                  "presentation_id": presentation_id,
                  "title": "Introduction to Machine Learning",
                  "summary": "This topic covers the basics of machine learning, including supervised and unsupervised learning techniques.",
                  "request_completion_id": "cmpl-7eWMTmLqeFr95"
        }

        save_result = db_save_topics(topics, presentation_id)
        if "error" in save_result:
            print(save_result["error"])
        else:
            print(f" [x] Topics saved for presentation {presentation_id}")

    channel.basic_consume(queue=START_LEARNING_QUEUE, on_message_callback=callback)

    print(' [*] Waiting for messages...')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
