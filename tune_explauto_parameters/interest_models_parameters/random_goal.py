import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


import tools


if __name__ == '__main__':

    results = tools.run_random_goal()
    tools.save_to_json(results, os.path.join(HERE_PATH, 'random_goal.json'))
