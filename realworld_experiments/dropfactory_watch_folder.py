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
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='dropfactory.log', filemode='w', level=logging.DEBUG)

#
import time

#
from tools.xp_watcher import XPWatcher
from utils.time_event import AboveHourEvent
from tools import email_notification

LAST_HOUR = 22

EMAILS_TO_NOTIFY = ['jonathan.grizou@glasgow.ac.uk']  # must be a list
# EMAILS_TO_NOTIFY = ['jonathan.grizou@glasgow.ac.uk', 'l.points.1@research.gla.ac.uk']  # must be a list

def send_email_notification(subject, body):
    for toaddr in EMAILS_TO_NOTIFY:
        email_notification.send_email_notification(toaddr, subject, body)

# define end of day sequence here, it needs manager
def end_of_day_sequence(manager, watcher):
    print 'Automatically stopping dropfactory at {}'.format(time.ctime())
    send_email_notification('[Dropfactory] Shuting down', 'Automatically stopping dropfactory at {}'.format(time.ctime()))
    watcher.stop()
    manager.empty_XP_queue()
    manager.bypass_waste_security = True  # this should only be done in extreme case like this one
    print 'Waiting for all ongoing XP to finish...'
    manager.wait_until_XP_finished()
    print 'Cleaning oil head...'
    manager.clean_oil_head()
    print 'Cleaning surfactant pump...'
    manager.clean_surfactant_pump()
    print 'Shutting down python...'
    os._exit(0)


if __name__ == '__main__':

    import sys

    # check dummy mistake before accessing the platform
    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    if not os.path.exists(pool_folder):
        raise Exception('The folder does not exists: {}!'.format(pool_folder))

    ##import mmanager now
    from manager import manager

    # asking for purge
    response = raw_input('## Do you want to quickly prime the oils and surfactant [Y/n]: ')
    if response not in ['n', 'N']:
        user_input_validated = False
        while not user_input_validated:
            response = raw_input('How many purge do you want [default is 4]: ')
            if response == '':
                response = '4'
            if response.isdigit():
                n_purge = int(response)
                user_input_validated = True
            else:
                print '{} is not a valid number, you must provide a positive int or 0'.format(response)
        print 'Great, purging {} times'.format(n_purge)
        manager.add_purge_sequence_XP(n_purge=n_purge)

    # start to add XP watched to manager
    watcher = XPWatcher(manager, pool_folder)

    time_keeping = AboveHourEvent(LAST_HOUR, end_of_day_sequence, manager, watcher)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        watcher.join()
        time_keeping.join()
