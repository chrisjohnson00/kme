from kme import KME, KMEMessage
from unittest import mock
from kafka import KafkaConsumer, KafkaProducer


def test_send_message():
    future_attrs = {'get.return_value': 'yaas'}
    mock_future = mock.Mock(**future_attrs)
    kafka_mock_attrs = {'send.return_value': mock_future}
    mock_kafka_producer = mock.Mock(KafkaProducer)
    mock_kafka_producer.configure_mock(**kafka_mock_attrs)
    kme = KME(bootstrap_servers=['foobar'])
    kme.producer = mock_kafka_producer
    kme.send_message(KMEMessage(topic='foobar'))
    mock_kafka_producer.send.assert_called_once()
    mock_future.get.assert_called_once()


def test_create_producer():
    kme = KME(bootstrap_servers=['foobar'])
    kme.producer = mock.Mock(KafkaProducer)
    ret = kme.create_producer()
    assert ret == kme.producer


@mock.patch('kme.kme.KafkaConsumer', autospec=True)
def test_create_consumer(kafka_consumer_mock):
    kme = KME(bootstrap_servers=['foobar'])
    consumer = kme.create_consumer()
    assert isinstance(consumer, KafkaConsumer)


def test_subscribe():
    with mock.patch.object(KME, 'process_message') as pm:
        with mock.patch.object(KME, 'create_consumer', return_value=['foobar']):
            kme = KME(bootstrap_servers=['foobar'])
            kme.subscribe(topics=['a'], consumer_group='a', callback='foobar')
            pm.assert_called_once()


def test_process_message_no_completion_topic():
    mock_kme_message = mock.Mock(spec=KMEMessage, completion_topic=None)
    with mock.patch.object(KMEMessage, 'load', return_value=mock_kme_message) as message_load:
        with mock.patch.object(KME, 'send_message') as sm:
            mock_message = mock.Mock(value='Messabe body')
            kme = KME(bootstrap_servers=['foobar'])
            kme.process_message(mock_message, mock_callback)
            sm.assert_not_called()
            message_load.assert_called_once()


def test_process_message_with_completion_topic():
    mock_kme_message = mock.Mock(spec=KMEMessage, completion_topic='foobar')
    with mock.patch.object(KMEMessage, 'load', return_value=mock_kme_message) as message_load:
        with mock.patch.object(KME, 'send_message') as sm:
            mock_message = mock.Mock(value='Messabe body')
            kme = KME(bootstrap_servers=['foobar'])
            kme.process_message(mock_message, mock_callback)
            sm.assert_called_once()
            kall = sm.call_args
            message = kall.args[0]  # type: KMEMessage
            assert message.topic == "foobar"
            message_load.assert_called_once()


def mock_callback(message: KMEMessage):
    return KMEMessage(topic='')
