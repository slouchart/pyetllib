import collections
import abc


class _controlled_iterator:
    """A chimera class, an iterator with the interface of a generator"""
    def __init__(self, callback):
        self._callback = callback
        self._buffer = collections.deque()
        self._should_stop = False
        self._exception = StopIteration

    def send(self, item):
        self._buffer.append(item)

    def throw(self, exc):
        self._should_stop = True
        self._exception = exc

    def __iter__(self):
        return self

    def __call__(self, *args, **kwargs):
        for item in iter(self):
            yield item

    def __next__(self):
        if not self._should_stop:
            if len(self._buffer) == 0:
                self._callback(self)  # draw a new value

            if len(self._buffer) == 0:  # nothing was sent
                self._should_stop = True

            if len(self._buffer) > 0:  # emit the first received element
                return self._buffer.popleft()

        if self._should_stop:
            raise self._exception


class _iterators_controller(object):
    def __new__(cls, iterable, *args, **kwargs):
        new_instance = super().__new__(cls)
        new_instance.__init__(iterable, *args, **kwargs)
        return tuple(new_instance._iterators)

    def __init__(self, iterable, *args, **kwargs):
        self._it = iter(iterable)
        self._iterators = self.create_controlled_iterators(*args, **kwargs)

    @abc.abstractmethod
    def create_controlled_iterators(self, *args, **kwargs):  # pragma: no cover
        pass

    @abc.abstractmethod
    def dispatch_item(self, item, requester):  # pragma: no cover
        pass

    def __call__(self, requester):
        try:
            item = next(self._it)

            self.dispatch_item(item, requester)

        except StopIteration:
            requester.throw(StopIteration)
        except Exception as e:
            self._throw_to_all(e)

    def __len__(self):  # pragma: no cover
        return len(self._iterators)

    def _throw_to_all(self, exc):
        # signal all iterators
        for it in self._iterators:
            it.throw(exc)
