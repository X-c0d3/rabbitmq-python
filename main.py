
import pika
import ssl
import logging
import os
from configparser import ConfigParser
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
configur = ConfigParser()
configur.read('config.ini')


hostname = configur.get('appsettings', 'RABBITMQ_HOST')
userid = configur.get('appsettings', 'RABBITMQ_USER')
password = configur.get('appsettings', 'RABBITMQ_PASS')
port = configur.getint('appsettings', 'RABBITMQ_PORT')
virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')
tls_key_pass = configur.get('appsettings', 'TLS_KEY_PASS')


logging.basicConfig(level=logging.DEBUG)


CurrentPath = os.path.dirname(os.path.abspath(__file__))

context = ssl.create_default_context(cafile=os.path.join(
    CurrentPath, 'certs/server/ca_certificate.pem'))
context.load_cert_chain(os.path.join(CurrentPath, "certs/client/client_certificate.pem"),
                        os.path.join(CurrentPath, "certs/client/client_key.pem"), tls_key_pass)


context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.check_hostname = False

ssl_options = pika.SSLOptions(context, hostname)


credentials = pika.PlainCredentials(userid, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,
                                                               port=port,
                                                               virtual_host=virtual_host,
                                                               credentials=credentials,
                                                               ssl_options=ssl_options,
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
