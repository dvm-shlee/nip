from sys import stdout
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import partial

class Scheduler(threading.Thread):
    def _run_coro(self, func):
        result = asyncio.run_coroutine_threadsafe(func, self.loop)
        return result
    
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.queue = asyncio.Queue()
        self._set_name()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _set_name(self):
        self.name = 'NIPScheduler'

    async def _event_loop(self):
        while True:
            task = await self.queue.get()
            if isinstance(task, tuple):
                if asyncio.iscoroutinefunction(task[0]):
                    func, args, kwargs = task
                    result = self._run_coro(func(*args, **kwargs))
                elif callable(task[0]):
                    func, args, kwargs = task
                    coro = await self.loop.run_in_executor(self.executor, partial(func, *args, **kwargs))
            else:
                if task == 0:
                    print("loop stopped")
                    break
                else:
                    print(task)
            
    def run(self):
        """serve as a target for Thread
        so when start()method called, this will run
        """
        self.loop.run_until_complete(self._event_loop())

    def queue_item(self, item):
        self._run_coro(self.queue.put(item))
        
    def _stop_event_loop(self):
        if self.loop.is_running():
            self._run_coro(self.queue.put(0))
            
    def _stop_thread(self):
        if self.is_alive():
            self.join()
        
    def stop(self):
        self._stop_event_loop()
        self._stop_thread()
        
    def __del__(self):
        self.stop()
        print('deleted!')


if __name__ == "__main__":
    schd = Scheduler()
    schd.start()