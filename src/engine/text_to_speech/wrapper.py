from google.cloud.texttospeech import TextToSpeechClient
from . import TranslateTTS, GoogleTTS

gcloud = None


class Dictionary():
    accents = ['gb', 'au', 'in', 'be', 'tw']

    languages = [
        'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el',
        'en', 'eo', 'es', 'et', 'fi', 'fr', 'gu', 'hi', 'hr', 'hu',
        'hy', 'id', 'is', 'it', 'iw', 'ja', 'jw', 'km', 'kn', 'ko',
        'la', 'lv', 'mk', 'ml', 'mr', 'ms', 'my', 'ne', 'nl', 'no',
        'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sq', 'sr', 'su', 'sv',
        'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh',
        'gb', 'au', 'in', 'be', 'tw'
    ]

    wavenets = {
        'ar-XA': [{'name': 'ar-XA-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'ar-XA-Wavenet-B', 'gender': 'MALE'}],
        'bn-IN': [{'name': 'bn-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'bn-IN-Wavenet-B', 'gender': 'MALE'}],
        'en-GB': [{'name': 'en-GB-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'en-GB-Wavenet-B', 'gender': 'MALE'}],
        'fr-CA': [{'name': 'fr-CA-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'fr-CA-Wavenet-B', 'gender': 'MALE'}],
        'en-US': [{'name': 'en-US-Wavenet-G', 'gender': 'FEMALE'}, {'name': 'en-US-Wavenet-B', 'gender': 'MALE'}],
        'es-ES': [{'name': 'es-ES-Wavenet-C', 'gender': 'FEMALE'}, {'name': 'es-ES-Wavenet-B', 'gender': 'MALE'}],
        'gu-IN': [{'name': 'gu-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'gu-IN-Wavenet-B', 'gender': 'MALE'}],
        'ja-JP': [{'name': 'ja-JP-Wavenet-B', 'gender': 'FEMALE'}, {'name': 'ja-JP-Wavenet-C', 'gender': 'MALE'}],
        'kn-IN': [{'name': 'kn-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'kn-IN-Wavenet-B', 'gender': 'MALE'}],
        'ml-IN': [{'name': 'ml-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'ml-IN-Wavenet-B', 'gender': 'MALE'}],
        'mr-IN': [{'name': 'mr-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'mr-IN-Wavenet-B', 'gender': 'MALE'}],
        'sv-SE': [{'name': 'sv-SE-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'sv-SE-Wavenet-C', 'gender': 'MALE'}],
        'ta-IN': [{'name': 'ta-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'ta-IN-Wavenet-B', 'gender': 'MALE'}],
        'tr-TR': [{'name': 'tr-TR-Wavenet-C', 'gender': 'FEMALE'}, {'name': 'tr-TR-Wavenet-B', 'gender': 'MALE'}],
        'ms-MY': [{'name': 'ms-MY-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'ms-MY-Wavenet-B', 'gender': 'MALE'}],
        'pa-IN': [{'name': 'pa-IN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'pa-IN-Wavenet-B', 'gender': 'MALE'}],
        'de-DE': [{'name': 'de-DE-Wavenet-F', 'gender': 'FEMALE'}, {'name': 'de-DE-Wavenet-B', 'gender': 'MALE'}],
        'en-AU': [{'name': 'en-AU-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'en-AU-Wavenet-B', 'gender': 'MALE'}],
        'en-IN': [{'name': 'en-IN-Wavenet-D', 'gender': 'FEMALE'}, {'name': 'en-IN-Wavenet-B', 'gender': 'MALE'}],
        'es-US': [{'name': 'es-US-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'es-US-Wavenet-B', 'gender': 'MALE'}],
        'fr-FR': [{'name': 'fr-FR-Wavenet-E', 'gender': 'FEMALE'}, {'name': 'fr-FR-Wavenet-B', 'gender': 'MALE'}],
        'hi-IN': [{'name': 'hi-IN-Wavenet-D', 'gender': 'FEMALE'}, {'name': 'hi-IN-Wavenet-B', 'gender': 'MALE'}],
        'id-ID': [{'name': 'id-ID-Wavenet-D', 'gender': 'FEMALE'}, {'name': 'id-ID-Wavenet-B', 'gender': 'MALE'}],
        'it-IT': [{'name': 'it-IT-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'it-IT-Wavenet-C', 'gender': 'MALE'}],
        'ko-KR': [{'name': 'ko-KR-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'ko-KR-Wavenet-C', 'gender': 'MALE'}],
        'ru-RU': [{'name': 'ru-RU-Wavenet-E', 'gender': 'FEMALE'}, {'name': 'ru-RU-Wavenet-B', 'gender': 'MALE'}],
        'da-DK': [{'name': 'da-DK-Wavenet-D', 'gender': 'FEMALE'}, {'name': 'da-DK-Wavenet-C', 'gender': 'MALE'}],
        'nb-NO': [{'name': 'nb-NO-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'nb-NO-Wavenet-B', 'gender': 'MALE'}],
        'nl-BE': [{'name': 'nl-BE-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'nl-BE-Wavenet-B', 'gender': 'MALE'}],
        'nl-NL': [{'name': 'nl-NL-Wavenet-D', 'gender': 'FEMALE'}, {'name': 'nl-NL-Wavenet-B', 'gender': 'MALE'}],
        'pt-PT': [{'name': 'pt-PT-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'pt-PT-Wavenet-B', 'gender': 'MALE'}],
        'vi-VN': [{'name': 'vi-VN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'vi-VN-Wavenet-B', 'gender': 'MALE'}],
        'pl-PL': [{'name': 'pl-PL-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'pl-PL-Wavenet-B', 'gender': 'MALE'}],
        'cmn-CN': [{'name': 'cmn-CN-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'cmn-CN-Wavenet-B', 'gender': 'MALE'}],
        'cmn-TW': [{'name': 'cmn-TW-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'cmn-TW-Wavenet-B', 'gender': 'MALE'}],
        'fil-PH': [{'name': 'fil-PH-Wavenet-A', 'gender': 'FEMALE'}, {'name': 'fil-PH-Wavenet-C', 'gender': 'MALE'}],
    }

    wavenet_support = {
        'ar': 'ar-XA', 'bn': 'bn-IN', 'en': 'en-US', 'fr': 'fr-FR', 'es': 'es-ES',
        'gu': 'gu-IN', 'ja': 'ja-JP', 'kn': 'kn-IN', 'ml': 'ml-IN', 'mr': 'mr-IN',
        'sv': 'sv-SE', 'ta': 'ta-IN', 'tr': 'tr-TR', 'ms': 'ms-MY', 'de': 'de-DE',
        'hi': 'hi-IN', 'id': 'id-ID', 'it': 'it-IT', 'ko': 'ko-KR', 'ru': 'ru-RU',
        'da': 'da-DK', 'nl': 'nl-NL', 'pt': 'pt-PT', 'vi': 'vi-VN', 'pl': 'pl-PL',
        'gb': 'en-GB', 'au': 'en-AU', 'in': 'en-IN', 'no': 'nb-NO', 'be': 'nl-BE',
        'fi': 'fil-PH', 'tw': 'cmn-TW', 'zh': 'cmn-CN'
    }


class TextToSpeech():
    def __init__(self, text: str, language='en', voice_name: str = None, gender: str = None, rate=1.0, pitch=0.0):
        self.language = language
        self.voice_name = voice_name
        self.gender = gender
        self.rate = rate
        self.pitch = pitch
        self.engine = None

        self.text = text
        self.result = b''

        global gcloud
        self.gcloud = gcloud

    @staticmethod
    def gcloud_connect_from_file(filename: str):
        global gcloud
        try:
            gcloud = TextToSpeechClient.from_service_account_file(filename)
        except:
            gcloud = None

    def __get_voice_name(self):
        if self.gender != None:
            for wavenet in Dictionary.wavenets[self.language]:
                if wavenet['gender'].lower() == self.gender:
                    self.voice_name = wavenet['name']
                    return self.voice_name

    def __get_engine(self):
        if self.gender != None or self.voice_name != None:
            self.engine = 'gcloud'
        else:
            self.engine = 'translate'

        if self.gcloud == None:
            self.engine = 'translate'

    def convert(self) -> bytes:
        self.__get_engine()

        if self.engine == 'gcloud':
            self.__get_voice_name()

            self.result = GoogleTTS(
                self.gcloud, self.text, self.language, self.voice_name, self.rate, self.pitch
            ).convert()
        
        if self.engine == 'translate':
            if self.language in Dictionary.accents:
                self.language = 'en'

            self.result = TranslateTTS(
                self.text, self.language
            ).convert()

        return self.result
    
    def save(self, filename: str):
        with open(filename, "wb") as out:
            out.write(self.result)