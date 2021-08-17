
import pika
import sys
import ssl
import logging
import certifi
from configparser import ConfigParser
logging.basicConfig(level=logging.DEBUG)
configur = ConfigParser()
configur.read('config.ini')


hostname = configur.get('appsettings', 'RABBITMQ_HOST')
userid = configur.get('appsettings', 'RABBITMQ_USER')
password = configur.get('appsettings', 'RABBITMQ_PASS')
port = configur.getint('appsettings', 'RABBITMQ_PORT')
virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')
client_key_pass = configur.get('appsettings', 'CLIENT_KEY_PASS')
logging.basicConfig(level=logging.DEBUG)
# context = ssl.create_default_context(
#     cafile="/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/ca_key.pem")

# context.load_cert_chain("/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_certificate.pem",
#                         "/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_key.pem")
# ssl_options = pika.SSLOptions(context, hostname)


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED

context = ssl.create_default_context(cafile=certifi.where())
context.load_cert_chain("certs/client_certificate.pem",
                        "certs/client_key.pem", client_key_pass)

# context.load_verify_locations(
#     "/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_certificate.pem",
#     '/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_key.pem')
# context.load_cert_chain(
#     "/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_certificate.pem")

credentials = pika.PlainCredentials(userid, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,
                                                               port=port,
                                                               virtual_host=virtual_host,
                                                               credentials=credentials,
                                                               ssl_options=pika.SSLOptions(
                                                                   context, hostname),
                                                               ))


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
