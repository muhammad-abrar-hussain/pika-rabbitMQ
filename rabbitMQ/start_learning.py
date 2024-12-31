#!/usr/bin/env python
import pika
presentation_id = "47ebc916-c793-11ef-bb91-b499e2a07b89"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='start_learning_queue', durable=True)

channel.basic_publish(exchange='',
                      routing_key='start_learning_queue',
                      body=presentation_id,
                      properties=pika.BasicProperties(
                          delivery_mode = pika.DeliveryMode.Persistent
                      ))
print(" [x] Sent 'Presentation ID'")
connection.close()