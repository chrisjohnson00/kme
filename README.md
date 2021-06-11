# kme
A Python library that enables building simple Kafka consumer/producer micro/nano services

This is a library that wraps the `kafka-python` library with some message routing helpers.

With this library, you can create micro/nano services (think like a Function, FaaS) that listens to one or more Kafka topics
and processes the message, then based on configuration can send a new message.

I developed this with the intent to create a distributed workflow for various automation activities in my Kubernetes cluster
and outside as well.

The workflow that I initially designed this for was:

1) On a schedule, submit a message to the "wakup-computer" topic.  This message contains details on which computer to 
   wake up and how we determine when the computer is ready for work, and "completion topic", where we send a message 
   when the computer is alive!  In my case, I have an old server with a ton of hard drives, which I use for cold 
   backups.  I only need it on while backups are running.
2) The completion topic, lets call it "run-backups" would accept the message and perform the backup processes.  Once it
   has completed, it will send a new message to the "shutdown-computer" topic.
3) The "shutdown-computer" topic has a consumer group for each computer which is included in this flow, and it receives
   the message and sees that it needs to shut down and does so.
   
I also invision using this workflow for my on-premise Kubernetes cluster so that I can "auto scale" nodes up/down when 
needed, reusing the "wakup-computer" and "shutdown-computer" topics and nano-services.

# Usage

```python
from kme import KMEMessage, KME
import os

# produce a message with a completion topic
def kme_producer():
    message = KMEMessage(topic=os.environ.get('KAFKA_TOPIC'))
    message.message = {'foo': 'bar', 'bar': 'foo'}
    message.completion_topic = 'foobar'
    k_client = KME(bootstrap_servers=[os.environ.get('KAFKA_BOOSTRAP_SERVER')])
    k_client.send_message(message=message)

# setup a consumer
def kme_consumer():
    k_client = KME(bootstrap_servers=[os.environ.get('KAFKA_BOOSTRAP_SERVER')])
    print(f"Subscribing to {os.environ.get('KAFKA_TOPIC')}", flush=True)
    # IMPORTANT - note the callback value!!
    k_client.subscribe(os.environ.get('KAFKA_TOPIC'), consumer_group='me', callback=process_message)  


# this is the method which is called for each message, so put your logic here!
def process_message(message: KMEMessage):
    print(f"Processing message {message}", flush=True)
    print(f"Message: {message.message}", flush=True)
    print(f"Topic: {message.topic}", flush=True)
    print(f"Completion Topic: {message.completion_topic}", flush=True)
    # if you want to pass a "completion message" you populate it and return it
    # if you don't want to pass a "completion message" just return `KMEMessage(topic='')`
    return_message = KMEMessage(topic=message.completion_topic)
    return_message.message = "foo the bar"
    return return_message

if __name__ == '__main__':
    print("Starting", flush=True)
    kme_producer() # produce a message
    kme_consumer() # now consume said message
    print("Finished", flush=True)
```
