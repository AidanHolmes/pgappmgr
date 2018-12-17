#    Class objects to implement Subject and Observer patterns for Python applications
#    Copyright (C) 2018  Aidan Holmes
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Email - aholmes@orbitalfruit.co.uk

class AppPublisher(object):
        def __init__(self, messagequeue=None):
                self.message_queue = messagequeue

        def notify_subscription(self, msgid, context):
                pass

        def register_message(self, msgid):
                'Thin wrapper to call message queue'
                if self.message_queue is not None:
                        return self.message_queue.register_message(self, msgid)

        def remove_message(self,msgid):
                'Thin wrapper to unregister a message in the queue'
                if self.message_queue is not None:
                        return self.message_queue.remove_message(self, msgid)
		
class AppSubscriber(object):
        def __init__(self, messagequeue=None):
                self.message_queue = messagequeue

        def subscribe_message(self, msgid, context, callback):
                'Thin wrapper to subscribe to a message in the queue'
                if self.message_queue is not None:
                        self.message_queue._subscribe_message(self, msgid, context, callback)

        def unsubscribe_message(self, msgid):
                'Thin wrapper to unsubscribe to a message in the queue'
                if self.message_queue is not None:
                        while self.message_queue._unsubscribe_message(self, msgid): pass

class MessageQueue(object):
        def __init__(self):
                # Array of subjects associated with the message ID
                self._subjectreg = {}
                # Subscription tuple array per message ID of (observer, context, callback)
                self._subscriptions = {}

        def register_message(self, subject, msgid):
                'Register a subject for a message ID. More than one subject can listen on a message ID'
                # Create a new list to store the subject object for a new message identifier
                if msgid not in self._subjectreg:
                        self._subjectreg[msgid] = []

                # Only add the subject once for a message
                if subject not in self._subjectreg[msgid]:
                        self._subjectreg[msgid].append(subject)
                        # Are there subscriptions already made? Call the notification
                        if msgid in self._subscriptions:
                                for subs in self._subscriptions[msgid]:
                                        _notify_subject_registration(msgid, subs[1])
                        return True
                # return False if the message was already registered
                return False

        def remove_message(self, subject, msgid):
                'Remove a subject handler for a message ID'
                if msgid in self._subjectreg:
                        if subject in self._subjectreg[msgid]:
                                self._subjectreg[msgid].remove(subject)
                                return True
                # returns False if the message wasn't there to be removed
                return False

        def _subscribe_message(self, observer, msgid, context, callback):
                'Internal queue function for observers to subscribe to messages'
                if msgid not in self._subscriptions:
                        self._subscriptions[msgid] = []
                # Note that duplicates could be entered by a subscriber! No checks are made
                self._subscriptions[msgid].append((observer, context, callback))
                # Notify the subject of the new subscriber
                self._notify_subject_registration(msgid, context)

        def _notify_subject_registration(self, msgid, context):
                'Function to notify all subjects registered to a message that an observer has registered'
                if msgid in self._subjectreg:
                        for subject in self._subjectreg[msgid]:
                                # send the notification to the subject
                                subject.notify_subscription(msgid, context)

        def _unsubscribe_message(self, observer, msgid):
                'Internal queue function to remove an observer from a message ID and stop listening'
                if msgid in self._subscriptions:
                        for sub_index in range(len(self._subscriptions[msgid])):
                                # if the observer is in the array then delete just once and quit the loop
                                if self._subscriptions[sub_index][0] == observer:
                                        self._subscriptions.pop(sub_index)
                                        return True
                # Nothing removed
                return False
        
        def post_message(self, msgid, context, message):
                'Post a message to the message queue for observers'
                if msgid in self._subscriptions:
                        for registration in self._subscriptions[msgid]:
                                registration[2](msgid, context, message)
			
	
