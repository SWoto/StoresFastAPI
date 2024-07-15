import functools
import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType

import json
import logging

from threading import Lock, Thread
from src.core.configs import settings


logger = logging.getLogger(__name__)


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AsyncioRabbitMQ(metaclass=SingletonMeta):
    EXCHANGE = 'message'
    EXCHANGE_TYPE = ExchangeType.topic
    PUBLISH_INTERVAL = 1
    QUEUE = 'text'
    ROUTING_KEY = 'example.text'

    _url = None

    def __init__(self, amqp_url):
        self._connection = None
        self._channel = None

        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        self._stopping = False
        self._url = amqp_url

    def connect(self):
        logger.info('Connecting to %s', self._url)
        return AsyncioConnection(
            pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def on_connection_open(self, connection):
        logger.info('Connection opened')
        self._connection = connection
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_open_error(self, _unused_connection, err):
        logger.error(f'Connection open failed: {err}')

    def on_connection_closed(self, _unused_connection, reason):
        logger.warning(f'Connection closed: {reason}')
        self._channel = None

    def on_channel_open(self, channel):
        logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        logger.warning(f'Channel {channel} was closed: {reason}')
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        logger.info(f'Declaring exchange {exchange_name}')
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name, exchange_type=self.EXCHANGE_TYPE, callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        logger.info(f'Exchange declared: {userdata}')
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        logger.info(f'Declaring queue {queue_name}')
        self._channel.queue_declare(
            queue=queue_name, callback=self.on_queue_declareok)

    def on_queue_declareok(self, _unused_frame):
        logger.info(
            f'Binding {self.EXCHANGE} to {self.QUEUE} with {self.ROUTING_KEY}')
        self._channel.queue_bind(
            self.QUEUE, self.EXCHANGE, routing_key=self.ROUTING_KEY, callback=self.on_bindok)

    def on_bindok(self, _unused_frame):
        logger.info('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        logger.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        logger.info(
            f'Received {confirmation_type} for delivery tag: {method_frame.method.delivery_tag}')
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        logger.info(
            f'Published {self._message_number} messages, {len(self._deliveries)} have yet to be confirmed, '
            f'{self._acked} were acked and {self._nacked} were nacked')

    def publish_message(self, message):
        if self._channel is None or not self._channel.is_open:
            return

        hdrs = {"type": "confirmation-email"}
        properties = pika.BasicProperties(
            app_id='stores-api',
            content_type='application/json',
            headers=hdrs)

        self._channel.basic_publish(self.EXCHANGE, self.ROUTING_KEY,
                                    json.dumps(message, ensure_ascii=False),
                                    properties)
        self._message_number += 1
        self._deliveries.append(self._message_number)
        logger.info(f'Published message # {self._message_number}')


aiorabbit = AsyncioRabbitMQ(settings.RABBITMQ_URL)
