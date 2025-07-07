from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition

class ManagedThread(QThread):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
        self._mutex = QMutex()
        self._should_stop = False
        self._condition = QWaitCondition()

    def run(self):
        self._mutex.lock()
        try:
            if self.target and not self._should_stop:
                self.target()
        finally:
            self._mutex.unlock()

    def safe_stop(self):
        self._mutex.lock()
        self._should_stop = True
        self._condition.wakeAll()
        self._mutex.unlock()
        self.wait(1000)  # Wait up to 1 second

class ThreadManager:
    def __init__(self):
        self._threads = []
        self._mutex = QMutex()

    def start_thread(self, target):
        thread = ManagedThread(target)
        self._mutex.lock()
        self._threads.append(thread)
        self._mutex.unlock()
        thread.start()
        return thread

    def stop_all(self):
        self._mutex.lock()
        threads = self._threads.copy()
        self._mutex.unlock()
        
        for thread in threads:
            thread.safe_stop()
            self._mutex.lock()
            if thread in self._threads:
                self._threads.remove(thread)
            self._mutex.unlock()

    def active_count(self):
        self._mutex.lock()
        count = sum(1 for t in self._threads if t.isRunning())
        self._mutex.unlock()
        return count