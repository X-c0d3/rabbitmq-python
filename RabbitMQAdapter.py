import pika
import os
import ssl
from configparser import ConfigParser


class RabbitMQAdapter():

    configur = ConfigParser()
    configur.read('config.ini')

    hostname = configur.get('appsettings', 'RABBITMQ_HOST')
    userid = configur.get('appsettings', 'RABBITMQ_USER')
    password = configur.get('appsettings', 'RABBITMQ_PASS')
    port = configur.getint('appsettings', 'RABBITMQ_PORT')
    virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')
    tls_key_pass = configur.get('appsettings', 'TLS_KEY_PASS')

    def __init__(self):
        super(self).__init__()

        currentPath = os.path.dirname(os.path.abspath(__file__))
        self.adapters = {}
        self.context = ssl.create_default_context(cafile=os.path.join(
            currentPath, 'certs/server/ca_certificate.pem'))
        self.context.load_cert_chain(os.path.join(currentPath, "certs/client/client_certificate.pem"),
                                     os.path.join(currentPath, "certs/client/client_key.pem"), self.tls_key_pass)

    def sendData(self, adapter):

        # context.verify_mode = ssl.CERT_NONE
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        # ssl_options = pika.SSLOptions(context)
        ssl_options = pika.SSLOptions(self.context, self.hostname)

        credentials = pika.PlainCredentials(self.userid, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.hostname,
                                                                       port=self.port,
                                                                       virtual_host=self.virtual_host,
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
                              body="[+] Test send Data 123345678 ")
        print("[x] Sent data")

        connection.close()
