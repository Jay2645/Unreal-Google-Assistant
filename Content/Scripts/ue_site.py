#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import unreal_engine as ue
from unreal_engine.classes import SoundWaveProcedural

from googlesdk.assistant.embedded.v1alpha1 import embedded_assistant_pb2
from googlesamples.assistant import (
	assistant_helpers,
	audio_helpers,
	auth_helpers,
	common_settings
)
ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'

def setup_assistant():
	""" This sets up the OAuth credentials for the Google Assistant. """
	
	ue.log("Initializing Google Assistant.")
	# Initialize credentials
	credentials = os.path.join(sys.path[0],
								common_settings.ASSISTANT_CREDENTIALS_FILENAME)

	# Load credentials.
	try:
		global creds
		creds = auth_helpers.load_credentials(
			credentials, scopes=[common_settings.ASSISTANT_OAUTH_SCOPE]
		)
	except Exception:
		# Maybe we didn't load the credentials yet?
		# This could happen on first run
		client_secret = os.path.join(sys.path[0], 'client_secrets.json')
		creds = auth_helpers.credentials_flow_interactive(client_secret, common_settings.ASSISTANT_OAUTH_SCOPE)
		auth_helpers.save_credentials(credentials, creds)
		try:
			creds = auth_helpers.load_credentials(
				credentials, scopes=[common_settings.ASSISTANT_OAUTH_SCOPE]
			)
		except Exception as e:
			ue.log_error('Error loading credentials: ' + str(e))
			ue.log_error('Run auth_helpers to initialize new OAuth2 credentials.')
			# Return invalid status code
			return -1
			
	# Define endpoint
	# This might where you can inject custom API.AI behaviors?
	api_endpoint = ASSISTANT_API_ENDPOINT

	# Create an authorized gRPC channel.
	grpc_channel = auth_helpers.create_grpc_channel(
		api_endpoint, creds
	)
	ue.log('Connecting to '+ str(api_endpoint))
	
	global assistant
	assistant = embedded_assistant_pb2.EmbeddedAssistantStub(grpc_channel)
	return 0 # Initialized Google Assistant successfully
			
def setup_unreal_engine_audio(audio_component):
	# Set up Unreal Audio Component
	global procedural_audio_wave
	procedural_audio_wave = SoundWaveProcedural()
	
	# Set up audio parameters
	audio_sample_rate = common_settings.DEFAULT_AUDIO_SAMPLE_RATE
	audio_sample_width = common_settings.DEFAULT_AUDIO_SAMPLE_WIDTH
	audio_iter_size = common_settings.DEFAULT_AUDIO_ITER_SIZE
	audio_block_size = common_settings.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
	audio_flush_size = common_settings.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
	
	audio_component.SetSound(procedural_audio_wave)
		
	# Configure audio source and sink.
	audio_device = None
	audio_source = audio_device = (
		audio_device or audio_helpers.UnrealSoundStream(
			sample_rate=audio_sample_rate,
			sample_width=audio_sample_width,
			block_size=audio_block_size,
			flush_size=audio_flush_size,
			procedural_audio_wave=procedural_audio_wave
		)
	)

	audio_sink = audio_device = (
		audio_device or audio_helpers.UnrealSoundStream(
			sample_rate=audio_sample_rate,
			sample_width=audio_sample_width,
			block_size=audio_block_size,
			flush_size=audio_flush_size,
			procedural_audio_wave=procedural_audio_wave
		)
	)
		
	# Create conversation stream with the given audio source and sink.
	global conversation_stream
	conversation_stream = audio_helpers.ConversationStream(
		source=audio_source,
		sink=audio_sink,
		iter_size=audio_iter_size,
		sample_width=audio_sample_width,
	)
	
setup_assistant()