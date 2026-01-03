# voice/voice_listener.py
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from PySide6.QtCore import QThread, Signal

GRAMMAR = [
    "fila", "borrar", "cantidad", "precio",
    "uno", "dos", "tres", "cuatro", "cinco",
    "consultoria", "hosting", "pintura_blanca",
    "siguiente", "cancelar", "producto"
]


class VoiceListener(QThread):
    result_ready = Signal(str)

    def __init__(self, grammar=None, model_path="models/vosk-es"):
        super().__init__()
        self.running = False
        self.grammar = grammar or GRAMMAR
        self.model_path = model_path
        self.last_tokens = []  # lista de tokens ya emitidos

    def run(self):
        self.running = True
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        model = Model(self.model_path)
        recognizer = KaldiRecognizer(model, 16000, json.dumps(self.grammar))

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
                current_tokens = partial.get("partial", "").upper().split()

                # obtenemos solo los tokens nuevos
                new_tokens = current_tokens[len(self.last_tokens):]

                if new_tokens:
                    self.last_tokens = current_tokens
                    for token in new_tokens:
                        self.result_ready.emit(token)

    def stop(self):
        self.running = False
        self.wait()
