"""
File contains the base handler for FishBowl. Will inherit information/functionality from all other sub handlers.
"""

import _voice_handler


class BaseHandler(_voice_handler.GoogleVoiceHandler):

    def __init__(self):
        _voice_handler.GoogleVoiceHandler.__init__(self)