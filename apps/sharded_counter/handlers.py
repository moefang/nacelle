from nacelle.handlers.base import JSONHandler
import counter


class CounterHandler(JSONHandler):

    """
    This handler demonstrates the use of nacelle's simple sharded counters
    """

    def get_context(self, counter_name):

        """
        Increment and return the specified counter's value
        """

        # increment the specified counter
        counter.increment(counter_name)
        # get the counter value
        hit_count = counter.get_count(counter_name)
        # return the counter value as JSON object
        return {'count': hit_count}
