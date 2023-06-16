import json

from ibm_watson import NaturalLanguageUnderstandingV1, SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, ClassificationsOptions

import config
# from WaveProcessor import WaveProcessor

class EmotionExtractor():
    """
    A class to extract emotions from speech using IBM Watson Speech-to-Text and Natural Language Understanding services.

    Attributes:
        nlu (NaturalLanguageUnderstandingV1): Instance of the Natural Language Understanding service.
        stt (SpeechToTextV1): Instance of the Speech-to-Text service.
        nlu_model_id (str): The ID of the Natural Language Understanding model.
        stt_model_id (str): The ID of the Speech-to-Text model.
        text (str): The most recent transcribed text from the audio file.
    """
    def __init__(self):
        """
        Initializes EmotionExtractor class with the IBM Cloud authentication details for the Speech-to-Text and Natural Language Understanding services.
        """

        # Authenticate Natural Language Understanding model with IBM Cloud
        self.nlu = NaturalLanguageUnderstandingV1(
            version='2022-04-07',
            authenticator=IAMAuthenticator(config.NLU_API_KEY)
        )

        self.nlu.set_service_url(config.NLU_URL)
        self.nlu_model_id = config.NLU_MODEL_ID

        # Authenticate Speech-to-Text model with IBM Cloud
        self.stt = SpeechToTextV1(
            authenticator=IAMAuthenticator(config.STT_API_KEY)
        )

        self.stt.set_service_url(config.STT_URL)
        self.stt_model_id = config.STT_MODEL_ID

        self.text = ""

    def get_stt_response(self, path):
        """
        Returns the transcribed text from a given audio file.

        Args:
            path (str): A string representing the path to the audio file.

        Returns:
            str: A string representing the transcribed text from the audio file.
        """

        # Transcribe the speech
        with open(path, 'rb') as proc_audio_file:

            stt_response = self.stt.recognize(
                audio=proc_audio_file,
                content_type='audio/mp3',
                model=self.stt_model_id,
                inactivity_timeout=360,
            ).get_result()

        text = ""
        for result in stt_response['results']:
            text += result['alternatives'][0]['transcript']

        print(text)

        self.text = text
        return text

    def get_nlu_response(self, text=None):
        """
        Analyzes the tone of a given text and returns the emotions.

        Args:
            text (str, optional): A string representing the text to be analyzed. If None, the text will be the most recent transcribed text from the get_stt_response function. Defaults to None.

        Returns:
            list: A list of emotions and their confidence levels as determined by the NLU model.
        """

        if text is None:
            text = self.text
        
        # Analyse the tone to get the emotions
        response = self.nlu.analyze(
            text=text,
            features=Features(classifications=ClassificationsOptions(model=config.NLU_MODEL_ID)),
            
        ).get_result()

        return response['classifications']