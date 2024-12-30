class Communication:

    def __init__(self, messageType, message, sender=None, recipient=None):

        self.messageType = messageType
        self.message = message
        self.sender = sender
        self.recipient = recipient