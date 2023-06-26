from google.cloud.texttospeech import TextToSpeechClient, SynthesisInput, AudioConfig, AudioEncoding, VoiceSelectionParams


class GoogleTTS():
    def __init__(self, gcloud: TextToSpeechClient, text: str, language='en', voice_name='en-US-Wavenet-A', rate=1.0, pitch=0.0):
        self.gcloud = gcloud
        self.language = language
        self.voice_name = voice_name
        self.rate = rate
        self.pitch = pitch
        self.text = text
        self.result = b''

    def convert(self) -> bytes:
        """Convert text into audio bytes using Google Cloud tts"""

        text_input = SynthesisInput(text=self.text)
        audio_config = AudioConfig(
            audio_encoding=AudioEncoding.LINEAR16,
            speaking_rate=self.rate,
            pitch=self.pitch
        )

        voice_params = VoiceSelectionParams(
            language_code=self.language,
            name=self.name
        )

        response = self.gcloud.synthesize_speech(input=text_input,
                                                 voice=voice_params,
                                                 audio_config=audio_config)

        self.result = response.audio_content
        return self.result
