import os
import time
import threading

import filetools


class Watcher(threading.Thread):

    def __init__(self, folder_to_watch, filename_to_watch, filename_to_ignore, callback, force=False, sleep_time=1):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.folder_to_watch = folder_to_watch
        self.filename_to_watch = filename_to_watch
        self.filename_to_ignore = filename_to_ignore
        self.callback = callback

        self.processed_folder = []

        self.force = force
        self.sleep_time = sleep_time

        self.start()

    def run(self):
        self.interrupted.acquire()
        while self.interrupted.locked():
            folders = filetools.list_folders(self.folder_to_watch)
            folders.sort()
            for folder in folders:
                if folder not in self.processed_folder:
                    watch_file = os.path.join(folder, self.filename_to_watch)
                    ignore_file = os.path.join(folder, self.filename_to_ignore)
                    if os.path.exists(watch_file):
                        if self.force or not os.path.exists(ignore_file):
                            self.callback(folder, watch_file)
                            self.processed_folder.append(folder)
            time.sleep(self.sleep_time)

    def stop(self):
        self.interrupted.release()
