import RabbitMQAdapter as MQ


if __name__ == '__main__':
    rabbitmq = MQ.RabbitMQAdapter()
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    rabbitmq.publishMessage("q-reflux-room", "[+] Test send Data 55555 ")
