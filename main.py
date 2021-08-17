
import pika
import sys
import ssl
import logging
from configparser import ConfigParser
logging.basicConfig(level=logging.INFO)
configur = ConfigParser()
configur.read('config.ini')


hostname = configur.get('appsettings', 'RABBITMQ_HOST')
userid = configur.get('appsettings', 'RABBITMQ_USER')
password = configur.get('appsettings', 'RABBITMQ_PASS')
port = configur.getint('appsettings', 'RABBITMQ_PORT')
virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')


context = ssl.create_default_context(
    cafile="/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/ca_key.pem")
context.load_cert_chain("/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_certificate.pem",
                        "/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_key.pem")
ssl_options = pika.SSLOptions(context, hostname)

credentials = pika.PlainCredentials(userid, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,
                                                               port=port,
                                                               virtual_host=virtual_host,
                                                               credentials=credentials,
                                                               ssl_options=ssl_options,
                                                               frame_max=10000))


channel = connection.channel()  # start a channel
channel.exchange_declare(
    exchange='x-reflux', exchange_type='topic',  durable=True)  # topic , fanout

result = channel.queue_declare(
    queue='q-reflux-room', exclusive=False, durable=True)


queue_name = result.method.queue

channel.queue_bind(exchange='x-reflux', queue=queue_name)
print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


# set up subscription on the queue
channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

# start consuming (blocks)
channel.start_consuming()
connection.close()
