import pika
import os
import logging
import ssl
from configparser import ConfigParser
configur = ConfigParser()
configur.read('config.ini')

# logging.basicConfig(level=logging.INFO)


class RabbitMQAdapter():

    hostname = configur.get('appsettings', 'RABBITMQ_HOST')
    userid = configur.get('appsettings', 'RABBITMQ_USER')
    password = configur.get('appsettings', 'RABBITMQ_PASS')
    port = configur.getint('appsettings', 'RABBITMQ_PORT')
    virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')
    tls_key_pass = configur.get('appsettings', 'TLS_KEY_PASS')

    def __init__(self):
        self.adapters = {}
        self.exchange = ''
        self.exchange_type = 'topic'  # topic/fanout
        self.durable = True
        self.heartbeat = 600
        self.timeout = 300
        self.exclusive = False
        self.connection = self.setupConnection()

    def setupConnection(self):
        # currentPath = os.path.normpath(os.path.join(__file__, '../../../'))
        currentPath = os.path.dirname(os.path.abspath(__file__))
        self.context = ssl.create_default_context(cafile=os.path.join(
            currentPath, 'certs/server/ca_certificate.pem'))
        self.context.load_cert_chain(os.path.join(currentPath, "certs/client/client_certificate.pem"),
                                     os.path.join(currentPath, "certs/client/client_key.pem"), self.tls_key_pass)

        # self.context.verify_mode = ssl.CERT_NONE
        # self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED

        # ssl_options = pika.SSLOptions(context)
        ssl_options = pika.SSLOptions(self.context, self.hostname)
        credentials = pika.PlainCredentials(self.userid, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.hostname,
                                                                       port=self.port,
                                                                       virtual_host=self.virtual_host,
                                                                       credentials=credentials,
                                                                       ssl_options=ssl_options,
                                                                       heartbeat=self.heartbeat,
                                                                       blocked_connection_timeout=self.timeout,
                                                                       ))
        return connection

    def publishMessage(self, routing_key, body):
        # start a channel
        channel = self.connection.channel()
        channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type,  durable=self.durable)

        channel.basic_publish(exchange=self.exchange,
                              routing_key=routing_key,
                              body=body)

        print("[x] Sent data")
        self.connection.close()

    def consumeData(self, routing_key, auto_ack=True):
        # start a channel
        channel = self.connection.channel()
        channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type,  durable=self.durable)

        result = channel.queue_declare(
            queue=routing_key, exclusive=self.exclusive, durable=self.durable)

        queue_name = result.method.queue
        channel.queue_bind(exchange=self.exchange, queue=queue_name)
        print(' [*] Waiting for logs. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            # Do something in here
            print(" [x] Received %r" % body)

        # set up subscription on the queue
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)

        # start consuming (blocks)
        channel.start_consuming()
        self.connection.close()


if __name__ == "__main__":
    rabbitmq = RabbitMQAdapter()
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    rabbitmq.exclusive = False
    rabbitmq.publishMessage("q-reflux-room", "[+] Test send Data 123345678")
