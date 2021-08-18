import time
import datetime
import RabbitMQAdapter as MQ


if __name__ == '__main__':
    rabbitmq = MQ.RabbitMQAdapter(ssl=False)
    rabbitmq.exchange = 'x-reflux'
    rabbitmq.exchange_type = 'topic'  # topic/fanout
    rabbitmq.durable = True

    timestamp = time.time()
    payload = {
        "user": {
            "firstName": "Watchara",
            "lastName": "Pongsri",
            "age": "38",

        },
        'created': int(timestamp),
    }
    rabbitmq.publishMessage("q-reflux-room", payload)
