import multiprocessing
from time import sleep

# Take an item off of the todo queue, run it, and put it on the done queue.
def run_item(todo, done):
    while not todo.empty():
        name, func, args = todo.get()
        results = func(*args)
        done.put((name, results))

class loom:

    # Default the pool size to the number of CPU's
    _poolsize = multiprocessing.cpu_count()
    _pool = None
    _todo_queue = multiprocessing.Queue()
    _done_queue = multiprocessing.Queue()
    _process_list = []
    _item_count = 0

    # Define the thread count if wanted, then create the pool.
    def __init__(self, poolsize=None):
        if poolsize != None:
            self._poolsize = poolsize

        self._pool = multiprocessing.Pool(self._poolsize)

    def run(self, f, d):
        self._item_count = len(d)
        for name, args in d.items():
            # create a tuple with the name, the function, and the arguments,
            # and put it on the queue
            self._todo_queue.put((name, f, tuple(args)))
        
        # spawn the worker processes then
        # add them to a list so we can join them later
        for i in range(self._poolsize):
            proc = self._pool.Process(
                target=run_item,
                args=(
                    self._todo_queue,
                    self._done_queue
                )
            )
            proc.start()
            self._process_list.append(proc)

    def get(self):
        # Busyish wait until all the processing is done
        # TODO replace this with multiprocessing Event
        while not self.is_done():
             sleep(50.0/1000.0) # 50 ms

        dq = self._done_queue
        d = {}
        for count in range(dq.qsize()):
            name, results = dq.get()
            d[name] = results

        return d
    
    # Does what it says on the tin
    def is_done(self):
        return self._done_queue.qsize() == self._item_count

    # A flote between 0 and 1
    def progress(self):
        return self._done_queue.qsize() / self._item_count

