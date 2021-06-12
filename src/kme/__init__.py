from kme.kme import KME, KMEMessage
import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger(__name__).addHandler(NullHandler())

__all__ = [
    'KME',
    'KMEMessage'
]
