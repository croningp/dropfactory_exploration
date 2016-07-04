import os
import time
import threading

SLEEP_TIME = 60


class AboveHourEvent(threading.Thread):

    def __init__(self, hour, callback, *args):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.hour = hour
        self.callback = callback
        self.args = args

        self.start()

    def run(self):
        self.interrupted.acquire()
        while self.interrupted.locked():
            if time.localtime().tm_hour >= self.hour:
                self.callback(*self.args)
                self.stop()
            time.sleep(SLEEP_TIME)

    def stop(self):
        self.interrupted.release()
