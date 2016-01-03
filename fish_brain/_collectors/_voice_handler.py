"""
Voice handler. Mainly used to communicate with the computer when external/out and about to set tasks/ perform tasks immediately.
"""

# Import external lib
import e_googlevoice
import BeautifulSoup

# Import python standard lib
import os

# Import FishBowl modules
import settings.const
import settings.user_auth


class GoogleVoiceHandler(object):
    def __init__(self, user_name, user_pass):
        self.voice = self._login(user_name, user_pass)
        if not self.voice:
            print 'Failed to login with creditentials passed in for {0}'.format(user_name)
        self.action_log = []  # List for logging stuff we do.

    ##################
    ## Call Methods ##
    ##################

    def call_public(self, outgoing_number, forwarding_number = None):
        self.action_log.append('Call: {0} from {1}'.format(outgoing_number, forwarding_number))
        self.voice(outgoing_number, forwarding_number)
        return True

    def cancel_call_public(self, outgoing_number, forwarding_number = None):
        self.action_log.append('Cancelling call: {0} from {1}'.format(outgoing_number, forwarding_number))
        self.voice.cancel(outgoing_number, forwarding_number)
        return True

    #################
    ## SMS Methods ##
    #################

    def send_sms(self, outgoing_number, text):
        self.action_log.append('Texting: {0} - {1}'.format(outgoing_number, text))
        self.voice.send_sms(outgoing_number, text)
        return True

    def _extractsms(self, htmlsms):
        """
        extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

        Output is a list of dictionaries, one per message.
        """

        msgitems = [] # accum message items here
        # Extract all conversations by searching for a DIV with an ID at top level.
        tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
        conversations = tree.findAll("div", attrs={"id": True}, recursive=False)
        for conversation in conversations:
            # For each conversation, extract each row, which is one SMS message.
            rows = conversation.findAll(attrs={"class": "gc-message-sms-row"})
            for row in rows:								# for all rows
                # For each row, which is one message, extract all the fields.
                msgitem = {"id": conversation["id"]}		# tag this message with conversation ID
                spans = row.findAll("span", attrs={"class": True}, recursive=False)
                for span in spans:							# for all spans in row
                    cl = span["class"].replace('gc-message-sms-', '')
                    msgitem[cl] = (" ".join( span.findAll( text=True ) ) ).strip()	# put text in dict
                msgitems.append(msgitem)					# add msg dictionary to list
        return msgitems

    def get_sms_messages( self, stored_messages = None):
        """
        Messages are checked from the server. IE All messages.

        :return: [ {'text': text of message, 'from': recieved from, 'id': message_ID, 'time': time recieved } ]
        :rtype: list of dict ( messages )
        """

        self.voice.sms( ) # init SMS
        sms_html = self.voice.sms.html # Grab the html page for the sms section of google voice
        messages = self._extractsms(sms_html) # Extract the sms messages

        if not stored_messages:
            stored_messages = { 'id':[], 'messages':[] }

        for message in messages:
            if settings.const.STORE_SELF_MESSAGES:
                if 'me:' == message['from'].lower():
                    # This is a message from us, so we don't need to check it. We sent it from the google voice number
                    continue

            # If we've already stored this message ID, we don't need to get it again.
            if message['id'] in stored_messages['id']:
                continue

            stored_messages['messages'].append( message )

        return stored_messages

    def update_sms_data(self):
        """
        Get our current storage of messages.
        Get new messages
        Save to data files
        :return:
        :rtype:
        """
        sms_message_data_file = os.path.join(settings.local_const.DATA_LOCATION, settings.const.STORED_MESSAGE_FILE_NAME)
        if not os.path.exists( sms_message_data_file ):
            return False, 'Failed to find sms file {0}'.format( sms_message_data_file )
        stored_messages = self._load_json(sms_message_data_file)
        updated_messages = self.get_sms_messages(stored_messages)
        self._save_json(sms_message_data_file)

        return True, 'Successful save to {0}'.format( sms_message_data_file )

    #####################
    ## Utility Methods ##
    #####################

    @staticmethod
    def _login(user_name=None, user_pass=None):
        # If nothing is passed in for either auth parameter, we use the settings.user_auth information.
        # This will allow us to make calls/etc. from other Google accounts in the future if desired.
        if not user_name or user_pass:
            user_name = settings.user_auth.VOICE_USERNAME
            user_pass = settings.user_auth.VOICE_USERPASS

        voice = e_googlevoice.Voice()
        # Login here. We need to probably have a check to be sure that we successfully logged in first.
        voice.login(user_name, user_pass)
        return voice

    @staticmethod
    def _load_json( path ):
        with open( path, 'r' ) as fp:
            contents = json.loads( fp.read( ) )
        return contents

    @staticmethod
    def _save_json( path, content ):
        with open( path, 'w' ) as fp:
            json.dumps( contents )
        return True

    def _get_creditentials(self):
        pass