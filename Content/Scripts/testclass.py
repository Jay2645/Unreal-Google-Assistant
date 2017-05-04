#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path
import unreal_engine as ue

import sys

sys.path.append('~/.local/lib/python3.5/site-packages')
import grpc
from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2
from google.rpc import code_pb2
#from tenacity import retry, stop_after_attempt, retry_if_exception
from googlesamples.assistant import (
    assistant_helpers,
    audio_helpers,
    auth_helpers,
    common_settings
)

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.ConverseResult.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.ConverseResult.CLOSE_MICROPHONE

class SampleAssistant(object):
    """Sample Assistant that supports follow-on conversations.

    Args:
      conversation_stream(ConversationStream): audio stream
        for recording query and playing back assistant answer.
      channel: authorized gRPC channel for connection to the
        Google Assistant API.
      deadline_sec: gRPC deadline in seconds for Google Assistant API call.
    """
    def __init__(self, conversation_stream, channel, deadline_sec):
        self.conversation_stream = conversation_stream

        # Opaque blob provided in ConverseResponse that,
        # when provided in a follow-up ConverseRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Converse()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        self.conversation_state = None

        # Create Google Assistant API gRPC client.
        self.assistant = embedded_assistant_pb2.EmbeddedAssistantStub(channel)
        self.deadline = deadline_sec

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False
        self.conversation_stream.close()

    def is_grpc_error_unavailable(e):
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            ue.log_error('grpc unavailable error: %s', e)
            return True
        return False

    #@retry(reraise=True, stop=stop_after_attempt(3),
    #       retry=retry_if_exception(is_grpc_error_unavailable))
    def converse(self):
        """Send a voice request to the Assistant and playback the response.

        Returns: True if conversation should continue.
        """
        continue_conversation = False

        self.conversation_stream.start_recording()
        ue.log('Recording audio request.')

        def iter_converse_requests():
            for c in self.gen_converse_requests():
                assistant_helpers.log_converse_request_without_audio(c)
                yield c
            self.conversation_stream.start_playback()

        # This generator yields ConverseResponse proto messages
        # received from the gRPC Google Assistant API.
        for resp in self.assistant.Converse(iter_converse_requests(),
                                            self.deadline):
            assistant_helpers.log_converse_response_without_audio(resp)
            if resp.error.code != code_pb2.OK:
                ue.log_error('server error: %s', resp.error.message)
                break
            if resp.event_type == END_OF_UTTERANCE:
                ue.log('End of audio request detected')
                self.conversation_stream.stop_recording()
            if resp.result.spoken_request_text:
                ue.log('Transcript of user request: "%s".',
                             resp.result.spoken_request_text)
                ue.log('Playing assistant response.')
            if len(resp.audio_out.audio_data) > 0:
                self.conversation_stream.write(resp.audio_out.audio_data)
            if resp.result.spoken_response_text:
                ue.log(
                    'Transcript of TTS response '
                    '(only populated from IFTTT): "%s".',
                    resp.result.spnoken_response_text)
            if resp.result.conversation_state:
                self.conversation_state = resp.result.conversation_state
            if resp.result.volume_percentage != 0:
                self.conversation_stream.volume_percentage = (
                    resp.result.volume_percentage
                )
            if resp.result.microphone_mode == DIALOG_FOLLOW_ON:
                continue_conversation = True
                ue.log('Expecting follow-on query from user.')
            elif resp.result.microphone_mode == CLOSE_MICROPHONE:
                continue_conversation = False
        ue.log('Finished playing assistant response.')
        self.conversation_stream.stop_playback()
        return continue_conversation

    def gen_converse_requests(self):
        """Yields: ConverseRequest messages to send to the API."""

        converse_state = None
        if self.conversation_state:
            ue.log('Sending converse_state: %s',
                          self.conversation_state)
            converse_state = embedded_assistant_pb2.ConverseState(
                conversation_state=self.conversation_state,
            )
        config = embedded_assistant_pb2.ConverseConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            converse_state=converse_state
        )
        # The first ConverseRequest must contain the ConverseConfig
        # and no audio data.
        yield embedded_assistant_pb2.ConverseRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.ConverseRequest(audio_in=data)

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
        ue.log('Initializing Google Samples API.')

        # Initialize defaults
        credentials = os.path.join(sys.path[0],
                                   common_settings.ASSISTANT_CREDENTIALS_FILENAME)

        # Load credentials.
        try:
            creds = auth_helpers.load_credentials(
                credentials, scopes=[common_settings.ASSISTANT_OAUTH_SCOPE]
            )
        except Exception as e:
            #logging.error('Error loading credentials: %s', e)
            #logging.error('Run auth_helpers to initialize new OAuth2 credentials.')
            ue.log_error('Error loading credentials: ' + str(e))
            ue.log_error('Run auth_helpers to initialize new OAuth2 credentials.')
            return

    # this is called at every 'tick'
    def tick(self, delta_time):
        # get current location
        location = self.uobject.get_actor_location()
        # increase Z honouring delta_time
        location.z += 1000 * delta_time
        # set new location
        self.uobject.set_actor_location(location)
