import os
import sys

# Add the 'packages' folder to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'packages'))

import pika
from database import db_fetch_question, db_save_question_detail


RABBITMQ_HOST = 'localhost'
QUESTION_QUEUE = 'question_Queue'


def main():
    """
        Main function to process messages from RabbitMQ queue.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUESTION_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        question_id = body.decode()

        try:
            question = db_fetch_question(question_id)
            # question_detail = open_api_get_relevancy(files_content)
            question_detail = {
                        "topic_id": "4",
                        "is_relevant": False
                        }
            save_result = db_save_question_detail(question_detail["topic_id"],question_detail["is_relevant"], question_id)
            print(save_result)
        except Exception as e:
            print(f"Error processing question {question_id}: {e}")
        finally:
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUESTION_QUEUE, on_message_callback=callback)

    print(f"Waiting for messages in queue '{QUESTION_QUEUE}'...")
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')