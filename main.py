from RabbitMQAdapter import RabbitMQAdapter
if __name__ == '__main__':
    rabbitmq = RabbitMQAdapter()
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    rabbitmq.consumeData("q-reflux-room")
