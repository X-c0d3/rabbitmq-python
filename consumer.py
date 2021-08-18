from RabbitMQAdapter import RabbitMQAdapter
if __name__ == '__main__':
    rabbitmq = RabbitMQAdapter(ssl=True)
    rabbitmq.exchange = 'acid-data'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True
    routing_key = 'test'
    rabbitmq.consumeData(routing_key)
