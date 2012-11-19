"""
A collection of useful datastore functions
"""


def count_query(query, limit=1000000000000):

    """
    Count the entities returned by a given query
    """

    # get entity count and return
    count = query.count(limit=limit)
    return count
