#!/usr/bin/env python
import pika
import pika

# Estabelece a conexão com o servidor RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declara a fila
queue_name = 'minha_fila'
queue_declare_ok = channel.queue_declare(queue_name, durable=True)

channel.basic_publish(exchange='', routing_key='minha_fila', body='Hello World!')
channel.basic_publish(exchange='', routing_key='minha_fila', body='Hello World! 2')

# Obtém a quantidade de mensagens na fila
message_count = queue_declare_ok.method.message_count
print(f"A fila '{queue_name}' tem {message_count} mensagens.")


connection.close()