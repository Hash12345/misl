import json, requests
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_watson import (
    IAMTokenManager,
    NaturalLanguageUnderstandingV1,
    TextToSpeechV1
)
from ibm_watson.natural_language_understanding_v1 import (
    Features,
    ConceptsOptions,
    EmotionOptions,
    SemanticRolesOptions,
    SentimentOptions,
    ClassificationsOptions
)
from decouple import config


class IBM_Watson:

    def __init__(self) -> None:
        self.authenticator = None
        self.token = None

    def authenticate(self, apikey): 
        self.token = IAMTokenManager(apikey=apikey).get_token()
        self.authenticator = BearerTokenAuthenticator(self.token)

    def get_natural_language_service(self, version):
        """
        Creates and returns a Natural Language Understanding service client object.

        Args:
            version (str): The API version of the Natural Language Understanding service to use.

        Returns:
            NaturalLanguageUnderstandingV1: The Natural Language Understanding service client object.
        """
        self.authenticate(config("NLP_KEY"))
        service = NaturalLanguageUnderstandingV1(
            version=version,
            authenticator=self.authenticator
        )
        service.set_service_url(config("NLP_BASE_URL"))
        return service
    
    def get_speech_to_text_result(self, file_path):
        """
        Transcribes audio content from an MP3 file using the Speech to Text service.

        Args:
            file_path (str): The path to the MP3 audio file to transcribe.

        Returns:
            str: The transcribed text if successful, otherwise None.

        Raises:
            Exception: If an error occurs during the request.
        """
        self.authenticate(config("STT_API_KEY"))
        transcript = None
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'audio/mp3',
            'x-global-transaction-id': 'presentation-skills-request'
        }
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(config("URL"), headers=headers, files=files)
        if response.status_code == 200:
            transcript = response.json()
        return transcript

    def get_text_to_speech_service(self):
        """
        Creates and returns a Text to Speech service client object.

        Returns:
            TextToSpeechV1: The Text to Speech service client object.
        """
        self.authenticate(config("TTS_API_KE"))
        service = TextToSpeechV1(authenticator=self.authenticator)
        service.set_service_url(config("TTS_BASE_URL"))
        return service
    
    def get_text_concept(self, text):
        """
        Extracts key concepts from a given text using the Natural Language Understanding service.

        Args:
            text (str): The text to analyze for concepts.

        Returns:
            str: A JSON string representation of the analysis results, including identified concepts.
        """
        natural_language_service =  self.get_natural_language_service('2022-04-07')
        response = natural_language_service.analyze(
            text=text,
            features=Features(concepts=ConceptsOptions(limit=3)),
            language="en"
        ).get_result()
        return json.dumps(response, indent=2)
    
    def get_text_emotion(self, text):
        """
        Analyzes the emotional tone of a given text using the Natural Language Understanding service.

        Args:
            text (str): The text to analyze for emotional tone.

        Returns:
            str: A JSON string representation of the analysis results, including identified emotions.
        """
        natural_language_service =  self.get_natural_language_service('2022-04-07')
        response = natural_language_service.analyze(
            text=text,
            features=Features(emotion=EmotionOptions()),
            language="en"
        ).get_result()
        return json.dumps(response, indent=2)
    
    def get_text_semantic_roles(self, text):
        """
        Analyzes the semantic roles of entities within a given text using the Natural Language Understanding service.

        Args:
            text (str): The text to analyze for semantic roles.

        Returns:
            str: A JSON string representation of the analysis results, including identified semantic roles.
        """
        natural_language_service =  self.get_natural_language_service('2022-04-07')
        response = natural_language_service.analyze(
            text=text,
            features=Features(semantic_roles=SemanticRolesOptions()),
            language="en"
        ).get_result()
        return json.dumps(response, indent=2)
    
    def get_text_sentiment(self, text):
        """
        Analyzes the sentiment of a given text using the Natural Language Understanding service.

        Args:
            text (str): The text to analyze for sentiment.

        Returns:
            str: A JSON string representation of the analysis results, including sentiment scores for the document and individual sentences.
        """
        natural_language_service =  self.get_natural_language_service('2022-04-07')
        response = natural_language_service.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(document=False, targets=text.split('.'))),
            language="en"
        ).get_result()
        return json.dumps(response, indent=2)
    
    def get_text_tone(self, text):
        natural_language_service =  self.get_natural_language_service('2022-04-07')
        response = natural_language_service.analyze(
            text=text,
            features=Features(classifications=ClassificationsOptions(model='tone-classifications-en-v1'))
        ).get_result()
        return json.dumps(response, indent=2)
