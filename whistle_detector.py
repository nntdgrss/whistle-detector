import pyaudio
import numpy as np

class WhistleDetector:
    def __init__(self, rate=44100, chunk=1024, target_range=(1000, 2000), threshold=200):
        self.rate = rate
        self.chunk = chunk
        self.target_range = target_range
        self.threshold = threshold
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.listening = False

    def list_input_devices(self):
        return [
            self.audio.get_device_info_by_index(i)["name"]
            for i in range(self.audio.get_device_count())
            if self.audio.get_device_info_by_index(i)["maxInputChannels"] > 0
        ]

    def set_input_device(self, device_index):
        if self.stream is not None:
            self.stop_listening()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=device_index,
        )

    def detect_whistle(self, data):
        fft = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), d=1 / self.rate)
        power = np.abs(fft)
        peak_freq_index = np.argmax(power)
        peak_freq = freqs[peak_freq_index]
        peak_power = power[peak_freq_index]
        return self.target_range[0] <= peak_freq <= self.target_range[1] and peak_power > self.threshold

    def start_listening(self, callback):
        if self.stream is None:
            raise ValueError("Input device is not set.")
        self.listening = True
        while self.listening:
            data = np.frombuffer(self.stream.read(self.chunk, exception_on_overflow=False), dtype=np.int16)
            if self.detect_whistle(data):
                callback(True)
            else:
                callback(False)

    def stop_listening(self):
        self.listening = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def terminate(self):
        self.audio.terminate()
