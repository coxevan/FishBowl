"""
Initializes FishBowl
"""
__author__ = 'evancox'

import util
import fish_brain


def run():
    setup_necessary = util.is_setup_necessary()
    if setup_necessary:
        results, message = util.setup_fishbowl()
        # if setup failed, return False
        if not results:
            return False, message

    fish_brain.start( )


if __name__ != '__main__':
    run()