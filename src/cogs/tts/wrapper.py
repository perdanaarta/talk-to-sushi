from dataclasses import dataclass
from typing import Optional
from gtts import gTTS
from google.cloud.texttospeech import TextToSpeechClient, SynthesisInput, AudioConfig, AudioEncoding, VoiceSelectionParams

from .dictionary import languages, wavenets, wavenet_support, accents
from main import config

gcloud = None

@dataclass
class VoiceConfig:
    lang: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    rate: Optional[float] = None
    pitch: Optional[float] = None

@dataclass
class VoiceResult:
    text: str
    audio: str

    def save(self, path):
        """Save into audio file"""

        with open(path, "wb") as out:
            out.write(self.audio)

class TalkToSpeechWrapper():
    """:params:
    
    'lang' = Language of the voice
    'gender' = Gender of the voice
    'rate' = Speaking rate of the voice
    'pitch' = Pitch for the voice
    """
    def __init__(self):
        self.gcloud = self.connect_gcloud()


    def connect_gcloud(self):
        global gcloud
        
        if gcloud is None:
            try:
                gcloud = TextToSpeechClient.from_service_account_file(config.GCLOUD_API_KEY)
            except:
                gcloud = None

        return gcloud

            
    def synthesize_speech(self, input: str, config: VoiceConfig) -> VoiceResult:
        """Transform text into audio"""            

        config, engine = self.check_config(config)
        if engine == "gtts" or self.gcloud == None:
            audio = self.gtts(input, config)

        elif engine == "gcs":
            audio = self.gcs(input, config)

        return VoiceResult(input, audio)


    def check_config(self, config: VoiceConfig) -> tuple[str, VoiceConfig]:
        """Checking if config is using gtts engine or gcs engine"""

        def get_wavenet(gender):
            for wn in wavenets[config.lang]:
                if wn['gender'].lower() == gender:
                    return wn['name']

        if config.lang in wavenet_support and config.gender is not None:
            config.lang = wavenet_support[config.lang]
            config.name = get_wavenet(config.gender)

        elif config.lang in accents:
            config.lang = wavenet_support[config.lang]
            config.name = get_wavenet('female')

        if config.lang in wavenet_support:
            engine = "gcs"
        else:
            engine = "gtts"

        return config, engine


    def gtts(self, text: str, config: VoiceConfig) -> bytes:
        """Transform text into audio bytes using gtts"""

        lang = "en" if config.lang is None else config.lang

        def process(text: str):
            for bit in (gTTS(text, 'com', lang).stream()): 
                return(bit)
                
        try:
            audio_data, line = b'', ""

            for word in text.split(" "):
                if len(line) + 1 + len(word) > 100:
                    audio_data += process(line)
                    line = ""
                    line += word

                else:
                    line += " " + word

            audio_data = audio_data + process(line)
            return audio_data
        
        except:
            return process('please dont abuse me')
    

    def gcs(self, text: str, config: VoiceConfig) -> bytes:
        """Transform text into audio bytes using gcs text to speech"""

        lang = config.lang
        name = config.name
        rate = 1.0 if config.rate is None else config.rate
        pitch = 0.0 if config.pitch is None else config.pitch

        text_input = SynthesisInput(text=text)
        audio_config = AudioConfig(
            audio_encoding = AudioEncoding.LINEAR16,
            speaking_rate = rate,
            pitch = pitch
        )

        voice_params = VoiceSelectionParams(
            language_code = lang,
            name = name
        )

        response = self.gcloud.synthesize_speech(input=text_input,
                                                 voice=voice_params,
                                                 audio_config=audio_config)

        return response.audio_content
