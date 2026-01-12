#voice_worker.py

from PySide6.QtCore import QThread, Signal
import json
import queue
import sounddevice as sd
import json

from vosk import Model, KaldiRecognizer


class VoiceWorker(QThread):
    result_ready = Signal(str)

    def __init__(self, grammar):
        super().__init__()
        self.grammar = grammar
        self.running = True
        self.last_token = ""


    def run(self):
        MODEL_PATH = "models/vosk-es"

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if self.running:
                q.put(bytes(indata))

        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(
            model, 16000, json.dumps(self.grammar)
        )

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback
        ):
            while self.running:
                data = q.get()

                recognizer.AcceptWaveform(data)

                partial = json.loads(recognizer.PartialResult())
                token = partial.get("partial", "").upper()

                if token and token != self.last_token:
                    self.last_token = token
                    self.result_ready.emit(token)



        self.running = False

    def stop(self):
        self.running = False


