#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path
import ue_site
import unreal_engine as ue

import threaded_assistant

import grpc
from unreal_engine.classes import AudioComponent

class Hero:
	# this is called on game start
	def begin_play(self):
		"""Samples for the Google Assistant API.

		Examples:
		  Run the sample with microphone input and speaker output:

			$ python -m googlesamples.assistant

		  Run the sample with file input and speaker output:

			$ python -m googlesamples.assistant -i <input file>

		  Run the sample with file input and output:

			$ python -m googlesamples.assistant -i <input file> -o <output file>
		"""
		self.audio_component = self.uobject.get_component_by_type(AudioComponent)
		ue_site.setup_unreal_engine_audio(self.audio_component)
		
	# this is called at every 'tick'
	def tick(self, delta_time):
		if self.uobject.is_input_key_down('Q'):
			try:
				# Only try to start a new conversation if one is not active
				if not self.assistant.is_alive():
					self.assistant = threaded_assistant.ThreadedAssistant()
					self.assistant.start()
			except AttributeError:
				# This happens the first time we attempt to start a conversation
				self.assistant = threaded_assistant.ThreadedAssistant()
				self.assistant.start()
