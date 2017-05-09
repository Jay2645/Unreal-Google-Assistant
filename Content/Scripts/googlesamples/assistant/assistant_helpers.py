# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper functions for the Google Assistant API."""

import logging
import unreal_engine as ue

from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2


END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE


def log_converse_request_without_audio(converse_request):
	"""Log ConverseRequest fields without audio data."""
	#resp_copy = embedded_assistant_pb2.ConverseRequest()
	#resp_copy.CopyFrom(converse_request)
	#if len(resp_copy.audio_in) > 0:
	#	size = len(resp_copy.audio_in)
	#	resp_copy.ClearField('audio_in')
	#	ue.log('ConverseRequest: audio_in (' + str(size) + ' bytes)')
	#	return
	#ue.log('ConverseRequest: ' + str(resp_copy))


def log_converse_response_without_audio(converse_response):
	"""Log ConverseResponse fields without audio data."""
	#resp_copy = embedded_assistant_pb2.ConverseResponse()
	#resp_copy.CopyFrom(converse_response)
	#has_audio_data = (resp_copy.HasField('audio_out') and
	#				  len(resp_copy.audio_out.audio_data) > 0)
	#if has_audio_data:
	#	size = len(resp_copy.audio_out.audio_data)
	#	resp_copy.audio_out.ClearField('audio_data')
	#	if resp_copy.audio_out.ListFields():
	#		ue.log('ConverseResponse: '+ str(resp_copy) +' audio_data ('+ str(size)+' bytes)')
	#	else:
	#		ue.log('ConverseResponse: audio_data ('+str(size)+' bytes)')
	#		return
	#	ue.log('ConverseResponse: '+str(resp_copy))
