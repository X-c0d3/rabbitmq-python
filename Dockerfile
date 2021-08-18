FROM rabbitmq:management

# RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

RUN apt update && apt install curl vim telnet net-tools -y

COPY ./certs/server/ /etc/rabbitmq/cert
RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/cert
COPY ./config/definitions.json /etc/rabbitmq
COPY ./config/enabled_plugins /etc/rabbitmq
COPY ./config/rabbitmq.conf /etc/rabbitmq




EXPOSE 443 15672 15671 5672 5671 4369 25672





# docker run -it -p 8883:8883 -p 1883:1883 -p 5671:5671 -p 15671:15671 --name rabbitmq_mqtt_tls_1 rabbitmq_mqtt_tls
# docker run -it -p 5671:5671 -p 15672:15672 --name rabbitmq_mqtt_tls_1 rabbitmq_mqtt_tls

# docker rm rabbitmq_mqtt_tls_1
# docker build . -t rabbitmq_mqtt_tls


# mosquitto_pub -t /device -m "<message_here>" \
#    -h localhost -p 8883 \
#    --cafile <path_to_genereate_certs>/ca_certificate.pem \
#    --cert <path_to_genereate_certs>/client_certificate.pem \
#    --key <path_to_genereate_certs>/client_key_unencrypted.pem \
#    -u guest -P guest -d