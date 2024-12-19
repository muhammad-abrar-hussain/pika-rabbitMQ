#!/usr/bin/env python
import pika
presentation_id = "7c3ec1c0-6c25-4194-a829-48cc4640e38f"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='start_learning_Queue', durable=True)

channel.basic_publish(exchange='',
                      routing_key='start_learning_Queue',
                      body=presentation_id,
                      properties=pika.BasicProperties(
                          delivery_mode = pika.DeliveryMode.Persistent
                      ))
print(" [x] Sent 'Presentation ID'")
connection.close()