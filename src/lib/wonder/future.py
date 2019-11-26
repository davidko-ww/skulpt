import time

class Future:
    """A WW implementation of a "Future" object (also known as a "Promise")
    """
    def __init__(self):
        self._result = None
        self._fulfilled = False

    def set_result(self, result):
        """Set the result of a waiting future. This also sets the status of the
        future to "fulfilled" and allows other coroutines waiting on this
        future to proceed."""
        self._result = result
        self._fulfilled = True

    def poll(self):
        """Check to see if the future is fulfilled"""
        return self._fulfilled

    def wait(self):
        """Wait for the future to be fulfilled.

        Returns: The result as set by Future.set_result()
        """
        while self._fulfilled is False:
            time.sleep(0.1)
        return self._result

class TimedFuture(Future):
    # Yields the result after a certain amount of time
    def __init__(self, timeout, result=None):
        super(TimedFuture, self).__init__()
        self._timeout = time.time() + timeout
        self._timeout_result = result

    def poll(self):
        if time.time() > self._timeout:
            return True
        else:
            return False

    def wait(self):
        t = self._timeout - time.time()
        if t > 0:
            time.sleep( t )
        return self._timeout_result
