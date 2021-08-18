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
client_key_pass = configur.get('appsettings', 'CLIENT_KEY_PASS')


CurrentPath = os.path.dirname(os.path.abspath(__file__))

context = ssl.create_default_context(cafile=os.path.join(
    CurrentPath, 'certs/server/ca_certificate.pem'))
context.load_cert_chain(os.path.join(CurrentPath, "certs/client/client_certificate.pem"),
                        os.path.join(CurrentPath, "certs/client/client_key.pem"), client_key_pass)


#context.verify_mode = ssl.CERT_NONE
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# ssl_options = pika.SSLOptions(context)
ssl_options = pika.SSLOptions(context, hostname)

credentials = pika.PlainCredentials(userid, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,
                                                               port=port,
                                                               virtual_host=virtual_host,
                                                               credentials=credentials,
                                                               ssl_options=ssl_options,
                                                               heartbeat=600,
                                                               blocked_connection_timeout=300,
                                                               ))
channel = connection.channel()  # start a channel

channel.exchange_declare(
    exchange='x-reflux', exchange_type='topic',  durable=True)  # topic/fanout


channel.basic_publish(exchange="x-reflux",
                      routing_key="q-reflux-room",
                      body="[+] " + datetime.now().strftime("%H:%M:%S") + " Test send Data 123345678 ")
print("[x] Sent data")

connection.close()
