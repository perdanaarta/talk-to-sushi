import subprocess
import threading


class Split():
    def __init__(self, audio_input_file):
        self.audio_input_file = audio_input_file
        self.output = ""
        self.error = ""
        self.return_code = ""

    def process(self):
        command = f"demucs --two-stems=vocals {self.audio_input_file} -o {'/'.join(self.audio_input_file.split('/')[:-1])}"

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.output, self.error = process.communicate()
        self.return_code = process.returncode

        if self.return_code == 0:
            self.callback(self)
        else:
            self.error_callback(self)

    def start(self):
        threading.Thread(target=self.process).start()

    def callback(self, *args, **kwargs):
        pass

    def error_callback(self, *args, **kwargs):
        pass
