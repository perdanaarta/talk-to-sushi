from gtts import gTTS


class TranslateTTS():
    def __init__(self, text: str, language='en', tld='com'):
        self.language = language
        self.tld = tld
        self.text = text
        self.result = b''

    def convert(self) -> bytes:
        """Convert text into audio bytes using Translate tts"""

        def process(text: str):
            for b in (gTTS(self.text, self.tld, self.language)):
                return b

        try:
            audio_data, line = b'', ""

            for word in self.text.split(" "):
                if len(line) + 1 + len(word) > 100:
                    audio_data += process(line)
                    line = ""
                    line += word

                else:
                    line += " " + word

            audio_data += process(line)

            self.result = audio_data
            return self.result

        except:
            self.result = process('please dont abuse me')
            return self.result
