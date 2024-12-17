#!/usr/bin/env python
import pika
presentation_id = "a821102eb2eb4280a99dac2f0b8a4d7b"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='start_learning_Queue')

channel.basic_publish(exchange='', routing_key='start_learning_Queue', body=presentation_id)
print(" [x] Sent 'Presentation ID'")
connection.close()