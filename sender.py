import time
import datetime
import RabbitMQAdapter as MQ


if __name__ == '__main__':
    rabbitmq = MQ.RabbitMQAdapter(ssl=True)
    rabbitmq.exchange = 'acid-data'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True

    payload = {
        "user": {
            "firstName": "Watchara",
            "lastName": "Pongsri",
            "age": "38",

        },
        'created': int(time.time()),
    }
    routing_key = 'test'
    rabbitmq.publishMessage(routing_key, payload)
