"""
A simple sharded counter implementation for use when a
very high performance counter is needed
"""
# stdlib imports
import random

# third-party imports
from google.appengine.api import memcache
from google.appengine.ext import db

# local imports
from models import GeneralCounterShard
from models import GeneralCounterShardConfig


def get_count(name):

    """
    Retrieve the value for a given sharded counter.

    Parameters:
      name - The name of the counter
    """

    total = memcache.get(name)
    if total is None:
        total = 0
        for counter in GeneralCounterShard.all().filter('name = ', name):
            total += counter.count
        memcache.add(name, total, 60)
    return total


def decrement(name):

    """
    Increment the value for a given sharded counter.

    Parameters:
      name - The name of the counter
    """

    config = GeneralCounterShardConfig.get_or_insert(name, name=name)

    def txn():
        index = random.randint(0, config.num_shards - 1)
        shard_name = name + str(index)
        counter = GeneralCounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = GeneralCounterShard(key_name=shard_name, name=name)
        counter.count -= 1
        counter.put()
    db.run_in_transaction(txn)

    # does nothing if the key does not exist
    memcache.decr(name)


def increment(name):

    """
    Increment the value for a given sharded counter.

    Parameters:
      name - The name of the counter
    """

    config = GeneralCounterShardConfig.get_or_insert(name, name=name)

    def txn():
        index = random.randint(0, config.num_shards - 1)
        shard_name = name + str(index)
        counter = GeneralCounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = GeneralCounterShard(key_name=shard_name, name=name)
        counter.count += 1
        counter.put()
    db.run_in_transaction(txn)

    # does nothing if the key does not exist
    memcache.incr(name)


def increase_shards(name, num):

    """
    Increase the number of shards for a given sharded counter.
    Will never decrease the number of shards.

    Parameters:
      name - The name of the counter
      num - How many shards to use

    """

    config = GeneralCounterShardConfig.get_or_insert(name, name=name)

    def txn():
        if config.num_shards < num:
            config.num_shards = num
            config.put()
    db.run_in_transaction(txn)
