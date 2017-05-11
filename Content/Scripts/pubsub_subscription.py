#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ue_site
from threading import Thread
import unreal_engine as ue

class SubscriptionThread(Thread):

  def __init__(self, msg_queue):

    Thread.__init__(self)

    self.shutdown_flag = Event()

    # Create a new pull subscription on the given topic
    pubsub_client = pubsub.Client(project=PUBSUB_PROJECT_ID, credentials=creds)
    topic_name = 'unreal_google_assistant'
    topic = pubsub_client.topic(topic_name)

    subscription_name = 'UnrealGoogleAssistantSub'
    self.subscription = topic.subscription(subscription_name)
    try:
      self.subscription.create()
      ue.log('Subscription created')
    except Exception as e:
      ue.log_error('Subscription already exists! '+str(e))

  def run(self):
    """ Poll for new messages from the pull subscription """

    while True:
      # pull messages
      results = self.subscription.pull(return_immediately=True)

      for ack_id, message in results:

          # convert bytes to string and slice string
          # http://stackoverflow.com/questions/663171/is-there-a-way-to-substring-a-string-in-python
          json_string = str(message.data)[3:-2]
          json_string = json_string.replace('\\\\', '')
          ue.log(json_string)

          # create dict from json string
          try:
              json_obj = json.loads(json_string)
          except Exception as e:
              ue.log_error('JSON Error: %s', e)

          # get intent from json
          intent = json_obj['intent']
          ue.log('pub/sub: ' + intent)

          # perform action based on intent
          if intent == 'move_character':
			ue.log(str(json_obj['move'])

          #elif intent == 'prime_pump_end':
          #  if PRIME_WHICH != None:
          #    ue.log('Stop priming pump ' + PRIME_WHICH)
          #    self.msg_queue.put('b' + PRIME_WHICH + 'l!') # turn off relay
          #    PRIME_WHICH = None

          #elif intent == 'make_drink':
          #  make_drink(json_obj['drink'], self.msg_queue)

      # ack received message
      if results:
        self.subscription.acknowledge([ack_id for ack_id, message in results])

      time.sleep(0.25)