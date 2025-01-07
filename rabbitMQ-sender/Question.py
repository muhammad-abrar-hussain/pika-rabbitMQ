#!/usr/bin/env python
import pika
Question_id = "10"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='question_Queue', durable=True)

channel.basic_publish(exchange='',
                      routing_key='question_Queue',
                      body=Question_id,
                      properties=pika.BasicProperties(
                          delivery_mode = pika.DeliveryMode.Persistent
                      ))
print(" [x] Sent 'Question'")
connection.close()