"""
File contains the base handler for FishBowl. Will inherit information/functionality from all other sub handlers.

"""

from fish_brain._handlers import _voice_handler


class BaseHandler(voice_handler.GoogleVoiceHandler):

    def __init__(self):
        _voice_handler.GoogleVoiceHandler.__init__(self)