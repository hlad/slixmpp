"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of SleekXMPP.

    See the file license.txt for copying permissio
"""

import logging
from . import base
from .. xmlstream.handler.callback import Callback
from .. xmlstream.matcher.xpath import MatchXPath
from .. xmlstream.stanzabase import ElementBase, ET, JID
from .. stanza.message import Message


class ChatState(ElementBase):
    namespace = 'http://jabber.org/protocol/chatstates'
    plugin_attrib = 'chat_state'
    interface = set(('state',))
    states = set(('active', 'composing', 'gone', 'inactive', 'paused'))
    
    def active(self):
        self.setState('active')
        
    def composing(self):
        self.setState('composing')

    def gone(self):
        self.setState('gone')

    def inactive(self):
        self.setState('inactive')

    def paused(self):
        self.setState('paused')

    def setState(self, state):
        if state in self.states:
            self.name = state
            self.xml.tag = state
            self.xml.attrib['xmlns'] = self.namespace

    def getState(self):
        return self.name

# In order to match the various chat state elements,
# we need one stanza object per state, even though
# they are all the same except for the initial name
# value. Do not depend on the type of the chat state
# stanza object for the actual state.

class Active(ChatState):
    name = 'active'
class Composing(ChatState):
    name = 'composing'
class Gone(ChatState):
    name = 'gone'
class Inactive(ChatState):
    name = 'inactive'
class Paused(ChatState):
    name = 'paused'


class xep_0085(base.base_plugin):
    """
    XEP-0085 Chat State Notifications
    """
    
    def plugin_init(self):
        self.xep = '0085'
        self.description = 'Chat State Notifications'
        
        handlers = [('Active Chat State', 'active'),
                    ('Composing Chat State', 'composing'),
                    ('Gone Chat State', 'gone'),
                    ('Inactive Chat State', 'inactive'),
                    ('Paused Chat State', 'paused')]
        for handler in handlers:
            self.xmpp.registerHandler(
                Callback(handler[0], 
                         MatchXPath("{%s}message/{%s}%s" % (self.xmpp.default_ns, 
                                                            ChatState.namespace,
                                                            handler[1])), 
                         self._handleChatState))

        self.xmpp.stanzaPlugin(Message, Active)
        self.xmpp.stanzaPlugin(Message, Composing)
        self.xmpp.stanzaPlugin(Message, Gone)
        self.xmpp.stanzaPlugin(Message, Inactive)
        self.xmpp.stanzaPlugin(Message, Paused)
        
    def post_init(self):
        base.base_plugin.post_init(self)
        self.xmpp.plugin['xep_0030'].add_feature('http://jabber.org/protocol/chatstates')
        
    def _handleChatState(self, msg):
        state = msg['chat_state'].name
        logging.debug("Chat State: %s, %s" % (state, msg['from'].jid))
        self.xmpp.event('chatstate_%s' % state, msg)
