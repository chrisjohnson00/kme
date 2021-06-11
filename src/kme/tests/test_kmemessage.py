from kme import KMEMessage


def test_str():
    kme = KMEMessage(topic='foobar')
    str_obj = kme.__str__()
    assert isinstance(str_obj, str)


def test_load():
    json_str = '''
    {
        "py/object":"kme.kme.KMEMessage",
        "message":"foo the bar",
        "topic":"foobar",
        "completion_topic":"something"
    }
    '''
    kme = KMEMessage(topic='barfoo')
    kme = kme.load(json_str)
    assert kme.message == "foo the bar"
    assert kme.topic == 'foobar'
    assert kme.completion_topic == 'something'
