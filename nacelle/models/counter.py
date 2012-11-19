"""
Datastore models for sharded counter
"""
# third-party imports
from google.appengine.ext import db


class GeneralCounterShardConfig(db.Model):

    """
    Tracks the number of shards for each named counter.
    """

    # counter name
    name = db.StringProperty(required=True)
    # number fo shards configured for this counter
    num_shards = db.IntegerProperty(required=True, default=250)


class GeneralCounterShard(db.Model):

    """
    Shards for each named counter
    """

    # name of counter
    name = db.StringProperty(required=True)
    # current count on this shard
    count = db.IntegerProperty(required=True, default=0)
