import subprocess
import threading
from pydub import AudioSegment


class Inference():
    def __init__(self, instrument_file, vocal_file, model_file, config_file, pitch=0):
        self.instrument_file = instrument_file
        self.vocal_file = vocal_file
        self.model_file = model_file
        self.config_file = config_file
        self.pitch = pitch

        self.output = ""
        self.error = ""
        self.return_code = ""

    def process(self):
        command = f"svc infer {self.vocal_file} -c {self.config_file} -m {self.model_file} -na -t {self.pitch}"

        process = subprocess.Popen(
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.output, self.error = process.communicate()
        self.return_code = process.returncode

        self.overlay(
            vocal_file=f"{'.'.join(self.vocal_file.split('.')[:-1])}.out.wav",
            instrument_file=self.instrument_file
        )
        self.callback(self)

    def overlay(self, vocal_file, instrument_file):
        vocal = AudioSegment.from_file(vocal_file)
        instrument = AudioSegment.from_file(instrument_file)

        combined = vocal.overlay(instrument)
        combined.export(f"{'.'.join(self.vocal_file.split('.')[:-1])}.final.wav")

    def start(self):
        threading.Thread(target=self.process).start()

    def callback(self, *args, **kwargs):
        pass
