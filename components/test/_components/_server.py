import multiprocessing
import sys
import traceback

multiprocessing.set_start_method("fork")


class _Process(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


class Server:
    def __init__(self, run, **kwargs) -> None:
        self.run = run
        self.kwargs = kwargs

    def __enter__(self):
        self.process = multiprocessing.Process(target=self.run, kwargs=self.kwargs)
        self.process.start()
        # if self.process.exception:
        #     print(self.process.exception)
        #     self.__exit__()

    def __exit__(self, *args):
        self.process.terminate()
        self.process.join(2)
        if self.process.is_alive:
            self.process.kill()
            self.process.join()
        self.process.close()
