import time

class Future:
    def __init__(self):
        self._result = None
        self._fulfilled = False

    def set_result(self, result):
        self._result = result
        self._fulfilled = True

    def poll(self):
        return self._fulfilled

    def wait(self):
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
