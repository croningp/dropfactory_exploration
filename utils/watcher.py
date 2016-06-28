import os
import time
import threading

import filetools

SLEEP_TIME = 1


class Watcher(threading.Thread):

    def __init__(self, folder_to_watch, filename_to_watch, filename_to_ignore, callback):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.folder_to_watch = folder_to_watch
        self.filename_to_watch = filename_to_watch
        self.filename_to_ignore = filename_to_ignore
        self.callback = callback

        self.start()

    def run(self):
        self.interrupted.acquire()
        while self.interrupted.locked():
            folders = filetools.list_folders(self.folder_to_watch)
            folders.sort()
            for folder in folders:
                watch_file = os.path.join(folder, self.filename_to_watch)
                ignore_file = os.path.join(folder, self.filename_to_ignore)
                if os.path.exists(watch_file) and not os.path.exists(ignore_file):

                    print 'Ready to process {}'.format(watch_file)
                    raw_input('Press enter to continue..')

                    self.callback(folder, watch_file)
            time.sleep(SLEEP_TIME)

    def stop(self):
        self.interrupted.release()
