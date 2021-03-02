from opentera.redis.RedisProtocolFactory import RedisProtocolFactory, redisProtocol

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl, defer

# Event based, twisted redis
import txredisapi as txredis

# Blocking redis
import redis


class RedisClient:

    def __init__(self, config=None):
        print('Init RedisClient', self, config)
        self.protocol = None
        self.callbacks_dict = dict()

        # Fill config
        if config is None:
            print('RedisClient - Warning, using default redis configuration')
            config = {'hostname': 'localhost', 'port': 6379, 'db': 0, 'username': '', 'password': ''}

        self.redisConfig = config

        # Redis client (synchronous)
        self.redis = redis.Redis(host=config['hostname'],
                                 port=config['port'],
                                 db=config['db'],
                                 username=config['username'],
                                 password=config['password'],
                                 client_name=self.__class__.__name__)

        # Redis client (async)
        self.conn = reactor.connectTCP(config['hostname'], config['port'],
                                       RedisProtocolFactory(parent=self, protocol=redisProtocol, config=config))
        # print(self.conn)

    def __del__(self):
        print("****- Deleting RedisClient")

    def getConfig(self):
        return self.redisConfig

    def redisConnectionMade(self):
        print('********************* RedisClient connectionMade')
        pass

    def redisMessageReceived(self, pattern, channel, message):
        # print(self, 'redisMessageReceived', pattern, channel, message)
        if pattern in self.callbacks_dict:
            # Call function.
            self.callbacks_dict[pattern](pattern, channel, message)

    def redisConnectionLost(self, reason):
        print("RedisClient lost connection", reason)
        pass

    def setProtocol(self, protocol: redisProtocol):
        print('RedisClient set protocol', protocol)
        self.protocol = protocol

    def subscribe(self, topic):
        if self.protocol:
            # print('RedisClient (', self, ') subscribing to: ',  topic)
            return self.protocol.psubscribe(topic)
        else:
            print('Error, no protocol')
            return defer.Deferred()

    def unsubscribe(self, topic):
        if self.protocol:
            return self.protocol.punsubscribe(topic)
        else:
            print('Error, no protocol')
            return defer.Deferred()

    def publish(self, topic, message):
        return self.redis.publish(topic, message)

    def redisGet(self, key):
        return self.redis.get(key)

    def redisSet(self, key, value, ex=None):
        return self.redis.set(key, value, ex=ex)

    def redisDelete(self, key):
        return self.redis.delete(key)

    def subscribe_pattern_with_callback(self, pattern, function):
        # print(self, 'subscribe_pattern_with_callback', pattern, function)
        self.callbacks_dict[pattern] = function
        return self.subscribe(pattern)

    def unsubscribe_pattern_with_callback(self, pattern, function):
        # print(self, 'unsubscribe_pattern_with_callback', pattern, function)
        ret = self.unsubscribe(pattern)
        del self.callbacks_dict[pattern]
        return ret

    @defer.inlineCallbacks
    def redisClose(self):
        if self.protocol:
            # Will not reconnect
            var = yield self.protocol.quit()
            self.protocol.parent = None
            print(var)

        if self.conn:
            # Disconnect socket
            self.conn.disconnect()

        if self.redis:
            # Close sync client (will terminate conn.)
            self.redis.close()
            # self.redis.connection_pool.disconnect()


# Debug
if __name__ == '__main__':
    print('Starting')

    from twisted.internet.task import deferLater
    from twisted.internet.defer import inlineCallbacks


    def sleep(secs):
        return deferLater(reactor, secs, lambda: None)


    @inlineCallbacks
    def function_with_client_should_remove_conn():
        class MyClient(RedisClient):
            def redisConnectionMade(self):
                print('redisConnectionMade')
                self.subscribe('*')

        client = MyClient()
        print('setting variable')
        client.redisSet('papa', 'rien', ex=60)
        print('redis get', client.redisGet('papa'))
        print('sleeping 10 secs.')
        yield sleep(2)
        print('done!')
        client.redisClose()

    def called(result):
        print('Function called')

    from twisted.internet import task
    d = task.deferLater(reactor, 1, function_with_client_should_remove_conn)
    d.addCallback(called)

    # RPCClient
    from opentera.redis.RedisRPCClient import RedisRPCClient
    from opentera.config.ConfigManager import ConfigManager
    config = ConfigManager()
    config.create_defaults()

    rpc = RedisRPCClient(config.redis_config)
    rpc.call('module', 'func', 1, 2, 3)

    print('Starting reactor')
    reactor.run()



