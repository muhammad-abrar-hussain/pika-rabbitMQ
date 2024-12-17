#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='start_learning_Queue')

channel.basic_publish(exchange='', routing_key='start_learning_Queue', body='09090meme')
print(" [x] Sent 'Presentation ID'")
connection.close()