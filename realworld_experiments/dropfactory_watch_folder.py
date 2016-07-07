import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

dropfactory_path = os.path.join(HERE_PATH, '..', '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

import logging
logging.basicConfig(level=logging.INFO)

#
import time

#
from manager import manager
from tools.xp_watcher import XPWatcher
from tools import email_notification

from utils.time_event import AboveHourEvent

LAST_HOUR = 22

EMAILS_TO_NOTIFY = ['jonathan.grizou@glasgow.ac.uk']  # must

def send_email_notification(subject, body):
    for toaddr in EMAILS_TO_NOTIFY:
        email_notification.send_email_notification(toaddr, subject, body)

def end_of_day_sequence(watcher):
    print 'Automatically stopping dropfactory at {}'.format(time.ctime())
    send_email_notification('[Dropfactory] Shuting down', 'Automatically stopping dropfactory at {}'.format(time.ctime()))
    watcher.stop()
    manager.empty_XP_queue()
    manager.bypass_waste_security = True  # this should only be done in extreme case like this one
    print 'Waiting for all ongoing XP to finish...'
    manager.wait_until_XP_finished()
    print 'Shutting down python...'
    os._exit(0)


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    response = raw_input('## Do you want to quickly prime the oils and surfactant [y/N]: ')
    if response in ['y', 'Y']:
        manager.add_purge_sequence_XP(n_purge=2)

    watcher = XPWatcher(manager, pool_folder)

    time_keeping = AboveHourEvent(LAST_HOUR, end_of_day_sequence, watcher)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        watcher.join()
        time_keeping.join()
