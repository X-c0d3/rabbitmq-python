import pika
import os
import ssl
from datetime import datetime
from configparser import ConfigParser
configur = ConfigParser()
configur.read('config.ini')


hostname = configur.get('appsettings', 'RABBITMQ_HOST')
userid = configur.get('appsettings', 'RABBITMQ_USER')
password = configur.get('appsettings', 'RABBITMQ_PASS')
port = configur.getint('appsettings', 'RABBITMQ_PORT')
virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(
    '/Users/x-c0d3/Desktop/DEV/rabbitmq-python/certs/client_certificate.pem')


credentials = pika.PlainCredentials(userid, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,
                                                               port=port,
                                                               virtual_host=virtual_host,
                                                               credentials=credentials,
                                                               # ssl_options=pika.SSLOptions(context),
                                                               frame_max=10000))
channel = connection.channel()  # start a channel

channel.exchange_declare(
    exchange='x-reflux', exchange_type='topic',  durable=True)  # topic , fanout


channel.basic_publish(exchange="x-reflux",
                      routing_key="q-reflux-room",
                      body="[+] " + datetime.now().strftime("%H:%M:%S") + " Test send Data 123345678 ")
print("[x] Sent data")

connection.close()
