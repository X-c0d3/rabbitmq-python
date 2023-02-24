import pika
import os
import logging
import ssl
import time
import json
import datetime
from configparser import ConfigParser
configur = ConfigParser()
configur.read('config.ini')

# logging.basicConfig(level=logging.INFO)


class RabbitMQAdapter():

    hostname = configur.get('appsettings', 'RABBITMQ_HOST')
    userid = configur.get('appsettings', 'RABBITMQ_USER')
    password = configur.get('appsettings', 'RABBITMQ_PASS')
    virtual_host = configur.get('appsettings', 'RABBITMQ_VIRTUALHOST')
    tls_key_pass = configur.get('appsettings', 'TLS_KEY_PASS')

    def __init__(self, ssl=True):
        self.adapters = {}
        self.ssl_enabled = ssl
        self.port_ssl = 5671
        self.port = 5672
        self.exchange = ''
        self.exchange_type = 'topic'  # topic/fanout
        self.durable = True
        self.heartbeat = 600
        self.timeout = 300
        self.exclusive = False
        self.connection = self.setupConnection()

    def setupConnection(self):
        # currentPath = os.path.normpath(os.path.join(__file__, '../../../'))

        print('Host:' + str(self.hostname))
        print('TLS/SSL Enabled:' + str(self.ssl_enabled))
        print('Host:' + str(self.userid))
        print('Pass:' + str(self.password))
        print('tls_key_pass:' + str(self.tls_key_pass))

        currentPath = os.path.dirname(os.path.abspath(__file__))
        self.context = ssl.create_default_context(cafile=os.path.join(
            currentPath, 'certs/client/ca_certificate.pem'))

        # for Cloudamqp dont need to vertify with Passphrase
        # https://letsencrypt.org/certs/isrgrootx1.pem
        if self.tls_key_pass:
            self.context.load_cert_chain(os.path.join(currentPath, "certs/client/client_certificate.pem"),
                                         os.path.join(currentPath, "certs/client/client_key.pem"), self.tls_key_pass)

        # self.context.verify_mode = ssl.CERT_NONE
        # self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED

        # ssl_options = pika.SSLOptions(context)
        ssl_options = pika.SSLOptions(
            self.context, self.hostname) if self.ssl_enabled else None
        port = self.port_ssl if self.ssl_enabled else self.port

        print('Host:' + str(self.hostname))
        print('Port:' + str(port) + ', TLS/SSL Enabled:' + str(self.ssl_enabled))
        print('user:' + str(self.userid))
        print('password:' + str(self.password))
        print('tls_key_pass:' + str(self.tls_key_pass))

        credentials = pika.PlainCredentials(self.userid, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.hostname,
                                                                       port=port,
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

        timestamp = time.time()

        print("[x] xxxx " + json.dumps(body))

        now = datetime.datetime.now()
        expire = 1000 * int((now.replace(hour=23, minute=59, second=59,
                                         microsecond=999999) - now).total_seconds())
        headers = {  # example how headers can be used
            'actionName': 'something',
            'created': int(timestamp)
        }
        channel.basic_publish(exchange=self.exchange,
                              routing_key=routing_key,
                              body=json.dumps(body),

                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # makes persistent job
                                  priority=0,  # default priority
                                  # timestamp of job creation
                                  timestamp=int(timestamp),
                                  # job expiration (milliseconds from now), must be string, handled by rabbitmq
                                  expiration=str(expire),
                                  headers=headers
                              )
                              )

        print("[x] Sent data: " + json.dumps(body))
        self.connection.close()

    def consumeData(self, routing_key, auto_ack=False):
        # start a channel
        channel = self.connection.channel()
        channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type,  durable=self.durable)

        result = channel.queue_declare(
            queue='', exclusive=self.exclusive, durable=self.durable)

        queue_name = result.method.queue
        print('[x] exchange: ' + str(self.exchange))
        print("[x] queue_name: " + queue_name)
        print("[x] routing_key: " + routing_key)
        print("[x] auto_ack: " + str(auto_ack))
        # queue_name = 'messages'
        channel.queue_bind(exchange=self.exchange,
                           queue=queue_name, routing_key=routing_key)
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
    rabbitmq = RabbitMQAdapter(ssl=True)
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    rabbitmq.exclusive = False
    rabbitmq.publishMessage("q-reflux-room", "[+] Test send Data 123345678")
