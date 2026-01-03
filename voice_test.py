import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-es"

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    print("🎙️ Escuchando... (Ctrl+C para salir)")
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print("Reconocido:", text)
