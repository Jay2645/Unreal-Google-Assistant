#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
import unreal_engine as ue
import ue_site

# Google Assistant imports
from googlesdk.assistant.embedded.v1alpha1 import embedded_assistant_pb2
from googlesamples.assistant import common_settings

# General Google imports
from google.rpc import code_pb2

END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.ConverseResult.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.ConverseResult.CLOSE_MICROPHONE

class ThreadedAssistant(Thread):
	def __init__(self):

		# Opaque blob provided in ConverseResponse that,
		# when provided in a follow-up ConverseRequest,
		# gives the Assistant a context marker within the current state
		# of the multi-Converse()-RPC "conversation".
		# This value, along with MicrophoneMode, supports a more natural
		# "conversation" with the Assistant.
		self.conversation_state = None

		# Create Google Assistant API gRPC client.
		self.deadline = common_settings.DEFAULT_GRPC_DEADLINE
		
		Thread.__init__(self)
		
	def __enter__(self):
		return self

	def __exit__(self, etype, e, traceback):
		if e:
			return False
		ue_site.conversation_stream.close()

	def is_grpc_error_unavailable(e):
		is_grpc_error = isinstance(e, grpc.RpcError)
		if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
			ue.log_error('grpc unavailable error: %s', e)
			return True
		return False

	def run(self):
		"""Send a voice request to the Assistant and playback the response.

		Returns: True if conversation should continue.
		"""
		continue_conversation = False

		ue_site.conversation_stream.start_recording()
		ue.log('Recording audio request.')

		# This generator yields ConverseResponse proto messages
		# received from the gRPC Google Assistant API.
		for resp in ue_site.assistant.Converse(self.gen_converse_requests(),
											self.deadline):
			# Something went wrong
			if resp.error.code != code_pb2.OK:
				ue.log_error('Server error: ' + str(resp.error.message))
				break
			
			# Detected the user is done talking
			if resp.event_type == END_OF_UTTERANCE:
				ue.log('End of audio request detected')
				ue_site.conversation_stream.stop_recording()
			
			# We parsed what the user said
			if resp.result.spoken_request_text:
				ue.log('Transcript of user request: ' +
							 str(resp.result.spoken_request_text))
							 
			# We have a response ready to play out the speakers
			if len(resp.audio_out.audio_data) > 0:
				ue_site.conversation_stream.write(resp.audio_out.audio_data)
			
			# We have an updated conversation state
			if resp.result.conversation_state:
				self.conversation_state = resp.result.conversation_state
			
			# Volume level needs to be updated
			if resp.result.volume_percentage != 0:
				ue_site.conversation_stream.volume_percentage = (
					resp.result.volume_percentage
				)
			
			# Check if user should reply
			if resp.result.microphone_mode == DIALOG_FOLLOW_ON:
				# Expecting user to reply
				continue_conversation = True
				ue.log('Expecting follow-on query from user.')
			elif resp.result.microphone_mode == CLOSE_MICROPHONE:
				# Not expecting user to reply
				continue_conversation = False

		ue.log('Finished playing assistant response.')
		ue_site.conversation_stream.stop_playback()
		return continue_conversation

	def gen_converse_requests(self):
		"""Generates ConverseRequest messages to send to the API.
		This happens over multiple frames, so it should be run in a separate thread.
		Otherwise it WILL lock up the game thread while it's "thinking."
		"""

		converse_state = None
		
		if self.conversation_state:
			ue.log('Sending converse_state: '+ str(self.conversation_state))
			converse_state = embedded_assistant_pb2.ConverseState(
				conversation_state=self.conversation_state,
			)
		
		# Generate the config for the assistant
		config = embedded_assistant_pb2.ConverseConfig(
			audio_in_config=embedded_assistant_pb2.AudioInConfig(
				encoding='LINEAR16',
				sample_rate_hertz=ue_site.conversation_stream.sample_rate,
			),
			audio_out_config=embedded_assistant_pb2.AudioOutConfig(
				encoding='LINEAR16',
				sample_rate_hertz=ue_site.conversation_stream.sample_rate,
				volume_percentage=ue_site.conversation_stream.volume_percentage,
			),
			converse_state=converse_state
		)
		
		# The first ConverseRequest must contain the ConverseConfig
		# and no audio data.
		yield embedded_assistant_pb2.ConverseRequest(config=config)
		
		# Below, we actually activate the microphone and begin recording.
		for data in ue_site.conversation_stream:
			# Subsequent requests need audio data, but not config.
			yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
		ue_site.conversation_stream.start_playback()