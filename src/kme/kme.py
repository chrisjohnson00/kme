from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps
import jsonpickle


class KMEMessage:
    """
    This is the object we serialize and deserialize into the message body in the kafka message
    """

    def __init__(self, topic: str):
        # The message data goes here
        self.message = None
        # The topic to send goes here
        self.topic = topic
        # Configuration for a post consume message topic
        self.completion_topic = None

    def __str__(self):
        return jsonpickle.encode(self)

    def load(self, json_ojb):
        self = jsonpickle.decode(json_ojb)
        return self


class KME:
    """
    This is the client for kafka, mostly a wrapper for Kafka with KMEMessage business logic
    """

    def __init__(self, bootstrap_servers: [str]):
        self.producer = None
        self.consumer = None
        self.auto_offset_reset = 'earliest'
        self.enable_auto_commit = True
        self.acks = 1
        self.bootstrap_servers = bootstrap_servers
        self.topics = None
        self.consumer_group = None

    def send_message(self, message: KMEMessage):
        producer = self.create_producer()
        future = producer.send(topic=message.topic,
                               value=jsonpickle.encode(message))
        future.get(timeout=60)

    def create_producer(self):
        if not self.producer:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                          acks=self.acks,
                                          value_serializer=lambda x: dumps(x).encode('utf-8'))
        return self.producer

    def create_consumer(self):
        self.consumer = KafkaConsumer(
            self.topics,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=self.enable_auto_commit,
            group_id=self.consumer_group,
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        return self.consumer

    def subscribe(self, topics: [str], consumer_group: str, callback):
        self.topics = topics
        self.consumer_group = consumer_group
        consumer = self.create_consumer()
        for message in consumer:
            self.process_message(message, callback)

    def process_message(self, message, callback):
        message_body = message.value
        kme_message = KMEMessage(topic='').load(message_body)
        processed_message = callback(kme_message)
        if kme_message.completion_topic:
            self.send_message(processed_message)
