FROM rabbitmq:management

RUN apt update && apt install curl vim telnet net-tools -y

COPY ./certs/server/ /etc/rabbitmq/cert
RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/cert
COPY ./config/definitions.json /etc/rabbitmq
COPY ./config/enabled_plugins /etc/rabbitmq
COPY ./config/rabbitmq.conf /etc/rabbitmq


EXPOSE 15672 15671 5672 5671



# docker run -it -p 5671:5671 -p 5672:5672 -p 15672:15672 -p 15671:15671 --name rabbitmq_mqtt_tls_1 rabbitmq_mqtt_tls

# docker rm rabbitmq_mqtt_tls_1
# docker build . -t rabbitmq_mqtt_tls