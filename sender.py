from RabbitMQAdapter import RabbitMQAdapter


if __name__ == '__main__':
    rabbitmq = RabbitMQAdapter()
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    rabbitmq.publishMessage("q-reflux-room", "[+] Test send Data 55555 ")
