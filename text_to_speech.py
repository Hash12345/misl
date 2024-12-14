# from decouple import config
import azure.cognitiveservices.speech as speechsdk

def create_speech_from_text(text: str, output_filename: str) -> list:
    """
    synthesize speech from a given text string and saves it to an audio file. Additionally, it extracts word boundaries 
    from the synthesized speech.

    Args:
        text: The text string to be converted into speech.
        output_filename: The filename (including path) where the synthesized audio will be saved. 

    Returns:
        A list of dictionaries containing word boundary information. Each dictionary has the following keys:

        - audio_offset (float): The time offset (in seconds) of the word in the audio file relative to the beginning.
        - duration (float): The duration of the word in seconds.
        - text (str): The actual word text.
        - text_offset (int): The character offset of the word within the original text string.
        - word_length (int): The number of characters in the word.

    Raises:
        ImportError: If the `decouple` or `azure.cognitiveservices.speech` libraries are not installed.
    """
    word_boundaries = []

    def speech_synthesizer_word_boundary_cb(evt: speechsdk.SessionEventArgs):
        word_boundary = {}
        word_boundary['audio_offset'] = (evt.audio_offset + 5000) / 10000
        word_boundary['duration'] = evt.duration
        word_boundary['text'] = evt.text
        word_boundary['text_offset'] = evt.text_offset
        word_boundary['word_length'] = evt.word_length
        word_boundaries.append(word_boundary)

    speech_config = speechsdk.SpeechConfig(
        subscription=config("SPEECH_KEY"),
        region=config("SERVICE_REGION")
    )

    # use the "en-US-AvaNeural" voice by default.
    speech_config.speech_synthesis_voice_name = "en-US-AvaNeural"
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    speech_config.set_property(
        property_id=speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary,
        value='true'
    )
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=output_filename
    )

    ssml = """<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
        <voice name='{}'>
            {}
        </voice>
    </speak>""".format("en-US-AvaNeural", text)
    
    # Synthesize speech from the given SSML string.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    speech_synthesizer.synthesis_word_boundary.connect(speech_synthesizer_word_boundary_cb)
    speech_synthesizer.speak_ssml(ssml)
    word_boundaries = [item for item in word_boundaries if not " " in item['text']]
    word_boundaries = sorted(word_boundaries, key=lambda x: x['text_offset'])

    return word_boundaries
